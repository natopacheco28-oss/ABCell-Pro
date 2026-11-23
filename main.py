import os
import sqlite3
import sys
from PySide6.QtWidgets import QApplication

from config.settings import ConfigManager
from ui.main_window import MainWindow

try:
    from database.db_manager import DatabaseManager
except Exception:
    class DatabaseManager:  # type: ignore
        def __init__(self, db_path: str = "abcell_taller.db"):
            self.db_path = db_path
            carpeta = os.path.dirname(os.path.abspath(self.db_path))
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)

        def connect(self) -> sqlite3.Connection:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn

        def init_db(self):
            conn = self.connect()
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, telefono TEXT NOT NULL, correo TEXT DEFAULT '', notas TEXT DEFAULT '', fecha_registro TEXT DEFAULT '')")
            c.execute("CREATE TABLE IF NOT EXISTS ordenes (folio INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, cliente_nombre TEXT NOT NULL, cliente_tel TEXT NOT NULL, categoria TEXT DEFAULT 'Celulares', marca TEXT NOT NULL, modelo TEXT NOT NULL, color TEXT DEFAULT 'N/A', imei TEXT DEFAULT '', pin_pass TEXT DEFAULT '', patron TEXT DEFAULT 'Sin patrón', estado_fisico TEXT DEFAULT 'Sin observaciones', falla TEXT NOT NULL, servicio_nombre TEXT DEFAULT '', costo_repuesto REAL DEFAULT 0.0, costo_total REAL DEFAULT 0.0, anticipo REAL DEFAULT 0.0, saldo REAL DEFAULT 0.0, estatus TEXT DEFAULT 'Recibido', ubicacion TEXT DEFAULT 'Sin asignar', notas_internas TEXT DEFAULT '', fecha_listo TEXT DEFAULT '', fecha_entrega TEXT DEFAULT '', cliente_id INTEGER)")
            c.execute("CREATE TABLE IF NOT EXISTS pagos_orden (id INTEGER PRIMARY KEY AUTOINCREMENT, folio INTEGER NOT NULL, fecha TEXT NOT NULL, tipo TEXT DEFAULT 'Abono parcial', monto REAL NOT NULL, metodo_pago TEXT DEFAULT 'Efectivo', nota TEXT DEFAULT '')")
            c.execute("CREATE TABLE IF NOT EXISTS catalogo_servicios (id INTEGER PRIMARY KEY AUTOINCREMENT, categoria TEXT DEFAULT 'Celulares', marca TEXT DEFAULT '', modelo TEXT DEFAULT '', nombre TEXT NOT NULL, descripcion TEXT DEFAULT '', precio REAL DEFAULT 0.0, tiempo_estimado TEXT DEFAULT '', activo INTEGER DEFAULT 1)")
            c.execute("CREATE TABLE IF NOT EXISTS ubicaciones (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE NOT NULL, tipo TEXT DEFAULT 'General', descripcion TEXT DEFAULT '', activa INTEGER DEFAULT 1)")
            c.execute("CREATE TABLE IF NOT EXISTS notificaciones_wa (id INTEGER PRIMARY KEY AUTOINCREMENT, folio INTEGER, cliente_nombre TEXT DEFAULT '', telefono TEXT DEFAULT '', tipo TEXT DEFAULT '', mensaje TEXT DEFAULT '', fecha TEXT DEFAULT '', estado TEXT DEFAULT 'Abierto en WA')")
            c.execute("INSERT OR IGNORE INTO ubicaciones (nombre, tipo, descripcion, activa) VALUES ('Sin asignar', 'General', 'Ubicación inicial', 1)")
            conn.commit()
            conn.close()


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
