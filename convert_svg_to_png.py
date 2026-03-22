# convert_svg_to_png.py
import os
import sys
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

def find_inkscape():
    """Ищет Inkscape в системе"""
    possible_paths = [
        r"C:\Program Files\Inkscape\bin\inkscape.exe",
        r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
        r"C:\Program Files\Inkscape\inkscape.exe",
        r"C:\Program Files (x86)\Inkscape\inkscape.exe",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def get_svg_size(svg_path):
    """Читает размер SVG из файла"""
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Ищем атрибуты width/height
        width = root.get('width')
        height = root.get('height')
        
        # Если есть viewBox
        viewbox = root.get('viewBox')
        if viewbox and (not width or not height):
            parts = viewbox.split()
            if len(parts) >= 4:
                width = parts[2]
                height = parts[3]
        
        # Убираем единицы измерения (px, pt, etc)
        if width:
            width = float(''.join(c for c in width if c.isdigit() or c == '.'))
        if height:
            height = float(''.join(c for c in height if c.isdigit() or c == '.'))
        
        # Если размеры не найдены, возвращаем 128
        if not width or not height or width <= 0 or height <= 0:
            return 128, 128
        
        return int(width), int(height)
        
    except Exception as e:
        print(f"  ⚠️ Не удалось прочитать размер: {e}")
        return 128, 128

def convert_svg_to_png_inkscape(svg_path, png_path, width=None, height=None):
    """Конвертирует SVG в PNG через Inkscape с сохранением пропорций"""
    inkscape = find_inkscape()
    if not inkscape:
        print("❌ Inkscape не найден")
        return False
    
    try:
        # Если размер не указан, берём оригинальный
        if width is None or height is None:
            width, height = get_svg_size(svg_path)
        
        # Используем Inkscape (новая версия)
        cmd = [
            inkscape,
            str(svg_path),
            "--export-filename", str(png_path),
            f"--export-width={width}",
            f"--export-height={height}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Пробуем старую версию Inkscape
            cmd_old = [
                inkscape,
                "-z", "-e", str(png_path),
                "-w", str(width), "-h", str(height),
                str(svg_path)
            ]
            result = subprocess.run(cmd_old, capture_output=True, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

def convert_all_svg(force_overwrite=True):
    """Конвертирует все SVG в PNG"""
    print("=" * 60)
    print("🖼️  КОНВЕРТЕР SVG → PNG (с сохранением размеров)")
    print("=" * 60)
    
    # Проверяем Inkscape
    inkscape = find_inkscape()
    if not inkscape:
        print("\n❌ Inkscape не найден!")
        print("\n📥 Скачайте Inkscape с: https://inkscape.org/release/")
        print("   Установите и запустите скрипт снова")
        return
    
    print(f"\n✅ Inkscape найден: {inkscape}")
    
    # Находим все SVG файлы
    svg_files = list(Path("assets/images").rglob("*.svg"))
    
    if not svg_files:
        print("\n⚠️ SVG файлы не найдены в папке assets/images")
        return
    
    print(f"\n📁 Найдено SVG файлов: {len(svg_files)}")
    
    # Статистика
    converted = 0
    failed = 0
    skipped = 0
    
    print("\n🔄 Конвертация...")
    print("-" * 60)
    
    for svg_path in svg_files:
        png_path = svg_path.with_suffix('.png')
        
        # Получаем оригинальный размер SVG
        orig_width, orig_height = get_svg_size(svg_path)
        
        # Если PNG существует и не нужно перезаписывать
        if png_path.exists() and not force_overwrite:
            print(f"⏭️  Пропуск (PNG уже есть): {svg_path.name}")
            skipped += 1
            continue
        
        print(f"📄 {svg_path.name} ({orig_width}x{orig_height})")
        
        if convert_svg_to_png_inkscape(svg_path, png_path, orig_width, orig_height):
            converted += 1
            print(f"   ✅ Создан: {png_path.name} ({orig_width}x{orig_height})")
        else:
            failed += 1
            print(f"   ❌ Ошибка")
    
    # Итог
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТ:")
    print(f"   ✅ Сконвертировано: {converted}")
    print(f"   ⏭️  Пропущено: {skipped}")
    print(f"   ❌ Ошибок: {failed}")
    print(f"   📁 Всего обработано: {len(svg_files)}")
    print("=" * 60)

def convert_single_file():
    """Конвертирует один выбранный файл"""
    print("=" * 60)
    print("🖼️  КОНВЕРТЕР ОДНОГО ФАЙЛА")
    print("=" * 60)
    
    svg_path = input("\nВведите путь к SVG файлу: ").strip()
    svg_path = Path(svg_path)
    
    if not svg_path.exists():
        print(f"❌ Файл не найден: {svg_path}")
        return
    
    if svg_path.suffix.lower() != '.svg':
        print("❌ Файл не является SVG")
        return
    
    # Получаем оригинальный размер
    width, height = get_svg_size(svg_path)
    print(f"📏 Оригинальный размер: {width}x{height}")
    
    png_path = svg_path.with_suffix('.png')
    
    if convert_svg_to_png_inkscape(svg_path, png_path, width, height):
        print(f"✅ Создан: {png_path} ({width}x{height})")
    else:
        print("❌ Ошибка конвертации")

def show_menu():
    """Показывает меню"""
    print("\n" + "=" * 60)
    print("🖼️  КОНВЕРТЕР SVG → PNG")
    print("=" * 60)
    print("1. Конвертировать все SVG (перезаписать PNG)")
    print("2. Конвертировать один файл")
    print("3. Выход")
    print("-" * 60)
    
    choice = input("Выберите действие (1-3): ").strip()
    
    if choice == "1":
        convert_all_svg(force_overwrite=True)
    elif choice == "2":
        convert_single_file()
    elif choice == "3":
        print("До свидания!")
        sys.exit(0)
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    # Проверяем папку
    if not os.path.exists("assets/images"):
        print("❌ Папка assets/images не найдена!")
        print("   Убедитесь, что вы запускаете скрипт из корневой папки проекта")
        sys.exit(1)
    
    while True:
        show_menu()
        input("\nНажмите Enter для продолжения...")