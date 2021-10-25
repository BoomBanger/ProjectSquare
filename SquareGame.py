from tkinter import *
from math import *

root = Tk()
root.title('SquareGame')
roomSize = 700
currentLevel = 0

room = Canvas(root, height=roomSize, width=roomSize)

class Box:

    def __init__(self):
        self.x = 150   # x position
        self.y = 15   # y position
        self.dy = 0   # change in y position
        self.dx = 0   # change in x position
        self.g = -0.1   # gravity
        self.jump = 3   # height of jump
        self.step = 2   # speed of the box
        self.width = 10   # width of box
        self.height = 10   # height of box
        self.onGround = False
        self.box = room.create_rectangle(self.x - self.width / 2, self.y - self.height / 2, self.x + self.width / 2,
                                         self.y + self.height / 2, fill='blue')
        room.after(10, self.loop)

    # creates a constant update loop for the box allowing the box to move 
    def loop(self):
        # horizontal movement is determined
        xStep = (keyboard.is_pressed('right') - keyboard.is_pressed('left')) * self.step
        self.dy -= self.g
        # jumping is applied here
        if (keyboard.is_pressed('up') or keyboard.is_pressed('space')) and self.onGround:
            self.dy = -self.jump
        self.onGround = False
        self.x += xStep
        self.y += self.dy
        self.dx = xStep
        room.move(self.box, xStep, self.dy)
        self.bounding()
        room.after(10, self.loop)

    # This loops through all necessary bounding functions
    def bounding(self):
        self.boundingFloor()
        self.boundingSides()
        self.boundingPlatforms()

    # bounds the bottom of the screen
    def boundingFloor(self):
        if self.y + (self.height / 2) > roomSize: 
            # finds distance between bottom of box and floor if the box is past the floor
            yStep = (self.y + (self.height / 2)) - roomSize  
            self.y -= yStep
            self.dy = 0
            room.move(self.box, 0, -yStep)
            self.onGround = True

    # bounds the sides of the room
    def boundingSides(self):
        if self.x + (self.width / 2) > roomSize:
            xStep = (self.x + (self.width / 2)) - roomSize
            self.x -= xStep
            room.move(self.box, -xStep, 0)
        if self.x - (self.width / 2) < 0:
            xStep = (self.x - (self.width / 2))
            self.x -= xStep
            room.move(self.box, -xStep, 0)

    # This handles loops through bounding for all relevant platforms
    def boundingPlatforms(self):
        resetDy = False
        # only checks bounding for relevant platforms 
        for platform in level.platformLayout:
            if isinstance(platform, MovingPlatform):
                platform.slide()
            move = platform.bounding(self.x, self.y, self.width, self.height, self.dx, self.dy)
            self.x += move[0]
            self.y += move[1]
            self.dx += move[0]
            self.dy += move[1]
            room.move(self.box, move[0], move[1])
            # checks to see if box bounded on the top or bottom, resets dy
            if move[2]:
                resetDy = True
            # checks to see if box is on top of something, sets its status to be on the ground
            if move[3]:
                self.onGround = True
        if resetDy: self.dy = 0


