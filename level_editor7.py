import pyglet
from pyglet.window import key, mouse
import json
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
GRID_SIZE = 40
WORLD_WIDTH = 60
WORLD_HEIGHT = 20

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Редактор уровней")


# Объекты с уникальными цветами
OBJECTS = {
    # Платформы
    32: {"name": "Земляz11", "color": (100, 100, 102), "category": "platform"},
    33: {"name": "Земляz12", "color": (0, 180, 3), "category": "platform"},
    34: {"name": "Земляz13", "color": (139, 90, 55), "category": "platform"},
   
    2: {"name": "Платформа", "color": (0, 180, 0), "category": "platform"},
    3: {"name": "Деревянная", "color": (139, 90, 43), "category": "platform"},
    4: {"name": "Каменная", "color": (128, 128, 128), "category": "platform"},
    
    # Монстры
    10: {"name": "Слизень", "color": (80, 200, 80), "category": "enemy"},
    11: {"name": "Скелет", "color": (220, 220, 240), "category": "enemy"},
    12: {"name": "Трухлявый пень", "color": (101, 67, 33), "category": "enemy"},
    13: {"name": "Приведение", "color": (180, 220, 255), "category": "enemy"},
    14: {"name": "Летучая мышь", "color": (80, 50, 100), "category": "enemy"},
    
    # Награды
    20: {"name": "Монета", "color": (255, 215, 0), "category": "reward"},
    21: {"name": "Слиток", "color": (255, 180, 50), "category": "reward"},
    22: {"name": "Алмаз", "color": (100, 200, 255), "category": "reward"},
    23: {"name": "Сердце", "color": (255, 80, 80), "category": "reward"},
    24: {"name": "Звезда", "color": (255, 255, 100), "category": "reward"},
    
    # Специальные
    30: {"name": "Старт", "color": (0, 200, 200), "category": "special"},
    31: {"name": "Финиш", "color": (255, 100, 255), "category": "special"},
}

# Объекты по категориям
CAT_OBJECTS = {
    "platform": [32,33,34, 2, 3, 4],
    "enemy": [10, 11, 12, 13, 14],
    "reward": [20, 21, 22, 23, 24],
    "special": [30, 31],
}

current_object = 2
camera_x = 0
camera_y = 0
show_grid = True
scroll_offset = 0
last_click_time = 0
current_file = None
modified = False

# Сетка
level = [[0 for _ in range(WORLD_WIDTH)] for _ in range(WORLD_HEIGHT)]

# Панели
LEFT_WIDTH = 280
RIGHT_WIDTH = 280
LEFT_X = 0
RIGHT_X = WINDOW_WIDTH - RIGHT_WIDTH
GRID_WIDTH = WINDOW_WIDTH - LEFT_WIDTH - RIGHT_WIDTH
GRID_HEIGHT = WINDOW_HEIGHT

# Координаты мини-карты для кликов
minimap_rect = None

