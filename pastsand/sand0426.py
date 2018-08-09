import pygame
import random
import math
import os
import numpy as np
from pygame.locals import *
from pygame import mixer
import scipy

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
YELLOW = (255,255, 153)
SAND = (237, 201, 175)
SANDDIM = 5
CARSPEED = 1

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
    if wleft.y -w.y >= 2*SANDDIM:
        sand.y += SANDDIM
    elif wright.y -w.y >= 2*SANDDIM:
        sand.x += SANDDIM

############################  sand helper  #############################

def makeSandList(sandlist, color, x, y, w):
    xList = np.random.normal(x, 10, 250)
    yList = np.random.normal(y, 5, 250)
    for i in range(250):
        posX = round(float(xList[i]))
        posY = round(float(yList[i]))
 #       posX = random.randrange(x-30, x+30)
 #       posY = random.randrange(y-10, y+10)
        sand = Sand(color, posX, posY)
        sand.dx = 0
        sand.dy = 10
        sand.bottom = SCREENH
        sand.walls = w

        sandlist.append(sand)

############################  sand related objects  #############################

class Sand(object):
    
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
    
    def __init__(self, color, y):
        self.y = y
        self.color = color

    def getWallY(self):
        return self.y

########0423 VERSION HAS A VERY DIFFERENT HILLS & VEHICLE CLASS######

############################  DRIVE mode  #############################

def changeWall(walllist, pos):
    #pos is x value of car
    #doing ten intervals in total
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
        #THIS MAY BE USED LATER
        self.fuel = 100


    def changeWall(self):

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
        l = self.changeWall()
        if self.x >= INTERV and self.x <= SCREENW - INTERV:
            slope = l[INTERV+1] - l[INTERV]
        elif self.x < INTERV:
            slope = l[self.x + 1] - l[self.x]
        else:
 #           epsilon = SCREENW-INTERV
