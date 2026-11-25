"""Distribución adaptable y controles con espacio real para texto e iconos.

Todas las medidas son píxeles lógicos de Qt: escalan con el DPI del monitor.
"""
import atexit
import sys

from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import QEvent, QLibraryInfo, QObject, QRect, QSize, Qt, QTimer, QTranslator
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QComboBox, QFormLayout, QLabel, QLayout,
    QDialog, QHeaderView, QLineEdit, QPlainTextEdit, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QStyle, QVBoxLayout,
    QStyleOptionButton, QTableWidget, QWidget, QWidgetItem,
)

from ui.table_sizing import fit_column_widths

BUTTON_HEIGHT = 32
INPUT_HEIGHT = 32


def button_content_size(button):
    """Caja mínima: glifos + icono + separación + padding y bordes."""
    text = button.text().replace("&&", "\0").replace("&", "").replace("\0", "&")
    lines = text.splitlines() or [""]
    metrics = button.fontMetrics()
    width = max(metrics.horizontalAdvance(line) for line in lines)
    height = metrics.lineSpacing() * len(lines)
    if not button.icon().isNull():
        width += button.iconSize().width() + (6 if text else 0)
        height = max(height, button.iconSize().height())
    return QSize(max(32, width + 24), max(BUTTON_HEIGHT, height + 12))


