# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 11:12:11 2022

@author: josea
"""
##Pass heatmaps##

#import neccesary libraries#
import matplotlib.pyplot as plt
from mplsoccer import Pitch,Sbopen,VerticalPitch
import pandas as pd
import numpy as np

#Opening the dataset, I am going to use Barcelona's 2017-2018 La liga's games.
#First, I founf the cometition and season ids#
parser = Sbopen()
df_competition = parser.competition()
#open the data
parser = Sbopen()
df_match = parser.match(competition_id=11, season_id=1)
#our team
team = "Barcelona"
#get list of games by our team, either home or away
match_ids = df_match.loc[(df_match["home_team_name"] == team) | (df_match["away_team_name"] == team)]["match_id"].tolist()
#calculate number of games
no_games = len(match_ids)#We have 36 games

#Finding Danger passes, I have changed the window to 5 seconds since 15 is too big#

#declare an empty dataframe
danger_passes = pd.DataFrame()
for idx in match_ids:
    #open the event data from this game
    df = parser.event(idx)[0]
    for period in [1, 2]:
        #keep only accurate passes by Barcelona that were not set pieces in this period
        mask_pass = (df.team_name == team) & (df.type_name == "Pass") & (df.outcome_name.isnull()) & (df.period == period) & (df.sub_type_name.isnull())
        #keep only necessary columns
        passes = df.loc[mask_pass, ["x", "y", "end_x", "end_y", "minute", "second", "player_name"]]
        #keep only Shots by Barcelona in this period
        mask_shot = (df.team_name == team) & (df.type_name == "Shot") & (df.period == period)
        #keep only necessary columns
        shots = df.loc[mask_shot, ["minute", "second"]]
        #convert time to seconds
        shot_times = shots['minute']*60+shots['second']
        shot_window = 5
        #find starts of the window
        shot_start = shot_times - shot_window
        #condition to avoid negative shot starts
        shot_start = shot_start.apply(lambda i: i if i>0 else (period-1)*45)
        #convert to seconds
        pass_times = passes['minute']*60+passes['second']
        #check if pass is in any of the windows for this half
        pass_to_shot = pass_times.apply(lambda x: True in ((shot_start < x) & (x < shot_times)).unique())

        #keep only danger passes
        danger_passes_period = passes.loc[pass_to_shot]
        #concatenate dataframe with a previous one to keep danger passes from the whole tournament
        danger_passes = pd.concat([danger_passes, danger_passes_period])

#Plotting location of danger passes#

#plot pitch
pitch = Pitch(line_color='black')
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
#scatter the location on the pitch
pitch.scatter(danger_passes.x, danger_passes.y, s=100, color='red', edgecolors='blue', linewidth=1, alpha=0.9, ax=ax["pitch"])
#plot arrows
pitch.arrows(danger_passes.x, danger_passes.y, danger_passes.end_x, danger_passes.end_y, color = "blue", ax=ax['pitch'])
#add title
fig.suptitle('Location of danger passes by ' + team, fontsize = 30)
plt.show()

#Making a heatmap#

#plot vertical pitch
pitch = Pitch(line_zorder=2, line_color='black')
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
#get the 2D histogram
bin_statistic = pitch.bin_statistic(danger_passes.x, danger_passes.y, statistic='count', bins=(6, 5), normalize=False)
#normalize by number of games
bin_statistic["statistic"] = bin_statistic["statistic"]/no_games
#make a heatmap
pcm  = pitch.heatmap(bin_statistic, cmap='Reds', edgecolor='grey', ax=ax['pitch'])
#legend to our plot
ax_cbar = fig.add_axes((1, 0.093, 0.03, 0.786))
cbar = plt.colorbar(pcm, cax=ax_cbar)
fig.suptitle('Danger passes by ' + team + " per game", fontsize = 30)
plt.show()

#Making a diagram of most involved players#

#keep only surnames
#danger_passes["player_name"] = danger_passes["player_name"].apply(lambda x: str(x).split()[-1]) I commented this one because
#It adds clarity to see the whole name of the player plus we are not plotting the name in the pitch#
#count passes by player and normalize them
pass_count = danger_passes.groupby(["player_name"]).x.count()/no_games
#make a histogram
ax = pass_count.plot.bar(pass_count)
#make legend
ax.set_xlabel("")
ax.set_ylabel("Barsa's number of danger passes per game 2017-2018 season by player")
plt.show()


##Challenge##

#Improve so that only high xG (>0.07) are included!#












#Make a heat map only for Barcelona's player who was the most involved in danger passes!#
#In Barcelona's case, this player is Messi (very surprising right?)
#Finding Danger passes

#declare an empty dataframe
danger_passes_messi = pd.DataFrame()
for idx in match_ids:
    #open the event data from this game
    df = parser.event(idx)[0]
    for period in [1, 2]:
        #keep only accurate passes by Messi(5503player_id)that were not set pieces in this period
        mask_pass_messi = (df.team_name == team) & (df.type_name == "Pass") & (df.outcome_name.isnull()) & (df.period == period) & (df.sub_type_name.isnull()) & (df.player_id==5503)
        #keep only necessary columns
        passes_messi = df.loc[mask_pass_messi, ["x", "y", "end_x", "end_y", "minute", "second", "player_name"]]
        #keep only Shots by Messi in this period
        mask_shot_messi = (df.team_name == team) & (df.type_name == "Shot") & (df.period == period)
        #keep only necessary columns
        shots_messi = df.loc[mask_shot_messi, ["minute", "second"]]
        #convert time to seconds
        shot_times_messi = shots_messi['minute']*60+shots['second']
        shot_window = 15 #I use the 15 seconds window
        #find starts of the window
        shot_start_messi = shot_times_messi - shot_window
        #condition to avoid negative shot starts
        shot_start_messi = shot_start_messi.apply(lambda i: i if i>0 else (period-1)*45)
        #convert to seconds
        pass_times_messi = passes_messi['minute']*60+passes['second']
        #check if pass is in any of the windows for this half
        pass_to_shot_messi = pass_times_messi.apply(lambda x: True in ((shot_start_messi < x) & (x < shot_times_messi)).unique())

        #keep only danger passes
        danger_passes_period_messi = passes_messi.loc[pass_to_shot_messi]
        #concatenate dataframe with a previous one to keep danger passes from the whole tournament
        danger_passes_messi = pd.concat([danger_passes_messi, danger_passes_period_messi])

#Plotting location of danger passes#

#plot pitch
pitch = Pitch(line_color='black')
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
#scatter the location on the pitch
pitch.scatter(danger_passes_messi.x, danger_passes_messi.y, s=100, color='red', edgecolors='blue', linewidth=1, alpha=0.9, ax=ax["pitch"])
#plot arrows
pitch.arrows(danger_passes_messi.x, danger_passes_messi.y, danger_passes_messi.end_x, danger_passes_messi.end_y, color = "blue", ax=ax['pitch'])
#add title
fig.suptitle('Location of danger passes by Messi ', fontsize = 30)
plt.show()

#Making a heatmap#

#plot vertical pitch
pitch = Pitch(line_zorder=2, line_color='black')
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
#get the 2D histogram
bin_statistic = pitch.bin_statistic(danger_passes_messi.x, danger_passes_messi.y, statistic='count', bins=(6, 5), normalize=False)
#normalize by number of games
bin_statistic["statistic"] = bin_statistic["statistic"]/no_games
#make a heatmap
pcm  = pitch.heatmap(bin_statistic, cmap='Reds', edgecolor='grey', ax=ax['pitch'])
#legend to our plot
ax_cbar = fig.add_axes((1, 0.093, 0.03, 0.786))
cbar = plt.colorbar(pcm, cax=ax_cbar)
fig.suptitle('Danger passes by Messi , per game', fontsize = 30)
plt.show()


