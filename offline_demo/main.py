"""Ejecutar: python -m offline_demo.main. Sin importaciones de la app completa."""
import sqlite3
import sys

from PySide6.QtCore import QLockFile
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox
from offline_demo.trial import Trial, TrialBlocked, profile_directory
from offline_demo.store import DemoStore
from offline_demo.window import ASSETS, DemoWindow
from ui.layouts import install_visual_policy
from ui.theme import construir_qss


def main():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ABCell.ABCellPro.Demo")
    app = QApplication(sys.argv)
    app.setApplicationName("ABCell Pro Demo")
    app.setApplicationDisplayName("ABCell Pro Demo")
    app.setOrganizationName("ABCell Profecional")
    install_visual_policy(app)
    app.setStyleSheet(construir_qss("Lima Pro"))
    app.setWindowIcon(QIcon(str(ASSETS / "abcell-pro.ico")))
    folder = profile_directory()
    try:
        folder.mkdir(parents=True, exist_ok=True)
        # Solo una instancia por perfil: evita altas/registros de inicio concurrentes.
        lock = QLockFile(str(folder / "running.lock"))
        if not lock.tryLock(0):
            QMessageBox.information(None, "ABCell Pro Demo", "La demo ya está abierta o no se pudo bloquear su carpeta de datos.")
            return 1
        trial = Trial(folder)
        trial.require_active()
        store = DemoStore(trial)
    except (TrialBlocked, OSError, sqlite3.Error) as exc:
        QMessageBox.warning(None, "ABCell Pro Demo", str(exc))
        return 1
    window = DemoWindow(store)
    window.show()
    result = app.exec()
    if not window._closed:
        store.close()
    lock.unlock()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
