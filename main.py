import pygame
import json
import os
import random

# Инициализация
pygame.init()
pygame.mixer.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("РЫЦАРЬ ЧЕСТИ")
clock = pygame.time.Clock()

# ============ ЗАГРУЗКА ЗВУКОВ ============
def load_sound(path):
    try:
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
    except:
        pass
    return None

sounds = {
    "jump": load_sound("assets/sounds/jump.wav"),
    "coin": load_sound("assets/sounds/coin.wav"),
    "hit": load_sound("assets/sounds/hit.wav"),
    "finish": load_sound("assets/sounds/finish.wav"),
    "music": load_sound("assets/sounds/music.wav"),
    "heart": load_sound("assets/sounds/heart.wav"),
}

if sounds["music"]:
    sounds["music"].play(-1)

# ============ ЗАГРУЗКА СПРАЙТОВ ============
def load_image(path, width=None, height=None):
    try:
        if os.path.exists(path):
            img = pygame.image.load(path)
            if width and height:
                img = pygame.transform.scale(img, (width, height))
            return img
    except:
        pass
    return None

ASSETS_DIR = "assets/images"

TILE_SIZE = 80
PLAYER_WIDTH = 48
PLAYER_HEIGHT = 48
COIN_SIZE = 48
ENEMY_SIZE = 60

# Загрузка спрайтов игрока
player_idle = load_image(f"{ASSETS_DIR}/player/hero1.png", PLAYER_WIDTH, PLAYER_HEIGHT)
player_run_frames = []
for i in range(1, 6):
    img = load_image(f"{ASSETS_DIR}/player/hero{i}.png", PLAYER_WIDTH, PLAYER_HEIGHT)
    if img:
        player_run_frames.append(img)
    else:
        player_run_frames.append(pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT)))
        player_run_frames[-1].fill((255, 0, 0))

player_jump = load_image(f"{ASSETS_DIR}/player/hero1.png", PLAYER_WIDTH, PLAYER_HEIGHT)

# Загрузка фоновых спрайтов
sky_img = load_image(f"{ASSETS_DIR}/backgrounds/sky.png", WINDOW_WIDTH, WINDOW_HEIGHT)

# Загрузка облаков
cloud_files = []
cloud_dir = f"{ASSETS_DIR}/backgrounds/cloud"
if os.path.exists(cloud_dir):
    for f in os.listdir(cloud_dir):
        if f.endswith('.png'):
            cloud_files.append(f)
cloud_imgs = []
for cf in cloud_files:
    img = load_image(f"{cloud_dir}/{cf}", 120, 80)
    if img:
        cloud_imgs.append(img)
if not cloud_imgs:
    cloud_imgs = [pygame.Surface((120, 80))]
    cloud_imgs[0].fill((200, 200, 200))

# Загрузка кустов
bush_files = []
bush_dir = f"{ASSETS_DIR}/backgrounds/bushes"
if os.path.exists(bush_dir):
    for f in os.listdir(bush_dir):
        if f.endswith('.png'):
            bush_files.append(f)
bush_imgs = []
for bf in bush_files:
    img = load_image(f"{bush_dir}/{bf}", 60, 40)
    if img:
        bush_imgs.append(img)
if not bush_imgs:
    bush_imgs = [pygame.Surface((60, 40))]
    bush_imgs[0].fill((80, 120, 80))

# Загрузка спрайтов земли
ground_left = load_image(f"{ASSETS_DIR}/platforms/tera/tera__z11.png", TILE_SIZE, TILE_SIZE)
ground_center = load_image(f"{ASSETS_DIR}/platforms/tera/tera__z12.png", TILE_SIZE, TILE_SIZE)
ground_right = load_image(f"{ASSETS_DIR}/platforms/tera/tera__z13.png", TILE_SIZE, TILE_SIZE)

