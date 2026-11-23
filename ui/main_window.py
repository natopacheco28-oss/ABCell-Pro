import os
import webbrowser
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
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
from integrations.printer_58mm import generar_texto_ticket, imprimir_ticket_58mm, logo_color_pil
from ui.theme import DARK_QSS, LIGHT_QSS

try:
    from core.catalog_data import (
        CATEGORIAS_EQUIPO,
        ESTATUS_ORDEN,
        METODOS_PAGO,
        PATRONES_SUGERIDOS,
    )
except Exception:
    CATEGORIAS_EQUIPO = [
        "Celulares",
        "Tablets",
        "Laptops",
        "Smartwatches",
        "Consolas",
        "Accesorios",
        "Otros",
    ]
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
    PATRONES_SUGERIDOS = ["Sin patrón", "Patrón en L", "Patrón en Z"]

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


def _make_card(titulo: str, valor: str = "", subtitulo: str = "") -> tuple[QFrame, QLabel, QLabel]:
    card = QFrame()
    card.setObjectName("Card")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 12, 14, 12)
    lay.setSpacing(4)
    lbl_t = QLabel(titulo)
    lbl_t.setObjectName("Subtitle")
    lbl_v = QLabel(valor)
    lbl_v.setObjectName("MetricValue")
    lbl_s = QLabel(subtitulo)
    lbl_s.setObjectName("Subtitle")
    lay.addWidget(lbl_t)
    if valor:
        lay.addWidget(lbl_v)
    if subtitulo:
        lay.addWidget(lbl_s)
    return card, lbl_v, lbl_s


