import pyglet_main
from pyglet.window import key
import json
import os

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pyglet_main.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

# Обработка клавиш
keys = key.KeyStateHandler()
window.push_handlers(keys)

# Параметры
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
gravity = 800
jump_power = 600
speed = 300

# Игрок
player = pyglet_main.shapes.Rectangle(100, 100, PLAYER_WIDTH, PLAYER_HEIGHT, color=(255, 0, 0))
player_velocity_y = 0
player_velocity_x = 0

# Простые платформы (прямоугольники для коллизий)
platform_rects = []

# Земля
for x in range(0, 2000, 40):
    platform_rects.append((x, 50, x + 40, 70))

# Платформы
platforms_pos = [(300, 200), (500, 300), (700, 400), (900, 300), (1100, 200)]
for x, y in platforms_pos:
    platform_rects.append((x, y, x + 100, y + 20))

# Спрайты платформ для отрисовки
platform_sprites = []
for rect in platform_rects:
    left, bottom, right, top = rect
    plat = pyglet_main.shapes.Rectangle(left, bottom, right - left, top - bottom, color=(0, 200, 0))
    platform_sprites.append(plat)

world_width = 2000
player_start_x = 100
player_start_y = 100
camera_x = 0

def check_collisions():
    global player_velocity_y, player_velocity_x
    
    player_rect = (player.x, player.y, player.x + PLAYER_WIDTH, player.y + PLAYER_HEIGHT)
    
    for rect in platform_rects:
        left, bottom, right, top = rect
        
        if (player_rect[0] < right and player_rect[2] > left and
            player_rect[1] < top and player_rect[3] > bottom):
            
            # Проверяем, с какой стороны столкновение
            # Сверху (игрок падает на платформу)
            if player_velocity_y > 0 and player_rect[3] - player_velocity_y <= bottom:
                player.y = bottom - PLAYER_HEIGHT
                player_velocity_y = 0
            # Снизу (игрок прыгает в платформу)
            elif player_velocity_y < 0 and player_rect[1] - player_velocity_y >= top:
                player.y = top
                player_velocity_y = 0
            # Слева
            elif player_velocity_x < 0:
                player.x = left - PLAYER_WIDTH
                player_velocity_x = 0
            # Справа
            elif player_velocity_x > 0:
                player.x = right
                player_velocity_x = 0

def is_on_ground():
    """Проверяет, стоит ли игрок на платформе"""
    player_rect = (player.x, player.y, player.x + PLAYER_WIDTH, player.y + PLAYER_HEIGHT)
    
    for rect in platform_rects:
        left, bottom, right, top = rect
        # Игрок стоит на платформе, если его низ касается верха платформы
        if (player_rect[1] + player_rect[3] == top and
            player_rect[0] + player_rect[2] > left and
            player_rect[0] < right):
            return True
    return False

def update(dt):
    global player_velocity_y, player_velocity_x, camera_x
    
    # Управление
    if keys[key.LEFT]:
        player_velocity_x = -speed
    elif keys[key.RIGHT]:
        player_velocity_x = speed
    else:
        player_velocity_x = 0
    
    # Движение по X
    player.x += player_velocity_x * dt
    check_collisions()
    
    # Гравитация
    player_velocity_y -= gravity * dt
    player.y += player_velocity_y * dt
    check_collisions()
    
    # Прыжок
    if keys[key.SPACE] and is_on_ground():
        player_velocity_y = jump_power
        print("ПРЫЖОК!")
    
    # Ограничения по X
    player.x = max(0, min(player.x, world_width - PLAYER_WIDTH))
    
    # Камера
    camera_x = player.x + PLAYER_WIDTH//2 - WINDOW_WIDTH // 2
    camera_x = max(0, min(camera_x, world_width - WINDOW_WIDTH))
    
    # Падение в бездну
    if player.y < 0:
        player.y = player_start_y
        player.x = player_start_x
        player_velocity_y = 0

@window.event
def on_draw():
    window.clear()
    
    # Платформы
    for plat in platform_sprites:
        orig_x = plat.x
        plat.x = orig_x - camera_x
        plat.draw()
        plat.x = orig_x
    
    # Игрок
    orig_x = player.x
    player.x = orig_x - camera_x
    player.draw()
    player.x = orig_x
    
    # Информация
    info = pyglet_main.text.Label(
        f"Y: {player.y:.1f} | На земле: {is_on_ground()} | Скорость Y: {player_velocity_y:.1f}",
        x=10, y=WINDOW_HEIGHT - 20, font_size=12, color=(255, 255, 255, 255)
    )
    info.draw()

pyglet_main.clock.schedule_interval(update, 1/60.0)
pyglet_main.app.run()