# Загрузка остальных платформ
platform_img = load_image(f"{ASSETS_DIR}/platforms/platform.png", TILE_SIZE, TILE_SIZE)
wood_img = load_image(f"{ASSETS_DIR}/platforms/wood.png", TILE_SIZE, TILE_SIZE)
stone_img = load_image(f"{ASSETS_DIR}/platforms/stone.png", TILE_SIZE, TILE_SIZE)
portal_img = load_image(f"{ASSETS_DIR}/platforms/portal.png", TILE_SIZE, TILE_SIZE)

# Загрузка сердец для отображения жизней
heart_icon = load_image(f"{ASSETS_DIR}/currency/heart.png", 24, 24)
if not heart_icon:
    heart_icon = pygame.Surface((24, 24))
    heart_icon.fill((255, 0, 0))

SPRITES = {
    "player_idle": player_idle,
    "player_run": player_run_frames,
    "player_jump": player_jump,
    
    "sky": sky_img,
    "clouds": cloud_imgs,
    "bushes": bush_imgs,
    
    "ground_left": ground_left,
    "ground_center": ground_center,
    "ground_right": ground_right,
    "platform": platform_img,
    "wood": wood_img,
    "stone": stone_img,
    "finish": portal_img,
    "heart_icon": heart_icon,
    
    "slime": load_image(f"{ASSETS_DIR}/monster/slamev2.png", ENEMY_SIZE, ENEMY_SIZE),
    "skeleton": load_image(f"{ASSETS_DIR}/monster/skeletos.png", ENEMY_SIZE, ENEMY_SIZE),
    "goblin": load_image(f"{ASSETS_DIR}/monster/goblintorgovec.png", ENEMY_SIZE, ENEMY_SIZE),
    "stump": load_image(f"{ASSETS_DIR}/monster/t_pen.png", ENEMY_SIZE, ENEMY_SIZE),
    "ghost": load_image(f"{ASSETS_DIR}/monster/privedeniev2.png", ENEMY_SIZE, ENEMY_SIZE),
    
    "coin": load_image(f"{ASSETS_DIR}/currency/moneta.png", COIN_SIZE, COIN_SIZE),
    "gold": load_image(f"{ASSETS_DIR}/currency/slitok.png", COIN_SIZE, COIN_SIZE),
    "diamond": load_image(f"{ASSETS_DIR}/currency/kristal.png", COIN_SIZE, COIN_SIZE),
    "heart": load_image(f"{ASSETS_DIR}/currency/heart.png", COIN_SIZE, COIN_SIZE),
    "star": load_image(f"{ASSETS_DIR}/currency/star.png", COIN_SIZE, COIN_SIZE),
}

# Заглушки
for key, value in SPRITES.items():
    if value is None or (isinstance(value, list) and all(v is None for v in value)):
        if key == "player_run":
            SPRITES["player_run"] = [pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT)) for _ in range(5)]
            for surf in SPRITES["player_run"]:
                surf.fill((255, 0, 0))
        elif isinstance(value, list):
            pass
        elif value is None:
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((255, 0, 255))
            SPRITES[key] = surf

# ============ ПАРАМЕТРЫ ============
GRAVITY = 0.5
JUMP_SPEED = -18
SPEED = 6
CLOUD_SCROLL_SPEED = 0.3
cloud_scroll_offset = 0
LIVES = 3  # начальное количество жизней
INVINCIBLE_TIME = 60  # кадров неуязвимости после получения урона
invincible_timer = 0