class Button:
    def __init__(self, x, y, width, height, text, color, action):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.action = action
        self.hover = False
    
    def draw(self):
        color = (self.color[0] + 25 if self.hover else self.color[0],
                 self.color[1] + 25 if self.hover else self.color[1],
                 self.color[2] + 25 if self.hover else self.color[2])
        rect = pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=color)
        rect.draw()
        label = pyglet.text.Label(self.text, x=self.x + self.width//2, y=self.y + self.height//2,
                                   font_size=11, color=(255,255,255,255), anchor_x='center', anchor_y='center')
        label.draw()
    
    def check_click(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

buttons = []
level_files = []

def get_level_files():
    global level_files
    if not os.path.exists("levels"):
        os.makedirs("levels")
    files = [f for f in os.listdir("levels") if f.endswith(".json")]
    level_files = sorted(files)

def init_buttons():
    global buttons
    y = GRID_HEIGHT - 70
    buttons = [
        Button(RIGHT_X + 15, y, 250, 35, "💾 СОХРАНИТЬ", (0, 100, 0), "save"),
        Button(RIGHT_X + 15, y - 42, 250, 35, "📂 ЗАГРУЗИТЬ", (0, 80, 100), "load"),
        Button(RIGHT_X + 15, y - 84, 250, 35, "➕ НОВЫЙ УРОВЕНЬ", (100, 80, 0), "new"),
        Button(RIGHT_X + 15, y - 126, 250, 35, "🗑️ ОЧИСТИТЬ ВСЁ", (120, 30, 30), "clear"),
        Button(RIGHT_X + 15, y - 168, 250, 35, "🔲 СЕТКА: ВКЛ", (60, 60, 80), "grid"),
        Button(RIGHT_X + 15, y - 210, 250, 35, "📋 ЭКСПОРТ", (100, 80, 0), "export"),
    ]

def set_modified():
    global modified
    modified = True

def check_save_before_action():
    global modified
    if modified:
        root = tk.Tk()
        root.withdraw()
        answer = messagebox.askyesnocancel("Несохранённые изменения", 
                                            "Сохранить изменения перед продолжением?")
        root.destroy()
        if answer is None:
            return False
        elif answer:
            save_level_dialog()
            if modified:
                return False
    return True

def save_level_dialog():
    global modified, current_file
    
    root = tk.Tk()
    root.withdraw()
    
    if current_file:
        filename = current_file
    else:
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="levels"
        )
        if not filename:
            root.destroy()
            return False
        filename = os.path.basename(filename)
    
    data = {"grid": level, "width": WORLD_WIDTH, "height": WORLD_HEIGHT}
    for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):
            if level[y][x] == 30:
                data["start_x"] = x * GRID_SIZE
                data["start_y"] = y * GRID_SIZE
                break
    
    try:
        with open(f"levels/{filename}", "w") as f:
            json.dump(data, f, indent=2)
        current_file = filename
        modified = False
        get_level_files()
        print(f"✅ Сохранено: {filename}")
        root.destroy()
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        root.destroy()
        return False

def load_level_dialog():
    global level, current_file, modified
    
    if not check_save_before_action():
        return
    
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        initialdir="levels"
    )
    
    if filename:
        filename = os.path.basename(filename)
        try:
            with open(f"levels/{filename}", "r") as f:
                data = json.load(f)
            
            for y in range(WORLD_HEIGHT):
                for x in range(WORLD_WIDTH):
                    level[y][x] = 0
            
            grid = data["grid"]
            for y in range(min(WORLD_HEIGHT, len(grid))):
                for x in range(min(WORLD_WIDTH, len(grid[y]))):
                    level[y][x] = grid[y][x]
            
            current_file = filename
            modified = False
            print(f"✅ Загружено: {filename}")
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
    
    root.destroy()

def load_level_dialog_by_name(filename):
    global level, current_file, modified
    try:
        with open(f"levels/{filename}", "r") as f:
            data = json.load(f)
        
        for y in range(WORLD_HEIGHT):
            for x in range(WORLD_WIDTH):
                level[y][x] = 0
        
        grid = data["grid"]
        for y in range(min(WORLD_HEIGHT, len(grid))):
            for x in range(min(WORLD_WIDTH, len(grid[y]))):
                level[y][x] = grid[y][x]
        
        current_file = filename
        modified = False
        print(f"✅ Загружено: {filename}")
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")

def new_level():
    global level, modified, current_file
    
    if not check_save_before_action():
        return
    
    for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):
            level[y][x] = 0
    
    current_file = None
    modified = False
    print("✅ Новый уровень")

def clear_level():
    global modified
    root = tk.Tk()
    root.withdraw()
    answer = messagebox.askyesno("Подтверждение", "Очистить весь уровень?")
    root.destroy()
    
    if answer:
        for y in range(WORLD_HEIGHT):
            for x in range(WORLD_WIDTH):
                level[y][x] = 0
        modified = True
        print("✅ Уровень очищен")

