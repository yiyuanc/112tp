import pygame
import random

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
YELLOW = (150, 113, 23)
SAND_DIM = 5

screenWidth = 1000
screenHeight = 500

def changeBottomBound(sandlist, x, y):
    for elem in sandlist:
        if elem.rect.x == x: #abs(elem.rect.x - x) <= SAND_DIM:
            elem.bottomBound = y - SAND_DIM

class Sand(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.image = pygame.Surface([SAND_DIM, SAND_DIM])
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.leftBound = 0
        self.rightBound = 0
        self.topBound = 0
        self.bottomBound = 0

        self.dx = 0
        self.dy = 0
        self.walls = None

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        hit = pygame.sprite.spritecollide(self, self.walls, False)
        if (self.rect.right >= self.rightBound or
            self.rect.left<= self.leftBound):
            self.dx *= -1
        if self.rect.bottom >= self.bottomBound:
            self.dy = 0

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface([SAND_DIM, SAND_DIM])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x

        
def makeMess(sandList, x, y, w):
        for i in range(50):
            sand = Sand(YELLOW)
            sand.rect.x = random.randrange(x-30, x+30)
            sand.rect.y = random.randrange(y-10, y+10)
            sand.dx = 0
            sand.dy = 5
            sand.leftBound = 0
            sand.topBound = 0
            sand.rightBound = screenWidth
            sand.bottomBound = screenHeight
            sand.walls = w
    
            sandList.add(sand)

class Game(object):
    def __init__(self):
        self.gameOver = False
        self.wallList = pygame.sprite.Group()
        self.sandList = pygame.sprite.Group()
        self.player = Sand(YELLOW)

        
    def process(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                (x,y) = pygame.mouse.get_pos()
                makeMess(self.sandList, x, y, self.wallList)
        return False
        
    def logic(self):
        if not self.gameOver:
            self.sandList.update()
            for elem in self.sandList:
                #hit = pygame.sprite.spritecollide(elem, self.wallList, False)
                if elem.dy == 0:
                    self.sandList.remove(elem)
                    (x,y) = (elem.rect.x, elem.rect.y)
                    self.wallList.add(Wall(x,y,BLACK))
                    changeBottomBound(self.sandList, x, y)
        else: return None

    def display(self, screen):
        screen.fill(WHITE)
        if self.gameOver:
            font = pygame.font.SysFont("serif", 25)
            text = font.render("Game Over, click to restart", True, BLACK)
            center_x = (screenWidth // 2) - (text.get_width() // 2)
            center_y = (screenHeight // 2) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])
        if not self.gameOver:
            self.sandList.draw(screen)
            self.wallList.draw(screen)
        pygame.display.flip()

    def debug(self):
        for w in self.wallList:
            print(w.rect.y)
        
def main():
    pygame.init()
    size = [screenWidth, screenHeight]
    screen = pygame.display.set_mode(size)
    
    pygame.display.set_caption('THIS IS SAND')
    pygame.mouse.set_visible(True)
    done = False
    clock = pygame.time.Clock()

    game= Game()

    while not done:
        done = game.process()
        game.logic()
        game.display(screen)
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()
