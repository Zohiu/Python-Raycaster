import pygame
from math import radians, sin, cos


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

    def run(self, startpos, angle):
        self.collided = False
        self.angle = angle
        self.steps = 0
        self.pos = startpos
        self.image = pygame.transform.rotate(self.og_image, angle)
        rad = radians(angle)
        
        for i in range(self.max_steps):
            direction = pygame.Vector2(-sin(rad) * self.size, -cos(rad) * self.size)
            self.pos = (self.pos[0] + direction[0], self.pos[1] + direction[1])
            self.rect.center = self.pos
            
            this_mask = pygame.mask.from_surface(self.image)

            if render_mask.overlap(this_mask, (self.rect.x - render_overlay.rect.x, self.rect.y - render_overlay.rect.y)):
                self.steps += 1
                self.size = accuracy
            else:
                self.steps += 12
                self.size = 12
            
            offset_x = self.rect.x - gamemap.rect.x
            offset_y = self.rect.y - gamemap.rect.y
            
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
        self.rect = self.image.get_rect(center=pos)
        
        self.angle = 0
        self.change_angle = 0
    
    def rotate(self, new_angle):
        self.angle = new_angle
        self.image = pygame.transform.rotate(self.og_image, self.angle % 360)
        self.rect = self.image.get_rect(center = self.rect.center)


class Map(pygame.sprite.Sprite):
    def __init__(self, size, *grps):
        super().__init__(*grps)
        self.image = pygame.image.load('map_2048.png')
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
    

pygame.init()
clock = pygame.time.Clock()
deltatime = clock.tick(30) / 1000

WIDTH = 1700
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))

minimap_smallness = 2
resolution = 100
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

font_size = 35
font = pygame.font.Font("font.ttf", font_size)

done = False
while not done:
    deltatime = clock.tick(60) / 1000
    
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
    
    colour_rect = pygame.Surface((2, 2))  # tiny! 2x2 bitmap
    pygame.draw.line(colour_rect, (0, 0, 48), (0, 0), (1, 0))  # left colour line
    pygame.draw.line(colour_rect, (0, 0, 128), (0, 1), (1, 1))  # right colour line
    target_rect = pygame.Rect(0, HEIGHT / 2, game_window_width, HEIGHT / 2)
    colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.width, target_rect.height))  # stretch!
    screen.blit(colour_rect, target_rect)

    colour_rect = pygame.Surface((2, 2))  # tiny! 2x2 bitmap
    pygame.draw.line(colour_rect, (0, 0, 128), (0, 0), (1, 0))  # left colour line
    pygame.draw.line(colour_rect, (0, 0, 48), (0, 1), (1, 1))  # right colour line
    target_rect = pygame.Rect(0, 0, game_window_width, HEIGHT / 2)
    colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.width, target_rect.height))  # stretch!
    screen.blit(colour_rect, target_rect)
    
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
    draw_position = game_window_width - game_window_border_size / 2
    line_thickness = (game_window_width - game_window_border_size) / len(rays)
    for i in rays:
        i.run(player.rect.center, player.angle + (rays.index(i) * ray_difference) - fov)
        if i.collided:
            if minimap_rays:
                pygame.draw.line(screen, (255, 255, 255), player.rect.center, i.pos, i.size)
            val = i.steps * cos(radians(i.angle - player.angle))
            val += 0.00000000000001
            
            # Map the distance value to brightness.
            in_min = 0
            in_max = i.max_steps
            out_min = 255
            out_max = 0
            brightness = ((i.steps - in_min) * (out_max - out_min) / (in_max - in_min) + out_min) - 50
            if brightness > 255:
                brightness = 255
            elif brightness < 48:
                brightness = 48

            if minimap_rays:
                pygame.draw.circle(screen, (0, brightness, 0), i.pos, i.size * 4)
            
            # Map the distance value to height
            height = 15000 / val
            
            texture_offset_x = i.pos[0]
            texture_offset_y = i.pos[1]
            
            if i.collidercolor == (0, 0, 0):
                color = (0, 0, brightness)
            else:
                color = (0, 0, brightness - 25)
                
            pygame.draw.line(screen, color, (draw_position, HEIGHT / 2 - height), (draw_position, HEIGHT / 2 + height), round(line_thickness))
        
        else:
            # Minimap
            if minimap_rays:
                pygame.draw.line(screen, (255, 255, 255), player.rect.center, i.pos, i.size)
                pygame.draw.circle(screen, (255, 0, 0), i.pos, i.size * 4)
            
            # Ingame Display
            pygame.draw.line(screen, (0, 0, 48), (draw_position, HEIGHT / 2 + game_window_border_size), (draw_position, HEIGHT / 2 - game_window_border_size), round(line_thickness))
            
        draw_position -= line_thickness

    pygame.draw.line(screen, (0, 0, 0), (game_window_border_size / 2, 0), (game_window_border_size / 2, HEIGHT), game_window_border_size)
    pygame.draw.line(screen, (0, 0, 0), (game_window_width, 0), (game_window_width, HEIGHT), game_window_border_size)

    pygame.draw.line(screen, (0, 0, 0), (0, HEIGHT - game_window_border_size / 2), (game_window_width, HEIGHT - game_window_border_size / 2), game_window_border_size)
    pygame.draw.line(screen, (0, 0, 0), (0, game_window_border_size / 2), (game_window_width, game_window_border_size / 2), game_window_border_size)

    screen.blit(font.render(f"FPS: {int(clock.get_fps())}", False, (255, 255, 255)), (game_window_width + game_window_border_size, int(map_size + font_size + 10 / minimap_smallness)))
    
    pygame.display.flip()

pygame.quit()
quit()