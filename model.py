import pygame
import neat
import os
import time
import random


BIRD_IMG1 = pygame.image.load(os.path.join('imgs', 'bird1.png'))
BIRD_IMG2 = pygame.image.load(os.path.join('imgs', 'bird2.png'))
BIRD_IMG3 = pygame.image.load(os.path.join('imgs', 'bird3.png'))
BIRD_IMGS = [pygame.transform.scale2x(BIRD_IMG1), pygame.transform.scale2x(BIRD_IMG2), pygame.transform.scale2x(BIRD_IMG3)]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))

class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y
		# the bird should start looking straight at the beginning
		self.tilt = 0
		# keep track of the frames
		self.tick_count = 0
		self.velocity = 0
		self.hight = self.y
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		# to go up use negative value as the point 0,0
		# is at the upper left corner
		self.velocity = -10.5
		# keep track of when are we last jump
		self.tick_count = 0
		# where the bird started to jump
		self.height = self.y
		

	def move(self):
		self.tick_count += 1
		distance = self.velocity * self.tick_count + 1.5 * self.tick_count**2
		
		# slow down the distance
		if distance > 16:
			distance = 16
		
		self.y = self.y + distance

		# if going up
		if distance < 0:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		# if going down
		else:
			if self.tilt > -90 and self.y > self.hight + 50:
				self.tilt -= 10

	def draw(self, window):
		self.img_count += 1

		if self.img_count < self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0
		
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2
		
		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
		window.blit(rotated_image, new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

class Pipe:
	GAP = 200
	VELOCITY = 5

	def __init__(self, x):
		self.x = x
		self.height = 0

		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIP_BOTTOM = PIPE_IMG

		self.passed = False
		self.set_height()
	

	def set_height(self):
		# generate random height
		# set the y of the top pipe to the height of the 
		# original pipe + random value
		# set the y of the bottom pipe to the random value + gap 
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP
	

	def move(self):
		self.x -= self.VELOCITY


	def draw(self,window):
		window.blit(self.PIPE_TOP, (self.x, self.top))
		window.blit(self.PIP_BOTTOM, (self.x, self.bottom))
	

	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIP_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		top_point = bird_mask.overlap(top_mask, top_offset)
		bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)

		# check if the masks collide
		if top_point or bottom_point:
			return True
		
		return False


class Base:
	VELOCITY = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH
	
	def move(self):
		self.x1 -= self.VELOCITY
		self.x2 -= self.VELOCITY

		# check if the first image is out side of the window
		# if true append it at the end of the second image
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		# check if the second image is out side of the window
		# if true append it at the end of the first image
		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	
	def draw(self, window):
		window.blit(self.IMG, (self.x1, self.y))
		window.blit(self.IMG, (self.x2, self.y))

	
	def collide(self,bird):
		bird_mask = bird.get_mask()
		base_mask = pygame.mask.from_surface(self.IMG)

		first_offset = (self.x1 - bird.x, self.y - round(bird.y))
		second_offset = (self.x2 - bird.x, self.y - round(bird.y))

		first_point = bird_mask.overlap(base_mask, first_offset)
		second_point = bird_mask.overlap(base_mask, second_offset)

		# check if the masks collide
		if first_point or second_point:
			return True
		
		return False