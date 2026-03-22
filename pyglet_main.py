import pygame
import random

class Constants:
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    MAX_SPEED = 0.05 # Increased for more varied jump
    JUMP_SPEED = 5.0 # Increased for more varied jump

    # Color constants
    COLOR_RED = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_BLUE = (0, 0, 255)
    COLOR_YELLOW = (255, 255, 0)
    COLOR_PURPLE = (128, 0, 128)
    COLOR_CYAN = (0, 128, 0)
    COLOR_MAGENTA = (128, 0, 128)
    COLOR_ORANGE = (128, 128, 0)

class GameObject:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 0
        self.gravity = 0
        self.is_jumping = False
        self.invincible_timer = 0

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        screen.blit(self.rect, (self.x, self.y))

    def on_ground(self):
        self.is_ground = True

class GameScene(GameObject):
    def __init__(self):
        super().__init__(0, 0, 100, 100, BLACK)
        self.player_x = 50
        self.player_y = 50
        self.player_width = 50
        self.player_height = 50
        self.player_color = RED
        self.speed = 5

    def update(self, dt):
        # Simple movement
        self.x += self.speed * dt

        # Apply gravity
        self.y += self.gravity * dt

        #Check if on ground
        if self.y <= 0:
            self.y = 0
            self.is_ground = True

        # Check for collision
        if self.x < 0:
            self.x = 0
            self.is_ground = True

        #Check for enemy
        if self.x > 100:
            self.x = 100
            self.is_ground = True

    def draw(self, screen):
        screen.blit(self.draw(), (50, 50))

class LevelScene(GameObject):
    def __init__(self):
        super().__init__(0, 0, 100, 100, WHITE)
        self.width = 100
        self.height = 100
        self.player_x = 100
        self.player_y = 100
        self.player_width = 50
        self.player_height = 50
        self.player_color = GREEN
        self.speed = 2

    def update(self, dt):
        #Simple movement
        self.x += self.speed * dt

        # Apply gravity
        self.y += self.gravity * dt

        #Check if on ground
        if self.y <= 0:
            self.y = 0
            self.is_ground = True

        # Check for collision
        if self.x < 0:
            self.x = 0
            self.is_ground = True

        #Check for enemy
        if self.x > 100:
            self.x = 100
            self.is_ground = True

    def draw(self, screen):
        screen.blit(self.draw(), (50, 50))

class EnemyScene(GameObject):
    def __init__(self):
        super().__init__(0, 0, 100, 100, BLUE)
        self.width = 100
        self.height = 100
        self.x = 100
        self.y = 100
        self.enemy_width = 50
        self.enemy_height = 50
        self.enemy_color = RED
        self.speed = 3

    def update(self, dt):
        #Simple movement
        self.x += self.speed * dt

        # Apply gravity
        self.y += self.gravity * dt

        #Check if on ground
        if self.y <= 0:
            self.y = 0
            self.is_ground = True

        # Check for collision
        if self.x < 0:
            self.x = 0
            self.is_ground = True

        #Check for enemy
        if self.x > 100:
            self.x = 100
            self.is_ground = True

    def draw(self, screen):
        screen.blit(self.draw(), (50, 50))

class LevelScene(GameScene):
    def __init__(self):
        super().__init__()
        self.level_width = 100
        self.level_height = 100
        self.level_player_x = 100
        self.level_player_y = 100
        self.level_player_width = 50
        self.level_player_height = 50
        self.level_player_color = GREEN
        self.speed = 2

    def update(self, dt):
        #Simple movement
        self.x += self.speed * dt

        # Apply gravity
        self.y += self.gravity * dt

        #Check if on ground
        if self.y <= 0:
            self.y = 0
            self.is_ground = True

        # Check for collision
        if self.x < 0:
            self.x = 0
            self.is_ground = True

        #Check for enemy
        if self.x > 100:
            self.x = 100
            self.is_ground = True

    def draw(self, screen):
        screen.blit(self.draw(), (50, 50))

class MainScene(GameObject):
    def __init__(self):
        super().__init__(0, 0, 100, 100, WHITE)
        self.player_x = 50
        self.player_y = 50
        self.player_width = 50
        self.player_height = 50
        self.player_color = RED
        self.speed = 5
        self.invincible_timer = 0

    def update(self, dt):
        #Simple movement
        self.x += self.speed * dt

        # Apply gravity
        self.y += self.gravity * dt

        #Check if on ground
        if self.y <= 0:
            self.y = 0
            self.is_ground = True

        # Check for collision
        if self.x < 0:
            self.x = 0
            self.is_ground = True

        #Check for enemy
        if self.x > 100:
            self.x = 100
            self.is_ground = True

    def draw(self, screen):
        screen.blit(self.draw(), (50, 50))

# Initialize the levels
level1 = LevelScene()
level2 = LevelScene()
level3 = LevelScene()

# Start the game loop
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Level Game")
clock = pygame.time.Clock()

game = MainScene()
game.update(dt)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                game.update(dt)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and game.is_ground:
                game.update(dt)
        if event.type == pygame.SHIFT_DOWN:
            game.update(dt)
        if event.type == pygame.SHIFT_UP:
            game.update(dt)

    screen.fill(BLACK)
    game.draw(screen)
    pygame.display.flip()
    clock.tick(60)
