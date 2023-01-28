import pygame
# Numpy is slower so I use default math module ok
from math import radians, sin, cos
import threading

class Ray(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = accuracy
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill((255, 255, 255))
        self.og_image = self.image
        self.rect = self.image.get_rect()
        self.pos = self.rect.center
        
        self.angle = 0
        self.steps = 0
        self.max_steps = int(render_distance / accuracy / minimap_smallness)
        self.collided = False
        self.collidercolor = None
        
        # Ray memory to draw previous result
        self.last_color = (0, 0, 0)
        self.last_height = 0
    
    def show_last(self, draw_position):
        pygame.draw.line(screen, self.last_color, (draw_position, HEIGHT / 2 - self.last_height), (draw_position, HEIGHT / 2 + self.last_height), round(line_thickness))
    
    def run(self, startpos, angle):
        self.collided = False
        self.angle = angle
        self.steps = 0
        self.pos = startpos
        self.image = pygame.transform.rotate(self.og_image, angle)
        rad = radians(angle)
        this_mask = pygame.mask.from_surface(self.image)
        
        for i in range(self.max_steps):
            direction = pygame.Vector2(-sin(rad) * self.size, -cos(rad) * self.size)
            self.pos = (self.pos[0] + direction[0], self.pos[1] + direction[1])
            
            if render_mask.overlap(this_mask, (self.pos[0] - render_overlay.rect.x, self.pos[1] - render_overlay.rect.y)):
                self.steps += 1
                self.size = accuracy
            else:
                self.steps += 12
                self.size = 12
            
            offset_x = self.pos[0] - gamemap.rect.x
            offset_y = self.pos[1] - gamemap.rect.y
            
            if map_mask.overlap(this_mask, (offset_x, offset_y)):
                self.collided = True
                colortest = gamemap.image.get_at((int(offset_x), int(offset_y)))[:3]
                self.collidercolor = colortest
                self.collided = True
                break

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *grps):
        super().__init__(*grps)
        self.og_image = pygame.image.load('player.png')
        self.og_image = pygame.transform.scale(self.og_image, (int(25 / minimap_smallness), int(25 / minimap_smallness)))
        self.image = self.og_image
        self.rect = self.image.get_rect(center = pos)
        
        self.angle = 0
        self.change_angle = 0
    
    def rotate(self, new_angle):
        self.angle = new_angle
        self.image = pygame.transform.rotate(self.og_image, self.angle % 360)
        self.rect = self.image.get_rect(center = self.rect.center)

class Map(pygame.sprite.Sprite):
    def __init__(self, size, *grps):
        super().__init__(*grps)
        self.image = pygame.image.load('map_256.png')
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()

class RenderOverlay(pygame.sprite.Sprite):
    def __init__(self, size, *grps):
        super().__init__(*grps)
        self.image = pygame.image.load('map_overlay_128.png')
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()

def playerMove(x, y):
    pos = player.rect.center
    
    direction = pygame.Vector2(x * deltatime, y * deltatime)
    pos += direction
    player.rect.center = round(pos[0]), round(pos[1])
    
    this_mask = pygame.mask.from_surface(player.image)
    offset_x = player.rect.x - gamemap.rect.x
    offset_y = player.rect.y - gamemap.rect.y
    
    if map_mask.overlap(this_mask, (offset_x, offset_y)):
        pos = player.rect.center
        direction = pygame.Vector2(-x * deltatime, -y * deltatime)
        pos += direction
        player.rect.center = round(pos[0]), round(pos[1])

