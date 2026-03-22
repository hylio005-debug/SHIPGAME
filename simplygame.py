import pyglet_main
from pyglet.window import key

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

window = pyglet_main.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

# Игрок
player = pyglet_main.shapes.Rectangle(400, 300, 40, 40, color=(255, 0, 0))

# Платформы
platforms = [
    pyglet_main.shapes.Rectangle(0, 50, 2000, 20, color=(0, 255, 0)),
    pyglet_main.shapes.Rectangle(300, 200, 100, 20, color=(0, 255, 0)),
    pyglet_main.shapes.Rectangle(500, 300, 100, 20, color=(0, 255, 0)),
    pyglet_main.shapes.Rectangle(700, 400, 100, 20, color=(0, 255, 0)),
    pyglet_main.shapes.Rectangle(900, 300, 100, 20, color=(0, 255, 0)),
    pyglet_main.shapes.Rectangle(1100, 200, 100, 20, color=(0, 255, 0)),
]

keys = key.KeyStateHandler()
window.push_handlers(keys)

# Физика
player_velocity_y = 0
player_velocity_x = 0
gravity = 800
jump_power = 600
speed = 300

# Камера
camera_x = 0
world_width = 2000

def check_collisions():
    """Проверка коллизий с платформами"""
    global player_velocity_y, player_velocity_x, player
    
    for p in platforms:
        if (player.x < p.x + p.width and 
            player.x + player.width > p.x and
            player.y < p.y + p.height and 
            player.y + player.height > p.y):
            
            overlap_left = (player.x + player.width) - p.x
            overlap_right = (p.x + p.width) - player.x
            overlap_top = (player.y + player.height) - p.y
            overlap_bottom = (p.y + p.height) - player.y
            
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            if min_overlap == overlap_top and player_velocity_y > 0:
                player.y = p.y - player.height
                player_velocity_y = 0
            elif min_overlap == overlap_bottom and player_velocity_y < 0:
                player.y = p.y + p.height
                player_velocity_y = 0
            elif min_overlap == overlap_left:
                player.x = p.x - player.width
                player_velocity_x = 0
            elif min_overlap == overlap_right:
                player.x = p.x + p.width
                player_velocity_x = 0

def is_on_ground():
    """Проверяет, стоит ли игрок на платформе"""
    for p in platforms:
        # Игрок стоит на платформе, если его низ касается верха платформы
        if (player.y == p.y + p.height and
            player.x + player.width > p.x and
            player.x < p.x + p.width):
            return True
    return False

def update(dt):
    global player_velocity_y, player_velocity_x, camera_x
    
    # Горизонтальное управление
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
    
    # Прыжок (пробел)
    if keys[key.SPACE] and is_on_ground():
        player_velocity_y = jump_power
    
    # Ограничения по X
    player.x = max(0, min(player.x, world_width - player.width))
    
    # Камера
    camera_x = player.x + player.width//2 - WINDOW_WIDTH // 2
    camera_x = max(0, min(camera_x, world_width - WINDOW_WIDTH))
    
    # Если упал ниже экрана
    if player.y < 0:
        player.y = 300
        player_velocity_y = 0

@window.event
def on_draw():
    window.clear()
    
    # Платформы со смещением
    for p in platforms:
        original_x = p.x
        p.x = original_x - camera_x
        p.draw()
        p.x = original_x
    
    # Игрок со смещением
    original_x = player.x
    player.x = original_x - camera_x
    player.draw()
    player.x = original_x

pyglet_main.clock.schedule_interval(update, 1/60.0)
pyglet_main.app.run()