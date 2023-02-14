import pygame
import sys
import os
import random
import math

pygame.init()

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

basset_url = resource_path('B.png')
b = pygame.image.load(basset_url)
#b.set_colorkey((255,255,255))

pygame.display.set_caption("Betris")
pygame.display.set_icon(b)


imageNames = ["SquareP.png","SquareR.png","SquareO.png","SquareG.png","SquareB.png"]

gameObj = []

gameOver = False

score = 0

font = pygame.font.Font('freesansbold.ttf', 32)
overfont = pygame.font.Font('freesansbold.ttf',64)

size = width, height = 525, 900
black = 0, 0, 0

moveAllowed = True

screen = pygame.display.set_mode(size)
s = pygame.Surface([700,1200])

class waiting:
    def __init__(self):
        self.startTime = 1
        self.endTime = 0

    def wait(self, time):
        if pygame.time.get_ticks() >= self.endTime:
            self.startTime = pygame.time.get_ticks()
            self.endTime = pygame.time.get_ticks() + time
            return True
        else:
            return False

    def resetTimer(self, time):
        self.startTime = pygame.time.get_ticks()
        self.endTime = pygame.time.get_ticks() + time

def generatePoly(maxSize):
    shape = []
    for i in range(maxSize):
        row = []
        for s in range(maxSize):
            row.append(0)
        shape.append(row)

    def minimize(p):
        clear = [True,True,True,True]
        for x in p:
            i=0
            for y in x:
                if y == 1:
                    clear[i] = False
                i = i + 1

        modified = p.copy()
        r = 0
        for x in p:
            c = 0
            o = 0
            for y in x:
                if clear[c]:
                    del modified[r][(c-o)]
                    o=o+1
                c=c+1
            r = r + 1

        if clear[-1]:
            for x in modified:
                del x[-1]

        final = modified.copy()
        r=0
        n=0
        for x in modified:
            d = True
            for y in x:
                if y == 1:
                    d = False
            if d:
                del final[r-n]
                n=n+1
            r=r+1

        return final

    def decide(size):
        modifier = size
        chance = random.random()
        if chance > 0.5 * modifier:
            return True
        else:
            return False

    def recursiveActivate(x, y, tempSize):
        shape[x][y] = 1
        tempIncrease = 0
        if 0 <= x + 1 < maxSize and shape[x + 1][y] == 0:
            if decide(tempSize):
                recursiveActivate(x + 1, y, tempSize)
                tempIncrease = tempIncrease + 1
        if 0 <= x - 1 < maxSize and shape[x - 1][y] == 0:
            if decide(tempSize):
                recursiveActivate(x - 1, y, tempSize)
                tempIncrease = tempIncrease + 1
        if 0 <= y - 1 < maxSize and shape[y - 1][y] == 0:
            if decide(tempSize):
                recursiveActivate(x, y - 1, tempSize)
                tempIncrease = tempIncrease + 1
        if 0 <= y + 1 < maxSize and shape[y + 1][y] == 0:
            if decide(tempSize):
                recursiveActivate(x, y + 1, tempSize)
                tempIncrease = tempIncrease + 1
        tempSize = tempSize + tempIncrease

    recursiveActivate(int(math.floor(maxSize / 2)), int(math.floor(maxSize / 2)), 1)

    return minimize(shape)

