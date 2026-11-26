"""Regresión visual: requiere Qt y sus bibliotecas gráficas de sistema."""
import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "windows" if sys.platform == "win32" else "offscreen")
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
    from ui.layouts import (
        ActionButton, AdaptiveDialog, ContentCombo, FlowLayout, MultilineInput,
        ReadableTable, BUTTON_HEIGHT, button_content_size, install_visual_policy,
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

    def test_save_configuration_button_persists_and_feeds_printing(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from PIL import Image
        from config.settings import ConfigManager
        from database.db_manager import DatabaseManager
        from ui.main_window import MainWindow
        from integrations.printer_58mm import generar_texto_ticket
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = ConfigManager(str(root / "config.json"))
            db = DatabaseManager(str(root / "test.db"))
            window = MainWindow(db, config)
            try:
                window.show()
                window.ir_a_seccion(6)
                button = next(b for b in window.findChildren(QPushButton)
                              if b.text() == "Guardar Configuración")
                for name, color in (("Taller Norte", "red"), ("Servicio Sur", "blue")):
                    logo = root / "elegido.png"
                    Image.new("RGB", (80, 40), color).save(logo)
                    window.cfg_nombre.setText(name)
                    window.cfg_tel.setText("9611234567")
                    window.cfg_dir.setText("Avenida Central 123")
                    window.cfg_logo.setText(str(logo))
                    window.cfg_garantia.setPlainText("Garantía actualizada")
                    with patch("ui.main_window.QMessageBox.information") as success:
                        button.click()  # Regresión: antes no había señal conectada.
                        self.settle()
                        success.assert_called_once()
                    saved = ConfigManager(config.config_path)
                    self.assertEqual(saved.get("identidad", "nombre_establecimiento"), name)
                    self.assertIn(name, window.windowTitle())
                    self.assertNotEqual(window.cfg_logo.text(), str(logo))
                    note = generar_texto_ticket({"folio": 1}, saved)
                    self.assertIn(name.upper(), note)
                    self.assertIn("Avenida Central 123", note)
                    with patch("ui.main_window.imprimir_ticket_prueba", return_value=(True, "OK")) as printing, \
                         patch("ui.main_window.QMessageBox.information"):
                        window._probar_impresora()
                        self.assertIs(printing.call_args.args[0], config)
                        self.assertEqual(printing.call_args.args[0].get("notas", "nombre_comercial"), name)
            finally:
                window.close()
                db.cerrar()

    def test_filter_labels_blend_into_parent_surface_in_all_themes(self):
        from PySide6.QtWidgets import QFrame
        from ui.main_window import _campo_filtro
        from ui.theme import PALETAS_TEMAS
        try:
            for name, palette in PALETAS_TEMAS.items():
                with self.subTest(theme=name):
                    self.app.setStyleSheet(construir_qss(name))
                    panel = QFrame()
                    panel.setObjectName("SubBar")
                    layout = QVBoxLayout(panel)
                    field = _campo_filtro("Método de pago", ContentCombo())
                    layout.addWidget(field)
                    panel.resize(400, 150)
                    panel.show()
                    self.settle()
                    label = field.findChild(QLabel)
                    image = panel.grab().toImage()
                    # A la derecha del texto: tanto el wrapper como la etiqueta
                    # deben mostrar la superficie de SubBar, no el fondo raíz.
                    from PySide6.QtCore import QPoint
                    for widget in (field, label):
                        point = widget.mapTo(panel, QPoint(widget.width() - 3, 3))
                        self.assertEqual(image.pixelColor(point).name(), palette["subcard_bg"])
                    panel.close()
        finally:
            self.app.setStyleSheet(construir_qss("Lima Pro"))

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
        self.assertGreaterEqual(button.height(), BUTTON_HEIGHT)
        dialog.close()

    def test_combo_is_compact_but_preserves_complete_options(self):
        combo = ContentCombo()
        text = "Una ubicación con nombre considerablemente más largo " * 3
        combo.addItems(["Corto", text])
        combo.setCurrentIndex(1)
        self.assertLessEqual(combo.sizeHint().width(), 240)
        self.assertEqual(combo.minimumSizeHint().width(), 110)
        self.assertEqual(combo.currentText(), text)
        self.assertEqual(combo.toolTip(), text)

    def test_multiline_api_preserves_long_notes(self):
        field = MultilineInput("Falla reportada\nSegunda línea")
        self.assertEqual(field.text(), "Falla reportada\nSegunda línea")
        field.setText("Diagnóstico " * 50)
        self.assertEqual(field.text(), "Diagnóstico " * 50)
        self.assertGreaterEqual(field.minimumHeight(), 80)

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

    def test_catalog_fits_1358_by_690_desktop(self):
        import tempfile
        from pathlib import Path
        from config.settings import ConfigManager
        from database.db_manager import DatabaseManager
        from ui.main_window import MainWindow
        from PySide6.QtWidgets import QPushButton, QScrollArea
        with tempfile.TemporaryDirectory() as tmp:
            db = DatabaseManager(str(Path(tmp) / "test.db"))
            window = MainWindow(db, ConfigManager(str(Path(tmp) / "config.json")))
            try:
                for index in range(25):
                    window.service.guardar_servicio({"nombre": "Mantenimiento Nintendo Switch",
                        "categoria": "Consolas", "marca": "Nintendo Switch / OLED", "precio": 1200})
                window.resize(1358, 690)
                window.show()
                window.ir_a_seccion(3)
                self.settle()
                table = window.tbl_servicios
                table.fit_contents()
                self.settle()
                self.assertLessEqual(window.sidebar.width(), 280, {
                    "sidebar_hint": window.sidebar.sizeHint().toTuple(),
                    "navigation": [(b.text(), b.minimumSize().toTuple(), b.sizeHint().toTuple(),
                                    b.font().toString()) for b in window.nav_buttons],
                    "brand": window.lbl_brand_sidebar.sizeHint().toTuple(),
                })
                self.assertEqual(table.horizontalScrollBar().maximum(), 0)
                action_cell = table.cellWidget(0, 5)
                self.assertLessEqual(action_cell.geometry().right(), table.viewport().width())
                for button in action_cell.findChildren(QPushButton):
                    self.assertTrue(action_cell.rect().contains(button.geometry()))
                for scroll in window.stack.currentWidget().findChildren(QScrollArea):
                    if scroll.isVisible():
                        self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
                self.assertFalse(window.windowIcon().isNull())
                self.assertIn("ABCell Pro", window.windowTitle())
                self.assertEqual(window.lbl_autor.text(), "Autor: ABCell Profecional")
                self.assertTrue(window.lbl_autor.isVisible())
                self.assertTrue(window.sidebar.rect().contains(window.lbl_autor.geometry()))
            finally:
                window.close()
                db.cerrar()

    def test_svg_icons_use_requested_contrast_color(self):
        from ui.icons import icono
        image = icono("orden", "#c5f467", 24).pixmap(24, 24).toImage()
        pixels = [image.pixelColor(x, y) for x in range(image.width()) for y in range(image.height())]
        self.assertTrue(any(p.alpha() > 128 and p.green() > 180 and p.red() > 140 for p in pixels))

    def test_qt_standard_button_uses_global_policy(self):
        button = QPushButton("Confirmar operación")
        button.show()
        self.settle()
        self.assertGreaterEqual(button.height(), BUTTON_HEIGHT)
        self.assertGreaterEqual(button.width(), button_content_size(button).width())
        button.close()


if __name__ == "__main__":
    unittest.main()
