import pygame
import constants as C
import objects as OBJECTS
import score as SCORE
import pygame_setup as SETUP
import math
from pygame.locals import *
import random
import numpy as np

#NOTE: this loop is only called at a interval set by openCV loop. approx. 20~40fps.
## not fast enough. I need a game fps of 60 with another clock?



def game_loop(gameTest, square, score, running, xObject, yObject, firstRun, num_frames, game_type):
    #while True:
    pygame.display.update()
    C.fps_clock.tick(C.GAME_FPS)

    # duplicate local (check speed)
    cars_list = SETUP.cars_list
##    bonuses_list = SETUP.bonuses_list
    deterministic_carList = SETUP.deterministic_carList
    deterministic_rockList = SETUP.deterministic_rockList

    #deterministic_bananaList = SETUP.deterministic_bananaList
    #deterministic_green_bananaList = SETUP.deterministic_green_bananaList
    min_car_speed = SETUP.min_car_speed
    max_car_speed = SETUP.max_car_speed
    stochastic_level=SETUP.stochastic_level
    odds = SETUP.odds
    paused = SETUP.paused
    default_font = SETUP.default_font
    ground_texture = SETUP.ground_texture
    background_img = SETUP.background_img
    car_fire_sound = SETUP.car_fire_sound
    game_music = SETUP.game_music

    #if firstRun:
#        create_deterministic_cars()
        
        

    if not paused:
        draw_repeating_background(background_img)
      
        if score.points >= 2000:
            #stochastic_level = 3000
            max_car_speed = 80
        elif score.points >= 1000:
            #stochastic_level = 3
            max_car_speed = 3
            max_car_speed = 15
        elif score.points >= 800:
            max_car_speed = 20
        elif score.points >= 600:
            #stochastic_level = 2
            max_car_speed = 16
        elif score.points >= 500:
            odds = 40
            max_car_speed = 14
        elif score.points >= 400:
            max_car_speed = 12
        elif score.points >= 300:
            odds = 50
            max_car_speed = 10
        elif score.points >= 200:
            # The smaller this number is, the probability for a car
            # to be shot is higher
            odds = 60
            max_car_speed = 8
        elif score.points >= 150:
            odds = 70
            max_car_speed = 6    
        elif score.points >= 100:
            odds = 80
            max_car_speed = 4
        elif score.points >= 60:
            odds = 90
            max_car_speed = 3
        elif score.points >= 30:
            odds = 100
            max_car_speed = 2

        if game_type == 'banana_game':
            deterministic_bananaList.add(row_of_bananas(num_frames, score)[0]) # test
            deterministic_green_bananaList.add(row_of_bananas(num_frames, score)[1]) 
        elif game_type == 'traffic_dodger':  
            #if random.randint(1, odds) == 1:
##                if random.randint(1, odds ) == 1:
##                    bonus = OBJECTS.Bonus(random.randint(30, C.WIDTH_GAME - 30),
##                                  random.randint(30, C.HEIGHT_GAME - 30))
##                    bonuses_list.add(bonus)
##                for i in range(stochastic_level):
##                    cars_list.add(random_car(random.randint(min_car_speed,
##                                                             max_car_speed)))
##                    score.points += 1
 #              pass
            deterministic_carList.add(row_of_cars(num_frames, score)[0]) # test
            deterministic_rockList.add(row_of_cars(num_frames, score)[1])
        
            
        draw_text('{}  points'.format(score.points), default_font, C.screen,
                  100, 20, C.DARK_ALLOY_ORANGE)
        draw_text('Record: {}'.format(score.high_score), default_font,
                  C.screen, C.WIDTH_GAME - 100, 20, C.DARK_ALLOY_ORANGE)
        cars_list.update()
        #bonuses_list.update()
        deterministic_carList.update()
        deterministic_rockList.update()

        #deterministic_bananaList.update()
        #deterministic_green_bananaList.update()
        cars_list.draw(C.screen)
        #bonuses_list.draw(C.screen)
        deterministic_carList.draw(C.screen)
        deterministic_rockList.draw(C.screen)
        #deterministic_bananaList.draw(C.screen)
        #deterministic_green_bananaList.draw(C.screen)

        ## collision between "cars" and player  
        #bonus_hit_list = square.collide(bonuses_list)
        deterministic_car_hit_list = square.collide(deterministic_carList)
        deterministic_rock_hit_list = square.collide(deterministic_rockList)

        #deterministic_banana_hit_list = square.collide(deterministic_bananaList)
        #deterministic_green_banana_hit_list = square.collide(deterministic_green_bananaList)

        
        if square.collide(cars_list):
            sound = pygame.mixer.Sound(car_fire_sound)
            pygame.mixer.music.stop()
            sound.play()
            score.points -= 30
            if score.high_score > score.highest_score:
                score.save_highest_score()
            #return 'game_over_screen'