def run_single_ray(ray, draw_position):
    ray.run(player.rect.center, player.angle + (rays.index(ray) * ray_difference) - fov)
    if ray.collided:
        if minimap_rays:
            pygame.draw.line(screen, (255, 255, 255), player.rect.center, ray.pos, ray.size)
        val = ray.steps * cos(radians(ray.angle - player.angle))
        
        # Map the distance value to brightness.
        in_min = 0
        in_max = ray.max_steps
        out_min = 255
        out_max = 0
        brightness = ((ray.steps - in_min) * (out_max - out_min) / (in_max - in_min) + out_min) - 50
        if brightness > 255:
            brightness = 255
        elif brightness < 48:
            brightness = 48
        
        if minimap_rays:
            pygame.draw.circle(screen, (0, brightness, 0), ray.pos, ray.size * 4)
        
        # Map the distance value to height
        height = 15000 / val
        texture_offset_x = ray.pos[0]
        texture_offset_y = ray.pos[1]
        
        if ray.collidercolor == (0, 0, 0):
            color = (0, 0, brightness)
        else:
            color = (0, 0, brightness - 25)
        
        # Actual game line
        
        ray.last_color = color
        ray.last_height = height
        pygame.draw.line(screen, color, (draw_position, HEIGHT / 2 - height), (draw_position, HEIGHT / 2 + height), round(line_thickness))
    
    else:
        # Minimap
        if minimap_rays:
            pygame.draw.line(screen, (255, 255, 255), player.rect.center, ray.pos, ray.size)
            pygame.draw.circle(screen, (255, 0, 0), ray.pos, ray.size * 4)

pygame.init()
clock = pygame.time.Clock()
deltatime = clock.tick(30) / 1000

WIDTH = 1700
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))

minimap_smallness = 2
resolution = 75
accuracy = 1
fov = 35
render_distance = 1000
minimap_rays = True

sprites = pygame.sprite.Group()
objects = pygame.sprite.Group()

map_size = HEIGHT / minimap_smallness
render_overlay = RenderOverlay(map_size, sprites, objects)
render_overlay.rect.center = (WIDTH - map_size / 2, HEIGHT / 2 / minimap_smallness)

render_mask = pygame.mask.from_surface(render_overlay.image)
screen.blit(render_overlay.image, (WIDTH, HEIGHT))

# MAP
gamemap = Map(map_size, sprites, objects)
gamemap.rect.center = (WIDTH - map_size / 2, HEIGHT / 2 / minimap_smallness)

map_mask = pygame.mask.from_surface(gamemap.image)
screen.blit(gamemap.image, (WIDTH, HEIGHT))

game_window_border_size = 25

game_window_width = WIDTH - map_size - game_window_border_size / 2

player_rotation = 0
player = Player((gamemap.rect.x + 100 / minimap_smallness, gamemap.rect.y + 100 / minimap_smallness), sprites)

ray_difference = fov * 2 / resolution

rays = []
for i in range(resolution):
    rays.append(Ray())

rotation_speed = 100
active_rotation = 0

walk_speed = 50
sprint_multiplier = 1.75
active_walking = 0
strafe_speed = 0
fps = 60

font_size = 35
font = pygame.font.Font("font.ttf", font_size)

# The background gradient surfaces!
colour_rect_1 = pygame.Surface((2, 2))  # tiny! 2x2 bitmap
pygame.draw.line(colour_rect_1, (0, 0, 48), (0, 0), (1, 0))  # left colour line
pygame.draw.line(colour_rect_1, (0, 0, 128), (0, 1), (1, 1))  # right colour line
target_rect_1 = pygame.Rect(0, HEIGHT / 2, game_window_width, HEIGHT / 2)
colour_rect_1 = pygame.transform.smoothscale(colour_rect_1, (target_rect_1.width, target_rect_1.height))  # stretch!

colour_rect_2 = pygame.Surface((2, 2))  # tiny! 2x2 bitmap
pygame.draw.line(colour_rect_2, (0, 0, 128), (0, 0), (1, 0))  # left colour line
pygame.draw.line(colour_rect_2, (0, 0, 48), (0, 1), (1, 1))  # right colour line
target_rect_2 = pygame.Rect(0, 0, game_window_width, HEIGHT / 2)
colour_rect_2 = pygame.transform.smoothscale(colour_rect_2, (target_rect_2.width, target_rect_2.height))  # stretch!

# Screen line thickness
line_thickness = (game_window_width - game_window_border_size) / len(rays)
pos_before = (None, None)

