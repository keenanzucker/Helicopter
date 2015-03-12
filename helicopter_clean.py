import os, sys
import pygame 
import random
import alsaaudio, time, audioop
from pygame.locals import *
pygame.init()

def load_image(name):
    """Code to load images from folder into game screen"""
    try:
        image = pygame.image.load(name)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    return image, image.get_rect()

class Game_element(pygame.sprite.Sprite):
    """ Because many of our game elements had redundant code, and because inheritance is cool, we decided to make
    a general template to initialize all our in-game sprites.
    """
    def __init__(self,image_name):
        pygame.sprite.Sprite.__init__(self) 
        self.image, self.rect = load_image(image_name)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

class Helicopter(Game_element):
    """Helicopter class defines the square sprite than can move up and down. Contains a simple physics engine
    and some red invinciblility frames when collisions are detected. Uses cruize method to control physics. 
    """
    def __init__(self):
        super(Helicopter, self).__init__('box.png')
        self.rect.topleft = 10, 50
        self.move = [0,0]
        self.jump=0
        self.timehit=time.time()
        self.burning=0
        self.lives=5

    def update(self):
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

        hitbox = self.rect.inflate(-5, -5)
        for spryte in model.sprite_list:
            if hitbox.colliderect(spryte.rect) and spryte != self:
                self.hit()

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

class Wall(Game_element):
    """The wall class is used two times to create walls that are randomly positioned and move across 
    the game screen at the helicopter. They reset into a new position on the right side of the screen
    after passing through the left side with restart method."""
    def __init__(self):
        """ Initilizes wall class with image and movement to the left """
        super(Wall, self).__init__('wall.png')    
        self.rect.topright = 0, 0
        self.length=self.rect.bottom
        self.move=[-1,0]
    def update(self, level):
        """ Updates position of wall based on level"""
        self.move[0]=-level-1.0
        self.rect=self.rect.move(self.move)
        if self.rect.right<0:
            self.restart()
    def restart(self):
        """ Restarts position of wall to random position on right side of screen."""
        self.rect.topleft=self.area.right,random.randint(0,self.area.bottom-self.length)

class Baddie(Game_element):
    """The Baddie class contains the code for the bad guy that moves across the screen to 
    try to intercept your helicopter sprite. Contains init and update methods only"""
    def __init__(self):
        """Initilizes Baddie's position and movement """
        super(Baddie, self).__init__('baddie.png')   
        self.rect.topleft = self.area.right,0
        self.move = [-5,0]
        self.passed = 0 
        self.exists = 0
    def update(self,helicopter, level):
        """ Update baddies position to right side of screen"""
        self.move[0]=-level-3.0
        if not self.exists and time.time()-model.time_start>2:
            self.rect.topleft = self.area.right, helicopter.rect.top
            self.exists = 1
        if self.exists:
            self.rect=self.rect.move(self.move)
            if self.rect.right < 0:
                self.passed = 1
                self.exists = 0

class Background(object):
    """ Creates background screen and flips the display.  """
    def __init__(self,xres,yres):
        """ Initializes game screen"""
        self.screen = pygame.display.set_mode((1000, 600))
        pygame.display.set_caption('Is it... helicopter?')
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((250, 250, 250))
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

def loadScreen(screen):
    #Creates load screen text
    xres = 1000
    yres = 600
    font = pygame.font.Font(None, 36)
    title_text = font.render('Press Space to Play!', 1, (10,10,10)) 
    textrect = title_text.get_rect()
    textrect.centerx = screen.get_rect().centerx
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

class Model(object):
    """Sets up the model for the game experience """
    def __init__(self,keyboard):
        """Initilizes the many variables to sete up the gameplay """
        #audio setup:
        self.keyboard=keyboard
        if not keyboard:
            self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
            self.inp.setchannels(1)
            self.inp.setrate(8000)
            self.inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            self.inp.setperiodsize(160)

        level = 0

        #screen setup:
        xres=1000
        yres=600
        self.background = Background(xres,yres)

        #initialization of sprites
        self.helicopter = Helicopter()
        self.wall1 = Wall()
        self.wall2 = Wall()
        self.baddie=Baddie()
        self.wall2.rect.topright=xres/2,50   
        self.sprite_list = [self.helicopter,self.wall1,self.wall2,self.baddie]

        #time related shenanigans
        self.time_start = time.time()
        self.clock = pygame.time.Clock()

    def update(self,helicopter,wall1,wall2,baddie, level):
        """Updates the model with the either keyboard or audio input. Sets actions to different keys. 
        Also updates all of the characters."""

        self.clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
            elif self.keyboard and event.type == KEYDOWN and event.key == K_SPACE:
                helicopter.jump=1
            elif self.keyboard and event.type == KEYUP and event.key == K_SPACE:
                helicopter.jump=0
        if not self.keyboard:
            l,data = self.inp.read()
            if l:
                loudness=audioop.max(data, 2)
            if loudness>=800:
                helicopter.jump=1
            else:
                helicopter.jump=0

        self.allsprites = pygame.sprite.RenderPlain(self.sprite_list)
        helicopter.update()
        wall1.update(level)
        wall2.update(level)
        baddie.update(helicopter, level)

    def visualize(self,background, score):
        """ Displays the screen and draws all of the sprites to the screen. """

        background.screen.blit(background.background, (0, 0))
        self.allsprites.draw(background.screen)
        font = pygame.font.Font(None, 36)
        lifeCounter = font.render("Lives: " + str(self.helicopter.lives), 1, (10, 10, 10))
        scoreCounter = font.render("Score: " + str(score), 1, (10, 10, 10))
        background.screen.blit(lifeCounter, (800, 50))
        background.screen.blit(scoreCounter, (600, 50))

        pygame.display.flip()

    def getLevel():
        return level

    def run(self):
        """ Loops continously until the game is quit, updating and visualizing the game"""
        """while 1:
            loadScreen(self.background.screen, )"""
        score = 0
        while 1:
            #loadScreen(self.background.screen)
            score += 1
            level = score / 400.0
            self.update(self.helicopter,self.wall1,self.wall2,self.baddie, level)
            self.visualize(self.background, score)
            if self.helicopter.lives == 0:
                pygame.quit()
            

    
if __name__ == '__main__':
    keyboard=True   #change this to operate the helicopter with audio or keyboard
    model=Model(keyboard)
    model.run()