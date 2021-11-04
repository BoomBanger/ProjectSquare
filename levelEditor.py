from tkinter import *
from math import *

root = Tk()
root.title('SquareGame')
roomSize = 700
room = Canvas(root, height=roomSize, width=roomSize, bd = 1)

class Platform:
    def __init__(self, type, x, y, w, h):
        self.type = type.lower()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed = 0
        self.dx = 0
        self.dy = 0
        self.tOn = 0
        self.tOff = 0
        self.tOffset = 0
        self.respawnX = 0
        self.respawnY = 0
        self.colors = {'normal': 'black', 'disappearing': '#00FF00', 'moving': 'magenta', 'danger': 'red'}
        self.platform = room.create_rectangle(x, y, x + w, y + h, fill=self.colors[self.type])
        self.mouseX = None
        self.mouseY = None
        self.slideX = 0
        self.slideY = 0
        self.forward = True
        self.time = self.tOffset
        self.play = False
        room.tag_bind(self.platform, "<ButtonPress-1>", self.startDrag)
        room.tag_bind(self.platform, "<ButtonRelease-1>", self.stopDrag)
        room.tag_bind(self.platform, "<B1-Motion>", self.drag)
        self.loop()

    def getVariables(self):
        return (self.x, self.y, self.w, self.h, self.type, self.speed, self.dx, self.dy, self.tOn, self.tOff, self.tOffset, self.respawnX, self.respawnY)
    
    def toCode(self):
        coordinates = ", ".join([str(self.x), str(self.y), str(self.x + self.w), str(self.y + self.h)])
        if self.type == "normal": return "Platform(" + coordinates + ")"
        if self.type == "moving": return "MovingPlatform(" + ", ".join([coordinates, str(self.dx), str(self.dy), str(self.speed)]) + ")"
        if self.type == "disappearing": return "DisappearingPlatform(" + ", ".join([coordinates, str(self.tOn), str(self.tOff), str(self.tOffset)]) + ")"
        if self.type == "danger": return "DangerPlatform(" + ", ".join([coordinates, str(self.respawnX), str(self.respawnY)]) + ")"

    def delete(self):
        global level, activePlatform
        level.remove(self)
        room.delete(self.platform)
        activePlatform = None
        del self
    
    def playPreview(self):
        self.slideX = 0
        self.slideY = 0
        self.forward = True
        self.setPos()
        self.time = self.tOffset * 100
        self.play = True

    def pausePreview(self):
        self.play = False

    def changePos(self, dx, dy):
        self.x += dx
        self.y += dy
        room.move(self.platform, dx, dy)

    def setPos(self, x=None, y=None):
        if x != None: self.x = x
        if y != None: self.y = y
        room.coords(self.platform, self.x + self.slideX, self.y + self.slideY, self.x + self.w + self.slideX, self.y + self.h + self.slideY)

    def setWH(self, w=None, h=None):
        x0, y0, _, _ = room.coords(self.platform)
        if w != None: self.w = w
        if h != None: self.h = h
        x1 = x0 + self.w
        y1 = y0 + self.h
        room.coords(self.platform, x0, y0, x1, y1)

    def setSpeed(self, speed):
        self.speed = speed
    
    def setDXDY(self, dx = None, dy = None):
        if dx != None: self.dx = dx
        if dy != None: self.dy = dy
        self.slideX = 0
        self.slideY = 0
        self.forward = True
        self.setPos()

    def setT(self, tOn=None, tOff=None, tOffset=None):
        if tOn != None: self.tOn = tOn
        if tOff != None: self.tOff = tOff
        if tOffset != None: self.tOffset = tOffset

    def setRespawn(self, x=None, y=None):
        if x != None: self.respawnX = x
        if y != None: self.respawnY = y
        room.coords(respawnBox, self.respawnX - 5, self.respawnY - 5, self.respawnX + 5, self.respawnY + 5)
    
    def setType(self, type):
        self.type = type.lower()
        room.itemconfig(self.platform, fill = self.colors[self.type])
        if type == "danger":
            room.itemconfigure(respawnBox, state='normal')
            room.coords(respawnBox, self.respawnX - 5, self.respawnY - 5, self.respawnX + 5, self.respawnY + 5)
        else: 
            room.itemconfigure(respawnBox, state='hidden')

    def clicked(self):
        clickedPlatform(self)
    
    def startDrag(self, event):
        self.mouseX = event.x
        self.mouseY = event.y
        self.clicked()
    
    def stopDrag(self, event):
        self.mouseX = None
        self.mouseY = None
        self.clicked()

    def drag(self, event):
        if self.mouseX != None and self.mouseY != None:
            dx = event.x - self.mouseX
            dy = event.y - self.mouseY
            self.changePos(dx, dy)
            self.mouseX = event.x
            self.mouseY = event.y
            self.clicked()

    def loop(self):
        global activePlatform, speedEntry, dxEntry, dyEntry, tOnEntry, tOffEntry, tOffsetEntry
        activeEntry = root.focus_get()
        slidingWidgetActive = activeEntry is speedEntry.getEntry() or activeEntry is dxEntry.getEntry() or activeEntry is dyEntry.getEntry()
        if self.type == "moving" and ((self is activePlatform and slidingWidgetActive) or self.play):
            distance = sqrt(self.dx ** 2 + self.dy ** 2)
            if distance > 0:
                scale = self.speed / distance
                xSpeed = self.dx * scale
                ySpeed = self.dy * scale
                pdx = xSpeed * (1 if self.forward else -1)
                pdy = ySpeed * (1 if self.forward else -1)
                self.slideX += pdx
                self.slideY += pdy
                self.setPos()
                if (self.slideX >= self.dx and self.slideY >= self.dy) or (self.slideX <= 0 and self.slideY <= 0):
                    self.forward = not self.forward
        else:
            self.slideX, self.slideY = 0, 0
            self.forward = True
            self.setPos()
        
        
        timingWidgetActive = activeEntry is tOnEntry.getEntry() or activeEntry is tOffEntry.getEntry() or activeEntry is tOffsetEntry.getEntry()
        if self.type == "disappearing" and ((self is activePlatform and timingWidgetActive) or self.play):
            self.time += 1
            self.time %= (100 * (self.tOff + self.tOn)) if self.tOff + self.tOn > 0 else 1
            if self.time < self.tOn * 100:
                color = "#"
                value = hex(round(255 * self.time / (self.tOn * 100)))
                value = value[2:]
                value = ((2 - len(value)) * "0") + value
                color += value + "FF" + value
                room.itemconfigure(self.platform, fill=color, state='normal')
            else:
                room.itemconfigure(self.platform, state='hidden')
        else:
            room.itemconfigure(self.platform, fill=self.colors[self.type], state='normal')
		
        if self is activePlatform: room.itemconfigure(self.platform, outline='blue', width=2)
        else: room.itemconfigure(self.platform, outline='black', width = 1)
        room.after(10, self.loop)

