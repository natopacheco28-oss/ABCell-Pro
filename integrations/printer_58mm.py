import base64
import io
import os
import struct
import textwrap
from config.settings import ConfigManager

try:
    from config.assets import LOGO_B64, LOGO_COLOR_B64
except Exception:
    LOGO_B64 = ""
    LOGO_COLOR_B64 = ""

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = ImageDraw = ImageFont = None


def logo_pil(config: ConfigManager | None = None):
    if Image is None:
        return None
    if config:
        custom = config.get("identidad", "logo_personalizado", "")
        if custom and os.path.exists(custom):
            try:
                return Image.open(custom).convert("L")
            except Exception:
                pass
    if not LOGO_B64:
        return None
    return Image.open(io.BytesIO(base64.b64decode(LOGO_B64))).convert("L")


def logo_color_pil(config: ConfigManager | None = None):
    if Image is None:
        return None
    if config:
        custom = config.get("identidad", "logo_personalizado", "")
        if custom and os.path.exists(custom):
            try:
                return Image.open(custom).convert("RGBA")
            except Exception:
                pass
    if not LOGO_COLOR_B64:
        return None
    return Image.open(io.BytesIO(base64.b64decode(LOGO_COLOR_B64))).convert("RGBA")


def _fuente(tam: int):
    for nombre in ("arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(nombre, tam)
        except Exception:
            pass
    try:
        return ImageFont.load_default(tam)
    except Exception:
        return ImageFont.load_default()


def _fuente_ajustada(texto: str, ancho_max: int, tam_ini: int, tam_min: int = 12):
    tam = tam_ini
    while tam > tam_min:
        f = _fuente(tam)
        if f.getlength(texto) <= ancho_max:
            return f
        tam -= 2
    return _fuente(tam_min)


def crear_encabezado_img(config: ConfigManager):
    if not config.get("notas", "mostrar_logo", True):
        return None
    logo = logo_pil(config)
    if logo is None:
        return None

    ancho = int(config.get("notas", "ancho_px", 384))
    logo_px = int(config.get("notas", "tam_logo_px", 128))
    nombre_comercial = config.get("notas", "nombre_comercial") or config.get(
        "identidad", "nombre_establecimiento", "ABCell Tizimin"
    )
    partes = nombre_comercial.strip().split(" ", 1)
    linea_1 = config.get("identidad", "linea_1_ticket") or partes[0]
    linea_2 = config.get("identidad", "linea_2_ticket") or (
        partes[1].upper() if len(partes) > 1 else ""
    )

    margen = 4
    img = Image.new("L", (ancho, logo_px + 2 * margen), 255)
    lg = logo.resize((logo_px, logo_px), Image.LANCZOS).point(
        lambda p: 0 if p < 200 else 255
    )
    img.paste(lg, (0, margen))

    x0 = logo_px + 10
    disponible = max(60, ancho - x0)
    d = ImageDraw.Draw(img)
    f1 = _fuente_ajustada(linea_1, disponible, 50)
    b1 = d.textbbox((0, 0), linea_1, font=f1)
    h1 = b1[3] - b1[1]

    if linea_2:
        f2 = _fuente_ajustada(linea_2, disponible, 28)
        b2 = d.textbbox((0, 0), linea_2, font=f2)
        h2, hueco = b2[3] - b2[1], 10
        y = (img.height - (h1 + hueco + h2)) // 2
        d.text((x0 - b1[0], y - b1[1]), linea_1, font=f1, fill=0)
        d.text((x0 - b2[0], y + h1 + hueco - b2[1]), linea_2, font=f2, fill=0)
    else:
        y = (img.height - h1) // 2
        d.text((x0 - b1[0], y - b1[1]), linea_1, font=f1, fill=0)
    return img


def imagen_a_escpos(img) -> bytes:
    bw = img.point(lambda p: 255 if p < 128 else 0).convert("1")
    w, h = bw.size
    ancho_bytes = (w + 7) // 8
    datos = bw.tobytes()
    salida = b""
    for y0 in range(0, h, 128):
        filas = min(128, h - y0)
        salida += b"\x1d\x76\x30\x00" + struct.pack("<HH", ancho_bytes, filas)
        salida += datos[y0 * ancho_bytes : (y0 + filas) * ancho_bytes]
    return salida


def guardar_ico(ruta: str = "logo.ico"):
    logo = logo_color_pil() or logo_pil()
    if logo is not None:
        logo.convert("RGBA").save(
            ruta,
            sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
        )


def generar_texto_ticket(
    orden: dict, config: ConfigManager, incluir_nombre: bool = True
) -> str:
    ancho = int(config.get("notas", "ancho_ticket_chars", 32))
    sep = "-" * ancho
    doble_sep = "=" * ancho
    simbolo = config.get("regional", "simbolo_moneda", "$")

    nombre_negocio = config.get("notas", "nombre_comercial") or config.get(
        "identidad", "nombre_establecimiento", "ABCell Tizimin"
    )
    direccion = config.get("notas", "direccion") or config.get("contacto", "direccion", "")
    telefono = config.get("notas", "telefono") or config.get("contacto", "telefono", "")
    extra_contacto = config.get("notas", "datos_contacto_extra", "")
    encabezado_extra = config.get("notas", "encabezado_extra", "")
    garantia = config.get("notas", "politicas_garantia", "")
    agradecimiento = config.get("notas", "texto_agradecimiento", "")
    pie_extra = config.get("notas", "pie_pagina_extra", "")

    def centrar(texto: str) -> str:
        lineas = textwrap.wrap(texto, ancho) or [""]
        return "\n".join(l.center(ancho) for l in lineas)

    def envolver(texto: str) -> str:
        return "\n".join(textwrap.wrap(texto, ancho))

    ticket = []
    if incluir_nombre:
        ticket.append(centrar(nombre_negocio.upper()))
    if direccion:
        ticket.append(centrar(direccion))
    if telefono:
        ticket.append(centrar(f"Tel/WA: {telefono}"))
    if extra_contacto:
        ticket.append(centrar(extra_contacto))
    if encabezado_extra:
        ticket.append(centrar(encabezado_extra))

    ticket.append(doble_sep)
    ticket.append(f"FOLIO: #{int(orden['folio']):04d}")
    ticket.append(f"FECHA: {orden.get('fecha', '')}")
    ticket.append(f"ESTATUS: {orden.get('estatus', 'Recibido')}")
    ticket.append(sep)
    ticket.append(f"CLIENTE: {orden.get('cliente_nombre', '')}")
    if orden.get("cliente_tel"):
        ticket.append(f"TEL: {orden.get('cliente_tel')}")
    ticket.append(sep)
    equipo = f"{orden.get('marca', '')} {orden.get('modelo', '')}".strip()
    ticket.append(f"EQUIPO: {equipo}")
    if orden.get("color") and orden.get("color") != "N/A":
        ticket.append(f"COLOR: {orden.get('color')}")
    if orden.get("imei"):
        ticket.append(f"IMEI/SERIE: {orden.get('imei')}")
    if orden.get("pin_pass"):
        ticket.append(f"PIN/PASS: {orden.get('pin_pass')}")
    if orden.get("patron") and orden.get("patron") != "Sin patrón":
        ticket.append(f"PATRON: {orden.get('patron')}")
    if orden.get("estado_fisico"):
        ticket.append("ESTADO FISICO:")
        ticket.append(envolver(str(orden.get("estado_fisico"))))
    ticket.append("FALLA / SERVICIO:")
    ticket.append(envolver(str(orden.get("falla", ""))))
    ticket.append(sep)

    total = float(orden.get("costo_total") or 0.0)
    anticipo = float(orden.get("anticipo") or 0.0)
    saldo = float(orden.get("saldo") or 0.0)

    ticket.append(f"TOTAL:    {simbolo}{total:,.2f}")
    ticket.append(f"ANTICIPO: {simbolo}{anticipo:,.2f}")
    ticket.append(f"SALDO:    {simbolo}{saldo:,.2f}")
    ticket.append(doble_sep)

    if garantia:
        ticket.append(centrar("GARANTIA Y CONDICIONES"))
        ticket.append(envolver(garantia))
        ticket.append(sep)
    if agradecimiento:
        ticket.append(centrar(agradecimiento))
    if pie_extra:
        ticket.append(centrar(pie_extra))

    ticket.append("\n\n")
    return "\n".join(ticket)


def imprimir_ticket_58mm(orden: dict, config: ConfigManager) -> tuple[bool, str]:
    nombre_impresora = config.get("notas", "impresora", "")
    texto = generar_texto_ticket(
        orden, config, incluir_nombre=not config.get("notas", "mostrar_logo", True)
    )

    try:
        import win32print

        if not nombre_impresora:
            nombre_impresora = win32print.GetDefaultPrinter()
        if not nombre_impresora:
            return False, "No hay impresora predeterminada configurada en Windows."

        hprinter = win32print.OpenPrinter(nombre_impresora)
        try:
            win32print.StartDocPrinter(hprinter, 1, ("Ticket ABCell", None, "RAW"))
            try:
                win32print.StartPagePrinter(hprinter)
                enc = crear_encabezado_img(config)
                if enc is not None:
                    win32print.WritePrinter(hprinter, imagen_a_escpos(enc))
                win32print.WritePrinter(hprinter, texto.encode("cp437", errors="replace"))
                if config.get("notas", "cortar_papel", True):
                    win32print.WritePrinter(hprinter, b"\x1d\x56\x42\x00")
                win32print.EndPagePrinter(hprinter)
            finally:
                win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)
        return True, f"Ticket enviado a {nombre_impresora}."
    except Exception as exc:
        return (
            False,
            f"No se pudo imprimir directo ({exc}). Puedes copiar o exportar el ticket.",
        )
