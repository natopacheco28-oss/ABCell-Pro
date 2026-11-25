"""Regresión visual: requiere Qt y sus bibliotecas gráficas de sistema."""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
    from ui.layouts import (
        ActionButton, AdaptiveDialog, ContentCombo, FlowLayout, MultilineInput,
        ReadableTable, button_content_size, install_visual_policy,
    )
    from ui.theme import construir_qss
    QT_ERROR = None
except ImportError as error:
    QT_ERROR = str(error)


@unittest.skipIf(QT_ERROR is not None, "Qt no disponible: " + str(QT_ERROR))
class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        install_visual_policy(cls.app)
        cls.app.setStyleSheet(construir_qss("Lima Pro"))

    def settle(self):
        for _ in range(6):
            self.app.processEvents()

    def test_flow_wraps_complete_buttons(self):
        parent = QWidget()
        row = FlowLayout(parent)
        buttons = [ActionButton("Acción completa de prueba") for _ in range(3)]
        for button in buttons:
            row.addWidget(button)
        parent.resize(400, 400)
        parent.show()
        self.settle()
        for button in buttons:
            self.assertGreaterEqual(button.width(), button_content_size(button).width())
            self.assertTrue(parent.rect().contains(button.geometry()))
        for left, right in zip(buttons, buttons[1:]):
            self.assertFalse(left.geometry().intersects(right.geometry()))
        parent.close()

    def test_dialog_reparents_content_to_scroll(self):
        dialog = AdaptiveDialog()
        layout = QVBoxLayout(dialog)
        for number in range(20):
            layout.addWidget(QLabel("Descripción técnica con ajuste de línea " * 3))
        button = ActionButton("Guardar cambios")
        layout.addWidget(button)
        dialog.prepare_layout()
        dialog.show()
        self.settle()
        self.assertIs(button.parentWidget(), dialog)
        self.assertTrue(dialog.rect().contains(button.geometry()))
        from PySide6.QtWidgets import QScrollArea
        self.assertTrue(dialog.findChildren(QScrollArea))
        self.assertGreaterEqual(button.height(), 44)
        dialog.close()

    def test_combo_reserves_complete_selected_text(self):
        combo = ContentCombo()
        combo.addItems(["Corto", "Una ubicación con nombre considerablemente más largo"])
        first = combo.sizeHint().width()
        combo.setCurrentIndex(1)
        self.assertGreater(combo.minimumSizeHint().width(), first)
        self.assertGreaterEqual(combo.minimumSizeHint().width(), combo.fontMetrics().horizontalAdvance(combo.currentText()) + 64)

    def test_multiline_api_preserves_long_notes(self):
        field = MultilineInput("Falla reportada\nSegunda línea")
        self.assertEqual(field.text(), "Falla reportada\nSegunda línea")
        field.setText("Diagnóstico " * 50)
        self.assertEqual(field.text(), "Diagnóstico " * 50)
        self.assertGreaterEqual(field.minimumHeight(), 120)

    def test_table_keeps_action_widgets_inside_cell(self):
        from PySide6.QtWidgets import QHBoxLayout
        table = ReadableTable(1, 1)
        table.setHorizontalHeaderLabels(["ACCIONES"])
        cell = QWidget()
        row = QHBoxLayout(cell)
        buttons = [ActionButton("Editar"), ActionButton("Eliminar")]
        for button in buttons:
            row.addWidget(button)
        table.setCellWidget(0, 0, cell)
        table.show()
        self.settle()
        table.fit_contents()
        self.settle()
        for button in buttons:
            self.assertTrue(cell.rect().contains(button.geometry()),
                            (cell.rect(), button.geometry()))
        table.close()

    def test_qt_standard_button_uses_global_policy(self):
        button = QPushButton("Confirmar operación")
        button.show()
        self.settle()
        self.assertGreaterEqual(button.height(), 44)
        self.assertGreaterEqual(button.width(), button_content_size(button).width())
        button.close()


if __name__ == "__main__":
    unittest.main()
