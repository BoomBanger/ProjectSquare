from tkinter import *
from math import *

root = Tk()
root.title('LevelEditor')
room = Canvas(root, bg='white', height=700, width=500)

selectedID = StringVar()
global idCount
idCount = 0
global platList
platList = []
global runOn
runOn = 1


class Platform:

    def __init__(self, x1, y1, x2, y2, id):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.id = id
        self.platform = room.create_rectangle(x1, y1, x2, y2, fill='black')
        self.type = "Normal"

    def move(self, x, y):
        self.x1 += x
        self.y1 += y
        self.x2 += x
        self.x2 += y
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
        super().__init__(x1, y1, x2, y2, id)
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
        super().__init__(x1, y1, x2, y2, id)
        self.tOn = tOn * 100
        self.tOff = tOff * 100
        self.time = tShift * 100
        super().changeColor('green')
        self.type = "Disappearing"

    def timeChange(self, x, y, w, h, dx, dy, pdx=0, pdy=0):
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


class DangerPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, startX, startY):
        super().__init__(x1, y1, x2, y2, id)
        self.startX = startX
        self.startY = startY
        super().changeColor('red')
        self.type = "Danger"


def updatePlat():
    platID = idLabel.cget("text")


def createPlat():
    pType = platTypeEntry.get(0, END).replace(" ", "")
    pType.lower()
    if pType == "n":
        x1 = topLeftCornerEn.get(0, END).replace(" ", "")
        index = x1.find(',')
        y1 = x1[index + 1:]
        x1 = x1[0, index]
        width = widthEntry.get(0, END).replace(" ", "")

    elif pType == "m":
        print('d')
    elif pType == "di":
        print('d')
    elif pType == "da":
        print('d')
    else:
        print('d')


def deletePlat():
    print("delete functionality")


def runLevel(clicked):
    global runOn
    runOn *= clicked
    if runOn == -1:
        buttonUpdate.config(state="disabled")
        buttonCreate.config(state="disabled")
        buttonDelete.config(state="disabled")
        room.after(10, platFunctions())
    else:
        buttonUpdate.config(state="normal")
        buttonCreate.config(state="normal")
        buttonDelete.config(state="normal")


def platFunctions():
    for plat in platList:
        if plat.type == "Moving":
            plat.slide()
        elif plat.type == "Disappearing":
            plat.timeChange()
    room.after(10, platFunctions())


def printLevelData():
    with open("platformLayout.txt", "w") as f:
        f.write("put code here to do stuff")
        f.close()


topLeftCorner = Label(root, text="Enter top left corner (x1, y1): ")
topLeftCornerEn = Entry(root)

widthLabel = Label(root, text="Enter width: ")
widthEntry = Entry(root)

heightLabel = Label(root, text="Enter height: ")
heightEntry = Entry(root)

xyCenterLabel = Label(root, text="Center x,y (default of 250, 250): ")
xyCenterEntry = Entry(root)

platTypeLabel = Label(root, text="Enter plat type (n, m, di, da): ")
platTypeEntry = Entry(root)

platDeltaXYLabel = Label(root, text="(M plat) Enter change in x, y: ")
platDeltaXYEntry = Entry(root)

platSpeedLabel = Label(root, text="(M plat) Enter plat speed: ")
platSpeedEntry = Entry(root)

platTimeLabel = Label(root, text="(Di plat) Enter plat time on, off, shift: ")
platTimeEntry = Entry(root)

platRespawnLabel = Label(root, text="(Da plat) Enter respawn location (x,y): ")
platRespawnEntry = Entry(root)

currentLabel = Label(root, text="Selected Box ID: ")
idLabel = Label(root, textvariable=selectedID)

buttonUpdate = Button(root, text="Update plat", command=updatePlat)
buttonCreate = Button(root, text="Create plat", command=createPlat)

buttonDelete = Button(root, text="Delete plat", command=deletePlat)
buttonRun = Button(root, text="Run level", command=lambda: runLevel(-1))

printPlatsButton = Button(root, text="Compile and print level data", command=printLevelData)

room.grid(column=0, row=0, rowspan=15)

topLeftCorner.grid(column=1, row=0)
topLeftCornerEn.grid(column=2, row=0)

widthLabel.grid(column=1, row=1)
widthEntry.grid(column=2, row=1)

heightLabel.grid(column=1, row=2)
heightEntry.grid(column=2, row=2)

xyCenterLabel.grid(column=1, row=3)
xyCenterEntry.grid(column=2, row=3)

platTypeLabel.grid(column=1, row=4)
platTypeEntry.grid(column=2, row=4)

platDeltaXYLabel.grid(column=1, row=5)
platDeltaXYEntry.grid(column=2, row=5)

platSpeedLabel.grid(column=1, row=6)
platSpeedEntry.grid(column=2, row=6)

platTimeLabel.grid(column=1, row=7)
platTimeEntry.grid(column=2, row=7)

platRespawnLabel.grid(column=1, row=8)
platRespawnEntry.grid(column=2, row=8)

currentLabel.grid(column=1, row=9)
idLabel.grid(column=2, row=9)

buttonUpdate.grid(column=1, row=10)
buttonCreate.grid(column=2, row=10)

buttonDelete.grid(column=1, row=11)
buttonRun.grid(column=2, row=11)

printPlatsButton.grid(column=1, columnspan=2, row=12)

room.focus_set()
root.mainloop()