class ActionButton(QPushButton):
    """Nunca sacrifica el contenido para caber en una fila: la fila debe envolver."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(BUTTON_HEIGHT)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        if text:
            self.setAccessibleName(text)

    def sizeHint(self):
        return super().sizeHint().expandedTo(button_content_size(self))

    def minimumSizeHint(self):
        return self.sizeHint()

    def setText(self, text):
        super().setText(text)
        self.setAccessibleName(text or self.toolTip())
        self.updateGeometry()


class FlowLayout(QLayout):
    """Fila que pasa elementos completos a otra línea, incluidos sublayouts.

    A diferencia de una fila rígida, el mínimo horizontal es el elemento más
    ancho, no la suma de todos. Los campos con stretch absorben el espacio
    libre en su línea. Los espaciadores no crean líneas vacías.
    """
    def __init__(self, parent=None, spacing=8):
        super().__init__(parent)
        self._items = []
        self._stretch = {}
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)
        self.invalidate()

    def addWidget(self, widget, stretch=0, alignment=Qt.Alignment()):
        self.addChildWidget(widget)
        item = QWidgetItem(widget)
        item.setAlignment(alignment)
        self._stretch[id(item)] = stretch
        self.addItem(item)

    def addLayout(self, layout, stretch=0):
        self.addChildLayout(layout)
        self._stretch[id(layout)] = stretch
        self.addItem(layout)

    def addStretch(self, stretch=1):
        # Al envolver no se necesita un resorte que consuma una línea entera.
        pass

    def addSpacing(self, size):
        self.addItem(QSpacerItem(size, 1, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < self.count() else None

    def takeAt(self, index):
        if 0 <= index < self.count():
            item = self._items.pop(index)
            self._stretch.pop(id(item), None)
            return item
        return None

    def expandingDirections(self):
        return Qt.Orientation.Horizontal

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._arrange(QRect(0, 0, max(1, width), 0), True)

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            if not item.isEmpty():
                size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        return size + QSize(margins.left() + margins.right(), margins.top() + margins.bottom())

    def sizeHint(self):
        # Ancho ideal acotado para que un diálogo no intente ocupar todo el monitor.
        width = min(920, max(320, sum(i.sizeHint().width() + self.spacing()
                                       for i in self._items if not i.isEmpty())))
        width = max(width, self.minimumSize().width())
        return QSize(width, self.heightForWidth(width))

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._arrange(rect, False)

    def _arrange(self, rect, test):
        margins = self.contentsMargins()
        area = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        available = max(1, area.width())
        rows, row, used = [], [], 0
        for item in self._items:
            if item.isEmpty():
                continue
            minimum = item.minimumSize().width()
            desired = max(minimum, item.sizeHint().width())
            width = min(available, desired)
            # Nunca reducir por debajo del mínimo; el scroll exterior resuelve
            # un elemento individual que sea más ancho que el viewport.
            width = max(minimum, width)
            if row and used + self.spacing() + width > available:
                rows.append(row)
                row, used = [], 0
            row.append((item, width))
            used += width + (self.spacing() if len(row) > 1 else 0)
        if row:
            rows.append(row)
        y = area.y()
        for row in rows:
            extra = max(0, available - sum(w for _, w in row) - self.spacing() * (len(row) - 1))
            weights = [self._stretch.get(id(item), 0) for item, _ in row]
            total = sum(weights)
            widths = [w + (extra * weight // total if total else 0)
                      for (_, w), weight in zip(row, weights)]
            heights = [max(item.minimumSize().height(),
                           item.heightForWidth(w) if item.hasHeightForWidth() else item.sizeHint().height())
                       for (item, _), w in zip(row, widths)]
            height = max(heights, default=0)
            x = area.x()
            for (item, _), width, item_height in zip(row, widths, heights):
                if not test:
                    item.setGeometry(QRect(x, y, width, height if item.expandingDirections() & Qt.Vertical else item_height))
                x += width + self.spacing()
            y += height + self.spacing()
        return max(0, y - area.y() - (self.spacing() if rows else 0)) + margins.top() + margins.bottom()


def scroll_page(widget):
    """Respaldo de accesibilidad para ventanas pequeñas, fuentes grandes y DPI alto."""
    if isinstance(widget, QScrollArea):
        return widget
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.NoFrame)
    scroll.setWidget(widget)
    scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    return scroll


class VisualPolicy(QObject):
    """También protege los botones creados por Qt en mensajes y diálogos nativos Qt."""
    def eventFilter(self, obj, event):
        if sys.is_finalizing() or getattr(self, "_applying", False):
            return False
        self._applying = True
        try:
            self._apply(obj, event)
        finally:
            self._applying = False
        return False

    def _apply(self, obj, event):
        if event.type() in (QEvent.Polish, QEvent.Show):
            if isinstance(obj, QPushButton):
                obj.setMaximumHeight(16777215)
                minimum = button_content_size(obj).expandedTo(obj.sizeHint())
                obj.setMinimumSize(minimum)
                obj.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
                obj.setAccessibleName(obj.text() or obj.toolTip() or "Acción")
            elif isinstance(obj, QLabel) and obj.text() and (obj.pixmap() is None or obj.pixmap().isNull()):
                obj.setWordWrap(True)
                obj.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            elif isinstance(obj, (QLineEdit, QComboBox, QAbstractSpinBox)):
                internal_editor = isinstance(obj, QLineEdit) and isinstance(obj.parentWidget(), (QComboBox, QAbstractSpinBox))
                if not internal_editor:
                    obj.setMinimumHeight(max(INPUT_HEIGHT, obj.fontMetrics().height() + 12))
                if isinstance(obj, QComboBox):
                    obj.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
                    obj.setMinimumContentsLength(10)
                    obj.view().setTextElideMode(Qt.ElideNone)
                    obj.setToolTip(obj.currentText())
            if isinstance(obj, QWidget) and obj.layout():
                self._forms(obj.layout())
        return False

    def _forms(self, layout):
        if isinstance(layout, QFormLayout):
            layout.setRowWrapPolicy(QFormLayout.WrapLongRows)
            layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            layout.setHorizontalSpacing(12)
            layout.setVerticalSpacing(8)
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if item.layout():
                self._forms(item.layout())


def install_visual_policy(app):
    if not hasattr(app, "_abcell_visual_policy"):
        QApplication.setAttribute(Qt.AA_DontUseNativeDialogs, True)
        app.setStyle("Fusion")
        palette = QPalette()
        for role, color in ((QPalette.Window, "#0c111b"), (QPalette.WindowText, "#edf2f7"),
                            (QPalette.Base, "#0f1826"), (QPalette.AlternateBase, "#182434"),
                            (QPalette.Text, "#edf2f7"), (QPalette.Button, "#1d2a3b"),
                            (QPalette.ButtonText, "#edf2f7"), (QPalette.Highlight, "#2a4329"),
                            (QPalette.HighlightedText, "#e4ffc6")):
            palette.setColor(role, QColor(color))
        app.setPalette(palette)
        app._abcell_visual_policy = VisualPolicy(app)
        app.installEventFilter(app._abcell_visual_policy)
        policy = app._abcell_visual_policy

        def uninstall():
            from shiboken6 import isValid
            if isValid(app) and isValid(policy):
                app.removeEventFilter(policy)

        # Retirar el filtro antes de la destrucción Qt/shiboken al cerrar el proceso.
        app.aboutToQuit.connect(uninstall)
        atexit.register(uninstall)
        translator = QTranslator(app)
        if translator.load("qtbase_es", QLibraryInfo.path(QLibraryInfo.TranslationsPath)):
            app.installTranslator(translator)
            app._abcell_translator = translator
    return app._abcell_visual_policy


class AdaptiveDialog(QDialog):
    """Los formularios largos se desplazan dentro del monitor, no fuera de él."""
    def prepare_layout(self):
        if self.property("adaptivePrepared") or not self.layout():
            return
        self.setProperty("adaptivePrepared", True)
        original = self.layout()
        content = QWidget()
        inner = QVBoxLayout(content)
        inner.setContentsMargins(4, 4, 4, 4)
        inner.setSpacing(10)
        # Las acciones finales quedan visibles; solo se desplaza el formulario.
        footer = None
        if original.count():
            last = original.itemAt(original.count() - 1)
            last_layout = last.layout()
            action_row = last_layout is not None and all(
                last_layout.itemAt(i).spacerItem() is not None
                or isinstance(last_layout.itemAt(i).widget(), QPushButton)
                for i in range(last_layout.count())
            )
            if action_row or isinstance(last.widget(), QPushButton):
                footer = original.takeAt(original.count() - 1)
        while original.count():
            item = original.takeAt(0)
            if item.widget():
                inner.addWidget(item.widget())
            elif item.layout():
                item.layout().setParent(None)
                inner.addLayout(item.layout())
            else:
                inner.addItem(item)
        original.addWidget(scroll_page(content), 1)
        if footer is not None:
            if footer.layout():
                footer.layout().setParent(None)
                original.addLayout(footer.layout())
            else:
                original.addWidget(footer.widget())
        screen = self.screen().availableGeometry()
        self.setMinimumHeight(0)
        self.setMinimumWidth(min(self.minimumWidth(), max(280, screen.width() - 40)))
        self.resize(min(720, screen.width() - 40), min(640, screen.height() - 60))
        self.setMaximumSize(screen.width() - 24, screen.height() - 24)

    def exec(self):
        self.prepare_layout()
        return super().exec()


class ReadableTable(QTableWidget):
    """Filas multilinea y columnas de acciones dimensionadas por sus widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWordWrap(True)
        self.setTextElideMode(Qt.ElideNone)
        self.setMinimumSize(240, 160)
        self._fit_timer = QTimer(self)
        self._fit_timer.setSingleShot(True)
        self._fit_timer.timeout.connect(self.fit_contents)
        self._fitting = False
        self.horizontalHeader().sectionResized.connect(self._schedule_fit)

    def _schedule_fit(self, *args):
        if not self._fitting:
            self._fit_timer.start(0)

    def setItem(self, row, column, item):
        item.setToolTip(item.text())
        super().setItem(row, column, item)
        self._fit_timer.start(0)

    def setCellWidget(self, row, column, widget):
        super().setCellWidget(row, column, widget)
        widget.ensurePolished()
        if widget.layout():
            widget.layout().activate()
        self._fit_timer.start(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_fit_timer"):
            self._schedule_fit()

    def viewportEvent(self, event):
        result = super().viewportEvent(event)
        if event.type() == QEvent.Resize and hasattr(self, "_fit_timer"):
            self._schedule_fit()
        return result

    def fit_contents(self):
        if self._fitting:
            return
        self._fitting = True
        try:
            header = self.horizontalHeader()
            header.setStretchLastSection(False)
            preferred, minimum, weights = [], [], []
            for column in range(self.columnCount()):
                title = self.horizontalHeaderItem(column)
                name = title.text().upper() if title else ""
                heading = self.fontMetrics().horizontalAdvance(name) + 20
                is_action = name == "ACCIONES"
                is_id = name in ("ID", "N°", "Nº", "FOLIO", "NÚMERO")
                is_number = any(key in name for key in ("PRECIO", "COSTO", "SALDO", "STOCK", "TOTAL", "ÓRDENES", "FACTURADO", "GANANCIA"))
                low = max(heading, 38 if is_id else 76 if is_number else 90)
                desired = low
                for row in range(self.rowCount()):
                    widget = self.cellWidget(row, column)
                    if widget:
                        # El estilo de celda añade 8 px por lado y 4 arriba/abajo.
                        needed = max(widget.minimumSizeHint().width(), widget.sizeHint().width()) + 20
                        low = max(low, needed)
                        desired = max(desired, low)
                    else:
                        item = self.item(row, column)
                        if item:
                            natural = self.fontMetrics().horizontalAdvance(item.text()) + 20
                            desired = max(desired, min(320, natural))
                preferred.append(max(low, desired))
                minimum.append(low)
                weights.append(0 if is_action or is_id or is_number else 1)
            available = self.viewport().width() - 2
            widths = fit_column_widths(preferred, minimum, available, weights)
            for column, width in enumerate(widths):
                self.setColumnWidth(column, width)
            self.doItemsLayout()
            self.resizeRowsToContents()
            for row in range(self.rowCount()):
                height = max(36, self.rowHeight(row))
                for column in range(self.columnCount()):
                    widget = self.cellWidget(row, column)
                    if widget:
                        height = max(height, widget.sizeHint().height() + 12)
                self.setRowHeight(row, height)
            self.doItemsLayout()
        finally:
            self._fitting = False
        if self.viewport().width() - 2 != available:
            self._fit_timer.start(0)


class ContentCombo(QComboBox):
    """El texto seleccionado siempre cabe; el desplegable conserva textos completos."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentTextChanged.connect(self._content_changed)

    def _content_changed(self, text):
        self.setToolTip(text)
        self.updateGeometry()

    def minimumSizeHint(self):
        return QSize(110, INPUT_HEIGHT)

    def sizeHint(self):
        width = self.fontMetrics().horizontalAdvance(self.currentText()) + 36
        return QSize(max(140, min(240, width)), INPUT_HEIGHT)

    def showPopup(self):
        longest = max((self.fontMetrics().horizontalAdvance(self.itemText(i))
                       for i in range(self.count())), default=0)
        available = self.screen().availableGeometry().width() - 40
        self.view().setMinimumWidth(min(available, max(self.width(), longest + 44)))
        super().showPopup()


class MultilineInput(QPlainTextEdit):
    """Descripción con ajuste de línea y API text/setText de los formularios."""
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setPlainText(text)
        self.setMinimumHeight(80)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)