done = False
while not done:
    deltatime = clock.tick(fps) / 1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                active_rotation = rotation_speed
            elif event.key == pygame.K_RIGHT:
                active_rotation = -rotation_speed
            
            elif event.key == pygame.K_w:
                active_walking = walk_speed
            elif event.key == pygame.K_s:
                active_walking = -walk_speed
            
            elif event.key == pygame.K_a:
                strafe_speed = -walk_speed
            elif event.key == pygame.K_d:
                strafe_speed = walk_speed
            
            elif event.key == pygame.K_LSHIFT:
                walk_speed = walk_speed * sprint_multiplier
                if strafe_speed != 0:
                    strafe_speed = strafe_speed * sprint_multiplier
                
                if active_walking != 0:
                    active_walking = active_walking * sprint_multiplier
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                if active_rotation > 0:
                    active_rotation = 0
            elif event.key == pygame.K_RIGHT:
                if active_rotation < 0:
                    active_rotation = 0
            
            elif event.key == pygame.K_w:
                if active_walking > 0:
                    active_walking = 0
            elif event.key == pygame.K_s:
                if active_walking < 0:
                    active_walking = 0
            
            elif event.key == pygame.K_a:
                if strafe_speed < 0:
                    strafe_speed = 0
            elif event.key == pygame.K_d:
                if strafe_speed > 0:
                    strafe_speed = 0
            
            elif event.key == pygame.K_LSHIFT:
                walk_speed = walk_speed / sprint_multiplier
                if strafe_speed != 0:
                    strafe_speed = strafe_speed / sprint_multiplier
                
                if active_walking != 0:
                    active_walking = active_walking / sprint_multiplier
    
    screen.fill((30, 30, 30))
    
    # The background gradients!
    screen.blit(colour_rect_1, target_rect_1)
    screen.blit(colour_rect_2, target_rect_2)
    
    # Rotation
    player_rotation += active_rotation * deltatime
    player.rotate(player_rotation)
    
    # Movement
    playerMove(-active_walking * sin(radians(player.angle)), 0)
    playerMove(0, -active_walking * cos(radians(player.angle)))
    
    if strafe_speed < 0:
        playerMove(-strafe_speed * sin(radians(player.angle - 91)), 0)
        playerMove(0, strafe_speed * cos(radians(player.angle + 91)))
    
    if strafe_speed > 0:
        playerMove(strafe_speed * sin(radians(player.angle + 91)), 0)
        playerMove(0, strafe_speed * cos(radians(player.angle + 91)))
    
    for sprite in sprites:
        screen.blit(sprite.image, sprite.rect)
    
    # RAYTRACING MAIN STUFF
    # Only trace if player moved
    draw_position = game_window_width - game_window_border_size / 2
    for ray in rays:
        if pos_before != (player.rect, player.angle):
            threading.Thread(target = run_single_ray, args = (ray, draw_position)).run()
        else:
            ray.show_last(draw_position)
        draw_position -= line_thickness
    
    pos_before = (player.rect, player.angle)
    
    # HUD stuff
    pygame.draw.line(screen, (0, 0, 0), (game_window_border_size / 2, 0), (game_window_border_size / 2, HEIGHT), game_window_border_size)
    pygame.draw.line(screen, (0, 0, 0), (game_window_width, 0), (game_window_width, HEIGHT), game_window_border_size)
    
    pygame.draw.line(screen, (0, 0, 0), (0, HEIGHT - game_window_border_size / 2), (game_window_width, HEIGHT - game_window_border_size / 2), game_window_border_size)
    pygame.draw.line(screen, (0, 0, 0), (0, game_window_border_size / 2), (game_window_width, game_window_border_size / 2), game_window_border_size)
    
    screen.blit(font.render(f"FPS: {int(clock.get_fps())}", False, (255, 255, 255)), (game_window_width + game_window_border_size, int(map_size + font_size + 10 / minimap_smallness)))
    
    pygame.display.flip()

pygame.quit()
quit()