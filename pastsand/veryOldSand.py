import pygame
import random
import os
import numpy as np
from pygame.locals import *
import scipy

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
YELLOW = (64,224,208)
SANDDIM = 5

SCREENW = 1200
SCREENH = 300

def detectCollision(sand, walllist):
    for wall in walllist:
        if (abs(wall - sand.x) < SANDDIM/4
            and walllist[wall].y <= sand.y):
            sand.dy = 0
            fixSpacing(sand, walllist, wall)
        #detects collision
        #changes dy to 0 when overlap

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

class SpriteSheet(object):
    #Using template from
    #http://programarcadegames.com/python_examples/f.php?file=platform_moving.py

    spriteSheet = None

    def __init__(self, fileName):
        self.spriteSheet = pygame.image.load(fileName).convert()

    def getImage(self, x, y, width, height):
        img = pygame.Surface([width, height]).convert()
        img.blit(self.spriteSheet, (0,0), (x, y, width, height))
        img.set_colorkey(BLACK)

        return img

class Hills(pygame.sprite.Sprite):

    #Using template from
    #http://programarcadegames.com/python_examples/f.php?file=platform_moving.py
    
    def __init__(self, walllist, starting, ending):

        pygame.sprite.Sprite.__init__(self)

        self.polygon = [[ending, SCREENH],
                        [startning, SCREENH],
                        [starting, round(float(walllist[starting].y))],
                        [ending, round(float(walllist[ending].y))]]

        self.slope = float(walllist[ending].y) - float(walllist[starting].y))
        self.dx = 0
        self.dy = 0

        self.level = None
        self.vehicle = None

    def update(self):

        maxH = self.vehicle.maxHeight
        
        self.x += self.dx

        hit = pygame.sprite.collide_rect(self, self.vehicle)

        if hit and maxH < self.slope:
            #if collides, check maxH
            #if greater than maxH, then do not update pos
            #if yes, then update pos
            self.vehicle.dx = 0
            self.vehicle.dy = 0

        elif hit and maxH >= self.slope:
            self.y += self.slope



class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, line):
        pygame.sprite.Sprite.__init__(self)

        car = SpriteSheet('blueCar.png')
        
        self.width = SCREENW/10
        self.height = SCREENH/5
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.maxheight = SANDDIM

        self.image = car.get_image(0, 0, 66, 90)

        self.rect = self.image

    def update(self):
       self.grav()
       self.x += self.dx
       self.y += self.dy
       
       

#using template from
#http://programarcadegames.com/python_examples/f.php?file=platform_moving.py

    def grav(self):
        """ Calculate effect of gravity. """
        if self.dy == 0:
            self.dy = 1
        else:
            self.dy += .35
            if (self.y >= SCREENH - self.height
                and self.dy >= 0):
                self.dy = 0
                self.y = SCREENH - self.height

class Game(object):

    def __init__(self):
        self.mode = 'splash'
        (self.r, self.g, self.b)= (64,224,208)
        self.walllist = {x: Wall((self.r, self.g, self.b),
                                 SCREENH) for x in range(SCREENW)}
        self.sandlist = []
        self.sandCount = 0
        self.level = 1
        self.maxSandCount = self.level * 1000
        self.gameWon = False

    def process(self):
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT: return True
            
            if self.mode == 'sand':
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if self.sandCount <= self.maxSandCount: 
                        self.sandCount += 1
                        (x,y) = pygame.mouse.get_pos()
                        (self.r, self.g, self.b) = ((self.r+19)%255, (self.g)%255,
                                                    (self.b)%255)
                        makeSandList(self.sandlist, (self.r, self.g, self.b),
                                     x, y, self.walllist)
                    
                    elif self.gameWon == True: #up to the next level, init
                       (self.r, self.g, self.b)= (64,224,208)
                       self.walllist = {x: Wall((self.r, self.g, self.b),
                                                SCREENH) for x in range(SCREENW)}
                       self.sandlist = []
                       self.sandCount = 0
                       self.level += 1
                       self.maxSandCount = self.level * 50
                       self.gameWon = False

                    elif self.sandCount > self.maxSandCount:
                        self.mode = 'drive'

            if self.mode == 'drive':
                pass
            #design car, to drive up the hills
                    
            if self.mode == 'splash' and event.type == pygame.MOUSEBUTTONDOWN:
                self.mode = 'sand'
        return False

    def logic(self):
        if self.mode == 'sand':
            for elem in self.sandlist:
                elem.update()
                if elem.dy == 0:
                    self.sandlist.remove(elem)
                    (x,y) = (elem.x, elem.y)
                    self.walllist[x] = Wall((self.r, self.g, self.b),
                                            y - SANDDIM)
        else: return None

    def splashScreen(self, screen):
        pygame.font.init()
        #can't get my words to show up...
        img = pygame.transform.scale(
            pygame.image.load('sandsandsand.jpg').convert(),
            (SCREENW, SCREENH))
        screen.blit(img, (0,0))
        pygame.display.flip()
        myfont = pygame.font.SysFont('Philosopher-Bold.ttf', 60)
        textsurface = myfont.render('Build yo own sand', 1, WHITE)
        screen.blit(textsurface, (0,0))
        textsurface = myfont.render('click anywhere on screen to start',
                                    1, WHITE)
        screen.blit(textsurface, (SCREENW/2, SCREENH/2))

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
        if self.mode == 'sand':
            screen.fill((255-self.r, 255-self.g, 255-self.b))
            for sand in self.sandlist:
                (x, y) = (sand.x, sand.y)
                r = pygame.Rect(x,y,SANDDIM, SANDDIM)
                pygame.draw.rect(screen, (self.r, self.g, self.b), r)
            self.drawWall(screen)
#            for x in range(SCREENW):
#                r = pygame.Rect(x, self.walllist[x].getWallY(), SANDDIM,
#                                SCREENH - self.walllist[x].getWallY())
#                pygame.draw.rect(screen, (self.r, self.g, self.b), r)
        elif self.mode == 'splash':
            self.splashScreen(screen)
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
        pygame.display.set_caption('Level = %d, leftover sand pile =  %d'
                                   %(game.level, game.maxSandCount -
                                     game.sandCount))
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()
