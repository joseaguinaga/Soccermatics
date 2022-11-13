# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 19:52:05 2022

@author: josea
"""

##Lets start by importing the neccesary libraries##
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import Pitch,Sbopen,VerticalPitch

##Open the event dataset from the champions league final;ID 18245##
parser = Sbopen()
df, related, freeze, tactics = parser.event(18245)#Real Madrid vs Liverpool

##Preparing the data: For passing networks we use only accurate/successful passes made by a team until the first substitution. This is mainly just to get going and there are several possible variations of this. We need information about pass start and end location as well as player who made and received the pass. To make the vizualisation clearer, we annotate the players using their surname##

#check for index of first sub
sub = df.loc[df["type_name"] == "Substitution"].loc[df["team_name"] == "Real Madrid"].iloc[0]["index"]
#make df with successfull passes by RM until the first substitution
mask_real_madrid = (df.type_name == 'Pass') & (df.team_name == "Real Madrid") & (df.index < sub) & (df.outcome_name.isnull()) & (df.sub_type_name != "Throw-in")
#taking necessary columns
df_pass = df.loc[mask_real_madrid, ['x', 'y', 'end_x', 'end_y', "player_name", "pass_recipient_name"]]
#adjusting that only the surname of a player is presented.
df_pass["player_name"] = df_pass["player_name"].apply(lambda x: str(x).split()[0])
df_pass["pass_recipient_name"] = df_pass["pass_recipient_name"].apply(lambda x: str(x).split()[0])

##Calculating vertices size and location##

scatter_df = pd.DataFrame()
for i, name in enumerate(df_pass["player_name"].unique()):
    passx = df_pass.loc[df_pass["player_name"] == name]["x"].to_numpy()
    recx = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_x"].to_numpy()
    passy = df_pass.loc[df_pass["player_name"] == name]["y"].to_numpy()
    recy = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_y"].to_numpy()
    scatter_df.at[i, "player_name"] = name
    #make sure that x and y location for each circle representing the player is the average of passes and receptions
    scatter_df.at[i, "x"] = np.mean(np.concatenate([passx, recx]))
    scatter_df.at[i, "y"] = np.mean(np.concatenate([passy, recy]))
    #calculate number of passes
    scatter_df.at[i, "no"] = df_pass.loc[df_pass["player_name"] == name].count().iloc[0]

#adjust the size of a circle so that the player who made more passes
scatter_df['marker_size'] = (scatter_df['no'] / scatter_df['no'].max() * 1500)

##Calculating edges width##

#counting passes between players
df_pass["pair_key"] = df_pass.apply(lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
lines_df = df_pass.groupby(["pair_key"]).x.count().reset_index()
lines_df.rename({'x':'pass_count'}, axis='columns', inplace=True)
#setting a treshold. You can try to investigate how it changes when you change it.
lines_df = lines_df[lines_df['pass_count']>2]

##Ploting vertices##

#Drawing pitch
pitch = Pitch(line_color='grey',pitch_color='green')
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
#Scatter the location on the pitch
pitch.scatter(scatter_df.x, scatter_df.y, s=scatter_df.marker_size, color='black', edgecolors='grey', linewidth=1, alpha=1, ax=ax["pitch"], zorder = 3)
#annotating player name
for i, row in scatter_df.iterrows():
    pitch.annotate(row.player_name, xy=(row.x, row.y), c='white', va='center', ha='center', weight = "bold", size=16, ax=ax["pitch"], zorder = 4)

fig.suptitle("Nodes location - Real Madrid", fontsize = 30)
plt.show()

##Plotting edges##

#plot once again pitch and vertices
pitch = Pitch(line_color='grey',pitch_color='green')
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
pitch.scatter(scatter_df.x, scatter_df.y, s=scatter_df.marker_size, color='white', edgecolors='black', linewidth=1, alpha=1, ax=ax["pitch"], zorder = 3)
for i, row in scatter_df.iterrows():
    pitch.annotate(row.player_name, xy=(row.x, row.y), c='black', va='center', ha='center', weight = "bold", size=16, ax=ax["pitch"], zorder = 4)

for i, row in lines_df.iterrows():
        player1 = row["pair_key"].split("_")[0]
        player2 = row['pair_key'].split("_")[1]
        #take the average location of players to plot a line between them
        player1_x = scatter_df.loc[scatter_df["player_name"] == player1]['x'].iloc[0]
        player1_y = scatter_df.loc[scatter_df["player_name"] == player1]['y'].iloc[0]
        player2_x = scatter_df.loc[scatter_df["player_name"] == player2]['x'].iloc[0]
        player2_y = scatter_df.loc[scatter_df["player_name"] == player2]['y'].iloc[0]
        num_passes = row["pass_count"]
        #adjust the line width so that the more passes, the wider the line
        line_width = (num_passes / lines_df['pass_count'].max() * 10)
        #plot lines on the pitch
        pitch.lines(player1_x, player1_y, player2_x, player2_y,
                        alpha=1, lw=line_width, zorder=2, color="white", ax = ax["pitch"])

fig.suptitle("Real Madrid Passing Network against Liverpool", fontsize = 30)
plt.show()

##Centralisation##

#calculate number of successful passes by player
no_passes = df_pass.groupby(['player_name']).x.count().reset_index()
no_passes.rename({'x':'pass_count'}, axis='columns', inplace=True)
#find one who made most passes
max_no = no_passes["pass_count"].max()
#calculate the denominator - 10*the total sum of passes
denominator = 10*no_passes["pass_count"].sum()
#calculate the nominator
nominator = (max_no - no_passes["pass_count"]).sum()
#calculate the centralisation index
centralisation_index = nominator/denominator
print("Centralisation index is ", centralisation_index)

##Challenge##

#Make a passing network from the game only with passes forward for Real Madrid!


#Use mask to get only passes forward #
mask_real_madrid_forward = (df.type_name == 'Pass') & (df.team_name == "Real Madrid") & (df.index < sub) & (df.outcome_name.isnull()) & (df.sub_type_name != "Throw-in") & (df.x<df.end_x)
#taking necessary columns
df_pass_forward = df.loc[mask_real_madrid_forward, ['x', 'y', 'end_x', 'end_y', "player_name", "pass_recipient_name"]]
#adjusting that only the surname of a player is presented.
df_pass_forward["player_name"] = df_pass_forward["player_name"].apply(lambda x: str(x).split()[0])
df_pass_forward["pass_recipient_name"] = df_pass_forward["pass_recipient_name"].apply(lambda x: str(x).split()[0])

##Calculating vertices size and location##
scatter_df_forward = pd.DataFrame()
for i, name in enumerate(df_pass_forward["player_name"].unique()):
    passx_f = df_pass_forward.loc[df_pass_forward["player_name"] == name]["x"].to_numpy()
    recx_f = df_pass_forward.loc[df_pass_forward["pass_recipient_name"] == name]["end_x"].to_numpy()
    passy_f = df_pass_forward.loc[df_pass_forward["player_name"] == name]["y"].to_numpy()
    recy_f = df_pass_forward.loc[df_pass_forward["pass_recipient_name"] == name]["end_y"].to_numpy()
    scatter_df_forward.at[i, "player_name"] = name
    #make sure that x and y location for each circle representing the player is the average of passes and receptions
    scatter_df_forward.at[i, "x"] = np.mean(np.concatenate([passx_f, recx_f]))
    scatter_df_forward.at[i, "y"] = np.mean(np.concatenate([passy_f, recy_f]))
    #calculate number of passes
    scatter_df_forward.at[i, "no"] = df_pass_forward.loc[df_pass_forward["player_name"] == name].count().iloc[0]

#adjust the size of a circle so that the player who made more passes
scatter_df_forward['marker_size'] = (scatter_df_forward['no'] / scatter_df_forward['no'].max() * 1500)

##Calculating edges width##

#counting passes between players
df_pass_forward["pair_key"] = df_pass_forward.apply(lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
lines_df_forward = df_pass_forward.groupby(["pair_key"]).x.count().reset_index()
lines_df_forward.rename({'x':'pass_count'}, axis='columns', inplace=True)
#setting a treshold. You can try to investigate how it changes when you change it.
lines_df_forward = lines_df_forward[lines_df_forward['pass_count']>2]

##Ploting vertices##

#Drawing pitch
pitch = Pitch(line_color='grey',pitch_color='green')
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
#Scatter the location on the pitch
pitch.scatter(scatter_df_forward.x, scatter_df_forward.y, s=scatter_df_forward.marker_size, color='black', edgecolors='grey', linewidth=1, alpha=1, ax=ax["pitch"], zorder = 3)
#annotating player name
for i, row in scatter_df_forward.iterrows():
    pitch.annotate(row.player_name, xy=(row.x, row.y), c='white', va='center', ha='center', weight = "bold", size=16, ax=ax["pitch"], zorder = 4)

fig.suptitle("Nodes location - Real Madrid", fontsize = 30)
plt.show()

##Plotting edges##

#plot once again pitch and vertices
pitch = Pitch(line_color='grey',pitch_color='green')
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
pitch.scatter(scatter_df_forward.x, scatter_df_forward.y, s=scatter_df_forward.marker_size, color='white', edgecolors='black', linewidth=1, alpha=1, ax=ax["pitch"], zorder = 3)
for i, row in scatter_df_forward.iterrows():
    pitch.annotate(row.player_name, xy=(row.x, row.y), c='black', va='center', ha='center', weight = "bold", size=16, ax=ax["pitch"], zorder = 4)

for i, row in lines_df_forward.iterrows():
        player1_f = row["pair_key"].split("_")[0]
        player2_f = row['pair_key'].split("_")[1]
        #take the average location of players to plot a line between them
        player1_x_f = scatter_df_forward.loc[scatter_df_forward["player_name"] == player1_f]['x'].iloc[0]
        player1_y_f= scatter_df_forward.loc[scatter_df_forward["player_name"] == player1_f]['y'].iloc[0]
        player2_x_f = scatter_df_forward.loc[scatter_df_forward["player_name"] == player2_f]['x'].iloc[0]
        player2_y_f = scatter_df_forward.loc[scatter_df_forward["player_name"] == player2_f]['y'].iloc[0]
        num_passes_f = row["pass_count"]
        #adjust the line width so that the more passes, the wider the line
        line_width_f = (num_passes_f / lines_df_forward['pass_count'].max() * 10)
        #plot lines on the pitch
        pitch.lines(player1_x_f, player1_y_f, player2_x_f, player2_y_f,
                        alpha=1, lw=line_width_f, zorder=2, color="white", ax = ax["pitch"])

fig.suptitle("Real Madrid Passing Network of only forward passes against Liverpool", fontsize = 30)
plt.show()