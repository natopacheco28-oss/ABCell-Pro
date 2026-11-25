import ast
import unittest
from pathlib import Path
from PIL import Image
from config.branding import APP_NAME, app_icon_path, app_logo_path

ROOT = Path(__file__).resolve().parents[1]


class BrandingTests(unittest.TestCase):
    def test_user_logo_and_multiresolution_icon_exist(self):
        self.assertEqual(APP_NAME, "ABCell Pro")
        with Image.open(app_logo_path()) as logo:
            self.assertEqual(logo.size, (1024, 1024))
        with Image.open(app_icon_path()) as icon:
            self.assertEqual(icon.format, "ICO")
            self.assertTrue({(16, 16), (32, 32), (48, 48), (256, 256)} <= icon.ico.sizes())

    def test_windows_metadata_has_correct_product_and_filename(self):
        metadata = (ROOT / "config/windows_version_info.txt").read_text(encoding="utf-8")
        ast.parse(metadata)
        self.assertIn("StringStruct('ProductName', 'ABCell Pro')", metadata)
        self.assertIn("StringStruct('OriginalFilename', 'ABCell Pro.exe')", metadata)

    def test_both_build_methods_use_same_icon_name_and_metadata(self):
        workflow = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
        local = (ROOT / "tools/build_windows.ps1").read_text(encoding="utf-8")
        for text in (workflow, local):
            self.assertIn('"ABCell Pro"', text)
            self.assertIn('abcell-pro.ico', text)
            self.assertIn('windows_version_info.txt', text)
            self.assertNotIn('ABCell_Gestion_Taller.exe', text)


if __name__ == "__main__":
    unittest.main()
