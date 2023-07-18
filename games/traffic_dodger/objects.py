import pygame
import os
from . import constants as C


class Car(pygame.sprite.Sprite):
    """ This class represents the car that is to dodge or gather.
        It derives from the "Sprite" class in Pygame"""
    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(Car, self).__init__()
        self.image = pygame.image.load(os.path.join(C.ASSETS, 'car.png'))
        self.rect = self.image.get_rect()
        self.rect.x = xpos + 10
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed

        self.set_direction()

    def update(self):
        """ set how cars move """
        #self.hspeed = self.hspeed*1.02
        #self.vspeed = self.vspeed*1.02
        self.rect.x += int(float(self.hspeed))  #
        self.rect.y += int(float(self.vspeed)) #
        if self.collide():
            self.kill()

    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > C.WIDTH_GAME:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > C.HEIGHT_GAME:
            return True

    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)


class OrangeCar(pygame.sprite.Sprite):
    """ This class represents the car that is to dodge or gather.
        It derives from the "Sprite" class in Pygame"""
    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(OrangeCar, self).__init__()
        self.image = pygame.image.load(os.path.join(C.ASSETS, 'orange_car.png'))
        self.rect = self.image.get_rect()
        self.rect.x = xpos+ 10
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed

        self.set_direction()

    def update(self):
        """ set how cars move """
        #self.hspeed = self.hspeed*1.02
        #self.vspeed = self.vspeed*1.02
        self.rect.x += int(float(self.hspeed))  #
        self.rect.y += int(float(self.vspeed)) #
        if self.collide():
            self.kill()

    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > C.WIDTH_GAME:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > C.HEIGHT_GAME:
            return True

    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)



class RandomCar(pygame.sprite.Sprite):
    """ This class represents the car that is to dodge or gather.
        It derives from the "Sprite" class in Pygame"""
    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(RandomCar, self).__init__()
        self.image = pygame.image.load(os.path.join(C.ASSETS, 'car.png'))
        self.rect = self.image.get_rect()
        self.rect.x = xpos+ 10
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed
        
        self.set_direction()
    
    def update(self):
        """ set how cars move """
        self.rect.x += self.hspeed  # constant linear
        self.rect.y += self.vspeed  # constant linear
        if self.collide():
            self.kill()


    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > C.WIDTH_GAME:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > C.HEIGHT_GAME:
            return True

    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)


class Rock(pygame.sprite.Sprite):
    """ This class represents the car that is to dodge or gather.
        It derives from the "Sprite" class in Pygame"""
    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(Rock, self).__init__()
        self.image = pygame.image.load(os.path.join(C.ASSETS, 'rock.png'))
        self.rect = self.image.get_rect()
        self.rect.x = xpos+ 10
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed
        
        self.set_direction()
    
    def update(self):
        """ set how cars move """
        #self.hspeed = self.hspeed*1.02
        #self.vspeed = self.vspeed*1.02
        
        self.rect.x += int(float(self.hspeed)) #
        self.rect.y += int(float(self.vspeed)) #
        if self.collide():
            self.kill()

    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > C.WIDTH_GAME:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > C.HEIGHT_GAME:
            return True

    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)

class Bus(pygame.sprite.Sprite):
    """ This class represents the car that is to dodge or gather.
        It derives from the "Sprite" class in Pygame"""
    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(Bus, self).__init__()
        self.image = pygame.image.load(os.path.join(C.ASSETS, 'bus.png'))
        self.rect = self.image.get_rect()
        self.rect.x = xpos+ 10
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed
        
        self.set_direction()
    
    def update(self):
        """ set how cars move """
        #self.hspeed = self.hspeed*1.05
        #self.vspeed = self.vspeed*1.05
        self.rect.x += int(float(self.hspeed)) # constant linear
        self.rect.y += int(float(self.vspeed)) # constant linear
        if self.collide():
            self.kill()

    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > C.WIDTH_GAME:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > C.HEIGHT_GAME:
            return True

    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)



class Bicycle(pygame.sprite.Sprite):
    """ This class represents the car that is to dodge or gather.
        It derives from the "Sprite" class in Pygame"""
    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(Bicycle, self).__init__()
        self.image = pygame.image.load(os.path.join(C.ASSETS, 'bicycle.png'))
        self.rect = self.image.get_rect()
        self.rect.x = xpos+ 10
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed

        self.set_direction()

    def update(self):
        """ set how cars move """
        #self.hspeed = self.hspeed*1.05
        #self.vspeed = self.vspeed*1.05
        self.rect.x += int(float(self.hspeed)) # constant linear 
        self.rect.y += int(float(self.vspeed)) # constant linear
        if self.collide():
            self.kill()

    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > C.WIDTH_GAME:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > C.HEIGHT_GAME:
            return True

    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)


class Banana(pygame.sprite.Sprite):
    """ This class represents the banana that is to dodge or gather.
        It derives from the "Sprite" class in Pygame"""
    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(Banana, self).__init__()
        self.image = pygame.image.load(os.path.join(C.ASSETS, 'banana.png'))
        self.rect = self.image.get_rect()
        self.rect.x = xpos+ 10
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed

        self.set_direction()

    def update(self):
        """ set how cars move """
        self.hspeed = self.hspeed*1.03
        self.vspeed = self.vspeed*1.03
        self.rect.x += int(float(self.hspeed))  # accelerate linear
        self.rect.y += int(float(self.vspeed))  # accelerate linear
        if self.collide():
            self.kill()

    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > C.WIDTH_GAME:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > C.HEIGHT_GAME:
            return True

    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)

class GreenBanana(pygame.sprite.Sprite):
    """ This class represents the banana that is to dodge or gather.
        It derives from the "Sprite" class in Pygame"""
    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(GreenBanana, self).__init__()
        self.image = pygame.image.load(os.path.join(C.ASSETS, 'green-banana.png'))
        self.rect = self.image.get_rect()
        self.rect.x = xpos+ 10
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed
        
        self.set_direction()
    
    def update(self):
        """ set how cars move """
        self.hspeed = self.hspeed*1.03
        self.vspeed = self.vspeed*1.03
        self.rect.x += int(float(self.hspeed))  # accelerate linear
        self.rect.y += int(float(self.vspeed))  # accelerate linear
        if self.collide():
            self.kill()
            
    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > C.WIDTH_GAME:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > C.HEIGHT_GAME:
            return True

    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)

            

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        """ This class represents the heart that is a bonus.
            It derives from the "Sprite" class in Pygame"""
        super(Bonus, self).__init__()
        self.image = pygame.image.load(os.path.join(C.ASSETS, 'heart.png'))
        #self.image = pygame.Surface((15, 15))
        #self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x - self.rect.centerx
        self.rect.y = y - self.rect.centery

    def update(self):
        """ set how cars move """
        #self.hspeed = self.hspeed*1.03
        #self.vspeed = self.vspeed*1.03
        self.rect.x += 0  #
        self.rect.y += 1  #
        if self.collide():
            self.kill()

    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > C.WIDTH_GAME:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > C.HEIGHT_GAME:
            return True