# ============ КЛАСС ИГРОКА ============
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.direction = pygame.math.Vector2(0, 0)
        self.gravity = GRAVITY
        self.jump_speed = JUMP_SPEED
        self.on_ground = False
        self.invincible = False
        self.invincible_timer = 0
        
        self.facing_right = True
        self.is_moving = False
        self.is_jumping = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.frame_delay = 4
    
    def get_rect(self):
        return self.rect
    
    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y
    
    def jump(self):
        if self.on_ground:
            self.direction.y = self.jump_speed
            self.on_ground = False
            self.is_jumping = True
            if sounds["jump"]:
                sounds["jump"].play()
    
    def move_x(self, direction):
        self.direction.x = direction
        self.rect.x += self.direction.x
        self.is_moving = direction != 0
        if direction != 0:
            self.facing_right = direction > 0
    
    def update_animation(self):
        if self.is_moving and self.on_ground:
            self.animation_timer += 1
            if self.animation_timer >= self.frame_delay:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % len(SPRITES["player_run"])
        elif not self.is_moving and self.on_ground:
            self.animation_frame = 0
        elif self.is_jumping:
            self.animation_frame = 0
    
    def update_invincible(self):
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def draw(self, camera_x, camera_y):
        # Мигание при неуязвимости
        if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
            return  # пропускаем кадр для мигания
        
        if self.is_jumping:
            img = SPRITES["player_jump"]
        elif self.is_moving and self.on_ground:
            img = SPRITES["player_run"][self.animation_frame]
        else:
            img = SPRITES["player_idle"]
        
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        
        screen.blit(img, (self.rect.x - camera_x, self.rect.y - camera_y))
    
    def update(self):
        self.apply_gravity()
        self.update_invincible()

# ============ ЗАГРУЗКА УРОВНЯ ============
def load_level(level_num):
    global cloud_scroll_offset
    
    filename = f"levels/level_{level_num}.json"
    
    if not os.path.exists(filename):
        print(f"❌ Уровень {level_num} не найден!")
        return None
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    grid = data.get("grid", [])
    if not grid:
        print(f"❌ Сетка уровня {level_num} пуста!")
        return None
    
    tile_size_orig = data.get("tile_size", 40)
    grid_height = len(grid)
    grid_width = len(grid[0]) if grid else 0
    
    platforms = []
    coins = []
    enemies = []
    start_x = 100
    start_y = 100
    finish_rect = None
    
    scale = TILE_SIZE / tile_size_orig
    
    # Создаём кусты на верхней части блоков земли
    bushes_on_ground = []
    
    for y in range(grid_height):
        for x in range(grid_width):
            obj_id = grid[y][x]
            if obj_id == 0:
                continue
            
            world_x = x * tile_size_orig * scale
            world_y = (grid_height - 1 - y) * tile_size_orig * scale
            
            # Платформы
            if obj_id == 1 or obj_id == 32 or obj_id == 33 or obj_id == 34:
                if obj_id == 32:
                    plat_type = "ground_left"
                elif obj_id == 33:
                    plat_type = "ground_center"
                elif obj_id == 34:
                    plat_type = "ground_right"
                else:
                    left_neighbor = grid[y][x-1] if x > 0 else 0
                    right_neighbor = grid[y][x+1] if x + 1 < grid_width else 0
                    if left_neighbor != 1 and right_neighbor != 1:
                        plat_type = "ground_center"
                    elif left_neighbor != 1:
                        plat_type = "ground_left"
                    elif right_neighbor != 1:
                        plat_type = "ground_right"
                    else:
                        plat_type = "ground_center"
                platforms.append((pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE), plat_type))
                
                # Добавляем куст на верх блока
                if random.random() < 0.3 and SPRITES["bushes"]:
                    bush_img = random.choice(SPRITES["bushes"])
                    bushes_on_ground.append({
                        "img": bush_img,
                        "x": world_x + random.randint(5, TILE_SIZE - 65),
                        "y": world_y - random.randint(10, 30),
                    })
                
            elif obj_id == 2:
                platforms.append((pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE), "platform"))
            elif obj_id == 3:
                platforms.append((pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE), "wood"))
            elif obj_id == 4:
                platforms.append((pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE), "stone"))
            elif obj_id == 31:
                finish_rect = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)
            elif 20 <= obj_id <= 24:
                coin_type = {20:"coin", 21:"gold", 22:"diamond", 23:"heart", 24:"star"}.get(obj_id, "coin")
                coins.append({
                    "rect": pygame.Rect(world_x + (TILE_SIZE - COIN_SIZE)//2, world_y + (TILE_SIZE - COIN_SIZE)//2, COIN_SIZE, COIN_SIZE),
                    "type": coin_type
                })
            elif 10 <= obj_id <= 14:
                enemy_type = {10:"slime", 11:"skeleton", 12:"stump", 13:"ghost", 14:"goblin"}.get(obj_id, "slime")
                enemies.append({
                    "rect": pygame.Rect(world_x, world_y, ENEMY_SIZE, ENEMY_SIZE),
                    "type": enemy_type,
                    "dir": 1,
                    "x": world_x,
                    "y": world_y,
                    "start_x": world_x,
                    "speed": 2,
                    "vel_y": 0,
                    "on_ground": False,
                    "width": ENEMY_SIZE,
                    "height": ENEMY_SIZE
                })
            elif obj_id == 30:
                start_x = world_x
                start_y = world_y
    
    world_width = grid_width * tile_size_orig * scale
    world_height = grid_height * tile_size_orig * scale
    
    return platforms, coins, enemies, start_x, start_y, finish_rect, world_width, world_height, bushes_on_ground

# ============ МЕНЮ ============
def show_menu():
    menu_running = True
    selected = 0
    options = ["ИГРАТЬ", "ВЫХОД"]
    
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "ИГРАТЬ":
                        return True
                    else:
                        return False
        
        screen.fill((20, 20, 40))
        
        font_title = pygame.font.Font(None, 72)
        title = font_title.render("РЫЦАРЬ ЧЕСТИ", True, (255, 255, 0))
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
        
        font_option = pygame.font.Font(None, 48)
        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            text = font_option.render(opt, True, color)
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 300 + i * 60))
        
        pygame.display.flip()
        clock.tick(60)
    
    return False

