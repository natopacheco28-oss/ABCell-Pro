"""Configuración real y notas, sin impresora física ni datos de producción."""
import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image, ImageDraw
from config.settings import ConfigManager
from integrations import printer_58mm as printer
from integrations.ticket_image import generar_imagen_ticket, ANCHO, MARGEN


ORDER = {"folio": 1, "cliente_nombre": "Cliente", "marca": "Samsung", "modelo": "A54",
         "falla": "Pantalla", "costo_total": 500, "anticipo": 100, "saldo": 400}


class WorkshopSettingsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = ConfigManager(str(self.root / "data" / "config.json"))

    def save_workshop(self, name="Taller Norte", color="red", phone="9611111111", address="Calle Uno 123"):
        source = self.root / "logo.png"
        Image.new("RGBA", (120, 60), color).save(source)
        self.config.guardar_datos_taller(name, phone, address, str(source), "Garantía vigente")
        return source

    def test_repeated_edits_update_thermal_digital_and_reloaded_settings(self):
        for name, color, phone, address in (
            ("Taller Norte", "red", "9611111111", "Calle Uno 123"),
            ("Servicio Sur", "blue", "9612222222", "Avenida Dos 456"),
        ):
            with self.subTest(workshop=name):
                source = self.save_workshop(name, color, phone, address)
                source.unlink()  # Ya no depende de Descargas ni del archivo original.
                loaded = ConfigManager(self.config.config_path)
                text = printer.generar_texto_ticket(ORDER, loaded)
                for value in (name.upper(), phone, address, "Garantía vigente"):
                    self.assertIn(value, text)
                self.assertNotIn("ABCell", text)
                self.assertEqual(loaded.get("identidad", "nombre_establecimiento"), name)
                self.assertEqual(loaded.get("contacto", "telefono"), phone)
                self.assertFalse(Path(loaded.get("identidad", "logo_personalizado")).is_absolute())
                self.assertEqual(printer.logo_color_pil(loaded).getpixel((0, 0)),
                                 (255, 0, 0, 255) if color == "red" else (0, 0, 255, 255))
                drawn = []
                original_text = ImageDraw.ImageDraw.text

                def record(draw, xy, text, *args, **kwargs):
                    drawn.append(str(text))
                    return original_text(draw, xy, text, *args, **kwargs)

                with patch.object(ImageDraw.ImageDraw, "text", new=record):
                    header = printer.crear_encabezado_img(loaded)
                    self.assertIsNotNone(header)
                    self.assertIn(name.split()[0], drawn)
                    self.assertIn(name.split()[1], drawn)
                    self.assertNotIn("TIZIMIN", drawn)
                    self.assertEqual(generar_imagen_ticket(ORDER, loaded, str(self.root / "note.png")),
                                     str(self.root / "note.png"))
                all_drawn = "\n".join(drawn)
                for value in (name.upper(), phone, address):
                    self.assertIn(value, all_drawn)
                with Image.open(self.root / "note.png") as image:
                    self.assertEqual(image.getpixel((ANCHO // 2, MARGEN + 20)),
                                     (255, 0, 0) if color == "red" else (0, 0, 255))

    def test_logo_is_portable_with_data_folder(self):
        self.save_workshop()
        moved = self.root / "moved"
        shutil.copytree(self.root / "data", moved)
        shutil.rmtree(self.root / "data")
        loaded = ConfigManager(str(moved / "config.json"))
        self.assertIsNotNone(printer.logo_pil(loaded))
        self.assertTrue(Path(loaded.ruta_logo_personalizado()).is_file())

    def test_missing_or_invalid_logo_and_blank_name_do_not_replace_saved_settings(self):
        self.save_workshop()
        old = copy.deepcopy(self.config.data)
        saved = Path(self.config.config_path).read_bytes()
        invalid = self.root / "invalid.png"
        invalid.write_text("not an image")
        for name, logo in (("", ""), ("Otro", str(invalid)), ("Otro", str(self.root / "missing.png"))):
            with self.assertRaises(ValueError):
                self.config.guardar_datos_taller(name, "", "", logo, "")
            self.assertEqual(self.config.data, old)
            self.assertEqual(Path(self.config.config_path).read_bytes(), saved)

    def test_write_failure_preserves_in_memory_and_disk_settings(self):
        self.save_workshop()
        old = copy.deepcopy(self.config.data)
        saved = Path(self.config.config_path).read_bytes()
        with patch("config.settings.os.replace", side_effect=PermissionError("Sin permiso")):
            with self.assertRaises(PermissionError):
                self.config.guardar_datos_taller("Otro", "", "", "", "")
        self.assertEqual(self.config.data, old)
        self.assertEqual(Path(self.config.config_path).read_bytes(), saved)
        self.assertEqual(list(Path(self.config.config_path).parent.glob("*.tmp")), [])

    def test_clear_contact_and_logo_does_not_reuse_old_branding(self):
        self.save_workshop()
        self.config.guardar_datos_taller("Otro taller", "", "", "", "")
        loaded = ConfigManager(self.config.config_path)
        text = printer.generar_texto_ticket(ORDER, loaded)
        self.assertIn("OTRO TALLER", text)
        self.assertNotIn("Calle Uno", text)
        self.assertNotIn("9611111111", text)
        self.assertIsNone(printer.logo_pil(loaded))
        self.assertIsNone(printer.logo_color_pil(loaded))
        self.assertIsNone(printer.crear_encabezado_img(loaded))

    def test_print_jobs_read_latest_settings_and_logo_each_time(self):
        device = MagicMock()
        device.GetDefaultPrinter.return_value = "POS-58"
        device.GetPrinter.return_value = {}
        with patch.dict(sys.modules, {"win32print": device}):
            for name, color in (("Taller Norte", "red"), ("Servicio Sur", "blue")):
                self.save_workshop(name, color)
                device.WritePrinter.reset_mock()
                ok, message = printer.imprimir_ticket_58mm(ORDER, self.config)
                self.assertTrue(ok, message)
                sent = b"".join(c.args[1] for c in device.WritePrinter.call_args_list)
                self.assertIn(b"Calle Uno 123", sent)
                self.assertIn(b"9611111111", sent)
                self.assertIn(b"\x1d\x76\x30\x00", sent)  # Logo/encabezado ESC/POS.
                ok, message = printer.imprimir_ticket_prueba(self.config)
                self.assertTrue(ok, message)
                sent = b"".join(c.args[1] for c in device.WritePrinter.call_args_list)
                self.assertIn(name.upper().encode(), sent)


if __name__ == "__main__":
    unittest.main()
