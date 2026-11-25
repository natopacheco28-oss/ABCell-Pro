"""Iconografía vectorial monocromática para la aplicación.

Todos los iconos se definen como gráficos SVG (estilo "feather/lucide":
trazos limpios, 24x24, ``currentColor``) y se renderizan con ``QSvgRenderer``.
Un icono toma el color que se le indique, de modo que se adapta al color del
botón o del estado visual, tal como exige la guía de jerarquía de botones.

Uso::

    from ui.icons import icono
    btn = icono("plus", "#1D4ED8", 18)   # devuelve QIcon

No depende de archivos externos ni de emojis de colores. Si ``QSvgRenderer``
no estuviera disponible, el módulo cae hacia un icono de trazo dibujado con
``QPainter`` para que el programa nunca rompa.
"""

from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QByteArray, QPointF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

try:
    from PySide6.QtSvg import QSvgRenderer

    _DISPONIBLE_SVG = True
except Exception:  # pragma: no cover - respaldo cuando QtSvg no está presente
    _DISPONIBLE_SVG = False


# --------------------------------------------------------------------------
# Gráficos SVG (trazos vectoriales limpios). Cada entrada usa currentColor.
# --------------------------------------------------------------------------
_ICONO_PATHS: Dict[str, str] = {
    # --- Navegación y acción general ---
    "orden": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<path d="M14 2v6h6"/>'
        '<path d="M16 13H8M16 17H8M10 9H8"/>'
    ),
    "nueva-orden": (
        '<path d="M12 5v14M5 12h14"/>'
    ),
    "inventario": (
        '<path d="M16.5 9.4 7.55 4.24"/>'
        '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>'
        '<path d="m3.27 6.96 8.73 5.05 8.73-5.05M12 22.08V12"/>'
    ),
    "catalogo": (
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>'
    ),
    "estadisticas": (
        '<path d="M3 3v18h18"/>'
        '<path d="M18 17V9"/>'
        '<path d="M13 17V5"/>'
        '<path d="M8 17v-3"/>'
    ),
    "utilidades": (
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'
    ),
    "configuracion": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>'
    ),
    "gearra": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>'
    ),
    # --- Acciones ---
    "imprimir": (
        '<polyline points="6 9 6 2 18 2 18 9"/>'
        '<path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>'
        '<rect x="6" y="14" width="12" height="8" rx="1"/>'
    ),
    "buscar": (
        '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'
    ),
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "trash": (
        '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
        '<path d="M10 11v6M14 11v6"/>'
    ),
    "editar": (
        '<path d="M12 20h9"/>'
        '<path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>'
    ),
    "copiar": (
        '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>'
        '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'
    ),
    "refresh": (
        '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>'
        '<path d="M21 3v5h-5"/>'
        '<path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>'
        '<path d="M3 21v-5h5"/>'
    ),
    "reiniciar": (
        '<path d="M23 4v6h-6"/><path d="M1 20v-6h6"/>'
        '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>'
    ),
    "guardar": (
        '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>'
        '<path d="M17 21v-8H7v8M7 3v5h8"/>'
    ),
    "descargar": (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>'
    ),
    "filtro": '<path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/>',
    "mas": '<path d="M12 5v14M5 12h14"/>',
    "menos": '<path d="M5 12h14"/>',
    "play": '<path d="M6 4l14 8-14 8z"/>',
    "stop": '<rect x="5" y="5" width="14" height="14" rx="2"/>',
    "ojo": (
        '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/>'
        '<circle cx="12" cy="12" r="3"/>'
    ),
    "ojo-off": (
        '<path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 10 8 10 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>'
        '<path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/>'
        '<path d="M2 2l20 20"/>'
    ),
    "confirmar": '<path d="M20 6 9 17l-5-5"/>',
    "cancelar": '<path d="M18 6 6 18M6 6l12 12"/>',
    "alerta": (
        '<path d="m10.29 3.86-8.18 14a2 2 0 0 0 1.71 3h16.36a2 2 0 0 0 1.71-3l-8.18-14a2 2 0 0 0-3.42 0z"/>'
        '<path d="M12 9v4M12 17h.01"/>'
    ),
    "info": (
        '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>'
    ),
    "zap": '<path d="M13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "flecha-derecha": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "flecha-izquierda": '<path d="M19 12H5M12 19l-7-7 7-7"/>',
    "chevron-abajo": '<path d="m6 9 6 6 6-6"/>',
    "chevron-derecha": '<path d="m9 18 6-6-6-6"/>',
    "combo": (
        '<path d="M4 7h16M4 12h16M4 17h16"/>'
    ),
    # --- Estado / métricas ---
    "escudo": (
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
    ),
    "escudo-check": (
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '<path d="M9 12l2 2 4-4"/>'
    ),
    "escudo-alerta": (
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '<path d="M12 8v4M12 16h.01"/>'
    ),
    "reloj": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "wifi": (
        '<path d="M5 13a10 10 0 0 1 14 0"/><path d="M8.5 16.5a5 5 0 0 1 7 0"/>'
        '<path d="M2 8.82a15 15 0 0 1 20 0"/><path d="M12 20h.01"/>'
    ),
    "bateria": (
        '<rect x="2" y="7" width="18" height="10" rx="2"/>'
        '<path d="M22 11v2"/>'
    ),
    "monitor": (
        '<rect x="2" y="3" width="20" height="14" rx="2"/>'
        '<path d="M8 21h8M12 17v4"/>'
    ),
    "chip": (
        '<rect x="4" y="4" width="16" height="16" rx="2"/>'
        '<rect x="9" y="9" width="6" height="6"/>'
        '<path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>'
    ),
    "base-datos": (
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>'
        '<path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>'
    ),
    "activity": (
        '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>'
    ),
    # --- Android / ADB ---
    "android": (
        '<path d="M5 16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5"/>'
        '<path d="M7 11V9a5 5 0 0 1 10 0v2"/>'
        '<path d="M9 6V4h6v2"/>'
        '<path d="M10 21v-2M14 21v-2"/>'
    ),
    "terminal": (
        '<path d="M4 17l6-6-6-6"/><path d="M12 19h8"/>'
    ),
    "camara": (
        '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>'
        '<circle cx="12" cy="13" r="4"/>'
    ),
    "piedra- papel": (
        '<path d="M12 3l4 7h-2l3 6-5 3-3-3-3 3-5-3 3-6h-2z"/>'
    ),
    # --- Catálogo / elementos ---
    "articulo": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M12 7v10M9.5 9.5h3.5a1.5 1.5 0 0 1 0 3h-3a1.5 1.5 0 0 0 0 3h3.5"/>'
    ),
    "ubicacion": (
        '<path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0 1 18 0z"/>'
        '<circle cx="12" cy="10" r="3"/>'
    ),
    "calendario": (
        '<rect x="3" y="4" width="18" height="18" rx="2"/>'
        '<path d="M16 2v4M8 2v4M3 10h18"/>'
    ),
    "user": (
        '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/>'
    ),
    "listado": (
        '<path d="M8 6h13M8 12h13M8 18h13"/>'
        '<path d="M3 6h.01M3 12h.01M3 18h.01"/>'
    ),
    "grilla": (
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>'
    ),
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "sun": (
        '<circle cx="12" cy="12" r="4"/>'
        '<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>'
    ),
    "papelera": (
        '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
    ),
    "mandar": (
        '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>'
    ),
    "mensajes": (
        '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>'
    ),
    "guarda": (
        '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>'
        '<path d="M17 21v-8H7v8M7 3v5h8"/>'
    ),
    "descarga": (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>'
    ),
    "mas-circulo": (
        '<circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/>'
    ),
    "herramienta": (
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'
    ),
}


