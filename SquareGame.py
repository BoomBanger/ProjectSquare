from tkinter import * 
from math import *

root = Tk()
root.title('SquareGame')
roomSize = 700


class Box:
	def __init__(self):
		self.x = 15
		self.y = 15
		self.dy = 0
		self.dx = 0
		self.g = -0.1
		self.jump = 3
		self.step = 2
		self.width = 10
		self.height = 10
		self.onGround = False
		self.box = room.create_rectangle(self.x - self.width / 2, self.y - self.height / 2, self.x + self.width / 2, self.y + self.height / 2, fill='blue')
		
		self.platforms = [Platform(130, 670, 170, 680), Platform(40, 640, 100, 660), Platform(200, 650, 250, 700),
			Platform(250, 570, 280, 700), Platform(320, 520, 340, 630), Platform(30, 0, 40, 660),
			DisappearingPlatform(320, 630, 340, 700, 1, 1, 0), DisappearingPlatform(370, 660, 390, 680, 1, 1, 0),
			Platform(410, 630, 430, 700), DisappearingPlatform(470, 660, 490, 670, 3, 1, 0),
			DisappearingPlatform(520, 640, 540, 650, 3, 1, 0), DisappearingPlatform(555, 670, 585, 680, 3, 1, 2),
			Platform(565, 570, 575, 650), MovingPlatform(60, 600, 90, 610, 90, 0, 1), DangerPlatform(200, 640, 250, 650, self.x, self.y),
			DangerPlatform(430, 690, 700, 700, self.x, self.y), DisappearingPlatform(610, 640, 630, 650, 3, 1, 0),
			DisappearingPlatform(670, 610, 690, 620, 3, 1, 0), DisappearingPlatform(610, 580, 630, 590, 3, 1, 1), 
			MovingPlatform(535, 450, 555, 460, 0, 80, 0.2), Platform(445, 500, 448, 510), Platform(238, 510, 241, 520), 
			MovingPlatform(100, 450, 120, 460, 0, 100, 4), Platform(140, 440, 170, 450)]
		

		room.after(10, self.loop)
		
	def loop(self):
		xStep = (keyboard.is_pressed('right') - keyboard.is_pressed('left')) * self.step
		self.dy -= self.g
		if (keyboard.is_pressed('up') or keyboard.is_pressed('space')) and self.onGround:
			self.dy = -self.jump
		self.onGround = False
		self.x += xStep
		self.y += self.dy
		self.dx = xStep
		room.move(self.box, xStep, self.dy)
		self.bounding()
		room.after(10, self.loop)
		
	def bounding(self):
		self.boundingFloor()
		self.boundingSides()
		self.boundingPlatforms()
			
	def boundingFloor(self):
		if self.y + (self.height / 2) > roomSize:
			yStep = (self.y + (self.height / 2)) - roomSize
			self.y -= yStep
			self.dy = 0
			room.move(self.box, 0, -yStep)
			self.onGround = True
			
	def boundingSides(self):
		if self.x + (self.width / 2) > roomSize:
			xStep = (self.x + (self.width / 2)) - roomSize
			self.x -= xStep
			room.move(self.box, -xStep, 0)
		if self.x - (self.width / 2) < 0:
			xStep = (self.x - (self.width / 2)) 
			self.x -= xStep
			room.move(self.box, -xStep, 0)
			
	def boundingPlatforms(self):
		for platform in self.platforms:
			if isinstance(platform, MovingPlatform): platform.slide()
			move = platform.bounding(self.x, self.y, self.width, self.height, self.dx, self.dy)
			self.x += move[0]
			self.y += move[1]
			room.move(self.box, move[0], move[1])
			if move[2]:
				self.dy = 0
			if move[3]:
				self.onGround = True


class Platform:
	
	def __init__(self, x1, y1, x2, y2):
		self.x1 = x1
		self.y1 = y2
		self.x2 = x2
		self.y2 = y2
		self.top = min(y1, y2)
		self.bottom = max(y1, y2)
		self.left = min(x1, x2)
		self.right = max(x1, x2)
		self.height = abs(y1 - y2)
		self.width = abs(x1 - x2)
		self.platform = room.create_rectangle(x1, y1, x2, y2, fill='black')
		
	def bounding(self, x, y, w, h, dx, dy, pdx = 0, pdy = 0):
		xStep = 0
		yStep = 0
		resetDy = False
		ground = False
		if x + (w / 2) > self.left and x - (w / 2) < self.right:
			if y + (h / 2) > self.top and y + (h / 2) - dy <= self.top - pdy:
				yStep = self.top - (y + (h / 2))
				resetDy = True
				ground = True
			elif y - (h / 2) < self.bottom and y - (h / 2) - dy >= self.bottom - pdy:
				yStep = self.bottom - (y - (h / 2))
				resetDy = True
		if y - (h / 2) < self.bottom and y + (h / 2) > self.top:
			if x - (w / 2) < self.right and x - (w / 2) - dx >= self.right - pdx:
				xStep = self.right - (x - (w / 2))
			elif x + (w / 2) > self.left and x + (w / 2) - dx <= self.left - pdx:
				xStep = self.left - (x + (w / 2))
		return (xStep, yStep, resetDy, ground)
		
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
		else:
			room.itemconfigure(self.platform, fill=color)
			room.itemconfigure(self.platform, state='normal')
			
		
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
		self.forward = True
		
	def bounding(self, x, y, w, h, dx, dy):
		output = super().bounding(x, y, w, h, dx, dy, self.xSpeed * (1 if self.forward else -1), self.ySpeed * (0 if self.forward else -1))
		xStep = output[0]
		yStep = output[1]
		resetDy = output[2]
		ground = output[3]
		if ground:
			xStep += self.xSpeed * (1 if self.forward else -1)
			yStep += self.ySpeed * (1 if self.forward else -1)
		return (xStep, yStep, resetDy, ground)
		
	def slide(self):
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
	
	def bounding(self, x, y, w, h, dx, dy):
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
		return (0, 0, False, False)

class DangerPlatform(Platform):
	def __init__(self, x1, y1, x2, y2, startX, startY):
		super().__init__(x1, y1, x2, y2)
		self.startX = startX
		self.startY = startY
		super().changeColor('red')
		
	def bounding(self, x, y, w, h, dx, dy):
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
		else: return (0, 0, False, False)
		return (xStep, yStep, resetDy, ground)

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
			

room = Canvas(root, height=roomSize, width=roomSize)

keyboard = Keyboard()
b = Box()


room.pack()
room.focus_set()
root.mainloop()
