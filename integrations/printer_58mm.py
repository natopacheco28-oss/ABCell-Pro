import base64
import io
import os
import re
import struct
import textwrap

try:
    from config.settings import ConfigManager
except Exception:
    class ConfigManager:  # type: ignore
        def __init__(self, *args, **kwargs):
            self.data = {}

        def get(self, seccion: str, clave: str, default=None):
            return default


try:
    from config.assets import LOGO_B64, LOGO_COLOR_B64
except Exception:
    LOGO_B64 = ""
    LOGO_COLOR_B64 = ""

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = ImageDraw = ImageFont = None

_RE_80MM = re.compile(
    r"(^|[^0-9])(80\s*mm|pos[-\s_]*80|xp[-\s_]*80|rp[-\s_]*80|tp[-\s_]*80|"
    r"ec[-\s_]*pm[-\s_]*80|atp[-\s_]*80|tm[-\s_]*t88|tm[-\s_]*t82|"
    r"tm[-\s_]*m30|srp[-\s_]*3[35]0|tsp\s*1[04]|ct[-\s_]*s310|72\s*mm|80c\b)",
    re.IGNORECASE,
)

_RE_58MM = re.compile(
    r"(^|[^0-9])(58\s*mm|pos[-\s_]*58|xp[-\s_]*58|rp[-\s_]*58|tp[-\s_]*58|"
    r"ec[-\s_]*pm[-\s_]*58|pt[-\s_]*210|tm[-\s_]*t20|mtp[-\s_]*(ii|2|3)|"
    r"goojprt|48\s*mm|58c\b)",
    re.IGNORECASE,
)

PARAMETROS_PAPEL = {
    "58mm": {"ancho_chars": 32, "ancho_px": 384, "logo_px": 128},
    "80mm": {"ancho_chars": 44, "ancho_px": 512, "logo_px": 148},
}


def clasificar_formato_papel(
    nombre_impresora: str = "",
    nombre_driver: str = "",
    nombre_papel: str = "",
    ancho_decimas_mm: int = 0,
) -> str:
    """Determina si una impresora térmica corresponde a formato 80mm o 58mm."""
    texto = f"{nombre_impresora} {nombre_driver} {nombre_papel}".strip()
    if _RE_80MM.search(texto):
        return "80mm"
    if _RE_58MM.search(texto):
        return "58mm"

    # PaperWidth en DEVMODE de Windows viene en décimas de milímetro (ej. 800 = 80.0 mm)
    if 650 <= int(ancho_decimas_mm or 0) <= 950:
        return "80mm"
    if 380 <= int(ancho_decimas_mm or 0) < 650:
        return "58mm"

    return "58mm"


def _detectar_formato_en_handle(win32print_mod, hprinter, nombre_impresora: str) -> str:
    driver_name = ""
    form_name = ""
    paper_width = 0
    try:
        info2 = win32print_mod.GetPrinter(hprinter, 2)
        if isinstance(info2, dict):
            driver_name = str(info2.get("pDriverName") or "")
            devmode = info2.get("pDevMode")
            if devmode is not None:
                form_name = str(getattr(devmode, "FormName", "") or "")
                paper_width = int(getattr(devmode, "PaperWidth", 0) or 0)
    except Exception:
        pass
    return clasificar_formato_papel(nombre_impresora, driver_name, form_name, paper_width)


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


