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


def _conexion_esta_cerrada(conn: sqlite3.Connection | None) -> bool:
    if conn is None:
        return True
    try:
        conn.execute("SELECT 1")
        return False
    except sqlite3.ProgrammingError:
        return True


class DatabaseManager:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or _obtener_ruta_bd_por_defecto()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def connect(self) -> sqlite3.Connection:
        if _conexion_esta_cerrada(getattr(self, "conn", None)):
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

    COLUMNAS_ORDENES = {
        "cliente_nombre": "TEXT DEFAULT ''",
        "cliente_tel": "TEXT DEFAULT ''",
        "categoria": "TEXT DEFAULT 'Celulares'",
        "marca": "TEXT DEFAULT ''",
        "modelo": "TEXT DEFAULT ''",
        "color": "TEXT DEFAULT ''",
        "imei": "TEXT DEFAULT ''",
        "pin_pass": "TEXT DEFAULT ''",
        "patron": "TEXT DEFAULT 'Sin patrón'",
        "estado_fisico": "TEXT DEFAULT ''",
        "falla": "TEXT DEFAULT ''",
        "servicio_nombre": "TEXT DEFAULT ''",
        "ubicacion": "TEXT DEFAULT 'Sin asignar'",
        "estatus": "TEXT DEFAULT 'Recibido'",
        "costo_repuesto": "REAL DEFAULT 0.0",
        "costo_total": "REAL DEFAULT 0.0",
        "anticipo": "REAL DEFAULT 0.0",
        "saldo": "REAL DEFAULT 0.0",
        "metodo_pago": "TEXT DEFAULT 'Efectivo'",
        "notas_internas": "TEXT DEFAULT ''",
        "fecha_ingreso": "TEXT DEFAULT ''",
        "fecha_actualizacion": "TEXT DEFAULT ''",
    }

    def _migrar_ordenes(self):
        """Repara bases de datos antiguas para que se puedan guardar órdenes."""
        cols = self._columnas_tabla("ordenes")
        if not cols:
            return

        # Esquema viejo: tenía 'fecha' (NOT NULL) en lugar de 'fecha_ingreso'.
        # SQLite no permite quitar ese NOT NULL con ALTER, así que se reconstruye la tabla.
        if "fecha" in cols and "fecha_ingreso" not in cols:
            cur = self.connect().cursor()
            cur.execute("ALTER TABLE ordenes RENAME TO ordenes_vieja")
            self.conn.commit()
            self._crear_tablas()
            vieja = self._columnas_tabla("ordenes_vieja")
            nuevas = self._columnas_tabla("ordenes")
            comunes = [c for c in vieja if c in nuevas and c != "fecha_ingreso"]
            destino = ", ".join(comunes + ["fecha_ingreso", "fecha_actualizacion"])
            origen = ", ".join(
                comunes
                + [
                    "COALESCE(fecha, datetime('now','localtime'))",
                    "COALESCE(fecha, datetime('now','localtime'))",
                ]
            )
            self.ejecutar(f"INSERT INTO ordenes ({destino}) SELECT {origen} FROM ordenes_vieja")
            self.ejecutar("DROP TABLE ordenes_vieja")
            cols = self._columnas_tabla("ordenes")

        # Esquema intermedio: faltan columnas sueltas.
        for nombre, definicion in self.COLUMNAS_ORDENES.items():
            if nombre not in cols:
                self.ejecutar(f"ALTER TABLE ordenes ADD COLUMN {nombre} {definicion}")

        cols_pg = self._columnas_tabla("pagos_orden")
        if cols_pg and "metodo_pago" not in cols_pg:
            self.ejecutar("ALTER TABLE pagos_orden ADD COLUMN
