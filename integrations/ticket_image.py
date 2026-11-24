"""Genera una imagen PNG del ticket/nota de taller para enviar por WhatsApp.

La imagen incluye los mismos datos del ticket de impresión: negocio, folio,
cliente, equipo, falla, total, anticipo, saldo, estatus, dirección y garantía.
"""

import os
import textwrap
from datetime import datetime

try:
    from config.settings import ConfigManager
except Exception:  # pragma: no cover
    class ConfigManager:  # type: ignore
        def __init__(self, *args, **kwargs):
            self.data = {}

        def get(self, seccion: str, clave: str, default=None):
            return default


try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # pragma: no cover
    Image = ImageDraw = ImageFont = None

try:
    from integrations.printer_58mm import logo_color_pil
except Exception:  # pragma: no cover
    def logo_color_pil(config=None):
        return None


ANCHO = 640
MARGEN = 36
AZUL = (2, 132, 199)
TEXTO_OSCURO = (15, 23, 42)
TEXTO_GRIS = (100, 116, 139)
LINEA = (226, 232, 240)
FONDO_CAJA = (224, 242, 254)


def _fuente(tam: int, negrita: bool = False):
    candidatos = (
        ("arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf")
        if negrita
        else ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf")
    )
    for nombre in candidatos:
        try:
            return ImageFont.truetype(nombre, tam)
        except Exception:
            pass
    try:
        return ImageFont.load_default(tam)
    except Exception:
        return ImageFont.load_default()


def _alto_texto(draw, texto: str, fuente) -> int:
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    return bbox[3] - bbox[1]


def _envolver_px(draw, texto: str, fuente, ancho_max: int) -> list[str]:
    """Envuelve el texto respetando el ancho en píxeles."""
    lineas: list[str] = []
    for parrafo in str(texto).splitlines() or [""]:
        palabras = parrafo.split()
        if not palabras:
            lineas.append("")
            continue
        actual = ""
        for palabra in palabras:
            prueba = f"{actual} {palabra}".strip()
            if draw.textlength(prueba, font=fuente) <= ancho_max or not actual:
                actual = prueba
            else:
                lineas.append(actual)
                actual = palabra
        if actual:
            lineas.append(actual)
    return lineas or [""]


def _formatear_fecha(valor) -> str:
    texto = str(valor or "").strip()
    if not texto:
        return ""
    for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto[:19], formato).strftime("%d/%m/%Y %H:%M")
        except Exception:
            continue
    return texto[:16]


