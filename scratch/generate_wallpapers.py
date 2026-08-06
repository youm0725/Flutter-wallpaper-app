import os
import json
import math
import random
from PIL import Image, ImageDraw, ImageFilter

# Path definitions
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_PATH = os.path.join(ROOT_DIR, "assets", "metadata", "wallpapers.json")
WALLPAPERS_DIR = os.path.join(ROOT_DIR, "assets", "wallpapers")

def create_gradient_canvas(width, height, color1, color2, vertical=True):
    base = Image.new("RGB", (width, height), color1)
    top = Image.new("RGB", (width, height), color2)
    mask = Image.new("L", (width, height))
    mask_draw = ImageDraw.Draw(mask)
    for y in range(height):
        ratio = y / height if vertical else 0
        val = int(255 * ratio)
        mask_draw.line([(0, y), (width, y)], fill=val)
    return Image.composite(top, base, mask)

def draw_nature(draw, width, height, item_id):
    if item_id == "nature_01":
        # Misty Alpine Forest
        draw.polygon([(0, height * 0.7), (width * 0.5, height * 0.4), (width, height * 0.75), (width, height), (0, height)], fill=(20, 45, 40))
        draw.polygon([(0, height * 0.8), (width * 0.7, height * 0.55), (width, height * 0.85), (width, height), (0, height)], fill=(12, 30, 26))
        for i in range(25):
            tx = random.randint(0, width)
            ty = int(height * (0.65 + random.random() * 0.3))
            tw = random.randint(30, 80)
            th = random.randint(100, 250)
            draw.polygon([(tx, ty - th), (tx - tw//2, ty), (tx + tw//2, ty)], fill=(8, 22, 18))
    elif item_id == "nature_02":
        # Golden Hour Horizon
        cx, cy = width // 2, int(height * 0.55)
        draw.ellipse([cx-140, cy-140, cx+140, cy+140], fill=(255, 230, 160))
        draw.polygon([(0, height * 0.6), (width * 0.4, height * 0.52), (width, height * 0.65), (width, height), (0, height)], fill=(80, 30, 10))
        draw.polygon([(0, height * 0.7), (width * 0.75, height * 0.58), (width, height * 0.72), (width, height), (0, height)], fill=(40, 12, 5))
    elif item_id == "nature_03":
        # Emerald Canyon River
        draw.polygon([(0, height*0.3), (width*0.4, height*0.7), (width*0.3, height), (0, height)], fill=(15, 35, 25))
        draw.polygon([(width, height*0.25), (width*0.55, height*0.7), (width*0.7, height), (width, height)], fill=(10, 25, 18))
        draw.polygon([(width*0.35, height*0.68), (width*0.45, height*0.8), (width*0.1, height), (width*0.8, height)], fill=(30, 160, 130))

def draw_abstract(draw, img, width, height, item_id):
    if item_id == "abstract_01":
        for i in range(6):
            r = random.randint(150, 400)
            cx = random.randint(0, width)
            cy = random.randint(0, height)
            color = random.choice([(230, 50, 150, 140), (50, 180, 240, 140), (140, 60, 230, 140)])
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            odraw = ImageDraw.Draw(overlay)
            odraw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
            overlay = overlay.filter(ImageFilter.GaussianBlur(60))
            img.paste(overlay, (0, 0), overlay)
    elif item_id == "abstract_02":
        for i in range(16):
            pts = [(random.randint(0, width), random.randint(0, height)) for _ in range(3)]
            c = (random.randint(100, 255), random.randint(100, 220), random.randint(150, 255), 110)
            overlay = Image.new("RGBA", (width, height), (0,0,0,0))
            odraw = ImageDraw.Draw(overlay)
            odraw.polygon(pts, fill=c, outline=(255, 255, 255, 180))
            img.paste(overlay, (0, 0), overlay)
    elif item_id == "abstract_03":
        for i in range(8):
            y = int(height * (0.15 + i * 0.12))
            draw.line([(0, y), (width, y + 100)], fill=(60, 65, 75), width=35)

def draw_amoled(draw, img, width, height, item_id):
    if item_id == "amoled_01":
        cx, cy = width // 2, height // 2 - 50
        r = 180
        glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.ellipse([cx-r-30, cy-r-30, cx+r+30, cy+r+30], fill=(0, 210, 255, 220))
        glow = glow.filter(ImageFilter.GaussianBlur(40))
        img.paste(glow, (0, 0), glow)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(0, 0, 0))
    elif item_id == "amoled_02":
        cx, cy = width // 2, height // 2
        for radius in range(60, 420, 50):
            draw.regular_polygon((cx, cy, radius), 6, rotation=radius, outline=(225, 185, 95), width=3)
    elif item_id == "amoled_03":
        for y in range(0, height, 50):
            draw.line([(0, y), (width, y)], fill=(0, 45, 65), width=1)
        for x in range(0, width, 50):
            draw.line([(x, 0), (x, height)], fill=(0, 45, 65), width=1)
        draw.line([(0, height*0.65), (width, height*0.35)], fill=(0, 240, 255), width=5)

def draw_anime(draw, img, width, height, item_id):
    if item_id == "anime_01":
        draw.ellipse([width*0.25, height*0.35, width*0.75, height*0.58], fill=(255, 110, 160))
        for i in range(14):
            w = random.randint(50, 100)
            h = random.randint(180, 500)
            x = i * 75
            draw.rectangle([x, height - h, x + w, height], fill=(18, 12, 35))
    elif item_id == "anime_02":
        draw.ellipse([width*0.15, height*0.12, width*0.85, height*0.48], fill=(245, 245, 230))
        gw = 160
        gx = width // 2
        gy = int(height * 0.62)
        draw.rectangle([gx - gw//2, gy, gx + gw//2, gy + 18], fill=(20, 15, 30))
        draw.rectangle([gx - gw//2 + 10, gy + 35, gx + gw//2 - 10, gy + 48], fill=(20, 15, 30))
        draw.rectangle([gx - 50, gy, gx - 32, gy + 220], fill=(20, 15, 30))
        draw.rectangle([gx + 32, gy, gx + 50, gy + 220], fill=(20, 15, 30))

def draw_space(draw, img, width, height, item_id):
    for _ in range(300):
        sx = random.randint(0, width)
        sy = random.randint(0, height)
        sz = random.randint(1, 3)
        brightness = random.randint(160, 255)
        draw.ellipse([sx, sy, sx+sz, sy+sz], fill=(brightness, brightness, brightness))
    nebula = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ndraw = ImageDraw.Draw(nebula)
    ndraw.ellipse([width*0.05, height*0.15, width*0.95, height*0.75], fill=(140, 40, 200, 110))
    ndraw.ellipse([width*0.15, height*0.35, width*0.85, height*0.85], fill=(40, 160, 230, 100))
    nebula = nebula.filter(ImageFilter.GaussianBlur(70))
    img.paste(nebula, (0, 0), nebula)

def draw_generic(draw, img, width, height, item_id, category):
    colors = [(240, 90, 80), (70, 130, 240), (250, 190, 40), (40, 200, 150)]
    c = random.choice(colors)
    draw.ellipse([width*0.2, height*0.3, width*0.8, height*0.6], outline=c, width=10)

def generate_wallpaper(item):
    item_id = item['id']
    category = item['category']
    title = item['title']

    print(f"Generating optimized WebP wallpaper for {item_id} ({title})...")

    full_w, full_h = 1080, 1920
    thumb_w, thumb_h = 360, 640

    if category == "nature":
        if "01" in item_id:
            c1, c2 = (15, 32, 39), (44, 83, 100)
        else:
            c1, c2 = (255, 120, 50), (40, 10, 20)
    elif category == "abstract":
        c1, c2 = (20, 10, 35), (80, 20, 90)
    elif category == "amoled":
        c1, c2 = (0, 0, 0), (5, 5, 10)
    elif category == "anime":
        c1, c2 = (30, 15, 55), (120, 40, 90)
    elif category == "architecture":
        c1, c2 = (25, 35, 45), (70, 85, 100)
    elif category == "cars":
        c1, c2 = (10, 15, 30), (60, 20, 60)
    elif category == "gaming":
        c1, c2 = (15, 5, 30), (80, 15, 70)
    elif category == "minimal":
        if "02" in item_id:
            c1, c2 = (240, 235, 225), (210, 190, 180)
        else:
            c1, c2 = (220, 100, 60), (40, 20, 30)
    elif category == "space":
        c1, c2 = (5, 5, 20), (25, 10, 45)
    else:
        c1, c2 = (30, 30, 40), (80, 80, 100)

    img = create_gradient_canvas(full_w, full_h, c1, c2)
    draw = ImageDraw.Draw(img)

    if category == "nature":
        draw_nature(draw, full_w, full_h, item_id)
    elif category == "abstract":
        draw_abstract(draw, img, full_w, full_h, item_id)
    elif category == "amoled":
        draw_amoled(draw, img, full_w, full_h, item_id)
    elif category == "anime":
        draw_anime(draw, img, full_w, full_h, item_id)
    elif category == "space":
        draw_space(draw, img, full_w, full_h, item_id)
    else:
        draw_generic(draw, img, full_w, full_h, item_id, category)

    cat_dir = os.path.join(WALLPAPERS_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    
    thumb_cat_dir = os.path.join(WALLPAPERS_DIR, "thumbnails", category)
    os.makedirs(thumb_cat_dir, exist_ok=True)

    filename_base = os.path.splitext(os.path.basename(item['imagePath']))[0]
    
    full_path = os.path.join(cat_dir, f"{filename_base}.webp")
    thumb_path = os.path.join(thumb_cat_dir, f"{filename_base}.webp")

    img.save(full_path, "WEBP", quality=85, method=6)
    
    thumb_img = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
    thumb_img.save(thumb_path, "WEBP", quality=75, method=6)

    rel_full_path = f"assets/wallpapers/{category}/{filename_base}.webp"
    rel_thumb_path = f"assets/wallpapers/thumbnails/{category}/{filename_base}.webp"

    full_bytes = os.path.getsize(full_path)
    thumb_bytes = os.path.getsize(thumb_path)

    full_kb = round(full_bytes / 1024, 1)
    thumb_kb = round(thumb_bytes / 1024, 1)

    print(f"  [OK] Full: {rel_full_path} ({full_kb} KB)")
    print(f"  [OK] Thumb: {rel_thumb_path} ({thumb_kb} KB)")

    return rel_full_path, rel_thumb_path, full_kb, thumb_kb

def main():
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        wallpapers = json.load(f)

    for item in wallpapers:
        rel_full, rel_thumb, f_kb, t_kb = generate_wallpaper(item)
        item['imagePath'] = rel_full
        item['thumbnailPath'] = rel_thumb
        item['fileSize'] = f"{int(f_kb)} KB" if f_kb < 1000 else f"{round(f_kb / 1024, 1)} MB"

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(wallpapers, f, indent=2)

    print("\n==========================================")
    print("ALL WEBP ASSETS SUCCESSFULLY GENERATED!")
    print(f"Total Full Wallpapers: {len(wallpapers)}")
    print("==========================================")

if __name__ == "__main__":
    main()
