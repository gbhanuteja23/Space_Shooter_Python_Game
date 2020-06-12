'''
Function:
	Space Shooter
Author:
	G Bhanuteja
GitHub Profile link:
	https://github.com/gbhanuteja23
'''
import os
import sys
import pygame
import random


WIDTH = 956
HEIGHT = 560


'''Define button'''
def BUTTON(screen, position, text):
	bwidth = 310
	bheight = 65
	left, top = position
	pygame.draw.line(screen, (150, 150, 150), (left, top), (left+bwidth, top), 5)
	pygame.draw.line(screen, (150, 150, 150), (left, top-2), (left, top+bheight), 5)
	pygame.draw.line(screen, (50, 50, 50), (left, top+bheight), (left+bwidth, top+bheight), 5)
	pygame.draw.line(screen, (50, 50, 50), (left+bwidth, top+bheight), [left+bwidth, top], 5)
	pygame.draw.rect(screen, (100, 100, 100), (left, top, bwidth, bheight))
	font = pygame.font.Font('./resources/font/simkai.ttf', 50)
	text_render = font.render(text, 1, (255, 0, 0))
	return screen.blit(text_render, (left+50, top+10))


'''Start interface'''
def start_interface(screen):
	clock = pygame.time.Clock()
	while True:
		button_1 = BUTTON(screen, (330, 190), 'Single player mode')
		button_2 = BUTTON(screen, (330, 305), 'Double mode')
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if button_1.collidepoint(pygame.mouse.get_pos()):
					return 1
				elif button_2.collidepoint(pygame.mouse.get_pos()):
					return 2
		clock.tick(60)
		pygame.display.update()


'''bullet'''
class Bullet(pygame.sprite.Sprite):
	def __init__(self, idx, position):
		pygame.sprite.Sprite.__init__(self)
		self.imgs = ['./resources/imgs/bullet.png']
		self.image = pygame.image.load(self.imgs[0]).convert_alpha()
		self.image = pygame.transform.scale(self.image, (10, 10))
		# position
		self.rect = self.image.get_rect()
		self.rect.left, self.rect.top = position
		self.position = position
		# speed
		self.speed = 8
		# Player ID
		self.playerIdx = idx
	'''Moving bullet'''
	def move(self):
		self.position = self.position[0], self.position[1] - self.speed
		self.rect.left, self.rect.top = self.position
	'''Draw bullets'''
	def draw(self, screen):
		screen.blit(self.image, self.rect)


