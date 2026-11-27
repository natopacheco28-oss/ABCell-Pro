"""Identidad del programa, independiente de los datos y el logo del taller."""
import sys
from pathlib import Path

APP_NAME = "ABCell Pro"
APP_AUTHOR = "ABCell Profecional"
APP_ID = "ABCell.Pro.1"


def resource_path(relativa: str) -> Path:
    """Busca recursos tanto en desarrollo como en paquetes PyInstaller.

    En onefile, _MEIPASS es el directorio temporal de extracción. En onedir
    moderno es normalmente _internal; también se admite un recurso situado
    directamente junto al ejecutable, como en distribuciones onedir antiguas.
    """
    if getattr(sys, "frozen", False):
        ejecutable = Path(sys.executable).resolve().parent
        if hasattr(sys, "_MEIPASS"):
            recurso = Path(sys._MEIPASS) / relativa
            if recurso.exists():
                return recurso
        return ejecutable / relativa
    return Path(__file__).resolve().parent.parent / relativa


def app_icon_path() -> Path:
    return resource_path("ui/assets/abcell-pro.ico")


def app_logo_path() -> Path:
    return resource_path("ui/assets/abcell-pro.jpg")