##        elif bonus_hit_list:
##            score.points += 10
##            bonus_hit_list[0].kill()
        elif deterministic_car_hit_list:
            score.points -= 10
            deterministic_car_hit_list[0].kill()
            running = False
        elif deterministic_rock_hit_list:
            score.points -= 20
            deterministic_rock_hit_list[0].kill()
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



 
        #print mouse_pos[0],  mouse_pos[1]
        if not gameTest:  # using webcam coordinate
            mouse_pos = (int(xObject), int(yObject))
            #### Cursor wrapping (not needed)
##            if mouse_pos[0] <= 10:
##                pygame.mouse.set_pos(C.WIDTH_GAME - 10, mouse_pos[1])
##            elif mouse_pos[0] >=C. WIDTH_GAME - 10:
##                pygame.mouse.set_pos(0 + 10, mouse_pos[1])
##            elif mouse_pos[1] <= 10:
##                pygame.mouse.set_pos(mouse_pos[0], C.HEIGHT_GAME - 10)
##            elif mouse_pos[1] >= C.HEIGHT_GAME - 10:
##                pygame.mouse.set_pos(mouse_pos[0], 0 + 10)
            square.set_pos(mouse_pos[0], C.HEIGHT_GAME - 50) # fix the y coordiate
            #square.set_pos(*mouse_pos)
       
        
        for event in pygame.event.get():
            if gameTest:  # use mouse input as input coordinates for game module test
                try:
                    event.type == pygame.MOUSEMOTION
                    mouse_pos = pygame.mouse.get_pos()
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

                square.set_pos(mouse_pos[0], C.HEIGHT_GAME - 50) # fix the y coordiate
                #square.set_pos(*mouse_pos)

            
 
##                if event.type == pygame.MOUSEBUTTONDOWN:
##                    random_x = random.randint(0, WIDTH)
##                    random_y = random.randint(0, HEIGHT)
##                    square.set_pos(random_x, random_y)
##                    pygame.mouse.set_pos([random_x, random_y])
                
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    #global paused
                    paused = not paused
                    if paused:
                        transp_surf = pygame.Surface((C.WIDTH_GAME, C.HEIGHT_GAME))
                        transp_surf.set_alpha(150)
                        screen.blit(transp_surf, transp_surf.get_rect())
                        pygame.mouse.set_visible(True)
                        draw_text('Paused', pygame.font.Font(None, 60), C.screen,
                                  C.WIDTH_GAME / 2, C.HEIGHT_GAME / 4, C.RED)
                if event.key == pygame.K_ESCAPE:
                    #global running
                    running = False
            if event.type == QUIT:
                #global running
                running = False
                #return 'quit'
    else:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    pygame.mouse.set_visible(False)
            elif event.key == pygame.K_f: #F11
                    toggle_fullscreen()
            if event.key == pygame.K_ESCAPE:
                #global running
                runnning = False
            if event.type == QUIT:
                #global running
                runnning = False

    # Limit to 40 frames per second
    #C.clock.tick(40)
                #return 'quit'
    # When out of the main loop, the game is over
    return running




def start_screen():
    pygame.mouse.set_cursor(*pygame.cursors.diamond)
    title_font = pygame.font.Font('freesansbold.ttf', 65)
    big_font = pygame.font.Font(None, 36)
    default_font = pygame.font.Font(None, 28)
    draw_text('TRAFFIC DODGER', title_font, C.screen,
              C.WIDTH_GAME / 2, C.HEIGHT_GAME / 3, C.RED, C.YELLOW)
    draw_text('Use the mouse to dodge the cars', big_font, C.screen,
              C.WIDTH_GAME / 2, C.HEIGHT_GAME / 2, C.GREEN, C.BLACK)
    draw_text("Press any mouse button or S when you're ready",
              default_font, C.screen, C.WIDTH_GAME / 2, C.HEIGHT_GAME / 1.7, C.GREEN, C.BLACK)
    draw_text('Press f to toggle full screen', default_font, C.screen,
              C.WIDTH_GAME / 2, C.HEIGHT_GAME / 1.1, C.GREEN, C.BLACK)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            return 'play'
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                return 'play'
            if event.key == K_f: #K_F11
                toggle_fullscreen()
        if event.type == pygame.QUIT:
            return 'quit'
    return 'start_screen'