def crear_encabezado_img(
    config: ConfigManager,
    ancho_px: int | None = None,
    logo_px: int | None = None,
):
    if not config.get("notas", "mostrar_logo", True):
        return None
    logo = logo_pil(config)
    if logo is None:
        return None

    ancho = int(ancho_px or config.get("notas", "ancho_px", 384))
    tam_logo = int(logo_px or config.get("notas", "tam_logo_px", 128))
    nombre_comercial = config.get("notas", "nombre_comercial") or config.get(
        "identidad", "nombre_establecimiento", "ABCell Tizimin"
    )
    partes = nombre_comercial.strip().split(" ", 1)
    linea_1 = config.get("identidad", "linea_1_ticket") or partes[0]
    linea_2 = config.get("identidad", "linea_2_ticket") or (
        partes[1].upper() if len(partes) > 1 else ""
    )

    margen = 4
    img = Image.new("L", (ancho, tam_logo + 2 * margen), 255)
    lg = logo.resize((tam_logo, tam_logo), Image.LANCZOS).point(
        lambda p: 0 if p < 200 else 255
    )
    img.paste(lg, (0, margen))

    x0 = tam_logo + 12
    disponible = max(60, ancho - x0)
    d = ImageDraw.Draw(img)
    tam_max_1 = 56 if ancho >= 500 else 50
    tam_max_2 = 32 if ancho >= 500 else 28
    f1 = _fuente_ajustada(linea_1, disponible, tam_max_1)
    b1 = d.textbbox((0, 0), linea_1, font=f1)
    h1 = b1[3] - b1[1]

    if linea_2:
        f2 = _fuente_ajustada(linea_2, disponible, tam_max_2)
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
    if Image is None:
        return
    logo = logo_color_pil() or logo_pil()
    if logo is not None:
        logo.convert("RGBA").save(
            ruta,
            sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
        )
        return
    fallback = Image.new("RGBA", (256, 256), (15, 23, 42, 255))
    if ImageDraw is not None:
        d = ImageDraw.Draw(fallback)
        d.rounded_rectangle(
            (24, 24, 232, 232), radius=36, fill=(37, 99, 235, 255)
        )
    fallback.save(
        ruta,
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


def generar_texto_ticket(
    orden: dict,
    config: ConfigManager,
    incluir_nombre: bool = True,
    ancho_chars: int | None = None,
) -> str:
    ancho = int(ancho_chars or config.get("notas", "ancho_ticket_chars", 32))
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
        salida = []
        for linea in str(texto).splitlines() or [""]:
            salida.extend(textwrap.wrap(linea, ancho) or [""])
        return "\n".join(salida)

    def fila_importe(etiqueta: str, monto: float) -> str:
        valor = f"{simbolo}{monto:,.2f}"
        espacio = ancho - len(etiqueta) - len(valor)
        if espacio >= 1:
            return f"{etiqueta}{' ' * espacio}{valor}"
        return f"{etiqueta} {valor}"

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
    fecha_txt = orden.get("fecha") or str(orden.get("fecha_ingreso") or "")[:16]
    ticket.append(f"FECHA: {fecha_txt}")
    ticket.append(f"ESTATUS: {orden.get('estatus', 'Recibido')}")
    ticket.append(sep)
    ticket.append(envolver(f"CLIENTE: {orden.get('cliente_nombre', '')}"))
    if orden.get("cliente_tel"):
        ticket.append(f"TEL: {orden.get('cliente_tel')}")
    ticket.append(sep)
    equipo = f"{orden.get('marca', '')} {orden.get('modelo', '')}".strip()
    ticket.append(envolver(f"EQUIPO: {equipo}"))
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

    ticket.append(fila_importe("TOTAL:", total))
    ticket.append(fila_importe("ANTICIPO:", anticipo))
    ticket.append(fila_importe("SALDO:", saldo))
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


def obtener_estado_impresora() -> dict:
    """Detecta la impresora predeterminada de Windows y su formato (58mm/80mm)."""
    try:
        import win32print
    except Exception:
        return {
            "ok": False,
            "nombre": "",
            "formato": "",
            "mensaje": "La detección de impresora solo funciona en Windows.",
        }
    try:
        nombre_impresora = str(win32print.GetDefaultPrinter() or "").strip()
        if not nombre_impresora:
            return {
                "ok": False,
                "nombre": "",
                "formato": "",
                "mensaje": "No hay una impresora predeterminada configurada en Windows.",
            }
        hprinter = win32print.OpenPrinter(nombre_impresora)
        try:
            formato = _detectar_formato_en_handle(win32print, hprinter, nombre_impresora)
        finally:
            win32print.ClosePrinter(hprinter)
        return {
            "ok": True,
            "nombre": nombre_impresora,
            "formato": formato,
            "mensaje": f"Impresora predeterminada: {nombre_impresora} (formato {formato}).",
        }
    except Exception as exc:
        return {
            "ok": False,
            "nombre": "",
            "formato": "",
            "mensaje": f"No se pudo detectar la impresora predeterminada: {exc}",
        }


def imprimir_ticket_prueba(config: ConfigManager) -> tuple[bool, str]:
    """Imprime una nota de prueba para verificar la impresora detectada (58mm u 80mm)."""
    try:
        import win32print

        nombre_impresora = str(win32print.GetDefaultPrinter() or "").strip()
        if not nombre_impresora:
            return False, "No hay una impresora predeterminada configurada en Windows."

        hprinter = win32print.OpenPrinter(nombre_impresora)
        try:
            formato = _detectar_formato_en_handle(win32print, hprinter, nombre_impresora)
            params = PARAMETROS_PAPEL[formato]
            ancho = params["ancho_chars"]
            nombre_negocio = config.get("notas", "nombre_comercial") or config.get(
                "identidad", "nombre_establecimiento", "ABCell"
            )
            lineas = [
                nombre_negocio.upper().center(ancho),
                "PRUEBA DE IMPRESION".center(ancho),
                "=" * ancho,
                f"Formato detectado: {formato}".center(ancho),
                "Si ves esta nota, la impresora responde bien.".center(ancho),
                "=" * ancho,
                "\n\n",
            ]
            win32print.StartDocPrinter(hprinter, 1, ("Prueba ABCell", None, "RAW"))
            try:
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, b"\x1b\x40")
                enc = crear_encabezado_img(
                    config,
                    ancho_px=params["ancho_px"],
                    logo_px=params["logo_px"],
                )
                if enc is not None:
                    win32print.WritePrinter(hprinter, b"\x1b\x61\x01")
                    win32print.WritePrinter(hprinter, imagen_a_escpos(enc))
                    win32print.WritePrinter(hprinter, b"\x1b\x61\x00")
                win32print.WritePrinter(
                    hprinter, "\n".join(lineas).encode("cp437", errors="replace")
                )
                if config.get("notas", "cortar_papel", True):
                    win32print.WritePrinter(hprinter, b"\x1d\x56\x42\x00")
                win32print.EndPagePrinter(hprinter)
            finally:
                win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)
        return True, f"Prueba enviada a {nombre_impresora} (formato {formato})."
    except Exception as exc:
        return (
            False,
            f"No se pudo imprimir la prueba ({exc}). Verifica la impresora predeterminada de Windows.",
        )


