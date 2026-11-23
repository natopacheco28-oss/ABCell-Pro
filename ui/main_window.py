import os
import webbrowser
from datetime import datetime
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from config.settings import ConfigManager
from database.db_manager import DatabaseManager
from integrations.printer_58mm import (
    generar_texto_ticket,
    imprimir_ticket_58mm,
    logo_color_pil,
    logo_pil,
)
from ui.theme import DARK_QSS, LIGHT_QSS

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

        painter.setPen(QPen(QColor("#cbd5e1"), 1.5))
        painter.setBrush(QColor("#f8fafc"))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)

        mapa = {num: pt for num, pt in self.puntos}

        if len(self.secuencia) >= 2:
            pen_linea = QPen(QColor("#0284c7"), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_linea)
            for i in range(len(self.secuencia) - 1):
                p1 = mapa[self.secuencia[i]]
                p2 = mapa[self.secuencia[i + 1]]
                painter.drawLine(p1, p2)

        if self.dibujando and self.secuencia and self.pos_actual is not None:
            ultimo_pt = mapa[self.secuencia[-1]]
            painter.setPen(QPen(QColor("#38bdf8"), 2.5, Qt.DashLine, Qt.RoundCap))
            painter.drawLine(ultimo_pt, self.pos_actual)

        for num, pt in self.puntos:
            seleccionado = num in self.secuencia
            if seleccionado:
                painter.setPen(QPen(QColor("#0284c7"), 2))
                painter.setBrush(QColor("#e0f2fe"))
                painter.drawEllipse(pt, 16, 16)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor("#0284c7"))
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


def _make_summary_card(titulo: str, subtitulo: str, enlace: str, badge_bg: str, badge_fg: str):
    card = QFrame()
    card.setObjectName("Card")
    lay = QHBoxLayout(card)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(12)

    badge = QLabel("●")
    badge.setFixedSize(36, 36)
    badge.setAlignment(Qt.AlignCenter)
    badge.setStyleSheet(
        f"background-color: {badge_bg}; color: {badge_fg}; border-radius: 18px; font-size: 15px; font-weight: 700;"
    )
    lay.addWidget(badge)

    txt = QVBoxLayout()
    txt.setSpacing(2)
    lbl_t = QLabel(titulo)
    lbl_t.setObjectName("CardTitle")
    row_sub = QHBoxLayout()
    row_sub.setSpacing(6)
    lbl_s = QLabel(subtitulo)
    lbl_s.setObjectName("CardSub")
    lbl_l = QLabel(enlace)
    lbl_l.setObjectName("CardLink")
    row_sub.addWidget(lbl_s)
    row_sub.addWidget(lbl_l)
    row_sub.addStretch()

    txt.addWidget(lbl_t)
    txt.addLayout(row_sub)
    lay.addLayout(txt, 1)
    return card, lbl_s, lbl_l


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
    tabla.verticalHeader().setDefaultSectionSize(42)
    tabla.setShowGrid(False)
    header = tabla.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Interactive)
    header.setStretchLastSection(True)
    if 0 <= stretch_col < tabla.columnCount():
        header.setSectionResizeMode(stretch_col, QHeaderView.Stretch)


