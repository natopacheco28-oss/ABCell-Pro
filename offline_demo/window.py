"""Interfaz demo con estilo compartido, sin importar la ventana completa."""
from datetime import datetime
from pathlib import Path
import sqlite3

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QSizePolicy,
    QStackedWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from ui.icons import icono
from ui.layouts import ActionButton, FlowLayout, ReadableTable, scroll_page
from offline_demo.store import DemoStore, MAX_ORDERS
from offline_demo.trial import TrialBlocked

ASSETS = Path(__file__).resolve().parent.parent / "ui" / "assets"


class DemoWindow(QMainWindow):
    def __init__(self, store: DemoStore):
        super().__init__()
        self.store = store
        self._closed = False
        self._blocked = False
        self.buttons = []
        self.setWindowTitle("ABCell Pro Demo — " + store.workshop()["name"])
        self.setWindowIcon(QIcon(str(ASSETS / "abcell-pro.ico")))
        self.resize(1280, 760)
        self.setMinimumSize(900, 600)
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.sidebar.setMinimumWidth(228)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(12, 16, 12, 12)
        side.setSpacing(8)
        brand = QHBoxLayout()
        logo = QLabel()
        logo.setFixedSize(44, 44)
        logo.setPixmap(QPixmap(str(ASSETS / "abcell-pro.jpg")).scaled(42, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        brand.addWidget(logo)
        title = QLabel("ABCell Pro\nDEMO")
        title.setObjectName("BrandTitle")
        brand.addWidget(title)
        side.addLayout(brand)
        self.time_label = QLabel()
        self.time_label.setObjectName("CardSub")
        self.time_label.setWordWrap(True)
        side.addWidget(self.time_label)
        self.nav = []
        for text, icon, index in (("Órdenes de trabajo", "orden", 0), ("Nueva orden", "nueva-orden", 1),
                                  ("Configuración de taller", "configuracion", 2), ("Sobre la demo", "info", 3)):
            button = self._button(text, lambda checked=False, i=index: self.navigate(i), icon, "NavBtn")
            button.setMinimumHeight(38)
            self.nav.append(button)
            side.addWidget(button)
        for text in ("Inventario", "Catálogo y Ubicaciones", "Estadísticas y Caja", "Utilidades Android"):
            button = self._button(text, None, "", "NavBtn")
            button.setEnabled(False)
            button.setToolTip("Disponible únicamente en ABCell Pro completo; no incluido en esta edición.")
            side.addWidget(button)
        side.addStretch()
        author = QLabel("Autor: ABCell Profecional")
        author.setObjectName("CardSub")
        side.addWidget(author)
        outer.addWidget(self.sidebar)
        self.stack = QStackedWidget()
        outer.addWidget(self.stack, 1)
        for page in (self._orders_page(), self._new_page(), self._settings_page(), self._about_page()):
            self.stack.addWidget(scroll_page(page))
        self.timer = QTimer(self)
        self.timer.setInterval(30000)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start()
        self.navigate(0)
        self.refresh_status()

    def _button(self, text, callback=None, icon="", name="SecondaryBtn"):
        button = ActionButton(text)
        button.setObjectName(name)
        if icon:
            button.setIcon(icono(icon, "#14200b" if name == "PrimaryBtn" else "#c2cfdf", 16))
        if callback is not None:
            button.clicked.connect(callback)
        self.buttons.append(button)
        return button

    def _page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)
        heading = QLabel(title)
        heading.setObjectName("Title")
        layout.addWidget(heading)
        return page, layout

    def _orders_page(self):
        page, layout = self._page("Órdenes de trabajo — DEMO")
        note = QLabel("Consulta y alta de hasta 20 órdenes. Edición, abonos, impresión y exportación no están incluidos.")
        note.setWordWrap(True)
        note.setObjectName("CardSub")
        layout.addWidget(note)
        row = FlowLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar cliente, marca, modelo o folio")
        self.search.setMinimumWidth(220)
        self.search.textChanged.connect(self.refresh_orders)
        row.addWidget(self.search, 1)
        row.addWidget(self._button("Nueva orden", lambda: self.navigate(1), "nueva-orden", "PrimaryBtn"))
        layout.addLayout(row)
        self.table = ReadableTable(0, 7)
        self.table.setHorizontalHeaderLabels(["FOLIO", "FECHA", "CLIENTE", "EQUIPO / MODELO", "FALLA", "PRECIO", "ESTADO"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table, 1)
        self.count_label = QLabel()
        layout.addWidget(self.count_label)
        return page

    def _new_page(self):
        page, layout = self._page("Nueva orden — DEMO")
        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        form.setContentsMargins(14, 12, 14, 12)
        self.fields = {}
        for name, label in (("client", "Cliente:"), ("phone", "Teléfono:"), ("brand", "Marca:"), ("model", "Modelo:")):
            field = QLineEdit()
            field.setMaxLength(2000)
            self.fields[name] = field
            form.addRow(label, field)
        self.fault = QPlainTextEdit()
        self.fault.setMinimumHeight(100)
        form.addRow("Falla reportada:", self.fault)
        self.total = QDoubleSpinBox()
        self.total.setRange(0, 999999)
        self.total.setDecimals(2)
        self.total.setPrefix("$ ")
        form.addRow("Precio total:", self.total)
        layout.addWidget(card)
        row = FlowLayout()
        self.save_button = self._button("Guardar orden", self.save_order, "guardar", "PrimaryBtn")
        row.addWidget(self.save_button)
        row.addWidget(self._button("Limpiar", self.clear_form))
        layout.addLayout(row)
        note = QLabel("Solo datos de prueba. La demo usa una base separada de la versión completa y no elimina las órdenes al vencer.")
        note.setWordWrap(True)
        note.setObjectName("CardSub")
        layout.addWidget(note)
        layout.addStretch()
        return page

    def _settings_page(self):
        page, layout = self._page("Configuración del taller — DEMO")
        data = self.store.workshop()
        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        self.workshop_fields = {}
        for key, label in (("name", "Nombre del negocio:"), ("phone", "Teléfono:"), ("address", "Dirección:")):
            field = QLineEdit(data[key])
            field.setMaxLength(500)
            self.workshop_fields[key] = field
            form.addRow(label, field)
        layout.addWidget(card)
        layout.addWidget(self._button("Guardar Configuración", self.save_settings, "guardar", "PrimaryBtn"), alignment=Qt.AlignRight)
        note = QLabel("La demo permite personalizar estos datos para la prueba. Logos de notas e impresión solo se incluyen en la versión completa.")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()
        return page

    def _about_page(self):
        page, layout = self._page("Prueba de 7 días sin internet")
        note = QLabel(
            "El plazo comienza la primera vez que abres la demo, no al descargar o descomprimir el ZIP. "
            "Son 7 días naturales (168 horas), aunque cierres el programa.\n\n"
            "Incluye alta y consulta de hasta 20 órdenes, búsqueda y datos básicos del taller. "
            "No incluye impresión, tickets digitales, exportación, edición de órdenes, abonos, "
            "inventario, catálogo, reportes, ADB ni modo maestro. Esas funciones no se empaquetan en esta edición.\n\n"
            "El registro se guarda en tu perfil de usuario de Windows, fuera del ZIP, con respaldo en "
            "HKEY_CURRENT_USER\\Software\\ABCell\\ABCellProDemo. Volver a descomprimir no reinicia la prueba "
            "en el mismo perfil. Cambiar de perfil o borrar todos los registros puede eludir un control local.\n\n"
            "Si detecta un atraso considerable del reloj, corrige la fecha y hora. Al vencer, solicita "
            "la versión completa al proveedor. Los datos no se borran. No se realizan conexiones de red."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        self.deadline = QLabel()
        self.deadline.setObjectName("FolioBadge")
        layout.addWidget(self.deadline)
        layout.addStretch()
        return page

    def _run(self, action):
        if self._blocked or self._closed:
            return
        try:
            self.store.trial.require_active()
            return action()
        except TrialBlocked as exc:
            self._blocked = True
            self.timer.stop()
            self.centralWidget().setEnabled(False)
            QMessageBox.warning(self, "ABCell Pro Demo — prueba bloqueada", str(exc))
            self.close()
        except (ValueError, OSError, sqlite3.Error) as exc:
            QMessageBox.warning(self, "No se pudo completar", str(exc))

    def navigate(self, index):
        def action():
            self.stack.setCurrentIndex(index)
            for i, button in enumerate(self.nav):
                button.setProperty("active", i == index)
                button.style().unpolish(button)
                button.style().polish(button)
            if index == 0:
                self.refresh_orders()
        self._run(action)

    def refresh_orders(self):
        def action():
            orders = self.store.list_orders(self.search.text())
            self.table.setRowCount(len(orders))
            for row, order in enumerate(orders):
                values = [f"#{order['folio']:04d}", order['created_at'], order['client'],
                          f"{order['brand']} {order['model']}", order['fault'],
                          f"${order['total_cents'] / 100:,.2f}", order['status']]
                for column, value in enumerate(values):
                    self.table.setItem(row, column, QTableWidgetItem(value))
            count = self.store.count()
            self.count_label.setText(f"Órdenes creadas: {count} / {MAX_ORDERS} · Resultados: {len(orders)}")
            self.save_button.setEnabled(count < MAX_ORDERS)
            self.table.fit_contents()
        self._run(action)

    def refresh_status(self):
        def action():
            status = self.store.trial.require_active()
            self.time_label.setText(f"Prueba: {status.days_left} día(s) restantes")
            end = datetime.fromtimestamp(status.expires_at).strftime("%d/%m/%Y %H:%M")
            self.deadline.setText(f"Vencimiento en esta PC: {end}")
        self._run(action)

    def clear_form(self):
        def action():
            for field in self.fields.values():
                field.clear()
            self.fault.clear()
            self.total.setValue(0)
        self._run(action)

    def save_order(self):
        def action():
            folio = self.store.create_order(**{key: field.text() for key, field in self.fields.items()},
                                            fault=self.fault.toPlainText(), total=self.total.value())
            self.clear_form()
            self.navigate(0)
            QMessageBox.information(self, "Orden guardada", f"Orden #{folio:04d} registrada en la demo.")
        self._run(action)

    def save_settings(self):
        def action():
            self.store.save_workshop(**{key: field.text() for key, field in self.workshop_fields.items()})
            self.setWindowTitle("ABCell Pro Demo — " + self.store.workshop()["name"])
            QMessageBox.information(self, "Guardado", "Datos del taller actualizados en la demo.")
        self._run(action)

    def closeEvent(self, event):
        if not self._closed:
            self.timer.stop()
            self.store.close()
            self._closed = True
        super().closeEvent(event)