def generar_imagen_ticket(orden: dict, config: ConfigManager, ruta_destino: str) -> str | None:
    """Crea el PNG del ticket en ruta_destino. Devuelve la ruta o None si falla."""
    if Image is None or ImageDraw is None:
        return None
    if not orden:
        return None

    simbolo = config.get("regional", "simbolo_moneda", "$")
    nombre_negocio = config.get("notas", "nombre_comercial") or config.get(
        "identidad", "nombre_establecimiento", "ABCell Tizimin"
    )
    direccion = config.get("notas", "direccion") or config.get("contacto", "direccion", "")
    telefono = config.get("notas", "telefono") or config.get("contacto", "telefono", "")
    garantia = config.get("notas", "politicas_garantia", "")
    agradecimiento = config.get("notas", "texto_agradecimiento", "¡Gracias por su preferencia!")

    folio = int(orden.get("folio") or 0)
    fecha_txt = _formatear_fecha(orden.get("fecha_ingreso") or orden.get("fecha"))
    estatus = str(orden.get("estatus") or "Recibido").upper()
    equipo = f"{orden.get('marca', '')} {orden.get('modelo', '')}".strip() or "Equipo"
    total = float(orden.get("costo_total") or 0.0)
    anticipo = float(orden.get("anticipo") or 0.0)
    saldo = float(orden.get("saldo") or 0.0)

    img = Image.new("RGB", (ANCHO, 2600), "white")
    draw = ImageDraw.Draw(img)
    ancho_util = ANCHO - 2 * MARGEN
    y = MARGEN

    def centrar(texto: str, fuente, color=TEXTO_OSCURO, espacio=6):
        nonlocal y
        for linea in _envolver_px(draw, texto, fuente, ancho_util):
            w = draw.textlength(linea, font=fuente)
            draw.text((MARGEN + (ancho_util - w) / 2, y), linea, font=fuente, fill=color)
            y += _alto_texto(draw, linea, fuente) + espacio

    def separador(espacio=14):
        nonlocal y
        y += espacio
        draw.line([(MARGEN, y), (ANCHO - MARGEN, y)], fill=LINEA, width=2)
        y += espacio

    def fila(etiqueta: str, valor: str):
        nonlocal y
        if valor is None or str(valor).strip() == "":
            return
        f_et = _fuente(17, negrita=True)
        f_val = _fuente(20, negrita=True)
        draw.text((MARGEN, y), etiqueta, font=f_et, fill=TEXTO_GRIS)
        y += _alto_texto(draw, etiqueta, f_et) + 2
        for linea in _envolver_px(draw, str(valor), f_val, ancho_util):
            draw.text((MARGEN, y), linea, font=f_val, fill=TEXTO_OSCURO)
            y += _alto_texto(draw, linea, f_val) + 4
        y += 6

    # --- Encabezado con logo ---
    try:
        logo = logo_color_pil(config)
    except Exception:
        logo = None
    if logo is not None:
        alto_logo = 110
        logo = logo.convert("RGBA")
        logo.thumbnail((alto_logo, alto_logo), Image.LANCZOS)
        img.paste(logo, ((ANCHO - logo.width) // 2, y), logo)
        y += alto_logo + 10

    centrar(str(nombre_negocio).upper(), _fuente(30, negrita=True), TEXTO_OSCURO, 4)
    centrar("NOTA DE TALLER", _fuente(20, negrita=True), AZUL, 4)
    separador()

    # --- Folio y estatus ---
    centrar(f"FOLIO #{folio:04d}", _fuente(38, negrita=True), AZUL, 4)
    if fecha_txt:
        centrar(f"Fecha: {fecha_txt}", _fuente(18), TEXTO_GRIS, 2)
    centrar(f"Estatus: {estatus}", _fuente(20, negrita=True), TEXTO_OSCURO, 2)
    separador()

    # --- Cliente ---
    fila("CLIENTE", orden.get("cliente_nombre", ""))
    if orden.get("cliente_tel"):
        fila("TELÉFONO", orden.get("cliente_tel"))
    separador()

    # --- Equipo ---
    fila("EQUIPO", equipo)
    if orden.get("color") and str(orden.get("color")).strip() not in ("", "N/A"):
        fila("COLOR", orden.get("color"))
    if orden.get("imei"):
        fila("IMEI / SERIE", orden.get("imei"))
    if orden.get("pin_pass"):
        fila("PIN / CONTRASEÑA", orden.get("pin_pass"))
    if orden.get("patron") and str(orden.get("patron")).strip() != "Sin patrón":
        fila("PATRÓN", orden.get("patron"))
    if orden.get("ubicacion"):
        fila("UBICACIÓN", orden.get("ubicacion"))
    if orden.get("estado_fisico"):
        fila("ESTADO FÍSICO", orden.get("estado_fisico"))
    fila("FALLA / SERVICIO", orden.get("falla", ""))
    separador()

    # --- Caja de montos ---
    caja_alto = 150
    draw.rounded_rectangle(
        [MARGEN, y, ANCHO - MARGEN, y + caja_alto], radius=14, fill=FONDO_CAJA
    )
    f_monto_et = _fuente(18, negrita=True)
    f_monto = _fuente(22, negrita=True)
    f_saldo = _fuente(28, negrita=True)
    yy = y + 16
    for etiqueta, valor, fuente in (
        ("TOTAL", f"{simbolo}{total:,.2f}", f_monto),
        ("ANTICIPO", f"{simbolo}{anticipo:,.2f}", f_monto),
        ("SALDO PENDIENTE", f"{simbolo}{saldo:,.2f}", f_saldo),
    ):
        draw.text((MARGEN + 20, yy), etiqueta, font=f_monto_et, fill=TEXTO_GRIS)
        w = draw.textlength(valor, font=fuente)
        draw.text((ANCHO - MARGEN - 20 - w, yy - 4), valor, font=fuente, fill=TEXTO_OSCURO)
        yy += 46
    y += caja_alto
    separador()

    # --- Contacto y garantía ---
    if direccion:
        centrar(str(direccion), _fuente(18), TEXTO_GRIS, 4)
    if telefono:
        centrar(f"Tel / WhatsApp: {telefono}", _fuente(18), TEXTO_GRIS, 4)
    if garantia:
        y += 6
        centrar("GARANTÍA Y CONDICIONES", _fuente(18, negrita=True), TEXTO_OSCURO, 4)
        centrar(str(garantia), _fuente(16), TEXTO_GRIS, 4)
    if agradecimiento:
        y += 6
        centrar(str(agradecimiento), _fuente(20, negrita=True), AZUL, 4)

    y += 10
    centrar(f"Folio #{folio:04d} · {nombre_negocio}", _fuente(15), TEXTO_GRIS, 2)
    y += MARGEN

    img = img.crop((0, 0, ANCHO, min(y, img.height)))
    carpeta = os.path.dirname(os.path.abspath(ruta_destino))
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    img.save(ruta_destino, "PNG")
    return ruta_destino
