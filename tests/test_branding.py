import ast
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from config.branding import APP_AUTHOR, APP_ID, APP_NAME, app_icon_path, app_logo_path, resource_path

ROOT = Path(__file__).resolve().parents[1]


class BrandingTests(unittest.TestCase):
    def test_user_logo_and_multiresolution_icon_exist(self):
        self.assertEqual(APP_NAME, "ABCell Pro")
        with Image.open(app_logo_path()) as logo:
            self.assertEqual(logo.size, (1024, 1024))
        with Image.open(app_icon_path()) as icon:
            self.assertEqual(icon.format, "ICO")
            sizes = {(size, size) for size in (16, 24, 32, 48, 64, 128, 256)}
            self.assertTrue(sizes <= icon.ico.sizes())
            for size in sizes:
                self.assertEqual(icon.ico.getimage(size).size, size)

    def test_resource_paths_in_development_and_frozen_modes(self):
        relative = "ui/assets/abcell-pro.ico"
        self.assertEqual(resource_path(relative), ROOT / relative)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            extraction = root / "extracted"
            executable_dir = root / "portable"
            extracted_icon = extraction / relative
            portable_icon = executable_dir / relative
            for icon in (extracted_icon, portable_icon):
                icon.parent.mkdir(parents=True)
                icon.write_bytes(b"icon")
            with patch.object(sys, "frozen", True, create=True), \
                 patch.object(sys, "_MEIPASS", str(extraction), create=True), \
                 patch.object(sys, "executable", str(executable_dir / "ABCell Pro.exe")):
                self.assertEqual(resource_path(relative), extracted_icon)
                extracted_icon.unlink()
                self.assertEqual(resource_path(relative), portable_icon.resolve())
            with patch.object(sys, "frozen", True, create=True), \
                 patch.object(sys, "executable", str(executable_dir / "ABCell Pro.exe")):
                self.assertEqual(resource_path(relative), portable_icon.resolve())

    def test_windows_identity_is_set_and_failures_are_nonfatal(self):
        import ctypes
        from unittest.mock import Mock
        try:
            from main import _establecer_identidad_windows
        except ImportError as error:
            self.skipTest(f"Qt no disponible: {error}")

        self.assertEqual(APP_ID, "ABCell.Pro.1")
        windll = Mock()
        with patch.object(sys, "platform", "win32"), \
             patch.object(ctypes, "windll", windll, create=True):
            _establecer_identidad_windows()
            windll.shell32.SetCurrentProcessExplicitAppUserModelID.assert_called_once_with(APP_ID)
            windll.shell32.SetCurrentProcessExplicitAppUserModelID.side_effect = OSError("falló")
            _establecer_identidad_windows()

    def test_dialogs_inherit_application_or_parent_icon(self):
        os.environ.setdefault("QT_QPA_PLATFORM", "windows" if sys.platform == "win32" else "offscreen")
        try:
            from PySide6.QtGui import QIcon
            from PySide6.QtWidgets import QApplication, QDialog, QInputDialog, QMainWindow, QMessageBox
            from ui.layouts import AdaptiveDialog
        except ImportError as error:
            self.skipTest(f"Qt no disponible: {error}")

        app = QApplication.instance() or QApplication([])
        previous = app.windowIcon()
        icon = QIcon(str(app_icon_path()))
        self.assertFalse(icon.isNull())
        try:
            app.setWindowIcon(icon)
            parent = QMainWindow()
            parent.setWindowIcon(icon)
            for dialog in (QDialog(parent), AdaptiveDialog(parent), QInputDialog(parent),
                           QMessageBox(parent), QDialog()):
                self.assertFalse(dialog.windowIcon().isNull())
                self.assertEqual(dialog.windowIcon().cacheKey(), icon.cacheKey())
        finally:
            app.setWindowIcon(previous)

    def test_windows_metadata_has_correct_product_and_filename(self):
        metadata = (ROOT / "config/windows_version_info.txt").read_text(encoding="utf-8")
        ast.parse(metadata)
        self.assertIn("StringStruct('ProductName', 'ABCell Pro')", metadata)
        self.assertIn("StringStruct('OriginalFilename', 'ABCell Pro.exe')", metadata)
        self.assertEqual(APP_AUTHOR, "ABCell Profecional")
        self.assertIn(f"StringStruct('CompanyName', '{APP_AUTHOR}')", metadata)
        self.assertIn(f"StringStruct('LegalCopyright', '© 2026 {APP_AUTHOR}')", metadata)

    def test_both_build_methods_use_same_icon_name_and_metadata(self):
        workflow = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
        local = (ROOT / "tools/build_windows.ps1").read_text(encoding="utf-8")
        for text in (workflow, local):
            self.assertIn('"ABCell Pro"', text)
            self.assertIn('abcell-pro.ico', text)
            self.assertIn('windows_version_info.txt', text)
            self.assertNotIn('ABCell_Gestion_Taller.exe', text)
            self.assertIn('--noconsole', text)
            self.assertIn('--onefile', text)
        self.assertIn('--add-data "ui/assets/abcell-pro.ico;ui/assets"', workflow)
        self.assertIn('"--add-data", "$icon;ui/assets"', local)


if __name__ == "__main__":
    unittest.main()
