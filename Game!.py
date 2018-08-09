########################################################################
################### yiyuan chen's 15-112 project #######################
########################################################################


import pygame
import random
import math
import os
import numpy as np
from pygame.locals import *
from pygame import mixer

#disclaimer: all fonts are downloaded from the internet
#http://www.fontspace.com/ttf

#Globals: colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
YELLOW = (255,255, 153)
SAND = (230, 230, 230)

#Globals: dimensions
SANDDIM = 5 #size of grain of snow falling
CARSPEED = 1

#Globals: ranges
SCREENW = 1200
SCREENH = 300
INTERV = round((SCREENW/10)/2)

############################  sand mode helper  #############################

def detectCollision(sand, walllist):
    for wall in walllist:
        if (abs(wall - sand.x) < SANDDIM/4
            and walllist[wall].y <= sand.y):
            sand.dy = 0
            fixSpacing(sand, walllist, wall)
        #detects collision
        #changes dy to 0 when overlap

############################  helper for collision  #############################

def fixSpacing(sand, walllist, wall):
    w = walllist[wall]
    if (wall-1) in walllist: wleft = walllist[wall-1]
    else: wleft = walllist[wall]
    if (wall+1) in walllist: wright = walllist[wall+1]
    else: wright = walllist[wall]

    #determine distance between grains of snow (sand)
    #if close enough, stack on top
    if wleft.y -w.y >= 2*SANDDIM:
        sand.y += SANDDIM
    elif wright.y -w.y >= 2*SANDDIM:
        sand.x += SANDDIM

############################  sand helper  #############################

def makeSandList(sandlist, color, x, y, w):
    #using normal distribution to look more natural
    xList = np.random.normal(x, 10, 250)
    yList = np.random.normal(y, 5, 250)
    
    for i in range(250):
        posX = round(float(xList[i]))
        posY = round(float(yList[i]))
        sand = Sand(color, posX, posY)
        sand.dx = 0
        sand.dy = 10
        sand.bottom = SCREENH
        sand.walls = w

        sandlist.append(sand)

############################  sand related objects  #############################

class Sand(object):

    #dynamic particles
    
    def __init__(self, color, x, y):
        (self.x, self.y) = (x,y)
        self.color = color
        self.bottom = SCREENH
        self.dx = 0
        self.dy = 5
        self.walls = None

    def update(self):
        self.x += self.dx
        self.y += self.dy
        detectCollision(self, self.walls)

class Wall(object):

    #stationary particles "settled" at the bottom
    
    def __init__(self, color, y):
        self.y = y
        self.color = color

    def getWallY(self):
        return self.y

############################  DRIVE helper  #############################

def changeWall(walllist, pos):
    #pos is x value of car
    #doing ten intervals in total
    #inputs an interval based on pos, returns values to draw
    #for each x pixel. (corresponding y value)
    if pos >= INTERV and pos <= SCREENW - INTERV:
        #normal case
        lowerBound = pos - INTERV
        upperBound = pos + INTERV
    elif pos <= INTERV:
        lowerBound = 0
        upperBound = 2*INTERV
    else:
        lowerBound = SCREENW - 2*INTERV
        upperBound = SCREENW
        
    x = np.linspace(lowerBound, upperBound, upperBound - lowerBound)
    ylist = []
    for i in range(lowerBound, upperBound):
        ylist.append(float(walllist[i].y))
    y = np.array(ylist)
    ax = np.polyfit(x,y,6)
    ay = np.poly1d(ax)
    xlist = np.linspace(x[0], x[-1], upperBound - lowerBound)
    ylist = ay(xlist)
    result = list(ylist)
    return result
    
    #returns a list of best fit values for drawing 

########################## CHANGED #########################

