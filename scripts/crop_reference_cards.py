from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(r"C:\Users\ADEMOLA\Downloads\d54868798ce26014a2d5edac9fa11eac.webp")
OUT_DIR = ROOT / "static" / "images"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(SOURCE).convert("RGB")

    crops = {
        "landing-capture-card.png": (160, 466, 688, 784),
        "landing-analytics-card.png": (694, 467, 1001, 783),
        "landing-report-card.png": (1080, 309, 1450, 622),
    }

    for filename, box in crops.items():
        cropped = image.crop(box)
        cropped.save(OUT_DIR / filename, quality=95)


if __name__ == "__main__":
    main()
