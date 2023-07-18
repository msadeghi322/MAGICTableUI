##  Won Joon Sohn
## create obstacle matrix - position of obstacles when it pass the bottom of the screen.
## Run this in the root folder: e.g. 'python games/traffic_dodger/create_obstacle_map.py'

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import glob
import os
import numpy as np
import pandas as pd
from ast import literal_eval
import constants as C
import pygame_setup as SETUP


## access parent directory
curfilePath = os.path.abspath(__file__)

### this will return current directory in which python file resides.
curDir = os.path.abspath(os.path.join(curfilePath, os.pardir))
baseDir = os.path.join(curDir, 'Output', 'AIM3_DATA' )

## long path ##
game_result_file_long = glob.glob(os.path.join(baseDir,  '*CM_s1*')) 

## load more traces
game_result_file = glob.glob(os.path.join(baseDir,  '*CM_d1*')) 
df_d1= pd.read_csv(game_result_file[0])
game_result_file = glob.glob(os.path.join(baseDir,  '*CM_d2*')) 
df_d2= pd.read_csv(game_result_file[0])
game_result_file = glob.glob(os.path.join(baseDir,  '*CM_d3*')) 
df_d3= pd.read_csv(game_result_file[0])
game_result_file = glob.glob(os.path.join(baseDir,  '*CM_d4*')) 
df_d4= pd.read_csv(game_result_file[0])


nrows = 1
fig, axes = plt.subplots(nrows, 1)
fig = plt.figure(figsize=(1.6,10))
fig.subplots_adjust(hspace = .5, wspace=.2)
window_title ='GamePath'
fig.canvas.set_window_title(window_title)



df_long= pd.read_csv(game_result_file_long[0])
### literal eval:  df.carX_at_bottom_list.apply(literal_eval)[0][0]
startTime_long= df_long.currentTime[0]
startTime_d1= df_d1.currentTime[0]
startTime_d2= df_d2.currentTime[0]
startTime_d3= df_d3.currentTime[0]
startTime_d4= df_d4.currentTime[0]
time_adjust_d1 = startTime_long - startTime_d1
time_adjust_d2 = startTime_long - startTime_d2
time_adjust_d3 = startTime_long - startTime_d3
time_adjust_d4 = startTime_long - startTime_d4


nrows= len(df_long.carX_in_row_list)-1
print 'nrows:', nrows


##############  CAR  ############

## try plt.scatter([10], [20])
# put a red dot, size 40, at 2 locations
# plt.scatter(x=[30, 40], y=[50, 60], c='r', s=40)

carX_at_bottom_list_remap = []
carTime_at_bottom_list_remap = []
rockX_at_bottom_list_remap = []
rockTime_at_bottom_list_remap = []
orange_carX_at_bottom_list_remap = []
orange_carTime_at_bottom_list_remap = []

car_frames_cnt_to_fall = int(float((C.HEIGHT_GAME - C.PLAYER_YOFFSET)/SETUP.car_speed)) # time for a car to fall ASSUMING CONSTANT SPEED.. e,g. 300/10 = 30frames
print car_frames_cnt_to_fall

print 'end time:', df_long.currentTime[nrows]
print 'start time:', df_long.currentTime[0]

for i in range(nrows): #
#    dots_in_row =len(df.carX_in_row_list.apply(literal_eval)[i])
    dots_in_row =len(df_long.carX_in_row_list.apply(literal_eval)[i])

    for k in range(dots_in_row): # for rows with > one car
        #carX_at_bottom_list_remap.append(df.carX_in_row_list.apply(literal_eval)[i][k])
        carX_at_bottom_list_remap.append(df_long.carX_in_row_list.apply(literal_eval)[i][k])
        #carTime_at_bottom_list_remap.append(df.currentTime[i+car_frames_cnt_to_fall])
        if i + car_frames_cnt_to_fall < nrows:
            carTime_at_bottom_list_remap.append(df_long.currentTime[i+car_frames_cnt_to_fall])
            last_i = i
        else:
            carTime_at_bottom_list_remap.append(df_long.currentTime[nrows]+int(float((i-last_i)*(df_long.currentTime[nrows-1]-df_long.currentTime[0])/nrows) ))


        #time_car_at_bottom_list_remap.append(df.time_car_at_bottom_list.apply(literal_eval)[i][k])
        #plt.plot(df.carX_at_bottom_list.apply(literal_eval)[i][k], df.time_car_at_bottom_list.apply(literal_eval)[i][k], 'ro')