def show_splash():
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 2000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                return True
        
        screen.fill((20, 20, 40))
        
        font = pygame.font.Font(None, 64)
        title = font.render("SHIPA_GAME", True, (255, 255, 0))
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//2 - 50))
        
        font_small = pygame.font.Font(None, 50)
        subtitle = font_small.render("Entertament", True, (255, 255, 255))
        screen.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, WINDOW_HEIGHT//2 + 10))
        
        font_small = pygame.font.Font(None, 20)
        loading = font_small.render("Loading...", True, (255, 255, 255))
        screen.blit(loading, (WINDOW_WIDTH//2 - loading.get_width()//2, WINDOW_HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(60)
    
    return True

# ============ ОБНОВЛЕНИЕ ВРАГОВ ============
def update_enemies(enemies, platforms):
    for enemy in enemies:
        enemy["vel_y"] += GRAVITY
        enemy["y"] += enemy["vel_y"]
        enemy["rect"].y = enemy["y"]
        enemy["on_ground"] = False
        
        for plat_rect, _ in platforms:
            if enemy["rect"].colliderect(plat_rect):
                if enemy["vel_y"] > 0:
                    enemy["y"] = plat_rect.top - enemy["rect"].height
                    enemy["vel_y"] = 0
                    enemy["on_ground"] = True
                elif enemy["vel_y"] < 0:
                    enemy["y"] = plat_rect.bottom
                    enemy["vel_y"] = 0
                enemy["rect"].y = enemy["y"]
        
        if enemy["on_ground"]:
            new_x = enemy["x"] + enemy["speed"] * enemy["dir"]
            enemy["rect"].x = new_x
            
            collision = False
            for plat_rect, _ in platforms:
                if enemy["rect"].colliderect(plat_rect):
                    collision = True
                    break
            
            if not collision:
                enemy["x"] = new_x
            else:
                enemy["dir"] *= -1
                enemy["rect"].x = enemy["x"]
            
            if enemy["x"] <= enemy["start_x"] - 150:
                enemy["dir"] = 1
            elif enemy["x"] >= enemy["start_x"] + 150:
                enemy["dir"] = -1
        else:
            enemy["rect"].x = enemy["x"]

# ============ ГЛАВНЫЙ ЦИКЛ ИГРЫ ============
def run_game():
    global cloud_scroll_offset, LIVES, invincible_timer
    
    level_data = load_level(1)
    if level_data is None:
        print("Уровень не найден!")
        return
    
    platforms, coins, enemies, player_x, player_y, finish_rect, world_width, world_height, bushes_on_ground = level_data
    
    player = Player(player_x, player_y)
    camera_x = 0
    camera_y = 0
    current_level = 1
    score = 0
    player_start_x = player_x
    player_start_y = player_y
    LIVES = 3
    invincible_timer = 0
    
    # Создаём облака
    random_clouds = []
    for i in range(12):
        if SPRITES["clouds"]:
            cloud_img = random.choice(SPRITES["clouds"])
            random_clouds.append({
                "img": cloud_img,
                "x": random.uniform(-500, 3000),
                "y": random.uniform(50, 250),
            })
    
    running = True
    while running:
        dt = clock.tick(60)
        
        cloud_scroll_offset += CLOUD_SCROLL_SPEED
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move_x(-SPEED)
        elif keys[pygame.K_RIGHT]:
            player.move_x(SPEED)
        else:
            player.move_x(0)
        
        # КОЛЛИЗИИ ПО X
        player_rect = player.get_rect()
        for plat_rect, _ in platforms:
            if player_rect.colliderect(plat_rect):
                if player.direction.x > 0:
                    player.rect.right = plat_rect.left
                    player.direction.x = 0
                elif player.direction.x < 0:
                    player.rect.left = plat_rect.right
                    player.direction.x = 0
        
        # Гравитация
        player.update()
        player_rect = player.get_rect()
        
        # КОЛЛИЗИИ ПО Y
        player.on_ground = False
        for plat_rect, _ in platforms:
            if player_rect.colliderect(plat_rect):
                if player.direction.y > 0:
                    player.rect.bottom = plat_rect.top
                    player.direction.y = 0
                    player.on_ground = True
                    player.is_jumping = False
                elif player.direction.y < 0:
                    player.rect.top = plat_rect.bottom
                    player.direction.y = 0
                else:
                    player.rect.bottom = plat_rect.top
                    player.on_ground = True
                    player.is_jumping = False
                player_rect = player.rect
        
        # Сбор монет и сердец
        for coin in coins[:]:
            if player_rect.colliderect(coin["rect"]):
                coins.remove(coin)
                if coin["type"] == "heart":
                    LIVES = min(LIVES + 1, 5)
                    if sounds["heart"]:
                        sounds["heart"].play()
                    print(f"❤️ Сердце! Жизней: {LIVES}")
                else:
                    score += {"coin": 1, "gold": 5, "diamond": 10, "star": 50}.get(coin["type"], 1)
                    if sounds["coin"]:
                        sounds["coin"].play()
        
        # Враги с коллизией по маске
        update_enemies(enemies, platforms)
        
        for enemy in enemies:
            if player_rect.colliderect(enemy["rect"]):
                if not player.invincible:
                    LIVES -= 1
                    player.invincible = True
                    player.invincible_timer = INVINCIBLE_TIME
                    if sounds["hit"]:
                        sounds["hit"].play()
                    print(f"💔 Потеряна жизнь! Осталось: {LIVES}")
                    
                    if LIVES <= 0:
                        print("💀 ИГРОК ПОГИБ!")
                        # Возврат на старт уровня
                        LIVES = 3
                        score = max(0, score - 50)
                        player.rect.x = player_start_x
                        player.rect.y = player_start_y
                        player.direction.x = 0
                        player.direction.y = 0
                        # Перезагрузка уровня
                        level_data = load_level(current_level)
                        if level_data:
                            platforms, coins, enemies, player.rect.x, player.rect.y, finish_rect, world_width, world_height, bushes_on_ground = level_data
                            player_start_x = player.rect.x
                            player_start_y = player.rect.y
                            print("🔄 Уровень перезагружен!")
                    else:
                        # Отбрасывание при получении урона
                        if player.rect.x < enemy["x"]:
                            player.rect.x = enemy["x"] - player.width - 20
                        else:
                            player.rect.x = enemy["x"] + enemy["width"] + 20
                        player.direction.y = -8
                break
        
        # Финиш
        if finish_rect and player_rect.colliderect(finish_rect):
            print(f"🎉 УРОВЕНЬ {current_level} ПРОЙДЕН! Счёт: {score}")
            if sounds["finish"]:
                sounds["finish"].play()
            current_level += 1
            level_data = load_level(current_level)
            if level_data is None:
                print("🏆 ПОБЕДА! ИГРА ЗАКОНЧЕНА!")
                font = pygame.font.Font(None, 48)
                text = font.render("ПОБЕДА! Нажмите ESC", True, (255, 255, 0))
                screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//2))
                pygame.display.flip()
                pygame.time.wait(2000)
                return
            else:
                platforms, coins, enemies, player.rect.x, player.rect.y, finish_rect, world_width, world_height, bushes_on_ground = level_data
                player_start_x = player.rect.x
                player_start_y = player.rect.y
                player.direction.x = 0
                player.direction.y = 0
                print(f"✅ Загружен уровень {current_level}")
        
        # Ограничения
        player.rect.x = max(0, min(player.rect.x, world_width - player.width))
        
        # Камера
        camera_x = player.rect.x + player.width//2 - WINDOW_WIDTH // 2
        camera_x = max(0, min(camera_x, world_width - WINDOW_WIDTH))
        camera_y = player.rect.y + player.height//2 - WINDOW_HEIGHT // 2
        camera_y = max(0, min(camera_y, world_height - WINDOW_HEIGHT))
        
        # Анимация
        player.update_animation()
        
        # Отрисовка
        if SPRITES["sky"]:
            screen.blit(SPRITES["sky"], (0, 0))
        
        # Облака
        for cloud in random_clouds:
            x = (cloud["x"] + cloud_scroll_offset) % (world_width + 2000) - 1000
            screen.blit(cloud["img"], (x, cloud["y"]))
        
        # Платформы
        for plat_rect, plat_type in platforms:
            img = SPRITES.get(plat_type)
            if img:
                screen.blit(img, (plat_rect.x - camera_x, plat_rect.y - camera_y))
        
        # Кусты
        for bush in bushes_on_ground:
            screen.blit(bush["img"], (bush["x"] - camera_x, bush["y"] - camera_y))
        
        # Финиш
        if finish_rect and SPRITES["finish"]:
            screen.blit(SPRITES["finish"], (finish_rect.x - camera_x, finish_rect.y - camera_y))
        
        # Монеты
        for coin in coins:
            img = SPRITES.get(coin["type"])
            if img:
                screen.blit(img, (coin["rect"].x - camera_x, coin["rect"].y - camera_y))
        
        # Враги
        for enemy in enemies:
            img = SPRITES.get(enemy["type"])
            if img:
                screen.blit(img, (enemy["rect"].x - camera_x, enemy["rect"].y - camera_y))
        
        # Игрок
        player.draw(camera_x, camera_y)
        
        # UI - Жизни
        for i in range(LIVES):
            screen.blit(SPRITES["heart_icon"], (10 + i * 30, 10))
        
        # UI - Счёт
        font = pygame.font.Font(None, 24)
        info = font.render(f"Уровень: {current_level} | Счёт: {score}", True, (255, 255, 255))
        screen.blit(info, (10, 40))
        
        coins_left = len(coins)
        if coins_left > 0:
            coin_info = font.render(f"Монет осталось: {coins_left}", True, (255, 255, 0))
            screen.blit(coin_info, (10, 65))
        
        pygame.display.flip()
    
    return

# ============ ЗАПУСК ============
if __name__ == "__main__":
    if show_splash():
        if show_menu():
            run_game()
    
    pygame.quit()