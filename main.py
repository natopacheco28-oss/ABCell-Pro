import os
import shutil
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from config.branding import APP_ID, APP_NAME, app_icon_path

from config.settings import ConfigManager
from ui.main_window import MainWindow

from database.db_manager import DatabaseManager


def _carpeta_datos_antigua() -> str:
    """Ubicación anterior de los datos (antes de ser portable)."""
    return os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "ABCell_Gestion_Taller",
    )


def _migrar_datos_antiguos(nueva_carpeta: str):
    """Copia la BD y la config desde la ubicación anterior si existen.

    Así, al pasar a modo portable no se pierde la información que ya
    estaba guardada en LOCALAPPDATA.
    """
    vieja = _carpeta_datos_antigua()
    if os.path.abspath(vieja) == os.path.abspath(nueva_carpeta):
        return
    for nombre in ("abcell_taller.db", "config.json"):
        origen = os.path.join(vieja, nombre)
        destino = os.path.join(nueva_carpeta, nombre)
        if os.path.exists(origen) and not os.path.exists(destino):
            try:
                shutil.copy2(origen, destino)
            except Exception:
                pass


def obtener_carpeta_datos() -> str:
    if getattr(sys, "frozen", False):
        # Modo portable: la carpeta "data" vive junto al ejecutable,
        # para poder mover todo el programa a otra PC sin perder datos.
        base = os.path.join(
            os.path.dirname(os.path.abspath(sys.executable)), "data"
        )
    else:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    try:
        os.makedirs(base, exist_ok=True)
    except OSError:
        # Si la carpeta del ejecutable no se puede escribir (p. ej. está en
        # Archivos de programa), se usa la ubicación anterior como respaldo.
        base = _carpeta_datos_antigua()
        os.makedirs(base, exist_ok=True)
    if getattr(sys, "frozen", False):
        _migrar_datos_antiguos(base)
    return base


def _establecer_identidad_windows():
    # Debe ejecutarse antes de crear QApplication o cualquier ventana.
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            # La aplicación sigue funcionando si Windows no permite asignarlo.
            pass


def main():
    _establecer_identidad_windows()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName("ABCell")
    app.setWindowIcon(QIcon(str(app_icon_path())))

    carpeta_datos = obtener_carpeta_datos()
    config = ConfigManager(os.path.join(carpeta_datos, "config.json"))
    db = DatabaseManager(os.path.join(carpeta_datos, "abcell_taller.db"))
    db.init_db()

    ventana = MainWindow(db, config)
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
