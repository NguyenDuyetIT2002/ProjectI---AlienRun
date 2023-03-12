import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 90
screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('AlienRun')

#define fontS
font = pygame.font.SysFont('Bauhaus', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

#define colours
white = (255, 255, 255)
blue = (0, 255, 255)

#define game variable
tile_size = 40
game_over = 0
main_menu = True
level = 1
max_levels = 6
score = 0

#load the image for platform
bg_img = pygame.image.load('img/bg_castle.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

#load sounds
pygame.mixer.music.load('sounds/theme.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
gold_fx = pygame.mixer.Sound('sounds/gold.wav')
gold_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('sounds/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('sounds/game_over.wav')
game_over_fx.set_volume(0.5)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#restart level function
def reset_level(level):
    global map_data, max_levels
    player.reset(90, screen_height - 110)
    slime_group.empty()
    fire_group.empty()
    door_group.empty()
    gold_group.empty()
    floatingstone_group.empty()

    #load level and create map
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        map_data = pickle.load(pickle_in)
    map = Map(map_data)

    return map

#define the game button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #get mouse possition
        pos = pygame.mouse.get_pos()

        #check mouse over and click condition
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        screen.blit(self.image, self.rect)

        return action

#define the player
class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):

        dx = 0
        dy = 0
        walk_cooldown = 10
        col_thresh = tile_size // 2

        if game_over == 0:

            #get keypress
            key = pygame.key.get_pressed()
            if key[pygame.K_w] and self.jumped == False and self.float == False:
                jump_fx.play()
                self.vel_y = -12
                self.jumped = True
            if not key[pygame.K_w]:
                self.jumped = False
            if key[pygame.K_a]:
                dx -= 2
                self.counter += 1
                self.direction = -1
            if key[pygame.K_d]:
                dx += 2
                self.counter += 1
                self.direction = 1
            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >=len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #make gravity
            self.vel_y +=0.7
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #check for collision
            self.float = True
            for tile in map.tile_list:

                #check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                #check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):

                    #check if below ground when jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # check if above the ground when falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.float = False

            #check for collision with enemmy and fire
            if pygame.sprite.spritecollide(self, slime_group, False):
                game_over = -1
                game_over_fx.play()
            if pygame.sprite.spritecollide(self, fire_group, False):
                game_over = -1
                game_over_fx.play()

            #check for collision with the door
            if pygame.sprite.spritecollide(self, door_group, False):
                game_over = 1

            #check for collision with floating stone
            for floatingstone in floatingstone_group:
                #collision with x direction
                if floatingstone.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #collision with y direction
                if floatingstone.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below stone
                    if abs((self.rect.top + dy) - floatingstone.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = floatingstone.rect.bottom - self.rect.top
                    #check if on stone
                    elif abs((self.rect.bottom + dy) - floatingstone.rect.top) < col_thresh:
                        self.rect.bottom = floatingstone.rect.top - 1 #we need the minus 2 because it will let the player float so it won't collide with the x direction of the stone so it still move left or right
                        self.float = False
                        dy = 0
                    #move with floating stone
                    if floatingstone.move_x != 0:
                        self.rect.x += floatingstone.direction

            #update player position
            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
                dy = 0

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('Game Over', font, blue, (screen_width // 2) - 130, screen_height // 2 + 50)
            if self.rect.y > 200:
                self.rect.y -= 5

        #draw player
        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 11):
            img_right = pygame.image.load(f'img/alien{num}.png')
            img_right = pygame.transform.scale(img_right, (tile_size - 5, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/alien_hurt.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (tile_size - 5, 60))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.float = True

class Map():
    def __init__(self, data):
        self.tile_list = []

        #load image
        stone_img = pygame.image.load('img/stone.png')

        #draw the stone
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(stone_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    slime = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    slime_group.add(slime)
                if tile == 3:
                    floatingstone = FloatingStone(col_count * tile_size, row_count * tile_size, 1, 0)
                    floatingstone_group.add(floatingstone)
                if tile == 4:
                    floatingstone = FloatingStone(col_count * tile_size, row_count * tile_size, 0, 1)
                    floatingstone_group.add(floatingstone)
                if tile == 5:
                    fire = Fire(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    fire_group.add(fire)
                if tile == 6:
                    gold = Gold(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    gold_group.add(gold)
                if tile == 7:
                    door = Door(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    door_group.add(door)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/slime.png')
        self.image = pygame.transform.scale(self.image, ((tile_size * 2 // 3), (tile_size * 2 // 3)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.move_count = 0
    def update(self):
        self.rect.x += self.direction
        self.move_count += 1
        #the slime can move in about 2 game tile. When it reach the limit it will change direction
        if abs(self.move_count) > 2 * tile_size:
            self.direction *= -1
            self.move_count *= -1

class FloatingStone(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/stone.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_count = 0
        self.direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        #if move_x = 1 and move_y = 0 then it mean the stone is moving left and right, so x will change and y will stay
        #if move_x = 0 and move_y = 1 then it mean the stone is moving up and down, so x will stay and y will change
        self.rect.x += self.direction * self.move_x
        self.rect.y += self.direction * self.move_y
        self.move_count += 1
        #the floating stone can move in about 1 game tile. When it reach the limit, it will change the direction
        if abs(self.move_count) > tile_size:
            self.direction *= -1
            self.move_count *= -1


class Fire(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/fire.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Gold(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/gold.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/door.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

map_data = []

player = Player(90, screen_height - 110)

slime_group = pygame.sprite.Group()
floatingstone_group = pygame.sprite.Group()
fire_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
gold_group = pygame.sprite.Group()


#load level data an create map
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    map_data = pickle.load(pickle_in)
map = Map(map_data)

#create button
restart_btn = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_btn = Button(screen_width // 2 - 200, screen_height // 2, start_img)
exit_btn = Button(screen_width // 2 + 200, screen_height // 2, exit_img)

run = True
while run:

    clock.tick(fps)

    #load the background
    screen.blit(bg_img, (0,0))

    if main_menu == True:
        if exit_btn.draw():
            run = False
        if start_btn.draw():
            main_menu = False
    else:
        map.draw()

        if game_over == 0:
            slime_group.update()
            floatingstone_group.update()
            #update score
            #check if a gold has been collected
            if pygame.sprite.spritecollide(player, gold_group, True):
                gold_fx.play()
                score += 1
            draw_text('Coin:  ' + str(score), font_score, white, tile_size - 10, 10)

        slime_group.draw(screen)
        floatingstone_group.draw(screen)
        fire_group.draw(screen)
        gold_group.draw(screen)
        door_group.draw(screen)

        game_over = player.update(game_over)

        #if player died
        if game_over == -1:
            if restart_btn.draw():
                map_data = []
                map = reset_level(level)
                game_over = 0
                score = 0

        #if player reach the gate and get to the next level
        if game_over == 1:
            #reset the game and next level
            level += 1
            if level <= max_levels:
                map_data = []
                map = reset_level(level)
                game_over = 0
                pass
            else:
                pass
                draw_text('You Win!!', font, blue, (screen_width // 2) - 140, screen_height // 2 + 10)
                draw_text('Want to play again?', font, blue, (screen_width // 2) - 220, screen_height // 2 + 50)
                #the restart button will let you play the game from level 1 if you completed all the level
                if restart_btn.draw():
                    level = 1
                    map_data = []
                    map = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