class Platform:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y2
        self.x2 = x2
        self.y2 = y2
        self.top = min(y1, y2)  # determines which y is the top of the box
        self.bottom = max(y1, y2)  # determines which y is the bottom of the box
        self.left = min(x1, x2)  # determines which x is the left of the box
        self.right = max(x1, x2)  # determines which x is the right of the box
        self.height = abs(y1 - y2)
        self.width = abs(x1 - x2)
        self.platform = room.create_rectangle(x1, y1, x2, y2, fill='black')
        self.type = "Normal"

    def bounding(self, x, y, w, h, dx, dy, pdx=0, pdy=0):
        # pdy and pdx are dealing with the platform's movement in each respective direction
        xStep = 0
        yStep = 0
        resetDy = False
        ground = False
        # this bounds for the top and bottom of platforms
        if x + (w / 2) > self.left and x - (w / 2) < self.right:
            # this bounds the top of the platform and bottom of box
            if y + (h / 2) > self.top and y + (h / 2) - dy <= self.top - pdy:
                yStep = self.top - (y + (h / 2))
                resetDy = True
                ground = True
            # this bounds the bottom of the platform and the top of the box
            elif y - (h / 2) < self.bottom and y - (h / 2) - dy >= self.bottom - pdy:
                yStep = self.bottom - (y - (h / 2))
                resetDy = True
        # this bounds the left and right of platforms
        if y - (h / 2) < self.bottom and y + (h / 2) > self.top:
            # this bounds the right of the platform and left of the box
            if x - (w / 2) < self.right and x - (w / 2) - dx >= self.right - pdx:
                xStep = self.right - (x - (w / 2))
            # this bounds the left of the platform and right of the box
            elif x + (w / 2) > self.left and x + (w / 2) - dx <= self.left - pdx:
                xStep = self.left - (x + (w / 2))
        # this returns to boundingPlatforms in the box class
        return xStep, yStep, resetDy, ground

    def move(self, x, y):
        self.x1 += x
        self.y1 += y
        self.x2 += x
        self.x2 += y
        self.left += x
        self.right += x
        self.top += y
        self.bottom += y
        room.move(self.platform, x, y)

    def changeColor(self, color):
        if color == "Hide":
            room.itemconfigure(self.platform, state='hidden')
        elif color == "Show":
            room.itemconfigure(self.platform, state='normal')
        else:
            room.itemconfigure(self.platform, fill=color, state='normal')


class MovingPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, xDelta, yDelta, speed):
        super().__init__(x1, y1, x2, y2)
        distance = sqrt(xDelta ** 2 + yDelta ** 2)
        scale = speed / distance
        self.xSpeed = xDelta * scale
        self.ySpeed = yDelta * scale
        self.xDelta = xDelta
        self.yDelta = yDelta
        self.pdx = 0
        self.pdy = 0
        self.x = 0
        self.y = 0
        self.xPrev = 0
        self.yPrev = 0
        self.forward = True
        self.type = "Moving"

    def bounding(self, x, y, w, h, dx, dy, pdx=0, pdy=0):
        pdx = self.x - self.xPrev
        pdy = self.y - self.yPrev
        output = super().bounding(x, y, w, h, dx, dy, pdx, pdy)
        xStep = output[0]
        yStep = output[1]
        resetDy = output[2]
        ground = output[3]
        if ground:
            xStep += pdx
        return xStep, yStep, resetDy, ground

    def slide(self):
        self.xPrev = self.x
        self.yPrev = self.y
        self.pdx = self.xSpeed * (1 if self.forward else -1)
        self.pdy = self.ySpeed * (1 if self.forward else -1)
        super().move(self.pdx, self.pdy)
        self.x += self.pdx
        self.y += self.pdy
        if (self.x >= self.xDelta and self.y >= self.yDelta) or (self.x <= 0 and self.y <= 0):
            self.forward = not self.forward


class DisappearingPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, tOn, tOff, tShift):
        super().__init__(x1, y1, x2, y2)
        self.tOn = tOn * 100
        self.tOff = tOff * 100
        self.time = tShift * 100
        super().changeColor('green')
        self.type = "Disappearing"

    def bounding(self, x, y, w, h, dx, dy, pdx=0, pdy=0):
        self.time += 1
        if self.time < self.tOn:
            color = "#"
            value = hex(round(255 * self.time / self.tOn))
            value = value[2:]
            value = ((2 - len(value)) * "0") + value
            color += value + "FF" + value
            super().changeColor(color)
        else:
            super().changeColor("Hide")
            self.time %= self.tOff + self.tOn

        if self.time < self.tOn:
            return super().bounding(x, y, w, h, dx, dy)
        return 0, 0, False, False


class DangerPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, startX, startY):
        super().__init__(x1, y1, x2, y2)
        self.startX = startX
        self.startY = startY
        super().changeColor('red')
        self.type = "Danger"

    def bounding(self, x, y, w, h, dx, dy, pdx=0, pdy=0):
        output = super().bounding(x, y, w, h, dx, dy)
        xStep = output[0]
        yStep = output[1]
        resetDy = output[2]
        ground = output[3]
        if xStep or yStep or resetDy or ground:
            xStep = self.startX - x
            yStep = self.startY - y
            resetDy = True
            ground = False
        else:
            return 0, 0, False, False
        return xStep, yStep, resetDy, ground


class Keyboard:
    def __init__(self):
        self.down = []
        room.bind('<KeyPress>', self.pressed)
        room.bind('<KeyRelease>', self.released)

    def is_pressed(self, key):
        return key.lower() in self.down

    def pressed(self, e):
        key = e.keysym.lower()
        if key not in self.down:
            self.down.append(key)

    def released(self, e):
        key = e.keysym.lower()
        if key in self.down:
            self.down.remove(key)


levelOne = [Platform(130, 670, 170, 680), Platform(40, 640, 100, 660), Platform(200, 650, 250, 700),
            Platform(250, 570, 280, 700), Platform(320, 520, 340, 630), Platform(30, 0, 40, 660),
            DisappearingPlatform(320, 630, 340, 700, 1, 1, 0),
            DisappearingPlatform(370, 660, 390, 680, 1, 1, 0),
            Platform(410, 630, 430, 700), DisappearingPlatform(470, 660, 490, 670, 3, 1, 0),
            DisappearingPlatform(520, 640, 540, 650, 3, 1, 0),
            DisappearingPlatform(555, 670, 585, 680, 3, 1, 2),
            Platform(565, 570, 575, 650), MovingPlatform(60, 600, 90, 610, 90, 0, 1),
            DangerPlatform(200, 640, 250, 650, 15, 15),
            DangerPlatform(430, 690, 700, 700, 15, 15),
            DisappearingPlatform(610, 640, 630, 650, 3, 1, 0),
            DisappearingPlatform(670, 610, 690, 620, 3, 1, 0),
            DisappearingPlatform(610, 580, 630, 590, 3, 1, 1),
            MovingPlatform(535, 460, 555, 470, 0, 75, 0.4), Platform(445, 500, 448, 510),
            Platform(238, 510, 241, 520),
            MovingPlatform(100, 450, 120, 460, 0, 100, 3), Platform(140, 440, 170, 450),
            MovingPlatform(170, 410, 250, 420, 300, 0, 1), DangerPlatform(210, 390, 220, 410, 155, 435),
            DangerPlatform(250, 360, 260, 390, 155, 435), DangerPlatform(300, 400, 350, 410, 155, 435),
            DangerPlatform(400, 400, 550, 410, 155, 435), DisappearingPlatform(450, 380, 480, 390, 3, 1, 2)]
platformList = [levelOne]


class Level:
    def __init__(self):
        # hiding all the other platforms in the other levels
        for level in platformList:
            for platform in level:
                platform.changeColor("Hide")
        
        self.platformLayout = platformList[currentLevel]

        for platform in self.platformLayout:
            platform.changeColor("Show")

    def changeLevel(self):
        global currentLevel

        for platform in self.platformLayout:
            platform.changeColor("Hide")

        currentLevel += 1
        self.platformLayout = platformList[currentLevel]

        for platform in self.platformLayout:
            platform.changeColor("Show")

            
# title screen functions and buttons
def startGame():
    startButton.destroy()
    gameTitle.destroy()
    keyboard = Keyboard()
    b = Box()
    level = Level()
   
startButton = Button(root, text="Start", padx=100, pady=10, command=startGame)
# add colors!!!
gameTitle = Label(root, text="SquareGame (working title)", font=("Helvetica", 20))

gameTitle.grid(row=0)
startButton.grid(row=1)

room.pack()
room.focus_set()
root.mainloop()
