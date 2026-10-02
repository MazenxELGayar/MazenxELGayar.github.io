from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIDTH, HEIGHT = 1200, 630


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}.ttf", size)


image = Image.new("RGB", (WIDTH, HEIGHT), "#0b1220")
pixels = image.load()
start = (11, 18, 32)
end = (20, 32, 53)
for y in range(HEIGHT):
    for x in range(WIDTH):
        glow = max(0.0, 1 - (((x - 910) / 700) ** 2 + ((y - 320) / 540) ** 2) ** 0.5)
        blend = (y / HEIGHT) * 0.35 + glow * 0.22
        pixels[x, y] = tuple(round(a * (1 - blend) + b * blend) for a, b in zip(start, end))

draw = ImageDraw.Draw(image, "RGBA")
# Fine ambient rings echo the interactive hero artwork on the site.
draw.ellipse((695, 92, 1165, 548), outline=(112, 137, 205, 85), width=2)
draw.ellipse((748, 58, 1110, 584), outline=(112, 137, 205, 65), width=2)
draw.rounded_rectangle((625, 83, 1145, 552), radius=34, fill=(20, 32, 53, 110), outline=(61, 78, 111, 150), width=2)

white = "#f4f6fb"
muted = "#b8c2d5"
blue = "#8197ed"
draw.text((78, 78), "SOFTWARE ENGINEER  ·  INDEPENDENT GAME DEVELOPER", font=font("segoeuib", 18), fill=blue)
draw.text((74, 177), "Mazen EL-Gayar", font=font("segoeuib", 60), fill=white, stroke_width=0)
draw.text((79, 259), "Software that ships.", font=font("segoeuii", 47), fill=blue)
draw.text((82, 339), "Flutter  ·  NestJS  ·  Unreal Engine", font=font("segoeui", 24), fill=muted)

# The portrait crop matches the round profile treatment in the current hero.
portrait = Image.open(ASSETS / "profile-photo.webp").convert("RGB")
side = min(portrait.size)
left = max(0, min(portrait.width - side, int(portrait.width * 0.24)))
top = max(0, min(portrait.height - side, int(portrait.height * 0.06)))
portrait = portrait.crop((left, top, left + side, top + side)).resize((250, 250), Image.Resampling.LANCZOS)
mask = Image.new("L", portrait.size, 0)
ImageDraw.Draw(mask).ellipse((0, 0, 249, 249), fill=255)
draw.ellipse((821, 174, 1095, 448), fill=(49, 67, 104, 220), outline=(126, 148, 222, 220), width=3)
image.paste(portrait, (833, 186), mask)
draw = ImageDraw.Draw(image, "RGBA")


def pill(x: int, y: int, label: str, width: int) -> None:
    draw.rounded_rectangle((x, y, x + width, y + 42), radius=11, fill=(18, 31, 51, 242), outline=(78, 96, 135, 190), width=1)
    draw.text((x + 14, y + 11), label, font=font("segoeui", 15), fill=white)


pill(657, 151, "Flutter", 112)
pill(1026, 291, "NestJS", 101)
pill(653, 444, "Unreal Engine", 163)

draw.rounded_rectangle((80, 432, 440, 490), radius=29, fill=(62, 83, 141, 230))
draw.text((106, 451), "4+ YEARS  ·  20+ LIVE PRODUCTS", font=font("segoeuib", 16), fill=white)
draw.text((82, 555), "MAZENX  /  INDEPENDENT STUDIO", font=font("segoeuib", 14), fill=(155, 169, 194, 230))

image.save(ASSETS / "social-preview-v2.jpg", "JPEG", quality=90, optimize=True, progressive=True, subsampling=0)