class MainWindow(QMainWindow):
    def __init__(self, db: DatabaseManager, config: ConfigManager):
        super().__init__()
        self.db = db
        self.config = config
        self.service = WorkshopService(db, config)
        self.wa = WhatsAppCenter(db, config)
        self.nav_buttons: list[QPushButton] = []
        self.stage_buttons: list[QPushButton] = []
        self.etapa_filtro: str = "Todas"

        nombre_negocio = self.config.get("identidad", "nombre_establecimiento", "ABCell")
        self.setWindowTitle(f"{nombre_negocio} — Taller")
        self.resize(1360, 820)
        self.setMinimumSize(1060, 700)

        self._build_ui()
        self._aplicar_icono_abcell()
        self.aplicar_tema()
        self.refrescar_todo()

    def _obtener_pixmap_abcell(self) -> QPixmap | None:
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
        pm = self._obtener_pixmap_abcell()
        if pm is not None and not pm.isNull():
            self.setWindowIcon(QIcon(pm))

    def _es_tema_claro(self) -> bool:
        tema = str(self.config.get("apariencia", "tema", "Claro")).strip().lower()
        return not tema.startswith("oscuro") and not tema.startswith("negro")

    def aplicar_tema(self):
        es_claro = self._es_tema_claro()
        self.setStyleSheet(LIGHT_QSS if es_claro else DARK_QSS)
        if hasattr(self, "btn_toggle_tema"):
            self.btn_toggle_tema.setText("Modo Oscuro" if es_claro else "Modo Claro")
        if hasattr(self, "cfg_tema"):
            self.cfg_tema.blockSignals(True)
            self.cfg_tema.setCurrentText("Claro" if es_claro else "Oscuro")
            self.cfg_tema.blockSignals(False)

    def alternar_tema_rapido(self):
        nuevo_tema = "Oscuro" if self._es_tema_claro() else "Claro"
        self.config.set("apariencia", "tema", nuevo_tema)
        self.config.save()
        self.aplicar_tema()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        topbar = QFrame()
        topbar.setObjectName("TopBar")
        topbar.setFixedHeight(52)
        tb_lay = QHBoxLayout(topbar)
        tb_lay.setContentsMargins(16, 8, 16, 8)
        tb_lay.setSpacing(10)

        self.lbl_topbar_logo = QLabel()
        self.lbl_topbar_logo.setFixedSize(28, 28)
        self.lbl_topbar_logo.setAlignment(Qt.AlignCenter)
        self._cargar_logo_widget(self.lbl_topbar_logo, 26)
        tb_lay.addWidget(self.lbl_topbar_logo)

        self.txt_global_search = QLineEdit()
        self.txt_global_search.setPlaceholderText("Buscar [ENTER] en órdenes o clientes...")
        self.txt_global_search.setMinimumWidth(260)
        self.txt_global_search.setMaximumWidth(360)
        self.txt_global_search.returnPressed.connect(self._buscar_global)

        lbl_fecha = QLabel(datetime.now().strftime("%d/%m/%Y"))
        lbl_fecha.setObjectName("CardSub")

        self.btn_toggle_tema = QPushButton("Modo Oscuro")
        self.btn_toggle_tema.setMinimumWidth(115)
        self.btn_toggle_tema.clicked.connect(self.alternar_tema_rapido)

        btn_quick_new = QPushButton("+ Nueva Orden")
        btn_quick_new.setObjectName("PrimaryBtn")
        btn_quick_new.setMinimumWidth(125)
        btn_quick_new.clicked.connect(lambda: self.ir_a_seccion(1))

        tb_lay.addWidget(self.txt_global_search)
        tb_lay.addWidget(lbl_fecha)
        tb_lay.addStretch()
        tb_lay.addWidget(self.btn_toggle_tema)
        tb_lay.addWidget(btn_quick_new)
        outer.addWidget(topbar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(225)
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(12, 16, 12, 16)
        sb_lay.setSpacing(4)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(8)
        self.lbl_logo_sidebar = QLabel()
        self.lbl_logo_sidebar.setFixedSize(40, 40)
        self.lbl_logo_sidebar.setAlignment(Qt.AlignCenter)
        self._cargar_logo_widget(self.lbl_logo_sidebar, 38)

        self.lbl_brand_sidebar = QLabel(
            self.config.get("identidad", "nombre_establecimiento", "ABCell")
        )
        self.lbl_brand_sidebar.setObjectName("BrandTitle")
        self.lbl_brand_sidebar.setWordWrap(True)
        brand_row.addWidget(self.lbl_logo_sidebar)
        brand_row.addWidget(self.lbl_brand_sidebar, 1)
        sb_lay.addLayout(brand_row)

        sb_lay.addSpacing(10)

        secciones = [
            ("Órdenes de trabajo", 0),
            ("Nueva orden", 1),
            ("Clientes (Historial)", 2),
            ("Catálogo y Ubicaciones", 3),
            ("Estadísticas y Caja", 4),
            ("WhatsApp y Tickets", 5),
            ("Configuración de taller", 6),
        ]
        for texto, idx in secciones:
            btn = QPushButton(texto)
            btn.setObjectName("NavBtn")
            btn.setMinimumHeight(36)
            btn.clicked.connect(lambda checked=False, i=idx: self.ir_a_seccion(i))
            sb_lay.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_lay.addStretch()

        btn_sync = QPushButton("Refrescar datos")
        btn_sync.setMinimumHeight(34)
        btn_sync.clicked.connect(self.refrescar_todo)
        sb_lay.addWidget(btn_sync)

        body.addWidget(sidebar)

        self.stack = QStackedWidget()
        body.addWidget(self.stack, 1)

        self.stack.addWidget(self._build_taller_ordenes_tab())
        self.stack.addWidget(self._build_nueva_orden_tab())
        self.stack.addWidget(self._build_clientes_tab())
        self.stack.addWidget(self._build_catalogo_ubicaciones_tab())
        self.stack.addWidget(self._build_reportes_tab())
        self.stack.addWidget(self._build_wa_tickets_tab())
        self.stack.addWidget(self._build_config_tab())

        outer.addLayout(body, 1)
        self.ir_a_seccion(0)

    def _buscar_global(self):
        texto = self.txt_global_search.text().strip()
        self.ir_a_seccion(0)
        if hasattr(self, "txt_buscar_orden"):
            self.txt_buscar_orden.setText(texto)
            self.refrescar_ordenes()

    def _cargar_logo_widget(self, label: QLabel, tam: int):
        pm = self._obtener_pixmap_abcell()
        if pm is None or pm.isNull():
            label.setText("AB")
            label.setStyleSheet(
                "background-color: #e0f2fe; color: #0284c7; border-radius: 10px; font-weight: 800; font-size: 13px;"
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
        self.refrescar_todo()

    # ------------------------------------------
    # 0. TALLER Y ÓRDENES
    # ------------------------------------------
    def _build_taller_ordenes_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(12)

        head_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_t = QLabel("Taller")
        lbl_t.setObjectName("Title")
        lbl_bc = QLabel("Principal › Taller › Órdenes")
        lbl_bc.setObjectName("Breadcrumb")
        title_box.addWidget(lbl_t)
        title_box.addWidget(lbl_bc)

        btn_crear = QPushButton("+ Crear")
        btn_crear.setObjectName("PrimaryBtn")
        btn_crear.setMinimumWidth(115)
        btn_crear.setMinimumHeight(34)
        btn_crear.clicked.connect(lambda: self.ir_a_seccion(1))

        head_row.addLayout(title_box)
        head_row.addStretch()
        head_row.addWidget(btn_crear)
        lay.addLayout(head_row)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        c1, self.lbl_c1_sub, self.lbl_c1_link = _make_summary_card(
            "Estado del taller", "¡Todo en orden!", "Ver activas", "#dcfce7", "#16a34a"
        )
        c2, self.lbl_c2_sub, self.lbl_c2_link = _make_summary_card(
            "Órdenes abiertas", "0 Abiertas", "Listado", "#e0f2fe", "#0284c7"
        )
        c3, self.lbl_c3_sub, self.lbl_c3_link = _make_summary_card(
            "Saldo por cobrar", "$0.00", "WhatsApp", "#fef3c7", "#d97706"
        )

        cards_row.addWidget(c1)
        cards_row.addWidget(c2)
        cards_row.addWidget(c3)
        lay.addLayout(cards_row)

        stage_bar = QHBoxLayout()
        stage_bar.setSpacing(6)
        etapas = [
            ("Todas", "Todas"),
            ("Entrada", "Entrada"),
            ("Reparación", "Reparación"),
            ("Salida", "Salida"),
        ]
        self.stage_buttons.clear()
        for etiqueta, clave in etapas:
            b = QPushButton(etiqueta)
            b.setObjectName("StageTab")
            b.setProperty("active", clave == self.etapa_filtro)
            b.clicked.connect(lambda checked=False, k=clave: self._seleccionar_etapa(k))
            stage_bar.addWidget(b)
            self.stage_buttons.append(b)
        stage_bar.addStretch()
        lay.addLayout(stage_bar)

        sub_bar = QFrame()
        sub_bar.setObjectName("SubBar")
        sb_l = QHBoxLayout(sub_bar)
        sb_l.setContentsMargins(16, 10, 16, 10)
        self.lbl_contador_ordenes = QLabel("Cantidad: 0 Órdenes")
        self.lbl_contador_ordenes.setObjectName("CardSub")
        self.lbl_resumen_extra = QLabel("Listas para entrega: 0")
        self.lbl_resumen_extra.setObjectName("CardSub")
        sb_l.addWidget(self.lbl_contador_ordenes)
        sb_l.addStretch()
        sb_l.addWidget(self.lbl_resumen_extra)
        lay.addWidget(sub_bar)

        tbl_card = QFrame()
        tbl_card.setObjectName("Card")
        tc_lay = QVBoxLayout(tbl_card)
        tc_lay.setContentsMargins(16, 14, 16, 14)
        tc_lay.setSpacing(10)

        t_head = QHBoxLayout()
        t_head.setSpacing(8)
        lbl_o = QLabel("Órdenes")
        lbl_o.setObjectName("Title")
        t_head.addWidget(lbl_o)
        t_head.addStretch()

        self.txt_buscar_orden = QLineEdit()
        self.txt_buscar_orden.setPlaceholderText("Buscar [ENTER]")
        self.txt_buscar_orden.setMinimumWidth(220)
        self.txt_buscar_orden.textChanged.connect(self.refrescar_ordenes)

        self.cmb_filtro_estatus = QComboBox()
        self.cmb_filtro_estatus.setMinimumWidth(155)
        self.cmb_filtro_estatus.addItems(["Todos"] + ESTATUS_ORDEN)
        self.cmb_filtro_estatus.currentTextChanged.connect(self.refrescar_ordenes)

        self.cmb_filtro_cat = QComboBox()
        self.cmb_filtro_cat.setMinimumWidth(135)
        self.cmb_filtro_cat.addItems(["Todas"] + CATEGORIAS_EQUIPO)
        self.cmb_filtro_cat.currentTextChanged.connect(self.refrescar_ordenes)

        t_head.addWidget(self.txt_buscar_orden)
        t_head.addWidget(self.cmb_filtro_estatus)
        t_head.addWidget(self.cmb_filtro_cat)
        tc_lay.addLayout(t_head)

        self.tbl_ordenes = QTableWidget(0, 8)
        self.tbl_ordenes.setHorizontalHeaderLabels(
            ["N°", "ESTADO", "EQUIPO / MODELO", "CLIENTE", "UBICACIÓN", "FALLA", "PRECIO", "SALDO"]
        )
        _configurar_tabla(self.tbl_ordenes, stretch_col=5)
        self.tbl_ordenes.itemSelectionChanged.connect(self._cargar_orden_seleccionada)
        tc_lay.addWidget(self.tbl_ordenes, 1)

        lay.addWidget(tbl_card, 1)

        panel_accion = QFrame()
        panel_accion.setObjectName("SubBar")
        pa_lay = QVBoxLayout(panel_accion)
        pa_lay.setContentsMargins(14, 10, 14, 10)
        pa_lay.setSpacing(8)

        f1 = QHBoxLayout()
        f1.setSpacing(8)
        self.lbl_folio_sel = QLabel("Selecciona una orden")
        self.lbl_folio_sel.setObjectName("FolioBadge")
        self.lbl_folio_sel.setMinimumWidth(220)
        f1.addWidget(self.lbl_folio_sel)

        f1.addWidget(QLabel("Estado:"))
        self.cmb_orden_estatus = QComboBox()
        self.cmb_orden_estatus.setMinimumWidth(160)
        self.cmb_orden_estatus.addItems(ESTATUS_ORDEN)
        f1.addWidget(self.cmb_orden_estatus)

        f1.addWidget(QLabel("Ubicación:"))
        self.cmb_orden_ubicacion = QComboBox()
        self.cmb_orden_ubicacion.setMinimumWidth(155)
        f1.addWidget(self.cmb_orden_ubicacion)

        f1.addStretch()

        btn_act_orden = QPushButton("Guardar Estado / Ubicación")
        btn_act_orden.setMinimumWidth(190)
        btn_act_orden.clicked.connect(self._actualizar_orden_sel)
        f1.addWidget(btn_act_orden)
        pa_lay.addLayout(f1)

        f2 = QHBoxLayout()
        f2.setSpacing(8)
        f2.addWidget(QLabel("Abono:"))
        self.spn_orden_abono = QDoubleSpinBox()
        self.spn_orden_abono.setRange(0, 999999)
        self.spn_orden_abono.setDecimals(2)
        self.spn_orden_abono.setMinimumWidth(115)
        f2.addWidget(self.spn_orden_abono)

        f2.addWidget(QLabel("Método:"))
        self.cmb_orden_mpago = QComboBox()
        self.cmb_orden_mpago.setMinimumWidth(130)
        self.cmb_orden_mpago.addItems(METODOS_PAGO)
        f2.addWidget(self.cmb_orden_mpago)

        btn_abonar = QPushButton("Registrar Abono")
        btn_abonar.setObjectName("PrimaryBtn")
        btn_abonar.setMinimumWidth(145)
        btn_abonar.clicked.connect(self._abonar_orden_sel)
        f2.addWidget(btn_abonar)

        f2.addStretch()

        btn_ticket = QPushButton("Ticket 58mm")
        btn_ticket.setMinimumWidth(125)
        btn_ticket.clicked.connect(self._imprimir_orden_sel)
        f2.addWidget(btn_ticket)

        btn_wa = QPushButton("WhatsApp")
        btn_wa.setMinimumWidth(120)
        btn_wa.clicked.connect(self._enviar_wa_orden_sel)
        f2.addWidget(btn_wa)

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
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(12)

        lbl = QLabel("Registrar Nueva Orden de Trabajo")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        form.setSpacing(10)
        form.setContentsMargins(18, 18, 18, 18)

        self.no_cliente = QLineEdit()
        self.no_cliente.setPlaceholderText("Nombre completo del cliente")
        self.no_tel = QLineEdit()
        self.no_tel.setPlaceholderText("Ej. 9861234567")

        self.no_cat = QComboBox()
        self.no_cat.addItems(CATEGORIAS_EQUIPO)
        self.no_cat.currentTextChanged.connect(self._actualizar_subcategorias_marca)

        self.no_marca = QComboBox()
        self.no_marca.setEditable(True)
        self.no_marca.setInsertPolicy(QComboBox.NoInsert)

        self.no_modelo = QLineEdit()
        self.no_modelo.setPlaceholderText("Ej. PlayStation 4 Slim, Xbox Series S, Galaxy A54")
        self.no_color = QLineEdit()
        self.no_color.setPlaceholderText("Ej. Negro, Blanco")

        self.no_imei = QLineEdit()
        self.no_imei.setPlaceholderText("IMEI o número de serie")
        self.no_pin = QLineEdit()
        self.no_pin.setPlaceholderText("PIN o contraseña escrita")

        patron_box = QFrame()
        patron_box.setObjectName("SubBar")
        pb_lay = QHBoxLayout(patron_box)
        pb_lay.setContentsMargins(12, 10, 12, 10)
        pb_lay.setSpacing(14)

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

        btn_limpiar_patron = QPushButton("Borrar patrón")
        btn_limpiar_patron.setMinimumWidth(130)
        btn_limpiar_patron.clicked.connect(self.patron_canvas.limpiar_patron)

        patron_info.addWidget(lbl_p_ayuda)
        patron_info.addWidget(self.lbl_patron_valor)
        patron_info.addWidget(btn_limpiar_patron, alignment=Qt.AlignLeft)
        patron_info.addStretch()
        pb_lay.addLayout(patron_info, 1)

        self.no_estado_fisico = QLineEdit()
        self.no_estado_fisico.setPlaceholderText("Observaciones físicas al recibir")

        self.no_servicio_cat = QComboBox()
        self.no_servicio_cat.currentIndexChanged.connect(self._aplicar_servicio_catalogo)

        self.no_falla = QLineEdit()
        self.no_falla.setPlaceholderText("Falla o servicio solicitado")

        self.no_ubicacion = QComboBox()

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

        self.no_metodo_pago = QComboBox()
        self.no_metodo_pago.addItems(METODOS_PAGO)

        self.lbl_no_saldo = QLabel("$0.00")
        self.lbl_no_saldo.setObjectName("MetricValue")

        self.no_notas = QPlainTextEdit()
        self.no_notas.setMaximumHeight(68)

        form.addRow("Cliente *:", self.no_cliente)
        form.addRow("Teléfono / WA *:", self.no_tel)
        form.addRow("Categoría:", self.no_cat)
        form.addRow("Marca / Consola *:", self.no_marca)
        form.addRow("Modelo / Versión *:", self.no_modelo)
        form.addRow("Color:", self.no_color)
        form.addRow("IMEI / Serie:", self.no_imei)
        form.addRow("PIN / Contraseña:", self.no_pin)
        form.addRow("Patrón (dibujo):", patron_box)
        form.addRow("Estado físico:", self.no_estado_fisico)
        form.addRow("Servicio del catálogo:", self.no_servicio_cat)
        form.addRow("Falla reportada *:", self.no_falla)
        form.addRow("Ubicación física:", self.no_ubicacion)
        form.addRow("Costo repuesto:", self.no_costo_rep)
        form.addRow("Costo total:", self.no_costo_total)
        form.addRow("Anticipo:", self.no_anticipo)
        form.addRow("Método de pago:", self.no_metodo_pago)
        form.addRow("Saldo restante:", self.lbl_no_saldo)
        form.addRow("Notas internas:", self.no_notas)

        lay.addWidget(card)

        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar Orden")
        btn_guardar.setObjectName("PrimaryBtn")
        btn_guardar.setMinimumWidth(145)
        btn_guardar.clicked.connect(self._guardar_nueva_orden)

        btn_limpiar = QPushButton("Limpiar")
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
        if (
            not self.no_cliente.text().strip()
            or not self.no_tel.text().strip()
            or not marca_txt
            or not self.no_modelo.text().strip()
            or not self.no_falla.text().strip()
        ):
            QMessageBox.warning(
                self,
                "Campos requeridos",
                "Completa cliente, teléfono, marca/consola, modelo y falla.",
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
        folio = self.service.crear_orden(datos)
        QMessageBox.information(self, "Orden creada", f"Se registró la orden #{folio:04d}.")
        self._limpiar_nueva_orden()
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

        metricas = self.service.obtener_metricas_dashboard("Todas")
        self.lbl_c2_sub.setText(f"{metricas['activas']} Abiertas")
        self.lbl_c3_sub.setText(f"{simbolo}{metricas['saldos_pendientes']:,.2f}")
        self.lbl_resumen_extra.setText(f"Listas para entrega: {metricas['por_entregar']}")
        if metricas["guardados_7"] > 0:
            self.lbl_c1_sub.setText(f"{metricas['guardados_7']} guardados +7 días")
        else:
            self.lbl_c1_sub.setText("¡Todo en orden!")

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
                self, "Ticket 58mm", f"{msg}\n\nVista previa:\n{generar_texto_ticket(o, self.config)}"
            )

    def _enviar_wa_orden_sel(self):
        folio = self._folio_seleccionado()
        if not folio:
            QMessageBox.information(self, "Selecciona orden", "Selecciona una orden de la tabla.")
            return
        o = self.service.obtener_orden(folio)
        if not o:
            return
        tipo = "listo" if o.get("estatus") == "Listo para entregar" else "recibido"
        msg = self.wa.construir_mensaje(tipo, o)
        url = self.wa.generar_url_wa(o.get("cliente_tel", ""), msg)
        self.wa.registrar_notificacion(
            folio, o.get("cliente_nombre", ""), o.get("cliente_tel", ""), tipo, msg
        )
        webbrowser.open(url)

    # ------------------------------------------
    # 2. CLIENTES
    # ------------------------------------------
    def _build_clientes_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(12)

        lbl = QLabel("Clientes (Historial)")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        self.txt_buscar_cli = QLineEdit()
        self.txt_buscar_cli.setPlaceholderText("Buscar cliente por nombre, teléfono o correo...")
        self.txt_buscar_cli.textChanged.connect(self.refrescar_clientes)
        lay.addWidget(self.txt_buscar_cli)

        self.tbl_clientes = QTableWidget(0, 6)
        self.tbl_clientes.setHorizontalHeaderLabels(
            ["ID", "NOMBRE", "TELÉFONO", "ÓRDENES", "TOTAL FACTURADO", "SALDO PENDIENTE"]
        )
        _configurar_tabla(self.tbl_clientes, stretch_col=1)
        lay.addWidget(self.tbl_clientes, 1)
        return w

    def refrescar_clientes(self):
        if not hasattr(self, "tbl_clientes"):
            return
        simbolo = self.config.get("regional", "simbolo_moneda", "$")
        clientes = self.service.listar_clientes(self.txt_buscar_cli.text())
        self.tbl_clientes.setRowCount(0)
        for idx, cl in enumerate(clientes):
            self.tbl_clientes.insertRow(idx)
            vals = [
                str(cl["id"]),
                cl.get("nombre", ""),
                cl.get("telefono", ""),
                str(cl.get("total_ordenes", 0)),
                f"{simbolo}{float(cl.get('total_facturado') or 0.0):,.2f}",
                f"{simbolo}{float(cl.get('saldo_pendiente') or 0.0):,.2f}",
            ]
            for c_idx, val in enumerate(vals):
                self.tbl_clientes.setItem(idx, c_idx, QTableWidgetItem(val))

    # ------------------------------------------
    # 3. CATÁLOGO Y UBICACIONES
    # ------------------------------------------
    def _build_catalogo_ubicaciones_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(12)

        lbl = QLabel("Catálogo de Servicios y Ubicaciones")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        tabs = QTabWidget()

        p_serv = QWidget()
        l_serv = QVBoxLayout(p_serv)
        row_s = QHBoxLayout()
        row_s.setSpacing(8)
        self.s_cat = QComboBox()
        self.s_cat.setMinimumWidth(125)
        self.s_cat.addItems(CATEGORIAS_EQUIPO)
        self.s_marca = QLineEdit()
        self.s_marca.setPlaceholderText("Marca / Consola")
        self.s_modelo = QLineEdit()
        self.s_modelo.setPlaceholderText("Modelo")
        self.s_nombre = QLineEdit()
        self.s_nombre.setPlaceholderText("Servicio (ej. Cambio de pantalla / Limpieza)")
        self.s_precio = QDoubleSpinBox()
        self.s_precio.setRange(0, 999999)
        self.s_precio.setDecimals(2)
        self.s_precio.setMinimumWidth(110)
        btn_add_s = QPushButton("+ Agregar")
        btn_add_s.setObjectName("PrimaryBtn")
        btn_add_s.setMinimumWidth(120)
        btn_add_s.clicked.connect(self._agregar_servicio)
        for widget in (self.s_cat, self.s_marca, self.s_modelo, self.s_nombre, self.s_precio, btn_add_s):
            row_s.addWidget(widget)
        l_serv.addLayout(row_s)

        self.tbl_servicios = QTableWidget(0, 5)
        self.tbl_servicios.setHorizontalHeaderLabels(
            ["ID", "CATEGORÍA", "MARCA / MODELO", "SERVICIO", "PRECIO"]
        )
        _configurar_tabla(self.tbl_servicios, stretch_col=3)
        l_serv.addWidget(self.tbl_servicios, 1)

        p_ub = QWidget()
        l_ub = QVBoxLayout(p_ub)
        row_u = QHBoxLayout()
        row_u.setSpacing(8)
        self.u_nombre = QLineEdit()
        self.u_nombre.setPlaceholderText("Ubicación (ej. Estante A-1)")
        self.u_tipo = QLineEdit()
        self.u_tipo.setPlaceholderText("Tipo")
        self.u_desc = QLineEdit()
        self.u_desc.setPlaceholderText("Descripción")
        btn_add_u = QPushButton("+ Agregar")
        btn_add_u.setObjectName("PrimaryBtn")
        btn_add_u.setMinimumWidth(120)
        btn_add_u.clicked.connect(self._agregar_ubicacion)
        for widget in (self.u_nombre, self.u_tipo, self.u_desc, btn_add_u):
            row_u.addWidget(widget)
        l_ub.addLayout(row_u)

        self.tbl_ubicaciones = QTableWidget(0, 4)
        self.tbl_ubicaciones.setHorizontalHeaderLabels(["ID", "NOMBRE", "TIPO", "DESCRIPCIÓN"])
        _configurar_tabla(self.tbl_ubicaciones, stretch_col=3)
        l_ub.addWidget(self.tbl_ubicaciones, 1)

        tabs.addTab(p_serv, "Servicios")
        tabs.addTab(p_ub, "Ubicaciones")
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

        ubicaciones = self.service.listar_ubicaciones(solo_activas=False)
        self.tbl_ubicaciones.setRowCount(0)
        for i, u in enumerate(ubicaciones):
            self.tbl_ubicaciones.insertRow(i)
            vals = [str(u["id"]), u.get("nombre", ""), u.get("tipo", ""), u.get("descripcion", "")]
            for c, v in enumerate(vals):
                self.tbl_ubicaciones.setItem(i, c, QTableWidgetItem(v))

        self._cargar_combos_orden()

    # ------------------------------------------
    # 4. ESTADÍSTICAS Y CAJA
    # ------------------------------------------
    def _build_reportes_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(12)

        lbl = QLabel("Estadísticas y Reportes Financieros")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(12)
        c_dia, self.r_dia, _ = _make_metric_card("Ingresos del Día", "$0.00", "Abonos y cobros hoy")
        c_mes, self.r_mes, _ = _make_metric_card("Ingresos del Mes", "$0.00", "Flujo mensual")
        c_gan, self.r_gan, _ = _make_metric_card(
            "Ganancia Neta (Mes)", "$0.00", "Total órdenes menos repuestos"
        )
        c_sal, self.r_sal, _ = _make_metric_card("Saldos por Cobrar", "$0.00", "Pendiente en taller")
        for c in (c_dia, c_mes, c_gan, c_sal):
            row.addWidget(c)
        lay.addLayout(row)

        self.tbl_rep_cat = QTableWidget(0, 5)
        self.tbl_rep_cat.setHorizontalHeaderLabels(
            ["CATEGORÍA", "ÓRDENES", "FACTURADO", "COSTO REPUESTOS", "GANANCIA ESTIMADA"]
        )
        _configurar_tabla(self.tbl_rep_cat, stretch_col=0)
        lay.addWidget(self.tbl_rep_cat, 1)
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
    # 5. WHATSAPP Y TICKETS
    # ------------------------------------------
    def _build_wa_tickets_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(12)

        lbl = QLabel("WhatsApp y Historial de Notificaciones")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        self.tbl_wa = QTableWidget(0, 6)
        self.tbl_wa.setHorizontalHeaderLabels(
            ["FOLIO", "CLIENTE", "TELÉFONO", "TIPO", "FECHA", "MENSAJE"]
        )
        _configurar_tabla(self.tbl_wa, stretch_col=5)
        lay.addWidget(self.tbl_wa, 1)
        return w

    def refrescar_wa(self):
        if not hasattr(self, "tbl_wa"):
            return
        notifs = self.wa.listar_notificaciones()
        self.tbl_wa.setRowCount(0)
        for i, n in enumerate(notifs):
            self.tbl_wa.insertRow(i)
            vals = [
                f"#{int(n.get('folio') or 0):04d}",
                n.get("cliente_nombre", ""),
                n.get("telefono", ""),
                n.get("tipo", ""),
                n.get("fecha", ""),
                n.get("mensaje", ""),
            ]
            for c, v in enumerate(vals):
                self.tbl_wa.setItem(i, c, QTableWidgetItem(v))

    # ------------------------------------------
    # 6. CONFIGURACIÓN DE TALLER
    # ------------------------------------------
    def _build_config_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(12)

        lbl = QLabel("Configuración de Taller")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        form.setSpacing(10)
        form.setContentsMargins(18, 18, 18, 18)

        self