level = []
def setup():
    code = ""
    with open("level.txt", "r") as f:
        code = f.read().replace('\n', '').replace(' ', '').replace('[', '').replace(']', '')

    code = code.replace("DisappearingPlatform(", "d").replace("DangerPlatform(", "k").replace("MovingPlatform(", "m").replace("Platform(", "p")

    platforms = code.split("),")

    for platform in platforms:
        platform = platform.replace(")", "")
        type = {"d": "disappearing", "k": "danger", "m": "moving", "p": "normal"} [platform[0]]
        numbers = platform[1:].split(",")
        x1, y1, x2, y2 = numbers[0:4]
        dx, dy, speed = 0, 0, 0
        if type == "moving":
            dx, dy, speed = numbers[4:7]
        tOn, tOff, tOffset = 0, 0, 0
        if type == "disappearing":
            tOn, tOff, tOffset = numbers[4:7]
        respawnX, respawnY = 0, 0
        if type == "danger":
            respawnX, respawnY = numbers[4:6]
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        dx = int(dx)
        dy = int(dy)
        speed = float(speed)
        tOn = int(tOn)
        tOff = int(tOff)
        tOffset = int(tOffset)
        respawnX = int(respawnX)
        respawnY = int(respawnY)
        
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x1 - x2)
        h = abs(y1 - y2)

        p = Platform(type, x, y, w, h)
        p.setDXDY(dx=dx, dy=dy)
        p.setSpeed(speed)
        p.setT(tOn=tOn, tOff=tOff, tOffset=tOffset)
        p.setRespawn(x=respawnX, y=respawnY)
        level.append(p)


