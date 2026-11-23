import os
import sqlite3
import sys
from datetime import datetime


def _obtener_ruta_bd_por_defecto(nombre_archivo: str = "taller_abcell.db") -> str:
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, nombre_archivo)


class DatabaseManager:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or _obtener_ruta_bd_por_defecto()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        if getattr(self, "conn", None) is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        self._crear_tablas()
        self._sembrar_datos_iniciales()

    def ejecutar(self, sql: str, params: tuple = ()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def consultar_todos(self, sql: str, params: tuple = ()) -> list[dict]:
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]

    def consultar_uno(self, sql: str, params: tuple = ()) -> dict | None:
        cur = self.conn.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None

    def _crear_tablas(self):
        self.ejecutar(
            """
            CREATE TABLE IF NOT EXISTS ordenes (
                folio INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_nombre TEXT NOT NULL,
                cliente_tel TEXT NOT NULL,
                categoria TEXT DEFAULT 'Celulares',
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                color TEXT DEFAULT '',
                imei TEXT DEFAULT '',
                pin_pass TEXT DEFAULT '',
                patron TEXT DEFAULT 'Sin patrón',
                estado_fisico TEXT DEFAULT '',
                falla TEXT NOT NULL,
                servicio_nombre TEXT DEFAULT '',
                ubicacion TEXT DEFAULT 'Sin asignar',
                estatus TEXT DEFAULT 'Recibido',
                costo_repuesto REAL DEFAULT 0.0,
                costo_total REAL DEFAULT 0.0,
                anticipo REAL DEFAULT 0.0,
                saldo REAL DEFAULT 0.0,
                metodo_pago TEXT DEFAULT 'Efectivo',
                notas_internas TEXT DEFAULT '',
                fecha_ingreso TEXT NOT NULL,
                fecha_actualizacion TEXT NOT NULL
            )
            """
        )

        self.ejecutar(
            """
            CREATE TABLE IF NOT EXISTS pagos_orden (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folio INTEGER NOT NULL,
                monto REAL NOT NULL,
                metodo_pago TEXT DEFAULT 'Efectivo',
                fecha TEXT NOT NULL,
                FOREIGN KEY (folio) REFERENCES ordenes (folio)
            )
            """
        )

        self.ejecutar(
            """
            CREATE TABLE IF NOT EXISTS servicios_catalogo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT DEFAULT 'Celulares',
                marca TEXT DEFAULT '',
                modelo TEXT DEFAULT '',
                nombre TEXT NOT NULL,
                precio REAL DEFAULT 0.0,
                activo INTEGER DEFAULT 1
            )
            """
        )

        self.ejecutar(
            """
            CREATE TABLE IF NOT EXISTS ubicaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                tipo TEXT DEFAULT 'General',
                descripcion TEXT DEFAULT '',
                activo INTEGER DEFAULT 1
            )
            """
        )

        self.ejecutar(
            """
            CREATE TABLE IF NOT EXISTS notificaciones_wa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folio INTEGER DEFAULT 0,
                cliente_nombre TEXT DEFAULT '',
                telefono TEXT DEFAULT '',
                tipo TEXT DEFAULT '',
                mensaje TEXT DEFAULT '',
                fecha TEXT NOT NULL
            )
            """
        )

    def _sembrar_datos_iniciales(self):
        existe_ub = self.consultar_uno("SELECT COUNT(*) AS total FROM ubicaciones")
        if not existe_ub or int(existe_ub["total"]) == 0:
            ubicaciones_base = [
                ("Mostrador", "Recepción", "Recepción y entrega rápida"),
                ("Estante A-1", "Estante", "Celulares y tablets"),
                ("Estante B-1", "Estante", "Consolas y controles"),
                ("Gaveta 1", "Gaveta", "Equipos en diagnóstico o refacción"),
            ]
            for nombre, tipo, desc in ubicaciones_base:
                self.ejecutar(
                    "INSERT OR IGNORE INTO ubicaciones (nombre, tipo, descripcion, activo) VALUES (?, ?, ?, 1)",
                    (nombre, tipo, desc),
                )

        existe_srv = self.consultar_uno("SELECT COUNT(*) AS total FROM servicios_catalogo")
        if not existe_srv or int(existe_srv["total"]) == 0:
            servicios_base = [
                ("Celulares", "Samsung", "", "Cambio de pantalla / módulo", 950.0),
                ("Celulares", "Apple (iPhone)", "", "Cambio de batería", 650.0),
                ("Celulares", "", "", "Limpieza de centro de carga", 250.0),
                ("Consolas", "PlayStation 4", "", "Mantenimiento y cambio de pasta térmica", 550.0),
                ("Consolas", "Xbox One", "", "Mantenimiento y limpieza interna", 550.0),
            ]
            for cat, marca, modelo, nombre, precio in servicios_base:
                self.ejecutar(
                    """
                    INSERT INTO servicios_catalogo (categoria, marca, modelo, nombre, precio, activo)
                    VALUES (?, ?, ?, ?, ?, 1)
                    """,
                    (cat, marca, modelo, nombre, precio),
                )

    def cerrar(self):
        try:
            self.conn.commit()
            self.conn.close()
        except Exception:
            pass
```[cite: 4]

---

### 2. `main.py` (completo)

```python
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
```[cite: 5]
