from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "static" / "images"
SIZE = (1200, 720)


def vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(image)
    width, height = size
    for y in range(height):
        mix = y / max(height - 1, 1)
        color = tuple(int(top[i] * (1 - mix) + bottom[i] * mix) for i in range(3))
        draw.line((0, y, width, y), fill=color)
    return image


def add_glow(base: Image.Image, box: tuple[int, int, int, int], color: tuple[int, int, int, int], blur: int) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse(box, fill=color)
    overlay = overlay.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(overlay)


def save_capture_image() -> None:
    img = vertical_gradient(SIZE, (254, 247, 239), (240, 247, 255)).convert("RGBA")
    add_glow(img, (80, 40, 540, 500), (251, 191, 36, 90), 38)
    add_glow(img, (620, 120, 1100, 620), (20, 184, 166, 100), 48)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle((85, 90, 520, 650), radius=34, fill=(255, 251, 246, 255), outline=(229, 211, 189, 255), width=6)
    draw.rounded_rectangle((140, 155, 390, 190), radius=18, fill=(231, 217, 199, 255))
    for y in (235, 290, 345, 400):
        draw.rounded_rectangle((140, y, 340, y + 24), radius=12, fill=(241, 229, 214, 255))
    draw.rounded_rectangle((140, 470, 300, 520), radius=18, fill=(217, 119, 6, 255))

    draw.rounded_rectangle((650, 165, 1085, 445), radius=34, fill=(15, 118, 110, 255))
    draw.rounded_rectangle((705, 225, 1020, 275), radius=22, fill=(255, 255, 255, 70))
    draw.rounded_rectangle((705, 315, 880, 345), radius=15, fill=(255, 255, 255, 85))
    draw.rounded_rectangle((705, 370, 960, 400), radius=15, fill=(255, 255, 255, 60))
    draw.line((770, 500, 840, 570, 980, 430), fill=(255, 250, 245, 255), width=18, joint="curve")
    draw.ellipse((735, 465, 805, 535), fill=(217, 119, 6, 255))
    draw.ellipse((807, 537, 877, 607), fill=(217, 119, 6, 255))
    draw.ellipse((945, 395, 1015, 465), fill=(255, 250, 245, 255))

    img.convert("RGB").save(OUT_DIR / "landing-capture-card.png", quality=95)


def save_analytics_image() -> None:
    img = vertical_gradient(SIZE, (241, 251, 249), (229, 239, 255)).convert("RGBA")
    add_glow(img, (40, 50, 500, 420), (14, 165, 233, 85), 40)
    add_glow(img, (760, 220, 1180, 700), (251, 191, 36, 90), 55)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle((95, 105, 1110, 615), radius=36, fill=(255, 253, 248, 255), outline=(221, 234, 232, 255), width=6)
    draw.rounded_rectangle((150, 150, 385, 190), radius=18, fill=(219, 236, 232, 255))
    draw.rounded_rectangle((150, 220, 295, 248), radius=14, fill=(236, 244, 242, 255))

    chart_points = [(165, 500), (315, 380), (470, 425), (640, 285), (810, 325), (1040, 185)]
    draw.line(chart_points, fill=(15, 118, 110, 255), width=20, joint="curve")
    for x, y in chart_points:
        draw.ellipse((x - 28, y - 28, x + 28, y + 28), fill=(217, 119, 6, 255))

    for x1, y1, x2, y2 in ((190, 535, 350, 570), (390, 535, 560, 570), (610, 535, 760, 570), (810, 535, 1010, 570)):
        draw.rounded_rectangle((x1, y1, x2, y2), radius=16, fill=(238, 232, 250, 255))

    img.convert("RGB").save(OUT_DIR / "landing-analytics-card.png", quality=95)


def save_report_image() -> None:
    img = vertical_gradient(SIZE, (248, 244, 255), (240, 249, 246)).convert("RGBA")
    add_glow(img, (60, 20, 500, 420), (168, 85, 247, 70), 46)
    add_glow(img, (740, 180, 1180, 680), (16, 185, 129, 90), 50)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle((120, 80, 1040, 635), radius=38, fill=(255, 252, 249, 255), outline=(231, 225, 244, 255), width=6)
    draw.rounded_rectangle((180, 145, 420, 185), radius=18, fill=(226, 220, 243, 255))
    row_y = 240
    for _ in range(4):
        draw.rounded_rectangle((180, row_y, 720, row_y + 26), radius=13, fill=(239, 233, 249, 255))
        row_y += 70

    draw.rounded_rectangle((180, 535, 390, 585), radius=18, fill=(217, 119, 6, 255))
    draw.line((745, 555, 835, 470, 915, 500, 1010, 360), fill=(15, 118, 110, 255), width=18, joint="curve")
    for x, y in ((745, 555), (835, 470), (915, 500), (1010, 360)):
        draw.ellipse((x - 24, y - 24, x + 24, y + 24), fill=(15, 118, 110, 255))

    img.convert("RGB").save(OUT_DIR / "landing-report-card.png", quality=95)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    save_capture_image()
    save_analytics_image()
    save_report_image()


if __name__ == "__main__":
    main()
