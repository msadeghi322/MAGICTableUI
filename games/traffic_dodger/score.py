import pygame
import os
from . import constants as C

class Score:
    # Highest score file
    def __init__(self):
        self.HIGHEST_SCORE_PATH = os.path.join(get_config_dir(), 'highest_score')
        if not os.path.exists(self.HIGHEST_SCORE_PATH):
            with open(self.HIGHEST_SCORE_PATH, 'w') as highest_score_file:
                highest_score_file.write('0')
        # Load highest score
        self.high_score = self.highest_score = self.load_highest_score()
        self.points = 0

    def load_highest_score(self):
        with open(self.HIGHEST_SCORE_PATH, 'r') as highest_score_file:
            highest_score = int(highest_score_file.readlines()[0])
        return highest_score

    def save_highest_score(self):
        with open(self.HIGHEST_SCORE_PATH, 'w') as highest_score_file:
            highest_score_file.write(str(self.high_score))




####################################################
###### from here on relates to car game ########
####################################################
def get_config_dir():
    """Get user's configuration directory."""
    if C.MSWIN:
        confdir = os.environ["APPDATA"]

    elif 'XDG_CONFIG_HOME' in os.environ:
        confdir = os.environ['XDG_CONFIG_HOME']

    else:
        confdir = os.path.join(os.path.expanduser("~"), '.config')

    game_confdir = os.path.join(confdir, "traffic-dodger")

    try:  # Python 2 compatibility
        os.makedirs(game_confdir)
    except OSError as e:
        pass

    return game_confdir
