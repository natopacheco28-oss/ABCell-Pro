"""GUI demo aislada; no inicia la prueba real del perfil de usuario."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "windows" if sys.platform == "win32" else "offscreen")
try:
    from PySide6.QtWidgets import QApplication, QPushButton
    from offline_demo.window import DemoWindow
    from offline_demo.store import DemoStore
    from offline_demo.trial import Trial, FileRecord, DURATION
    from ui.layouts import install_visual_policy, button_content_size
    from ui.theme import construir_qss
    QT_ERROR = None
except ImportError as exc:
    QT_ERROR = str(exc)


@unittest.skipIf(QT_ERROR is not None, "Qt no disponible: " + str(QT_ERROR))
class DemoUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        install_visual_policy(cls.app)
        cls.app.setStyleSheet(construir_qss("Lima Pro"))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.now = 1800000000
        folder = Path(self.tmp.name)
        self.trial = Trial(folder, clock=lambda: self.now, monotonic=lambda: 0,
                           records=[FileRecord(folder / "trial.json")])
        self.store = DemoStore(self.trial)
        self.window = DemoWindow(self.store)
        self.addCleanup(self.window.close)
        self.window.show()
        self.settle()

    def settle(self):
        for _ in range(8):
            self.app.processEvents()

    def test_create_search_and_save_settings_by_buttons(self):
        self.window.nav[1].click()
        for key, text in dict(client="Ana", phone="9611234567", brand="Samsung", model="A54").items():
            self.window.fields[key].setText(text)
        self.window.fault.setPlainText("Pantalla dañada")
        self.window.total.setValue(500)
        with patch("offline_demo.window.QMessageBox.information"):
            self.window.save_button.click()
        self.settle()
        self.assertEqual(self.store.count(), 1)
        self.assertEqual(self.window.table.rowCount(), 1)
        self.window.search.setText("No existe")
        self.settle()
        self.assertEqual(self.window.table.rowCount(), 0)
        self.window.nav[2].click()
        self.window.workshop_fields["name"].setText("Taller Demo")
        save = next(button for button in self.window.buttons if button.text() == "Guardar Configuración")
        with patch("offline_demo.window.QMessageBox.information"):
            save.click()
        self.assertEqual(self.store.workshop()["name"], "Taller Demo")
        self.assertIn("Taller Demo", self.window.windowTitle())

    def test_expired_open_window_blocks_and_preserves_database(self):
        self.now += DURATION
        with patch("offline_demo.window.QMessageBox.warning") as warning:
            self.window.refresh_status()
            self.assertTrue(warning.called)
        self.assertTrue(self.window._blocked)
        self.assertTrue(self.window._closed)
        self.assertTrue(self.store.path.exists())
        self.assertFalse(self.window.timer.isActive())

    def test_pages_and_buttons_fit_compact_desktop(self):
        rows = []
        audit = os.environ.get("DEMO_AUDIT_DIR")
        for width, height in ((900, 600), (1358, 690), (1920, 1080)):
            self.window.resize(width, height)
            for index in range(4):
                self.window.navigate(index)
                self.settle()
                self.assertLessEqual(self.window.sidebar.width(), 280)
                for button in self.window.findChildren(QPushButton):
                    if not button.isVisible():
                        continue
                    minimum = button_content_size(button)
                    self.assertGreaterEqual(button.width(), minimum.width(), button.text())
                    self.assertGreaterEqual(button.height(), minimum.height(), button.text())
                    self.assertTrue(button.parentWidget().rect().contains(button.geometry()), button.text())
                    rows.append({"page": index, "resolution": f"{width}x{height}", "button": button.text(),
                                 "minimum": [minimum.width(), minimum.height()], "ok": True})
                if index == 0 and width >= 1358:
                    self.assertEqual(self.window.table.horizontalScrollBar().maximum(), 0)
                if audit and width == 1358:
                    folder = Path(audit)
                    folder.mkdir(parents=True, exist_ok=True)
                    self.window.grab().save(str(folder / f"demo-page-{index}.png"))
        if audit:
            (Path(audit) / "buttons.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
            unique = sorted({(row["page"], row["button"], *row["minimum"]) for row in rows})
            text = "# Botones de ABCell Pro Demo\n\nGeometría, no validación de hardware. Páginas: 0 órdenes, 1 nueva, 2 configuración, 3 límites.\n\n| Página | Botón | Mínimo ancho × alto | Resultado |\n|---|---|---|---|\n"
            for page, button, width, height in unique:
                text += f"| {page} | {button} | {width} × {height} | Sin recorte geométrico |\n"
            (Path(audit) / "BUTTON_CHECKLIST.md").write_text(text, encoding="utf-8")
        restricted = [button for button in self.window.buttons if not button.isEnabled()]
        self.assertGreaterEqual(len(restricted), 4)
        self.assertFalse(hasattr(self.window, "_imprimir_orden_sel"))
        self.assertFalse(hasattr(self.window, "_build_utilidades_android_tab"))


if __name__ == "__main__":
    unittest.main()
