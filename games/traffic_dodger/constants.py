import pygame
import os


###### dimensions #####################
## pro tip: smaller screen size will improve fps.
WIDTH_GAME = 50*6  # 450
HEIGHT_GAME =36*15  
PLAYER_YOFFSET = 30


#global WIDTH_GAME, HEIGHT_GAME, BLACK, GREEN, DARK_ALLOY_ORANGE, RED, YELLOW, MSWIN, ASSETS, GAME_FPS
#WIDTH_GAME = 640
#HEIGHT_GAME = 360

##### Colors ###########################
BLACK               = (0, 0, 0)
GREEN               = (0, 255, 0)
DARK_ALLOY_ORANGE   = (196, 121, 67)
RED                 = (255, 0, 0)
YELLOW              = (255, 255, 12)


MSWIN = os.name == 'nt'
ASSETS = os.path.join(os.path.dirname(__file__), 'assets')
GAME_FPS = 60 # this may be an upper limit but puttig high num doesn't increase fps any more.
#pygame.init()

# Display
screen = pygame.display.set_mode((WIDTH_GAME, HEIGHT_GAME))
fullscreen = False


# Timing
fps_clock = pygame.time.Clock()

# Used to manage how fast the screen updates
clock = pygame.time.Clock()
