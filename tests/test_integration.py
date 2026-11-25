"""Pruebas de regresión de las funciones recuperadas, sin GUI ni hardware."""
import tempfile
import unittest
from pathlib import Path

from config.settings import ConfigManager
from database.db_manager import DatabaseManager
from services.workshop_service import WorkshopService
from ui.theme import GestorTemas


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = ConfigManager(str(self.root / "config.json"))
        self.db = DatabaseManager(str(self.root / "test.db"))
        self.addCleanup(self.db.cerrar)
        self.service = WorkshopService(self.db, self.config)

    def create_order(self):
        return self.service.crear_orden({
            "cliente_nombre": "Cliente de prueba", "cliente_tel": "9991234567",
            "marca": "Samsung", "modelo": "A54", "falla": "Pantalla rota",
            "costo_total": 1000, "anticipo": 200,
        })

    def test_edit_order_preserves_payments(self):
        folio = self.create_order()
        self.service.registrar_pago(folio, 100)
        self.assertTrue(self.service.actualizar_orden_datos(
            folio, {"modelo": "A55", "costo_total": 1200}))
        order = self.service.obtener_orden(folio)
        self.assertEqual(order["modelo"], "A55")
        self.assertEqual(order["anticipo"], 300)
        self.assertEqual(order["saldo"], 900)
        payments = self.db.consultar_uno(
            "SELECT SUM(monto) AS total FROM pagos_orden WHERE folio = ?", (folio,))
        self.assertEqual(payments["total"], 300)

    def test_inventory_crud_and_stock(self):
        product_id = self.service.guardar_producto_inventario({
            "nombre": "Pantalla A54", "stock": 3, "costo_compra": 100,
            "precio_venta": 200,
        })
        self.assertTrue(self.service.actualizar_producto_inventario(
            product_id, {"nombre": "Pantalla Samsung A54"}))
        self.assertEqual(self.service.ajustar_stock_inventario(product_id, -1)["stock"], 2)
        summary = self.service.obtener_resumen_inventario()
        self.assertEqual(summary["total_unidades"], 2)
        self.assertEqual(summary["valor_costo"], 200)
        self.assertTrue(self.service.eliminar_producto_inventario(product_id))
        self.assertIsNone(self.service.obtener_producto_inventario(product_id))

    def test_catalog_and_locations_edit_delete(self):
        service_id = self.service.guardar_servicio({"nombre": "Servicio prueba", "precio": 150})
        self.assertTrue(self.service.actualizar_servicio(
            service_id, {"nombre": "Servicio editado", "precio": 200}))
        self.assertTrue(self.service.eliminar_servicio(service_id))
        self.service.guardar_ubicacion("Estante prueba")
        location = next(row for row in self.service.listar_ubicaciones()
                        if row["nombre"] == "Estante prueba")
        self.assertTrue(self.service.actualizar_ubicacion(location["id"], "Estante editado"))
        self.assertTrue(self.service.eliminar_ubicacion(location["id"]))

    def test_database_reinitialization_preserves_order(self):
        folio = self.create_order()
        self.db.init_db()
        self.db.init_db()
        self.assertEqual(self.service.obtener_orden(folio)["cliente_nombre"], "Cliente de prueba")
        self.assertEqual(len(self.service.listar_ordenes()), 1)
        self.assertEqual(self.db.consultar_uno("PRAGMA integrity_check")["integrity_check"], "ok")

    def test_six_themes_generate_and_persist(self):
        manager = GestorTemas(self.config)
        self.assertEqual(len(manager.lista()), 6)
        for theme in manager.lista():
            self.assertIn("QMainWindow", manager.qss(theme))
            manager.seleccionar(theme)
            self.assertEqual(manager.actual(), theme)
        loaded = ConfigManager(self.config.config_path)
        self.assertEqual(GestorTemas(loaded).actual(), manager.actual())


if __name__ == "__main__":
    unittest.main()
