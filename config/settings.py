import hashlib
import hmac
import json
import os


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
        "tema": "Claro",
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
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

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