class Vehicle(object):

    def __init__(self, walllist):
        #initialize using list of walls
        self.walllist = walllist
        #track car position
        self.x = 0
        self.y = 0
        #load game image
        self.file = 'blueCar.png'
        #car image from internet
        #http://www.clker.com/cliparts/R/K/W/x/W/V/blue-car-styalized-md.png
        self.width = round(SCREENW/10)
        self.height = round(SCREENH/5)
        self.center = (SCREENW/2 - self.width/2, SCREENH/2 + self.height/2)
        self.img = pygame.transform.scale(
            pygame.image.load(self.file). convert_alpha(),
            (self.width, self.height))
        self.maxIncline = 50
        #speed 
        self.dx = 0
        self.dy = 0


    def changeWall(self):

        #using best fit line to draw 

        walllist = self.walllist
        pos = self.x
        
        if pos >= INTERV and pos <= SCREENW - INTERV:
            #normal case
            lowerBound = pos - INTERV
            upperBound = pos + INTERV
        elif pos <= INTERV:
            lowerBound = 0
            upperBound = 2*INTERV
        else:
            lowerBound = SCREENW - 2*INTERV
            upperBound = SCREENW
        
        x = np.linspace(lowerBound, upperBound, upperBound - lowerBound)
        ylist = []
        for i in range(lowerBound, upperBound):
            ylist.append(float(walllist[i].y))
        y = np.array(ylist)
        ax = np.polyfit(x,y,6)
        ay = np.poly1d(ax)
        xlist = np.linspace(x[0], x[-1], upperBound - lowerBound)
        ylist = ay(xlist)
        result = list(ylist)
        return result
    #returns a short list of best fit values for drawing

    def getAngle(self):
        #gets you the current angle, duhhhhh
        l = self.changeWall()
        if self.x >= INTERV and self.x <= SCREENW - INTERV:
            slope = l[INTERV+1] - l[INTERV]
        elif self.x < INTERV:
            slope = l[self.x + 1] - l[self.x]
        else:
            slope = l[(self.x%len(l)) + 1] - l[self.x%len(l)]
        return math.degrees(math.atan(slope))
    #return in degrees       

    def draw(self, screen):

        #DRAW WALL

        results = self.changeWall()

        if self.x <= (INTERV/2 -1):
            stdY = results[self.x] 
        elif self.x >= SCREENW - INTERV/2 + 1:
            stdY = results[self.x%INTERV]
        else:
            stdY = results[INTERV]

        theta = - self.getAngle()
        #reversed because below the x axis is the first quadrant
        #reverse of the normal cartesian graph
        hyp = math.sqrt(self.width **2 + self.height**2)/2
        plus = hyp*math.sin(math.radians(self.getAngle()))
        
        for x in range(len(results) - 1):
            x1 = x + 1
            y = (SCREENH/2+self.height/2) + (results[x] - stdY) * 10
            y1 = (SCREENH/2+self.height/2) + (results[x1] - stdY) * 10
            pygame.draw.polygon(screen, SAND, [[x1 * 10, SCREENH],
                                                [x1 * 10, y1],
                                                [x * 10, y],
                                                [x * 10, SCREENH]])

        #DRAW CAR
        
        if self.x < (INTERV/2 - 1):
            posx = self.x * (SCREENW / INTERV)
            posy = (SCREENH-self.height)/2

        elif self.x > SCREENW - INTERV/2 + 1:
            posx = (self.x % INTERV) * (SCREENW/INTERV) - self.width
            posy = (SCREENH-self.height)/2

        else:
            posx = (SCREENW-self.width)/2
            posy = (SCREENH-self.height)/2

        #car is drawn with a little error so i corrected it
        #depends on the pos of the car; we start at the very left
        #of the screen at first

        img = pygame.transform.rotate(self.img, theta)
        screen.blit(img, (posx + plus, posy))
        
    def changeVelo(self, dx, dy):
        #change velocity...
        self.dx = dx
        self.dy = dy

    def update(self):
        #change position of car
        self.x += self.dx
        self.y += self.dy


############################  GAME class  #############################

    ###########ENHANCE GAME WITH OBSTACLES ###############
 
def createObstacles(walllist, level):
        #num = how many obstacles
        #level of difficulty
    lb = 3*INTERV
    ub = SCREENW - 2*INTERV

    minheight = int(SCREENH * (4/5) - (level-1)*SANDDIM)
    maxheight = int(SCREENH * (4/5) - (level+9) * SANDDIM)
        
    for i in range(5 + level):
            location = random.randint(lb, ub)
            height = random.randint(maxheight, minheight)
            for j in range(location, location+10):
                walllist[j] = Wall(BLACK, height)
                                        


class Game(object):

    #game template from tutorials online,
    #http://programarcadegames.com
    #but all objects are written by self

    def __init__(self):
        self.mode = 'splash'
        self.walllist = {x: Wall(WHITE, SCREENH) for x in range(SCREENW)}
        self.sandlist = []
        self.sandCount = 0
        self.level = 1
        createObstacles(self.walllist, self.level)
        self.maxSandCount = 121 - self.level * 10
        self.gameWon = False
        self.vehicle = Vehicle(self.walllist)
        #A BUNCH OF BUTTONS
        self.button1c = WHITE
        self.button2c = WHITE
        self.helpTextColor = WHITE
        self.helpLeftArrowColor = WHITE
        self.helpRightArrowColor = WHITE
        self.sandRestartColor = WHITE
        self.initialDriveTime = -1
        self.driveTextColor = WHITE
        self.driveSqrColor = BLACK
        self.helps = ['help1.png','help2.png','help3.png']
        #photos screenshotted by myself
        self.help = 0
        self.automatic = False
        self.modesPos = 'no'
        self.sandContinueColor = WHITE
        self.loserboardColor = WHITE
        self.scoreboardColor = WHITE
        self.maxGameLevel = 10

    def changeLevels(self):
        #re-init without changing some of the things
        #like self.automatic
        self.mode = 'sand'
        self.walllist = {x: Wall(WHITE, SCREENH) for x in range(SCREENW)}
        self.sandlist = []
        self.sandCount = 0
        self.level += 1
        createObstacles(self.walllist, self.level)
        self.maxSandCount = 121 - self.level*10
        self.gameWon = False
        self.vehicle = Vehicle(self.walllist)
        self.button1c = WHITE
        self.button2c = WHITE
        self.helpTextColor = WHITE
        self.helpLeftArrowColor = WHITE
        self.helpRightArrowColor = WHITE
        self.sandRestartColor = WHITE
        self.initialDriveTime = -1
        self.driveTextColor = WHITE
        self.driveSqrColor = BLACK
        self.helps = ['help1.png','help2.png','help3.png']
        self.help = 0
        self.modesPos = 'no'
        self.sandContinueColor = WHITE
        self.loserboardColor = WHITE

    def process(self):

        #KEY PRESSING!!!!!!