def export_level():
    data = {
        "name": current_file or "untitled",
        "width": WORLD_WIDTH,
        "height": WORLD_HEIGHT,
        "tile_size": GRID_SIZE,
        "objects": []
    }
    
    for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):
            obj_id = level[y][x]
            if obj_id != 0 and obj_id in OBJECTS:
                obj = OBJECTS[obj_id]
                data["objects"].append({
                    "id": obj_id,
                    "name": obj["name"],
                    "category": obj["category"],
                    "x": x * GRID_SIZE,
                    "y": y * GRID_SIZE,
                    "grid_x": x,
                    "grid_y": y
                })
    
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        initialdir="levels",
        initialfile=f"export_{current_file}" if current_file else "export"
    )
    
    if filename:
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Экспорт сохранён: {filename}")
            print(f"   Объектов: {len(data['objects'])}")
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
    
    root.destroy()

def draw_left_panel():
    global scroll_offset
    bg = pyglet.shapes.Rectangle(LEFT_X, 0, LEFT_WIDTH, GRID_HEIGHT, color=(35, 35, 45))
    bg.draw()
    
    pyglet.text.Label("ВЫБОР ОБЪЕКТОВ", x=LEFT_X + LEFT_WIDTH//2, y=GRID_HEIGHT - 25,
                       font_size=16, color=(255, 220, 100, 255), anchor_x='center').draw()
    
    y = GRID_HEIGHT - 70 + scroll_offset
    for cat_name, obj_list in CAT_OBJECTS.items():
        pyglet.text.Label(cat_name.upper(), x=LEFT_X + 15, y=y,
                           font_size=12, color=(200, 200, 100, 255)).draw()
        y -= 25
        
        for obj_id in obj_list:
            if obj_id in OBJECTS:
                obj = OBJECTS[obj_id]
                obj_y = y
                if current_object == obj_id:
                    pyglet.shapes.Rectangle(LEFT_X + 10, obj_y - 2, LEFT_WIDTH - 20, 24, color=(80, 100, 120)).draw()
                
                pyglet.shapes.Rectangle(LEFT_X + 12, obj_y, 30, 20, color=obj["color"]).draw()
                pyglet.text.Label(obj["name"], x=LEFT_X + 50, y=obj_y + 4,
                                   font_size=11, color=(220,220,220,255)).draw()
                
                if not hasattr(window, 'obj_buttons'):
                    window.obj_buttons = []
                window.obj_buttons.append((obj_id, LEFT_X + 10, obj_y - 2, LEFT_WIDTH - 20, 24))
                y -= 26
        y -= 10
    
    # Инфо
    pyglet.shapes.Rectangle(LEFT_X, 10, LEFT_WIDTH, 90, color=(25, 25, 35)).draw()
    cur = OBJECTS.get(current_object, {"name": "Пусто"})
    pyglet.text.Label(f"ТЕКУЩИЙ:", x=LEFT_X + 15, y=20, font_size=10, color=(150,150,180)).draw()
    pyglet.text.Label(cur["name"], x=LEFT_X + 15, y=40, font_size=14, color=(255,220,100)).draw()
    
    if current_file:
        pyglet.text.Label(f"Файл: {current_file}", x=LEFT_X + 15, y=65, 
                          font_size=9, color=(100,150,200)).draw()
    if modified:
        pyglet.text.Label("*", x=LEFT_X + LEFT_WIDTH - 20, y=GRID_HEIGHT - 28, 
                          font_size=16, color=(255,100,100)).draw()