'''Asteroid'''
class Asteroid(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.imgs = ['./resources/imgs/asteroid.png']
		self.image = pygame.image.load(self.imgs[0]).convert_alpha()
		# position
		self.rect = self.image.get_rect()
		self.position = (random.randrange(20, WIDTH-40), -64)
		self.rect.left, self.rect.top = self.position
		# speed
		self.speed = random.randrange(3, 9)
		self.angle = 0
		self.angular_velocity = random.randrange(1, 5)
		self.rotate_ticks = 3
	'''Moving asteroid'''
	def move(self):
		self.position = self.position[0], self.position[1] + self.speed
		self.rect.left, self.rect.top = self.position
	'''Spinning asteroid'''
	def rotate(self):
		self.rotate_ticks -= 1
		if self.rotate_ticks == 0:
			self.angle = (self.angle + self.angular_velocity) % 360
			orig_rect = self.image.get_rect()
			rot_image = pygame.transform.rotate(self.image, self.angle)
			rot_rect = orig_rect.copy()
			rot_rect.center = rot_image.get_rect().center
			rot_image = rot_image.subsurface(rot_rect).copy()
			self.image = rot_image
			self.rotate_ticks = 3
	'''Draw asteroids'''
	def draw(self, screen):
		screen.blit(self.image, self.rect)


'''spaceship'''
class Ship(pygame.sprite.Sprite):
	def __init__(self, idx):
		pygame.sprite.Sprite.__init__(self)
		self.imgs = ['./resources/imgs/ship.png', './resources/imgs/ship_exploded.png']
		self.image = pygame.image.load(self.imgs[0]).convert_alpha()
		self.explode_img = pygame.image.load(self.imgs[1]).convert_alpha()
		# position
		self.position = {'x': random.randrange(-10, 918), 'y': random.randrange(-10, 520)}
		self.rect = self.image.get_rect()
		self.rect.left, self.rect.top = self.position['x'], self.position['y']
		# speed
		self.speed = {'x': 10, 'y': 5}
		# Player ID
		self.playerIdx = idx
		# Bullet cooling time
		self.cooling_time = 0
		# For explosion
		self.explode_step = 0
	'''Spaceship explosion'''
	def explode(self, screen):
		img = self.explode_img.subsurface((48*(self.explode_step-1), 0), (48, 48))
		screen.blit(img, (self.position['x'], self.position['y']))
		self.explode_step += 1
	'''Mobile spaceship'''
	def move(self, direction):
		if direction == 'left':
			self.position['x'] = max(-self.speed['x']+self.position['x'], -10)
		elif direction == 'right':
			self.position['x'] = min(self.speed['x']+self.position['x'], 918)
		elif direction == 'up':
			self.position['y'] = max(-self.speed['y']+self.position['y'], -10)
		elif direction == 'down':
			self.position['y'] = min(self.speed['y']+self.position['y'], 520)
		self.rect.left, self.rect.top = self.position['x'], self.position['y']
	'''Painted spaceship'''
	def draw(self, screen):
		screen.blit(self.image, self.rect)
	'''shooting'''
	def shot(self):
		return Bullet(self.playerIdx, (self.rect.center[0] - 5, self.position['y'] - 5))


'''game interface'''
def GameDemo(num_player, screen):
	pygame.mixer.music.load(("./resources/sounds/Cool Space Music.mp3"))
	pygame.mixer.music.set_volume(0.4)
	pygame.mixer.music.play(-1)
	explosion_sound = pygame.mixer.Sound('./resources/sounds/boom.wav')
	fire_sound = pygame.mixer.Sound('./resources/sounds/shot.ogg')
	font = pygame.font.Font('./resources/font/simkai.ttf', 20)
	# Game background image
	bg_imgs = ['./resources/imgs/bg_big.png',
			   './resources/imgs/seamless_space.png',
			   './resources/imgs/space3.jpg']
	bg_move_dis = 0
	bg_1 = pygame.image.load(bg_imgs[0]).convert()
	bg_2 = pygame.image.load(bg_imgs[1]).convert()
	bg_3 = pygame.image.load(bg_imgs[2]).convert()
	# Players, bullets and asteroid elves
	playerGroup = pygame.sprite.Group()
	bulletGroup = pygame.sprite.Group()
	asteroidGroup = pygame.sprite.Group()
	# The time interval to generate an asteroid
	asteroid_ticks = 90
	for i in range(num_player):
		playerGroup.add(Ship(i+1))
	clock = pygame.time.Clock()
	#fraction
	Score_1 = 0
	Score_2 = 0
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		# Player one: ↑↓←→ control, j shooting
		# Player two: wsad control, space shooting
		pressed_keys = pygame.key.get_pressed()
		i = -1
		for player in playerGroup:
			i += 1
			direction = None
			if i == 0:
				if pressed_keys[pygame.K_UP]:
					direction = 'up'
				elif pressed_keys[pygame.K_DOWN]:
					direction = 'down'
				elif pressed_keys[pygame.K_LEFT]:
					direction = 'left'
				elif pressed_keys[pygame.K_RIGHT]:
					direction = 'right'
				if direction:
					player.move(direction)
				if pressed_keys[pygame.K_LSHIFT]:
					if player.cooling_time == 0:
						fire_sound.play()
						bulletGroup.add(player.shot())
						player.cooling_time = 20
			elif i == 1:
				if pressed_keys[pygame.K_w]:
					direction = 'up'
				elif pressed_keys[pygame.K_s]:
					direction = 'down'
				elif pressed_keys[pygame.K_a]:
					direction = 'left'
				elif pressed_keys[pygame.K_d]:
					direction = 'right'
				if direction:
					player.move(direction)
				if pressed_keys[pygame.K_SPACE]:
					if player.cooling_time == 0:
						fire_sound.play()
						bulletGroup.add(player.shot())
						player.cooling_time = 20
			if player.cooling_time > 0:
				player.cooling_time -= 1
		if (Score_1 + Score_2) < 500:
			background = bg_1
		elif (Score_1 + Score_2) < 1500:
			background = bg_2
		else:
			background = bg_3
		# Move the background image down to achieve the effect of the spaceship moving up
		screen.blit(background, (0, -background.get_rect().height + bg_move_dis))
		screen.blit(background, (0, bg_move_dis))
		bg_move_dis = (bg_move_dis + 2) % background.get_rect().height
		# Spawn asteroid
		if asteroid_ticks == 0:
			asteroid_ticks = 90
			asteroidGroup.add(Asteroid())
		else:
			asteroid_ticks -= 1
		# Painted spaceship
		for player in playerGroup:
			if pygame.sprite.spritecollide(player, asteroidGroup, True, None):
				player.explode_step = 1
				explosion_sound.play()
			elif player.explode_step > 0:
				if player.explode_step > 3:
					playerGroup.remove(player)
					if len(playerGroup) == 0:
						return
				else:
					player.explode(screen)
			else:
				player.draw(screen)
		# Draw bullets
		for bullet in bulletGroup:
			bullet.move()
			if pygame.sprite.spritecollide(bullet, asteroidGroup, True, None):
				bulletGroup.remove(bullet)
				if bullet.playerIdx == 1:
					Score_1 += 1
				else:
					Score_2 += 1
			else:
				bullet.draw(screen)
		# Draw asteroids
		for asteroid in asteroidGroup:
			asteroid.move()
			asteroid.rotate()
			asteroid.draw(screen)
		# Show score
		Score_1_text = 'Player one score: %s' % Score_1
		Score_2_text = 'Player two score: %s' % Score_2
		text_1 = font.render(Score_1_text, True, (0, 0, 255))
		text_2 = font.render(Score_2_text, True, (255, 0, 0))
		screen.blit(text_1, (2, 5))
		screen.blit(text_2, (2, 35))
		pygame.display.update()
		clock.tick(60)


'''End interface'''
def end_interface(screen):
	clock = pygame.time.Clock()
	while True:
		button_1 = BUTTON(screen, (330, 190), 'Restart')
		button_2 = BUTTON(screen, (330, 305), 'exit the game')
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if button_1.collidepoint(pygame.mouse.get_pos()):
					return
				elif button_2.collidepoint(pygame.mouse.get_pos()):
					pygame.quit()
					sys.exit()
		clock.tick(60)
		pygame.display.update()


'''Main function'''
def main():
	pygame.init()
	pygame.font.init()
	pygame.mixer.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption('Space Shooter Made By:  G Bhanuteja')
	num_player = start_interface(screen)
	if num_player == 1:
		while True:
			GameDemo(num_player=1, screen=screen)
			end_interface(screen)
	else:
		while True:
			GameDemo(num_player=2, screen=screen)
			end_interface(screen)


'''run'''
if __name__ == '__main__':
	main()