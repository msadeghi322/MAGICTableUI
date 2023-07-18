import os
import pygame as pg
import numpy as np
import csv
import random
from . import constants as C
from . import player as PLAYER
from . import score as SCORE
from . import objects as OBJECTS

############################# game #############################################################

#def pygame_setup():
    ### WJ Note: too much GLOBAL variable will probably make the program run slower.
    ### However, in the pygame mode, speed (fps) is less of an issue so it is okay to use some globals for convenience. 
    
    #########################################################
    ##################### pygame ############################
    #########################################################
##    # Resolution
##    global WIDTH_GAME, HEIGHT_GAME, BLACK, GREEN, DARK_ALLOY_ORANGE, RED, YELLOW, MSWIN, ASSETS, GAME_FPS
##    WIDTH_GAME = 640
##    HEIGHT_GAME = 360
##    # Colors
##    BLACK = (0, 0, 0)
##    GREEN = (0, 255, 0)
##    DARK_ALLOY_ORANGE = (196, 121, 67)
##    RED = (255, 0, 0)
##    YELLOW = (255, 255, 12)
##
##    MSWIN = os.name == 'nt'
##    ASSETS = os.path.join(os.path.dirname(__file__), 'assets')
##
##    GAME_FPS = 60

##    pygame.init()
    #global default_font, ground_texture, background_img, car_fire_sound, car_fire_sound, game_music
##
##    # Display
##    screen = pygame.display.set_mode((C.WIDTH_GAME, C.HEIGHT_GAME))
##    fullscreen = False
    # Window titlebar
    #pygame.display.set_caption(_(/Users/wonjoonsohn'Car dodger'))

pg.mouse.set_visible(False)
cars_list = pg.sprite.Group()
bonuses_list = pg.sprite.Group()


### car matrix creation
deterministic_carList =pg.sprite.Group()
deterministic_rockList =pg.sprite.Group()
deterministic_orange_carList =pg.sprite.Group()


row=100
column = 1
## TODO:
car_xpos = np.random.randint(0, 30, (row, column)) # integer range
car_ypos = np.zeros((row, column))
car_hspeed =np.zeros((row, column))
car_vspeed =np.ones((row, column))
car_rand_matrix= np.column_stack((car_xpos,car_ypos,car_hspeed,car_vspeed))

import xlrd

# rp1 - ra2 - rp2
## Car / traffic loader
# random_stage_col8_practice: practice stage ra2f
# random_stage_col8_ra1, random_stage_col8_repeat1
stagefilename = 'stage-col8-ra-3.xls'
stagename, stagename_ext = os.path.splitext(stagefilename)
book = xlrd.open_workbook(os.path.join('games', 'traffic_dodger', 'stage', stagefilename))
traffic_sheet = book.sheet_by_index(0)
traffic_matrix = np.zeros((traffic_sheet.nrows, traffic_sheet.ncols))

xgrid = int(float(C.WIDTH_GAME/traffic_sheet.ncols))  # e.g.  384 / (8) = 48

for j in range(0,traffic_sheet.nrows):  # e.g. 120  (0~119)
    for k in range(0,traffic_sheet.ncols): # e.g. 8  (0~7)
        if traffic_sheet.cell(j, k).value != xlrd.empty_cell.value:
            traffic_matrix[j][k] = traffic_sheet.cell(j, k).value

""" object speeds: very important """
visibility= 10 # 3, 5, 8. choose between 1 and max rows (10)
row_per_screen = 12 # Fix the number of grids vertically for all cases. Important for consistency in visual perception.
y_grid_size = C.HEIGHT_GAME / row_per_screen #  vertical grid size. 720/12 =60

speed_factor = 4 # # VARY THIS. Pick 4 for 9/19. 1 to 8, integer only
update_fps = speed_factor #This should be proportional to speed (faster drop = faster update fps)
camera_update_scale_factor = 20 # expected update at every 20ms. (~50Hz)
update_spf = int(2/update_fps * camera_update_scale_factor) # second per frame, an inverse of fps.

car_speed = y_grid_size  # down this much per update
rock_speed = y_grid_size  # down this much per per update
banana_speed =  y_grid_size

#       list_j = np.concatenate((list_j,sheet.row_values(k-1)))
#list_j.append(sheet.row_values(k-1)[j-1]))


#deterministic_carList = pg.sprite.Group()
#for row in range(5):
#    offset=0
#    for column in range(40):
#        bike = OBJECTS.Bicycle(offset + row*30,  column*30, 0, 2)
#        deterministic_carList.add(bike)
#        offset = offset + 10
#return deterministic_carList


## BANANA loader
deterministic_bananaList =pg.sprite.Group()
deterministic_green_bananaList =pg.sprite.Group()

book = xlrd.open_workbook(os.path.join('games', 'traffic_dodger', 'stage', 'banana_stage1.xlsx')) #games/traffic_dodger/
banana_sheet = book.sheet_by_index(0)
banana_matrix = np.zeros((banana_sheet.nrows, banana_sheet.ncols))

for j in range(0,banana_sheet.nrows):  # e.g. 120
    for k in range(0,banana_sheet.ncols): # e.g. 8
        if banana_sheet.cell(j, k).value != xlrd.empty_cell.value:
            banana_matrix[j][k] = banana_sheet.cell(j, k).value


min_car_speed = 1
max_car_speed = 1
stochastic_level = 1
odds = 12
paused = False

pg.init()
game_icon = os.path.join(C.ASSETS, 'car.png')
pg.display.set_icon(pg.image.load(game_icon))

# Preload resources
default_font = pg.font.Font(None, 28)
ground_texture = os.path.join(C.ASSETS, 'ground.png')
background_img = pg.image.load(ground_texture)
car_fire_sound = os.path.join(C.ASSETS, 'gun_fire.ogg')
game_music = os.path.join(C.ASSETS, 'Hitman.ogg')
pg.mixer.music.load(game_music)