############################  winner mode  #############################

        if self.mode == 'carpediem':
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return True
                #SHOWS UP WHEN YOU WIN ALL LEVELS!

############################  ready go mode  #############################

        if self.mode == 'readygo':
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mode = 'modes'
                    #shows up after reading instructions and starts game

############################  example mode  #############################

        if self.mode == 'example':
            #shows example of game
            
            for event in pygame.event.get():
                
                if event.type == pygame.QUIT: return True
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()

                    #basically switching between screens
                    if self.help == 0 and (x >= 10 and x <= 110
                                           and y >= 100 and y <= 200 and
                                           self.help >= 0):
                        self.mode = 'help'
                        
                    elif (x >= 10 and x <= 110 and y >= 100 and y <= 200 and 
                        self.help >= 1):
                        self.help -= 1
                        
                    elif (x >= SCREENW - 100 and x <= SCREENW
                        and y >= 100 and y <= 200 and
                          self.help < len(self.helps) -1):
                        self.help += 1
                        
                elif event.type == pygame.KEYDOWN:
                    # a backup option for switching between modes
                    # advice taken from peer group session, @joe
                    keys = pygame.key.get_pressed()

                    if keys[pygame.K_LEFT] and self.help == 0:
                        self.mode = 'help'
                    elif keys[pygame.K_LEFT] and self.help >= 1:
                        self.help -= 1
                    elif keys[pygame.K_RIGHT] and (self.help <
                                                   len(self.helps) -1):
                        self.help += 1
                    

############################  freeze mode  #############################

        if self.mode == 'freeze':
            for event in pygame.event.get():
            
                if event.type == pygame.QUIT: return True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.automatic:
                        self.mode = 'autodrive'
                    else:
                        self.mode = 'drive'
                    self.initialDriveTime = pygame.time.get_ticks()

############################  sand mode  #############################
            
        if self.mode == 'sand':
            
                for event in pygame.event.get():
            
                    if event.type == pygame.QUIT: return True

                    #Creates sand
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        (x,y) = pygame.mouse.get_pos()

                        #restart
                        if (x >=15 and y >= 15 and x <= 15 + 2*INTERV-30
                            and y <= 15 + 30):
                            self.__init__()

                        #when you're done with dropping snow and ready to
                        #move on to drive mode
                        elif (x >= SCREENW - 2*INTERV + 15 and
                              y >= 15 and
                              x <= SCREENW - 15 and
                              y <= 15 + 30):
                            self.mode = 'freeze'

                        #click is out of range
                        elif y <= 50 or x < 2*INTERV or x > SCREENW - 2*INTERV:
                            pass

                        #click to create piles of snow
                        elif (len(self.sandlist) == 0 and
                              self.sandCount <= self.maxSandCount):
                            self.sandCount += 1
                            makeSandList(self.sandlist, WHITE,
                                         x, y, self.walllist)

                        #in case there are some leftover
                        #and you want to move on to the
                        #next pile
                        elif len(self.sandlist) != 0:
                            if len(self.sandlist) <= 10:
                                self.sandlist = []

                        #done with all sand available
                        elif self.maxSandCount-self.sandCount <= 0:
                            self.mode = 'freeze'
                        
                    elif event.type == pygame.MOUSEMOTION:
                        (x,y) = pygame.mouse.get_pos()

                        #light up the buttonzzzzzz
                        if (x >=15 and y >= 15 and x <= 15 + 2*INTERV-30
                            and y <= 15 + 30):
                            self.sandRestartColor = YELLOW
                            self.sandContinueColor = WHITE
                            
                        elif (x >= SCREENW - 2*INTERV + 15 and
                              y >= 15 and
                              x <= SCREENW - 15 and
                              y <= 15 + 30):
                            self.sandContinueColor = YELLOW
                            self.sandRestartColor = WHITE
                            
                        else:
                            self.sandRestartColor = WHITE
                            self.sandContinueColor = WHITE

##########################  gameover mode  #############################
                        
        if self.mode == 'gameover':

            #shows when gameover
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return True
                elif self.gameWon and event.type == MOUSEBUTTONDOWN:
                    self.mode = 'scoreboard'
                elif not self.gameWon and event.type == MOUSEBUTTONDOWN:
                    self.mode = 'loserboard'

##########################  scoreboard mode  #############################
        if self.mode == 'scoreboard':

            #shows when game is won
            #with option to go to next level

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return True

                elif event.type == MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    if (x >= SCREENW/2 - 60 - 10 and
                        y >= SCREENH/5 - 10 and
                        x <= SCREENW/2 + 50 and
                        y <= SCREENH/5 + 40):
                        self.changeLevels()

                elif event.type == MOUSEMOTION:
                    (x,y) = pygame.mouse.get_pos()
                    if (x >= SCREENW/2 - 60 - 10 and
                        y >= SCREENH/5 - 10 and
                        x <= SCREENW/2 + 50 and
                        y <= SCREENH/5 + 40):
                        self.scoreboardColor = (255,0,0)
                    else:
                        self.scoreboardColor = WHITE
                    

