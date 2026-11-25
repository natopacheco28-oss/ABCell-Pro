"""Identidad del programa, independiente de los datos y el logo del taller."""
from pathlib import Path

APP_NAME = "ABCell Pro"
APP_AUTHOR = "ABCell Profecional"
APP_ID = "ABCell.ABCellPro.Desktop"
ASSET_DIR = Path(__file__).resolve().parent.parent / "ui" / "assets"


def app_icon_path() -> Path:
    return ASSET_DIR / "abcell-pro.ico"


def app_logo_path() -> Path:
    return ASSET_DIR / "abcell-pro.jpg"
