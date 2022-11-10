# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 16:05:57 2022

@author: josea
"""

##1: EVENT DATA: Plotting Shots (Challenge) I decided to use match ID: 18245 which is Real Madrid vs Liverpool champions league final 2018 

"Import neccesary libraries"
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import Pitch,VerticalPitch,Sbopen

"Open the dataset with parser Sbopen - statsbomb"

parser = Sbopen()
df, related, freeze, tactics = parser.event(18245)
#get team names
team1, team2 = df.team_name.unique()
#A dataframe of shots
shots = df.loc[df['type_name'] == 'Shot'].set_index('id')

"Now we first, create the pitch and then we iterate through shots to get all shots in the match. We also get x and y coordinates, the team, and if a goal was scored."

pitch = Pitch(line_color = "black")
fig, ax = pitch.draw(figsize=(10, 7))
#Size of the pitch in yards (!!!)
pitchLengthX = 120
pitchWidthY = 80
#Plot the shots by looping through them.
for i,shot in shots.iterrows():
    #get the information
    x=shot['x']
    y=shot['y']
    goal=shot['outcome_name']=='Goal'
    team_name=shot['team_name']
    #set circlesize
    circleSize=2
    #plot Real Madrid
    if (team_name==team1):
        if goal:
            shotCircle=plt.Circle((x,y),circleSize,color="black")
            plt.text(x+1,y-2,shot['player_name'])
        else:
            shotCircle=plt.Circle((x,y),circleSize,color="black")
            shotCircle.set_alpha(.2)
    #plot Liverpool
    else:
        if goal:
            shotCircle=plt.Circle((pitchLengthX-x,pitchWidthY - y),circleSize,color="red")
            plt.text(pitchLengthX-x+1,pitchWidthY - y - 2 ,shot['player_name'])
        else:
            shotCircle=plt.Circle((pitchLengthX-x,pitchWidthY - y),circleSize,color="red")
            shotCircle.set_alpha(.2)
    ax.add_patch(shotCircle)
#set title
fig.suptitle("Real Madrid (white) and Liverpool (red) shots", fontsize = 24)
fig.set_size_inches(10, 7)
plt.show()
 
"Plot shots using the pitch class"

#create pitch
pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=True)
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
#query
mask_real_madrid = (df.type_name == 'Shot') & (df.team_name == team1)
#finding rows in the df and keeping only necessary columns
df_real_madrid = df.loc[mask_real_madrid, ['x', 'y', 'outcome_name', "player_name"]]

#plot them - if shot ended with Goal - alpha 1 and add name
#for Real Madrid
for i, row in df_real_madrid.iterrows():
    if row["outcome_name"] == 'Goal':
    #make circle
       pitch.scatter(row.x, row.y, alpha = 1, s = 500, color = "white", ax=ax['pitch'])
       pitch.annotate(row["player_name"], (row.x + 1, row.y - 2), ax=ax['pitch'], fontsize = 12)
    else:
       pitch.scatter(row.x, row.y, alpha = 0.2, s = 500, color = "white", ax=ax['pitch'])

mask_liverpool = (df.type_name == 'Shot') & (df.team_name == team2)
df_liverpool = df.loc[mask_liverpool, ['x', 'y', 'outcome_name', "player_name"]]

#for Liverpool we need to revert coordinates
for i, row in df_liverpool.iterrows():
    if row["outcome_name"] == 'Goal':
       pitch.scatter(120 - row.x, 80 - row.y, alpha = 1, s = 500, color = "red", ax=ax['pitch'])
       pitch.annotate(row["player_name"], (120 - row.x + 1, 80 - row.y - 2), ax=ax['pitch'], fontsize = 12)
    else:
       pitch.scatter(120 - row.x, 80 - row.y, alpha = 0.2, s = 500, color = "red", ax=ax['pitch'])

fig.suptitle("Real Madrid (white), Liverpool (red) Shots", fontsize = 30)
plt.show()
          

                              
  ###CHALLENGE STARTS##
                                         
                                         
                                         
##Create a dataframe of passes which contains all the passes of the match
passes = df.loc[df['type_name'] == 'Pass'].loc[df['sub_type_name'] != 'Throw-in'].set_index('id')
##Plot the start point of every Liverpool pass. Attacking left to right.
#create pitch
pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=True)
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)

#we can plot the start points by using the xy coordinates
for i,row in passes.iterrows():
    if row["team_name"]=="Liverpool":
        pitch.scatter(row.x, row.y, alpha = 1, s = 500, color = "red", ax=ax['pitch'])
      
fig.suptitle("Liverpool starting point passes", fontsize = 30)
plt.show()

##Plot only passes made by  Luka Modrić

#create pitch
pitch = Pitch(line_color='black',
              stripe=False)
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)

#we can plot the start points by using the xy coordinates
for i,row in passes.iterrows():
    if row["player_name"]=="Luka Modrić":
        pitch.scatter(row.x, row.y, alpha = 0.2, s = 500, color = "blue", ax=ax['pitch'])
      
fig.suptitle("All starting point passes from Luka Modric", fontsize = 30)
plt.show()

##Plot arrows to show where the passes went to.
# I am going to use the mplsoccer function to do this one.
#Filter passes made by Luka
mask_luka = (df.type_name == 'Pass') & (df.player_name == "Luka Modrić")
df_pass = df.loc[mask_luka, ['x', 'y', 'end_x', 'end_y']]

pitch = Pitch(line_color='black')
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
pitch.arrows(df_pass.x, df_pass.y,
            df_pass.end_x, df_pass.end_y, color = "blue", ax=ax['pitch'])
pitch.scatter(df_pass.x, df_pass.y, alpha = 0.2, s = 500, color = "blue", ax=ax['pitch'])
fig.suptitle("Luka passes direction", fontsize = 30)
plt.show()

#create df for plotting only forward passes