##########################  loserboard mode  #############################
        if self.mode == 'loserboard':

            #when lost...
            
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return True

                elif event.type == MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    if (x >= SCREENW/2 - 60 - 10 and
                        y >= SCREENH/5 - 10 and
                        x <= SCREENW/2 + 50 and
                        y <= SCREENH/5 + 40):
                        self.__init__()

                elif event.type == MOUSEMOTION:
                    (x,y) = pygame.mouse.get_pos()
                    if (x >= SCREENW/2 - 60 - 10 and
                        y >= SCREENH/5 - 10 and
                        x <= SCREENW/2 + 50 and
                        y <= SCREENH/5 + 40):
                        self.loserboardColor = (255,0,0)
                    else:
                        self.loserboardColor = WHITE

##########################  modes mode  #############################
                        
        if self.mode == 'modes':

            #choose between driverless or drive
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return True
                elif event.type == MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    if x <= SCREENW/2:
                        self.automatic = True
                    else:
                        self.automatic = False
                    self.mode = 'sand'
                elif event.type == MOUSEMOTION:
                    (x,y) = pygame.mouse.get_pos()
                    if y >= 0 and y<= SCREENH: 
                        if x <= SCREENW/2:
                            self.modesPos = 'left'
                        else:
                            self.modesPos = 'right'
                    else: self.modesPos = 'no'

########################## autodrive mode  #############################
                    
        if self.mode == 'autodrive':

            #driverless mode

            for event in pygame.event.get():

                curTime = pygame.time.get_ticks()
                if (curTime - self.initialDriveTime)%100:
                    self.vehicle.changeVelo(CARSPEED, 0)
                    
                if event.type == MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    if (x >= SCREENW - 110 and y >= 3 and
                        x <= SCREENW - 30 and y <= 28):
                        self.__init__()
                elif event.type == MOUSEMOTION:
                    (x,y) = pygame.mouse.get_pos()
                    if (x >= SCREENW - 110 and y >= 3 and
                        x <= SCREENW - 30 and y <= 28):
                        self.driveTextColor = BLACK
                        self.driveSqrColor = WHITE
                    else:
                        self.driveTextColor = WHITE
                        self.driveSqrColor = BLACK
            self.vehicle.update()
            
                                        

##########################  drive mode  #############################

        if self.mode == 'drive':

            #drive by self

            for event in pygame.event.get():

                angle = - self.vehicle.getAngle()
            
                if event.type == pygame.QUIT: return True
                
                elif event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()

                    #press up & down

                    if keys[pygame.K_RIGHT]:
                        self.vehicle.changeVelo(CARSPEED, 0)
                    if keys[pygame.K_LEFT]:
                        self.vehicle.changeVelo(-CARSPEED, 0)
                    if angle > 5 and not keys[K_UP]:
                        self.mode = 'gameover'
                    if angle < -5 and not keys[K_DOWN]:
                        self.mode = 'gameover'
                    if abs(angle) < 1 and (keys[K_UP] or keys[K_DOWN]):
                        self.mode = 'gameover'
                elif event.type == pygame.KEYUP:
                    self.vehicle.changeVelo(0,0)
                elif event.type == MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    if (x >= SCREENW - 110 and y >= 3 and
                        x <= SCREENW - 30 and y <= 28):
                        self.__init__()
                elif event.type == MOUSEMOTION:
                    (x,y) = pygame.mouse.get_pos()
                    if (x >= SCREENW - 110 and y >= 3 and
                        x <= SCREENW - 30 and y <= 28):
                        self.driveTextColor = BLACK
                        self.driveSqrColor = WHITE
                    else:
                        self.driveTextColor = WHITE
                        self.driveSqrColor = BLACK
            self.vehicle.update()

                    
            #design car, to drive up the hills

##########################  splash screen ############################
                    
        if self.mode == 'splash':

             for event in pygame.event.get():
            
                if event.type == pygame.QUIT: return True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    (x, y) = pygame.mouse.get_pos()
                    if y >= SCREENH*.4 - 10 and y <= SCREENH*.4 + 40:
                        #at one of the buttons
                        if x >= SCREENW*.55 - 10 and x <= SCREENW*.55 + 190:
                            self.mode = 'modes'
                        elif x >= SCREENW*(3/4) - 10 and x <= SCREENW*(3/4) + 190:
                            self.mode = 'help'
                        
                elif event.type == pygame.MOUSEMOTION:
                    (x, y) = pygame.mouse.get_pos()
                    if y >= SCREENH*.4 - 10 and y <= SCREENH*.4 + 40:
                        #at one of the buttons
                        if x >= SCREENW*.55 - 10 and x <= SCREENW*.55 + 190:
                            self.button1c = BLACK
                            self.button2c = WHITE
                        elif x >= SCREENW*(3/4) - 10 and x <= SCREENW*(3/4) + 190:
                            self.button2c = BLACK
                            self.button1c = WHITE
                        else:
                            self.button1c = WHITE
                            self.button2c = WHITE
                    else:
                        self.button1c = WHITE
                        self.button2c = WHITE