#            slope = l[self.x - epsilon + 1] - l[self.x - epsilon - 1]
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

        img = pygame.transform.rotate(self.img, theta)
        screen.blit(img, (posx + plus, posy))
        
    def changeVelo(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def update(self):
        self.x += self.dx
        self.y += self.dy
        
############################  GAME class  #############################

class selfDriver(Vehicle):

    #init, changeWall, change draw

    def isSafe(self):
        if (self.dy == -1 and self.getAngle()%360 < 180
              and self.getAngle()%360 > 5):
            #user presses downward key
            #slope is negative
            return True
 #       elif (self.dy == 1 and self.getAngle())
            

 #   def draw(self, screen):


############################  GAME class  #############################

    ###########ENHANCE GAME WITH OBSTACLES #########
 
def createObstacles(walllist, level):
        #num = how many obstacles
        #level of difficulty
    lb = 2*INTERV
    ub = SCREENW - 2*INTERV

    minheight = int(SCREENH * (2/3) - (level-1)*SANDDIM)
    maxheight = int(SCREENH * (2/3) - (level+9) * SANDDIM)
        
    for i in range(5 + level):
            location = random.randint(lb, ub)
            height = random.randint(maxheight, minheight)
            for j in range(location, location+10):
                walllist[j] = Wall(BLACK, height)
                                        

class Game(object):

    def __init__(self):
        self.mode = 'splash'
        (self.r, self.g, self.b)= (64,224,208)
        self.walllist = {x: Wall((self.r, self.g, self.b),
                                 SCREENH) for x in range(SCREENW)}
        self.sandlist = []
        self.sandCount = 0
        self.level = 1
        createObstacles(self.walllist, self.level)
        self.maxSandCount = self.level * 5
        self.gameWon = False
        self.vehicle = Vehicle(self.walllist)
 #       self.road = Road(self.vehicle.x, self.walllist)
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

    def process(self):

        #KEY PRESSING!!!!!!
        

############################  example mode  #############################

        if self.mode == 'example':
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    if self.help == 0 and (x >= 10 and x <= 110 and y >= 100 and y <= 200 and
                                           self.help >= 0):
                        self.mode = 'help'
                    elif (x >= 10 and x <= 110 and y >= 100 and y <= 200 and 
                        self.help >= 1):
                        self.help -= 1
                    elif (x >= SCREENW - 100 and x <= SCREENW
                        and y >= 100 and y <= 200 and
                          self.help < len(self.helps) -1):
                        self.help += 1

############################  freeze mode  #############################

        if self.mode == 'freeze':
            for event in pygame.event.get():
            
                if event.type == pygame.QUIT: return True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mode = 'drive'
                    self.initialDriveTime = pygame.time.get_ticks()

############################  sand mode  #############################
            
        if self.mode == 'sand':
                for event in pygame.event.get():
            
                    if event.type == pygame.QUIT: return True
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        (x,y) = pygame.mouse.get_pos()
                        if x >= 15 and y >= 15 and x <= 70+15 and y <= 15+30:
                            self.__init__()
                        elif y <= 50 or x < 2*INTERV or x > SCREENW - 2*INTERV:
                            pass
                        elif (len(self.sandlist) == 0 and
                              self.sandCount <= self.maxSandCount):
                            self.sandCount += 1
                            (self.r, self.g, self.b) = ((self.r+19)%255, (self.g)%255,
                                                        (self.b)%255)
                            makeSandList(self.sandlist, (self.r, self.g, self.b),
                                         x, y, self.walllist)
                        elif len(self.sandlist) != 0:
                            if len(self.sandlist) <= 10:
                                self.sandlist = []
                    #elif self.gameWon == True: #up to the next level, init
#                       (self.r, self.g, self.b)= (64,224,208)
#                       self.walllist = {x: Wall((self.r, self.g, self.b),
#                                                SCREENH) for x in range(SCREENW)}
#                       self.sandlist = []
#                       self.sandCount = 0
#                       self.level += 1
#                       self.maxSandCount = self.level * 50
#                       self.gameWon = False

                        elif self.maxSandCount-self.sandCount <= 0:
                            self.mode = 'freeze'
                        
                    elif event.type == pygame.MOUSEMOTION:
                        (x,y) = pygame.mouse.get_pos()
                        if x >= 15 and y >= 15 and x <= 70+15 and y <= 15+30:
                            self.sandRestartColor = YELLOW
                        else: self.sandRestartColor = WHITE

##########################  gameover mode  #############################
        if self.mode == 'gameover':
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return True
                elif event.type == MOUSEBUTTONDOWN:
                    self.mode = 'splash'

##########################  drive mode  #############################

        if self.mode == 'drive':

            for event in pygame.event.get():
            
                if event.type == pygame.QUIT: return True
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:                       
                        self.vehicle.changeVelo(CARSPEED, 0)
                    if event.key == pygame.K_LEFT:
                        self.vehicle.changeVelo(-CARSPEED, 0)
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
                            self.mode = 'sand'
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

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    if x >= 10 and x <= 110 and y >= 100 and y <= 200:
                        self.mode = 'splash'
                    elif (x >= SCREENW - 100 and x <= SCREENW
                        and y >= 100 and y <= 200):
                        self.mode = 'sand'
                    elif (x >= 2*SCREENW/3 and x <= 5*SCREENW/6
                        and y >= 160 and y <= 200):
                        self.mode = 'example'
                        
                elif event.type == pygame.MOUSEMOTION:
                    (x, y) = pygame.mouse.get_pos()
                    #example text
                    if (x >= 2*SCREENW/3 and x <= 5*SCREENW/6
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
                            
        return False

    def logic(self):

############################  sand mode  #############################
        
        if self.mode == 'sand':
            for elem in self.sandlist:
                elem.update()
                if elem.dy == 0:
                    self.sandlist.remove(elem)
                    (x,y) = (elem.x, elem.y)
                    self.walllist[x] = Wall((self.r, self.g, self.b),
                                            y - SANDDIM)
        elif self.mode == 'drive':
            if (self.vehicle.x >= SCREENW - INTERV
                or abs(self.vehicle.getAngle()) > self.vehicle.maxIncline):
                self.mode = 'gameover'

############################  splash screen  #############################
        
    def splashScreen(self, screen):
        pygame.font.init()
        #can't get my words to show up...
        img = pygame.transform.scale(
            pygame.image.load('sandsandsand.jpg').convert(),
            (SCREENW, SCREENH))
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
        myfont = pygame.font.Font('oj.ttf', 70)
        textsurface = myfont.render("It's time for desert!", 1, BLACK)
        screen.blit(textsurface, (round(SCREENW/2),20))
        
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
        textsurface = myfont.render("Help is here!", 1, YELLOW)
        screen.blit(textsurface, (round(SCREENW*.4),20))

        (a,b,c) = YELLOW
        
        a -= 20

        somefont = pygame.font.Font('bboron.ttf', 30)
        text = 'Create Sand by clicking anywhere on the sand screen.'
        textsurface = somefont.render(text, 1, (a, b, c))
        screen.blit(textsurface, (200,80))

        a-= 20
        text = 'Sand will pile up at the bottom of the screen, and this'
        textsurface = somefont.render(text, 1, (a, b, c))
        screen.blit(textsurface, (200,120))

        a-= 20
        text = 'will be the path that you drive over.'
        textsurface = somefont.render(text, 1, (a, b, c))
        screen.blit(textsurface, (200,160))

        textsurface = somefont.render('((see example))', 1, self.helpTextColor)
        screen.blit(textsurface, (2*SCREENW/3, 160))

        a-= 20
        text = 'Press up, down, left and right to move on sand dunes.'
        textsurface = somefont.render(text, 1, (a, b, c))
        screen.blit(textsurface, (200,200))

        a-= 20
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
            points = np.array(l)
            x = points[:,0]
            y = points[:,1]
            a = np.polyfit(x,y,6)
            b = np.poly1d(a)
            aX = np.linspace(x[0], x[-1], 10)
            aY = b(aX)
            for i in range(len(aX)-1):
                c = (self.r, self.g, self.b)
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

############################  example mode draw  #############################

        if self.mode == 'example':
            screen.fill(BLACK)
            pygame.font.init()
            #can't get my words to show up...
            img = pygame.transform.scale(
                pygame.image.load(self.helps[self.help]).convert(),
                (SCREENW, SCREENH))
            screen.blit(img, (0, 0))

            largefont = pygame.font.Font('bboron.ttf',100)
            smolfont = pygame.font.Font('28.ttf',40)

            if self.help == 0: 
                img = pygame.transform.scale(
                    pygame.image.load('cursor.png').convert_alpha(),
                    (20, 20))
                screen.blit(img, (SCREENW/2 + 20, SCREENH/2))

                text = 'You can click anywhere on the screen to drop sand'
                textsurface = smolfont.render(text, 1, BLACK)
                screen.blit(textsurface, (SCREENW/6, SCREENH/3))

            elif self.help == 1:
                text = 'Click to enter drive mode after designing sand dunes'
                textsurface = smolfont.render(text, 1, YELLOW)
                screen.blit(textsurface, (SCREENW/6, SCREENH/4))

            elif self.help == 2:
                text = 'Press RIGHT LEFT UP and DOWN to drive'
                textsurface = smolfont.render(text, 1, YELLOW)
                screen.blit(textsurface, (SCREENW/3 + 100, 6*SCREENH/7))

            
            textsurface = largefont.render(' < ', 1, YELLOW)
            screen.blit(textsurface, (0, SCREENH/4))

            textsurface = largefont.render(' >', 1, YELLOW)
            screen.blit(textsurface, (SCREENW - 100, SCREENH/4))

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
            screen.fill((255-self.r, 255-self.g, 255-self.b))
            for sand in self.sandlist:
                (x, y) = (sand.x, sand.y)
                r = pygame.Rect(x,y,SANDDIM, SANDDIM)
                pygame.draw.rect(screen, (self.r, self.g, self.b), r)
            self.drawWall(screen)

            pygame.draw.rect(screen, BLACK, (0, 0, 2*INTERV, SCREENH))
            pygame.draw.rect(screen, BLACK, (SCREENW - 2*INTERV, 0, 2*INTERV,
                                             SCREENH))

            pygame.draw.rect(screen, BLACK, (0, 0, SCREENW, 60))
            
            somefont = pygame.font.Font('bboron.ttf', 25)
            text = 'There are %d loads of sand leftover!'%(self.maxSandCount -
                                                           self.sandCount + 1)
            textsurface = somefont.render(text, 1, WHITE)
            screen.blit(textsurface, (SCREENW/3 -10, 13))

            pygame.draw.rect(screen, self.sandRestartColor, (15, 15, 70, 30))

            somefont = pygame.font.Font('bboron.ttf', 15)
            text = 'restart'
            textsurface = somefont.render(text, 1, BLACK)
            screen.blit(textsurface, (20,20))

############################  splash mode  #############################

        elif self.mode == 'splash':
            self.splashScreen(screen)
            
############################  drive mode draw  #############################

        elif self.mode == 'drive':

            theta = - self.vehicle.getAngle()

            #the idea of importing a sky image
            #was inspired by brian scheuermann

            img = pygame.transform.scale(pygame.image.load('desertsky.jpg').convert(),
                                         (2*SCREENW, 2*SCREENW))

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

            time = 'Time passed: ' + str((pygame.time.get_ticks()
                                          - self.initialDriveTime)//1000)

            textsurface = somefont.render(time, 1, BLACK)
            screen.blit(textsurface, (2*SCREENW/3, 5))

            pygame.draw.rect(screen, self.driveTextColor,
                             (SCREENW - 110, 3, 80, 25))
            pygame.draw.rect(screen, self.driveSqrColor,
                             (SCREENW - 105, 5, 70, 20))

            textsurface = somefont.render('restart', 1, self.driveTextColor)
            screen.blit(textsurface, (SCREENW - 100, 5))
            
 #           self.road.draw(screen)
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
    
    pygame.display.set_caption('Loads of Sand = %d'%game.sandCount)
    pygame.mouse.set_visible(True)
    done = False
    clock = pygame.time.Clock()

    while not done:
        done = game.process()
        game.logic()
        game.display(screen)
        pygame.display.set_caption('SandSandSand')
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