activePlatform = None

mouseX = None
mouseY = None
def startDragRespawn(event):
    global mouseX, mouseY
    mouseX = event.x
    mouseY = event.y

def stopDragRespawn(event):
    global mouseX, mouseY
    mouseX = None
    mouseY = None

def dragRespawn(event):
    global mouseX, mouseY
    dx = event.x - mouseX
    dy = event.y - mouseY
    room.move(respawnBox, dx, dy)
    _, _, _, _, _, _, _, _, _, _, _, x, y = activePlatform.getVariables()
    x += dx
    y += dy
    activePlatform.setRespawn(x=x, y=y)
    mouseX = event.x
    mouseY = event.y
    clickedPlatform(activePlatform)

respawnBox = room.create_rectangle(10, 10, 20, 20, fill="blue")
room.itemconfigure(respawnBox, state='hidden')
room.tag_bind(respawnBox, "<ButtonPress-1>", startDragRespawn)
room.tag_bind(respawnBox, "<ButtonRelease-1>", stopDragRespawn)
room.tag_bind(respawnBox, "<B1-Motion>", dragRespawn)

def clickedPlatform(platform):
    global activePlatform, xEntry, yEntry, wEntry, hEntry, svType, speedEntry, dxEntry, dyEntry, tOnEntry, tOffEntry, tOffsetEntry, respawnXEntry, respawnYEntry
    activePlatform = platform
    x, y, w, h, t, speed, dx, dy, tOn, tOff, tOffset, respawnX, respawnY = activePlatform.getVariables()
    xEntry.set(x)
    yEntry.set(y)
    wEntry.set(w)
    hEntry.set(h)
    svType.set(t)
    speedEntry.set(speed)
    dxEntry.set(dx)
    dyEntry.set(dy)
    tOnEntry.set(tOn)
    tOffEntry.set(tOff)
    tOffsetEntry.set(tOffset)
    respawnXEntry.set(respawnX)
    respawnYEntry.set(respawnY)

def createPlatform():
    global activePlatform
    clickedPlatform(Platform("normal", 0, 0, 10, 10))
    level.append(activePlatform)

class EntryWithChangeHandler:
    def __init__(self, root, row = 0, column = 0, rowspan = 1, columnspan = 1, onchange = lambda x: None, intsOnly = True, floatsOnly = False):
        self.sv = StringVar()
        self.sv.trace_add("write", lambda name, index, mode: onchange(self.sv.get()))
        self.intsOnly = intsOnly
        self.floatsOnly = floatsOnly
        vcmd = (root.register(self.validate))
        self.entry = Entry(root, textvariable=self.sv, validate='all', validatecommand=(vcmd, '%P'))
        self.entry.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)
    
    def get(self):
        return self.sv.get()
    
    def set(self, val):
        self.sv.set(str(val))

    def validate(self, text):
        if self.intsOnly: return str.isdecimal(text) or text == ""
        if self.floatsOnly:
            if text == "": return True
            try:
                x = float(text)
                return x >= 0
            except:
                return False
        return True

    def getEntry(self):
        return self.entry

##New Platform
Button(root, text="New Platform", padx=50, pady=10, font=("Helvetic", 12), command=createPlatform).grid(row = 0, column = 1, columnspan=4)
##Type Select
def setType(text):
    if activePlatform: activePlatform.setType(text)
svType = StringVar()
svType.set("normal")
svType.trace_add("write", lambda name, index, mode: setType(svType.get()))
OptionMenu(root, svType, "normal", "moving", "disappearing", "danger").grid(row=1, column=1, columnspan=4)
##X
Label(root, text="X").grid(row = 2, column = 1)
def setX(text):
    if activePlatform: activePlatform.setPos(x = int(text) if text else 0)
xEntry = EntryWithChangeHandler(root, row = 2, column=2, onchange=setX)
##Y
Label(root, text="Y").grid(row = 2, column = 3)
def setY(text):
    if activePlatform: activePlatform.setPos(y = int(text) if text else 0)
yEntry = EntryWithChangeHandler(root, row = 2, column = 4, onchange=setY)
##W
Label(root, text="W").grid(row = 3, column = 1)
def setW(text):
    if activePlatform: activePlatform.setWH(w = int(text) if text else 0)