##########################  help screen ############################

        if self.mode == 'help':

            for event in pygame.event.get():
            
                if event.type == pygame.QUIT: return True

                #JUST SOME BUTTONS..

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    if x >= 10 and x <= 110 and y >= 100 and y <= 200:
                        self.mode = 'splash'
                    elif (x >= SCREENW - 100 and x <= SCREENW
                        and y >= 100 and y <= 200):
                        self.mode = 'readygo'
                    elif (x >= 2*SCREENW/3 + 50 and x <= 5*SCREENW/6 + 50
                        and y >= 160 and y <= 200):
                        self.mode = 'example'
                        
                elif event.type == pygame.MOUSEMOTION:
                    (x, y) = pygame.mouse.get_pos()
                    #example text
                    if (x >= 2*SCREENW/3 + 50 and x <= 5*SCREENW/6 + 50
                        and y >= 160 and y <= 200):
                        self.helpTextColor = (255, 0, 0)
                    else: self.helpTextColor = WHITE
                    #left arrow
                    if x >= 10 and x <= 110 and y >= 100 and y <= 200:
                        self.helpLeftArrowColor = (255, 0, 0)
                    else: self.helpLeftArrowColor = WHITE

                    #right arrow
                    if (x >= SCREENW - 100 and x <= SCREENW
                        and y >= 100 and y <= 200):
                        self.helpRightArrowColor = (255, 0, 0)
                    else: self.helpRightArrowColor = WHITE

                elif event.type == pygame.KEYDOWN:

                    keys = pygame.key.get_pressed()

                    if keys[pygame.K_LEFT]:
                        self.mode = 'splash'
                    elif keys[pygame.K_RIGHT]:
                        self.mode = 'readygo'
                            
        return False

    def logic(self):

        #determines when game will end

############################  sand mode  #############################
        
        if self.mode == 'sand':
            for elem in self.sandlist:
                elem.update()
                if elem.dy == 0:
                    self.sandlist.remove(elem)
                    (x,y) = (elem.x, elem.y)
                    self.walllist[x] = Wall(WHITE,
                                            y - SANDDIM)
                    
        elif self.mode == 'autodrive':
            
            if (self.vehicle.x >= SCREENW - INTERV):
                self.mode = 'scoreboard'
            elif abs(self.vehicle.getAngle()) > self.vehicle.maxIncline:
                self.mode = 'gameover'

        elif self.mode == 'drive':
            if (self.vehicle.x >= SCREENW - INTERV):
                self.mode = 'scoreboard'
            elif abs(self.vehicle.getAngle()) > self.vehicle.maxIncline:
                self.mode = 'gameover'

        elif self.level >= self.maxGameLevel:
            self.mode = 'carpediem'
            

############################  splash screen  #############################
        
    def splashScreen(self, screen):
        pygame.font.init()
        img = pygame.transform.scale(
            pygame.image.load('sandsandsand.jpg').convert(),
            (SCREENW, SCREENH))
        #sandsandsand.jpg comes from google
        #http://milen.com/wp-content/uploads/2016/07/art-2270-1300px-sign.jpg
        
        screen.blit(img, (0,0))

        rect1 = (SCREENW*.55 - 10, SCREENH*.4 - 10, 200, 50)
        rect2 = (SCREENW*(3/4) - 10, SCREENH*.4 - 10, 175, 50)
        
        if self.button1c == WHITE: b1 = BLACK
        else: b1 = WHITE
        pygame.draw.rect(screen, b1, rect1)
        if self.button2c == WHITE: b2 = BLACK
        else: b2 = WHITE
        pygame.draw.rect(screen, b2, rect2)
        
        #title
        myfont = pygame.font.Font('28.ttf', 90)
        textsurface = myfont.render("On thin ice", 1, WHITE)
        screen.blit(textsurface, (0.55*SCREENW,20))
        
        #buttons
        buttonfont = pygame.font.Font('28.ttf', 30)
        textsurface = buttonfont.render('start playing', 1, self.button1c)
        screen.blit(textsurface, (SCREENW*.55, SCREENH*.4))

        textsurface = buttonfont.render('Instructions', 1, self.button2c)
        screen.blit(textsurface, (SCREENW*(3/4), SCREENH*.4))

############################  help mode helper  #############################

    def helpScreen(self, screen):
        pygame.font.init()
        myfont = pygame.font.Font('bboron.ttf', 50)
        textsurface = myfont.render("Help is here!", 1, (0, 127, 255))
        screen.blit(textsurface, (round(SCREENW*.4),20))

        (a,b,c) = (0, 127, 255)
        
        b += 20

        somefont = pygame.font.Font('bboron.ttf', 30)
        text = 'Create avalanche by clicking anywhere on screen. Snow'
        textsurface = somefont.render(text, 1, (a, b, c))
        screen.blit(textsurface, (200,80))

        b+= 20
        text = 'will pile up at the bottom of the screen, and you will drive'
        textsurface = somefont.render(text, 1, (a, b, c))
        screen.blit(textsurface, (200,120))

        b+= 20
        text = 'through this landscape one of two modes.' 
        textsurface = somefont.render(text, 1, (a, b, c))
        screen.blit(textsurface, (200,160))

        textsurface = somefont.render('     ((see example))', 1, self.helpTextColor)
        screen.blit(textsurface, (2*SCREENW/3, 160))

        b+= 20
        text = 'Press up, down, left and right to move on sand dunes.'
        textsurface = somefont.render(text, 1, (a, b, c))
        screen.blit(textsurface, (200,200))

        b+= 20
        text = 'You must reach the destination before timer runs out.'
        textsurface = somefont.render(text, 1, (a, b, c))
        screen.blit(textsurface, (200,240))

        largefont = pygame.font.Font('bboron.ttf',100)
        textsurface = largefont.render(' < ', 1, self.helpLeftArrowColor)
        screen.blit(textsurface, (0, SCREENH/4))

        textsurface = largefont.render(' >', 1, self.helpRightArrowColor)
        screen.blit(textsurface, (SCREENW - 100, SCREENH/4))
        