plt.scatter(x=carX_at_bottom_list_remap, y=carTime_at_bottom_list_remap, edgecolors='black', c='none', marker="s", s=22, alpha=0.7, label='Cars')
#plt.legend((car_scatter), ('Cars'), scatterpoints = 1, loc = 'lower left', ncol=3, fontsize=8)


##############  ROCK  ############  
#df_rock= pd.read_csv(rock_obstacle_file[0])
### literal eval:  df.carX_at_bottom_list.apply(literal_eval)[0][0]
#nrows= len(df_long.rockX_in_row_list)-1

## try plt.scatter([10], [20])
# put a red dot, size 40, at 2 locations
# plt.scatter(x=[30, 40], y=[50, 60], c='r', s=40)

rock_frames_cnt_to_fall = int(float((C.HEIGHT_GAME - C.PLAYER_YOFFSET)/SETUP.rock_speed)) # time for a car to fall ASSUMING CONSTANT SPEED.. e,g. (540-60)/10 = 48frames

for i in range(nrows): #
    dots_in_row =len(df_long.rockX_in_row_list.apply(literal_eval)[i])
    for k in range(dots_in_row):
        rockX_at_bottom_list_remap.append(df_long.rockX_in_row_list.apply(literal_eval)[i][k])
        #rockTime_at_bottom_list_remap.append(df_long.currentTime[i+rock_frames_cnt_to_fall]- time_adjust)
        #plt.plot(df_rock.rockX_at_bottom_list.apply(literal_eval)[i][k], df_rock.time_rock_at_bottom_list.apply(literal_eval)[i][k], 'bo')
        if i + rock_frames_cnt_to_fall < nrows:
            rockTime_at_bottom_list_remap.append(df_long.currentTime[i+rock_frames_cnt_to_fall])
            last_i = i
        else:
            rockTime_at_bottom_list_remap.append(df_long.currentTime[nrows]+int(float((i-last_i)*(df_long.currentTime[nrows-1]-df_long.currentTime[0])/nrows) ))

plt.scatter(x=rockX_at_bottom_list_remap, y=rockTime_at_bottom_list_remap, c='black', marker="s", s=22, alpha=0.7, label='Rocks')


## orange car
for i in range(nrows): #
    dots_in_row =len(df_long.orange_carX_in_row_list.apply(literal_eval)[i])
    for k in range(dots_in_row):
        orange_carX_at_bottom_list_remap.append(df_long.orange_carX_in_row_list.apply(literal_eval)[i][k])
        #rockTime_at_bottom_list_remap.append(df_long.currentTime[i+rock_frames_cnt_to_fall]- time_adjust)
        #plt.plot(df_rock.rockX_at_bottom_list.apply(literal_eval)[i][k], df_rock.time_rock_at_bottom_list.apply(literal_eval)[i][k], 'bo')
        if i + rock_frames_cnt_to_fall < nrows:
            orange_carTime_at_bottom_list_remap.append(df_long.currentTime[i+rock_frames_cnt_to_fall])
            last_i = i
        else:
            orange_carTime_at_bottom_list_remap.append(df_long.currentTime[nrows]+int(float((i-last_i)*(df_long.currentTime[nrows-1]-df_long.currentTime[0])/nrows) ))

plt.scatter(x=orange_carX_at_bottom_list_remap, y=orange_carTime_at_bottom_list_remap, c='green', marker="^" , s=70, alpha=1.0, label='Trees')


############### PLAYER PATH  #############
#df= pd.read_csv(game_result_file[0])
plt.plot(df_long.xObject, df_long.currentTime, '--',  label='S1 path')
plt.savefig(os.path.join(baseDir,window_title+'_S1.pdf'))


## LOAD MORE TRACES ###
##
##plt.plot(df_d1.xObject, df_d1.currentTime+time_adjust_d1, '--',  label='D1 path')
##plt.plot(df_d2.xObject, df_d2.currentTime+time_adjust_d2, '--',  label='D2 path')
##plt.plot(df_d3.xObject, df_d3.currentTime+time_adjust_d3, '--',  label='D3 path')  # reference (long)
##plt.plot(df_d4.xObject, df_d4.currentTime+time_adjust_d4, '--',  label='D4 path')

# Now add the legend with some customizations.
plt.xlabel('X-position (px)', fontsize = 20)
plt.ylabel('Time (ms)', fontsize = 20)
plt.legend() #loc='upper left', bbox_to_anchor=(1, 0.5),prop={'size':10})



plt.savefig(os.path.join(baseDir,window_title+'.pdf'))
#df.plot(df['carX_at_bottom_list'], df['time_car_at_bottom_list'])
plt.show()




