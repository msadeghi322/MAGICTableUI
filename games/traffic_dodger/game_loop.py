import pygame
import pandas as pd
from . import constants as C
from . import objects as OBJECTS
from . import score as SCORE
from . import pygame_setup as SETUP
import math
from pygame.locals import *
import random
import numpy as np
import time

#NOTE: this loop is only called at a interval set by openCV loop. approx. 20~40fps.
## not fast enough. I need a game fps of 60 with another clock?

## TODO 0125: add global clock
##           logging data - [subject name, trialnum, recording time, survival time (score), trajectory]
## TODO 0127: draw trace + obstacle map ACCURATELY

class TrafficDodger():
    def __init__(self):
        #super(TrafficDodger, self).__init__()
        self.cars_list = SETUP.cars_list
    ##    self.bonuses_list = SETUP.bonuses_list
        self.deterministic_carList = SETUP.deterministic_carList
        self.deterministic_rockList = SETUP.deterministic_rockList
        self.deterministic_orange_carList = SETUP.deterministic_orange_carList

        """ visibility window """
        self.image = pygame.Surface((C.WIDTH_GAME,(SETUP.y_grid_size*(SETUP.row_per_screen-SETUP.visibility-2))))
        # self.image = pygame.Surface((C.WIDTH_GAME,C.HEIGHT_GAME))

        # self.image.set_alpha(200)
        # self.image.fill((0,0,0))
        # self.rect = self.image.get_rect(top=(int(C.WIDTH_GAME/2), SETUP.y_grid_size*(SETUP.row_per_screen-SETUP.visibility)))
        self.rect = self.image.get_rect(top=SETUP.y_grid_size*1)

        # self.mask = pygame.mask.from_surface(self.image)


        #self.deterministic_bananaList = SETUP.deterministic_bananaList
        #self.deterministic_green_bananaList = SETUP.deterministic_green_bananaList
        self.min_car_speed = SETUP.min_car_speed
        self.max_car_speed = SETUP.max_car_speed
        self.stochastic_level=SETUP.stochastic_level
        self.odds = SETUP.odds
        self.paused = SETUP.paused
        self.default_font = SETUP.default_font
        self.ground_texture = SETUP.ground_texture
        self.background_img = SETUP.background_img
        self.car_fire_sound = SETUP.car_fire_sound
        self.game_music = SETUP.game_music

        ## initiate a clock
        self.clock = pygame.time.Clock()
        self.current_time = 0.0
        self.currentTimeList = []
        self.currentEpochTimeList =[]
        self.rowNumberList = []

        self.mouse_pos = pygame.mouse.get_pos()
        self.xObjectList = []
        self.yObjectList = []
        self.scoreList = []
        #self.obstacles_matrix_at_bottom_list= []
        self.carX_in_row_list = []
        self.rockX_in_row_list = []
        self.orange_carX_in_row_list = []

        # initial location when keyboard_input is used
        #num_of_blocks = 8 # parameterize this
        self.xObject_discrete =200
        self.block_move = 0
        self.block_loc = 4
        self.row = 0
        # self.block_move_now = 0
        # self.block_move_now = 0
 #       self.time_car_at_bottom_list = []