wEntry = EntryWithChangeHandler(root, row = 3, column=2, onchange=setW)
##H
Label(root, text="H").grid(row = 3, column = 3)
def setH(text):
    if activePlatform: activePlatform.setWH(h = int(text) if text else 0)
hEntry = EntryWithChangeHandler(root, row = 3, column=4, onchange=setH)
##Moving Platform Label
Label(root, text="---Moving Platform---").grid(row=4, column=1, columnspan=4)
##Speed
Label(root, text="Speed").grid(row = 5, column = 1, columnspan=2)
def setSpeed(text):
    if activePlatform: activePlatform.setSpeed(float(text) if text else 0)
speedEntry = EntryWithChangeHandler(root, row = 5, column=3, columnspan=2, onchange=setSpeed, intsOnly=False, floatsOnly=True)
##dx
Label(root, text="dX").grid(row = 6, column = 1)
def setDX(text):
    if activePlatform: activePlatform.setDXDY(dx = int(text) if text else 0)
dxEntry = EntryWithChangeHandler(root, row = 6, column=2, onchange=setDX)
##dy
Label(root, text="dY").grid(row = 6, column = 3)
def setDY(text):
    if activePlatform: activePlatform.setDXDY(dy = int(text) if text else 0)
dyEntry = EntryWithChangeHandler(root, row = 6, column=4, onchange=setDY)
##Disappearing Label
Label(root, text="---Disappearing Platform---").grid(row=7, column=1, columnspan=4)
##Time On
Label(root, text="tOn").grid(row = 8, column = 1)
def setTOn(text):
    if activePlatform: activePlatform.setT(tOn = int(text) if text else 0)
tOnEntry = EntryWithChangeHandler(root, row = 8, column=2, onchange=setTOn)
##Time Off
Label(root, text="tOff").grid(row = 8, column = 3)
def setTOff(text):
    if activePlatform: activePlatform.setT(tOff = int(text) if text else 0)
tOffEntry = EntryWithChangeHandler(root, row = 8, column=4, onchange=setTOff)
##Time Offset
Label(root, text="Clock Offset").grid(row = 9, column = 1, columnspan=2)
def setTOffset(text):
    if activePlatform: activePlatform.setT(tOffset = int(text) if text else 0)
tOffsetEntry = EntryWithChangeHandler(root, row = 9, column=3, columnspan=2, onchange=setTOffset)
##Danger Label
Label(root, text="---Danger Platform---").grid(row=10, column=1, columnspan=4)
##Respawn X
Label(root, text="Respawn X").grid(row = 11, column = 1, columnspan=2)
def setRespawnX(text):
    if activePlatform: activePlatform.setRespawn(x = int(text) if text else 0)
respawnXEntry = EntryWithChangeHandler(root, row = 11, column=3, columnspan=2, onchange=setRespawnX)
##Respawn X
Label(root, text="Respawn Y").grid(row = 12, column = 1, columnspan=2)
def setRespawnY(text):
    if activePlatform: activePlatform.setRespawn(y = int(text) if text else 0)
respawnYEntry = EntryWithChangeHandler(root, row = 12, column=3, columnspan=2, onchange=setRespawnY)
##Play preview
play = False
def playPause():
    global play
    play = not play
    if play:
        for platform in level:
            platform.playPreview()
    else:
        for platform in level:
            platform.pausePreview()

Button(root, text="Play/Pause Preview", padx=50, pady=10, font=("Helvetic", 12), command=playPause).grid(row = 13, column = 1, columnspan=4)
##Delete
def deletePlatform():
    if activePlatform: activePlatform.delete()
Label(root, text="").grid(row=14, column=1)
Label(root, text="").grid(row=15, column=1)
Button(root, text="Delete Platform", padx=50, pady=10, font=("Helvetic", 12), command=deletePlatform).grid(row = 16, column = 1, columnspan=4)
##Save
Label(root, text="").grid(row=17, column=1)
def save():
    plats = []
    for plat in level:
        plats.append(plat.toCode())
    code = "[" + ", \n".join(plats) + "]"
    with open("level.txt", "w") as f:
        f.write(code)
Button(root, text="Download", padx=50, pady=10, font=("Helvetic", 14), command=save).grid(row = 18, column = 1, columnspan=4)

room.grid(row=0, column=0, rowspan=30)
setup()
root.mainloop()