class Poly:
    def __init__(self, polyMap):
        pygame.sprite.Sprite.__init__(self)
        self.polyMap = polyMap
        asset_url = resource_path(imageNames[random.randrange(0,len(imageNames))])
        self.image = pygame.image.load(asset_url)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rects = []
        self.x, self.y = 0, 0
        self.angle = 0
        self.recalcRects()
        self.moving = True
        gameObj.append(self)

    def recalcRects(self):
        x = 0
        y = 0
        self.rects = []
        for tab in self.polyMap:
            for t in tab:
                if self.polyMap[x][y] == 1:
                    self.rects.append(
                        [self.image.get_rect().move((50 * x), (50 * y)), x, y])
                y = y + 1
            y = 0
            x = x + 1

        recalc = False
        for r in self.rects:
            r[0].y = self.y + (50 * r[2])
            r[0].x = self.x + (50 * r[1])
            if r[0].x >= 500:
                self.x = self.x-50
                recalc = True

        if recalc:
            self.recalcRects()

    def moveR(self, inX, inY):
        for i in self.rects:
            for x in gameObj:
                if x != self:
                    for r in x.rects:
                        if i[0].collidepoint(r[0].midtop[0], r[0].midtop[1] - 1):
                            self.moving = False
                            return False
        if not moveAllowed:
            return False
        fuse = []
        for i in self.rects:
            fuse.append(i[0])
        master = fuse[0].unionall(fuse[1::])
        if master.bottom < 1200:
            self.y = self.y + inY
            for r in self.rects:
                r[0].y = self.y + (50 * r[2])
        if master.left == 0:
            if inX > 0:
                pass
            else:
                return False
        if master.right == 500:
            if inX < 0:
                pass
            else:
                return False

        able = True
        for o in gameObj:
            if o != self:
                for j in o.rects:
                    for r in self.rects:
                        if j[0].collidepoint(r[0].center[0]+inX,r[0].center[1]):
                            able = False
        if able:
            pass
        else:
            return False

        self.x = self.x + inX
        for r in self.rects:
            r[0].x = self.x + (50 * r[1])

    def check(self):
        if self.moving == False:
            total = []
            clear = []
            for x in range(25):
                total.append(0)
            for o in gameObj:
                for u in o.rects:
                    total[math.floor(u[0].bottom / 50)] = total[math.floor(u[0].bottom / 50)] + 1
            for i in range(len(total)):
                if total[i] == 10:
                    clear.append(i)

            for i in clear:
                for o in gameObj:
                    index = 0
                    for r in o.rects:
                        if math.floor(r[0].bottom/50) == i:
                            o.rects[index] = "Erase"
                        index = index+1
                    while "Erase" in o.rects:
                        o.rects.remove("Erase")
                        global score
                        score = score+100
                    for r in o.rects:
                        if math.floor(r[0].bottom / 50) < i:
                            r[0].y = r[0].y+50
        else:
            fuse = []
            for i in self.rects:
                for x in gameObj:
                    if x != self:
                        for r in x.rects:
                            if i[0].collidepoint(r[0].midtop[0], r[0].midtop[1] - 1):
                                self.moving = False
                                return True
                            if i[0].collidepoint(r[0].midtop[0], r[0].midtop[1]):
                                self.y = self.y-1
                                self.moving = False
                                return True
                fuse.append(i[0])
            master = fuse[0].unionall(fuse[1::])

            if master.bottom >= 1200:
                self.moving = False
                return True

    def lock(self):
        pass

    def rotate(self, dir):
        if dir == 1:
            rotated = []
            for i in range(len(self.polyMap[0])):
                rotated.append([])
            for r in self.polyMap:
                x = 0
                for c in r:
                    rotated[x].append(c)
                    x=x+1
            rotated = rotated[::-1]

            self.polyMap = rotated
            self.recalcRects()

    def draw(self):
        for r in self.rects:
            s.blit(self.image, r[0])
            moveAllowed = True

drop = waiting()
move = waiting()
lock = waiting()

dropSpeed = 1000

currentPoly = Poly(generatePoly(4))
currentVelocity = [0, 50]

while True:
    s.fill(black)
    for x in range(11):
        pygame.draw.line(s,pygame.Color(255,255,255,255),(x*50,0),(x*50,1200))
    for y in range(24):
        pygame.draw.line(s,pygame.Color(255,255,255,255),(0,y*50),(500,y*50))

    for obj in gameObj:
        obj.draw()

    if gameOver:
        overText = overfont.render("GAME OVER!", True, pygame.Color(255,255,255))
        subText = font.render("Press space to replay!", True, pygame.Color(255,255,255))
        s.blit(overText,overText.get_rect().move(100,500))
        s.blit(subText, subText.get_rect().move(150, 600))

    text = font.render('Score: ' + str(score), True, pygame.Color(255,255,255))
    textRect = text.get_rect()
    textRect.center = (600,500)

    s.blit(text, textRect)

    frame = pygame.transform.scale(s,(525,900))
    screen.blit(frame,frame.get_rect())
    pygame.display.flip()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if gameOver:
                if event.key == pygame.K_SPACE:
                    gameObj.clear()
                    score = 0
                    gameOver = False
                    currentPoly = Poly(generatePoly(4))
            else:
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    currentVelocity[0] = 50
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    currentVelocity[0] = -50
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    dropSpeed = 100
                    drop.resetTimer(100)
                if event.key == pygame.K_UP:
                    currentPoly.rotate(1)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d or event.key == pygame.K_a or event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                currentVelocity[0] = 0
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                dropSpeed = 1000
                drop.resetTimer(1000)

    currentPoly.check()

    moving = move.wait(100)
    if moving:
        currentPoly.moveR(currentVelocity[0], 0)

    dropping = drop.wait(dropSpeed)
    if dropping:
        currentPoly.moveR(0, currentVelocity[1])

    if currentPoly.check():
        currentPoly.check()
        currentPoly = Poly(generatePoly(4))

    if not currentPoly.moving:
        gameOver = True
