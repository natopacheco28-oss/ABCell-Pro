import os
import sqlite3
import sys
from PySide6.QtWidgets import QApplication

from config.settings import ConfigManager
from ui.main_window import MainWindow

from database.db_manager import DatabaseManager


def obtener_carpeta_datos() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ABCell_Gestion_Taller")
    else:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(base, exist_ok=True)
    return base


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ABCell Gestion Taller")

    carpeta_datos = obtener_carpeta_datos()
    config = ConfigManager(os.path.join(carpeta_datos, "config.json"))
    db = DatabaseManager(os.path.join(carpeta_datos, "abcell_taller.db"))
    db.init_db()

    ventana = MainWindow(db, config)
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