def imprimir_ticket_58mm(orden: dict, config: ConfigManager) -> tuple[bool, str]:
    """Imprime automáticamente en la impresora predeterminada de Windows (58mm u 80mm)."""
    try:
        import win32print

        nombre_impresora = str(win32print.GetDefaultPrinter() or "").strip()
        if not nombre_impresora:
            return False, "No hay una impresora predeterminada configurada en Windows."

        hprinter = win32print.OpenPrinter(nombre_impresora)
        try:
            formato = _detectar_formato_en_handle(win32print, hprinter, nombre_impresora)
            params = PARAMETROS_PAPEL[formato]
            enc = crear_encabezado_img(
                config,
                ancho_px=params["ancho_px"],
                logo_px=params["logo_px"],
            )
            # Si no hay logo gráfico, el nombre del negocio va dentro del texto.
            texto = generar_texto_ticket(
                orden,
                config,
                incluir_nombre=enc is None,
                ancho_chars=params["ancho_chars"],
            )

            win32print.StartDocPrinter(hprinter, 1, ("Ticket ABCell", None, "RAW"))
            try:
                win32print.StartPagePrinter(hprinter)
                # Inicializa impresora ESC/POS
                win32print.WritePrinter(hprinter, b"\x1b\x40")
                if enc is not None:
                    # Centra el encabezado gráfico tanto en rollos de 58mm como de 80mm
                    win32print.WritePrinter(hprinter, b"\x1b\x61\x01")
                    win32print.WritePrinter(hprinter, imagen_a_escpos(enc))
                    win32print.WritePrinter(hprinter, b"\x1b\x61\x00")
                win32print.WritePrinter(hprinter, texto.encode("cp437", errors="replace"))
                if config.get("notas", "cortar_papel", True):
                    win32print.WritePrinter(hprinter, b"\x1d\x56\x42\x00")
                win32print.EndPagePrinter(hprinter)
            finally:
                win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)
        return True, f"Ticket enviado a {nombre_impresora} (formato {formato})."
    except Exception as exc:
        return (
            False,
            f"No se pudo imprimir directo ({exc}). Verifica que tengas una impresora predeterminada en Windows.",
        )
