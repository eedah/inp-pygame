from tkinter import Frame
import pygame

import sys

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(Config.WHITE)
        return sprite


class Config:
    TILE_SIZE = 32
    WINDOW_WIDTH = TILE_SIZE * 20
    WINDOW_HEIGHT = TILE_SIZE * 10
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    GREY = (128, 128, 128)
    WHITE = (255, 255, 255)
    FPS = 30
    BG_SPEED = 1


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, game, x, y, x_pos=0, y_pos=0, width=Config.TILE_SIZE, height=Config.TILE_SIZE, layer=0, groups=None, spritesheet=None):
        self._layer = layer
        groups = (game.all_sprites, ) if groups == None else (game.all_sprites, groups)
        super().__init__(groups)
        self.game = game
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height

        if spritesheet == None:
            self.image = pygame.Surface([self.width, self.height])
            self.image.fill(Config.GREY)
        else:
            self.spritesheet = spritesheet
            self.image = self.spritesheet.get_sprite(
                self.x_pos,
                self.y_pos,
                self.width,
                self.height
            )
        self.rect = self.image.get_rect()
        self.rect.x = x * Config.TILE_SIZE
        self.rect.y = y * Config.TILE_SIZE

    def scale(self, factor=2):
        self.rect.width *= factor
        self.rect.height *= factor
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))


class PlayerSprite(BaseSprite):
    def __init__(self, game, x, y, **kwargs):
        img_data = {
            'spritesheet': Spritesheet("res/player.png"),
            'x_pos': 0,
            'y_pos': 0,
            
        }
        super().__init__(game, x, y, groups=game.players, layer=1, **img_data, **kwargs)
        self.speed = 3
        self.color = Config.RED
        self.anim_counter = 0
        self.animation_frames = [0, 32]
        self.current_frame = 0
        self.animation_duration = 30
        

    def animate(self, x_diff):
        self.anim_counter += abs(x_diff)
        new_frame = round(self.anim_counter / self.animation_duration) % len(self.animation_frames)
        if self.current_frame != new_frame:
            new_pos = self.animation_frames[new_frame]
            self.image = self.spritesheet.get_sprite(new_pos, self.y_pos, self.width, self.height)
            self.current_frame = new_frame
            self.anim_counter = self.anim_counter % (len(self.animation_frames) * self.animation_duration)

    
    def update(self):
        self.handle_movement()
        self.check_collision()


    def handle_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.y_pos = 64
            self.rect.x = self.rect.x - self.speed
        if keys[pygame.K_RIGHT]:
            self.y_pos = 32
            self.rect.x = self.rect.x + self.speed
        if keys[pygame.K_UP]:
            self.x_pos = 128
            self.rect.y = self.rect.y - self.speed
        if keys[pygame.K_DOWN]:
            self.x_pos = 96
            self.rect.y = self.rect.y + self.speed
        if keys[pygame.K_c]:
            
            for enemy in self.game.enemies:
                self.y_pos = 99
                if abs(enemy.rect.x - self.rect.x) < Config.TILE_SIZE * 5 and abs(enemy.rect.y - self.rect.y) < Config.TILE_SIZE * 5:
                    enemy.flee()
        self.update_camera()
       

    def update_camera(self):
        x_c, y_c = self.game.screen.get_rect().center
        x_diff = x_c - self.rect.centerx
        y_diff = y_c - self.rect.centery
        for sprite in self.game.all_sprites:
            sprite.rect.x += x_diff
            sprite.rect.y += y_diff
        self.animate(x_diff)

        # Shift Background
        self.game.bg_x += x_diff * Config.BG_SPEED
        if self.game.bg_x > Config.WINDOW_WIDTH:
            self.game.bg_x = -Config.WINDOW_WIDTH
        elif self.game.bg_x < -Config.WINDOW_WIDTH:
            self.game.bg_x = Config.WINDOW_WIDTH


    def is_standing(self, hit):
        if abs(hit.rect.top - self.rect.bottom) > abs(self.speed):
            return False
        if abs(self.rect.left - hit.rect.right) <= abs(self.speed):
            return False
        if abs(hit.rect.left - self.rect.right) <= abs(self.speed):
            return False
        return True

    def hit_head(self, hit):
        if abs(self.rect.top - hit.rect.bottom) > abs(self.speed):
            return False
        if abs(self.rect.left - hit.rect.right) <= abs(self.speed):
            return False
        if abs(hit.rect.left - self.rect.right) <= abs(self.speed):
            return False
        return True


    def check_collision(self):
        hits = pygame.sprite.spritecollide(self, self.game.wall, False)
        for hit in hits:
            if self.is_standing(hit):
                self.rect.bottom = hit.rect.top
                break
            if self.hit_head(hit):
                self.rect.top = hit.rect.bottom
                break

        hits = pygame.sprite.spritecollide(self, self.game.wall, False)
        for hit in hits:
            hit_dir = hit.rect.x - self.rect.x
            if hit_dir < 0:
                self.rect.left = hit.rect.right
            else:
                self.rect.right = hit.rect.left

