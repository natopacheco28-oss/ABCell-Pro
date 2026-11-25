"""Genera un ICO Windows multirresolución a partir del logo real adjuntado."""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ui" / "assets" / "abcell-pro.jpg"
DESTINATION = ROOT / "ui" / "assets" / "abcell-pro.ico"
SIZES = [(size, size) for size in (16, 24, 32, 48, 64, 128, 256)]


def prepare_icon():
    with Image.open(SOURCE) as source:
        image = ImageOps.exif_transpose(source).convert("RGBA")
        # Contain, no crop: conservar completo el emblema y el texto del usuario.
        image = ImageOps.pad(image, (256, 256), method=Image.Resampling.LANCZOS,
                             color=(0, 0, 0, 0))
        image.save(DESTINATION, format="ICO", sizes=SIZES)
    return DESTINATION


if __name__ == "__main__":
    print(prepare_icon())
