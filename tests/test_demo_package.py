"""La demo no debe transportar funciones ni datos de la versión completa."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from tools.package_demo import stage, archive


class DemoPackageTests(unittest.TestCase):
    def test_independent_bundle_is_allowlisted_and_contains_no_production_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "demo"
            manifest = stage(target)
            self.assertTrue((target / "main.py").exists())
            for forbidden in ("services", "integrations", "database", "config", "ui/main_window.py",
                              "data", "trial.json", "orders.sqlite3"):
                self.assertFalse((target / forbidden).exists(), forbidden)
            self.assertIn("offline_demo/window.py", manifest)
            result = subprocess.run([sys.executable, "-c", "from offline_demo.trial import Trial; from offline_demo.store import DemoStore; import importlib.util; assert importlib.util.find_spec('integrations') is None"],
                                    cwd=target, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            # El ZIP usa el manifiesto, no copia cachés generados por las pruebas.
            archive(target, root / "source.zip")
            with zipfile.ZipFile(root / "source.zip") as zipped:
                self.assertFalse(any("__pycache__" in name or name.endswith(".sqlite3") for name in zipped.namelist()))
                self.assertEqual(len(zipped.namelist()), len(manifest) + 1)
            self.assertEqual(json.loads((target / "MANIFEST.json").read_text()), manifest)

    def test_refuses_to_overwrite_nonempty_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "keep.txt").write_text("keep")
            with self.assertRaises(ValueError):
                stage(root)
            self.assertEqual((root / "keep.txt").read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
