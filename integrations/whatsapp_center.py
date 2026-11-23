import urllib.parse
from datetime import datetime
from database.db_manager import DatabaseManager
from config.settings import ConfigManager


class WhatsAppCenter:
    """Genera mensajes, enlaces wa.me y guarda historial de notificaciones de WhatsApp."""

    def __init__(self, db: DatabaseManager, config: ConfigManager):
        self.db = db
        self.config = config

    @staticmethod
    def normalizar_telefono(telefono: str, codigo_pais: str = "52") -> str:
        digitos = "".join(ch for ch in (telefono or "") if ch.isdigit())
        if not digitos:
            return ""
        cp = "".join(ch for ch in (codigo_pais or "52") if ch.isdigit()) or "52"
        if len(digitos) == 10:
            return f"{cp}{digitos}"
        if len(digitos) == 12 and digitos.startswith("521"):
            return "52" + digitos[3:]
        return digitos

    def construir_mensaje(self, tipo: str, orden: dict) -> str:
        negocio = self.config.get("identidad", "nombre_establecimiento", "ABCell Tizimin")
        simbolo = self.config.get("regional", "simbolo_moneda", "$")
        folio = f"#{int(orden.get('folio', 0)):04d}"
        cliente = orden.get("cliente_nombre", "Cliente")
        equipo = f"{orden.get('marca', '')} {orden.get('modelo', '')}".strip()
        total = f"{simbolo}{float(orden.get('costo_total') or 0.0):,.2f}"
        anticipo = f"{simbolo}{float(orden.get('anticipo') or 0.0):,.2f}"
        saldo = f"{simbolo}{float(orden.get('saldo') or 0.0):,.2f}"
        falla = orden.get("falla", "")

        if tipo == "recibido":
            plantilla = self.config.get(
                "whatsapp",
                "plantilla_recibido",
                "Hola {cliente}, en {negocio} recibimos tu {equipo} (Folio {folio}) por: {falla}. Total: {total}, Anticipo: {anticipo}, Saldo: {saldo}.",
            )
        elif tipo == "listo":
            plantilla = self.config.get(
                "whatsapp",
                "plantilla_listo",
                "Hola {cliente}, tu {equipo} (Folio {folio}) en {negocio} ya esta listo para entrega. Saldo pendiente: {saldo}.",
            )
        elif tipo == "recordatorio":
            plantilla = self.config.get(
                "whatsapp",
                "plantilla_recordatorio",
                "Hola {cliente}, te recordamos que tu {equipo} (Folio {folio}) esta listo en {negocio}. Saldo pendiente: {saldo}.",
            )
        else:
            plantilla = self.config.get(
                "whatsapp",
                "plantilla_custom",
                "Hola {cliente}, te escribimos de {negocio} respecto a tu {equipo} (Folio {folio}).",
            )

        return plantilla.format(
            cliente=cliente,
            negocio=negocio,
            equipo=equipo,
            folio=folio,
            falla=falla,
            total=total,
            anticipo=anticipo,
            saldo=saldo,
        )

    def generar_url_wa(self, telefono: str, mensaje: str) -> str:
        cp = self.config.get("whatsapp", "codigo_pais", "52")
        num = self.normalizar_telefono(telefono, cp)
        texto_encoded = urllib.parse.quote(mensaje or "")
        if num:
            return f"https://wa.me/{num}?text={texto_encoded}"
        return f"https://wa.me/?text={texto_encoded}"

    def registrar_notificacion(
        self,
        folio: int,
        cliente_nombre: str,
        telefono: str,
        tipo: str,
        mensaje: str,
        estado: str = "Abierto en WA",
    ):
        conn = self.db.connect()
        c = conn.cursor()
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        c.execute(
            """
            INSERT INTO notificaciones_wa (folio, cliente_nombre, telefono, tipo, mensaje, fecha, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (folio, cliente_nombre, telefono, tipo, mensaje, fecha, estado),
        )
        conn.commit()
        conn.close()

    def listar_notificaciones(self, busqueda: str = "") -> list[dict]:
        conn = self.db.connect()
        c = conn.cursor()
        like = f"%{busqueda.strip()}%"
        rows = c.execute(
            """
            SELECT * FROM notificaciones_wa
            WHERE CAST(folio AS TEXT) LIKE ? OR cliente_nombre LIKE ? OR telefono LIKE ? OR tipo LIKE ? OR mensaje LIKE ?
            ORDER BY id DESC
            """,
            (like, like, like, like, like),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
