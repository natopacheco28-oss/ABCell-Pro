import hashlib
import hmac
import json
import os
import copy
import io
import tempfile
from pathlib import Path


DEFAULT_CONFIG = {
    "identidad": {
        "nombre_establecimiento": "ABCell Tizimin",
        "linea_1_ticket": "ABCell",
        "linea_2_ticket": "TIZIMIN",
        "logo_personalizado": "",
    },
    "contacto": {
        "telefono": "",
        "direccion": "",
    },
    "regional": {
        "simbolo_moneda": "$",
        "formato_fecha": "%d/%m/%Y",
        "formato_hora": "%H:%M",
    },
    "notas": {
        "nombre_comercial": "ABCell Tizimin",
        "direccion": "",
        "telefono": "",
        "datos_contacto_extra": "",
        "encabezado_extra": "",
        "politicas_garantia": "",
        "texto_agradecimiento": "¡Gracias por su preferencia!",
        "pie_pagina_extra": "",
        "ancho_ticket_chars": 32,
        "ancho_px": 384,
        "tam_logo_px": 128,
        "mostrar_logo": True,
        "cortar_papel": True,
    },
    "whatsapp": {
        "codigo_pais": "52",
        "plantilla_recibido": (
            "Hola {cliente}, en {negocio} recibimos tu {equipo} (Folio {folio}) "
            "por: {falla}. Total: {total}, Anticipo: {anticipo}, Saldo: {saldo}."
        ),
        "plantilla_listo": (
            "Hola {cliente}, tu {equipo} (Folio {folio}) en {negocio} ya esta "
            "listo para entrega. Saldo pendiente: {saldo}."
        ),
        "plantilla_recordatorio": (
            "Hola {cliente}, te recordamos que tu {equipo} (Folio {folio}) esta "
            "listo en {negocio}. Saldo pendiente: {saldo}."
        ),
        "plantilla_custom": (
            "Hola {cliente}, te escribimos de {negocio} respecto a tu {equipo} (Folio {folio})."
        ),
    },
    "apariencia": {
        "tema": "Lima Pro",
    },
    "seguridad": {
        "salt": "",
        "hash": "",
    },
    "android": {
        "ruta_adb": "",
    },
}


class ConfigManager:
    """Maneja la configuración persistente en JSON con valores por defecto."""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.data: dict = json.loads(json.dumps(DEFAULT_CONFIG))
        self.load()

    def load(self):
        if not self.config_path or not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                cargado = json.load(f)
            if isinstance(cargado, dict):
                for seccion, valores in cargado.items():
                    if isinstance(valores, dict):
                        self.data.setdefault(seccion, {}).update(valores)
                    else:
                        self.data[seccion] = valores
        except Exception:
            pass

    def save(self):
        if not self.config_path:
            return
        carpeta = os.path.dirname(os.path.abspath(self.config_path))
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        # No dejar un JSON truncado si falla la escritura o se interrumpe.
        temporal = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=carpeta,
                                             suffix=".tmp", delete=False) as f:
                temporal = f.name
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(temporal, self.config_path)
        finally:
            if temporal and os.path.exists(temporal):
                os.unlink(temporal)

    def ruta_logo_personalizado(self) -> str:
        """Soporta rutas absolutas antiguas y logos portables junto al JSON."""
        ruta = str(self.get("identidad", "logo_personalizado", "") or "").strip()
        if not ruta:
            return ""
        path = Path(ruta).expanduser()
        if not path.is_absolute():
            path = Path(self.config_path).resolve().parent / path
        return str(path)

    def guardar_datos_taller(self, nombre: str, telefono: str, direccion: str,
                            logo: str, garantia: str):
        """Una sola actualización para identidad, contacto y todas las notas.

        El logo se valida y se convierte a PNG en data/logos; su ruta relativa
        permite trasladar la carpeta de datos con el ejecutable.
        """
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("Escribe el nombre del taller.")
        logo = logo.strip()
        ruta_guardada = ""
        if logo:
            from PIL import Image, ImageOps, UnidentifiedImageError
            source = Path(logo).expanduser()
            if not source.is_absolute():
                source = Path(self.config_path).resolve().parent / source
            try:
                with Image.open(source) as original:
                    image = ImageOps.exif_transpose(original).convert("RGBA")
                    image.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
            except (OSError, ValueError, UnidentifiedImageError) as exc:
                raise ValueError("No se pudo leer el logo. Elige una imagen válida y accesible.") from exc
            contenido = buffer.getvalue()
            filename = "logo-" + hashlib.sha256(contenido).hexdigest() + ".png"
            carpeta = Path(self.config_path).resolve().parent / "logos"
            carpeta.mkdir(parents=True, exist_ok=True)
            destino = carpeta / filename
            if not destino.exists():
                destino.write_bytes(contenido)
            ruta_guardada = "logos/" + filename

        anterior = copy.deepcopy(self.data)
        try:
            self.set("identidad", "nombre_establecimiento", nombre)
            self.set("notas", "nombre_comercial", nombre)
            # Retirar las líneas heredadas ABCell/TIZIMIN del encabezado.
            partes = nombre.split(maxsplit=1)
            self.set("identidad", "linea_1_ticket", partes[0])
            self.set("identidad", "linea_2_ticket", partes[1] if len(partes) > 1 else "")
            for clave, valor in (("telefono", telefono), ("direccion", direccion)):
                self.set("contacto", clave, valor.strip())
                self.set("notas", clave, valor.strip())
            self.set("identidad", "logo_personalizado", ruta_guardada)
            self.set("notas", "mostrar_logo", bool(ruta_guardada))
            self.set("notas", "politicas_garantia", garantia.strip())
            self.save()
        except Exception:
            self.data = anterior
            raise

    def get(self, seccion: str, clave: str, default=None):
        sec = self.data.get(seccion)
        if isinstance(sec, dict) and clave in sec:
            return sec[clave]
        return default

    def set(self, seccion: str, clave: str, valor):
        self.data.setdefault(seccion, {})[clave] = valor

    # --- Código maestro (solo se guarda un hash, nunca el texto) ---
    @staticmethod
    def _hash_codigo(codigo: str, salt_hex: str) -> str:
        clave = hashlib.pbkdf2_hmac(
            "sha256", codigo.encode("utf-8"), bytes.fromhex(salt_hex), 120000
        )
        return clave.hex()

    def tiene_codigo_maestro(self) -> bool:
        return bool(self.get("seguridad", "hash", "")) and bool(
            self.get("seguridad", "salt", "")
        )

    def definir_codigo_maestro(self, codigo: str):
        salt = os.urandom(16).hex()
        self.set("seguridad", "salt", salt)
        self.set("seguridad", "hash", self._hash_codigo(codigo, salt))

    def verificar_codigo_maestro(self, codigo: str) -> bool:
        if not self.tiene_codigo_maestro():
            return False
        try:
            salt = self.get("seguridad", "salt", "")
            esperado = self.get("seguridad", "hash", "")
            return hmac.compare_digest(self._hash_codigo(codigo, salt), esperado)
        except Exception:
            return False
