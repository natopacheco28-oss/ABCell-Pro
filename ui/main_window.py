import os
import webbrowser
from datetime import datetime
from PySide6.QtCore import QPoint, QPointF, QSize, Qt, Signal, QUrl
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QIcon,
    QKeySequence,
    QPainter,
    QPen,
    QPixmap,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.layouts import (
    ActionButton, AdaptiveDialog, ContentCombo, FlowLayout, MultilineInput, ReadableTable,
    install_visual_policy, scroll_page,
)

from config.branding import APP_NAME, app_icon_path, app_logo_path
from config.settings import ConfigManager
from database.db_manager import DatabaseManager
from integrations.printer_58mm import (
    generar_texto_ticket,
    imprimir_ticket_58mm,
    imprimir_ticket_prueba,
    logo_color_pil,
    logo_pil,
    obtener_estado_impresora,
)

try:
    from integrations.ticket_image import generar_imagen_ticket
except Exception:

    def generar_imagen_ticket(orden, config, ruta_destino):  # type: ignore
        return None
from ui.icons import icono
from ui.theme import (
    PALETAS_TEMAS,
    GestorTemas,
    construir_qss,
    es_tema_oscuro,
    nombre_tema,
    TEMAS_ORDEN,
    TEMA_POR_DEFECTO,
)

CATEGORIAS_INVENTARIO = [
    "Refacciones",
    "Pantallas",
    "Baterías",
    "Centros de carga",
    "Accesorios",
    "Micas y Fundas",
    "Cables y Cargadores",
    "Consolas",
    "Consumibles",
    "Otros",
]

GARANTIA_EJEMPLO = (
    "Garantia de 30 dias en la reparacion y en la refaccion instalada, "
    "contados desde la fecha de entrega.\n"
    "La garantia no cubre golpes, caidas, humedad, pantalla estrellada, "
    "sellos rotos o equipos revisados por otro taller.\n"
    "Para hacer valida la garantia es necesario presentar esta nota.\n"
    "Equipos no recogidos despues de 30 dias del aviso no generan "
    "responsabilidad para el taller."
)

try:
    from core.catalog_data import (
        CATEGORIAS_EQUIPO,
        ESTATUS_ORDEN,
        METODOS_PAGO,
        SUBCATEGORIAS_POR_CATEGORIA,
    )
except Exception:
    CATEGORIAS_EQUIPO = [
        "Celulares",
        "Consolas",
        "Tablets",
        "Laptops",
        "Smartwatches",
        "Accesorios",
        "Otros",
    ]
    SUBCATEGORIAS_POR_CATEGORIA = {
        "Celulares": ["Samsung", "Apple (iPhone)", "Xiaomi / Redmi", "Motorola", "Otra marca"],
        "Consolas": [
            "PlayStation 5",
            "PlayStation 4",
            "Xbox Series X|S",
            "Xbox One",
            "Nintendo Switch",
            "Otra consola",
        ],
        "Tablets": ["Apple (iPad)", "Samsung Galaxy Tab", "Lenovo Tab", "Otra marca"],
        "Laptops": ["HP", "Lenovo", "Dell", "ASUS", "Apple (MacBook)", "Otra marca"],
        "Smartwatches": ["Apple Watch", "Samsung Galaxy Watch", "Otra marca"],
        "Accesorios": ["Cargadores y cables", "Audífonos / TWS", "Controles", "Otro accesorio"],
        "Otros": ["Otro equipo"],
    }
    ESTATUS_ORDEN = [
        "Recibido",
        "En diagnóstico",
        "Esperando refacción",
        "En reparación",
        "Listo para entregar",
        "Entregado",
        "Cancelado",
    ]
    METODOS_PAGO = ["Efectivo", "Transferencia", "Tarjeta", "Depósito"]

try:
    from services.workshop_service import WorkshopService
except Exception:
    class WorkshopService:  # type: ignore
        def __init__(self, db, config):
            self.db = db
            self.config = config

        def listar_ordenes(self, *args, **kwargs):
            return []

        def listar_clientes(self, *args, **kwargs):
            return []

        def listar_servicios(self, *args, **kwargs):
            return []

        def listar_ubicaciones(self, *args, **kwargs):
            return []

        def obtener_metricas_dashboard(self, *args, **kwargs):
            return {
                "activas": 0,
                "por_entregar": 0,
                "guardados_7": 0,
                "anticipos_totales": 0.0,
                "saldos_pendientes": 0.0,
                "lista_por_entregar": [],
                "actividad_reciente": [],
            }

        def generar_reporte_financiero(self, *args, **kwargs):
            return {
                "ingresos_diarios": 0.0,
                "ingresos_mensuales": 0.0,
                "saldos_pendientes": 0.0,
                "ganancia_neta_mes": 0.0,
                "por_categoria": {},
            }

        def crear_orden(self, datos):
            return 1

        def obtener_orden(self, folio):
            return None

        def registrar_pago(self, *args, **kwargs):
            return None

        def actualizar_orden_detalle(self, *args, **kwargs):
            return None

        def guardar_servicio(self, *args, **kwargs):
            return 1

        def guardar_ubicacion(self, *args, **kwargs):
            return None

        def eliminar_orden(self, *args, **kwargs):
            return False

        def actualizar_orden_datos(self, *args, **kwargs):
            return False

        def actualizar_servicio(self, *args, **kwargs):
            return False

        def eliminar_servicio(self, *args, **kwargs):
            return False

        def actualizar_ubicacion(self, *args, **kwargs):
            return False

        def eliminar_ubicacion(self, *args, **kwargs):
            return False

        def listar_inventario(self, *args, **kwargs):
            return []

        def obtener_producto_inventario(self, *args, **kwargs):
            return None

        def guardar_producto_inventario(self, *args, **kwargs):
            return 1

        def actualizar_producto_inventario(self, *args, **kwargs):
            return False

        def ajustar_stock_inventario(self, *args, **kwargs):
            return None

        def eliminar_producto_inventario(self, *args, **kwargs):
            return False

        def obtener_resumen_inventario(self, *args, **kwargs):
            return {
                "total_productos": 0,
                "total_unidades": 0,
                "stock_bajo": 0,
                "agotados": 0,
                "valor_costo": 0.0,
                "valor_venta": 0.0,
                "ganancia_potencial": 0.0,
            }

try:
    from integrations.adb_manager import ADBManager, PROVEEDORES_DNS
except Exception:
    PROVEEDORES_DNS = [
        {
            "id": "adguard",
            "nombre": "AdGuard DNS — Bloquea anuncios y pop-ups",
            "hostname": "dns.adguard-dns.com",
            "descripcion": "Bloquea anuncios y rastreadores.",
        }
    ]

    class ADBManager:  # type: ignore
        def __init__(self, base_data_dir="", custom_adb_path=""):
            self.base_data_dir = base_data_dir
            self.custom_adb_path = custom_adb_path

        def establecer_ruta_personalizada(self, ruta):
            self.custom_adb_path = ruta

        def resolver_ruta_adb(self):
            return False, ""

        def listar_dispositivos(self):
            return {
                "adb_ok": False,
                "ruta_adb": "",
                "dispositivos": [],
                "mensaje": "Módulo ADB no disponible.",
            }

        def reiniciar_servidor(self):
            return False, "Módulo ADB no disponible."

        def diagnosticar_equipo(self, serial):
            return {"ok": False, "error": "Módulo ADB no disponible."}

        def capturar_pantalla(self, serial, ruta):
            return False, "Módulo ADB no disponible."

        def reiniciar_equipo(self, serial, modo=""):
            return False, "Módulo ADB no disponible."

        def escanear_malware(self, serial):
            return {"ok": False, "error": "Módulo ADB no disponible.", "apps": []}

        def detectar_app_en_pantalla(self, serial):
            return {"ok": False, "error": "Módulo ADB no disponible."}

        def desinstalar_paquete(self, serial, package):
            return False, "Módulo ADB no disponible."

        def desactivar_paquete(self, serial, package):
            return False, "Módulo ADB no disponible."

        def revocar_superposicion(self, serial, package):
            return False, "Módulo ADB no disponible."

        def limpiar_spam_navegador(self, serial, package="com.android.chrome"):
            return False, "Módulo ADB no disponible."

        def obtener_estado_dns(self, serial):
            return {"ok": False, "modo": "", "servidor": "", "descripcion_corta": "No disponible"}

        def anclar_dns(self, serial, servidor_dns):
            return False, "Módulo ADB no disponible."

        def restaurar_dns_automatico(self, serial):
            return False, "Módulo ADB no disponible."

        def desactivar_dns_privado(self, serial):
            return False, "Módulo ADB no disponible."

        def probar_conectividad_dns(self, serial):
            return False, "Módulo ADB no disponible."

try:
    from integrations.whatsapp_center import WhatsAppCenter
except Exception:
    class WhatsAppCenter:  # type: ignore
        def __init__(self, db, config):
            self.db = db
            self.config = config

        def construir_mensaje(self, tipo, orden):
            return ""

        def generar_url_wa(self, telefono, mensaje):
            return "https://wa.me/"

        def registrar_notificacion(self, *args, **kwargs):
            return None

        def listar_notificaciones(self, *args, **kwargs):
            return []


class PatronCanvasWidget(QWidget):
    """Cuadrícula interactiva de 3x3 puntos para dibujar el patrón de desbloqueo a mano."""

    patron_cambiado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(210, 210)
        self.setMouseTracking(True)
        self.dibujando = False
        self.secuencia: list[int] = []
        self.pos_actual: QPointF | None = None
        self.puntos: list[tuple[int, QPointF]] = []
        self._calcular_puntos()

    def _calcular_puntos(self):
        self.puntos.clear()
        margen = 36.0
        paso = (self.width() - 2 * margen) / 2.0
        idx = 1
        for fila in range(3):
            for col in range(3):
                x = margen + col * paso
                y = margen + fila * paso
                self.puntos.append((idx, QPointF(x, y)))
                idx += 1

    def limpiar_patron(self):
        self.dibujando = False
        self.secuencia.clear()
        self.pos_actual = None
        self.update()
        self.patron_cambiado.emit("Sin patrón")

    def obtener_texto_patron(self) -> str:
        if not self.secuencia:
            return "Sin patrón"
        return " -> ".join(str(n) for n in self.secuencia)

    def establecer_patron_texto(self, texto: str):
        self.secuencia.clear()
        if texto and "->" in texto:
            for parte in texto.split("->"):
                limpio = parte.strip()
                if limpio.isdigit():
                    num = int(limpio)
                    if 1 <= num <= 9 and num not in self.secuencia:
                        self.secuencia.append(num)
        self.update()
        self.patron_cambiado.emit(self.obtener_texto_patron())

    def _punto_cercano(self, pos: QPointF, radio: float = 24.0) -> int | None:
        for num, pt in self.puntos:
            dx = pos.x() - pt.x()
            dy = pos.y() - pt.y()
            if (dx * dx + dy * dy) <= radio * radio:
                return num
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position()
            self.dibujando = True
            self.secuencia.clear()
            self.pos_actual = pos
            num = self._punto_cercano(pos)
            if num is not None:
                self.secuencia.append(num)
            self.update()
            self.patron_cambiado.emit(self.obtener_texto_patron())

    def mouseMoveEvent(self, event):
        if not self.dibujando:
            return
        pos = event.position()
        self.pos_actual = pos
        num = self._punto_cercano(pos)
        if num is not None and num not in self.secuencia:
            self.secuencia.append(num)
            self.patron_cambiado.emit(self.obtener_texto_patron())
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dibujando:
            self.dibujando = False
            self.pos_actual = None
            self.update()
            self.patron_cambiado.emit(self.obtener_texto_patron())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(QColor("#52657b"), 1.5))
        painter.setBrush(QColor("#0f1826"))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)

        mapa = {num: pt for num, pt in self.puntos}

        if len(self.secuencia) >= 2:
            pen_linea = QPen(QColor("#c5f467"), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_linea)
            for i in range(len(self.secuencia) - 1):
                p1 = mapa[self.secuencia[i]]
                p2 = mapa[self.secuencia[i + 1]]
                painter.drawLine(p1, p2)

        if self.dibujando and self.secuencia and self.pos_actual is not None:
            ultimo_pt = mapa[self.secuencia[-1]]
            painter.setPen(QPen(QColor("#d7ff8a"), 2.5, Qt.DashLine, Qt.RoundCap))
            painter.drawLine(ultimo_pt, self.pos_actual)

        for num, pt in self.puntos:
            seleccionado = num in self.secuencia
            if seleccionado:
                painter.setPen(QPen(QColor("#c5f467"), 2))
                painter.setBrush(QColor("#253623"))
                painter.drawEllipse(pt, 16, 16)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor("#c5f467"))
                painter.drawEllipse(pt, 10, 10)

                painter.setPen(QColor("#ffffff"))
                painter.setFont(self.font())
                painter.drawText(
                    int(pt.x()) - 10, int(pt.y()) - 10, 20, 20, Qt.AlignCenter, str(num)
                )
            else:
                painter.setPen(QPen(QColor("#94a3b8"), 2))
                painter.setBrush(QColor("#ffffff"))
                painter.drawEllipse(pt, 11, 11)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor("#64748b"))
                painter.drawEllipse(pt, 4, 4)


def _make_metric_card(titulo: str, valor: str, subtitulo: str):
    card = QFrame()
    card.setObjectName("Card")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 12, 16, 12)
    lay.setSpacing(3)
    lbl_t = QLabel(titulo)
    lbl_t.setObjectName("CardSub")
    lbl_v = QLabel(valor)
    lbl_v.setObjectName("MetricValue")
    lbl_s = QLabel(subtitulo)
    lbl_s.setObjectName("CardSub")
    lay.addWidget(lbl_t)
    lay.addWidget(lbl_v)
    lay.addWidget(lbl_s)
    return card, lbl_v, lbl_s


def _configurar_tabla(tabla: QTableWidget, stretch_col: int = -1):
    tabla.setAlternatingRowColors(True)
    tabla.setSelectionBehavior(QTableWidget.SelectRows)
    tabla.setEditTriggers(QTableWidget.NoEditTriggers)
    tabla.verticalHeader().setVisible(False)
    tabla.verticalHeader().setDefaultSectionSize(40)
    tabla.setShowGrid(False)
    header = tabla.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Interactive)
    header.setStretchLastSection(False)
    if 0 <= stretch_col < tabla.columnCount():
        header.setSectionResizeMode(stretch_col, QHeaderView.Interactive)


def _tarjeta(titulo: str = "", subtitulo: str = "", margenes=(12, 10, 12, 10)) -> tuple:
    """Crea una tarjeta con borde finito, esquinas redondeadas y un título.

    Devuelve ``(frame, layout)`` para agregar contenido con relleno amplio.
    """
    card = QFrame()
    card.setObjectName("Card")
    lay = QVBoxLayout(card)
    margen_l, margen_t, margen_r, margen_b = margenes
    lay.setContentsMargins(margen_l, margen_t, margen_r, margen_b)
    lay.setSpacing(8)
    if titulo:
        lay.addWidget(_etiqueta(titulo, "CardTitle"))
    if subtitulo:
        lay.addWidget(_etiqueta(subtitulo, "CardSub"))
    return card, lay


def _etiqueta(texto: str, object_name: str) -> QLabel:
    etiqueta = QLabel(texto)
    etiqueta.setObjectName(object_name)
    return etiqueta


def _campo_filtro(titulo: str, campo: QWidget) -> QWidget:
    """Etiqueta y control son una unidad: nunca quedan en líneas diferentes."""
    contenedor = QWidget()
    layout = QVBoxLayout(contenedor)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addWidget(_etiqueta(titulo, "CardSub"))
    layout.addWidget(campo)
    return contenedor


def _fila(espacio: int = 10) -> QHBoxLayout:
    """Fila horizontal con separación uniforme entre controles."""
    fila = FlowLayout()
    fila.setSpacing(espacio)
    fila.setContentsMargins(0, 0, 0, 0)
    return fila


def _columna(espacio: int = 12) -> QVBoxLayout:
    columna = QVBoxLayout()
    columna.setSpacing(espacio)
    columna.setContentsMargins(0, 0, 0, 0)
    return columna


