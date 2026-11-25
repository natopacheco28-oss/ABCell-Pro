"""Prueba local de siete días. Disuasión básica, no DRM inviolable.

El reloj y el almacenamiento pertenecen al usuario: borrar ambos registros,
reinstalar el sistema o modificar el código puede eludir este control.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time
from dataclasses import dataclass

DURATION = 7 * 24 * 60 * 60
CLOCK_TOLERANCE = 300
REGISTRY_KEY = r"Software\ABCell\ABCellProDemo"
# Solo detecta ediciones casuales; esta clave NO es un secreto de seguridad.
_INTEGRITY_KEY = b"ABCell-Pro-Demo-local-record-v1"


def profile_directory() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "ABCellProDemo"


class TrialBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class TrialStatus:
    started_at: int
    expires_at: int
    remaining_seconds: int

    @property
    def days_left(self):
        return max(0, math.ceil(self.remaining_seconds / 86400))


def encode_record(data: dict) -> str:
    body = json.dumps(data, sort_keys=True, separators=(",", ":"))
    checksum = hmac.new(_INTEGRITY_KEY, body.encode(), hashlib.sha256).hexdigest()
    return json.dumps({"record": data, "integrity": checksum})


def decode_record(raw: str) -> dict:
    try:
        wrapper = json.loads(raw)
        record = wrapper["record"]
        body = json.dumps(record, sort_keys=True, separators=(",", ":"))
        checksum = hmac.new(_INTEGRITY_KEY, body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(checksum, wrapper["integrity"]):
            raise ValueError("Integridad incorrecta")
        if record["version"] != 1:
            raise ValueError("Versión incorrecta")
        for key in ("started_at", "last_seen"):
            if type(record[key]) is not int or record[key] <= 0:
                raise ValueError("Fecha incorrecta")
        if record["last_seen"] < record["started_at"]:
            raise ValueError("Fechas incoherentes")
        return record
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise TrialBlocked("El registro de la prueba es inválido. Contacta al proveedor; tus órdenes no se han borrado.") from exc


class FileRecord:
    def __init__(self, path: Path):
        self.path = path

    def read(self):
        try:
            return self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def write(self, raw):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent,
                                             delete=False, suffix=".tmp") as output:
                temp = output.name
                output.write(raw)
            os.replace(temp, self.path)
        finally:
            if temp and os.path.exists(temp):
                os.unlink(temp)


class WindowsRecord:
    """Respaldo transparente por usuario; no necesita permisos de administrador."""
    def read(self):
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY) as key:
                raw, _ = winreg.QueryValueEx(key, "TrialState")
                return raw
        except FileNotFoundError:
            return None

    def write(self, raw):
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY) as key:
            winreg.SetValueEx(key, "TrialState", 0, winreg.REG_SZ, raw)


class Trial:
    def __init__(self, directory: Path | None = None, *, clock=time.time,
                 monotonic=time.monotonic, records=None):
        self.directory = Path(directory) if directory is not None else profile_directory()
        self.clock = clock
        self.monotonic = monotonic
        self.records = records if records is not None else [FileRecord(self.directory / "trial.json")]
        if records is None and sys.platform == "win32":
            self.records.append(WindowsRecord())
        self._anchor_wall = None
        self._anchor_tick = None

    def require_active(self) -> TrialStatus:
        try:
            return self._check()
        except (OSError, UnicodeError) as exc:
            raise TrialBlocked("No se pudo leer o guardar el registro de la prueba. Revisa los permisos de tu perfil; no se borraron datos.") from exc

    def _check(self):
        now = int(self.clock())
        if now <= 0:
            raise TrialBlocked("La fecha de la PC no es válida.")
        loaded = []
        for storage in self.records:
            raw = storage.read()
            if raw is not None:
                loaded.append(decode_record(raw))
        if loaded:
            started = min(record["started_at"] for record in loaded)
            high_water = max(record["last_seen"] for record in loaded)
        else:
            # Perder el registro no debe reiniciar una demo con datos existentes.
            if (self.directory / "orders.sqlite3").exists():
                raise TrialBlocked("Falta el registro de una prueba ya iniciada. Tus órdenes siguen guardadas.")
            started = high_water = now
        if self._anchor_wall is not None:
            high_water = max(high_water, int(self._anchor_wall + self.monotonic() - self._anchor_tick))
        if now + CLOCK_TOLERANCE < high_water:
            raise TrialBlocked("Se detectó un atraso del reloj. Corrige la fecha y hora de la PC para continuar la prueba.")
        effective = max(now, high_water)
        raw = encode_record({"version": 1, "started_at": started, "last_seen": effective})
        for storage in self.records:
            storage.write(raw)
        if effective >= started + DURATION:
            raise TrialBlocked("Los 7 días de prueba han terminado. Solicita ABCell Pro completo. Tus órdenes no se han borrado.")
        if self._anchor_wall is None:
            self._anchor_wall = effective
            self._anchor_tick = self.monotonic()
        return TrialStatus(started, started + DURATION, started + DURATION - effective)
