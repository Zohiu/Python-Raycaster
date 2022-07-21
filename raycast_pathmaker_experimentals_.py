import pygame
import random


class Config:
    width = 800
    height = 800
    fps = 30


config = Config()


class Directions:
    x = 0
    y = 1


dir = Directions()

pygame.init()
clock = pygame.time.Clock()
dt = clock.tick(config.fps) / 1000

screen = pygame.display.set_mode((config.width, config.height))
screen.fill((0, 0, 0))


class DrawSprite(pygame.sprite.Sprite):
    def __init__(self, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([size, size])
        self.color = (255, 255, 255)
        self.image.fill(self.color)
        self.position = [0, 0]

    def draw(self):
        screen.blit(self.image, self.position)


def draw_map_straight(size, extremity, main_direction, constant_direction, start_position, end_axis):
    sprite = DrawSprite(size)
    sprite.position = [start_position[0], start_position[1]]
    sprite.draw()
    pos_before = sprite.position
    while True:
        adder = random.choice((-size, size))
        for x in range(random.randint(1, extremity)):
            
            sprite.position[main_direction] += adder
            
            if sprite.position[main_direction] > config.width - size or sprite.position[0] < 0:
                sprite.position[main_direction] -= adder
            
            sprite.draw()
            
        for y in range(x):
            sprite.position[constant_direction] += size
            sprite.draw()
        
        if sprite.position[constant_direction] > end_axis:
            return pos_before, sprite.position


all_ends = []

all_ends += draw_map_straight(10, 2, dir.x, dir.y, (config.width / 2, 0), config.width)
all_ends += draw_map_straight(10, 2, dir.x, dir.y, (config.width / 4, 0), config.width)
all_ends += draw_map_straight(10, 2, dir.x, dir.y, (config.width - config.width / 4, 0), config.width)

all_ends += draw_map_straight(10, 2, dir.y, dir.x, (0, config.height / 2), config.height)
all_ends += draw_map_straight(10, 2, dir.y, dir.x, (0, config.height / 4), config.height)
all_ends += draw_map_straight(10, 2, dir.y, dir.x, (0, config.height - config.height / 4), config.height)

print(all_ends)

while True:
    dt = clock.tick(config.fps) / 1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    
    pygame.display.flip()