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
from core.catalog_data import (
    CATEGORIAS_EQUIPO,
    ESTATUS_ORDEN,
    METODOS_PAGO,
    SUBCATEGORIAS_POR_CATEGORIA,
)
from database.db_manager import DatabaseManager
from integrations.printer_58mm import (
    generar_texto_ticket,
    imprimir_ticket_58mm,
    logo_color_pil,
    logo_pil,
)
from integrations.whatsapp_center import WhatsAppCenter
from services.workshop_service import WorkshopService
from ui.theme import DARK_QSS, LIGHT_QSS


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

    def mostrar_todas_las_ordenes(self):
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

        self.refrescar_ordenes()

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

        btn
