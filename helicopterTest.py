import os, sys
import pygame 
import random
import alsaaudio, time, audioop
from pygame.locals import *
import time

def load_image(name):
    """Code to load images from folder into game screen"""
    try:
        image = pygame.image.load(name)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    return image, image.get_rect()

class Helicopter(pygame.sprite.Sprite):
    """Helicopter class defines the square sprite than can move up and down. Contains a simple physics engine
    and some red invinsibility frames when collisions are detected. Uses cruize method to control physics. """
    def __init__(self):
        """Initilizes the Helicopter with certain traits"""
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
    def update(self, level):
        """Updates the Helicopter to next position"""
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
        """Physics engine for moving up and down"""
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
        """ Sets up invincibility if Helicopter gets hit. """
        if not self.burning:
            self.lives-=1
            pos=self.rect.topleft
            self.image, self.rect = load_image('hit.png')
            self.rect.topleft=pos
            self.timehit=time.time()
            self.burning=1

class Wall(pygame.sprite.Sprite):
    """The wall class is used four times to create walls that are randomly positioned and move across 
    the game screen at the helicopter. They reset into a new position on the right side of the screen
    after passing through the left side with restart method."""
    def __init__(self,start_pos):
        """ Initilizes wall class with image and movement to the left """
        pygame.sprite.Sprite.__init__(self) 
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.image, self.rect = load_image('wall.png')    
        self.length=self.rect.bottom
        self.move=[-1,0]
        self.rect.topright = start_pos, random.randint(0,self.area.bottom-self.length)
    def update(self,level):
        """ Updates position of wall based on level"""
        self.move[0]=-level-1.0
        self.rect=self.rect.move(self.move)
        if self.rect.right<0:
            self.restart()
    def restart(self):
        """ Restarts position of wall to random position on right side of screen."""
        self.rect.topleft=self.area.right,random.randint(0,self.area.bottom-self.length)

class Baddie(pygame.sprite.Sprite):
    """The Baddie class contains the code for the bad guy that moves across the screen to 
    try to intercept your helicopter sprite. Contains init and update methods only"""
    def __init__(self,heli_pos):
        """Initilizes Baddie's position and movement """
        pygame.sprite.Sprite.__init__(self)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.image, self.rect = load_image('baddie.png')    
        self.rect.topleft = self.area.right,heli_pos
        self.move=[-5,0]
        self.passed=0
    def update(self,level):
        """ Update baddies position to right side of screen"""
        self.rect=self.rect.move(self.move)
        if self.rect.right<0:
            self.passed=1

def main():
    """The main function of the helicopter game. It sets up the load screen and game, creates and updates the sprites, 
    and renders the score and lives."""
    pygame.init()

    #audio initialization code
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
    inp.setchannels(1)
    inp.setrate(8000)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(300)


    #Setting up basic game elements like screen size, clock, and background display.
    xres=1200
    yres=600
    level=0
    audioOn = 0
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((xres, yres))
    pygame.display.set_caption('Is it... helicopter?')
    font = pygame.font.Font(None, 36)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))
    pygame.display.flip()


    #Initialized helicopter and wall classes. 
    helicopter = Helicopter()
    wall0=Wall(xres)
    wall1=Wall(xres+xres/4)
    wall2=Wall(xres/2)
    wall3=Wall(3*xres/4)

    sprite_list=[wall0,wall1,wall2,wall3,helicopter]
    baddie_exists=0


    #Creates load screen text
   # title_font = pygame.font.Font(None, 150)
    title_text = font.render('Press Space to Play!', 1, (10,10,10)) 
    textrect = title_text.get_rect()
    textrect.centerx = screen.get_rect().centerx
    #textrect.centery = screen.get_rect().centery
    textrect.centery = 100
    screen.blit(title_text, textrect)

    buttonText   = font.render('Or Click Button For Audio Control!', 1, (10,10,10))
    buttonPos = buttonText.get_rect()
    buttonPos.centerx = screen.get_rect().centerx
    buttonPos.centery = 250
    screen.blit(buttonText, buttonPos)

    button = pygame.draw.rect(screen, (50,50,150), (xres/2 - 100,350,200,100), 0)
    #screen.blit(button, (100,100))
    pygame.display.flip()

    #Keyboard input for load screen
    breaker=0
    while 1:

        for event in pygame.event.get():
            mousePos = pygame.mouse.get_pos()
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                breaker=1
                break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button.collidepoint(mousePos):
                    print 'COLLIDE'
                    audioOn = 1
                    breaker = 1
                    break
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
        if breaker:
            break

    time_start=time.time()


    #Keyboard input for running game screen
    while 1:
        clock.tick(60)
        score=int(time.time()*10-time_start*10)
        if helicopter.lives == 0:
            main()
         #Code for audio input version of control
        if audioOn == 1:
            l,data = inp.read()
            #print audioop.max(data, 2)
            if l:
                loudness=audioop.max(data, 2)
            if loudness>=1000:
                helicopter.jump=1
            else:
                helicopter.jump=0

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                main()
            elif event.type == KEYDOWN and event.key == K_SPACE and audioOn == 0:
                helicopter.jump=1
            elif event.type == KEYUP and event.key == K_SPACE and audioOn == 0:
                helicopter.jump=0
       

        #Increases speed of walls as game progresses
        if score<400.0:
            level=score/100.0


        #Creates a baddie at position of your character! Scary!
        if baddie_exists==0 and score>100:
            baddie=Baddie(helicopter.rect.top)
            sprite_list.append(baddie)
            baddie_exists=1

        if baddie_exists:
            if baddie.passed==1:
                sprite_list.remove(baddie)
                baddie_exists=0


        #Collision detection for helicopter
        hitbox = helicopter.rect.inflate(-5, -5)
        for spryte in sprite_list: #because sprite was taken
            if hitbox.colliderect(spryte.rect) and spryte!=helicopter:
                helicopter.hit()


        #Rendering of game screen with live updates for score and lives. 
        scoreCounter = font.render("Score: " + str(score), 1, (10, 10, 10))
        lifeCounter = font.render("Lives: " + str(helicopter.lives), 1, (10, 10, 10))
        allsprites = pygame.sprite.RenderPlain(sprite_list)
        allsprites.update(level)
        screen.blit(background, (0, 0))
        screen.blit(lifeCounter, (xres*.8, yres*.1))
        screen.blit(scoreCounter, (xres*.6, yres*.1))
        allsprites.draw(screen)
        pygame.display.flip()   

if __name__ == '__main__':
    main()