def game_over_screen(score):
    #global score
    pygame.mouse.set_visible(True)
    # Text
    draw_text('{}  points'.format(score.points), SETUP.default_font, C.screen,
              100, 20, C.GREEN)
    draw_text('Record: {}'.format(score.high_score), SETUP.default_font, C.screen,
              C.WIDTH_GAME - 100, 20, C.GREEN)
    # Transparent surface
    transp_surf = pygame.Surface((C.WIDTH_GAME, C.HEIGHT_GAME))
    transp_surf.set_alpha(200)
    C.screen.blit(transp_surf, transp_surf.get_rect())

    draw_text("You've Finished!", pygame.font.Font(None, 40), C.screen,
              C.WIDTH_GAME / 2 - 100, C.HEIGHT_GAME / 3, C.RED)
    draw_text('{}  points'.format(score.points), pygame.font.Font(None, 40), C.screen,
              C.WIDTH_GAME / 2 + 110, C.HEIGHT_GAME / 3, C.GREEN)
    #draw_text('To play again press C or any mouse button',
#              SETUP.default_font, C.screen, C.WIDTH_GAME / 2, C.HEIGHT_GAME / 2.1, C.GREEN)
    draw_text('To quit the game press Q', SETUP.default_font, C.screen,
              C.WIDTH_GAME / 2, C.HEIGHT_GAME / 1.9, C.GREEN)
    draw_text('Press F11 to toggle full screen', SETUP.default_font, C.screen,
              C.WIDTH_GAME / 2, C.HEIGHT_GAME / 1.1, C.GREEN, C.BLACK)

    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == K_F11:
                toggle_fullscreen()
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


def toggle_fullscreen():
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


def draw_text(text, font, surface, x, y, main_color, background_color=None):
    textobj = font.render(text, True, main_color, background_color)
    textrect = textobj.get_rect()
    textrect.centerx = x
    textrect.centery = y
    surface.blit(textobj, textrect)
    

def draw_repeating_background(background_img):
    background_rect = background_img.get_rect()
    background_rect_width = background_rect.width
    background_rect_height = background_rect.height
    for i in range(int(math.ceil(C.WIDTH_GAME / background_rect.width))):
        for j in range(int(math.ceil(C.HEIGHT_GAME / background_rect.height))):
            C.screen.blit(background_img, Rect(i * background_rect_width,
                                             j * background_rect_height,
                                             background_rect_width,
                                             background_rect_height))


def random_car(speed):
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
def row_of_cars(num_frames, score):
    bike_row = pygame.sprite.Group()
    rock_row = pygame.sprite.Group()

    if num_frames % 10 == 0:  # every 5 frames of update
        row = num_frames / 10
        if row < SETUP.car_sheet.nrows:
            ## TODO: READ from prerecorded.  (xpos, 0, 0, speed) 4x1000 matrix.
            xgrid = 15 # invisible grid interval
            xpos = np.nonzero(SETUP.car_matrix[row]) # car indices in a row
            for i in range(len(xpos[0])): # indices of 1s
                if xpos[0].size > 0: # check empty
                    #print "int(float(SETUP.car_sheet.nrows)/2): ", int(float(SETUP.car_sheet.nrows)/2)
                    if row < int(float(SETUP.car_sheet.nrows)/2): # half way speed up
                        speed = 10
                    else:
                        speed = 10
                    #print SETUP.car_matrix[row][xpos[0][i]]                                      
                    if SETUP.car_matrix[row][xpos[0][i]] == 1: 
                        bike = OBJECTS.Car(xpos[0][i]*xgrid,0,0, speed)
                        bike_row.add(bike)
                    else: #
                        rock = OBJECTS.Rock(xpos[0][i]*xgrid,0,0, 10)
                        rock_row.add(rock)
       
                    
            score.points += 5  # per line
        else:
            pass
        #tempList.add(bike)
    #return bike_row
    #print 'bike_row:', bike_row,  'rock:', rock_row
    return bike_row, rock_row


def row_of_bananas(num_frames, score):
    banana_row = pygame.sprite.Group()
    green_banana_row = pygame.sprite.Group()
    if num_frames % 10 == 0:  # every 10 frames of update
        row = num_frames / 10
        if row < SETUP.banana_sheet.nrows:
            ## TODO: READ from prerecorded.  (xpos, 0, 0, speed) 4x1000 matrix.
            xgrid = 15
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
                        banana = OBJECTS.Banana(xpos[0][i]*xgrid,0,0, speed)
                        banana_row.add(banana)
                    else: # green banana
                        green_banana = OBJECTS.GreenBanana(xpos[0][i]*xgrid,0,0, speed)
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





