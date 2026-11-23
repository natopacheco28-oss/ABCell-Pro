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

    COLUMNAS_PAGOS = {
        "metodo_pago": "TEXT DEFAULT 'Efectivo'",
    }

    COLUMNAS_WA = {
        "estado": "TEXT DEFAULT 'Abierto en WA'",
    }

    def _migrar_ordenes(self):
        """Repara bases de datos antiguas para que se puedan guardar órdenes."""
        cols = self._columnas_tabla("ordenes")
        if not cols:
            return

        # Esquema viejo: tenía 'fecha' (NOT NULL) en lugar de 'fecha_ingreso'.
        # SQLite no permite quitar ese NOT NULL con ALTER,
        # así que se reconstruye la tabla.
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
            sql = (
                f"INSERT INTO ordenes ({destino}) "
                f"SELECT {origen} FROM ordenes_vieja"
            )
            self.ejecutar(sql)
            self.ejecutar("DROP TABLE ordenes_vieja")
            cols = self._columnas_tabla("ordenes")

        # Esquema intermedio: faltan columnas sueltas.
        self._agregar_columnas("ordenes", self.COLUMNAS_ORDENES)
        self._agregar_columnas("pagos_orden", self.COLUMNAS_PAGOS)

    def _agregar_columnas(self, tabla: str, columnas: dict):
        existentes = self._columnas_tabla(tabla)
        if not existentes:
            return
        for nombre, definicion in columnas.items():
            if nombre not in existentes:
                sql = f"ALTER TABLE {tabla} ADD COLUMN {nombre} {definicion}"
                self.ejecutar(sql)

    def _migrar_columnas(self):
        self._migrar_ordenes()
        self._agregar_columnas("notificaciones_wa", self.COLUMNAS_WA)
        cols_ub = self._columnas_tabla("ubicaciones")
        if cols_ub and "activo" not in cols_ub:
            self.ejecutar(
                "ALTER TABLE ubicaciones ADD COLUMN activo INTEGER DEFAULT 1"
            )
            if "activa" in cols_ub:
                self.ejecutar(
                    "UPDATE ubicaciones SET activo = COALESCE(activa, 1)"
                )

        cols_srv = self._columnas_tabla("servicios_catalogo")
        if cols_srv and "activo" not in cols_srv:
            self.ejecutar(
                "ALTER TABLE servicios_catalogo "
                "ADD COLUMN activo INTEGER DEFAULT 1"
            )
            if "activa" in cols_srv:
                self.ejecutar(
                    "UPDATE servicios_catalogo "
                    "SET activo = COALESCE(activa, 1)"
                )

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
                estado TEXT DEFAULT 'Abierto en WA',
                fecha TEXT NOT NULL
            )
            """
        )

    def _sembrar_datos_iniciales(self):
        existe_ub = self.consultar_uno(
            "SELECT COUNT(*) AS total FROM ubicaciones"
        )
        if not existe_ub or int(existe_ub["total"]) == 0:
            ubicaciones_base = [
                ("Mostrador", "Recepción", "Recepción y entrega rápida"),
                ("Estante A-1", "Estante", "Celulares y tablets"),
                ("Estante B-1", "Estante", "Consolas y controles"),
                ("Gaveta 1", "Gaveta", "Equipos en diagnóstico o refacción"),
            ]
            for nombre, tipo, desc in ubicaciones_base:
                self.ejecutar(
                    "INSERT OR IGNORE INTO ubicaciones "
                    "(nombre, tipo, descripcion, activo) VALUES (?, ?, ?, 1)",
                    (nombre, tipo, desc),
                )

        existe_srv = self.consultar_uno(
            "SELECT COUNT(*) AS total FROM servicios_catalogo"
        )
        if not existe_srv or int(existe_srv["total"]) == 0:
            servicios_base = [
                ("Celulares", "Samsung", "",
                 "Cambio de pantalla / módulo", 950.0),
                ("Celulares", "Apple (iPhone)", "", "Cambio de batería", 650.0),
                ("Celulares", "", "", "Limpieza de centro de carga", 250.0),
                ("Consolas", "PlayStation 4", "",
                 "Mantenimiento y cambio de pasta térmica", 550.0),
                ("Consolas", "Xbox One", "",
                 "Mantenimiento y limpieza interna", 550.0),
            ]
            for cat, marca, modelo, nombre, precio in servicios_base:
                self.ejecutar(
                    """
                    INSERT INTO servicios_catalogo
                    (categoria, marca, modelo, nombre, precio, activo)
                    VALUES (?, ?, ?, ?, ?, 1)
                    """,
                    (cat, marca, modelo, nombre, precio),
                )

    def respaldar(self) -> str:
        """Guarda una copia de la base en la carpeta 'respaldos'."""
        carpeta = os.path.join(
            os.path.dirname(os.path.abspath(self.db_path)), "respaldos"
        )
        os.makedirs(carpeta, exist_ok=True)
        marca = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = os.path.join(carpeta, f"abcell_taller_{marca}.db")
        self.connect().commit()
        copia = sqlite3.connect(destino)
        try:
            self.conn.backup(copia)
        finally:
            copia.close()
        return destino

    def restablecer_ordenes(self):
        """Borra todas las órdenes, pagos y avisos. Folios vuelven a 1."""
        for tabla in ("pagos_orden", "notificaciones_wa", "ordenes"):
            self.ejecutar(f"DELETE FROM {tabla}")
        self.ejecutar(
            "DELETE FROM sqlite_sequence WHERE name IN "
            "('ordenes', 'pagos_orden', 'notificaciones_wa')"
        )

    def restablecer_todo(self):
        """Borra órdenes, catálogo y ubicaciones; vuelve a los datos base."""
        self.restablecer_ordenes()
        self.ejecutar("DELETE FROM servicios_catalogo")
        self.ejecutar("DELETE FROM ubicaciones")
        self.ejecutar(
            "DELETE FROM sqlite_sequence WHERE name IN "
            "('servicios_catalogo', 'ubicaciones')"
        )
        self._sembrar_datos_iniciales()

    def cerrar(self):
        try:
            self.conn.commit()
            self.conn.close()
        except Exception:
            pass
