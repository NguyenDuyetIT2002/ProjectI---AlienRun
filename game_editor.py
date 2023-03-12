import pygame
import pickle
from os import path


pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
tile_size = 30
cols = 20
margin = 80
screen_width = tile_size * cols
screen_height = (tile_size * cols) + margin

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Level Editor')


#load images
bg_img = pygame.image.load('img/bg_castle.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height - margin))
stone_img = pygame.image.load('img/stone.png')
slime_img = pygame.image.load('img/slime.png')
stone_x_img = pygame.image.load('img/stone_move_x.png')
stone_y_img = pygame.image.load('img/stone_move_y.png')
fire_img = pygame.image.load('img/fire.png')
gold_img = pygame.image.load('img/gold.png')
door_img = pygame.image.load('img/door.png')
save_img = pygame.image.load('img/save_btn.png')
load_img = pygame.image.load('img/load_btn.png')


#define game variables
clicked = False
level = 1

#define colours
white = (255, 255, 255)
green = (144, 201, 120)

font = pygame.font.SysFont('Futura', 24)

#create empty tile list
map_data = []
for row in range(20):
	r = [0] * 20
	map_data.append(r)

#create boundary
for tile in range(0, 20):
	map_data[19][tile] = 1
	map_data[0][tile] = 1
	map_data[tile][0] = 1
	map_data[tile][19] = 1

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_grid():
	for c in range(21):
		#vertical lines
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
		#horizontal lines
		pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))


def draw_world():
	for row in range(20):
		for col in range(20):
			if map_data[row][col] > 0:
				if map_data[row][col] == 1:
					#stone
					img = pygame.transform.scale(stone_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if map_data[row][col] == 2:
					#enemy
					img = pygame.transform.scale(slime_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if map_data[row][col] == 3:
					#floating stone move left and right
					img = pygame.transform.scale(stone_x_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if map_data[row][col] == 4:
					#floating stone move up and down
					img = pygame.transform.scale(stone_y_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if map_data[row][col] == 5:
					#fire
					img = pygame.transform.scale(fire_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size // 2)))
				if map_data[row][col] == 6:
					#gold
					img = pygame.transform.scale(gold_img, (tile_size // 2, tile_size // 2))
					screen.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
				if map_data[row][col] == 7:
					#exit door
					img = pygame.transform.scale(door_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

#create load and save buttons
save_button = Button(screen_width // 2 - 150, screen_height - 70, save_img)
load_button = Button(screen_width // 2 + 50, screen_height - 70, load_img)

#main game loop
run = True
while run:

	clock.tick(fps)

	#draw background
	screen.fill(green)
	screen.blit(bg_img, (0, 0))

	#load and save level
	if save_button.draw():
		#save level data
		pickle_out = open(f'level{level}_data', 'wb')
		pickle.dump(map_data, pickle_out)
		pickle_out.close()
	if load_button.draw():
		#load in level data
		if path.exists(f'level{level}_data'):
			pickle_in = open(f'level{level}_data', 'rb')
			world_data = pickle.load(pickle_in)


	#show the grid and draw the level tiles
	draw_grid()
	draw_world()


	#text showing current level
	draw_text(f'Level: {level}', font, white, tile_size, screen_height - 50)
	draw_text('Press UP or DOWN to change level', font, white, tile_size, screen_height - 30)

	#event handler
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#mouseclicks to change tiles
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			#check that the coordinates are within the tile area
			if x < 20 and y < 20:
				#update tile value
				if pygame.mouse.get_pressed()[0] == 1:
					map_data[y][x] += 1
					if map_data[y][x] > 7:
						map_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					map_data[y][x] -= 1
					if map_data[y][x] < 0:
						map_data[y][x] = 8
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		#up and down key presses to change level number
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				level += 1
			elif event.key == pygame.K_s and level > 1:
				level -= 1

	#update game display window
	pygame.display.update()

pygame.quit()