############################  sand mode helper  #############################

    def drawWall(self, screen):
        for x in range(0, SCREENW, 50):
            l = []
            if x > 0:
                l.append((x-2, self.walllist[x-2].y))
            if x+55 <= SCREENW:
                for y in range(x, x+55):
                    l.append((y, self.walllist[y].y))
            else:
                for y in range(x,x+50):
                    l.append((y, self.walllist[y].y))

            #casts these raw data points into array
            points = np.array(l)

            #pairs
            x = points[:,0]
            y = points[:,1]

            #highest of sixth degree polynomial
            a = np.polyfit(x,y,6)
            b = np.poly1d(a)
            aX = np.linspace(x[0], x[-1], 10)
            aY = b(aX)

            #creating list with all the outputs
            #of the sixth degree polynomial
            for i in range(len(aX)-1):
                c = WHITE
                side1 = round(float(aY[i]))
                side2 = round(float(aY[i+1]))
                if i == 0 and abs(side1 - self.walllist[aX[i]].y) >= 2*SANDDIM:
                    side1 = (side1 + self.walllist[aX[i]].y)/2
                if (i == len(aX)- 2 and
                    abs(side2 - self.walllist[aX[i+1]].y) >= 2*SANDDIM):
                    side2 = (side2 + self.walllist[aX[i+1]].y)/2
                pygame.draw.polygon(screen, c, [[round(float(aX[i]+SANDDIM+2)),
                                                 SCREENH],
                                                [round(float(aX[i])),
                                                 SCREENH],
                                                [round(float(aX[i])),
                                                 side1],
                                                [round(float(aX[i]+SANDDIM+2)),
                                                 side2]])


    def display(self, screen):

        if self.mode == 'readygo':
            screen.fill(BLACK)
            largefont = pygame.font.Font('28.ttf', 100)

            text = 'Click to make snow'
            textsurface = largefont.render(text, 1, WHITE)
            screen.blit(textsurface, (SCREENW/6, SCREENH/3))

            

############################  carpediem mode draw  ############################

        if self.mode == 'carpediem':
            pygame.font.init()

            for i in range(round(SCREENW/80)):
                for j in range(round(SCREENH/100)):
                    img = pygame.transform.scale(
                    pygame.image.load('kosbie.jpg').convert(),
                    (80, 100))
                    #photo from kosbie's website:
                    #http://www.kosbie.net/cmu/dkosbie.jpg
                    screen.blit(img, (i*80, j*100))

            largefont = pygame.font.Font('oj.ttf', 110)

            text = "BIE-KOS I'M HAPPY!"
            textsurface = largefont.render(text, 1, WHITE)
            screen.blit(textsurface, (SCREENW/6, SCREENH/3))

############################  scoreboard mode draw  #############################

        if self.mode == 'scoreboard':
            screen.fill(BLACK)

            largefont = pygame.font.Font('bboron.ttf', 100)

            text = 'Current level: %d'%self.level
            textsurface = largefont.render(text, 1, WHITE)
            screen.blit(textsurface, (SCREENW/6, SCREENH/3))

            smol = pygame.font.Font('pbold.ttf', 26)

            pygame.draw.rect(screen, self.scoreboardColor,
                             (SCREENW/2 - 60 - 10,
                              SCREENH/5 - 10,
                              130, 50))
            pygame.draw.rect(screen, BLACK, (SCREENW/2 - 60 - 5,
                                             SCREENH/5 - 5,
                                             120, 40))

            text = 'Continue'
            textsurface = smol.render(text, 1, self.scoreboardColor)
            screen.blit(textsurface, (SCREENW/2 - 60, SCREENH/5))
            

############################  loserboard mode draw  #############################

        if self.mode == 'loserboard':

            #shows when lost
            
            screen.fill(BLACK)

            largefont = pygame.font.Font('pbold.ttf', 50)

            text = ' Highest record: %d'%self.level
            textsurface = largefont.render(text, 1, YELLOW)
            screen.blit(textsurface, (SCREENW/3, SCREENH/3))

            text = 'Mileage: %d'%self.vehicle.x
            textsurface = largefont.render(text, 1, YELLOW)
            screen.blit(textsurface, (SCREENW/2.5 - 10, SCREENH/3 + 50))

            smol = pygame.font.Font('pbold.ttf', 30)

            pygame.draw.rect(screen, self.loserboardColor,
                             (SCREENW/2 - 60 - 10,
                              SCREENH/5 - 10,
                              130, 50))
            pygame.draw.rect(screen, BLACK, (SCREENW/2 - 60 - 5,
                                             SCREENH/5 - 5,
                                             120, 40))

            text = ' restart'
            textsurface = smol.render(text, 1, self.loserboardColor)
            screen.blit(textsurface, (SCREENW/2 - 60, SCREENH/5))
            