def draw_right_panel():
    bg = pyglet.shapes.Rectangle(RIGHT_X, 0, RIGHT_WIDTH, GRID_HEIGHT, color=(40, 40, 48))
    bg.draw()
    
    pyglet.text.Label("УПРАВЛЕНИЕ", x=RIGHT_X + RIGHT_WIDTH//2, y=GRID_HEIGHT - 25,
                       font_size=16, color=(100, 200, 255), anchor_x='center').draw()
    
    for btn in buttons:
        btn.draw()
    
    list_y = GRID_HEIGHT - 320
    pyglet.text.Label("ДОСТУПНЫЕ УРОВНИ:", x=RIGHT_X + 15, y=list_y,
                       font_size=12, color=(220, 220, 150)).draw()
    
    y = list_y - 30
    if not hasattr(window, 'file_buttons'):
        window.file_buttons = []
    window.file_buttons = []
    for f in level_files:
        color = (75, 95, 115) if f == current_file else (55, 55, 65)
        pyglet.shapes.Rectangle(RIGHT_X + 12, y - 2, RIGHT_WIDTH - 24, 26, color=color).draw()
        pyglet.text.Label(f, x=RIGHT_X + 20, y=y + 4, font_size=10, color=(200,200,220)).draw()
        window.file_buttons.append((f, RIGHT_X + 12, y - 2, RIGHT_WIDTH - 24, 26))
        y -= 30

def draw_minimap():
    global minimap_rect
    minimap_width = 240
    minimap_height = 140
    minimap_x = RIGHT_X + (RIGHT_WIDTH - minimap_width) // 2
    minimap_y = 15
    
    minimap_rect = (minimap_x, minimap_y, minimap_width, minimap_height)
    
    pyglet.shapes.Rectangle(minimap_x, minimap_y, minimap_width, minimap_height, color=(20, 20, 30)).draw()
    
    # Рамка
    pyglet.shapes.Rectangle(minimap_x, minimap_y, minimap_width, 1, color=(80, 80, 100)).draw()
    pyglet.shapes.Rectangle(minimap_x, minimap_y + minimap_height - 1, minimap_width, 1, color=(80, 80, 100)).draw()
    pyglet.shapes.Rectangle(minimap_x, minimap_y, 1, minimap_height, color=(80, 80, 100)).draw()
    pyglet.shapes.Rectangle(minimap_x + minimap_width - 1, minimap_y, 1, minimap_height, color=(80, 80, 100)).draw()
    
    scale_x = minimap_width / WORLD_WIDTH
    scale_y = minimap_height / WORLD_HEIGHT
    
    for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):
            obj_id = level[y][x]
            if obj_id != 0:
                obj = OBJECTS.get(obj_id)
                if obj:
                    rect_x = minimap_x + x * scale_x
                    rect_y = minimap_y + y * scale_y
                    w = max(1, scale_x)
                    h = max(1, scale_y)
                    pyglet.shapes.Rectangle(rect_x, rect_y, w, h, color=obj["color"]).draw()
    
    view_x = camera_x / GRID_SIZE
    view_y = camera_y / GRID_SIZE
    view_w = GRID_WIDTH / GRID_SIZE
    view_h = GRID_HEIGHT / GRID_SIZE
    
    view_rect_x = minimap_x + view_x * scale_x
    view_rect_y = minimap_y + view_y * scale_y
    view_rect_w = max(1, view_w * scale_x)
    view_rect_h = max(1, view_h * scale_y)
    
    # Рамка области видимости
    if 0 <= view_rect_x < minimap_x + minimap_width:
        pyglet.shapes.Line(view_rect_x, view_rect_y + view_rect_h, 
                           view_rect_x + view_rect_w, view_rect_y + view_rect_h, 
                           color=(255, 255, 100)).draw()
        pyglet.shapes.Line(view_rect_x, view_rect_y, 
                           view_rect_x + view_rect_w, view_rect_y, 
                           color=(255, 255, 100)).draw()
        pyglet.shapes.Line(view_rect_x, view_rect_y, 
                           view_rect_x, view_rect_y + view_rect_h, 
                           color=(255, 255, 100)).draw()
        pyglet.shapes.Line(view_rect_x + view_rect_w, view_rect_y, 
                           view_rect_x + view_rect_w, view_rect_y + view_rect_h, 
                           color=(255, 255, 100)).draw()
    
    pyglet.text.Label("МИНИ-КАРТА (кликабельно)", x=minimap_x + minimap_width//2, y=minimap_y + minimap_height + 8,
                       font_size=9, color=(150,150,150), anchor_x='center').draw()

