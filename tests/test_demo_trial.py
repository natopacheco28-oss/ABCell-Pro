"""Demo: todas las pruebas usan reloj y almacenamiento aislados del perfil real."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from offline_demo.trial import Trial, TrialBlocked, FileRecord, DURATION, decode_record
from offline_demo.store import DemoStore, MAX_ORDERS


class MemoryRecord:
    def __init__(self):
        self.raw = None

    def read(self):
        return self.raw

    def write(self, raw):
        self.raw = raw


class DemoTrialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = 1800000000
        self.tick = 1000
        self.record = FileRecord(self.root / "trial.json")
        self.mirror = MemoryRecord()
        self.trial = self.new_trial()

    def new_trial(self):
        return Trial(self.root, clock=lambda: self.now, monotonic=lambda: self.tick,
                     records=[self.record, self.mirror])

    def advance(self, seconds):
        self.now += seconds
        self.tick += seconds

    def test_start_only_on_first_check_and_preserve_on_reopen(self):
        self.assertFalse((self.root / "trial.json").exists())
        first = self.trial.require_active()
        self.assertEqual(first.remaining_seconds, DURATION)
        self.assertEqual(first.days_left, 7)
        self.advance(3 * 86400)
        other = self.new_trial().require_active()
        self.assertEqual(other.started_at, first.started_at)
        self.assertEqual(other.days_left, 4)

    def test_expires_exactly_after_168_hours_while_closed(self):
        self.trial.require_active()
        self.advance(DURATION - 1)
        self.assertEqual(self.new_trial().require_active().remaining_seconds, 1)
        self.advance(1)
        with self.assertRaisesRegex(TrialBlocked, "terminado"):
            self.new_trial().require_active()
        self.now -= 86400
        with self.assertRaises(TrialBlocked):
            self.new_trial().require_active()

    def test_rollback_and_frozen_clock_are_blocked(self):
        self.trial.require_active()
        self.now -= 3600
        with self.assertRaisesRegex(TrialBlocked, "atraso"):
            self.trial.require_active()
        self.now += 3600
        self.tick += 600
        with self.assertRaisesRegex(TrialBlocked, "atraso"):
            self.trial.require_active()

    def test_small_clock_adjustment_does_not_extend_deadline(self):
        first = self.trial.require_active()
        self.advance(600)
        self.trial.require_active()
        self.now -= 120
        status = self.trial.require_active()
        self.assertEqual(status.expires_at, first.expires_at)
        self.assertEqual(status.remaining_seconds, DURATION - 600)

    def test_deleting_one_record_restores_without_restarting(self):
        first = self.trial.require_active()
        self.advance(86400)
        self.record.path.unlink()
        status = self.new_trial().require_active()
        self.assertEqual(status.started_at, first.started_at)
        self.assertEqual(status.days_left, 6)
        self.assertTrue(self.record.path.exists())
        self.mirror.raw = None
        self.assertEqual(self.new_trial().require_active().started_at, first.started_at)
        self.assertIsNotNone(self.mirror.raw)

    def test_corrupt_or_edited_state_fails_closed(self):
        self.trial.require_active()
        raw = json.loads(self.record.path.read_text())
        raw["record"]["started_at"] += 86400
        self.record.path.write_text(json.dumps(raw))
        with self.assertRaisesRegex(TrialBlocked, "inválido"):
            self.new_trial().require_active()

    def test_no_state_with_existing_data_does_not_start_new_trial(self):
        (self.root / "orders.sqlite3").touch()
        with self.assertRaisesRegex(TrialBlocked, "Falta el registro"):
            self.trial.require_active()

    def test_storage_failure_fails_closed(self):
        with patch.object(self.record, "write", side_effect=PermissionError("no")):
            with self.assertRaisesRegex(TrialBlocked, "permisos"):
                self.trial.require_active()

    def test_invalid_schema_is_not_silently_restarted(self):
        for raw in ('{}', 'null', '[]', '{"record":{},"integrity":"no"}'):
            with self.subTest(raw=raw), self.assertRaises(TrialBlocked):
                decode_record(raw)

    def make_store(self):
        store = DemoStore(self.trial)
        self.addCleanup(store.close)
        return store

    def add(self, store, **overrides):
        data = dict(client="Cliente", phone="9611234567", brand="Samsung", model="A54",
                    fault="Pantalla", total="100.25")
        data.update(overrides)
        return store.create_order(**data)

    def test_order_limit_is_in_model_not_only_button(self):
        store = self.make_store()
        for i in range(MAX_ORDERS):
            self.assertEqual(self.add(store), i + 1)
        with self.assertRaisesRegex(ValueError, "20 órdenes"):
            self.add(store)
        self.assertEqual(store.count(), MAX_ORDERS)
        self.assertEqual(store.list_orders()[0]["total_cents"], 10025)
        for forbidden in ("print_ticket", "export", "edit_order", "delete_order", "payment", "inventory", "adb"):
            self.assertFalse(hasattr(store, forbidden))

    def test_expiry_blocks_model_without_deleting_orders(self):
        store = self.make_store()
        self.add(store)
        self.advance(DURATION)
        for operation in (store.list_orders, lambda: self.add(store), store.workshop,
                          lambda: store.save_workshop("Nombre", "", "")):
            with self.assertRaises(TrialBlocked):
                operation()
        self.assertEqual(store.connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 1)

    def test_fields_and_amounts_validated(self):
        store = self.make_store()
        for data in ({"client": " "}, {"total": "NaN"}, {"total": "Infinity"},
                     {"total": -1}, {"total": "invalid"}, {"fault": "x" * 2001}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.add(store, **data)
        self.assertEqual(store.count(), 0)

    def test_settings_and_search_persist(self):
        store = self.make_store()
        store.save_workshop("Taller Norte", "961", "Calle Uno")
        self.assertEqual(store.workshop()["name"], "Taller Norte")
        self.add(store, client="Ana")
        self.add(store, client="Luis")
        self.assertEqual(len(store.list_orders("Ana")), 1)
        self.assertEqual(len(store.list_orders("A54")), 2)
        self.assertEqual(len(store.list_orders("missing")), 0)


if __name__ == "__main__":
    unittest.main()