#        self.time_rock_at_bottom_list = []

    def draw(self):
        # C.screen.fill((255,255,255))
        C.screen.blit(self.image, self.rect)


    def game_loop(self, gameTest, square, score, running, xObject, yObject, firstRun, num_frames, game_name, timeTag, categories, args):
        #while True:
        pygame.display.update()
        C.fps_clock.tick(C.GAME_FPS)
        # num_frames = int(num_frames)

        ## update time marker
        self.current_time = pygame.time.get_ticks()

        epochtime = time.time()  # epoch time in second




        if not self.paused:
            self.draw_repeating_background(self.background_img)

          
            if score.points >= 2000:
                #self.stochastic_level = 3000
                self.max_car_speed = 80
            elif score.points >= 1000:
                #self.stochastic_level = 3
                self.max_car_speed = 3
                self.max_car_speed = 15
            elif score.points >= 800:
                self.max_car_speed = 20
            elif score.points >= 600:
                #self.stochastic_level = 2
                self.max_car_speed = 16
            elif score.points >= 500:
                self.odds = 40
                self.max_car_speed = 14
            elif score.points >= 400:
                self.max_car_speed = 12
            elif score.points >= 300:
                self.odds = 50
                self.max_car_speed = 10
            elif score.points >= 200:
                # The smaller this number is, the probability for a car
                # to be shot is higher
                self.odds = 60
                self.max_car_speed = 8
            elif score.points >= 150:
                self.odds = 70
                self.max_car_speed = 6    
            elif score.points >= 100:
                self.odds = 80
                self.max_car_speed = 4
            elif score.points >= 60:
                self.odds = 90
                self.max_car_speed = 3
            elif score.points >= 30:
                self.odds = 100
                self.max_car_speed = 2

            if game_name == 'banana_game':
                banana_row=row_of_bananas(num_frames, score)
                self.deterministic_bananaList.add(banana_row[0]) # test
                self.deterministic_green_bananaList.add(banana_row[1]) 
            elif game_name == 'traffic_dodger':
                #if random.randint(1, self.odds) == 1:
    ##                if random.randint(1, self.odds ) == 1:
    ##                    bonus = OBJECTS.Bonus(random.randint(30, C.WIDTH_GAME - 30),
    ##                                  random.randint(30, C.HEIGHT_GAME - 30))
    ##                    bonuses_list.add(bonus)
    ##                for i in range(self.stochastic_level):
    ##                    self.cars_list.add(random_car(random.randint(self.min_car_speed,
    ##                                                             self.max_car_speed)))
    ##                    score.points += 1
     #              pass
                """ Row loading speed """
                if num_frames % SETUP.update_spf== 0:  # row advnace at every x frames.
                    self.row = int(num_frames / SETUP.update_spf) # row = 1, 2, 3, 4....


                    traffic_row = self.row_of_cars(self.row, score)
                    traffic_row = self.row_of_cars(self.row, score)

                
                    car_row = traffic_row[0]
                    rock_row  = traffic_row[1]
                    orange_car_row  = traffic_row[2]
                else:
                    car_row = []
                    rock_row = []
                    orange_car_row = []

                ##### DO this in the Post-processing #####
                #car_vel = SETUP.car_speed
                #rock_vel = SETUP.rock_speed 

                #fps = 30
                #time_car_at_bottom = [int(float((C.HEIGHT_GAME-C.PLAYER_YOFFSET)/ car_vel*fps))+ self.current_time for x in car_row]
                #time_rock_at_bottom = [int(float((C.HEIGHT_GAME-C.PLAYER_YOFFSET)/ rock_vel*fps))+ self.current_time for x in rock_row]

                carX_in_row= [x.rect.x for x in car_row]
                rockX_in_row = [x.rect.x for x in rock_row]
                orange_carX_in_row = [x.rect.x for x in orange_car_row]

                            
                #coordinates_vs_time_car = (carX_at_bottom, time_car_at_bottom)
                #coordinates_vs_time_rock = (rockX_at_bottom, time_rock_at_bottom)

                
     ##                if len(carX_in_row)> 0:
##                    self.carX_in_row_list.append(carX_in_row)
##                    self.time_car_at_bottom_list.append(time_car_at_bottom)
##                if len(rockX_in_row)> 0:
##                    self.rockX_in_row_list.append(rockX_in_row)
##                    self.time_rock_at_bottom_list.append(time_rock_at_bottom)

                ##########################################
                    
                self.deterministic_carList.add(car_row)
                self.deterministic_rockList.add(rock_row)
                self.deterministic_orange_carList.add(orange_car_row)
            
            
            self.draw_text('{}  points'.format(score.points), self.default_font, C.screen,
                      70, 20, C.DARK_ALLOY_ORANGE)
            self.draw_text('Record: {}'.format(score.high_score), self.default_font,
                      C.screen, C.WIDTH_GAME - 70, 20, C.DARK_ALLOY_ORANGE)


            """ Update only at every discrete row advance"""
            if num_frames % SETUP.update_spf==0:
                # self.cars_list.update()
                #bonuses_list.update()
                self.deterministic_carList.update()
                self.deterministic_rockList.update()
                self.deterministic_orange_carList.update()


            #self.deterministic_bananaList.update()
            #self.deterministic_green_bananaList.update()
            self.cars_list.draw(C.screen)
            #bonuses_list.draw(C.screen)
            self.deterministic_carList.draw(C.screen)
            self.deterministic_rockList.draw(C.screen)
            self.deterministic_orange_carList.draw(C.screen)
            #self.deterministic_bananaList.draw(C.screen)
            #self.deterministic_green_bananaList.draw(C.screen)

            """ draw visibility mask"""
            self.draw()



            ## collision between "cars" and player  
            #bonus_hit_list = square.collide(bonuses_list)
            # traffic_list = square.collide(self.trafficList)
            deterministic_car_hit_list = square.collide(self.deterministic_carList)
            deterministic_rock_hit_list = square.collide(self.deterministic_rockList)
            deterministic_orange_car_hit_list = square.collide(self.deterministic_orange_carList)


            #deterministic_banana_hit_list = square.collide(self.deterministic_bananaList)
            #deterministic_green_banana_hit_list = square.collide(self.deterministic_green_bananaList)


            if square.collide(self.cars_list):
                sound = pygame.mixer.Sound(self.car_fire_sound)
                # pygame.mixer.music.stop()
                sound.play()
                #score.points -= 30
                if score.high_score > score.highest_score:
                    score.save_highest_score()
                #return 'game_over_screen'
    ##        elif bonus_hit_list:
    ##            score.points += 10
    ##            bonus_hit_list[0].kill()
            elif deterministic_car_hit_list:
                score.points -= 20
                deterministic_car_hit_list[0].kill()
                if args["practice"]:
                    sound = pygame.mixer.Sound(self.car_fire_sound)
                    # pygame.mixer.music.stop()
                    sound.play()
                    """ TODO: record the location?"""
                    pass
                else:
                    running = False
            elif deterministic_rock_hit_list:
                score.points -= 20
                deterministic_rock_hit_list[0].kill()
                if args["practice"]:
                    sound = pygame.mixer.Sound(self.car_fire_sound)
                    # pygame.mixer.music.stop()
                    sound.play()
                    pass
                else:
                    running = False
            elif deterministic_orange_car_hit_list:
                score.points -= 20
                deterministic_orange_car_hit_list[0].kill()
                if args["practice"]:
                    sound = pygame.mixer.Sound(self.car_fire_sound)
                    # pygame.mixer.music.stop()
                    sound.play()
                    pass
                else:
                    running = False
    ##        elif deterministic_banana_hit_list:
    ##            #print "banana"
    ##            score.points += 10
    ##            deterministic_banana_hit_list[0].kill()
    ##        elif deterministic_green_banana_hit_list:
    ##            #print "green banana"
    ##            score.points -= 200
    ##            deterministic_green_banana_hit_list[0].kill()

            if score.points > score.high_score:
                score.high_score = score.points

            C.screen.blit(square.img, square.rect)


            """ KEY LOCK PER ROW ADVANCE"""
            if num_frames % SETUP.update_spf ==0: # reset the number of block move at every row advance
                self.current_loc= self.block_loc

     
            """ Computer vision control VS Keyboard / Mouse control """
            if not gameTest:  # using computer vision
                controller = 'Tracking'

                x_orig = int(xObject)
                y_orig = int(yObject)
                ## remapping to reduce the range within the table. (b/c edge is not good) 20180130
                xoffset = 80
                xObject_adjust = x_orig - xoffset
                

                
                self.mouse_pos = (xObject_adjust, y_orig)
                #### Cursor wrapping (not needed)
                if self.mouse_pos[0] <= 10:
                    #print "left out"
                    pygame.mouse.set_pos(C.WIDTH_GAME - 10, self.mouse_pos[1])
                    square.set_pos(10, C.HEIGHT_GAME - C.PLAYER_YOFFSET) # fix the y coordiate

                elif self.mouse_pos[0] >=(C. WIDTH_GAME - 10):
                    #print "right out"
                    pygame.mouse.set_pos(C.WIDTH_GAME - 10, self.mouse_pos[1])
                    square.set_pos(C.WIDTH_GAME - 10, C.HEIGHT_GAME - C.PLAYER_YOFFSET) # fix the y coordiate

    ##            elif mouse_pos[1] <= 10:
    ##                pygame.mouse.set_pos(mouse_pos[0], C.HEIGHT_GAME - 10)
    ##            elif mouse_pos[1] >= C.HEIGHT_GAME - 10:
    ##                pygame.mouse.set_pos(mouse_pos[0], 0 + 10)
                else:
                    #print "middle"
                    square.set_pos(self.mouse_pos[0], C.HEIGHT_GAME - C.PLAYER_YOFFSET) # fix the y coordiate
                #square.set_pos(*mouse_pos)
                if args["discrete_control"] > 0:
                    xObject = int(xObject / SETUP.xgrid) * SETUP.xgrid
                    yObject = C.HEIGHT_GAME - C.PLAYER_YOFFSET
                    controller = 'TrackingDiscrete'
                    square.set_pos(xObject, C.HEIGHT_GAME - C.PLAYER_YOFFSET)  # fix the y coordiate

            success = 1

            """ keyboard input for control or break out"""
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        # self.block_diff += 1
                        self.block_loc = min(self.current_loc+1, self.block_loc+1, SETUP.traffic_sheet.ncols-1)
                        print(SETUP.traffic_sheet.ncols)
                        # self.block_move_now = min(self.block_move, 1)
                    if event.key == pygame.K_LEFT:
                        # self.block_diff -= 1
                        # self.block_loc = self.block_loc+  max(-1, self.block_diff)
                        self.block_loc = max(self.current_loc-1, self.block_loc-1, 0)

                        # self.block_move_now = max(self.block_move, -1)
                    if event.key == pygame.K_p:
                        #global self.paused
                        self.paused = not self.paused
                        if self.paused:
                            transp_surf = pygame.Surface((C.WIDTH_GAME, C.HEIGHT_GAME))
                            transp_surf.set_alpha(150)
                            screen.blit(transp_surf, transp_surf.get_rect())
                            pygame.mouse.set_visible(True)
                            self.draw_text('self.paused', pygame.font.Font(None, 60), C.screen,
                                      C.WIDTH_GAME / 2, C.HEIGHT_GAME / 4, C.RED)
                    if event.key == pygame.K_ESCAPE:
                        #global running
                        success=0
                        running = False
                if event.type == QUIT:
                    #global running
                    running = False
                    #return 'quit'

                """ add successful break condition when the end row is reached"""
                if self.row > SETUP.traffic_sheet.nrows + 12:
                    success = 1
                    running = False

                if gameTest:  # use mouse /keyboard input as input coordinates for game module test
                    try:
                        event.type == pygame.MOUSEMOTION
                        self.mouse_pos = pygame.mouse.get_pos()
                    except:
                        print("Some error")
                        raise
                    ### Cursor wrapping (not needed)
    ##                if mouse_pos[0] <= 10:
    ##                    pygame.mouse.set_pos(C.WIDTH_GAME - 10, mouse_pos[1])
    ##                elif mouse_pos[0] >= C.WIDTH_GAME - 10:
    ##                    pygame.mouse.set_pos(0 + 10, mouse_pos[1])
    ##                elif mouse_pos[1] <= 10:
    ##                    pygame.mouse.set_pos(mouse_pos[0], C.HEIGHT_GAME - 10)
    ##                elif mouse_pos[1] >= C.HEIGHT_GAME - 10:
    ##                    pygame.mouse.set_pos(mouse_pos[0], 0 + 10)

                    """ Play in a discretized grid in X """

                    if args["keyboard_control"]: # keyboard input
                        # xObject = self.xObject_discrete + self.block_move* SETUP.xgrid
                        xObject = self.block_loc * SETUP.xgrid + int(SETUP.xgrid/2) # last part for centering on a grid
                        yObject = C.HEIGHT_GAME - C.PLAYER_YOFFSET
                        controller = 'Keyboard'

                        # self.xObject_discrete = xObject
                    # print("blocksize:", block_size, " xObject:", xObject)
                    else: # from mouse
                        if args["discrete_control"] > 0:
                            xObject = int(self.mouse_pos[0] / SETUP.xgrid) * SETUP.xgrid
                            yObject = C.HEIGHT_GAME - C.PLAYER_YOFFSET
                            controller = 'MouseBlocked'
                        else:
                            xObject = self.mouse_pos[0]
                            yObject = self.mouse_pos[1]
                            square.set_pos(self.mouse_pos[0], C.HEIGHT_GAME - C.PLAYER_YOFFSET)
                            controller = 'RawMouse'


                    square.set_pos(xObject, C.HEIGHT_GAME - C.PLAYER_YOFFSET)  # fix the y coordiate

                    # print("xObject", xObject, "self.mouse_pos[0]:", self.mouse_pos[0])

                # else: # from computer vision tracking

                    #square.set_pos(*mouse_pos)

                
                # else: # if not a gameTest


    ##                if event.type == pygame.MOUSEBUTTONDOWN:
    ##                    random_x = random.randint(0, WIDTH)
    ##                    random_y = random.randint(0, HEIGHT)
    ##                    square.set_pos(random_x, random_y)
    ##                    pygame.mouse.set_pos([random_x, random_y])
                    
                        





            #obstacles = 

            ## recording the time and coordinates.
            self.currentTimeList.append(self.current_time)
            self.currentEpochTimeList.append(epochtime)
            self.rowNumberList.append(self.row)
            self.xObjectList.append(xObject)
            self.yObjectList.append(yObject)
            self.scoreList.append(score.points)
            self.carX_in_row_list.append(carX_in_row)
            self.rockX_in_row_list.append(rockX_in_row)
            self.orange_carX_in_row_list.append(orange_carX_in_row)
            # self.row_list.append(row)






        else: # if it is paused.
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                        pygame.mouse.set_visible(False)
                elif event.key == pygame.K_f: #F11
                        toggle_fullscreen()
                if event.key == pygame.K_ESCAPE:
                    #global running
                    running = False
                if event.type == QUIT:
                    #global running
                    running = False

        # Limit to 40 frames per second
        #C.clock.tick(40)
                    #return 'quit'
        # When out of the main loop, the game is over

        if running == False:
               ## reconstruct the obstacle map referenced to the x-coordinate when it hits the bottom
               #  t = s/v. v=12 (now),

               print('currentTime', len(self.currentTimeList))
               print('carX_in_row_list', len(self.carX_in_row_list))
               print('rockX_in_row_list', len(self.rockX_in_row_list))
               
               import os
               data = pd.DataFrame({'currentTime': self.currentTimeList,
                                    'currentEpochTime': self.currentEpochTimeList,
                                    'row_number': self.rowNumberList,
                                    'xObject': self.xObjectList,
                                    'yObject': self.yObjectList,
                                    'carX_in_row_list': self.carX_in_row_list,
                                    # 'rockX_in_row_list': self.rockX_in_row_list,
                                    # 'orange_carX_in_row_list': self.orange_carX_in_row_list,
                                    'score': self.scoreList})
               #car_map_data = pd.DataFrame({'carX_at_bottom_list': self.carX_at_bottom_list, 'time_car_at_bottom_list': self.time_car_at_bottom_list})
               #rock_map_data = pd.DataFrame({'rockX_at_bottom_list': self.rockX_at_bottom_list, 'time_rock_at_bottom_list': self.time_rock_at_bottom_list})

               # """ Decide output file names """
               # x = int(input("Was this game a success?  Y(1) or N(0) "))

               # if args["gamenote"] > 0:
               #     note = input("Write any note if any. Enter when done >> ")
               # else:
               #     note = ""

               local_path = os.getcwd()

               # os.path.join(dataOutput_path, timeTag + "_" + categories + "_" + subjectID + "_" + controller + "_success" + str(x) + ".csv")
               fullfilename = os.path.join(local_path, 'games', game_name, 'Output', timeTag + "_" + categories + "_" + args["subject"] + "_" + controller + "_V"+str(SETUP.visibility)+"_S"+str(SETUP.speed_factor)+"_"+game_name+ "_STG_" + SETUP.stagename + "_success" + str(success) + ".csv")

               data.to_csv(fullfilename, sep=',', encoding='utf-8')
               #car_map_data.to_csv(os.path.join(local_path, "car_resultant_matrix.csv"), sep=',', encoding='utf-8')
               #rock_map_data.to_csv(os.path.join(local_path, "rock_resultant_matrix.csv"), sep=',', encoding='utf-8')


        return running




    def start_screen(self):
        pygame.mouse.set_cursor(*pygame.cursors.diamond)
        title_font = pygame.font.Font('freesansbold.ttf', 65)
        big_font = pygame.font.Font(None, 36)
        default_font = pygame.font.Font(None, 28)
        self.draw_text('TRAFFIC DODGER', title_font, C.screen,
                  C.WIDTH_GAME / 2, C.HEIGHT_GAME / 3, C.RED, C.YELLOW)
        self.draw_text('Use the mouse to dodge the cars', big_font, C.screen,
                  C.WIDTH_GAME / 2, C.HEIGHT_GAME / 2, C.GREEN, C.BLACK)
        self.draw_text("Press any mouse button or S when you're ready",
                  self.default_font, C.screen, C.WIDTH_GAME / 2, C.HEIGHT_GAME / 1.7, C.GREEN, C.BLACK)
        self.draw_text('Press f to toggle full screen', self.default_font, C.screen,
                  C.WIDTH_GAME / 2, C.HEIGHT_GAME / 1.1, C.GREEN, C.BLACK)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                return 'play'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return 'play'
                if event.key == K_f: #K_F11
                    self.toggle_fullscreen()
            if event.type == pygame.QUIT:
                return 'quit'
        return 'start_screen'




    def game_over_screen(self, score):
        #global score
        pygame.mouse.set_visible(True)
        # Text
        self.draw_text('{}  points'.format(score.points), SETUP.default_font, C.screen,
                  60, 20, C.GREEN)
        self.draw_text('Record: {}'.format(score.high_score), SETUP.default_font, C.screen,
                  C.WIDTH_GAME - 60, 20, C.GREEN)
        # Transparent surface
        transp_surf = pygame.Surface((C.WIDTH_GAME, C.HEIGHT_GAME))
        transp_surf.set_alpha(200)
        C.screen.blit(transp_surf, transp_surf.get_rect())

        self.draw_text("You've Finished!", pygame.font.Font(None, 40), C.screen,
                  C.WIDTH_GAME / 2 - 100, C.HEIGHT_GAME / 3, C.RED)
        self.draw_text('{}  points'.format(score.points), pygame.font.Font(None, 40), C.screen,
                  C.WIDTH_GAME / 2 + 110, C.HEIGHT_GAME / 3, C.GREEN)
        #self.draw_text('To play again press C or any mouse button',
    #              SETUP.default_font, C.screen, C.WIDTH_GAME / 2, C.HEIGHT_GAME / 2.1, C.GREEN)
        self.draw_text('To quit the game press Q', SETUP.default_font, C.screen,
                  C.WIDTH_GAME / 2, C.HEIGHT_GAME / 1.9, C.GREEN)
        self.draw_text('Press F11 to toggle full screen', SETUP.default_font, C.screen,
                  C.WIDTH_GAME / 2, C.HEIGHT_GAME / 1.1, C.GREEN, C.BLACK)

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_F11:
                    self.toggle_fullscreen()
                if event.key == pygame.K_q:
                    break
                    #return 'quit'
                elif event.key == pygame.K_c:
                    pass #return 'play'
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
                #return 'play'
            if event.type == QUIT:
                #global running
                break
                running = False
                
        import time
        time.sleep(2.0)
    #       return 'quit'
        #return 'game_over_screen'


    def toggle_fullscreen(self):
        if pygame.display.get_driver() == 'x11':
            pygame.display.toggle_fullscreen()
        else:
            #global screen, fullscreen
            screen_copy = C.screen.copy()
            if C.fullscreen:
                C.screen = pygame.display.set_mode((C.WIDTH_GAME, C.HEIGHT_GAME))
            else:
                C.screen = pygame.display.set_mode((C.WIDTH_GAME, C.HEIGHT_GAME), pygame.FULLSCREEN)
            C.fullscreen = not C.fullscreen
            C.screen.blit(screen_copy, (0, 0))


    def draw_text(self, text, font, surface, x, y, main_color, background_color=None):
        textobj = font.render(text, True, main_color, background_color)
        textrect = textobj.get_rect()
        textrect.centerx = x
        textrect.centery = y
        surface.blit(textobj, textrect)
        

    def draw_repeating_background(self,background_img):
        background_rect = background_img.get_rect()
        background_rect_width = background_rect.width
        background_rect_height = background_rect.height
        for i in range(int(math.ceil(C.WIDTH_GAME / background_rect.width))):
            for j in range(int(math.ceil(C.HEIGHT_GAME / background_rect.height))):
                C.screen.blit(self.background_img, Rect(i * background_rect_width,
                                                 j * background_rect_height,
                                                 background_rect_width,
                                                 background_rect_height))


    def random_car(self,speed):
        random_or = random.randint(1, 1)
        if random_or == 1:  # Up -> Down
            return OBJECTS.Car(random.randint(0, C.WIDTH_GAME), 0, 0, speed)
    ##    elif random_or == 2:  # Right -> Left
    ##        return Car(WIDTH, random.randint(0, HEIGHT), -speed, 0)
        #elif random_or == 2:  # Down -> Up
    #        return OBJECTS.Car(random.randint(0, C.WIDTH_GAME), C.HEIGHT_GAME, 0, -speed)
    ##    elif random_or == 4:  # Left -> Right
    ##        return Car(0, random.randint(0, HEIGHT), speed, 0)



    ### READ a list from a file, one line at a time. Need a global clock tick. WJS 20180112.  
    def row_of_cars(self,row, score):
        bike_row = pygame.sprite.Group()
        rock_row = pygame.sprite.Group()
        orange_car_row = pygame.sprite.Group()