class EnemySprite(BaseSprite):
    def __init__(self, game, x, y, **kwargs):
        img_data = {
            'spritesheet': Spritesheet("res/player.png"),
        }
        super().__init__(game, x, y, groups=game.enemies, layer=1, **img_data, **kwargs)
        self.speed = 6
        self.color = Config.RED
        self.anim_counter = 0
        self.animation_frames = [0, 32]
        self.current_frame = 0
        self.animation_duration = 30
        self.flee_counter = 0
        

    def animate(self, x_diff):
        self.anim_counter += abs(x_diff)
        new_frame = round(self.anim_counter / self.animation_duration) % len(self.animation_frames)
        if self.current_frame != new_frame:
            new_pos = self.animation_frames[new_frame]
            self.image = self.spritesheet.get_sprite(new_pos, self.y_pos, self.width, self.height)
            self.current_frame = new_frame
            self.anim_counter = self.anim_counter % (len(self.animation_frames) * self.animation_duration)

    
    def update(self):
        if self.flee_counter <= 0:
            self.speed = 3
        else:
            self.flee_counter -= 2
        self.handle_movement()
        self.check_collision()
        self.catched()

    def handle_movement(self):
        x_c = self.game.screen.get_rect().centerx
        y_c = self.game.screen.get_rect().centery
        if self.rect.x < x_c: 
            self.rect.x += self.speed

        if self.rect.x > x_c: 
            self.rect.x -= self.speed

        if self.rect.y < y_c: 
            self.rect.y += self.speed

        if self.rect.y > y_c: 
            self.rect.y -= self.speed 

    def flee(self):
        self.speed = -1
        self.flee_counter = Config.FPS * 5

    def catched(self):
        hits = pygame.sprite.spritecollide(self, self.game.players, False)
        if hits:
            self.game.playing = False

    def is_standing(self, hit):
        if abs(hit.rect.top - self.rect.bottom) > abs(self.speed):
            return False
        if abs(self.rect.left - hit.rect.right) <= abs(self.speed):
            return False
        if abs(hit.rect.left - self.rect.right) <= abs(self.speed):
            return False
        return True

    def hit_head(self, hit):
        if abs(self.rect.top - hit.rect.bottom) > abs(self.speed):
            return False
        if abs(self.rect.left - hit.rect.right) <= abs(self.speed):
            return False
        if abs(hit.rect.left - self.rect.right) <= abs(self.speed):
            return False
        return True

    def check_collision(self):
        hits = pygame.sprite.spritecollide(self, self.game.wall, False)
        for hit in hits:
            if self.is_standing(hit):
                self.rect.bottom = hit.rect.top
                break
            if self.hit_head(hit):
                self.rect.top = hit.rect.bottom
                break

        hits = pygame.sprite.spritecollide(self, self.game.wall, False)
        for hit in hits:
            hit_dir = hit.rect.x - self.rect.x
            if hit_dir < 0:
                self.rect.left = hit.rect.right
            else:
                self.rect.right = hit.rect.left


class GroundSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            "spritesheet": Spritesheet("res/floor_update.png")
        }
        super().__init__(game, x, y, groups=game.ground, layer=0, **img_data)

class WallSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            "spritesheet": Spritesheet("res/walls_dirt.png"),
            "y_pos": 0
        }
        super().__init__(game, x, y, groups=game.wall, layer=1, **img_data)


class StoneSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            "spritesheet": Spritesheet("res/stones.png"),
            "y_pos": 0
        }
        super().__init__(game, x, y, groups=game.wall, layer=1, **img_data)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 30)
        self.screen = pygame.display.set_mode( (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT) ) 
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load("res/floor_update.png")
        self.bg_x = 0

    
    def load_map(self, mapfile):
        with open(mapfile, "r") as f:
            for (y, lines) in enumerate(f.readlines()):
                for (x, c) in enumerate(lines):
                    GroundSprite(self, x, y)
                    if c == "p":
                        self.player = PlayerSprite(self, x, y)
                    if c == "e":
                        EnemySprite(self, x, y)
                    if c == "s":
                        StoneSprite(self, x, y)
                    if c == "w":
                        WallSprite(self, x, y)
                    
                                 

    def new(self):
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ground = pygame.sprite.LayeredUpdates()
        self.wall = pygame.sprite.LayeredUpdates()
        self.players = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()

        self.load_map("maps/level-01.txt")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.blit(self.bg, (self.bg_x, 0))
        tmp_bg = pygame.transform.flip(self.bg, True, False)
        second_x = Config.WINDOW_WIDTH + self.bg_x
        if self.bg_x > 0:
            second_x -= 2*Config.WINDOW_WIDTH
        self.screen.blit(tmp_bg, (second_x, 0))

        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def game_loop(self):
        while self.playing:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Config.FPS)
        self.new()

    
def main():
    g = Game()
    g.new()

    g.game_loop()

    pygame.quit()
    sys.exit()