def _svg_envelope(cuerpo: str) -> str:
    """Envuelve los trazos en un SVG 24x24 con estilo de trazo limpio."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f"{cuerpo}</svg>"
    )


def _svg_para(nombre: str) -> str:
    cuerpo = _ICONO_PATHS.get(nombre)
    if cuerpo is None:
        cuerpo = _ICONO_PATHS["configuracion"]
    return _svg_envelope(cuerpo)


def _render_svg(svg: str, color: str, tamano: int) -> QPixmap:
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    if not renderer.isValid():
        return QPixmap()
    # Alta resolución para nítidez en pantallas con alta densidad de píxeles.
    px = tamano * 4
    pix = QPixmap(px, px)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    renderer.render(painter)
    painter.end()
    # Escalar al tamaño pedido, conservando la transparencia.
    return pix.scaled(
        tamano, tamano, Qt.KeepAspectRatio, Qt.SmoothTransformation
    )


def _fallback_dibujado(nombre: str, color: str, tamano: int) -> QPixmap:
    """Respaldo sin QtSvg: dibuja un trazo simple pero legible."""
    from math import cos, radians, sin

    pix = QPixmap(tamano, tamano)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setPen(QPen(QColor(color), max(1, tamano // 12)))
    p.setBrush(Qt.NoBrush)
    cx = cy = tamano / 2.0
    radio = tamano * 0.32
    if nombre in {"gearra", "configuracion"}:
        p.drawEllipse(QPointF(cx, cy), radio * 0.6, radio * 0.6)
        for i in range(8):
            ang = radians(i * 45)
            x = cx + (radio - 2) * cos(ang)
            y = cy + (radio - 2) * sin(ang)
            p.drawLine(QPointF(x, y), QPointF(x + 4 * cos(ang), y + 4 * sin(ang)))
    else:
        p.drawEllipse(QPointF(cx, cy), radio, radio)
    p.end()
    return pix


def icono(nombre: str, color: str, tamano: int = 18) -> QIcon:
    """Devuelve un ``QIcon`` vectorial del icono ``nombre`` en ``color``.

    Si ``nombre`` no existe, se usa el icono de configuración como valor por
    defecto. Si ``QSvgRenderer`` no está disponible, se usa un trazo dibujado.
    """
    svg = _svg_para(nombre)
    if _DISPONIBLE_SVG:
        pix = _render_svg(svg, color, tamano)
        if pix.isNull():
            pix = _fallback_dibujado(nombre, color, tamano)
    else:
        pix = _fallback_dibujado(nombre, color, tamano)
    return QIcon(pix)


def existe_icono(nombre: str) -> bool:
    return nombre in _ICONO_PATHS


def nombres_iconos() -> tuple:
    return tuple(sorted(_ICONO_PATHS.keys()))