def _configurar_tabla(tabla: QTableWidget, stretch_col: int = -1):
    tabla.setAlternatingRowColors(True)
    tabla.setSelectionBehavior(QTableWidget.SelectRows)
    tabla.setEditTriggers(QTableWidget.NoEditTriggers)
    tabla.verticalHeader().setVisible(False)
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

        nombre_negocio = self.config.get("identidad", "nombre_establecimiento", "ABCell Tizimin")
        self.setWindowTitle(f"{nombre_negocio} — Sistema de Gestión de Taller")
        self.resize(1320, 800)
        self.setMinimumSize(1024, 680)

        self._build_ui()
        self.aplicar_tema()
        self.refrescar_todo()

    def _es_tema_claro(self) -> bool:
        tema = str(self.config.get("apariencia", "tema", "Oscuro")).strip().lower()
        return tema.startswith("claro") or tema.startswith("blanco")

    def aplicar_tema(self):
        es_claro = self._es_tema_claro()
        self.setStyleSheet(LIGHT_QSS if es_claro else DARK_QSS)
        if hasattr(self, "btn_toggle_tema"):
            self.btn_toggle_tema.setText("Tema: Oscuro" if es_claro else "Tema: Claro")
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
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Barra lateral
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(12, 18, 12, 18)
        sb_lay.setSpacing(6)

        self.lbl_logo_sidebar = QLabel()
        self.lbl_logo_sidebar.setAlignment(Qt.AlignCenter)
        self._cargar_logo_widget(self.lbl_logo_sidebar, 68)
        sb_lay.addWidget(self.lbl_logo_sidebar)

        self.lbl_brand_sidebar = QLabel(
            self.config.get("identidad", "nombre_establecimiento", "ABCell Pro")
        )
        self.lbl_brand_sidebar.setObjectName("BrandTitle")
        self.lbl_brand_sidebar.setAlignment(Qt.AlignCenter)
        self.lbl_brand_sidebar.setWordWrap(True)
        sb_lay.addWidget(self.lbl_brand_sidebar)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #1e293b; max-height: 1px; margin: 6px 0;")
        sb_lay.addWidget(line)

        secciones = [
            ("Dashboard", 0),
            ("Nueva Orden", 1),
            ("Órdenes y Taller", 2),
            ("Clientes", 3),
            ("Catálogo y Ubicaciones", 4),
            ("Reportes Financieros", 5),
            ("WhatsApp y Tickets", 6),
            ("Configuración", 7),
        ]
        for texto, idx in secciones:
            btn = QPushButton(texto)
            btn.setObjectName("NavBtn")
            btn.setMinimumHeight(38)
            btn.clicked.connect(lambda checked=False, i=idx: self.ir_a_seccion(i))
            sb_lay.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_lay.addStretch()

        self.btn_toggle_tema = QPushButton("Tema: Claro")
        self.btn_toggle_tema.setMinimumHeight(36)
        self.btn_toggle_tema.clicked.connect(self.alternar_tema_rapido)
        sb_lay.addWidget(self.btn_toggle_tema)

        btn_sync = QPushButton("Actualizar datos")
        btn_sync.setMinimumHeight(36)
        btn_sync.clicked.connect(self.refrescar_todo)
        sb_lay.addWidget(btn_sync)

        root.addWidget(sidebar)

        # Contenedor principal
        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self.stack.addWidget(self._build_dashboard_tab())
        self.stack.addWidget(self._build_nueva_orden_tab())
        self.stack.addWidget(self._build_ordenes_tab())
        self.stack.addWidget(self._build_clientes_tab())
        self.stack.addWidget(self._build_catalogo_ubicaciones_tab())
        self.stack.addWidget(self._build_reportes_tab())
        self.stack.addWidget(self._build_wa_tickets_tab())
        self.stack.addWidget(self._build_config_tab())

        self.ir_a_seccion(0)

    def _cargar_logo_widget(self, label: QLabel, tam: int):
        pil_img = logo_color_pil(self.config)
        if pil_img is None:
            label.setText("ABCell")
            label.setStyleSheet("font-size: 16px; font-weight: 700; color: #38bdf8; padding: 4px;")
            return
        tmp_path = os.path.join(os.path.dirname(self.db.db_path), "_tmp_logo_ui.png")
        pil_img.save(tmp_path)
        pm = QPixmap(tmp_path)
        if not pm.isNull():
            label.setPixmap(pm.scaled(tam, tam, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def ir_a_seccion(self, indice: int):
        self.stack.setCurrentIndex(indice)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", i == indice)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.refrescar_todo()

    # ------------------------------------------
    # 0. DASHBOARD
    # ------------------------------------------
    def _build_dashboard_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(14)

        top = QHBoxLayout()
        lbl_t = QLabel("Panel de Control del Taller")
        lbl_t.setObjectName("Title")
        top.addWidget(lbl_t)
        top.addStretch()
        top.addWidget(QLabel("Categoría:"))
        self.cmb_dash_cat = QComboBox()
        self.cmb_dash_cat.setMinimumWidth(140)
        self.cmb_dash_cat.addItems(["Todas"] + CATEGORIAS_EQUIPO)
        self.cmb_dash_cat.currentTextChanged.connect(self.refrescar_dashboard)
        top.addWidget(self.cmb_dash_cat)
        lay.addLayout(top)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        c1, self.m_activas, _ = _make_card("Órdenes Activas", "0", "En proceso en taller")
        c2, self.m_listas, _ = _make_card("Listas para Entregar", "0", "Esperando al cliente")
        c3, self.m_7dias, _ = _make_card("Guardados +7 Días", "0", "Requieren seguimiento")
        c4, self.m_cobrado, _ = _make_card("Anticipos / Cobrado", "$0.00", "Pagos recibidos")
        c5, self.m_saldo, _ = _make_card("Saldo Pendiente", "$0.00", "Por cobrar en activas")
        for c in (c1, c2, c3, c4, c5):
            cards_row.addWidget(c)
        lay.addLayout(cards_row)

        tables_row = QHBoxLayout()
        tables_row.setSpacing(14)

        box_listos = QFrame()
        box_listos.setObjectName("Card")
        l1 = QVBoxLayout(box_listos)
        l1.addWidget(QLabel("Equipos Listos para Entregar / +7 Días"))
        self.tbl_dash_listos = QTableWidget(0, 5)
        self.tbl_dash_listos.setHorizontalHeaderLabels(["Folio", "Cliente", "Equipo", "Días", "Saldo"])
        _configurar_tabla(self.tbl_dash_listos, stretch_col=1)
        l1.addWidget(self.tbl_dash_listos)

        box_recientes = QFrame()
        box_recientes.setObjectName("Card")
        l2 = QVBoxLayout(box_recientes)
        l2.addWidget(QLabel("Actividad Reciente de Órdenes"))
        self.tbl_dash_recientes = QTableWidget(0, 5)
        self.tbl_dash_recientes.setHorizontalHeaderLabels(["Folio", "Cliente", "Equipo", "Estatus", "Ubicación"])
        _configurar_tabla(self.tbl_dash_recientes, stretch_col=1)
        l2.addWidget(self.tbl_dash_recientes)

        tables_row.addWidget(box_listos)
        tables_row.addWidget(box_recientes)
        lay.addLayout(tables_row, 1)
        return w

    def refrescar_dashboard(self):
        simbolo = self.config.get("regional", "simbolo_moneda", "$")
        cat = self.cmb_dash_cat.currentText() if hasattr(self, "cmb_dash_cat") else "Todas"
        m = self.service.obtener_metricas_dashboard(cat)

        self.m_activas.setText(str(m["activas"]))
        self.m_listas.setText(str(m["por_entregar"]))
        self.m_7dias.setText(str(m["guardados_7"]))
        self.m_cobrado.setText(f"{simbolo}{m['anticipos_totales']:,.2f}")
        self.m_saldo.setText(f"{simbolo}{m['saldos_pendientes']:,.2f}")

        self.tbl_dash_listos.setRowCount(0)
        for r_idx, o in enumerate(m["lista_por_entregar"]):
            self.tbl_dash_listos.insertRow(r_idx)
            vals = [
                f"#{int(o['folio']):04d}",
                o.get("cliente_nombre", ""),
                f"{o.get('marca', '')} {o.get('modelo', '')}".strip(),
                f"{o.get('dias_espera', 0)} d",
                f"{simbolo}{float(o.get('saldo') or 0.0):,.2f}",
            ]
            for c_idx, val in enumerate(vals):
                self.tbl_dash_listos.setItem(r_idx, c_idx, QTableWidgetItem(val))

        self.tbl_dash_recientes.setRowCount(0)
        for r_idx, o in enumerate(m["actividad_reciente"]):
            self.tbl_dash_recientes.insertRow(r_idx)
            vals = [
                f"#{int(o['folio']):04d}",
                o.get("cliente_nombre", ""),
                f"{o.get('marca', '')} {o.get('modelo', '')}".strip(),
                o.get("estatus", ""),
                o.get("ubicacion", ""),
            ]
            for c_idx, val in enumerate(vals):
                self.tbl_dash_recientes.setItem(r_idx, c_idx, QTableWidgetItem(val))

    # ------------------------------------------
    # 1. NUEVA ORDEN
    # ------------------------------------------
    def _build_nueva_orden_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)

        lbl = QLabel("Registrar Nueva Orden de Servicio")
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

        self.no_marca = QLineEdit()
        self.no_marca.setPlaceholderText("Ej. Samsung, iPhone, Xiaomi")
        self.no_modelo = QLineEdit()
        self.no_modelo.setPlaceholderText("Ej. A54, iPhone 13, Redmi Note 12")
        self.no_color = QLineEdit()
        self.no_color.setPlaceholderText("Ej. Negro, Azul")

        self.no_imei = QLineEdit()
        self.no_pin = QLineEdit()
        self.no_patron = QComboBox()
        self.no_patron.addItems(PATRONES_SUGERIDOS)
        self.no_patron.setEditable(True)

        self.no_estado_fisico = QLineEdit()
        self.no_estado_fisico.setPlaceholderText("Ej. Rayones leves en marco, tapa trasera intacta")

        self.no_servicio_cat = QComboBox()
        self.no_servicio_cat.currentIndexChanged.connect(self._aplicar_servicio_catalogo)

        self.no_falla = QLineEdit()
        self.no_falla.setPlaceholderText("Describe la falla o servicio solicitado")

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
        self.no_notas.setMaximumHeight(70)

        form.addRow("Cliente *:", self.no_cliente)
        form.addRow("Teléfono / WA *:", self.no_tel)
        form.addRow("Categoría:", self.no_cat)
        form.addRow("Marca *:", self.no_marca)
        form.addRow("Modelo *:", self.no_modelo)
        form.addRow("Color:", self.no_color)
        form.addRow("IMEI / Serie:", self.no_imei)
        form.addRow("PIN / Contraseña:", self.no_pin)
        form.addRow("Patrón:", self.no_patron)
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
        btn_guardar.setMinimumWidth(140)
        btn_guardar.clicked.connect(self._guardar_nueva_orden)

        btn_limpiar = QPushButton("Limpiar campos")
        btn_limpiar.setMinimumWidth(130)
        btn_limpiar.clicked.connect(self._limpiar_nueva_orden)

        btns.addStretch()
        btns.addWidget(btn_limpiar)
        btns.addWidget(btn_guardar)
        lay.addLayout(btns)

        scroll.setWidget(w)
        return scroll

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
        self.no_cat.setCurrentText(s.get("categoria", "Celulares"))
        if s.get("marca") and not self.no_marca.text().strip():
            self.no_marca.setText(s["marca"])
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
            self.no_marca,
            self.no_modelo,
            self.no_color,
            self.no_imei,
            self.no_pin,
            self.no_estado_fisico,
            self.no_falla,
        ):
            campo.clear()
        self.no_notas.clear()
        self.no_costo_rep.setValue(0)
        self.no_costo_total.setValue(0)
        self.no_anticipo.setValue(0)
        self.no_servicio_cat.setCurrentIndex(0)

    def _guardar_nueva_orden(self):
        if (
            not self.no_cliente.text().strip()
            or not self.no_tel.text().strip()
            or not self.no_marca.text().strip()
            or not self.no_modelo.text().strip()
            or not self.no_falla.text().strip()
        ):
            QMessageBox.warning(
                self, "Campos requeridos", "Completa cliente, teléfono, marca, modelo y falla."
            )
            return

        s_cat = self.no_servicio_cat.currentData()
        datos = {
            "cliente_nombre": self.no_cliente.text(),
            "cliente_tel": self.no_tel.text(),
            "categoria": self.no_cat.currentText(),
            "marca": self.no_marca.text(),
            "modelo": self.no_modelo.text(),
            "color": self.no_color.text(),
            "imei": self.no_imei.text(),
            "pin_pass": self.no_pin.text(),
            "patron": self.no_patron.currentText(),
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
        QMessageBox.information(self, "Orden creada", f"Se registró la orden #{folio:04d} correctamente.")
        self._limpiar_nueva_orden()
        self.ir_a_seccion(2)

    # ------------------------------------------
    # 2. ÓRDENES Y TALLER
    # ------------------------------------------
    def _build_ordenes_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)

        lbl = QLabel("Órdenes y Control de Taller")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        filtros = QHBoxLayout()
        filtros.setSpacing(10)
        self.txt_buscar_orden = QLineEdit()
        self.txt_buscar_orden.setPlaceholderText(
            "Buscar por folio, cliente, teléfono, marca, modelo o ubicación..."
        )
        self.txt_buscar_orden.textChanged.connect(self.refrescar_ordenes)

        self.cmb_filtro_estatus = QComboBox()
        self.cmb_filtro_estatus.setMinimumWidth(160)
        self.cmb_filtro_estatus.addItems(["Todos"] + ESTATUS_ORDEN)
        self.cmb_filtro_estatus.currentTextChanged.connect(self.refrescar_ordenes)

        self.cmb_filtro_cat = QComboBox()
        self.cmb_filtro_cat.setMinimumWidth(140)
        self.cmb_filtro_cat.addItems(["Todas"] + CATEGORIAS_EQUIPO)
        self.cmb_filtro_cat.currentTextChanged.connect(self.refrescar_ordenes)

        filtros.addWidget(self.txt_buscar_orden, 2)
        filtros.addWidget(self.cmb_filtro_estatus)
        filtros.addWidget(self.cmb_filtro_cat)
        lay.addLayout(filtros)

        self.tbl_ordenes = QTableWidget(0, 8)
        self.tbl_ordenes.setHorizontalHeaderLabels(
            ["Folio", "Cliente", "Equipo", "Falla", "Estatus", "Ubicación", "Total", "Saldo"]
        )
        _configurar_tabla(self.tbl_ordenes, stretch_col=3)
        self.tbl_ordenes.itemSelectionChanged.connect(self._cargar_orden_seleccionada)
        lay.addWidget(self.tbl_ordenes, 1)

        panel_accion = QFrame()
        panel_accion.setObjectName("Card")
        pa_lay = QVBoxLayout(panel_accion)
        pa_lay.setContentsMargins(14, 12, 14, 12)
        pa_lay.setSpacing(10)

        fila_sup = QHBoxLayout()
        fila_sup.setSpacing(10)

        self.lbl_folio_sel = QLabel("Selecciona una orden")
        self.lbl_folio_sel.setObjectName("FolioBadge")
        self.lbl_folio_sel.setMinimumWidth(210)
        fila_sup.addWidget(self.lbl_folio_sel)

        fila_sup.addWidget(QLabel("Estatus:"))
        self.cmb_orden_estatus = QComboBox()
        self.cmb_orden_estatus.setMinimumWidth(165)
        self.cmb_orden_estatus.addItems(ESTATUS_ORDEN)
        fila_sup.addWidget(self.cmb_orden_estatus)

        fila_sup.addWidget(QLabel("Ubicación:"))
        self.cmb_orden_ubicacion = QComboBox()
        self.cmb_orden_ubicacion.setMinimumWidth(165)
        fila_sup.addWidget(self.cmb_orden_ubicacion)

        fila_sup.addStretch()

        btn_act_orden = QPushButton("Guardar Estatus / Ubicación")
        btn_act_orden.setMinimumWidth(195)
        btn_act_orden.clicked.connect(self._actualizar_orden_sel)
        fila_sup.addWidget(btn_act_orden)

        pa_lay.addLayout(fila_sup)

        fila_inf = QHBoxLayout()
        fila_inf.setSpacing(10)

        fila_inf.addWidget(QLabel("Abono:"))
        self.spn_orden_abono = QDoubleSpinBox()
        self.spn_orden_abono.setRange(0, 999999)
        self.spn_orden_abono.setDecimals(2)
        self.spn_orden_abono.setMinimumWidth(120)
        fila_inf.addWidget(self.spn_orden_abono)

        fila_inf.addWidget(QLabel("Método:"))
        self.cmb_orden_mpago = QComboBox()
        self.cmb_orden_mpago.setMinimumWidth(135)
        self.cmb_orden_mpago.addItems(METODOS_PAGO)
        fila_inf.addWidget(self.cmb_orden_mpago)

        btn_abonar = QPushButton("Registrar Abono")
        btn_abonar.setObjectName("PrimaryBtn")
        btn_abonar.setMinimumWidth(145)
        btn_abonar.clicked.connect(self._abonar_orden_sel)
        fila_inf.addWidget(btn_abonar)

        fila_inf.addStretch()

        btn_ticket = QPushButton("Imprimir Ticket 58mm")
        btn_ticket.setMinimumWidth(165)
        btn_ticket.clicked.connect(self._imprimir_orden_sel)
        fila_inf.addWidget(btn_ticket)

        btn_wa = QPushButton("Enviar WhatsApp")
        btn_wa.setMinimumWidth(150)
        btn_wa.clicked.connect(self._enviar_wa_orden_sel)
        fila_inf.addWidget(btn_wa)

        pa_lay.addLayout(fila_inf)
        lay.addWidget(panel_accion)
        return w

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
        self.tbl_ordenes.setRowCount(0)
        for idx, o in enumerate(ordenes):
            self.tbl_ordenes.insertRow(idx)
            vals = [
                f"#{int(o['folio']):04d}",
                o.get("cliente_nombre", ""),
                f"{o.get('marca', '')} {o.get('modelo', '')}".strip(),
                o.get("falla", ""),
                o.get("estatus", ""),
                o.get("ubicacion", ""),
                f"{simbolo}{float(o.get('costo_total') or 0.0):,.2f}",
                f"{simbolo}{float(o.get('saldo') or 0.0):,.2f}",
            ]
            for c_idx, val in enumerate(vals):
                self.tbl_ordenes.setItem(idx, c_idx, QTableWidgetItem(val))

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
        self.lbl_folio_sel.setText(f"Folio #{folio:04d} — {o.get('cliente_nombre', '')}")
        self.cmb_orden_estatus.setCurrentText(o.get("estatus", "Recibido"))
        idx_u = self.cmb_orden_ubicacion.findText(o.get("ubicacion", ""))
        if idx_u >= 0:
            self.cmb_orden_ubicacion.setCurrentIndex(idx_u)
        self.spn_orden_abono.setValue(float(o.get("saldo") or 0.0))

    def _actualizar_orden_sel(self):
        folio = self._folio_seleccionado()
        if not folio:
            QMessageBox.information(self, "Selecciona orden", "Primero selecciona una orden de la tabla.")
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
            QMessageBox.information(self, "Selecciona orden", "Primero selecciona una orden de la tabla.")
            return
        monto = self.spn_orden_abono.value()
        if monto <= 0:
            QMessageBox.warning(self, "Monto inválido", "Ingresa un monto mayor a cero.")
            return
        self.service.registrar_pago(folio, monto, self.cmb_orden_mpago.currentText())
        self.refrescar_ordenes()
        QMessageBox.information(self, "Abono registrado", f"Abono aplicado a la orden #{folio:04d}.")

    def _imprimir_orden_sel(self):
        folio = self._folio_seleccionado()
        if not folio:
            QMessageBox.information(self, "Selecciona orden", "Primero selecciona una orden de la tabla.")
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
            QMessageBox.information(self, "Selecciona orden", "Primero selecciona una orden de la tabla.")
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
    # 3. CLIENTES
    # ------------------------------------------
    def _build_clientes_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)

        lbl = QLabel("Directorio y Expediente de Clientes")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        self.txt_buscar_cli = QLineEdit()
        self.txt_buscar_cli.setPlaceholderText("Buscar cliente por nombre, teléfono o correo...")
        self.txt_buscar_cli.textChanged.connect(self.refrescar_clientes)
        lay.addWidget(self.txt_buscar_cli)

        self.tbl_clientes = QTableWidget(0, 6)
        self.tbl_clientes.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Teléfono", "Órdenes", "Total Facturado", "Saldo Pendiente"]
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
    # 4. CATÁLOGO Y UBICACIONES
    # ------------------------------------------
    def _build_catalogo_ubicaciones_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)

        lbl = QLabel("Catálogo de Servicios y Ubicaciones Físicas")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        tabs = QTabWidget()

        # Subpestaña Servicios
        p_serv = QWidget()
        l_serv = QVBoxLayout(p_serv)
        row_s = QHBoxLayout()
        row_s.setSpacing(8)
        self.s_cat = QComboBox()
        self.s_cat.setMinimumWidth(125)
        self.s_cat.addItems(CATEGORIAS_EQUIPO)
        self.s_marca = QLineEdit()
        self.s_marca.setPlaceholderText("Marca (opcional)")
        self.s_modelo = QLineEdit()
        self.s_modelo.setPlaceholderText("Modelo (opcional)")
        self.s_nombre = QLineEdit()
        self.s_nombre.setPlaceholderText("Nombre del servicio (ej. Cambio de pantalla)")
        self.s_precio = QDoubleSpinBox()
        self.s_precio.setRange(0, 999999)
        self.s_precio.setDecimals(2)
        self.s_precio.setMinimumWidth(110)
        btn_add_s = QPushButton("Agregar Servicio")
        btn_add_s.setObjectName("PrimaryBtn")
        btn_add_s.setMinimumWidth(140)
        btn_add_s.clicked.connect(self._agregar_servicio)
        for widget in (self.s_cat, self.s_marca, self.s_modelo, self.s_nombre, self.s_precio, btn_add_s):
            row_s.addWidget(widget)
        l_serv.addLayout(row_s)

        self.tbl_servicios = QTableWidget(0, 5)
        self.tbl_servicios.setHorizontalHeaderLabels(
            ["ID", "Categoría", "Marca / Modelo", "Servicio", "Precio"]
        )
        _configurar_tabla(self.tbl_servicios, stretch_col=3)
        l_serv.addWidget(self.tbl_servicios, 1)

        # Subpestaña Ubicaciones
        p_ub = QWidget()
        l_ub = QVBoxLayout(p_ub)
        row_u = QHBoxLayout()
        row_u.setSpacing(8)
        self.u_nombre = QLineEdit()
        self.u_nombre.setPlaceholderText("Ej. Estante A-1, Gaveta 3")
        self.u_tipo = QLineEdit()
        self.u_tipo.setPlaceholderText("Tipo (Ej. Estante, Gaveta, Vitrinas)")
        self.u_desc = QLineEdit()
        self.u_desc.setPlaceholderText("Descripción")
        btn_add_u = QPushButton("Agregar Ubicación")
        btn_add_u.setObjectName("PrimaryBtn")
        btn_add_u.setMinimumWidth(150)
        btn_add_u.clicked.connect(self._agregar_ubicacion)
        for widget in (self.u_nombre, self.u_tipo, self.u_desc, btn_add_u):
            row_u.addWidget(widget)
        l_ub.addLayout(row_u)

        self.tbl_ubicaciones = QTableWidget(0, 4)
        self.tbl_ubicaciones.setHorizontalHeaderLabels(["ID", "Nombre", "Tipo", "Descripción"])
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
    # 5. REPORTES FINANCIEROS
    # ------------------------------------------
    def _build_reportes_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(14)

        lbl = QLabel("Reportes Financieros y Ganancias")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(12)
        c_dia, self.r_dia, _ = _make_card("Ingresos del Día", "$0.00")
        c_mes, self.r_mes, _ = _make_card("Ingresos del Mes", "$0.00")
        c_gan, self.r_gan, _ = _make_card(
            "Ganancia Neta (Mes)", "$0.00", "Total órdenes mes menos repuestos"
        )
        c_sal, self.r_sal, _ = _make_card("Saldos por Cobrar", "$0.00")
        for c in (c_dia, c_mes, c_gan, c_sal):
            row.addWidget(c)
        lay.addLayout(row)

        self.tbl_rep_cat = QTableWidget(0, 5)
        self.tbl_rep_cat.setHorizontalHeaderLabels(
            ["Categoría", "Órdenes", "Facturado", "Costo Repuestos", "Ganancia Estimada"]
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
    # 6. WHATSAPP Y TICKETS
    # ------------------------------------------
    def _build_wa_tickets_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)

        lbl = QLabel("Historial de Notificaciones WhatsApp")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        self.tbl_wa = QTableWidget(0, 6)
        self.tbl_wa.setHorizontalHeaderLabels(["Folio", "Cliente", "Teléfono", "Tipo", "Fecha", "Mensaje"])
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
    # 7. CONFIGURACIÓN
    # ------------------------------------------
    def _build_config_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)

        lbl = QLabel("Configuración del Establecimiento y Apariencia")
        lbl.setObjectName("Title")
        lay.addWidget(lbl)

        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        form.setSpacing(10)
        form.setContentsMargins(18, 18, 18, 18)

        self.cfg_nombre = QLineEdit(
            self.config.get("identidad", "nombre_establecimiento", "ABCell Tizimin")
        )
        self.cfg_tel = QLineEdit(self.config.get("contacto", "telefono", ""))
        self.cfg_dir = QLineEdit(self.config.get("contacto", "direccion", ""))
        self.cfg_impresora = QLineEdit(self.config.get("notas", "impresora", ""))
        self.cfg_tema = QComboBox()
        self.cfg_tema.addItems(["Oscuro", "Claro"])
        self.cfg_tema.setCurrentText("Claro" if self._es_tema_claro() else "Oscuro")
        self.cfg_tema.currentTextChanged.connect(self._cambiar_tema_desde_combo)

        row_logo = QHBoxLayout()
        self.cfg_logo = QLineEdit(self.config.get("identidad", "logo_personalizado", ""))
        btn_logo = QPushButton("Elegir logo")
        btn_logo.clicked.connect(self._elegir_logo)
        row_logo.addWidget(self.cfg_logo)
        row_logo.addWidget(btn_logo)

        form.addRow("Nombre del negocio:", self.cfg_nombre)
        form.addRow("Teléfono / WhatsApp:", self.cfg_tel)
        form.addRow("Dirección:", self.cfg_dir)
        form.addRow("Impresora 58mm:", self.cfg_impresora)
        form.addRow("Tema visual (Oscuro / Claro):", self.cfg_tema)
        form.addRow("Logo personalizado:", row_logo)

        lay.addWidget(card)

        btn_save = QPushButton("Guardar Configuración")
        btn_save.setObjectName("PrimaryBtn")
        btn_save.setMinimumWidth(180)
        btn_save.clicked.connect(self._guardar_config)
        lay.addWidget(btn_save, alignment=Qt.AlignRight)
        lay.addStretch()
        return w

    def _cambiar_tema_desde_combo(self, nuevo_tema: str):
        self.config.set("apariencia", "tema", nuevo_tema)
        self.config.save()
        self.aplicar_tema()

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
        self.config.set("notas", "impresora", self.cfg_impresora.text().strip())
        self.config.set("apariencia", "tema", self.cfg_tema.currentText())
        self.config.set("identidad", "logo_personalizado", self.cfg_logo.text().strip())
        self.config.save()

        self.aplicar_tema()
        self.lbl_brand_sidebar.setText(self.cfg_nombre.text().strip() or "ABCell Pro")
        self._cargar_logo_widget(self.lbl_logo_sidebar, 68)
        QMessageBox.information(self, "Guardado", "La configuración se guardó correctamente.")
        self.refrescar_todo()

    def refrescar_todo(self):
        self.refrescar_dashboard()
        self._cargar_combos_orden()
        self.refrescar_ordenes()
        self.refrescar_clientes()
        self.refrescar_catalogo_ubicaciones()
        self.refrescar_reportes()
        self.refrescar_wa()