############################  example mode draw  #############################

        if self.mode == 'example':
            screen.fill(BLACK)
            pygame.font.init()
            img = pygame.transform.scale(
                pygame.image.load(self.helps[self.help]).convert(),
                (SCREENW, SCREENH))
            screen.blit(img, (0, 0))

            largefont = pygame.font.Font('bboron.ttf',100)
            smolfont = pygame.font.Font('pbold.ttf',30)

            #all the buttons

            if self.help == 0: 
                text = 'Driverless mode is less challenging.'
                textsurface = smolfont.render(text, 1, (0,89,179))
                screen.blit(textsurface, (SCREENW/20, SCREENH/16))

                text = '(Highly recommended for first timers)'
                textsurface = smolfont.render(text, 1, (0,89,179))
                screen.blit(textsurface, (SCREENW/20, SCREENH/16 + 40))

                text = 'Driver mode requires more skill.'
                textsurface = smolfont.render(text, 1, (77, 165,255))
                screen.blit(textsurface, ((SCREENW/2) + SCREENW/20,
                                          SCREENH/16))
                textsurface = largefont.render(' < ', 1, (0,255,255))
                screen.blit(textsurface, (0, SCREENH/4))
    
                textsurface = largefont.render(' >', 1, (0,255,255))
                screen.blit(textsurface, (SCREENW - 100, SCREENH/4))

            elif self.help == 1:
                img = pygame.transform.scale(
                    pygame.image.load('cursor.png').convert_alpha(),
                    (20, 20))
                #cursor img from internet
                #http://www.freeiconspng.com/free-images/cursor-png-1129
                screen.blit(img, (SCREENW/2 -20, SCREENH/2 - 30))
                
                text = 'Click on screen to create relatively smooth landscape. Your car will'
                textsurface = smolfont.render(text, 1, WHITE)
                screen.blit(textsurface, (2*INTERV + 10, SCREENH/4 - 15))

                text = 'crash if the climb is too steep. The white glaciers are obstacles.'
                textsurface = smolfont.render(text, 1, WHITE)
                screen.blit(textsurface, (2*INTERV + 10, SCREENH/4 + 40 - 30))

                textsurface = largefont.render(' < ', 1, (0,255,255))
                screen.blit(textsurface, (0, SCREENH/4))

                textsurface = largefont.render(' >', 1, (0,255,255))
                screen.blit(textsurface, (SCREENW - 100, SCREENH/4))

            elif self.help == 2:
                text = 'In drive mode, press UP, DOWN, LEFT and RIGHT to control vehicle.'
                textsurface = smolfont.render(text, 1, BLACK)
                screen.blit(textsurface, (3*INTERV + 50, 6*SCREENH/7))
                textsurface = largefont.render(' < ', 1, (0,255,255))
                screen.blit(textsurface, (0, SCREENH/4))


############################  modes mode draw  #############################

        elif self.mode == 'modes':

            #choose between modes
            
            screen.fill(BLACK)
            pygame.font.init()
            somefont = pygame.font.Font('bboron.ttf', 30)

            textColor1 = WHITE
            textColor2 = WHITE

            if self.modesPos == 'left':
                pygame.draw.rect(screen, WHITE, (0,0, SCREENW/2, SCREENH))
                textColor1 = BLACK
            elif self.modesPos == 'right':
                pygame.draw.rect(screen, WHITE, (SCREENW/2, 0, SCREENW, SCREENH))
                textColor2 = BLACK
                
            text = 'Driverless mode'
            textsurface = somefont.render(text, 1, textColor1)
            screen.blit(textsurface, (SCREENW/6, SCREENH/2 - 25))

            text = 'Driver mode'
            textsurface = somefont.render(text, 1, textColor2)
            screen.blit(textsurface, (SCREENW*(2/3), SCREENH/2 - 25))

############################  gameover mode draw  #############################

        elif self.mode == 'gameover':
            pygame.font.init()
            somefont = pygame.font.Font('bboron.ttf', 30)
            text = 'GAMEOVER'
            textsurface = somefont.render(text, 1, WHITE)
            screen.blit(textsurface, (SCREENW/4, SCREENH/2 - 25))
            
