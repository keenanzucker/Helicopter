import os, sys
import pygame 
import random
import alsaaudio, time, audioop
from pygame.locals import *
import time

def load_image(name):
    try:
        image = pygame.image.load(name)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    return image, image.get_rect()

class Helicopter(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) 
        self.image, self.rect = load_image('box.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 50
        self.move = [0,0]
        self.jump=0
        self.timehit=time.time()
        self.burning=0
        self.lives=5

    def update(self):
        if self.rect.top<self.area.top or self.rect.bottom>self.area.bottom:
            self.burning=0
            self.move[1]=0
            self.rect.topleft=10,self.area.bottom/2-32
            self.hit()

        if time.time()-2>self.timehit:  #it has been more than 2 secs since hit
            self.burning=0
            pos=self.rect.topleft
            self.image, self.rect = load_image('box.png')
            self.rect.topleft=pos

        self.cruize()

    def cruize(self):
        if self.jump:
            self.move[1] += -.2
        else:
            self.move[1] += .2
        if abs(self.move[1]) <= .1:
            if self.jump:
                self.move[1]=-1
            else:
                self.move[1] = 1
        self.rect = self.rect.move(self.move)

    def hit(self):
        if not self.burning:
            self.lives-=1
            pos=self.rect.topleft
            self.image, self.rect = load_image('hit.png')
            self.rect.topleft=pos
            self.timehit=time.time()
            self.burning=1

class Wall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) 
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.image, self.rect = load_image('wall.png')    
        self.rect.topright = 0, 0
        self.length=self.rect.bottom
        self.move=[-3,0]
    def update(self):
        self.rect=self.rect.move(self.move)
        if self.rect.right<0:
            self.restart()
    def restart(self):
        self.rect.topleft=self.area.right,random.randint(0,self.area.bottom-self.length)

class Baddie(pygame.sprite.Sprite):
    def __init__(self,heli_pos):
        pygame.sprite.Sprite.__init__(self)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.image, self.rect = load_image('baddie.png')    
        self.rect.topleft = self.area.right,heli_pos
        self.move=[-5,0]
        self.passed=0
    def update(self):
        self.rect=self.rect.move(self.move)
        if self.rect.right<0:
            self.passed=1

def main():
    #audio initialization
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
    inp.setchannels(1)
    inp.setrate(8000)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(160)

    xres=1000
    yres=600
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption('Is it... helicopter?')
    font = pygame.font.Font(None, 36)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))
    pygame.display.flip()

    helicopter = Helicopter()
    wall1=Wall()
    wall2=Wall()
    wall2.rect.topright=xres/2,50       #moves the second wall to half way across the screen to give it a head start
    time_start=time.time()
    clock = pygame.time.Clock()
    sprite_list=[wall1,wall2,helicopter]
    baddie_exists=0
    
    while 1:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                loadPage()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                helicopter.jump=1
            elif event.type == KEYUP and event.key == K_SPACE:
                helicopter.jump=0

        l,data = inp.read()
        if l:
            loudness=audioop.max(data, 2)
        if loudness>=2000:
            helicopter.jump=1
        else:
            helicopter.jump=0
 
 # abs(time.time()-time_start)%10<1 and
        if baddie_exists==0:
            baddie=Baddie(helicopter.rect.top)
            sprite_list.append(baddie)
            baddie_exists=1

        if baddie_exists:
            if baddie.passed==1:
                sprite_list.remove(baddie)
                baddie_exists=0

        hitbox = helicopter.rect.inflate(-5, -5)
        for spryte in sprite_list:
            if hitbox.colliderect(spryte.rect) and spryte!=helicopter:
                helicopter.hit()

        lifeCounter = font.render("Lives: " + str(helicopter.lives), 1, (10, 10, 10))
        allsprites = pygame.sprite.RenderPlain(sprite_list)
        allsprites.update()
        screen.blit(background, (0, 0))
        screen.blit(lifeCounter, (xres*.8, yres*.1))
        allsprites.draw(screen)
        pygame.display.flip()   

def loadPage():

    pygame.init()
    xsize = 1000
    ysize = 600
    screen = pygame.display.set_mode((xsize, ysize))
    pygame.display.set_caption('Is it... helicopter?')
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))
    pygame.display.flip()

    font = pygame.font.Font(None, 76)

    text = font.render('Press Space to Play!', 1, (10,10,10)) 
    textrect = text.get_rect()
    textrect.centerx = screen.get_rect().centerx
    textrect.centery = screen.get_rect().centery
    screen.blit(text, textrect)

    pygame.display.flip()

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                main()

if __name__ == '__main__':
    loadPage()