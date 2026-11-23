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

    def connect(self) -> sqlite3.Connection:
        if getattr(self, "conn", None) is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_db(self):
        self.connect()
        self._crear_tablas()
        self._migrar_columnas()
        self._sembrar_datos_iniciales()

    def ejecutar(self, sql: str, params: tuple = ()):
        cur = self.connect().cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def consultar_todos(self, sql: str, params: tuple = ()) -> list[dict]:
        cur = self.connect().cursor()
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]

    def consultar_uno(self, sql: str, params: tuple = ()) -> dict | None:
        cur = self.connect().cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None

    def _columnas_tabla(self, tabla: str) -> set[str]:
        rows = self.consultar_todos(f"PRAGMA table_info({tabla})")
        return {str(r["name"]) for r in rows}

    def _migrar_columnas(self):
        cols_ub = self._columnas_tabla("ubicaciones")
        if cols_ub and "activo" not in cols_ub:
            self.ejecutar("ALTER TABLE ubicaciones ADD COLUMN activo INTEGER DEFAULT 1")
            if "activa" in cols_ub:
                self.ejecutar("UPDATE ubicaciones SET activo = COALESCE(activa, 1)")

        cols_srv = self._columnas_tabla("servicios_catalogo")
        if cols_srv and "activo" not in cols_srv:
            self.ejecutar("ALTER TABLE servicios_catalogo ADD COLUMN activo INTEGER DEFAULT 1")
            if "activa" in cols_srv:
                self.ejecutar("UPDATE servicios_catalogo SET activo = COALESCE(activa, 1)")

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