############################  sand mode draw  #############################

        elif self.mode == 'sand':
            pygame.font.init()
            img = pygame.transform.scale(
                pygame.image.load('litsky.jpg').convert(),
                (SCREENW, SCREENH))
            #litsky.jpg comes from google
            #http://milen.com/wp-content/uploads/2016/07/art-2270-1300px-sign.jpg

            screen.blit(img, (0, 0))

            #draw walls

            for sand in self.sandlist:
                (x, y) = (sand.x, sand.y)
                r = pygame.Rect(x,y,SANDDIM, SANDDIM)
                pygame.draw.rect(screen, WHITE, r)
            self.drawWall(screen)

            #draw bounds

            pygame.draw.rect(screen, BLACK, (0, 0, 2*INTERV, SCREENH))
            pygame.draw.rect(screen, BLACK, (SCREENW - 2*INTERV, 0, 2*INTERV,
                                             SCREENH))

            pygame.draw.rect(screen, BLACK, (0, 0, SCREENW, 60))
            
            somefont = pygame.font.Font('bboron.ttf', 25)
            text = 'There are %d loads of snow leftover!'%(self.maxSandCount -
                                                           self.sandCount + 1)
            textsurface = somefont.render(text, 1, WHITE)
            screen.blit(textsurface, (SCREENW/3 -10, 13))

            pygame.draw.rect(screen, self.sandRestartColor, (15, 15,
                                                             2*INTERV-30, 30))
            pygame.draw.rect(screen, self.sandContinueColor,
                             (SCREENW - 2*INTERV + 15, 15, 2*INTERV- 30, 30))

            somefont = pygame.font.Font('bboron.ttf', 15)
            text = '  restart'
            textsurface = somefont.render(text, 1, BLACK)
            screen.blit(textsurface, (20,20))

            somefont = pygame.font.Font('bboron.ttf', 15)
            text = ' continue'
            textsurface = somefont.render(text, 1, BLACK)
            screen.blit(textsurface, (SCREENW - 2*INTERV + 20,20))

############################  splash mode  #############################

        elif self.mode == 'splash':
            #called helper
            self.splashScreen(screen)
            
############################  autodrive mode draw  #############################

        elif self.mode == 'autodrive' or self.mode == 'drive':

            theta = - self.vehicle.getAngle()

            #the idea of importing a sky image
            #was inspired by brian scheuermann

            img = pygame.transform.scale(pygame.image.load('desertsky.jpg').convert(),
                                         (2*SCREENW, 2*SCREENW))
            #sky from internet
            #http://1.bp.blogspot.com/-2RE9pBrEy4k/T_xWt9bHY8I/
            #AAAAAAAAH-w/p44pbhRZimc/s1600/Copy+of+July+2012+004.jpg

            #rotate sky till fits with the angle
            img = pygame.transform.rotate(
                img,
                theta)
            screen.blit(img, (-SCREENW/2, -SCREENW))

            self.vehicle.draw(screen)

            pygame.draw.rect(screen, WHITE, (0, 0, 30, SCREENH))
            pygame.draw.rect(screen, WHITE, (SCREENW-30, 0, 30, SCREENH))
            pygame.draw.line(screen, BLACK, (30, 30), (SCREENW-30, 30), 10)
            pygame.draw.line(screen, BLACK, (30, 30), (30, SCREENH), 5)
            pygame.draw.line(screen, BLACK, (SCREENW-30, 30),
                             (SCREENW-30, SCREENH), 5)

            pygame.draw.rect(screen, WHITE, (0, 0, SCREENW, 30))
            
            
            somefont = pygame.font.Font('bboron.ttf', 15)
            text = 'Miles to travel: %d'%(SCREENW - self.vehicle.x -INTERV)
            textsurface = somefont.render(text, 1, BLACK)
            screen.blit(textsurface, (SCREENW/3 -10, 5))

            time = 'Time passed: %d years'%((pygame.time.get_ticks()-
                                            self.initialDriveTime)//1000)

            textsurface = somefont.render(time, 1, BLACK)
            screen.blit(textsurface, (2*SCREENW/3, 5))

            pygame.draw.rect(screen, self.driveTextColor,
                             (SCREENW - 110, 3, 80, 25))
            pygame.draw.rect(screen, self.driveSqrColor,
                             (SCREENW - 105, 5, 70, 20))

            textsurface = somefont.render('restart', 1, self.driveTextColor)
            screen.blit(textsurface, (SCREENW - 100, 5))

            ########## HINT HINT HINT HINT ###########
            if self.mode == 'drive' and self.vehicle.x <= SCREENW/4:
                reminder = pygame.font.Font('pbold.ttf', 30)
                text = ''
                if theta > 1:
                    text = 'up'
                elif theta < -1:
                    text = 'down'
                textsurface = reminder.render(text, 1, WHITE)
                screen.blit(textsurface, (SCREENW/2, 50))
                #creates hint when about to go uphill
            
            pygame.display.flip()


##########################  help screen ############################
                        
        elif self.mode == 'help':
            screen.fill(BLACK)
            self.helpScreen(screen)

##########################  freeze screen ############################

        elif self.mode == 'freeze':
            somefont = pygame.font.Font('bboron.ttf', 30)
            text = 'CLICK ANYWHERE TO START DRIVING!'
            textsurface = somefont.render(text, 1, WHITE)
            screen.blit(textsurface, (SCREENW/4, SCREENH/2 - 25))
            
        pygame.display.flip()
            

def main():
    pygame.init()
    size = [SCREENW, SCREENH]
    screen = pygame.display.set_mode(size)

    game= Game()
    
    pygame.mouse.set_visible(True)
    done = False
    clock = pygame.time.Clock()

    while not done:
        done = game.process()
        game.logic()
        game.display(screen)
        if (game.mode == 'sand' or game.mode == 'drive'
            or game.mode == 'autodrive'):
            pygame.display.set_caption('Level %d'%game.level)
        else:
            pygame.display.set_caption('* On Thin Ice *')
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