class MainWindow(QMainWindow):
    def __init__(self, db: DatabaseManager, config: ConfigManager):
        super().__init__()
        self.db = db
        self.config = config
        self.service = WorkshopService(db, config)
        self.wa = WhatsAppCenter(db, config)
        carpeta_datos = os.path.dirname(os.path.abspath(db.db_path))
        self.adb = ADBManager(
            carpeta_datos,
            str(config.get("android", "ruta_adb", "") or ""),
        )
        self.inventario_desbloqueado: bool = False
        self._ultimo_diag_adb: dict | None = None
        self._apps_malware_cache: list[dict] = []
        self.nav_buttons: list[QPushButton] = []
        self.stage_buttons: list[QPushButton] = []
        self.etapa_filtro: str = "Todas"

        self.atajo_modo_maestro = QShortcut(QKeySequence("Ctrl+P"), self)
        self.atajo_modo_maestro.activated.connect(self._abrir_modo_maestro)

        nombre_negocio = self.config.get("identidad", "nombre_establecimiento", "ABCell")
        self.setWindowTitle(f"{APP_NAME} — {nombre_negocio} — Taller")
        self.resize(1280, 760)
        self.setMinimumSize(900, 600)
        install_visual_policy(QApplication.instance())
        # Aplicar la fuente antes de medir mínimos (importante en Windows/HiDPI).
        QApplication.instance().setStyleSheet(self._gestor_temas().qss())

        self._build_ui()
        self._aplicar_icono_abcell()
        self.aplicar_tema()
        self.refrescar_todo()

    def _obtener_pixmap_abcell(self) -> QPixmap | None:
        marca = QPixmap(str(app_logo_path()))
        if not marca.isNull():
            return marca
        pil_img = logo_color_pil(self.config) or logo_pil(self.config)
        if pil_img is not None:
            tmp_path = os.path.join(
                os.path.dirname(os.path.abspath(self.db.db_path)), "_tmp_logo_ui.png"
            )
            pil_img.save(tmp_path)
            pm = QPixmap(tmp_path)
            if not pm.isNull():
                return pm

        for candidato in (
            "logo.ico",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo.ico"),
        ):
            if os.path.exists(candidato):
                pm = QPixmap(candidato)
                if not pm.isNull():
                    return pm
        return None

    def _aplicar_icono_abcell(self):
        # La marca del programa no depende del logo personalizado de los tickets.
        self.setWindowIcon(QIcon(str(app_icon_path())))

    # --- Gestor de temas (centralizado en ui.theme) ---
    def _gestor_temas(self) -> GestorTemas:
        if getattr(self, "_gestor", None) is None:
            self._gestor = GestorTemas(self.config)
        return self._gestor

    def _tema_actual(self) -> str:
        return self._gestor_temas().actual()

    def _es_tema_claro(self) -> bool:
        return not self._gestor_temas().es_oscuro()

    def _paleta_actual(self) -> dict:
        return PALETAS_TEMAS[nombre_tema(self._tema_actual())]

    def _color_icono(self, object_name: str, jerarquia: str, activo: bool = False) -> str:
        """Color que debe usar un icono según la jerarquía del botón.

        Los iconos toman el color del texto/fondo del botón para integrarse
        con el tema activo (directriz: iconografía monocromática coherente).
        """
        p = self._paleta_actual()
        if object_name == "WarningBtn":
            return p["warning_fg"]
        if object_name in ("DangerBtn", "AccDangerBtn"):
            return p["danger_fg"]
        if object_name == "PrimaryBtn":
            return p["primary_fg"]
        if object_name == "DangerBtn":
            return p["danger_fg"]
        if object_name == "SecondaryBtn":
            return p["secondary_fg"]
        if object_name == "NavBtn":
            return p["nav_active_fg"] if activo else p["nav_fg"]
        if object_name in ("StageTab",):
            return p["stage_active"] if activo else p["stage_fg"]
        if object_name in ("IconBtn", "GearBtn", "NavBtn"):
            return p["icon"]
        return p["btn_fg"]

    def _boton(
        self,
        texto: str = "",
        icono_nombre: str = "",
        jerarquia: str = "secundario",
        object_name: str = "",
        tooltip: str = "",
        icon_size: int = 16,
    ) -> QPushButton:
        """Crea un botón moderno con icono vectorial a la izquierda + texto.

        ``jerarquia``: ``"principal"``, ``"secundario"`` o ``"critico"``.
        El icono se colorea según la jerarquía y se re-adapta al cambiar de
        tema (ver ``_actualizar_iconos_botones``).
        """
        if not object_name:
            object_name = {
                "principal": "PrimaryBtn",
                "secundario": "SecondaryBtn",
                "critico": "DangerBtn",
            }.get(jerarquia, "SecondaryBtn")
        boton = ActionButton(texto)
        boton.setObjectName(object_name)
        if tooltip:
            boton.setToolTip(tooltip)
        if icono_nombre:
            color = self._color_icono(object_name, jerarquia)
            boton.setIcon(icono(icono_nombre, color, icon_size))
            boton.setIconSize(QSize(icon_size, icon_size))
            boton.setProperty("_icono_nombre", icono_nombre)
            boton.setProperty("_icono_jerarquia", jerarquia)
        return boton

    def _boton_icono(self, icono_nombre: str, object_name: str = "IconBtn", tooltip: str = "", tamano: int = 20) -> QPushButton:
        boton = ActionButton()
        boton.setObjectName(object_name)
        if tooltip:
            boton.setToolTip(tooltip)
        color = self._color_icono(object_name, "secundario")
        boton.setIcon(icono(icono_nombre, color, tamano))
        boton.setIconSize(QSize(tamano, tamano))
        boton.setProperty("_icono_nombre", icono_nombre)
        boton.setProperty("_icono_jerarquia", "icono")
        boton.setProperty("_icono_objeto", object_name)
        return boton

    def _actualizar_iconos_botones(self):
        """Recolorea los iconos de todos los botones según el tema activo."""
        for boton in self.findChildren(QPushButton):
            nombre = boton.property("_icono_nombre")
            if not nombre:
                continue
            object_name = boton.objectName()
            activo = bool(boton.property("active") is True) or (object_name == "NavBtn" and boton.property("active") is True)
            jerarquia = boton.property("_icono_jerarquia") or "secundario"
            color = self._color_icono(object_name, jerarquia, activo=activo)
            tamano = boton.iconSize().width() or 18
            boton.setIcon(icono(nombre, color, tamano))

    def aplicar_tema(self):
        g = self._gestor_temas()
        QApplication.instance().setStyleSheet(g.qss())
        self._actualizar_iconos_botones()
        if hasattr(self, "lbl_tema_actual"):
            self.lbl_tema_actual.setText(f"Tema: {g.actual()}")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(228)
        sidebar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.sidebar = sidebar
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(12, 16, 12, 12)
        sb_lay.setSpacing(6)

        # Una fila simple: FlowLayout tiene un ancho ideal de 320 px para
        # formularios, que aquí ensanchaba innecesariamente toda la barra.
        brand_row = QHBoxLayout()
        brand_row.setSpacing(8)
        self.lbl_logo_sidebar = QLabel()
        self.lbl_logo_sidebar.setFixedSize(44, 44)
        self.lbl_logo_sidebar.setAlignment(Qt.AlignCenter)
        self._cargar_logo_widget(self.lbl_logo_sidebar, 42)

        self.lbl_brand_sidebar = QLabel(APP_NAME)
        self.lbl_brand_sidebar.setObjectName("BrandTitle")
        self.lbl_brand_sidebar.setWordWrap(True)
        brand_row.addWidget(self.lbl_logo_sidebar)
        brand_row.addWidget(self.lbl_brand_sidebar, 1)
        sb_lay.addLayout(brand_row)

        self.lbl_sidebar_fecha = QLabel(datetime.now().strftime("%d/%m/%Y"))
        self.lbl_sidebar_fecha.setObjectName("CardSub")
        sb_lay.addWidget(self.lbl_sidebar_fecha)

        sb_lay.addSpacing(16)

        secciones = [
            ("Órdenes de trabajo", "orden", 0),
            ("Nueva orden", "nueva-orden", 1),
            ("Inventario", "inventario", 2),
            ("Catálogo y Ubicaciones", "catalogo", 3),
            ("Estadísticas y Caja", "estadisticas", 4),
            ("Utilidades Android", "android", 5),
            ("Configuración de taller", "configuracion", 6),
        ]
        for texto, icono_nombre, idx in secciones:
            btn = self._boton(texto, icono_nombre, jerarquia="secundario", object_name="NavBtn")
            btn.setMinimumHeight(38)
            btn.clicked.connect(lambda checked=False, i=idx: self.ir_a_seccion(i))
            sb_lay.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_lay.addStretch(1)

        body.addWidget(sidebar)

        self.stack = QStackedWidget()
        body.addWidget(self.stack, 1)

        self.stack.addWidget(scroll_page(self._build_taller_ordenes_tab()))
        self.stack.addWidget(scroll_page(self._build_nueva_orden_tab()))
        self.stack.addWidget(scroll_page(self._build_inventario_tab()))
        self.stack.addWidget(scroll_page(self._build_catalogo_ubicaciones_tab()))
        self.stack.addWidget(scroll_page(self._build_reportes_tab()))
        self.stack.addWidget(scroll_page(self._build_utilidades_android_tab()))
        self.stack.addWidget(scroll_page(self._build_config_tab()))

        outer.addLayout(body, 1)
        self.ir_a_seccion(0)

    def _cargar_logo_widget(self, label: QLabel, tam: int):
        pm = self._obtener_pixmap_abcell()
        if pm is None or pm.isNull():
            label.setText("AB")
            label.setStyleSheet(
                "background-color: #253623; color: #c5f467; border-radius: 10px; font-weight: 800; font-size: 13px;"
            )
            return
        label.setStyleSheet("background-color: transparent;")
        label.setPixmap(pm.scaled(tam, tam, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def ir_a_seccion(self, indice: int):
        self.stack.setCurrentIndex(indice)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", i == indice)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._actualizar_iconos_botones()
        self.refrescar_todo()

    def _mostrar_todas_las_ordenes(self):
        self.etapa_filtro = "Todas"
        for btn in self.stage_buttons:
            btn.setProperty("active", btn.text() == "Todas")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if hasattr(self, "txt_buscar_orden"):
            self.txt_buscar_orden.blockSignals(True)
            self.txt_buscar_orden.clear()
            self.txt_buscar_orden.blockSignals(False)

        if hasattr(self, "cmb_filtro_estatus"):
            self.cmb_filtro_estatus.blockSignals(True)
            self.cmb_filtro_estatus.setCurrentText("Todos")
            self.cmb_filtro_estatus.blockSignals(False)

        if hasattr(self, "cmb_filtro_cat"):
            self.cmb_filtro_cat.blockSignals(True)
            self.cmb_filtro_cat.setCurrentText("Todas")
            self.cmb_filtro_cat.blockSignals(False)

    # ------------------------------------------
    # 0. TALLER Y ÓRDENES
    # ------------------------------------------
    def _build_taller_ordenes_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        stage_bar = FlowLayout()
        stage_bar.setSpacing(8)
        etapas = [
            ("Todas", "Todas"),
            ("Entrada", "Entrada"),
            ("Reparación", "Reparación"),
            ("Salida", "Salida"),
        ]
        self.stage_buttons.clear()
        for etiqueta, clave in etapas:
            b = ActionButton(etiqueta)
            b.setObjectName("StageTab")
            b.setProperty("active", clave == self.etapa_filtro)
            b.clicked.connect(lambda checked=False, k=clave: self._seleccionar_etapa(k))
            stage_bar.addWidget(b)
            self.stage_buttons.append(b)
        stage_bar.addStretch()
        lay.addLayout(stage_bar)

        filtr_card = QFrame()
        filtr_card.setObjectName("Card")
        fc_lay = QVBoxLayout(filtr_card)
        fc_lay.setContentsMargins(12, 10, 12, 10)
        fc_lay.setSpacing(10)

        fila_filtros = FlowLayout()
        fila_filtros.setSpacing(10)
        self.txt_buscar_orden = QLineEdit()
        self.txt_buscar_orden.setPlaceholderText("Buscar cliente, equipo o falla")
        self.txt_buscar_orden.setMinimumWidth(200)
        self.txt_buscar_orden.textChanged.connect(self.refrescar_ordenes)

        self.cmb_filtro_estatus = ContentCombo()
        self.cmb_filtro_estatus.setMinimumWidth(180)
        self.cmb_filtro_estatus.addItems(["Todos"] + ESTATUS_ORDEN)
        self.cmb_filtro_estatus.currentTextChanged.connect(self.refrescar_ordenes)

        self.cmb_filtro_cat = ContentCombo()
        self.cmb_filtro_cat.setMinimumWidth(160)
        self.cmb_filtro_cat.addItems(["Todas"] + CATEGORIAS_EQUIPO)
        self.cmb_filtro_cat.currentTextChanged.connect(self.refrescar_ordenes)

        fila_filtros.addWidget(_campo_filtro("Buscar órdenes", self.txt_buscar_orden), 1)
        fila_filtros.addWidget(_campo_filtro("Estado", self.cmb_filtro_estatus))
        fila_filtros.addWidget(_campo_filtro("Categoría", self.cmb_filtro_cat))
        fc_lay.addLayout(fila_filtros)

        self.lbl_contador_ordenes = QLabel("Cantidad: 0 Órdenes")
        self.lbl_contador_ordenes.setObjectName("CardSub")
        fc_lay.addWidget(self.lbl_contador_ordenes)
        lay.addWidget(filtr_card)

        tbl_card = QFrame()
        tbl_card.setObjectName("Card")
        tc_lay = QVBoxLayout(tbl_card)
        tc_lay.setContentsMargins(12, 10, 12, 10)
        tc_lay.setSpacing(10)

        t_head = FlowLayout()
        t_head.setSpacing(8)
        lbl_o = QLabel("Órdenes")
        lbl_o.setObjectName("Title")
        t_head.addWidget(lbl_o)
        t_head.addStretch()

        ayuda_tbl = QLabel(
            "Doble clic en una fila para editar la orden. Selecciona una orden para "
            "actualizar su estado, registrar abonos o imprimir su ticket."
        )
        ayuda_tbl.setObjectName("CardSub")
        ayuda_tbl.setWordWrap(True)
        tc_lay.addLayout(t_head)
        tc_lay.addWidget(ayuda_tbl)

        self.tbl_ordenes = ReadableTable(0, 8)
        self.tbl_ordenes.setHorizontalHeaderLabels(
            ["N°", "ESTADO", "EQUIPO / MODELO", "CLIENTE", "UBICACIÓN", "FALLA", "PRECIO", "SALDO"]
        )
        _configurar_tabla(self.tbl_ordenes, stretch_col=5)
        self.tbl_ordenes.itemSelectionChanged.connect(self._cargar_orden_seleccionada)
        self.tbl_ordenes.itemDoubleClicked.connect(self._editar_orden_sel)
        tc_lay.addWidget(self.tbl_ordenes, 1)

        lay.addWidget(tbl_card, 1)

        panel_accion = QFrame()
        panel_accion.setObjectName("SubBar")
        pa_lay = QVBoxLayout(panel_accion)
        pa_lay.setContentsMargins(12, 10, 12, 10)
        pa_lay.setSpacing(8)

        f1 = FlowLayout()
        f1.setSpacing(8)
        self.lbl_folio_sel = QLabel("Selecciona una orden")
        self.lbl_folio_sel.setObjectName("FolioBadge")
        self.lbl_folio_sel.setMinimumWidth(220)
        pa_lay.addWidget(self.lbl_folio_sel)
        self.cmb_orden_estatus = ContentCombo()
        self.cmb_orden_estatus.setMinimumWidth(160)
        self.cmb_orden_estatus.addItems(ESTATUS_ORDEN)
        f1.addWidget(_campo_filtro("Estado", self.cmb_orden_estatus))
        self.cmb_orden_ubicacion = ContentCombo()
        self.cmb_orden_ubicacion.setMinimumWidth(155)
        f1.addWidget(_campo_filtro("Ubicación", self.cmb_orden_ubicacion))

        f1.addStretch()

        btn_act_orden = self._boton("Guardar Estado / Ubicación", "guardar", jerarquia="secundario", tooltip="Guardar cambios de estado y ubicación")
        btn_act_orden.setMinimumWidth(190)
        btn_act_orden.clicked.connect(self._actualizar_orden_sel)
        f1.addWidget(btn_act_orden)

        btn_editar_orden = self._boton("Editar orden", "editar", jerarquia="secundario", tooltip="Editar la orden seleccionada")
        btn_editar_orden.setMinimumWidth(125)
        btn_editar_orden.clicked.connect(self._editar_orden_sel)
        f1.addWidget(btn_editar_orden)
        pa_lay.addLayout(f1)

        f2 = FlowLayout()
        f2.setSpacing(8)
        self.spn_orden_abono = QDoubleSpinBox()
        self.spn_orden_abono.setRange(0, 999999)
        self.spn_orden_abono.setDecimals(2)
        self.spn_orden_abono.setMinimumWidth(115)
        f2.addWidget(_campo_filtro("Abono", self.spn_orden_abono))

        self.cmb_orden_mpago = ContentCombo()
        self.cmb_orden_mpago.setMinimumWidth(130)
        self.cmb_orden_mpago.addItems(METODOS_PAGO)
        f2.addWidget(_campo_filtro("Método de pago", self.cmb_orden_mpago))

        btn_abonar = self._boton("Registrar Abono", "zap", jerarquia="principal", tooltip="Registrar un abono en la orden")
        btn_abonar.setMinimumWidth(145)
        btn_abonar.clicked.connect(self._abonar_orden_sel)
        f2.addWidget(btn_abonar)

        f2.addStretch()

        btn_ticket = self._boton("Imprimir ticket", "imprimir", jerarquia="secundario", tooltip="Imprimir el ticket en la impresora")
        btn_ticket.setMinimumWidth(125)
        btn_ticket.clicked.connect(self._imprimir_orden_sel)
        f2.addWidget(btn_ticket)

        btn_img = self._boton("Ticket digital", "descargar", jerarquia="secundario", tooltip="Generar el ticket como imagen y copiarlo")
        btn_img.setMinimumWidth(125)
        btn_img.clicked.connect(self._generar_imagen_ticket_sel)
        f2.addWidget(btn_img)

        btn_eliminar = self._boton("Eliminar orden", "trash", jerarquia="critico", tooltip="Eliminar la orden seleccionada")
        btn_eliminar.setMinimumWidth(130)
        btn_eliminar.clicked.connect(self._eliminar_orden_sel)
        f2.addWidget(btn_eliminar)

        pa_lay.addLayout(f2)
        lay.addWidget(panel_accion)
        return w

    def _seleccionar_etapa(self, etapa: str):
        self.etapa_filtro = etapa
        for btn in self.stage_buttons:
            btn.setProperty("active", btn.text() == etapa)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.refrescar_ordenes()

    # ------------------------------------------
    # 1. NUEVA ORDEN
    # ------------------------------------------
    def _build_nueva_orden_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        lbl = QLabel("Registrar Nueva Orden de Trabajo")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        self.no_cliente = QLineEdit()
        self.no_cliente.setPlaceholderText("Nombre completo del cliente")
        self.no_tel = QLineEdit()
        self.no_tel.setPlaceholderText("Ej. 9861234567")

        self.no_cat = ContentCombo()
        self.no_cat.addItems(CATEGORIAS_EQUIPO)
        self.no_cat.currentTextChanged.connect(self._actualizar_subcategorias_marca)

        self.no_marca = ContentCombo()
        self.no_marca.setEditable(True)
        self.no_marca.setInsertPolicy(QComboBox.NoInsert)

        self.no_modelo = QLineEdit()
        self.no_modelo.setPlaceholderText("Modelo o versión del equipo")
        self.no_color = QLineEdit()
        self.no_color.setPlaceholderText("Ej. Negro, Blanco")

        self.no_imei = QLineEdit()
        self.no_imei.setPlaceholderText("IMEI o número de serie")
        self.no_pin = QLineEdit()
        self.no_pin.setPlaceholderText("PIN o contraseña escrita")

        patron_box = QFrame()
        patron_box.setObjectName("SubBar")
        pb_lay = FlowLayout(patron_box)
        pb_lay.setContentsMargins(12, 10, 12, 10)
        pb_lay.setSpacing(10)

        self.patron_canvas = PatronCanvasWidget()
        self.patron_canvas.patron_cambiado.connect(self._on_patron_dibujado)
        pb_lay.addWidget(self.patron_canvas)

        patron_info = QVBoxLayout()
        patron_info.setSpacing(8)
        lbl_p_ayuda = QLabel("Dibuja el patrón conectando los puntos con el mouse:")
        lbl_p_ayuda.setObjectName("CardSub")
        lbl_p_ayuda.setWordWrap(True)

        self.lbl_patron_valor = QLabel("Patrón: Sin patrón")
        self.lbl_patron_valor.setObjectName("FolioBadge")
        self.lbl_patron_valor.setWordWrap(True)

        btn_limpiar_patron = self._boton("Borrar patrón", "x", jerarquia="secundario", tooltip="Limpiar el patrón dibujado")
        btn_limpiar_patron.setMinimumWidth(130)
        btn_limpiar_patron.clicked.connect(self.patron_canvas.limpiar_patron)

        patron_info.addWidget(lbl_p_ayuda)
        patron_info.addWidget(self.lbl_patron_valor)
        patron_info.addWidget(btn_limpiar_patron, alignment=Qt.AlignLeft)
        patron_info.addStretch()
        pb_lay.addLayout(patron_info, 1)

        self.no_estado_fisico = QLineEdit()
        self.no_estado_fisico.setPlaceholderText("Observaciones físicas al recibir")

        self.no_servicio_cat = ContentCombo()
        self.no_servicio_cat.currentIndexChanged.connect(self._aplicar_servicio_catalogo)

        self.no_falla = MultilineInput()
        self.no_falla.setPlaceholderText("Falla o servicio solicitado")

        self.no_ubicacion = ContentCombo()

        self.no_costo_rep = QDoubleSpinBox()
        self.no_costo_rep.setRange(0, 999999)
        self.no_costo_rep.setDecimals(2)

        self.no_costo_total = QDoubleSpinBox()
        self.no_costo_total.setRange(0, 999999)
        self.no_costo_total.setDecimals(2)
        self.no_costo_total.valueChanged.connect(self._recalcular_saldo_nueva_orden)

        self.no_anticipo = QDoubleSpinBox()
        self.no_anticipo.setRange(0, 999999)
        self.no_anticipo.setDecimals(2)
        self.no_anticipo.valueChanged.connect(self._recalcular_saldo_nueva_orden)

        self.no_metodo_pago = ContentCombo()
        self.no_metodo_pago.addItems(METODOS_PAGO)

        self.lbl_no_saldo = QLabel("$0.00")
        self.lbl_no_saldo.setObjectName("MetricValue")

        self.no_notas = QPlainTextEdit()
        self.no_notas.setMinimumHeight(80)

        def seccion(titulo, ayuda):
            tarjeta, contenido = _tarjeta(titulo, ayuda)
            formulario = QFormLayout()
            formulario.setRowWrapPolicy(QFormLayout.WrapLongRows)
            formulario.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            formulario.setSpacing(10)
            contenido.addLayout(formulario)
            lay.addWidget(tarjeta)
            return formulario

        datos_card, datos_layout = _tarjeta("Datos de la orden", "Folio automático · nueva recepción")
        datos_fila = FlowLayout()
        datos_fila.addWidget(_etiqueta("Estado inicial: Recibido", "FolioBadge"))
        datos_fila.addWidget(_etiqueta("Ingreso: " + datetime.now().strftime("%d/%m/%Y"), "CardSub"))
        datos_layout.addLayout(datos_fila)
        lay.addWidget(datos_card)

        form = seccion("01 · Cliente", "Datos de contacto para el seguimiento de la reparación")
        form.addRow("Cliente *:", self.no_cliente)
        form.addRow("Teléfono / WA *:", self.no_tel)
        form = seccion("02 · Equipo", "Tipo de equipo, identificación y estado de recepción")
        form.addRow("Categoría:", self.no_cat)
        form.addRow("Marca / Consola *:", self.no_marca)
        form.addRow("Modelo / Versión *:", self.no_modelo)
        form.addRow("Color:", self.no_color)
        form.addRow("IMEI / Serie:", self.no_imei)
        form.addRow("Estado físico:", self.no_estado_fisico)
        form = seccion("03 · Diagnóstico y servicio", "Elige un servicio rápido o describe la falla reportada")
        form.addRow("Servicio rápido:", self.no_servicio_cat)
        form.addRow("Falla reportada *:", self.no_falla)
        form.addRow("Ubicación física:", self.no_ubicacion)
        form = seccion("04 · Clave y patrón", "Datos de acceso proporcionados por el cliente")
        form.addRow("PIN / Contraseña:", self.no_pin)
        form.addRow("Patrón (dibujo):", patron_box)
        form = seccion("05 · Importes y notas", "Revisa el anticipo y el saldo antes de guardar")
        form.addRow("Costo repuesto:", self.no_costo_rep)
        form.addRow("Costo total:", self.no_costo_total)
        form.addRow("Anticipo:", self.no_anticipo)
        form.addRow("Método de pago:", self.no_metodo_pago)
        form.addRow("Saldo restante:", self.lbl_no_saldo)
        form.addRow("Notas internas:", self.no_notas)

        btns = FlowLayout()
        btns.setSpacing(8)
        btn_guardar = self._boton("Guardar Orden", "guardar", jerarquia="principal", tooltip="Guardar la nueva orden")
        btn_guardar.setMinimumWidth(145)
        btn_guardar.clicked.connect(self._guardar_nueva_orden)

        btn_limpiar = self._boton("Limpiar", "refresh", jerarquia="secundario", tooltip="Limpiar todos los campos")
        btn_limpiar.setMinimumWidth(115)
        btn_limpiar.clicked.connect(self._limpiar_nueva_orden)

        btns.addStretch()
        btns.addWidget(btn_limpiar)
        btns.addWidget(btn_guardar)
        lay.addLayout(btns)

        self._actualizar_subcategorias_marca(self.no_cat.currentText())

        scroll.setWidget(w)
        return scroll

    def _on_patron_dibujado(self, texto_patron: str):
        self.lbl_patron_valor.setText(f"Patrón: {texto_patron}")

    def _actualizar_subcategorias_marca(self, categoria: str):
        if not hasattr(self, "no_marca"):
            return
        opciones = SUBCATEGORIAS_POR_CATEGORIA.get(categoria, ["Otra marca"])
        self.no_marca.blockSignals(True)
        self.no_marca.clear()
        self.no_marca.addItems(opciones)
        self.no_marca.setCurrentIndex(0)
        self.no_marca.blockSignals(False)

        if categoria == "Consolas":
            self.no_modelo.setPlaceholderText("Ej. Slim 1TB, Fat, Series S, Switch v2")
        elif categoria == "Celulares":
            self.no_modelo.setPlaceholderText("Ej. Galaxy A54, iPhone 13, Redmi Note 12")
        else:
            self.no_modelo.setPlaceholderText("Modelo o versión del equipo")

    def _cargar_combos_orden(self):
        if not hasattr(self, "no_servicio_cat"):
            return
        servicios = self.service.listar_servicios(solo_activos=True)
        self.no_servicio_cat.blockSignals(True)
        self.no_servicio_cat.clear()
        self.no_servicio_cat.addItem("-- Seleccionar servicio del catálogo --", None)
        for s in servicios:
            desc = (
                f"[{s['categoria']}] {s['nombre']} "
                f"({s.get('marca', '')} {s.get('modelo', '')}) - ${float(s['precio']):,.2f}"
            )
            self.no_servicio_cat.addItem(desc, s)
        self.no_servicio_cat.blockSignals(False)

        ubicaciones = self.service.listar_ubicaciones(solo_activas=True)
        actual_ub = self.no_ubicacion.currentText()
        self.no_ubicacion.clear()
        for u in ubicaciones:
            self.no_ubicacion.addItem(u["nombre"])
        if actual_ub:
            idx = self.no_ubicacion.findText(actual_ub)
            if idx >= 0:
                self.no_ubicacion.setCurrentIndex(idx)

    def _aplicar_servicio_catalogo(self):
        s = self.no_servicio_cat.currentData()
        if not s:
            return
        cat = s.get("categoria", "Celulares")
        self.no_cat.setCurrentText(cat)
        self._actualizar_subcategorias_marca(cat)
        if s.get("marca"):
            idx = self.no_marca.findText(s["marca"])
            if idx >= 0:
                self.no_marca.setCurrentIndex(idx)
            else:
                self.no_marca.setCurrentText(s["marca"])
        if s.get("modelo") and not self.no_modelo.text().strip():
            self.no_modelo.setText(s["modelo"])
        self.no_falla.setText(s["nombre"])
        self.no_costo_total.setValue(float(s.get("precio") or 0.0))

    def _recalcular_saldo_nueva_orden(self):
        simbolo = self.config.get("regional", "simbolo_moneda", "$")
        saldo = max(0.0, self.no_costo_total.value() - self.no_anticipo.value())
        self.lbl_no_saldo.setText(f"{simbolo}{saldo:,.2f}")

    def _limpiar_nueva_orden(self):
        for campo in (
            self.no_cliente,
            self.no_tel,
            self.no_modelo,
            self.no_color,
            self.no_imei,
            self.no_pin,
            self.no_estado_fisico,
            self.no_falla,
        ):
            campo.clear()
        self.no_cat.setCurrentIndex(0)
        self._actualizar_subcategorias_marca(self.no_cat.currentText())
        self.patron_canvas.limpiar_patron()
        self.no_notas.clear()
        self.no_costo_rep.setValue(0)
        self.no_costo_total.setValue(0)
        self.no_anticipo.setValue(0)
        self.no_servicio_cat.setCurrentIndex(0)

    def _guardar_nueva_orden(self):
        marca_txt = self.no_marca.currentText().strip()
        faltantes = []
        if not self.no_cliente.text().strip():
            faltantes.append("Cliente")
        if not self.no_tel.text().strip():
            faltantes.append("Teléfono / WA")
        if not marca_txt:
            faltantes.append("Marca / Consola")
        if not self.no_modelo.text().strip():
            faltantes.append("Modelo / Versión")
        if not self.no_falla.text().strip():
            faltantes.append("Falla reportada")

        if faltantes:
            QMessageBox.warning(
                self,
                "Campos requeridos",
                "Completa los siguientes campos: " + ", ".join(faltantes) + ".",
            )
            return

        s_cat = self.no_servicio_cat.currentData()
        datos = {
            "cliente_nombre": self.no_cliente.text(),
            "cliente_tel": self.no_tel.text(),
            "categoria": self.no_cat.currentText(),
            "marca": marca_txt,
            "modelo": self.no_modelo.text(),
            "color": self.no_color.text(),
            "imei": self.no_imei.text(),
            "pin_pass": self.no_pin.text(),
            "patron": self.patron_canvas.obtener_texto_patron(),
            "estado_fisico": self.no_estado_fisico.text(),
            "falla": self.no_falla.text(),
            "servicio_nombre": s_cat["nombre"] if s_cat else "",
            "ubicacion": self.no_ubicacion.currentText() or "Sin asignar",
            "costo_repuesto": self.no_costo_rep.value(),
            "costo_total": self.no_costo_total.value(),
            "anticipo": self.no_anticipo.value(),
            "metodo_pago": self.no_metodo_pago.currentText(),
            "notas_internas": self.no_notas.toPlainText(),
        }
        try:
            folio = self.service.crear_orden(datos)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error al guardar",
                f"No se pudo guardar la orden en la base de datos:\n{exc}",
            )
            return

        QMessageBox.information(self, "Orden creada", f"Se registró la orden #{folio:04d}.")
        self._limpiar_nueva_orden()
        self._mostrar_todas_las_ordenes()
        self.ir_a_seccion(0)

    def _folio_seleccionado(self) -> int | None:
        row = self.tbl_ordenes.currentRow()
        if row < 0:
            return None
        item = self.tbl_ordenes.item(row, 0)
        if not item:
            return None
        return int(item.text().replace("#", ""))

    def refrescar_ordenes(self):
        if not hasattr(self, "tbl_ordenes"):
            return
        simbolo = self.config.get("regional", "simbolo_moneda", "$")
        ordenes = self.service.listar_ordenes(
            busqueda=self.txt_buscar_orden.text(),
            estatus=self.cmb_filtro_estatus.currentText(),
            categoria=self.cmb_filtro_cat.currentText(),
        )

        if self.etapa_filtro == "Entrada":
            ordenes = [o for o in ordenes if o.get("estatus") in ("Recibido", "En diagnóstico")]
        elif self.etapa_filtro == "Reparación":
            ordenes = [
                o for o in ordenes if o.get("estatus") in ("Esperando refacción", "En reparación")
            ]
        elif self.etapa_filtro == "Salida":
            ordenes = [
                o for o in ordenes if o.get("estatus") in ("Listo para entregar", "Entregado")
            ]

        self.tbl_ordenes.setRowCount(0)
        for idx, o in enumerate(ordenes):
            self.tbl_ordenes.insertRow(idx)
            equipo_txt = f"{o.get('marca', '')} {o.get('modelo', '')}".strip()
            vals = [
                f"#{int(o['folio']):04d}",
                o.get("estatus", ""),
                equipo_txt,
                o.get("cliente_nombre", ""),
                o.get("ubicacion", ""),
                o.get("falla", ""),
                f"{simbolo}{float(o.get('costo_total') or 0.0):,.2f}",
                f"{simbolo}{float(o.get('saldo') or 0.0):,.2f}",
            ]
            for c_idx, val in enumerate(vals):
                self.tbl_ordenes.setItem(idx, c_idx, QTableWidgetItem(val))

        self.lbl_contador_ordenes.setText(f"Cantidad: {len(ordenes)} Órdenes")

        ubicaciones = self.service.listar_ubicaciones(solo_activas=True)
        actual = self.cmb_orden_ubicacion.currentText()
        self.cmb_orden_ubicacion.clear()
        for u in ubicaciones:
            self.cmb_orden_ubicacion.addItem(u["nombre"])
        if actual:
            i = self.cmb_orden_ubicacion.findText(actual)
            if i >= 0:
                self.cmb_orden_ubicacion.setCurrentIndex(i)

    def _cargar_orden_seleccionada(self):
        folio = self._folio_seleccionado()
        if not folio:
            return
        o = self.service.obtener_orden(folio)
        if not o:
            return
        self.lbl_folio_sel.setText(f"Orden #{folio:04d} · {o.get('cliente_nombre', '')}")
        self.cmb_orden_estatus.setCurrentText(o.get("estatus", "Recibido"))
        idx_u = self.cmb_orden_ubicacion.findText(o.get("ubicacion", ""))
        if idx_u >= 0:
            self.cmb_orden_ubicacion.setCurrentIndex(idx_u)
        self.spn_orden_abono.setValue(float(o.get("saldo") or 0.0))

    def _actualizar_orden_sel(self):
        folio = self._folio_seleccionado()
        if not folio:
            QMessageBox.information(self, "Selecciona orden", "Selecciona una orden de la tabla.")
            return
        o = self.service.obtener_orden(folio)
        if not o:
            return
        self.service.actualizar_orden_detalle(
            folio=folio,
            estatus=self.cmb_orden_estatus.currentText(),
            ubicacion=self.cmb_orden_ubicacion.currentText(),
            notas_internas=o.get("notas_internas", ""),
            liquidar_al_entregar=True,
            metodo_pago_entrega=self.cmb_orden_mpago.currentText(),
        )
        self.refrescar_ordenes()
        QMessageBox.information(self, "Actualizado", f"Orden #{folio:04d} actualizada.")

    def _editar_orden_sel(self):
        folio = self._folio_seleccionado()
        if not folio:
            QMessageBox.information(self, "Selecciona orden", "Selecciona una orden de la tabla.")
            return
        o = self.service.obtener_orden(folio)
        if not o:
            return

        dlg = AdaptiveDialog(self)
        dlg.setWindowTitle(f"Editar orden #{folio:04d}")
        dlg.setMinimumWidth(480)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)
        form_w = QWidget()
        form = QFormLayout(form_w)
        form.setSpacing(8)

        txt_cliente = QLineEdit(o.get("cliente_nombre", ""))
        txt_tel = QLineEdit(o.get("cliente_tel", ""))
        cmb_cat = ContentCombo()
        cmb_cat.addItems(CATEGORIAS_EQUIPO)
        cmb_cat.setCurrentText(o.get("categoria", "Celulares"))
        cmb_marca = ContentCombo()
        cmb_marca.setEditable(True)
        cmb_marca.setInsertPolicy(QComboBox.NoInsert)
        txt_modelo = QLineEdit(o.get("modelo", ""))
        txt_color = QLineEdit(o.get("color", ""))
        txt_imei = QLineEdit(o.get("imei", ""))
        txt_pin = QLineEdit(o.get("pin_pass", ""))
        txt_patron = QLineEdit(o.get("patron", "Sin patrón"))
        txt_patron.setPlaceholderText("Ej. 1 -> 2 -> 3 (o Sin patrón)")
        txt_estado = QLineEdit(o.get("estado_fisico", ""))
        txt_falla = MultilineInput(o.get("falla", ""))
        cmb_ubic = ContentCombo()
        for u in self.service.listar_ubicaciones(solo_activas=True):
            cmb_ubic.addItem(u["nombre"])
        if o.get("ubicacion") and cmb_ubic.findText(o.get("ubicacion", "")) < 0:
            cmb_ubic.addItem(o.get("ubicacion", ""))
        cmb_ubic.setCurrentText(o.get("ubicacion", "Sin asignar"))
        cmb_estatus = ContentCombo()
        cmb_estatus.addItems(ESTATUS_ORDEN)
        cmb_estatus.setCurrentText(o.get("estatus", "Recibido"))
        spn_rep = QDoubleSpinBox()
        spn_rep.setRange(0, 999999)
        spn_rep.setDecimals(2)
        spn_rep.setValue(float(o.get("costo_repuesto") or 0.0))
        spn_total = QDoubleSpinBox()
        spn_total.setRange(0, 999999)
        spn_total.setDecimals(2)
        spn_total.setValue(float(o.get("costo_total") or 0.0))
        txt_notas = QPlainTextEdit(o.get("notas_internas", ""))
        txt_notas.setMinimumHeight(80)

        def _cargar_marcas(categoria: str):
            opciones = SUBCATEGORIAS_POR_CATEGORIA.get(categoria, ["Otra marca"])
            cmb_marca.blockSignals(True)
            cmb_marca.clear()
            cmb_marca.addItems(opciones)
            cmb_marca.blockSignals(False)
            marca_actual = o.get("marca", "")
            if marca_actual:
                if cmb_marca.findText(marca_actual) >= 0:
                    cmb_marca.setCurrentText(marca_actual)
                else:
                    cmb_marca.setCurrentText(marca_actual)

        cmb_cat.currentTextChanged.connect(_cargar_marcas)
        _cargar_marcas(cmb_cat.currentText())

        form.addRow("Cliente *:", txt_cliente)
        form.addRow("Teléfono / WA *:", txt_tel)
        form.addRow("Categoría:", cmb_cat)
        form.addRow("Marca / Consola *:", cmb_marca)
        form.addRow("Modelo / Versión *:", txt_modelo)
        form.addRow("Color:", txt_color)
        form.addRow("IMEI / Serie:", txt_imei)
        form.addRow("PIN / Contraseña:", txt_pin)
        form.addRow("Patrón:", txt_patron)
        form.addRow("Estado físico:", txt_estado)
        form.addRow("Falla reportada *:", txt_falla)
        form.addRow("Ubicación:", cmb_ubic)
        form.addRow("Estatus:", cmb_estatus)
        form.addRow("Costo repuesto:", spn_rep)
        form.addRow("Costo total:", spn_total)
        form.addRow("Notas internas:", txt_notas)
        scroll.setWidget(form_w)
        lay.addWidget(scroll, 1)

        nota = QLabel(
            "El saldo se recalcula solo (total menos anticipo ya registrado). "
            "Los abonos ya hechos no se modifican."
        )
        nota.setObjectName("CardSub")
        nota.setWordWrap(True)
        lay.addWidget(nota)

        fila_btns = FlowLayout()
        fila_btns.setSpacing(10)
        btn_cancelar = self._boton("Cancelar", "cancelar", jerarquia="secundario", tooltip="Descartar cambios")
        btn_cancelar.clicked.connect(dlg.reject)
        btn_guardar = self._boton("Guardar cambios", "guardar", jerarquia="principal", tooltip="Guardar los cambios")
        btn_guardar.setMinimumWidth(150)
        fila_btns.addStretch()
        fila_btns.addWidget(btn_cancelar)
        fila_btns.addWidget(btn_guardar)
        lay.addLayout(fila_btns)

        def _guardar():
            faltantes = []
            if not txt_cliente.text().strip():
                faltantes.append("Cliente")
            if not txt_tel.text().strip():
                faltantes.append("Teléfono / WA")
            if not cmb_marca.currentText().strip():
                faltantes.append("Marca / Consola")
            if not txt_modelo.text().strip():
                faltantes.append("Modelo / Versión")
            if not txt_falla.text().strip():
                faltantes.append("Falla reportada")
            if faltantes:
                QMessageBox.warning(
                    self,
                    "Campos requeridos",
                    "Completa los siguientes campos: " + ", ".join(faltantes) + ".",
                )
                return
            ok = self.service.actualizar_orden_datos(
                folio,
                {
                    "cliente_nombre": txt_cliente.text(),
                    "cliente_tel": txt_tel.text(),
                    "categoria": cmb_cat.currentText(),
                    "marca": cmb_marca.currentText(),
                    "modelo": txt_modelo.text(),
                    "color": txt_color.text(),
                    "imei": txt_imei.text(),
                    "pin_pass": txt_pin.text(),
                    "patron": txt_patron.text() or "Sin patrón",
                    "estado_fisico": txt_estado.text(),
                    "falla": txt_falla.text(),
                    "ubicacion": cmb_ubic.currentText() or "Sin asignar",
                    "estatus": cmb_estatus.currentText(),
                    "costo_repuesto": spn_rep.value(),
                    "costo_total": spn_total.value(),
                    "notas_internas": txt_notas.toPlainText(),
                },
            )
            if not ok:
                QMessageBox.warning(self, "No se guardó", "La orden ya no existe.")
                return
            dlg.accept()
            self.refrescar_ordenes()
            QMessageBox.information(self, "Guardado", f"Orden #{folio:04d} actualizada.")

        btn_guardar.clicked.connect(_guardar)
        dlg.exec()

    def _abonar_orden_sel(self):
        folio = self._folio_seleccionado()
        if not folio:
            QMessageBox.information(self, "Selecciona orden", "Selecciona una orden de la tabla.")
            return
        monto = self.spn_orden_abono.value()
        if monto <= 0:
            QMessageBox.warning(self, "Monto inválido", "Ingresa un monto mayor a cero.")
            return
        self.service.registrar_pago(folio, monto, self.cmb_orden_mpago.currentText())
        self.refrescar_ordenes()
        QMessageBox.information(self, "Abono registrado", f"Abono aplicado a #{folio:04d}.")

    def _imprimir_orden_sel(self):
        folio = self._folio_seleccionado()
        if not folio:
            QMessageBox.information(self, "Selecciona orden", "Selecciona una orden de la tabla.")
            return
        o = self.service.obtener_orden(folio)
        if not o:
            return
        ok, msg = imprimir_ticket_58mm(o, self.config)
        if ok:
            QMessageBox.information(self, "Impresión", msg)
        else:
            QMessageBox.warning(
                self, "Imprimir ticket", f"{msg}\n\nVista previa:\n{generar_texto_ticket(o, self.config)}"
            )

    def _generar_imagen_ticket_sel(self):
        folio = self._folio_seleccionado()
        if not folio:
            QMessageBox.information(self, "Selecciona orden", "Selecciona una orden de la tabla.")
            return
        o = self.service.obtener_orden(folio)
        if not o:
            return
        carpeta = os.path.join(
            os.path.dirname(os.path.abspath(self.db.db_path)), "tickets"
        )
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, f"ticket_{folio:04d}.png")
        try:
            ruta_ok = generar_imagen_ticket(o, self.config, ruta)
        except Exception as exc:
            QMessageBox.warning(
                self, "No se pudo generar", f"No se pudo crear la imagen del ticket:\n{exc}"
            )
            return
        if not ruta_ok:
            QMessageBox.warning(
                self,
                "No disponible",
                "No se pudo generar la imagen (falta el componente de imágenes).",
            )
            return
        self._mostrar_dialogo_imagen_ticket(o, ruta_ok)

    def _mostrar_dialogo_imagen_ticket(self, orden: dict, ruta: str):
        folio = int(orden.get("folio") or 0)
        dlg = AdaptiveDialog(self)
        dlg.setWindowTitle(f"Ticket digital — Folio #{folio:04d}")
        dlg.setMinimumWidth(520)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        ayuda = QLabel(
            "Esta imagen está lista para enviar por WhatsApp. "
            "Pulsa «Enviar por WhatsApp»: la imagen se copiará al portapapeles "
            "y solo tendrás que pegarla con Ctrl+V en el chat."
        )
        ayuda.setObjectName("CardSub")
        ayuda.setWordWrap(True)
        lay.addWidget(ayuda)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(280)
        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignCenter)
        pm = QPixmap(ruta)
        if not pm.isNull():
            lbl_img.setPixmap(
                pm.scaled(460, 460, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            lbl_img.setText("No se pudo cargar la vista previa.")
        scroll.setWidget(lbl_img)
        lay.addWidget(scroll, 1)

        lbl_ruta = QLabel(ruta)
        lbl_ruta.setObjectName("CardSub")
        lbl_ruta.setWordWrap(True)
        lay.addWidget(lbl_ruta)

        fila = FlowLayout()
        fila.setSpacing(10)
        btn_abrir = self._boton("Abrir imagen", "ojo", jerarquia="secundario", tooltip="Abrir la imagen del ticket")
        btn_abrir.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(ruta))
        )
        btn_carpeta = self._boton("Abrir carpeta", "descargar", jerarquia="secundario", tooltip="Abrir la carpeta del ticket")
        btn_carpeta.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl.fromLocalFile(os.path.dirname(ruta))
            )
        )
        btn_wa = self._boton("Enviar por WhatsApp", "mensajes", jerarquia="principal", object_name="PrimaryBtn", tooltip="Preparar el mensaje en WhatsApp")
        btn_wa.setMinimumWidth(170)
        btn_wa.clicked.connect(lambda: self._enviar_wa_desde_imagen(orden, ruta))
        btn_cerrar = self._boton("Cerrar", "x", jerarquia="secundario", tooltip="Cerrar la vista previa")
        btn_cerrar.clicked.connect(dlg.accept)
        for b in (btn_abrir, btn_carpeta, btn_wa, btn_cerrar):
            fila.addWidget(b)
        lay.addLayout(fila)
        dlg.exec()

    def _enviar_wa_desde_imagen(self, orden: dict, ruta: str = ""):
        # Copia la imagen del ticket al portapapeles para pegarla en WhatsApp.
        if ruta and os.path.exists(ruta):
            pm = QPixmap(ruta)
            if not pm.isNull():
                QApplication.clipboard().setPixmap(pm)
        tipo = "listo" if orden.get("estatus") == "Listo para entregar" else "recibido"
        msg = self.wa.construir_mensaje(tipo, orden)
        url = self.wa.generar_url_wa(orden.get("cliente_tel", ""), msg)
        self.wa.registrar_notificacion(
            int(orden.get("folio") or 0),
            orden.get("cliente_nombre", ""),
            orden.get("cliente_tel", ""),
            tipo,
            msg,
        )
        webbrowser.open(url)
        QMessageBox.information(
            self,
            "WhatsApp abierto",
            "Se abrió el chat con el mensaje listo.\n\n"
            "La imagen del ticket ya está copiada: pégala en el chat con Ctrl+V "
            "(o con clic derecho → Pegar) y envíala.",
        )

    def _autorizar_con_codigo(self, accion: str, obligatorio: bool = False) -> bool:
        if not self.config.tiene_codigo_maestro():
            if obligatorio:
                QMessageBox.information(
                    self,
                    "Código maestro",
                    "Primero define un código maestro con Ctrl+P.",
                )
                return False
            return True
        codigo, ok = QInputDialog.getText(
            self,
            "Código maestro",
            f"Escribe el código maestro para {accion}:",
            QLineEdit.EchoMode.Password,
        )
        if not ok:
            return False
        if not self.config.verificar_codigo_maestro(codigo):
            QMessageBox.warning(self, "Código incorrecto", "El código maestro no es correcto.")
            return False
        return True

    def _eliminar_orden_sel(self):
        folio = self._folio_seleccionado()
        if not folio:
            QMessageBox.information(self, "Selecciona orden", "Selecciona una orden de la tabla.")
            return
        o = self.service.obtener_orden(folio)
        if not o:
            return
        si_no = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        resp = QMessageBox.question(
            self,
            "Eliminar orden",
            f"¿Eliminar la orden #{folio:04d} de {o.get('cliente_nombre', '')}?\n\n"
            "También se borrarán sus pagos. Esta acción no se puede deshacer.",
            si_no,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        if not self._autorizar_con_codigo(f"eliminar la orden #{folio:04d}"):
            return
        self.service.eliminar_orden(folio)
        self.lbl_folio_sel.setText("Selecciona una orden")
        self.refrescar_todo()
        QMessageBox.information(self, "Orden eliminada", f"Se eliminó la orden #{folio:04d}.")

    # ------------------------------------------
    # 3. CATÁLOGO Y UBICACIONES
    # ------------------------------------------
    def _build_catalogo_ubicaciones_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        lbl = QLabel("Catálogo de Servicios y Ubicaciones")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        tabs = QTabWidget()

        p_serv = QWidget()
        l_serv = QVBoxLayout(p_serv)
        row_s = FlowLayout()
        row_s.setSpacing(8)
        self.s_cat = ContentCombo()
        self.s_cat.setMinimumWidth(125)
        self.s_cat.addItems(CATEGORIAS_EQUIPO)
        self.s_marca = QLineEdit()
        self.s_marca.setPlaceholderText("Marca / Consola")
        self.s_modelo = QLineEdit()
        self.s_modelo.setPlaceholderText("Modelo")
        self.s_nombre = QLineEdit()
        self.s_nombre.setPlaceholderText("Nombre del servicio")
        self.s_nombre.setMinimumWidth(160)
        self.s_precio = QDoubleSpinBox()
        self.s_precio.setRange(0, 999999)
        self.s_precio.setDecimals(2)
        self.s_precio.setMinimumWidth(110)
        btn_add_s = self._boton("Agregar servicio", "mas", jerarquia="principal", object_name="PrimaryBtn", tooltip="Agregar un servicio al catálogo")
        btn_add_s.setMinimumWidth(150)
        btn_add_s.clicked.connect(self._agregar_servicio)
        for titulo, widget in (("Categoría", self.s_cat), ("Marca", self.s_marca),
                               ("Modelo", self.s_modelo), ("Servicio", self.s_nombre),
                               ("Precio", self.s_precio)):
            row_s.addWidget(_campo_filtro(titulo, widget))
        row_s.addWidget(btn_add_s)
        l_serv.addLayout(row_s)

        self.tbl_servicios = ReadableTable(0, 6)
        self.tbl_servicios.setHorizontalHeaderLabels(
            ["ID", "CATEGORÍA", "MARCA / MODELO", "SERVICIO", "PRECIO", "ACCIONES"]
        )
        _configurar_tabla(self.tbl_servicios, stretch_col=3)
        self.tbl_servicios.setColumnWidth(5, 170)
        l_serv.addWidget(self.tbl_servicios, 1)

        p_ub = QWidget()
        l_ub = QVBoxLayout(p_ub)
        row_u = FlowLayout()
        row_u.setSpacing(8)
        self.u_nombre = QLineEdit()
        self.u_nombre.setPlaceholderText("Ubicación (ej. Estante A-1)")
        self.u_tipo = QLineEdit()
        self.u_tipo.setPlaceholderText("Tipo")
        self.u_desc = QLineEdit()
        self.u_desc.setPlaceholderText("Descripción")
        btn_add_u = self._boton("Agregar ubicación", "mas", jerarquia="principal", object_name="PrimaryBtn", tooltip="Agregar una ubicación")
        btn_add_u.setMinimumWidth(160)
        btn_add_u.clicked.connect(self._agregar_ubicacion)
        for titulo, widget in (("Ubicación", self.u_nombre), ("Tipo", self.u_tipo),
                               ("Descripción", self.u_desc)):
            row_u.addWidget(_campo_filtro(titulo, widget), 1)
        row_u.addWidget(btn_add_u)
        l_ub.addLayout(row_u)

        self.tbl_ubicaciones = ReadableTable(0, 5)
        self.tbl_ubicaciones.setHorizontalHeaderLabels(
            ["ID", "NOMBRE", "TIPO", "DESCRIPCIÓN", "ACCIONES"]
        )
        _configurar_tabla(self.tbl_ubicaciones, stretch_col=3)
        self.tbl_ubicaciones.setColumnWidth(4, 170)
        l_ub.addWidget(self.tbl_ubicaciones, 1)

        tabs.addTab(scroll_page(p_serv), "Servicios")
        tabs.addTab(scroll_page(p_ub), "Ubicaciones")
        lay.addWidget(tabs, 1)
        return w

    def _agregar_servicio(self):
        if not self.s_nombre.text().strip():
            return
        self.service.guardar_servicio(
            {
                "categoria": self.s_cat.currentText(),
                "marca": self.s_marca.text(),
                "modelo": self.s_modelo.text(),
                "nombre": self.s_nombre.text(),
                "precio": self.s_precio.value(),
                "activo": True,
            }
        )
        self.s_nombre.clear()
        self.s_precio.setValue(0)
        self.refrescar_catalogo_ubicaciones()

    def _agregar_ubicacion(self):
        if not self.u_nombre.text().strip():
            return
        self.service.guardar_ubicacion(
            self.u_nombre.text(), self.u_tipo.text() or "General", self.u_desc.text()
        )
        self.u_nombre.clear()
        self.u_desc.clear()
        self.refrescar_catalogo_ubicaciones()

    def _crear_botones_accion(
        self, al_editar, al_eliminar
    ) -> QWidget:
        """Crea el widget con botones Editar / Eliminar para una fila del catálogo."""
        cont = QWidget()
        lay = QHBoxLayout(cont)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(6)
        btn_editar = self._boton("Editar", "editar", jerarquia="secundario", object_name="AccBtn", icon_size=14)
        btn_editar.setMinimumWidth(78)
        btn_editar.clicked.connect(al_editar)
        btn_eliminar = self._boton("Eliminar", "trash", jerarquia="critico", object_name="AccDangerBtn", icon_size=14)
        btn_eliminar.setMinimumWidth(84)
        btn_eliminar.clicked.connect(al_eliminar)
        lay.addWidget(btn_editar)
        lay.addWidget(btn_eliminar)
        lay.addStretch()
        return cont

    def refrescar_catalogo_ubicaciones(self):
        if not hasattr(self, "tbl_servicios"):
            return
        simbolo = self.config.get("regional", "simbolo_moneda", "$")
        servicios = self.service.listar_servicios()
        self.tbl_servicios.setRowCount(0)
        for i, s in enumerate(servicios):
            self.tbl_servicios.insertRow(i)
            eq = f"{s.get('marca', '')} {s.get('modelo', '')}".strip() or "General"
            vals = [
                str(s["id"]),
                s.get("categoria", ""),
                eq,
                s.get("nombre", ""),
                f"{simbolo}{float(s.get('precio') or 0.0):,.2f}",
            ]
            for c, v in enumerate(vals):
                self.tbl_servicios.setItem(i, c, QTableWidgetItem(v))
            sid = int(s["id"])
            self.tbl_servicios.setCellWidget(
                i,
                5,
                self._crear_botones_accion(
                    lambda checked=False, _id=sid: self._editar_servicio(_id),
                    lambda checked=False, _id=sid: self._eliminar_servicio(_id),
                ),
            )

        ubicaciones = self.service.listar_ubicaciones(solo_activas=False)
        self.tbl_ubicaciones.setRowCount(0)
        for i, u in enumerate(ubicaciones):
            self.tbl_ubicaciones.insertRow(i)
            vals = [str(u["id"]), u.get("nombre", ""), u.get("tipo", ""), u.get("descripcion", "")]
            for c, v in enumerate(vals):
                self.tbl_ubicaciones.setItem(i, c, QTableWidgetItem(v))
            uid = int(u["id"])
            self.tbl_ubicaciones.setCellWidget(
                i,
                4,
                self._crear_botones_accion(
                    lambda checked=False, _id=uid: self._editar_ubicacion(_id),
                    lambda checked=False, _id=uid: self._eliminar_ubicacion(_id),
                ),
            )

        self._cargar_combos_orden()

    def _obtener_servicio_por_id(self, servicio_id: int) -> dict | None:
        for s in self.service.listar_servicios():
            if int(s.get("id") or 0) == int(servicio_id):
                return s
        return None

    def _obtener_ubicacion_por_id(self, ubicacion_id: int) -> dict | None:
        for u in self.service.listar_ubicaciones(solo_activas=False):
            if int(u.get("id") or 0) == int(ubicacion_id):
                return u
        return None

    def _editar_servicio(self, servicio_id: int):
        s = self._obtener_servicio_por_id(servicio_id)
        if not s:
            QMessageBox.warning(self, "No encontrado", "El servicio ya no existe.")
            return

        dlg = AdaptiveDialog(self)
        dlg.setWindowTitle("Editar servicio")
        dlg.setMinimumWidth(420)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        cmb_cat = ContentCombo()
        cmb_cat.addItems(CATEGORIAS_EQUIPO)
        cmb_cat.setCurrentText(s.get("categoria", "Celulares"))
        txt_marca = QLineEdit(s.get("marca", ""))
        txt_modelo = QLineEdit(s.get("modelo", ""))
        txt_nombre = QLineEdit(s.get("nombre", ""))
        spn_precio = QDoubleSpinBox()
        spn_precio.setRange(0, 999999)
        spn_precio.setDecimals(2)
        spn_precio.setValue(float(s.get("precio") or 0.0))

        form.addRow("Categoría:", cmb_cat)
        form.addRow("Marca / Consola:", txt_marca)
        form.addRow("Modelo:", txt_modelo)
        form.addRow("Servicio:", txt_nombre)
        form.addRow("Precio:", spn_precio)
        lay.addLayout(form)

        fila_btns = FlowLayout()
        fila_btns.setSpacing(10)
        btn_cancelar = self._boton("Cancelar", "cancelar", jerarquia="secundario", tooltip="Descartar cambios")
        btn_cancelar.clicked.connect(dlg.reject)
        btn_guardar = self._boton("Guardar cambios", "guardar", jerarquia="principal", tooltip="Guardar los cambios")
        btn_guardar.setMinimumWidth(140)
        fila_btns.addStretch()
        fila_btns.addWidget(btn_cancelar)
        fila_btns.addWidget(btn_guardar)
        lay.addLayout(fila_btns)

        def _guardar():
            if not txt_nombre.text().strip():
                QMessageBox.warning(self, "Falta el servicio", "Escribe el nombre del servicio.")
                return
            ok = self.service.actualizar_servicio(
                servicio_id,
                {
                    "categoria": cmb_cat.currentText(),
                    "marca": txt_marca.text(),
                    "modelo": txt_modelo.text(),
                    "nombre": txt_nombre.text(),
                    "precio": spn_precio.value(),
                },
            )
            if not ok:
                QMessageBox.warning(self, "No se guardó", "El servicio ya no existe.")
                return
            dlg.accept()
            self.refrescar_catalogo_ubicaciones()
            QMessageBox.information(self, "Guardado", "Servicio actualizado.")

        btn_guardar.clicked.connect(_guardar)
        dlg.exec()

    def _eliminar_servicio(self, servicio_id: int):
        s = self._obtener_servicio_por_id(servicio_id)
        if not s:
            QMessageBox.warning(self, "No encontrado", "El servicio ya no existe.")
            return
        resp = QMessageBox.question(
            self,
            "Eliminar servicio",
            f"¿Eliminar el servicio '{s.get('nombre', '')}' "
            f"({s.get('categoria', '')} {s.get('marca', '')})?\n\n"
            "Ya no aparecerá en el catálogo ni en las nuevas órdenes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        if not self._autorizar_con_codigo("eliminar el servicio del catálogo"):
            return
        if self.service.eliminar_servicio(servicio_id):
            self.refrescar_catalogo_ubicaciones()
            QMessageBox.information(self, "Eliminado", "Servicio eliminado del catálogo.")
        else:
            QMessageBox.warning(self, "No se eliminó", "El servicio ya no existe.")

    def _editar_ubicacion(self, ubicacion_id: int):
        u = self._obtener_ubicacion_por_id(ubicacion_id)
        if not u:
            QMessageBox.warning(self, "No encontrada", "La ubicación ya no existe.")
            return

        dlg = AdaptiveDialog(self)
        dlg.setWindowTitle("Editar ubicación")
        dlg.setMinimumWidth(420)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        txt_nombre = QLineEdit(u.get("nombre", ""))
        txt_tipo = QLineEdit(u.get("tipo", "General"))
        txt_desc = QLineEdit(u.get("descripcion", ""))

        form.addRow("Nombre:", txt_nombre)
        form.addRow("Tipo:", txt_tipo)
        form.addRow("Descripción:", txt_desc)
        lay.addLayout(form)

        fila_btns = FlowLayout()
        fila_btns.setSpacing(10)
        btn_cancelar = self._boton("Cancelar", "cancelar", jerarquia="secundario", tooltip="Descartar cambios")
        btn_cancelar.clicked.connect(dlg.reject)
        btn_guardar = self._boton("Guardar cambios", "guardar", jerarquia="principal", tooltip="Guardar los cambios")
        btn_guardar.setMinimumWidth(140)
        fila_btns.addStretch()
        fila_btns.addWidget(btn_cancelar)
        fila_btns.addWidget(btn_guardar)
        lay.addLayout(fila_btns)

        def _guardar():
            if not txt_nombre.text().strip():
                QMessageBox.warning(self, "Falta el nombre", "Escribe el nombre de la ubicación.")
                return
            ok = self.service.actualizar_ubicacion(
                ubicacion_id,
                txt_nombre.text(),
                txt_tipo.text() or "General",
                txt_desc.text(),
            )
            if not ok:
                QMessageBox.warning(
                    self,
                    "No se guardó",
                    "Ya existe otra ubicación con ese nombre, o la ubicación ya no existe.",
                )
                return
            dlg.accept()
            self.refrescar_catalogo_ubicaciones()
            QMessageBox.information(self, "Guardado", "Ubicación actualizada.")

        btn_guardar.clicked.connect(_guardar)
        dlg.exec()

    def _eliminar_ubicacion(self, ubicacion_id: int):
        u = self._obtener_ubicacion_por_id(ubicacion_id)
        if not u:
            QMessageBox.warning(self, "No encontrada", "La ubicación ya no existe.")
            return
        resp = QMessageBox.question(
            self,
            "Eliminar ubicación",
            f"¿Eliminar la ubicación '{u.get('nombre', '')}'?\n\n"
            "Ya no aparecerá en el selector de ubicaciones de las órdenes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        if not self._autorizar_con_codigo("eliminar la ubicación"):
            return
        if self.service.eliminar_ubicacion(ubicacion_id):
            self.refrescar_catalogo_ubicaciones()
            QMessageBox.information(self, "Eliminada", "Ubicación eliminada.")
        else:
            QMessageBox.warning(self, "No se eliminó", "La ubicación ya no existe.")

    # ------------------------------------------
    # 4. ESTADÍSTICAS Y CAJA
    # ------------------------------------------
    def _build_reportes_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        lbl = QLabel("Estadísticas y Reportes Financieros")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        row = FlowLayout()
        row.setSpacing(8)
        c_dia, self.r_dia, _ = _make_metric_card("Ingresos del Día", "$0.00", "Abonos y cobros hoy")
        c_mes, self.r_mes, _ = _make_metric_card("Ingresos del Mes", "$0.00", "Flujo mensual")
        c_gan, self.r_gan, _ = _make_metric_card(
            "Ganancia Neta (Mes)", "$0.00", "Total órdenes menos repuestos"
        )
        c_sal, self.r_sal, _ = _make_metric_card("Saldos por Cobrar", "$0.00", "Pendiente en taller")
        for c in (c_dia, c_mes, c_gan, c_sal):
            row.addWidget(c)
        lay.addLayout(row)

        rep_card, rep_lay = _tarjeta("Reporte por categoría", "Ganancia estimada según ingresos y repuestos")
        self.tbl_rep_cat = ReadableTable(0, 5)
        self.tbl_rep_cat.setHorizontalHeaderLabels(
            ["CATEGORÍA", "ÓRDENES", "FACTURADO", "COSTO REPUESTOS", "GANANCIA ESTIMADA"]
        )
        _configurar_tabla(self.tbl_rep_cat, stretch_col=0)
        rep_lay.addWidget(self.tbl_rep_cat, 1)
        lay.addWidget(rep_card, 1)
        return w

    def refrescar_reportes(self):
        if not hasattr(self, "r_dia"):
            return
        simbolo = self.config.get("regional", "simbolo_moneda", "$")
        rep = self.service.generar_reporte_financiero()
        self.r_dia.setText(f"{simbolo}{rep['ingresos_diarios']:,.2f}")
        self.r_mes.setText(f"{simbolo}{rep['ingresos_mensuales']:,.2f}")
        self.r_gan.setText(f"{simbolo}{rep['ganancia_neta_mes']:,.2f}")
        self.r_sal.setText(f"{simbolo}{rep['saldos_pendientes']:,.2f}")

        self.tbl_rep_cat.setRowCount(0)
        for idx, (cat, d) in enumerate(rep["por_categoria"].items()):
            self.tbl_rep_cat.insertRow(idx)
            vals = [
                cat,
                str(d["ordenes"]),
                f"{simbolo}{d['facturado']:,.2f}",
                f"{simbolo}{d['costo_rep']:,.2f}",
                f"{simbolo}{d['ganancia']:,.2f}",
            ]
            for c_i, val in enumerate(vals):
                self.tbl_rep_cat.setItem(idx, c_i, QTableWidgetItem(val))

    # ------------------------------------------
    # 2. INVENTARIO DE PRODUCTOS Y REFACCIONES
    # ------------------------------------------
    def _build_inventario_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        head_row = QVBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_t = QLabel("Inventario de Productos y Refacciones")
        lbl_t.setObjectName("Title")
        title_box.addWidget(lbl_t)

        self.lbl_inv_candado = QLabel("")
        self.lbl_inv_candado.setObjectName("CardSub")

        self.btn_inv_candado = self._boton("Desbloquear edición", "ojo", jerarquia="secundario", tooltip="Iniciar sesión de edición (se pide el código maestro una vez)")
        self.btn_inv_candado.setMinimumHeight(32)
        self.btn_inv_candado.clicked.connect(self._alternar_candado_inventario)

        btn_nuevo_prod = self._boton("Agregar producto", "mas", jerarquia="principal", object_name="PrimaryBtn", tooltip="Agregar un producto o refacción")
        btn_nuevo_prod.setMinimumWidth(165)
        btn_nuevo_prod.setMinimumHeight(32)
        btn_nuevo_prod.clicked.connect(self._agregar_producto_inventario)

        head_row.addLayout(title_box)
        acciones = FlowLayout()
        acciones.addWidget(self.lbl_inv_candado)
        acciones.addWidget(self.btn_inv_candado)
        acciones.addWidget(btn_nuevo_prod)
        head_row.addLayout(acciones)
        lay.addLayout(head_row)

        cards_row = FlowLayout()
        cards_row.setSpacing(8)
        c_prod, self.lbl_inv_total, self.lbl_inv_unidades = _make_metric_card(
            "Productos registrados", "0", "0 unidades disponibles"
        )
        c_alert, self.lbl_inv_alertas, self.lbl_inv_alertas_sub = _make_metric_card(
            "Alertas de stock", "0", "Todo con existencia suficiente"
        )
        c_costo, self.lbl_inv_costo, _ = _make_metric_card(
            "Valor en costo", "$0.00", "Inversión actual en almacén"
        )
        c_venta, self.lbl_inv_venta, self.lbl_inv_ganancia = _make_metric_card(
            "Valor en venta", "$0.00", "Ganancia est.: $0.00"
        )
        for c in (c_prod, c_alert, c_costo, c_venta):
            cards_row.addWidget(c)
        lay.addLayout(cards_row)

        tbl_card = QFrame()
        tbl_card.setObjectName("Card")
        tc_lay = QVBoxLayout(tbl_card)
        tc_lay.setContentsMargins(16, 14, 16, 14)
        tc_lay.setSpacing(10)

        filtros_row = FlowLayout()
        filtros_row.setSpacing(8)

        self.txt_buscar_inv = QLineEdit()
        self.txt_buscar_inv.setPlaceholderText(
            "Buscar por código, producto, marca/modelo o ubicación..."
        )
        self.txt_buscar_inv.setMinimumWidth(220)
        self.txt_buscar_inv.textChanged.connect(self.refrescar_inventario)

        self.cmb_inv_cat = ContentCombo()
        self.cmb_inv_cat.setMinimumWidth(160)
        self.cmb_inv_cat.addItems(["Todas"] + CATEGORIAS_INVENTARIO)
        self.cmb_inv_cat.currentTextChanged.connect(self.refrescar_inventario)

        self.cmb_inv_stock = ContentCombo()
        self.cmb_inv_stock.setMinimumWidth(150)
        self.cmb_inv_stock.addItems(["Todos", "Disponible", "Stock bajo", "Agotado"])
        self.cmb_inv_stock.currentTextChanged.connect(self.refrescar_inventario)

        filtros_row.addWidget(_campo_filtro("Buscar productos", self.txt_buscar_inv), 1)
        filtros_row.addWidget(_campo_filtro("Categoría", self.cmb_inv_cat))
        filtros_row.addWidget(_campo_filtro("Existencia", self.cmb_inv_stock))
        tc_lay.addLayout(filtros_row)

        self.tbl_inventario = ReadableTable(0, 9)
        self.tbl_inventario.setHorizontalHeaderLabels(
            [
                "ID",
                "CÓDIGO",
                "PRODUCTO",
                "CATEGORÍA",
                "MARCA / MODELO",
                "STOCK",
                "COSTO",
                "PRECIO VENTA",
                "ACCIONES",
            ]
        )
        _configurar_tabla(self.tbl_inventario, stretch_col=2)
        self.tbl_inventario.setColumnWidth(0, 52)
        self.tbl_inventario.setColumnWidth(1, 95)
        self.tbl_inventario.setColumnWidth(5, 115)
        self.tbl_inventario.setColumnWidth(6, 105)
        self.tbl_inventario.setColumnWidth(7, 115)
        self.tbl_inventario.setColumnWidth(8, 255)
        self.tbl_inventario.itemDoubleClicked.connect(self._editar_inventario_doble_clic)
        tc_lay.addWidget(self.tbl_inventario, 1)

        ayuda_inv = QLabel(
            "Doble clic en cualquier producto para editarlo. El código maestro se pide una sola vez "
            "al iniciar modificaciones y puedes agregar, ajustar o eliminar sin volver a escribirlo."
        )
        ayuda_inv.setObjectName("CardSub")
        ayuda_inv.setWordWrap(True)
        tc_lay.addWidget(ayuda_inv)

        lay.addWidget(tbl_card, 1)
        self._actualizar_ui_candado_inventario()
        return w

    def _actualizar_ui_candado_inventario(self):
        if not hasattr(self, "lbl_inv_candado"):
            return
        if not self.config.tiene_codigo_maestro():
            self.lbl_inv_candado.setText("Edición libre (sin código maestro)")
            self.lbl_inv_candado.setStyleSheet("color: #c5f467; font-weight: 600;")
            self.btn_inv_candado.setVisible(False)
            return

        self.btn_inv_candado.setVisible(True)
        if self.inventario_desbloqueado:
            self.lbl_inv_candado.setText("Edición activa")
            self.lbl_inv_candado.setStyleSheet("color: #c5f467; font-weight: 700;")
            self.btn_inv_candado.setText("Bloquear edición")
        else:
            self.lbl_inv_candado.setText("Edición protegida")
            self.lbl_inv_candado.setStyleSheet("color: #f5b84b; font-weight: 700;")
            self.btn_inv_candado.setText("Desbloquear edición")

    def _alternar_candado_inventario(self):
        if self.inventario_desbloqueado:
            self.inventario_desbloqueado = False
            self._actualizar_ui_candado_inventario()
            QMessageBox.information(
                self,
                "Inventario bloqueado",
                "El área de inventario quedó protegida nuevamente.",
            )
            return
        if self._asegurar_edicion_inventario():
            QMessageBox.information(
                self,
                "Edición desbloqueada",
                "Ya puedes agregar, editar, ajustar stock o eliminar productos sin volver a ingresar la contraseña.",
            )

    def _asegurar_edicion_inventario(self) -> bool:
        """Pide el código maestro solo la primera vez que se intenta modificar el inventario."""
        if self.inventario_desbloqueado:
            return True
        if not self.config.tiene_codigo_maestro():
            self.inventario_desbloqueado = True
            self._actualizar_ui_candado_inventario()
            return True
        if self._autorizar_con_codigo("modificar el inventario"):
            self.inventario_desbloqueado = True
            self._actualizar_ui_candado_inventario()
            return True
        return False

    def _crear_botones_inventario(self, producto_id: int) -> QWidget:
        cont = QWidget()
        lay = QHBoxLayout(cont)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(4)

        btn_menos = self._boton_icono("menos", "IconBtn", "Restar 1 al stock", 16)
        btn_menos.setMinimumWidth(32)
        btn_menos.clicked.connect(
            lambda _=False, pid=producto_id: self._ajustar_stock_rapido(pid, -1)
        )

        btn_mas = self._boton_icono("mas", "IconBtn", "Sumar 1 al stock", 16)
        btn_mas.setMinimumWidth(32)
        btn_mas.clicked.connect(
            lambda _=False, pid=producto_id: self._ajustar_stock_rapido(pid, 1)
        )

        btn_editar = self._boton("Editar", "editar", jerarquia="secundario", object_name="AccBtn", icon_size=14)
        btn_editar.setMinimumWidth(76)
        btn_editar.clicked.connect(
            lambda _=False, pid=producto_id: self._editar_producto_inventario(pid)
        )

        btn_eliminar = self._boton("Eliminar", "trash", jerarquia="critico", object_name="AccDangerBtn", icon_size=14)
        btn_eliminar.setMinimumWidth(84)
        btn_eliminar.clicked.connect(
            lambda _=False, pid=producto_id: self._eliminar_producto_inventario(pid)
        )

        for b in (btn_menos, btn_mas, btn_editar, btn_eliminar):
            lay.addWidget(b)
        lay.addStretch()
        return cont

    def refrescar_inventario(self):
        if not hasattr(self, "tbl_inventario"):
            return
        self._actualizar_ui_candado_inventario()
        simbolo = self.config.get("regional", "simbolo_moneda", "$")

        resumen = self.service.obtener_resumen_inventario()
        self.lbl_inv_total.setText(str(resumen["total_productos"]))
        self.lbl_inv_unidades.setText(f"{resumen['total_unidades']} unidades disponibles")

        alertas_tot = resumen["stock_bajo"] + resumen["agotados"]
        self.lbl_inv_alertas.setText(str(alertas_tot))
        if alertas_tot > 0:
            self.lbl_inv_alertas_sub.setText(
                f"{resumen['agotados']} agotados · {resumen['stock_bajo']} con stock bajo"
            )
        else:
            self.lbl_inv_alertas_sub.setText("Todo con existencia suficiente")

        self.lbl_inv_costo.setText(f"{simbolo}{resumen['valor_costo']:,.2f}")
        self.lbl_inv_venta.setText(f"{simbolo}{resumen['valor_venta']:,.2f}")
        self.lbl_inv_ganancia.setText(
            f"Ganancia est.: {simbolo}{resumen['ganancia_potencial']:,.2f}"
        )

        productos = self.service.listar_inventario(
            busqueda=self.txt_buscar_inv.text(),
            categoria=self.cmb_inv_cat.currentText(),
            filtro_stock=self.cmb_inv_stock.currentText(),
        )

        self.tbl_inventario.setRowCount(0)
        for i, p in enumerate(productos):
            self.tbl_inventario.insertRow(i)
            pid = int(p["id"])
            stock = int(p.get("stock") or 0)
            stock_min = int(
                p.get("stock_minimo") if p.get("stock_minimo") is not None else 2
            )
            if stock <= 0:
                txt_stock = "0 (Agotado)"
                color_stock = QColor("#ff9aab")
            elif stock <= stock_min:
                txt_stock = f"{stock} (Bajo)"
                color_stock = QColor("#f5b84b")
            else:
                txt_stock = str(stock)
                color_stock = None

            marca_ub = str(p.get("marca_modelo") or "").strip()
            ubic = str(p.get("ubicacion") or "").strip()
            detalle_mm = f"{marca_ub} · [{ubic}]" if (marca_ub and ubic) else (marca_ub or ubic or "—")

            vals = [
                str(pid),
                p.get("codigo") or "—",
                p.get("nombre", ""),
                p.get("categoria", ""),
                detalle_mm,
                txt_stock,
                f"{simbolo}{float(p.get('costo_compra') or 0.0):,.2f}",
                f"{simbolo}{float(p.get('precio_venta') or 0.0):,.2f}",
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                if c == 5 and color_stock is not None:
                    item.setForeground(color_stock)
                self.tbl_inventario.setItem(i, c, item)

            self.tbl_inventario.setCellWidget(
                i, 8, self._crear_botones_inventario(pid)
            )

    def _editar_inventario_doble_clic(self, item: QTableWidgetItem):
        fila = item.row()
        id_item = self.tbl_inventario.item(fila, 0)
        if id_item and id_item.text().isdigit():
            self._editar_producto_inventario(int(id_item.text()))

    def _dialogo_producto_inventario(self, actual: dict | None = None) -> dict | None:
        es_edicion = actual is not None
        dlg = AdaptiveDialog(self)
        dlg.setWindowTitle("Editar producto" if es_edicion else "Agregar producto al inventario")
        dlg.setMinimumWidth(460)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        txt_codigo = QLineEdit((actual or {}).get("codigo", ""))
        txt_codigo.setPlaceholderText("Código o SKU (opcional)")

        txt_nombre = QLineEdit((actual or {}).get("nombre", ""))
        txt_nombre.setPlaceholderText("Nombre del producto o refacción")

        cmb_cat = ContentCombo()
        cmb_cat.setEditable(True)
        cmb_cat.setInsertPolicy(QComboBox.NoInsert)
        cmb_cat.addItems(CATEGORIAS_INVENTARIO)
        cat_ini = (actual or {}).get("categoria", "Refacciones")
        if cat_ini:
            cmb_cat.setCurrentText(cat_ini)

        txt_mm = QLineEdit((actual or {}).get("marca_modelo", ""))
        txt_mm.setPlaceholderText("Marca y modelo compatible")

        spn_stock = QSpinBox()
        spn_stock.setRange(0, 999999)
        spn_stock.setValue(int((actual or {}).get("stock") or 0))

        spn_min = QSpinBox()
        spn_min.setRange(0, 999999)
        spn_min.setValue(
            int(actual["stock_minimo"])
            if actual and actual.get("stock_minimo") is not None
            else 2
        )

        spn_costo = QDoubleSpinBox()
        spn_costo.setRange(0, 999999)
        spn_costo.setDecimals(2)
        spn_costo.setValue(float((actual or {}).get("costo_compra") or 0.0))

        spn_precio = QDoubleSpinBox()
        spn_precio.setRange(0, 999999)
        spn_precio.setDecimals(2)
        spn_precio.setValue(float((actual or {}).get("precio_venta") or 0.0))

        lbl_margen = QLabel("$0.00")
        lbl_margen.setObjectName("CardSub")

        cmb_ubic = ContentCombo()
        cmb_ubic.setEditable(True)
        cmb_ubic.setInsertPolicy(QComboBox.NoInsert)
        cmb_ubic.addItem("")
        for u in self.service.listar_ubicaciones(solo_activas=True):
            cmb_ubic.addItem(u["nombre"])
        cmb_ubic.setCurrentText((actual or {}).get("ubicacion", ""))

        txt_notas = QLineEdit((actual or {}).get("notas", ""))
        txt_notas.setPlaceholderText("Proveedor, calidad o notas adicionales")

        simbolo = self.config.get("regional", "simbolo_moneda", "$")

        def _actualizar_margen():
            util = spn_precio.value() - spn_costo.value()
            lbl_margen.setText(f"{simbolo}{util:,.2f} por unidad")

        spn_costo.valueChanged.connect(_actualizar_margen)
        spn_precio.valueChanged.connect(_actualizar_margen)
        _actualizar_margen()

        form.addRow("Código / SKU:", txt_codigo)
        form.addRow("Producto *:", txt_nombre)
        form.addRow("Categoría:", cmb_cat)
        form.addRow("Marca / Modelo:", txt_mm)
        form.addRow("Stock disponible:", spn_stock)
        form.addRow("Alerta stock mínimo:", spn_min)
        form.addRow("Costo compra:", spn_costo)
        form.addRow("Precio venta:", spn_precio)
        form.addRow("Utilidad unitaria:", lbl_margen)
        form.addRow("Ubicación:", cmb_ubic)
        form.addRow("Notas / Proveedor:", txt_notas)
        lay.addLayout(form)

        resultado: dict = {}

        fila_btns = FlowLayout()
        fila_btns.setSpacing(10)
        btn_cancelar = self._boton("Cancelar", "cancelar", jerarquia="secundario", tooltip="Descartar cambios")
        btn_cancelar.clicked.connect(dlg.reject)
        btn_guardar = self._boton("Guardar cambios" if es_edicion else "Guardar producto", "guardar", jerarquia="principal", tooltip="Guardar")
        btn_guardar.setMinimumWidth(150)
        fila_btns.addStretch()
        fila_btns.addWidget(btn_cancelar)
        fila_btns.addWidget(btn_guardar)
        lay.addLayout(fila_btns)

        def _confirmar():
            if not txt_nombre.text().strip():
                QMessageBox.warning(
                    dlg, "Campo requerido", "Escribe el nombre del producto o refacción."
                )
                return
            resultado.update(
                {
                    "codigo": txt_codigo.text().strip(),
                    "nombre": txt_nombre.text().strip(),
                    "categoria": cmb_cat.currentText().strip() or "Refacciones",
                    "marca_modelo": txt_mm.text().strip(),
                    "stock": spn_stock.value(),
                    "stock_minimo": spn_min.value(),
                    "costo_compra": spn_costo.value(),
                    "precio_venta": spn_precio.value(),
                    "ubicacion": cmb_ubic.currentText().strip(),
                    "notas": txt_notas.text().strip(),
                }
            )
            dlg.accept()

        btn_guardar.clicked.connect(_confirmar)
        if dlg.exec() == QDialog.Accepted and resultado:
            return resultado
        return None

    def _agregar_producto_inventario(self):
        if not self._asegurar_edicion_inventario():
            return
        datos = self._dialogo_producto_inventario(None)
        if not datos:
            return
        self.service.guardar_producto_inventario(datos)
        self.refrescar_inventario()

    def _editar_producto_inventario(self, producto_id: int):
        if not self._asegurar_edicion_inventario():
            return
        actual = self.service.obtener_producto_inventario(producto_id)
        if not actual:
            QMessageBox.warning(self, "No encontrado", "El producto ya no existe.")
            return
        datos = self._dialogo_producto_inventario(actual)
        if not datos:
            return
        if self.service.actualizar_producto_inventario(producto_id, datos):
            self.refrescar_inventario()
        else:
            QMessageBox.warning(self, "No se guardó", "El producto ya no existe.")

    def _ajustar_stock_rapido(self, producto_id: int, delta: int):
        if not self._asegurar_edicion_inventario():
            return
        if self.service.ajustar_stock_inventario(producto_id, delta) is None:
            QMessageBox.warning(self, "No encontrado", "El producto ya no existe.")
            return
        self.refrescar_inventario()

    def _eliminar_producto_inventario(self, producto_id: int):
        if not self._asegurar_edicion_inventario():
            return
        actual = self.service.obtener_producto_inventario(producto_id)
        if not actual:
            QMessageBox.warning(self, "No encontrado", "El producto ya no existe.")
            return
        resp = QMessageBox.question(
            self,
            "Eliminar del inventario",
            f"¿Eliminar '{actual.get('nombre', '')}' del inventario?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        if self.service.eliminar_producto_inventario(producto_id):
            self.refrescar_inventario()
        else:
            QMessageBox.warning(self, "No se eliminó", "El producto ya no existe.")

    # ------------------------------------------
    # 5. UTILIDADES ANDROID (ADB, MALWARE Y DNS)
    # ------------------------------------------
    def _build_utilidades_android_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        head_row = FlowLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_t = QLabel("Utilidades Android (ADB)")
        lbl_t.setObjectName("Title")
        title_box.addWidget(lbl_t)

        head_row.addLayout(title_box)
        head_row.addStretch()
        lay.addLayout(head_row)

        # Tarjeta compartida de conexión ADB
        conn_card, conn_lay = _tarjeta("Conexión ADB", "Detecta y gestiona los equipos Android conectados")
        conn_fila = FlowLayout()
        conn_fila.setSpacing(10)
        self.lbl_adb_motor = QLabel("ADB:")
        self.lbl_adb_motor.setObjectName("FolioBadge")
        conn_fila.addWidget(self.lbl_adb_motor)

        self.cmb_adb_dispositivos = ContentCombo()
        self.cmb_adb_dispositivos.setMinimumWidth(220)
        self.cmb_adb_dispositivos.addItem(
            "Selecciona un equipo detectado", None
        )
        conn_fila.addWidget(self.cmb_adb_dispositivos, 1)

        btn_detectar = self._boton("Detectar equipos", "buscar", jerarquia="principal", object_name="WarningBtn", tooltip="Detectar los equipos Android conectados")
        btn_detectar.setMinimumWidth(150)
        btn_detectar.clicked.connect(lambda: self._detectar_equipos_adb(silencioso=False))
        conn_fila.addWidget(btn_detectar)

        btn_reiniciar_adb = self._boton("Reiniciar ADB", "refresh", jerarquia="secundario", tooltip="Reiniciar el servidor ADB")
        btn_reiniciar_adb.clicked.connect(self._reiniciar_servidor_adb)
        conn_fila.addWidget(btn_reiniciar_adb)

        conn_lay.addLayout(conn_fila)
        lay.addWidget(conn_card)

        # Subpestañas internas dentro de Utilidades Android
        tabs_android = QTabWidget()
        tabs_android.addTab(scroll_page(self._build_subtab_diagnostico_adb()), "Diagnóstico ADB")
        tabs_android.addTab(scroll_page(self._build_subtab_malware_adb()), "Remoción de Malware")
        tabs_android.addTab(scroll_page(self._build_subtab_dns_adb()), "Anclar DNS")
        lay.addWidget(tabs_android, 1)

        # Registro compacto de operaciones ADB
        log_box = QFrame()
        log_box.setObjectName("Card")
        log_lay = QVBoxLayout(log_box)
        log_lay.setContentsMargins(12, 8, 12, 8)
        log_lay.setSpacing(4)
        log_head = FlowLayout()
        lbl_reg = QLabel("Registro de actividad ADB")
        lbl_reg.setObjectName("CardSub")
        btn_limpiar_log = self._boton("Limpiar registro", "x", jerarquia="secundario", object_name="SecondaryBtn", tooltip="Borrar el registro de actividad")
        log_head.addWidget(lbl_reg)
        log_head.addStretch()
        log_head.addWidget(btn_limpiar_log)
        log_lay.addLayout(log_head)

        self.txt_adb_log = QPlainTextEdit()
        self.txt_adb_log.setReadOnly(True)
        self.txt_adb_log.setMinimumHeight(100)
        self.txt_adb_log.setPlaceholderText(
            "Aquí se mostrarán los resultados de diagnóstico, desinstalaciones y cambios de DNS..."
        )
        btn_limpiar_log.clicked.connect(self.txt_adb_log.clear)
        log_lay.addWidget(self.txt_adb_log)
        lay.addWidget(log_box)

        self._actualizar_estado_binario_adb()
        return w

    def _build_subtab_diagnostico_adb(self) -> QWidget:
        p = QWidget()
        lay = QVBoxLayout(p)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)

        # --- Bloque: acciones de diagnóstico ---
        diag_card = QFrame()
        diag_card.setObjectName("Card")
        d_lay = QVBoxLayout(diag_card)
        d_lay.setContentsMargins(12, 10, 12, 10)
        d_lay.setSpacing(8)
        lbl_diag_t = QLabel("Diagnóstico")
        lbl_diag_t.setObjectName("CardTitle")
        d_lay.addWidget(lbl_diag_t)

        row1 = FlowLayout()
        row1.setSpacing(10)
        btn_diag = self._boton("Ejecutar diagnóstico completo", "activity", jerarquia="principal", object_name="WarningBtn", tooltip="Ejecutar el diagnóstico completo del equipo")
        btn_diag.setMinimumWidth(250)
        btn_diag.clicked.connect(self._ejecutar_diagnostico_adb)
        btn_copiar = self._boton("Copiar reporte", "copiar", jerarquia="secundario", tooltip="Copiar el reporte al portapapeles")
        btn_copiar.clicked.connect(self._copiar_reporte_adb)
        row1.addWidget(btn_diag)
        row1.addWidget(btn_copiar)
        row1.addStretch()
        d_lay.addLayout(row1)

        row2 = FlowLayout()
        row2.setSpacing(10)
        btn_cap = self._boton("Captura de pantalla", "camara", jerarquia="secundario", tooltip="Tomar una captura de pantalla del equipo")
        btn_cap.clicked.connect(self._capturar_pantalla_adb)
        btn_orden = self._boton("Enviar a Nueva Orden", "mandar", jerarquia="secundario", tooltip="Pasa el diagnóstico a una nueva orden")
        btn_orden.clicked.connect(self._pasar_diag_a_nueva_orden)
        row2.addWidget(btn_cap)
        row2.addWidget(btn_orden)
        row2.addStretch()
        d_lay.addLayout(row2)
        lay.addWidget(diag_card)

        # --- Bloque: reinicio del equipo ---
        reboot_card = QFrame()
        reboot_card.setObjectName("Card")
        r_lay = QVBoxLayout(reboot_card)
        r_lay.setContentsMargins(12, 10, 12, 10)
        r_lay.setSpacing(8)
        lbl_reb_t = QLabel("Reinicio del equipo")
        lbl_reb_t.setObjectName("CardTitle")
        r_lay.addWidget(lbl_reb_t)

        self.cmb_adb_reboot = ContentCombo()
        self.cmb_adb_reboot.addItems(
            ["Reinicio normal", "Modo Recovery", "Modo Bootloader / Fastboot"]
        )
        btn_reboot = self._boton("Reiniciar equipo", "reiniciar", jerarquia="secundario", tooltip="Reiniciar el equipo en el modo seleccionado")
        btn_reboot.clicked.connect(self._reiniciar_equipo_adb)
        r_row = FlowLayout()
        r_row.setSpacing(10)
        r_row.addWidget(QLabel("Modo:"))
        r_row.addWidget(self.cmb_adb_reboot)
        r_row.addStretch()
        r_row.addWidget(btn_reboot)
        r_lay.addLayout(r_row)
        lay.addWidget(reboot_card)

        cards = FlowLayout()
        cards.setSpacing(10)
        c1, self.lbl_diag_modelo, self.lbl_diag_serie = _make_metric_card(
            "Equipo detectado", "—", "Serie / IMEI pendiente"
        )
        c2, self.lbl_diag_android, self.lbl_diag_parche = _make_metric_card(
            "Sistema Android", "—", "Parche de seguridad"
        )
        c3, self.lbl_diag_bat, self.lbl_diag_bat_sub = _make_metric_card(
            "Batería y Temperatura", "—", "Salud y voltaje"
        )
        c4, self.lbl_diag_mem, self.lbl_diag_ram = _make_metric_card(
            "Almacenamiento", "—", "Memoria RAM"
        )
        for c in (c1, c2, c3, c4):
            cards.addWidget(c)
        lay.addLayout(cards)

        self.txt_diag_reporte = QPlainTextEdit()
        self.txt_diag_reporte.setReadOnly(True)
        self.txt_diag_reporte.setPlaceholderText(
            "Conecta el equipo Android con Depuración USB activada y pulsa "
            "«Ejecutar diagnóstico completo» para ver marca, modelo, batería, temperatura, "
            "almacenamiento, RAM, resolución, IMEI y estado de DNS."
        )
        lay.addWidget(self.txt_diag_reporte, 1)
        return p

    def _build_subtab_malware_adb(self) -> QWidget:
        p = QWidget()
        lay = QVBoxLayout(p)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(10)

        top_bar = FlowLayout()
        top_bar.setSpacing(8)

        btn_escanear = self._boton("Escanear aplicaciones", "escudo", jerarquia="principal", object_name="WarningBtn", tooltip="Escanear las apps de usuario en busca de contenido sospechoso")
        btn_escanear.setMinimumWidth(190)
        btn_escanear.clicked.connect(self._escanear_malware_adb)

        btn_en_pantalla = self._boton("¿Qué app está en pantalla?", "ojo", jerarquia="secundario", tooltip="Identificar la app que se muestra en pantalla")
        btn_en_pantalla.setToolTip(
            "Útil cuando aparece un anuncio invasivo: identifica de inmediato qué paquete lo muestra."
        )
        btn_en_pantalla.clicked.connect(self._detectar_app_pantalla_adb)

        self.cmb_filtro_malware = ContentCombo()
        self.cmb_filtro_malware.addItems(
            [
                "Todas las apps de usuario",
                "Solo sospechosas / revisar",
                "Con permiso sobre otras apps",
            ]
        )
        self.cmb_filtro_malware.currentTextChanged.connect(self._refrescar_tabla_malware)

        self.txt_buscar_malware = QLineEdit()
        self.txt_buscar_malware.setPlaceholderText("Filtrar paquete Android")
        self.txt_buscar_malware.textChanged.connect(self._refrescar_tabla_malware)

        top_bar.addWidget(btn_escanear)
        top_bar.addWidget(btn_en_pantalla)
        top_bar.addWidget(self.cmb_filtro_malware)
        top_bar.addWidget(self.txt_buscar_malware, 1)
        lay.addLayout(top_bar)

        mid_bar = FlowLayout()
        self.lbl_resumen_malware = QLabel(
            "Escaneo pendiente. Se analizan únicamente apps instaladas por el usuario (protegiendo el sistema Android)."
        )
        self.lbl_resumen_malware.setObjectName("CardSub")

        btn_sel_sosp = self._boton("Marcar sospechosas", "alerta", jerarquia="secundario", tooltip="Marcar las apps marcadas como sospechosas")
        btn_sel_sosp.clicked.connect(self._marcar_sospechosas_malware)
        btn_desel = self._boton("Desmarcar todo", "x", jerarquia="secundario", tooltip="Desmarcar todas las apps")
        btn_desel.clicked.connect(self._desmarcar_todas_malware)

        mid_bar.addWidget(self.lbl_resumen_malware, 1)
        mid_bar.addWidget(btn_sel_sosp)
        mid_bar.addWidget(btn_desel)
        lay.addLayout(mid_bar)

        self.tbl_adb_malware = ReadableTable(0, 5)
        self.tbl_adb_malware.setHorizontalHeaderLabels(
            [
                "MARCAR",
                "NIVEL DE RIESGO",
                "PAQUETE (ID ANDROID)",
                "ESTADO",
                "MOTIVO / PERMISOS DETECTADOS",
            ]
        )
        _configurar_tabla(self.tbl_adb_malware, stretch_col=4)
        self.tbl_adb_malware.setColumnWidth(0, 75)
        self.tbl_adb_malware.setColumnWidth(1, 150)
        self.tbl_adb_malware.setColumnWidth(2, 260)
        self.tbl_adb_malware.setColumnWidth(3, 100)
        lay.addWidget(self.tbl_adb_malware, 1)

        bot_card = QFrame()
        bot_card.setObjectName("Card")
        b_lay = QVBoxLayout(bot_card)
        b_lay.setContentsMargins(12, 10, 12, 10)
        b_lay.setSpacing(8)
        lbl_bot_t = QLabel("Acciones sobre las aplicaciones marcadas")
        lbl_bot_t.setObjectName("CardTitle")
        b_lay.addWidget(lbl_bot_t)

        b_row1 = FlowLayout()
        b_row1.setSpacing(10)
        btn_quitar_ov = self._boton("Bloquear anuncios flotantes", "escudo-check", jerarquia="secundario", tooltip="Bloquear los anuncios flotantes de las apps marcadas")
        btn_quitar_ov.clicked.connect(self._bloquear_anuncios_seleccionados)
        btn_chrome = self._boton("Limpiar notificaciones spam de Chrome", "trash", jerarquia="secundario", tooltip="Limpiar las notificaciones spam de Chrome")
        btn_chrome.clicked.connect(self._limpiar_spam_chrome_adb)
        b_row1.addWidget(btn_quitar_ov)
        b_row1.addWidget(btn_chrome)
        b_row1.addStretch()
        b_lay.addLayout(b_row1)

        b_row2 = FlowLayout()
        b_row2.setSpacing(10)
        btn_desactivar = self._boton("Desactivar marcadas", "ojo-off", jerarquia="critico", tooltip="Desactivar (ocultar) las apps marcadas")
        btn_desactivar.clicked.connect(self._desactivar_malware_seleccionado)
        btn_desinstalar = self._boton("Desinstalar marcadas", "trash", jerarquia="critico", tooltip="Desinstalar las apps marcadas")
        btn_desinstalar.setMinimumWidth(175)
        btn_desinstalar.clicked.connect(self._desinstalar_malware_seleccionado)
        b_row2.addWidget(btn_desactivar)
        b_row2.addStretch()
        b_row2.addWidget(btn_desinstalar)
        b_lay.addLayout(b_row2)
        lay.addWidget(bot_card)
        return p

    def _build_subtab_dns_adb(self) -> QWidget:
        p = QWidget()
        lay = QVBoxLayout(p)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        estado_card = QFrame()
        estado_card.setObjectName("SubBar")
        est_lay = FlowLayout(estado_card)
        est_lay.setContentsMargins(16, 12, 16, 12)

        est_info = QVBoxLayout()
        lbl_est_t = QLabel("Estado actual de DNS Privado en el equipo")
        lbl_est_t.setObjectName("CardSub")
        self.lbl_dns_actual = QLabel("Sin consultar — conecta un equipo y pulsa «Leer DNS actual»")
        self.lbl_dns_actual.setObjectName("FolioBadge")
        est_info.addWidget(lbl_est_t)
        est_info.addWidget(self.lbl_dns_actual)

        btn_leer_dns = self._boton("Leer DNS actual", "wifi", jerarquia="secundario", tooltip="Consultar el DNS privado activo en el equipo")
        btn_leer_dns.clicked.connect(self._consultar_dns_actual_adb)

        est_lay.addLayout(est_info, 1)
        est_lay.addWidget(btn_leer_dns)
        lay.addWidget(estado_card)

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_lay = QVBoxLayout(form_card)
        form_lay.setContentsMargins(12, 10, 12, 10)
        form_lay.setSpacing(8)

        form = QFormLayout()
        form.setSpacing(10)

        self.cmb_dns_preset = ContentCombo()
        for prov in PROVEEDORES_DNS:
            self.cmb_dns_preset.addItem(prov["nombre"].split(" — ")[0], prov)
        self.cmb_dns_preset.currentIndexChanged.connect(self._al_cambiar_preset_dns)

        self.lbl_dns_desc = QLabel("")
        self.lbl_dns_desc.setObjectName("CardSub")
        self.lbl_dns_desc.setWordWrap(True)

        self.txt_dns_hostname = QLineEdit()
        self.txt_dns_hostname.setPlaceholderText("Ej. dns.adguard-dns.com o one.one.one.one")

        form.addRow("Proveedor recomendado:", self.cmb_dns_preset)
        form.addRow("Función:", self.lbl_dns_desc)
        form.addRow("Servidor DNS (TLS):", self.txt_dns_hostname)
        form_lay.addLayout(form)

        btns_dns = FlowLayout()
        btns_dns.setSpacing(8)

        btn_anclar = self._boton("Anclar DNS en el equipo", "escudo-check", jerarquia="principal", object_name="PrimaryBtn", tooltip="Anclar el servidor DNS privado en el equipo")
        btn_anclar.setMinimumWidth(195)
        btn_anclar.clicked.connect(self._anclar_dns_adb)

        btn_probar = self._boton("Probar conexión DNS", "check", jerarquia="secundario", tooltip="Verificar que el DNS anclado responde")
        btn_probar.clicked.connect(self._probar_dns_adb)

        btn_auto = self._boton("Restaurar DNS automático", "refresh", jerarquia="secundario", tooltip="Restaurar el DNS por defecto del sistema")
        btn_auto.clicked.connect(self._restaurar_dns_adb)

        btn_off = self._boton("Desactivar DNS privado", "ojo-off", jerarquia="critico", tooltip="Quitar el DNS privado anclado")
        btn_off.clicked.connect(self._desactivar_dns_adb)

        btns_dns.addWidget(btn_anclar)
        btns_dns.addWidget(btn_probar)
        btns_dns.addStretch()
        btns_dns.addWidget(btn_auto)
        btns_dns.addWidget(btn_off)
        form_lay.addLayout(btns_dns)

        nota_dns = QLabel(
            "Nota técnica: En Android 9.0 o superior, el DNS anclado queda guardado globalmente "
            "tanto para redes Wi-Fi como para Datos móviles y permanece activo aunque el equipo "
            "se apague o reinicie. Ideal para bloquear publicidad emergente tras una limpieza de malware."
        )
        nota_dns.setObjectName("CardSub")
        nota_dns.setWordWrap(True)
        form_lay.addWidget(nota_dns)

        lay.addWidget(form_card)
        lay.addStretch()

        self._al_cambiar_preset_dns()
        return p

    # --- Métodos auxiliares de Utilidades Android ---
    def _log_adb(self, mensaje: str):
        if not hasattr(self, "txt_adb_log"):
            return
        hora = datetime.now().strftime("%H:%M:%S")
        self.txt_adb_log.appendPlainText(f"[{hora}] {mensaje}")

    def _ejecutar_con_espera(self, fn):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        try:
            return fn()
        finally:
            QApplication.restoreOverrideCursor()

    def _actualizar_estado_binario_adb(self):
        if not hasattr(self, "lbl_adb_motor"):
            return
        ok, ruta = self.adb.resolver_ruta_adb()
        if ok:
            self.lbl_adb_motor.setText("ADB listo:")
            self.lbl_adb_motor.setToolTip(ruta)
        else:
            self.lbl_adb_motor.setText("ADB no localizado:")
            self.lbl_adb_motor.setToolTip("ADB se busca automáticamente en platform-tools y en el PATH del sistema.")

    def _detectar_equipos_adb(self, silencioso: bool = False) -> str | None:
        info = self._ejecutar_con_espera(self.adb.listar_dispositivos)
        self._actualizar_estado_binario_adb()

        seleccion_previa = self.cmb_adb_dispositivos.currentData()
        serial_previo = seleccion_previa.get("serial") if isinstance(seleccion_previa, dict) else None

        self.cmb_adb_dispositivos.blockSignals(True)
        self.cmb_adb_dispositivos.clear()
        dispositivos = info.get("dispositivos", [])
        if not dispositivos:
            self.cmb_adb_dispositivos.addItem("-- Sin equipos detectados --", None)
        else:
            idx_elegir = 0
            for i, d in enumerate(dispositivos):
                texto = f"{d['modelo']} [{d['serial']}] — {d['estado_legible']}"
                self.cmb_adb_dispositivos.addItem(texto, d)
                if serial_previo and d["serial"] == serial_previo:
                    idx_elegir = i
                elif d["estado"] == "device" and idx_elegir == 0:
                    idx_elegir = i
            self.cmb_adb_dispositivos.setCurrentIndex(idx_elegir)
        self.cmb_adb_dispositivos.blockSignals(False)

        self._log_adb(info.get("mensaje", ""))
        if not silencioso:
            if not info.get("adb_ok"):
                QMessageBox.warning(self, "ADB no encontrado", info.get("mensaje", ""))
            elif not dispositivos:
                QMessageBox.information(self, "Sin equipos", info.get("mensaje", ""))

        actual = self.cmb_adb_dispositivos.currentData()
        if isinstance(actual, dict) and actual.get("estado") == "device":
            return actual["serial"]
        return None

    def _reiniciar_servidor_adb(self):
        ok, msg = self._ejecutar_con_espera(self.adb.reiniciar_servidor)
        self._log_adb(msg)
        if ok:
            self._detectar_equipos_adb(silencioso=True)
            QMessageBox.information(self, "ADB reiniciado", msg)
        else:
            QMessageBox.warning(self, "ADB", msg)

    def _serial_adb_listo(self) -> str | None:
        actual = self.cmb_adb_dispositivos.currentData()
        if not isinstance(actual, dict):
            serial_auto = self._detectar_equipos_adb(silencioso=True)
            if serial_auto:
                return serial_auto
            actual = self.cmb_adb_dispositivos.currentData()

        if not isinstance(actual, dict):
            QMessageBox.information(
                self,
                "Conecta un equipo Android",
                "No se detectó ningún equipo conectado por USB.\n\n"
                "Verifica el cable de datos y activa «Depuración por USB» en Opciones de desarrollador.",
            )
            return None

        if actual.get("estado") != "device":
            QMessageBox.warning(
                self,
                "Equipo no autorizado o no listo",
                f"Estado actual del equipo ({actual.get('serial')}): {actual.get('estado_legible')}.\n\n"
                "Desbloquea el celular y acepta la ventana «Permitir depuración por USB», "
                "luego vuelve a pulsar «Detectar equipos».",
            )
            return None

        return str(actual["serial"])

    # --- Acciones de Diagnóstico ADB ---
    def _ejecutar_diagnostico_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        res = self._ejecutar_con_espera(lambda: self.adb.diagnosticar_equipo(serial))
        if not res.get("ok"):
            err = res.get("error", "Error durante el diagnóstico.")
            self._log_adb(f"Error diagnóstico: {err}")
            QMessageBox.warning(self, "Diagnóstico ADB", err)
            return

        self._ultimo_diag_adb = res
        self.lbl_diag_modelo.setText(f"{res['marca']} {res['modelo']}".strip())
        self.lbl_diag_serie.setText(f"Serie: {res['serie_real']}")
        self.lbl_diag_android.setText(f"Android {res['android_version']} (API {res['sdk_int']})")
        self.lbl_diag_parche.setText(f"Parche: {res['parche_seguridad']}")

        bat = res["bateria"]
        nivel_str = f"{bat['nivel']}%" if bat["nivel"] >= 0 else "N/D"
        temp_str = f"{bat['temperatura_c']} °C" if bat["temperatura_c"] > 0 else "N/D"
        self.lbl_diag_bat.setText(f"{nivel_str} · {temp_str}")
        self.lbl_diag_bat_sub.setText(f"{bat['salud']} · {bat['estado']}")

        alm = res["almacenamiento"]
        if alm.get("total_gb", 0) > 0:
            self.lbl_diag_mem.setText(f"{alm['libre_gb']} GB libres / {alm['total_gb']} GB")
        else:
            self.lbl_diag_mem.setText("N/D")
        self.lbl_diag_ram.setText(f"RAM: {res['ram'].get('resumen', 'N/D')}")

        self.txt_diag_reporte.setPlainText(res["texto_reporte"])
        dns_desc = res.get("dns", {}).get("descripcion_corta", "")
        if dns_desc and hasattr(self, "lbl_dns_actual"):
            self.lbl_dns_actual.setText(dns_desc)

        self._log_adb(f"Diagnóstico completado para {res['marca']} {res['modelo']} ({serial}).")

    def _capturar_pantalla_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        carpeta = os.path.join(
            os.path.dirname(os.path.abspath(self.db.db_path)), "capturas_adb"
        )
        marca_t = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = os.path.join(carpeta, f"captura_{marca_t}.png")
        ok, detalle = self._ejecutar_con_espera(
            lambda: self.adb.capturar_pantalla(serial, ruta)
        )
        if not ok:
            self._log_adb(f"Error captura: {detalle}")
            QMessageBox.warning(self, "Captura de pantalla", detalle)
            return

        self._log_adb(f"Captura guardada en {ruta}")
        pm = QPixmap(ruta)
        if not pm.isNull():
            QApplication.clipboard().setPixmap(pm)

        dlg = AdaptiveDialog(self)
        dlg.setWindowTitle("Captura de pantalla del equipo")
        dlg.setMinimumWidth(460)
        lay = QVBoxLayout(dlg)
        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignCenter)
        if not pm.isNull():
            lbl_img.setPixmap(pm.scaled(380, 520, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lay.addWidget(lbl_img, 1)
        lbl_r = QLabel(f"Copiada al portapapeles y guardada en:\n{ruta}")
        lbl_r.setObjectName("CardSub")
        lbl_r.setWordWrap(True)
        lay.addWidget(lbl_r)

        btns = FlowLayout()
        btns.setSpacing(10)
        b_abrir = self._boton("Abrir imagen", "ojo", jerarquia="secundario", tooltip="Abrir la imagen del ticket")
        b_abrir.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(ruta)))
        b_carp = self._boton("Abrir carpeta", "descargar", jerarquia="secundario", tooltip="Abrir la carpeta del ticket")
        b_carp.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(ruta)))
        )
        b_cerrar = self._boton("Cerrar", "x", jerarquia="secundario", tooltip="Cerrar")
        b_cerrar.clicked.connect(dlg.accept)
        for b in (b_abrir, b_carp, b_cerrar):
            btns.addWidget(b)
        lay.addLayout(btns)
        dlg.exec()

    def _copiar_reporte_adb(self):
        texto = self.txt_diag_reporte.toPlainText().strip()
        if not texto:
            QMessageBox.information(
                self, "Sin reporte", "Primero ejecuta el diagnóstico del equipo."
            )
            return
        QApplication.clipboard().setText(texto)
        self._log_adb("Reporte de diagnóstico copiado al portapapeles.")
        QMessageBox.information(
            self, "Copiado", "El reporte completo se copió al portapapeles."
        )

    def _pasar_diag_a_nueva_orden(self):
        if not self._ultimo_diag_adb:
            QMessageBox.information(
                self,
                "Sin diagnóstico",
                "Primero ejecuta el diagnóstico completo para leer los datos del equipo.",
            )
            return
        d = self._ultimo_diag_adb
        self.no_cat.setCurrentText("Celulares")
        self._actualizar_subcategorias_marca("Celulares")
        self.no_marca.setCurrentText(d.get("marca", ""))
        self.no_modelo.setText(d.get("modelo", ""))
        imei_val = d.get("imei", "")
        if imei_val and not imei_val.startswith("Protegido"):
            self.no_imei.setText(imei_val)
        else:
            self.no_imei.setText(d.get("serie_real", ""))
        bat = d.get("bateria", {})
        resumen_tec = (
            f"ADB: Android {d.get('android_version')} · Bat {bat.get('nivel', '?')}% "
            f"({bat.get('salud', '')}, {bat.get('temperatura_c', 0)}°C) · "
            f"Alm: {d.get('almacenamiento', {}).get('resumen', '')}"
        )
        self.no_notas.setPlainText(resumen_tec)
        self.ir_a_seccion(1)
        QMessageBox.information(
            self,
            "Datos cargados",
            "Se copiaron marca, modelo, serie/IMEI y resumen técnico al formulario de Nueva Orden.",
        )

    def _reiniciar_equipo_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        opcion = self.cmb_adb_reboot.currentText()
        modo = ""
        if "Recovery" in opcion:
            modo = "recovery"
        elif "Bootloader" in opcion:
            modo = "bootloader"

        resp = QMessageBox.question(
            self,
            "Reiniciar equipo",
            f"¿Enviar orden de «{opcion}» al equipo conectado ({serial})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        ok, msg = self._ejecutar_con_espera(lambda: self.adb.reiniciar_equipo(serial, modo))
        self._log_adb(msg)
        if ok:
            QMessageBox.information(self, "Reinicio enviado", msg)
        else:
            QMessageBox.warning(self, "No se pudo reiniciar", msg)

    # --- Acciones de Remoción de Malware ---
    def _escanear_malware_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        res = self._ejecutar_con_espera(lambda: self.adb.escanear_malware(serial))
        if not res.get("ok"):
            err = res.get("error", "No se pudo completar el escaneo.")
            self._log_adb(f"Error escaneo malware: {err}")
            QMessageBox.warning(self, "Escaneo de aplicaciones", err)
            return

        self._apps_malware_cache = res.get("apps", [])
        self.lbl_resumen_malware.setText(
            f"Apps de usuario analizadas: {res['total']} · "
            f"Sospechosas / a revisar: {res['sospechosas']} "
            f"(Riesgo alto: {res['alto_riesgo']})"
        )
        self._refrescar_tabla_malware()
        self._log_adb(
            f"Escaneo finalizado: {res['total']} apps de usuario, {res['sospechosas']} sospechosas."
        )

    def _refrescar_tabla_malware(self):
        if not hasattr(self, "tbl_adb_malware"):
            return
        filtro = self.cmb_filtro_malware.currentText()
        busq = self.txt_buscar_malware.text().strip().lower()

        lista = self._apps_malware_cache
        if filtro == "Solo sospechosas / revisar":
            lista = [a for a in lista if a["prioridad"] >= 1]
        elif filtro == "Con permiso sobre otras apps":
            lista = [a for a in lista if a.get("tiene_overlay")]

        if busq:
            lista = [
                a
                for a in lista
                if busq in a["package"].lower() or busq in a["motivos"].lower()
            ]

        self.tbl_adb_malware.setRowCount(0)
        for i, app_info in enumerate(lista):
            self.tbl_adb_malware.insertRow(i)

            chk_item = QTableWidgetItem("")
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, app_info["package"])
            self.tbl_adb_malware.setItem(i, 0, chk_item)

            riesgo_item = QTableWidgetItem(app_info["riesgo"])
            if app_info["prioridad"] >= 2:
                riesgo_item.setForeground(QColor("#ff9aab"))
            elif app_info["prioridad"] == 1:
                riesgo_item.setForeground(QColor("#f5b84b"))
            self.tbl_adb_malware.setItem(i, 1, riesgo_item)

            self.tbl_adb_malware.setItem(i, 2, QTableWidgetItem(app_info["package"]))
            self.tbl_adb_malware.setItem(i, 3, QTableWidgetItem(app_info["estado"]))
            self.tbl_adb_malware.setItem(i, 4, QTableWidgetItem(app_info["motivos"]))

    def _marcar_sospechosas_malware(self):
        marcadas = 0
        for fila in range(self.tbl_adb_malware.rowCount()):
            riesgo_txt = self.tbl_adb_malware.item(fila, 1).text()
            chk = self.tbl_adb_malware.item(fila, 0)
            if chk and ("ALTO" in riesgo_txt or "REVISAR" in riesgo_txt):
                chk.setCheckState(Qt.Checked)
                marcadas += 1
        if marcadas == 0:
            QMessageBox.information(
                self, "Sin sospechosas", "No hay aplicaciones sospechosas en la lista actual."
            )

    def _desmarcar_todas_malware(self):
        for fila in range(self.tbl_adb_malware.rowCount()):
            chk = self.tbl_adb_malware.item(fila, 0)
            if chk:
                chk.setCheckState(Qt.Unchecked)

    def _paquetes_malware_seleccionados(self) -> list[str]:
        seleccionados: list[str] = []
        for fila in range(self.tbl_adb_malware.rowCount()):
            chk = self.tbl_adb_malware.item(fila, 0)
            if chk and chk.checkState() == Qt.Checked:
                pkg = chk.data(Qt.UserRole)
                if pkg:
                    seleccionados.append(str(pkg))
        return seleccionados

    def _detectar_app_pantalla_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        res = self._ejecutar_con_espera(lambda: self.adb.detectar_app_en_pantalla(serial))
        if not res.get("ok"):
            QMessageBox.warning(
                self, "App en pantalla", res.get("error", "No se pudo detectar.")
            )
            return

        pkg = res["package"]
        es_usr = res["es_usuario"]
        es_prot = res["es_protegido"]
        self._log_adb(f"App activa en pantalla detectada: {pkg}")

        if es_prot or not es_usr:
            QMessageBox.information(
                self,
                "Aplicación en primer plano",
                f"Paquete actual en pantalla:\n{pkg}\n\n"
                "Corresponde a una aplicación del sistema o preinstalada.",
            )
            return

        resp = QMessageBox.question(
            self,
            "Aplicación de usuario detectada en pantalla",
            f"La ventana o anuncio actual pertenece al paquete:\n\n{pkg}\n\n"
            "¿Deseas desinstalar esta aplicación del equipo ahora mismo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            ok, msg = self._ejecutar_con_espera(
                lambda: self.adb.desinstalar_paquete(serial, pkg)
            )
            self._log_adb(msg)
            if ok:
                QMessageBox.information(self, "Eliminada", msg)
                self._escanear_malware_adb()
            else:
                QMessageBox.warning(self, "No se pudo eliminar", msg)

    def _bloquear_anuncios_seleccionados(self):
        pkgs = self._paquetes_malware_seleccionados()
        if not pkgs:
            QMessageBox.information(
                self, "Selecciona aplicaciones", "Marca al menos una aplicación en la columna «MARCAR»."
            )
            return
        serial = self._serial_adb_listo()
        if not serial:
            return

        exitos = 0
        for pkg in pkgs:
            ok, msg = self._ejecutar_con_espera(
                lambda p=pkg: self.adb.revocar_superposicion(serial, p)
            )
            self._log_adb(msg)
            if ok:
                exitos += 1

        self._escanear_malware_adb()
        QMessageBox.information(
            self,
            "Permisos actualizados",
            f"Se bloquearon permisos de anuncios superpuestos e instalación en {exitos} de {len(pkgs)} app(s).",
        )

    def _desactivar_malware_seleccionado(self):
        pkgs = self._paquetes_malware_seleccionados()
        if not pkgs:
            QMessageBox.information(
                self, "Selecciona aplicaciones", "Marca al menos una aplicación en la tabla."
            )
            return
        serial = self._serial_adb_listo()
        if not serial:
            return
        resp = QMessageBox.question(
            self,
            "Desactivar aplicaciones",
            f"¿Congelar / desactivar {len(pkgs)} aplicación(es) seleccionada(s)?\n\n"
            + "\n".join(f"• {p}" for p in pkgs[:10]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        exitos = 0
        for pkg in pkgs:
            ok, msg = self._ejecutar_con_espera(
                lambda p=pkg: self.adb.desactivar_paquete(serial, p)
            )
            self._log_adb(msg)
            if ok:
                exitos += 1

        self._escanear_malware_adb()
        QMessageBox.information(
            self,
            "Resultado",
            f"Se desactivaron {exitos} de {len(pkgs)} aplicación(es).",
        )

    def _desinstalar_malware_seleccionado(self):
        pkgs = self._paquetes_malware_seleccionados()
        if not pkgs:
            QMessageBox.information(
                self, "Selecciona aplicaciones", "Marca las aplicaciones que deseas desinstalar."
            )
            return
        serial = self._serial_adb_listo()
        if not serial:
            return

        lista_previa = "\n".join(f"• {p}" for p in pkgs[:12])
        if len(pkgs) > 12:
            lista_previa += f"\n... y {len(pkgs) - 12} más."

        resp = QMessageBox.question(
            self,
            "Desinstalar aplicaciones",
            f"¿Desinstalar permanentemente estas {len(pkgs)} aplicación(es) del teléfono?\n\n"
            f"{lista_previa}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        exitos = 0
        errores: list[str] = []
        for pkg in pkgs:
            ok, msg = self._ejecutar_con_espera(
                lambda p=pkg: self.adb.desinstalar_paquete(serial, p)
            )
            self._log_adb(msg)
            if ok:
                exitos += 1
            else:
                errores.append(msg)

        self._escanear_malware_adb()
        resumen = f"Aplicaciones desinstaladas correctamente: {exitos} de {len(pkgs)}."
        if errores:
            resumen += "\n\nAvisos:\n" + "\n".join(errores[:5])
        QMessageBox.information(self, "Limpieza completada", resumen)

    def _limpiar_spam_chrome_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        resp = QMessageBox.question(
            self,
            "Limpiar notificaciones falsas de Chrome",
            "Esta función borra los datos y permisos de sitios web en Google Chrome "
            "(elimina falsas alertas de virus que llegan en la barra de notificaciones).\n\n"
            "Nota: se cerrarán las pestañas abiertas de Chrome en el celular.\n¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        ok, msg = self._ejecutar_con_espera(
            lambda: self.adb.limpiar_spam_navegador(serial, "com.android.chrome")
        )
        self._log_adb(msg)
        if ok:
            QMessageBox.information(self, "Navegador limpio", msg)
        else:
            QMessageBox.warning(self, "Aviso", msg)

    # --- Acciones de Anclar DNS ---
    def _al_cambiar_preset_dns(self):
        if not hasattr(self, "cmb_dns_preset"):
            return
        prov = self.cmb_dns_preset.currentData()
        if not isinstance(prov, dict):
            return
        self.lbl_dns_desc.setText(prov.get("descripcion", ""))
        host = prov.get("hostname", "")
        if host:
            self.txt_dns_hostname.setText(host)
        else:
            self.txt_dns_hostname.clear()
            self.txt_dns_hostname.setFocus()

    def _consultar_dns_actual_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        info = self._ejecutar_con_espera(lambda: self.adb.obtener_estado_dns(serial))
        desc = info.get("descripcion_corta", "No disponible")
        self.lbl_dns_actual.setText(desc)
        self._log_adb(f"DNS actual en equipo ({serial}): {desc}")

    def _anclar_dns_adb(self):
        servidor = self.txt_dns_hostname.text().strip()
        if not servidor:
            QMessageBox.warning(
                self, "Falta servidor DNS", "Selecciona un proveedor o escribe un servidor DNS."
            )
            return
        serial = self._serial_adb_listo()
        if not serial:
            return

        ok, msg = self._ejecutar_con_espera(lambda: self.adb.anclar_dns(serial, servidor))
        self._log_adb(msg.replace("\n", " "))
        if ok:
            self._consultar_dns_actual_adb()
            QMessageBox.information(self, "DNS anclado", msg)
        else:
            QMessageBox.warning(self, "No se pudo anclar el DNS", msg)

    def _restaurar_dns_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        ok, msg = self._ejecutar_con_espera(
            lambda: self.adb.restaurar_dns_automatico(serial)
        )
        self._log_adb(msg)
        if ok:
            self._consultar_dns_actual_adb()
            QMessageBox.information(self, "DNS restaurado", msg)
        else:
            QMessageBox.warning(self, "Aviso", msg)

    def _desactivar_dns_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        ok, msg = self._ejecutar_con_espera(lambda: self.adb.desactivar_dns_privado(serial))
        self._log_adb(msg)
        if ok:
            self._consultar_dns_actual_adb()
            QMessageBox.information(self, "DNS desactivado", msg)
        else:
            QMessageBox.warning(self, "Aviso", msg)

    def _probar_dns_adb(self):
        serial = self._serial_adb_listo()
        if not serial:
            return
        ok, msg = self._ejecutar_con_espera(
            lambda: self.adb.probar_conectividad_dns(serial)
        )
        self._log_adb(msg.splitlines()[0] if msg else "")
        if ok:
            QMessageBox.information(self, "Prueba exitosa", msg)
        else:
            QMessageBox.warning(self, "Sin respuesta de red", msg)

    # ------------------------------------------
    # 6. CONFIGURACIÓN DE TALLER
    # ------------------------------------------
    def _build_config_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        lbl = QLabel("Configuración de Taller")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        form.setSpacing(10)
        form.setContentsMargins(14, 12, 14, 12)

        self.cfg_nombre = QLineEdit(
            self.config.get("identidad", "nombre_establecimiento", "ABCell")
        )
        self.cfg_tel = QLineEdit(self.config.get("contacto", "telefono", ""))
        self.cfg_dir = QLineEdit(self.config.get("contacto", "direccion", ""))
        # --- Impresión de tickets: detecta automáticamente la impresora de Windows ---
        imp_card = QFrame()
        imp_card.setObjectName("Card")
        imp_lay = QVBoxLayout(imp_card)
        imp_lay.setContentsMargins(12, 10, 12, 10)
        imp_lay.setSpacing(8)

        lbl_imp_t = QLabel("Impresión de tickets")
        lbl_imp_t.setObjectName("CardTitle")
        self.lbl_imp_auto = QLabel("Detectando la impresora predeterminada de Windows...")
        self.lbl_imp_auto.setObjectName("CardSub")
        self.lbl_imp_auto.setWordWrap(True)
        btn_probar_imp = self._boton("Probar impresión", "imprimir", jerarquia="secundario", tooltip="Imprimir una prueba de ticket")
        btn_probar_imp.setMinimumWidth(160)
        btn_probar_imp.clicked.connect(self._probar_impresora)
        imp_lay.addWidget(lbl_imp_t)
        imp_lay.addWidget(self.lbl_imp_auto)
        imp_lay.addWidget(btn_probar_imp, alignment=Qt.AlignLeft)

        # --- Botón de engranaje para elegir el tema (selector emergente) ---
        self.btn_gearra_tema = self._boton_icono("gearra", "GearBtn", "Cambiar tema visual", 22)
        self.btn_gearra_tema.setMinimumWidth(34)
        self.btn_gearra_tema.setMinimumHeight(34)
        self.btn_gearra_tema.clicked.connect(self._abrir_selector_tema)

        self.lbl_tema_actual = QLabel("Tema: " + self._tema_actual())
        self.lbl_tema_actual.setObjectName("CardSub")

        row_tema = FlowLayout()
        row_tema.setSpacing(8)
        row_tema.addWidget(self.btn_gearra_tema)
        row_tema.addWidget(self.lbl_tema_actual)
        row_tema.addStretch()

        row_logo = FlowLayout()
        row_logo.setSpacing(10)
        self.cfg_logo = QLineEdit(self.config.get("identidad", "logo_personalizado", ""))
        btn_logo = self._boton("Elegir logo", "ojo", jerarquia="secundario", tooltip="Elegir una imagen de logo personalizada")
        btn_logo.clicked.connect(self._elegir_logo)
        row_logo.addWidget(self.cfg_logo, 1)
        row_logo.addWidget(btn_logo)

        form.addRow("Nombre del negocio:", self.cfg_nombre)
        form.addRow("Teléfono / WhatsApp:", self.cfg_tel)
        form.addRow("Dirección:", self.cfg_dir)
        form.addRow("Impresión de tickets:", imp_card)
        form.addRow("Tema visual:", row_tema)
        form.addRow("Logo personalizado:", row_logo)

        self.cfg_garantia = QPlainTextEdit()
        self.cfg_garantia.setPlainText(
            str(self.config.get("notas", "politicas_garantia", "") or "")
        )
        self.cfg_garantia.setMinimumHeight(100)
        self.cfg_garantia.setPlaceholderText(
            "Escribe aqui las politicas de garantia que se imprimen en la nota..."
        )
        lbl_garantia_ayuda = QLabel(
            "Se imprime al final de cada nota. Cada renglon se ajusta al "
            "ancho del ticket. Si lo dejas vacio, no se imprime."
        )
        lbl_garantia_ayuda.setObjectName("CardSub")
        lbl_garantia_ayuda.setWordWrap(True)
        btn_garantia_ejemplo = self._boton("Insertar texto de ejemplo", "info", jerarquia="secundario", tooltip="Insertar un texto de ejemplo para las políticas de garantía")
        btn_garantia_ejemplo.clicked.connect(self._insertar_garantia_ejemplo)

        box_garantia = QVBoxLayout()
        box_garantia.setSpacing(6)
        box_garantia.addWidget(self.cfg_garantia)
        box_garantia.addWidget(lbl_garantia_ayuda)
        box_garantia.addWidget(btn_garantia_ejemplo, alignment=Qt.AlignLeft)
        form.addRow("Políticas de garantía:", box_garantia)

        lay.addWidget(card)

        card_seg = QFrame()
        card_seg.setObjectName("Card")
        seg_lay = QVBoxLayout(card_seg)
        seg_lay.setContentsMargins(18, 14, 18, 14)
        lbl_seg = QLabel(
            "Modo maestro: presiona Ctrl+P en cualquier pantalla para entrar "
            "con tu código maestro."
        )
        lbl_seg.setObjectName("CardSub")
        lbl_seg.setWordWrap(True)
        seg_lay.addWidget(lbl_seg)
        lay.addWidget(card_seg)

        btn_save = self._boton("Guardar Configuración", "guardar", jerarquia="principal", object_name="PrimaryBtn", tooltip="Guardar todos los cambios de configuración")
        btn_save.setMinimumWidth(195)
        lay.addWidget(btn_save, alignment=Qt.AlignRight)
        lay.addStretch()

        scroll.setWidget(w)
        self._actualizar_estado_impresora()
        return scroll

    def _definir_codigo_maestro(self, autorizado: bool = False):
        if self.config.tiene_codigo_maestro() and not autorizado:
            if not self._autorizar_con_codigo("cambiar el código maestro"):
                return
        nuevo, ok = QInputDialog.getText(
            self,
            "Nuevo código maestro",
            "Escribe el nuevo código (mínimo 4 caracteres):",
            QLineEdit.EchoMode.Password,
        )
        if not ok:
            return
        nuevo = nuevo.strip()
        if len(nuevo) < 4:
            QMessageBox.warning(self, "Código muy corto", "Usa al menos 4 caracteres.")
            return
        repetido, ok = QInputDialog.getText(
            self, "Repite el código", "Escribe el código otra vez:", QLineEdit.EchoMode.Password
        )
        if not ok or repetido.strip() != nuevo:
            QMessageBox.warning(self, "No coinciden", "Los códigos no coinciden. No se cambió nada.")
            return
        self.config.definir_codigo_maestro(nuevo)
        self.config.save()
        self.inventario_desbloqueado = False
        self._actualizar_ui_candado_inventario()
        QMessageBox.information(self, "Código maestro", "El código maestro quedó guardado.")

    def _abrir_modo_maestro(self):
        if not self.config.tiene_codigo_maestro():
            QMessageBox.information(
                self,
                "Modo maestro",
                "Todavía no hay un código maestro. Crea uno ahora.",
            )
            self._definir_codigo_maestro(autorizado=True)
            if not self.config.tiene_codigo_maestro():
                return
        elif not self._autorizar_con_codigo("entrar al modo maestro"):
            return

        dlg = AdaptiveDialog(self)
        dlg.setWindowTitle("Modo maestro")
        dlg.setMinimumWidth(440)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(10)

        titulo = QLabel("Modo maestro")
        titulo.setObjectName("Title")
        ayuda = QLabel(
            "Acciones protegidas. Antes de borrar se crea un respaldo "
            "automático en la carpeta 'respaldos'."
        )
        ayuda.setObjectName("CardSub")
        ayuda.setWordWrap(True)

        btn_ordenes = self._boton("Borrar todas las órdenes", "trash", jerarquia="critico", tooltip="Eliminar todas las órdenes (con respaldo)")
        btn_ordenes.clicked.connect(
            lambda _=False: self._borrar_todas_las_ordenes(autorizado=True)
        )
        btn_base = self._boton("Restablecer base de datos completa", "base-datos", jerarquia="critico", tooltip="Restablecer toda la base de datos")
        btn_base.clicked.connect(
            lambda _=False: self._restablecer_base_completa(autorizado=True)
        )
        btn_codigo = self._boton("Cambiar código maestro", "editar", jerarquia="secundario", tooltip="Definir un nuevo código maestro")
        btn_codigo.clicked.connect(
            lambda _=False: self._definir_codigo_maestro(autorizado=True)
        )
        btn_cerrar = self._boton("Cerrar", "x", jerarquia="secundario", tooltip="Cerrar")
        btn_cerrar.clicked.connect(dlg.accept)

        for widget in (titulo, ayuda, btn_ordenes, btn_base, btn_codigo, btn_cerrar):
            lay.addWidget(widget)
        dlg.exec()

    def _confirmar_borrado(self, titulo: str, texto: str) -> bool:
        si_no = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        resp = QMessageBox.question(
            self, titulo, texto, si_no, QMessageBox.StandardButton.No
        )
        return resp == QMessageBox.StandardButton.Yes

    def _borrar_todas_las_ordenes(self, autorizado: bool = False):
        if not autorizado and not self._autorizar_con_codigo(
            "borrar todas las órdenes", obligatorio=True
        ):
            return
        total = len(self.service.listar_ordenes())
        if not self._confirmar_borrado(
            "Borrar todas las órdenes",
            f"Se borrarán las {total} órdenes con sus pagos y avisos, y los folios "
            "volverán a empezar en 1.\n\nEl catálogo de servicios y las ubicaciones "
            "se conservan. Se hará un respaldo antes.\n\n¿Continuar?",
        ):
            return
        try:
            respaldo = self.db.respaldar()
        except Exception as exc:
            QMessageBox.critical(
                self, "Sin respaldo", f"No se pudo crear el respaldo, no se borró nada:\n{exc}"
            )
            return
        self.db.restablecer_ordenes()
        self.lbl_folio_sel.setText("Selecciona una orden")
        self.refrescar_todo()
        QMessageBox.information(
            self, "Órdenes borradas", f"Listo. Respaldo guardado en:\n{respaldo}"
        )

    def _restablecer_base_completa(self, autorizado: bool = False):
        if not autorizado and not self._autorizar_con_codigo(
            "restablecer la base de datos", obligatorio=True
        ):
            return
        if not self._confirmar_borrado(
            "Restablecer base de datos",
            "Se borrarán TODAS las órdenes, el inventario, el catálogo de servicios con tus precios "
            "y las ubicaciones. Quedarán solo los datos de ejemplo iniciales.\n\n"
            "Se hará un respaldo antes.\n\n¿Seguro que quieres continuar?",
        ):
            return
        try:
            respaldo = self.db.respaldar()
        except Exception as exc:
            QMessageBox.critical(
                self, "Sin respaldo", f"No se pudo crear el respaldo, no se borró nada:\n{exc}"
            )
            return
        self.db.restablecer_todo()
        self.lbl_folio_sel.setText("Selecciona una orden")
        self.refrescar_todo()
        QMessageBox.information(
            self, "Base restablecida", f"Listo. Respaldo guardado en:\n{respaldo}"
        )

    def _insertar_garantia_ejemplo(self):
        if self.cfg_garantia.toPlainText().strip():
            resp = QMessageBox.question(
                self,
                "Reemplazar texto",
                "Ya hay texto escrito. ¿Reemplazarlo con el ejemplo?",
            )
            if resp != QMessageBox.StandardButton.Yes:
                return
        self.cfg_garantia.setPlainText(GARANTIA_EJEMPLO)

    # Icono distintivo para cada tema en el selector.
    _ICONO_TEMA = {
        "Mostrador Limpio": "sun",
        "Laboratorio Minimal": "grilla",
        "Arena Suave": "articulo",
        "Grafito Pro": "moon",
        "Midnight Slate": "monitor",
        "Placa Madre Emerald": "base-datos",
    }

    def _abrir_selector_tema(self):
        menu = QMenu(self)
        menu.setTitle("Cambiar tema")
        actual = self._tema_actual()
        color = self._color_icono("IconBtn", "secundario")
        for nombre in TEMAS_ORDEN:
            accion = menu.addAction(nombre)
            ic = self._ICONO_TEMA.get(nombre, "configuracion")
            accion.setIcon(icono(ic, color, 18))
            accion.setCheckable(True)
            accion.setChecked(nombre == actual)
            accion.triggered.connect(lambda checked=False, n=nombre: self._cambiar_tema(n))
        puntos = self.btn_gearra_tema.mapToGlobal(QPoint(0, 0))
        menu.exec(puntos)

    def _cambiar_tema(self, nuevo_tema: str):
        if self._gestor_temas().seleccionar(nuevo_tema):
            self.aplicar_tema()

    # --- Impresión automática en la impresora predeterminada de Windows ---
    def _actualizar_estado_impresora(self):
        if not hasattr(self, "lbl_imp_auto"):
            return
        info = obtener_estado_impresora()
        self.lbl_imp_auto.setText(info.get("mensaje", ""))

    def _probar_impresora(self):
        ok, msg = imprimir_ticket_prueba(self.config)
        if ok:
            QMessageBox.information(self, "Prueba de impresión", msg)
            self._actualizar_estado_impresora()
        else:
            QMessageBox.warning(self, "No se pudo imprimir", msg)

    def _elegir_logo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar logo", "", "Imágenes (*.png *.jpg *.jpeg *.webp)"
        )
        if ruta:
            self.cfg_logo.setText(ruta)

    def _guardar_config(self):
        self.config.set("identidad", "nombre_establecimiento", self.cfg_nombre.text().strip())
        self.config.set("notas", "nombre_comercial", self.cfg_nombre.text().strip())
        self.config.set("contacto", "telefono", self.cfg_tel.text().strip())
        self.config.set("notas", "telefono", self.cfg_tel.text().strip())
        self.config.set("contacto", "direccion", self.cfg_dir.text().strip())
        self.config.set("notas", "direccion", self.cfg_dir.text().strip())
        self.config.set("identidad", "logo_personalizado", self.cfg_logo.text().strip())
        self.config.set(
            "notas", "politicas_garantia", self.cfg_garantia.toPlainText().strip()
        )
        self.config.save()

        self._aplicar_icono_abcell()
        self.aplicar_tema()
        self.lbl_brand_sidebar.setText(APP_NAME)
        self.setWindowTitle(f"{APP_NAME} — {self.cfg_nombre.text().strip()} — Taller")
        self._cargar_logo_widget(self.lbl_logo_sidebar, 42)
        self._actualizar_estado_impresora()
        QMessageBox.information(self, "Guardado", "La configuración se guardó correctamente.")
        self.refrescar_todo()

    def refrescar_todo(self):
        self._cargar_combos_orden()
        self.refrescar_ordenes()
        self.refrescar_inventario()
        self.refrescar_catalogo_ubicaciones()
        self.refrescar_reportes()
        self._actualizar_estado_binario_adb()
        if self.stack.currentIndex() == 6:
            self._actualizar_estado_impresora()
