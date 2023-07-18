import pygame
from . import constants as C
import os

class Player(pygame.sprite.Sprite):
    """ This class represents the ball that moves in a circle.
        It derives from the "Sprite" class in Pygame"""
    def __init__(self):
        super(Player, self).__init__()
        self.img = pygame.image.load(os.path.join(C.ASSETS, 'mycar.png'))

#self.img = pygame.Surface((30, 30))
#self.img.fill(C.YELLOW)
        self.rect = self.img.get_rect()
        self.centerx = self.rect.centerx
        self.centery = self.rect.centery

    def set_pos(self, x, y):
        'Positions the player center in x and y location'
        self.rect.x = x - self.centerx
        self.rect.y = y - self.centery

    def collide(self, sprites):
        sprite_hit_list = pygame.sprite.spritecollide(self, sprites, True)
        return sprite_hit_list   # return the first in the list, this should suffice for the purpose.
##        for sprite in sprites:
##            if pygame.sprite.collide_rect(self, sprite):
##                return sprite
