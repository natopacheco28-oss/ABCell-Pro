"""Modelo reducido: no contiene impresión, ADB, inventario, caja ni exportación."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sqlite3

from offline_demo.trial import Trial

MAX_ORDERS = 20


class DemoStore:
    def __init__(self, trial: Trial):
        self.trial = trial
        trial.require_active()  # Antes de crear el archivo, para no falsear primer inicio.
        trial.directory.mkdir(parents=True, exist_ok=True)
        self.path = trial.directory / "orders.sqlite3"
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS orders (
                folio INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL, client TEXT NOT NULL, phone TEXT NOT NULL,
                brand TEXT NOT NULL, model TEXT NOT NULL, fault TEXT NOT NULL,
                total_cents INTEGER NOT NULL CHECK(total_cents >= 0),
                status TEXT NOT NULL DEFAULT 'Recibido'
            );
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        self.connection.commit()

    def close(self):
        self.connection.close()

    def count(self):
        self.trial.require_active()
        return self.connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    def list_orders(self, query=""):
        self.trial.require_active()
        term = "%" + query.strip() + "%"
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM orders WHERE client LIKE ? OR model LIKE ? OR brand LIKE ? OR CAST(folio AS TEXT) LIKE ? ORDER BY folio DESC",
            (term, term, term, term))]

    def create_order(self, *, client, phone, brand, model, fault, total):
        self.trial.require_active()
        fields = [str(value).strip() for value in (client, phone, brand, model, fault)]
        if not all(fields):
            raise ValueError("Completa cliente, teléfono, marca, modelo y falla.")
        if any(len(value) > 2000 for value in fields):
            raise ValueError("Cada campo admite hasta 2000 caracteres.")
        try:
            amount = Decimal(str(total))
            if not amount.is_finite() or not 0 <= amount <= 999999:
                raise ValueError("Importe fuera de rango.")
            cents = int((amount * 100).quantize(Decimal("1")))
        except (InvalidOperation, OverflowError) as exc:
            raise ValueError("El importe no es válido.") from exc
        with self.connection:
            # BEGIN IMMEDIATE serializa la comprobación y alta, incluso entre conexiones.
            self.connection.execute("BEGIN IMMEDIATE")
            if self.connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] >= MAX_ORDERS:
                raise ValueError("La demo permite un máximo de 20 órdenes. Solicita la versión completa.")
            result = self.connection.execute(
                "INSERT INTO orders(created_at,client,phone,brand,model,fault,total_cents) VALUES(?,?,?,?,?,?,?)",
                (datetime.now().strftime("%d/%m/%Y %H:%M"), *fields, cents))
        return result.lastrowid

    def workshop(self):
        self.trial.require_active()
        data = {row[0]: row[1] for row in self.connection.execute("SELECT key,value FROM settings")}
        return {"name": data.get("name", "Mi taller"), "phone": data.get("phone", ""),
                "address": data.get("address", "")}

    def save_workshop(self, name, phone, address):
        self.trial.require_active()
        if not name.strip():
            raise ValueError("Escribe el nombre del taller.")
        with self.connection:
            for key, value in (("name", name), ("phone", phone), ("address", address)):
                self.connection.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value.strip()))
