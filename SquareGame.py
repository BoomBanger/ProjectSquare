from tkinter import * 
import keyboard
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
		self.box = room.create_rectangle(10, 10, 10 + self.width, 10 + self.height, fill='blue')
		
		self.platforms = [Platform(130, 670, 170, 680), Platform(0, 640, 100, 660), Platform(200, 640, 250, 700), Platform(250, 570, 280, 700), Platform(320, 520, 340, 630)]
		self.movingPlatforms = [MovingPlatform(40, 600, 90, 610, 110, 0, 0.2)]
		
		room.after(10, self.loop)
		
	def loop(self):
		xStep = (keyboard.is_pressed('right') - keyboard.is_pressed('left')) * self.step
		##yStep = (keyboard.is_pressed('down') - keyboard.is_pressed('up')) * self.step
		self.dy -= self.g
		if(keyboard.is_pressed('up') and self.onGround):
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
		self.boundingMovingPlatforms()
			
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
			move = platform.bounding(self.x, self.y, self.width, self.height, self.dx, self.dy)
			self.x += move[0]
			self.y += move[1]
			room.move(self.box, move[0], move[1])
			if move[2]:
				self.dy = 0
			if move[3]:
				self.onGround = True
			
	def boundingMovingPlatforms(self):
		for platform in self.movingPlatforms:
			platform.slide()
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
		
	def bounding(self, x, y, w, h, dx, dy):
		xStep = 0
		yStep = 0
		resetDy = False
		ground = False
		if x + (w / 2) > self.left and x - (w / 2) < self.right:
			if y + (h / 2) > self.top and y + (h / 2) - dy <= self.top:
				yStep = self.top - (y + (h / 2))
				resetDy = True
				ground = True
			elif y - (h / 2) < self.bottom and y - (h / 2) - dy >= self.bottom:
				yStep = self.bottom - (y - (h / 2))
				resetDy = False
		if y - (h / 2) < self.bottom and y + (h / 2) > self.top:
			if x - (w / 2) < self.right and x - (w / 2) - dx >= self.right:
				xStep = self.right - (x - (w / 2))
			elif x + (w / 2) > self.left and x + (w / 2) - dx <= self.left:
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
		room.itemConfig(self.platform, color)
		
class MovingPlatform(Platform):
	def __init__(self, x1, y1, x2, y2, xDelta, yDelta, speed):
		super().__init__(x1, y1, x2, y2)
		distance = sqrt(xDelta ** 2 + yDelta ** 2)
		scale = speed / distance
		self.xSpeed = xDelta * scale
		self.ySpeed = yDelta * scale
		self.xDelta = xDelta
		self.yDelta = yDelta
		self.x = 0
		self.y = 0
		self.forward = True
		
	def bounding(self, x, y, w, h, dx, dy):
		output = super().bounding(x, y, w, h, dx, dy)
		xStep = output[0]
		yStep = output[1]
		resetDy = output[2]
		ground = output[3]
		if ground:
			xStep += self.xSpeed * (1 if self.forward else -1)
			yStep += self.ySpeed * (1 if self.forward else -1)
		return (xStep, yStep, resetDy, ground)
		
	def slide(self):
		dx = self.xSpeed * (1 if self.forward else -1)
		dy = self.ySpeed * (1 if self.forward else -1)
		super().move(dx, dy)
		self.x += dx
		self.y += dy
		if (self.x >= self.xDelta and self.y >= self.yDelta) or (self.x <= 0 and self.y <= 0):
			self.forward = not self.forward
			
class DisappearingPlatform(Platform):
	def __init__(self, x1, y1, x2, y2, tOn, tOff, tShift):
		super().__init__(x1, y1, x2, y2)
		self.tOn = tOn
		self.tOff = tOff
		self.time = tShift
		super().changeColor('purple')
	
	def bounding(self, x, y, w, h, dx, dy):
		self.time += 1
		if self.time < tOn / 3:
			super().changeColor('green')
		

room = Canvas(root, height=roomSize, width=roomSize)
room = Canvas(root, height=roomSize, width=roomSize)

b = Box()


room.pack()
root.mainloop()