def draw_grid():
    if not show_grid:
        return
    for x in range(0, WORLD_WIDTH * GRID_SIZE + 1, GRID_SIZE):
        pyglet.shapes.Line(x - camera_x + LEFT_WIDTH, 0 - camera_y,
                           x - camera_x + LEFT_WIDTH, GRID_HEIGHT - camera_y,
                           color=(70, 70, 90)).draw()
    for y in range(0, WORLD_HEIGHT * GRID_SIZE + 1, GRID_SIZE):
        pyglet.shapes.Line(LEFT_WIDTH, y - camera_y,
                           LEFT_WIDTH + GRID_WIDTH, y - camera_y,
                           color=(70, 70, 90)).draw()

def draw_level():
    for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):
            obj_id = level[y][x]
            if obj_id != 0 and obj_id in OBJECTS:
                obj = OBJECTS[obj_id]
                pyglet.shapes.Rectangle(
                    x * GRID_SIZE - camera_x + LEFT_WIDTH,
                    y * GRID_SIZE - camera_y,
                    GRID_SIZE - 1, GRID_SIZE - 1,
                    color=obj["color"]
                ).draw()

def get_cell(mx, my):
    if mx < LEFT_WIDTH or mx > LEFT_WIDTH + GRID_WIDTH or my > GRID_HEIGHT:
        return None, None
    wx = mx - LEFT_WIDTH + camera_x
    wy = my + camera_y
    cx = int(wx // GRID_SIZE)
    cy = int(wy // GRID_SIZE)
    if 0 <= cx < WORLD_WIDTH and 0 <= cy < WORLD_HEIGHT:
        return cx, cy
    return None, None

def minimap_to_camera(mx, my):
    """Преобразует координаты клика на мини-карте в позицию камеры"""
    global minimap_rect
    if not minimap_rect:
        return
    
    minimap_x, minimap_y, minimap_w, minimap_h = minimap_rect
    
    # Проверяем, попал ли клик в область мини-карты
    if not (minimap_x <= mx <= minimap_x + minimap_w and 
            minimap_y <= my <= minimap_y + minimap_h):
        return None
    
    # Нормализуем координаты от 0 до 1
    nx = (mx - minimap_x) / minimap_w
    ny = (my - minimap_y) / minimap_h
    
    # Преобразуем в координаты мира
    world_x = nx * WORLD_WIDTH * GRID_SIZE
    world_y = ny * WORLD_HEIGHT * GRID_SIZE
    
    # Центрируем камеру на выбранной точке
    new_camera_x = world_x - GRID_WIDTH // 2
    new_camera_y = world_y - GRID_HEIGHT // 2
    
    # Ограничиваем камеру
    new_camera_x = max(0, min(new_camera_x, WORLD_WIDTH * GRID_SIZE - GRID_WIDTH))
    new_camera_y = max(0, min(new_camera_y, WORLD_HEIGHT * GRID_SIZE - GRID_HEIGHT))
    
    return new_camera_x, new_camera_y

@window.event
def on_mouse_press(x, y, btn, mod):
    global current_object, show_grid, last_click_time, modified, camera_x, camera_y
    
    current_time = time.time()
    if current_time - last_click_time < 0.1:
        return
    last_click_time = current_time
    
    # Проверка клика по мини-карте
    if btn == mouse.LEFT:
        new_camera = minimap_to_camera(x, y)
        if new_camera:
            camera_x, camera_y = new_camera
            return
    
    if btn == mouse.RIGHT:
        cx, cy = get_cell(x, y)
        if cx is not None:
            level[cy][cx] = 0
            modified = True
        return
    
    for b in buttons:
        if b.check_click(x, y):
            if b.action == "save":
                save_level_dialog()
            elif b.action == "load":
                load_level_dialog()
            elif b.action == "new":
                new_level()
            elif b.action == "clear":
                clear_level()
            elif b.action == "grid":
                show_grid = not show_grid
                b.text = "🔲 СЕТКА: ВКЛ" if show_grid else "🔲 СЕТКА: ВЫКЛ"
            elif b.action == "export":
                export_level()
            return
    
    if hasattr(window, 'file_buttons'):
        for fname, fx, fy, fw, fh in window.file_buttons:
            if fx <= x <= fx + fw and fy <= y <= fy + fh:
                if not check_save_before_action():
                    return
                load_level_dialog_by_name(fname)
                return
    
    if x < LEFT_WIDTH:
        if hasattr(window, 'obj_buttons'):
            for obj_id, ox, oy, ow, oh in window.obj_buttons:
                if ox <= x <= ox + ow and oy <= y <= oy + oh:
                    current_object = obj_id
                    return
    
    cx, cy = get_cell(x, y)
    if cx is not None:
        level[cy][cx] = current_object
        modified = True

@window.event
def on_mouse_drag(x, y, dx, dy, btn, mod):
    if btn == mouse.LEFT and x > LEFT_WIDTH and x < LEFT_WIDTH + GRID_WIDTH and y < GRID_HEIGHT:
        cx, cy = get_cell(x, y)
        if cx is not None and level[cy][cx] != current_object:
            level[cy][cx] = current_object
            modified = True

@window.event
def on_mouse_scroll(x, y, sx, sy):
    global scroll_offset
    if x < LEFT_WIDTH:
        scroll_offset += sy * 15
        scroll_offset = min(0, max(scroll_offset, -400))

@window.event
def on_mouse_motion(x, y, dx, dy):
    for b in buttons:
        b.hover = b.check_click(x, y)

@window.event
def on_key_press(sym, mod):
    global camera_x, camera_y, modified
    
    step = 50
    if sym == key.LEFT:
        camera_x -= step
    elif sym == key.RIGHT:
        camera_x += step
    elif sym == key.UP:
        camera_y -= step
    elif sym == key.DOWN:
        camera_y += step
    elif sym == key.S and (mod & key.MOD_CTRL):
        save_level_dialog()
    elif sym == key.L and (mod & key.MOD_CTRL):
        load_level_dialog()
    elif sym == key.N and (mod & key.MOD_CTRL):
        new_level()
    
    camera_x = max(0, min(camera_x, WORLD_WIDTH * GRID_SIZE - GRID_WIDTH))
    camera_y = max(0, min(camera_y, WORLD_HEIGHT * GRID_SIZE - GRID_HEIGHT))

@window.event
def on_draw():
    window.clear()
    draw_level()
    draw_grid()
    draw_left_panel()
    draw_right_panel()
    draw_minimap()
    
    info = f"Камера: X={camera_x} Y={camera_y} | Сетка: {'Вкл' if show_grid else 'Выкл'} | Объектов: {sum(1 for row in level for cell in row if cell != 0)}"
    pyglet.text.Label(info, x=10, y=8, font_size=9, color=(150,150,180)).draw()

# Запуск
init_buttons()
get_level_files()

print("=" * 60)
print("РЕДАКТОР УРОВНЕЙ v4.3")
print("=" * 60)
print("🖱️ ЛЕВАЯ панель - выбор объектов")
print("🖱️ ПРАВАЯ панель - кнопки управления")
print("🖱️ ЛКМ на сетке - поставить блок")
print("🖱️ ПКМ на сетке - удалить блок")
print("🖱️ КЛИК на мини-карте - переместить камеру")
print("⌨️ Стрелки - перемещение камеры")
print("⌨️ Ctrl+S - сохранить")
print("⌨️ Ctrl+L - загрузить")
print("⌨️ Ctrl+N - новый уровень")
print("=" * 60)

pyglet.app.run()