#        print row
#        if num_frames % 10 == 0:  # every 10 frames of update
#            row = num_frames / 10
            #print row
        if row < SETUP.traffic_sheet.nrows:
            ## TODO: READ from prerecorded.  (xpos, 0, 0, speed) 4x1000 matrix.
            xgrid = SETUP.xgrid # invisible grid interval
            # print(SETUP.traffic_matrix[row])
            #print("row", row)
            xpos = np.nonzero(SETUP.traffic_matrix[row]) # car indices in a row
            for i in range(len(xpos[0])): # indices of 1s
                if xpos[0].size > 0: # check empty
                    #print "int(float(SETUP.car_sheet.nrows)/2): ", int(float(SETUP.car_sheet.nrows)/2)
                    # if row < int(float(SETUP.traffic_sheet.nrows)/2): # half way speed up
                    #     speed = SETUP.car_speed
                    # else:
                    speed = SETUP.car_speed
                    if SETUP.traffic_matrix[row][xpos[0][i]] == 1: 
                        bike = OBJECTS.Car((xpos[0][i-1])*xgrid,0,0, SETUP.car_speed)
                        bike_row.add(bike)
                    elif SETUP.traffic_matrix[row][xpos[0][i]] == 2:
                        rock = OBJECTS.Rock((xpos[0][i-1])*xgrid,0,0, SETUP.rock_speed)
                        rock_row.add(rock)
                    else:
                        orange_car = OBJECTS.OrangeCar((xpos[0][i-1])*xgrid,0,0, SETUP.car_speed)
                        orange_car_row.add(orange_car)
       
                    
            score.points += 5  # per line
