"""Audita botones reales de todas las vistas y diálogos, sin impresora ni teléfono.

QT_QPA_PLATFORM=offscreen python tools/audit_ui.py --output artifacts/ui
QT_SCALE_FACTOR=1.5 QT_QPA_PLATFORM=offscreen python tools/audit_ui.py --output artifacts/ui-150
No ejecuta acciones destructivas ni conecta dispositivos: solo construye vistas.
"""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QInputDialog, QMessageBox,
    QPushButton, QTabWidget,
)
from config.settings import ConfigManager
from database.db_manager import DatabaseManager
from integrations.ticket_image import generar_imagen_ticket
from services.workshop_service import WorkshopService
from ui.layouts import AdaptiveDialog, ReadableTable, button_content_size
from ui.main_window import MainWindow


def audit(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("ABCell — auditoría visual")
    records, failures, screenshots = {}, [], []

    def settle():
        for _ in range(6):
            app.processEvents()

    def capture(root, section, resolution, screenshot=False):
        settle()
        for table in root.findChildren(ReadableTable):
            table.fit_contents()
        settle()
        for button in root.findChildren(QPushButton):
            if not button.isVisible():
                continue
            name = button.text().replace("&", "") or button.toolTip() or button.accessibleName()
            expected = button_content_size(button)
            actual = button.size()
            parent = button.parentWidget()
            fits = actual.width() >= expected.width() and actual.height() >= expected.height()
            contained = parent is None or parent.rect().contains(button.geometry())
            passed = fits and contained
            key = (section, name)
            record = records.setdefault(key, {
                "section": section, "button": name, "minimum_height": button.minimumHeight(),
                "minimum_width": button.minimumWidth(), "tested_sizes": [], "passed": True,
            })
            record["tested_sizes"].append(f"{resolution}: {actual.width()}×{actual.height()}")
            record["passed"] = record["passed"] and passed
            if not passed:
                failures.append(f"{section} / {name} [{resolution}]: "
                                f"actual={actual.width()}x{actual.height()}, "
                                f"contenido={expected.width()}x{expected.height()}, "
                                f"dentro_del_padre={contained}")
        if screenshot:
            filename = f"{len(screenshots):02d}-{section.replace('/', '-').replace(' ', '_')}.png"
            root.grab().save(str(output / filename))
            screenshots.append(filename)

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        config = ConfigManager(str(root / "config.json"))
        config.definir_codigo_maestro("prueba-no-produccion")
        db = DatabaseManager(str(root / "test.db"))
        try:
            service = WorkshopService(db, config)
            folio = service.crear_orden({
                "cliente_nombre": "Cliente con nombre completo de prueba", "cliente_tel": "9991234567",
                "marca": "Samsung", "modelo": "Galaxy A54", "costo_total": 1250,
                "anticipo": 250, "falla": "Pantalla dañada y diagnóstico de carga pendiente. " * 3,
            })
            product_id = service.guardar_producto_inventario({
                "nombre": "Pantalla Samsung Galaxy A54 de prueba", "stock": 3, "costo_compra": 450,
            })
            window = MainWindow(db, config)
            window.show()
            settle()
            sections = ["Órdenes de trabajo", "Nueva orden", "Inventario", "Catálogo y Ubicaciones",
                        "Estadísticas y Caja", "Utilidades Android", "Configuración de taller"]
            for width, height in ((900, 600), (1366, 768), (1920, 1080)):
                window.resize(width, height)
                for index, section in enumerate(sections):
                    window.ir_a_seccion(index)
                    settle()
                    tabs = window.stack.currentWidget().findChildren(QTabWidget)
                    if tabs:
                        for tab in tabs:
                            for tab_index in range(tab.count()):
                                tab.setCurrentIndex(tab_index)
                                capture(window, f"{section}/{tab.tabText(tab_index)}", f"{width}x{height}", width == 1366)
                    else:
                        capture(window, section, f"{width}x{height}", width == 1366)
            # Los dos estados del botón de bloqueo y las acciones de filas.
            window.ir_a_seccion(2)
            window.inventario_desbloqueado = True
            window.refrescar_inventario()
            capture(window, "Inventario/edición desbloqueada", "1366x768")

            # Construir los diálogos auténticos sin entrar en bucles modales.
            def inspect_dialog(dialog):
                dialog.prepare_layout()
                dialog.show()
                settle()
                capture(dialog, "Diálogo/" + dialog.windowTitle(), "monitor disponible", True)
                dialog.reject()
                return QDialog.Rejected

            window.ir_a_seccion(0)
            window.tbl_ordenes.selectRow(0)
            image_path = str(root / "ticket.png")
            generar_imagen_ticket(service.obtener_orden(folio), config, image_path)
            with patch.object(AdaptiveDialog, "exec", inspect_dialog):
                window._editar_orden_sel()
                window._editar_servicio(service.listar_servicios()[0]["id"])
                window._editar_ubicacion(service.listar_ubicaciones()[0]["id"])
                window._dialogo_producto_inventario()
                window._dialogo_producto_inventario(service.obtener_producto_inventario(product_id))
                window._mostrar_dialogo_imagen_ticket(service.obtener_orden(folio), image_path)
                with patch.object(window, "_autorizar_con_codigo", return_value=True):
                    window._abrir_modo_maestro()

            # Botones estándar de Qt: confirmaciones, código maestro, selector de archivos.
            for buttons in (QMessageBox.Ok, QMessageBox.Yes | QMessageBox.No):
                dialog = QMessageBox(QMessageBox.Information, "Confirmación del sistema",
                                     "Mensaje descriptivo de prueba. " * 4, buttons, window)
                dialog.show()
                capture(dialog, "Diálogo/Mensajes estándar", "monitor disponible")
                dialog.close()
            dialog = QInputDialog(window)
            dialog.setWindowTitle("Código maestro")
            dialog.setLabelText("Introduce el código maestro para continuar:")
            dialog.setTextEchoMode(__import__('PySide6.QtWidgets', fromlist=['QLineEdit']).QLineEdit.Password)
            dialog.show()
            capture(dialog, "Diálogo/Código maestro", "monitor disponible")
            dialog.reject()
            dialog = QFileDialog(window, "Elegir logo")
            dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            dialog.show()
            capture(dialog, "Diálogo/Archivos Qt", "monitor disponible")
            dialog.reject()

            forbidden = {"Elegir adb.exe", "¿Cómo conectar por USB?", "Refrescar datos"}
            for button in window.findChildren(QPushButton):
                if button.text() in forbidden:
                    failures.append("Botón prohibido presente: " + button.text())
            window.close()
        finally:
            db.cerrar()

    result = {
        "platform": sys.platform, "qt_scale_factor": os.environ.get("QT_SCALE_FACTOR", "1"),
        "checks": list(records.values()), "failures": failures, "screenshots": screenshots,
        "scope": "Geometría Qt y caja de contenido de botones; no sustituye prueba física de hardware ni revisión manual en Windows.",
    }
    (output / "buttons.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Verificación de botones — ABCell", "", result["scope"], "",
             "Medidas en píxeles lógicos. Los controles fuera del viewport se alcanzan mediante scroll.", "",
             "| Pantalla / sección | Botón | Mínimo ancho × alto | Verificación geométrica |",
             "|---|---|---|---|"]
    for record in result["checks"]:
        name = record['button'].replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {record['section']} | {name} | {record['minimum_width']} × {record['minimum_height']} | "
                     f"{'Sin recorte de contenido' if record['passed'] else 'REVISAR'} |")
    lines += ["", "## Retirados", "", "- Elegir adb.exe", "- ¿Cómo conectar por USB?", "- Refrescar datos", "",
              "## Incidencias", ""] + (failures or ["Ninguna incidencia geométrica de botones en las condiciones probadas."])
    (output / "BUTTON_CHECKLIST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Botones/secciones comprobados: {len(records)}; incidencias: {len(failures)}")
    for failure in failures:
        print("ERROR:", failure)
    return len(failures) == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="artifacts/ui")
    arguments = parser.parse_args()
    raise SystemExit(0 if audit(arguments.output) else 1)
