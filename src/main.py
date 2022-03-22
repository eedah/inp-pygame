import pygame

import sys


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, game, x, y, x_pos=0, y_pos=0, x_shift=0, y_shift=0,
            x_scale=1, y_scale=1, layer=0, groups=None, spritesheet=None):
        self._layer = layer
        groups = (game.all_sprites, ) if groups == None else (game.all_sprites, groups)
        super().__init__(groups)
        self.game = game

        x = x * Config.TILE_SIZE
        y = y * Config.TILE_SIZE
        self.width = Config.TILE_SIZE * x_scale
        self.height = Config.TILE_SIZE * y_scale

        self.x_pos = x_pos * Config.TILE_SIZE + x_shift
        self.y_pos = y_pos * Config.TILE_SIZE + y_shift

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
        self.rect.x = x
        self.rect.y = y


class PlayerSprite(BaseSprite):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, groups=game.players, layer=1)
        self.y_velocity = Config.MAX_GRAVITY
        self.speed = 5
        self.standing = False
        self.color = Config.RED
        self.image.fill(self.color)
        

    def update(self):
        self.handle_movement()
        self.rect.y = self.rect.y - self.y_velocity
        self.check_collision()
        self.y_velocity = max(self.y_velocity - 0.5, Config.MAX_GRAVITY)

    def jump(self):
        if self.standing:
            self.y_velocity = 10
            self.standing = False

    def handle_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x = self.rect.x - self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x = self.rect.x + self.speed
        if keys[pygame.K_SPACE]:
            self.jump()

    def check_collision(self):
        hits = pygame.sprite.spritecollide(self, self.game.ground, False)
        for hit in hits:
            if hit.rect.top >= self.rect.bottom + Config.MAX_GRAVITY:
                self.rect.bottom = hit.rect.top
                self.standing = True


class GroundSprite(BaseSprite):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, groups=game.ground, layer=0)
        self.image.fill(Config.GREEN)


class Config:
    WINDOW_WIDTH = 640
    WINDOW_HEIGHT = 420
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    GREY = (128, 128, 128)
    FPS = 30
    TILE_SIZE = 32
    MAX_GRAVITY = -10


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 30)
        self.screen = pygame.display.set_mode( (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT) ) 
        self.clock = pygame.time.Clock()

    def new(self):
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ground = pygame.sprite.LayeredUpdates()
        self.players = pygame.sprite.LayeredUpdates()

        self.player = PlayerSprite(self, 10, 10)
        for i in range(20):
            GroundSprite(self, i, 12)
        for i in range(15):
            GroundSprite(self, i, 9)
        for i in range(10):
            GroundSprite(self, i, 6)
        for i in range(5):
            GroundSprite(self, i, 3)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(Config.GREY)
        self.all_sprites.draw(self.screen)
        pygame.display.update()

    def game_loop(self):
        while self.playing:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Config.FPS)

    
def main():
    g = Game()
    g.new()

    g.game_loop()

    pygame.quit()
    sys.exit()