##            else:
##                pass
            #tempList.add(bike)
        #return bike_row
        #print 'bike_row:', bike_row,  'rock:', rock_row
        return bike_row, rock_row, orange_car_row


    def row_of_bananas(self,num_frames, score):
        banana_row = pygame.sprite.Group()
        green_banana_row = pygame.sprite.Group()
        if num_frames % 10 == 0:  # every 10 frames of update
            row = num_frames / 10
            if row < SETUP.banana_sheet.nrows:
                ## TODO: READ from prerecorded.  (xpos, 0, 0, speed) 4x1000 matrix.
                xgrid = SETUP.xgrid
                xpos = np.nonzero(SETUP.banana_matrix[row]) # banana indices in a row
                for i in range(len(xpos[0])): # indices of 1s
                    if xpos[0].size > 0: # check empty
                        #print "xpos: ", xpos[0][i]
                        if row < int(float(xpos[0].size/2)): # half way speed up
                            speed = 1
                        else:
                            speed = 2

                        #print SETUP.banana_matrix[row][xpos[0][i]]
                        if SETUP.banana_matrix[row][xpos[0][i]] == 1: # yellow banana
                            banana = OBJECTS.Banana((xpos[0][i]-1)*xgrid,0,0, speed)
                            banana_row.add(banana)
                        else: # green banana
                            green_banana = OBJECTS.GreenBanana((xpos[0][i]-1)*xgrid,0,0, speed)
                            green_banana_row.add(green_banana)
                #score.points += 5  # per line
            else:
                pass
            #tempList.add(bike)
        return banana_row, green_banana_row


    ##def main_loop():
    ##    action = 'start_screen'
    ##    score = SCORE.Score()
    ##    while action != 'quit':
    ##        if action == 'start_screen':
    ##            action = start_screen()
    ##        elif action == 'play':
    ##            action = game_loop()
    ##        elif action == 'game_over_screen':
    ##            action = game_over_screen()





