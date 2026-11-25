"""Sistema de temas profesional de la aplicación.

Este módulo es el **único punto centralizado** de la apariencia. Cada tema es
una paleta de colores que se expande en un stylesheet QSS completo y
coherente (fondos, paneles, bordes, inputs, tablas, textos, estados,
scrollbars) mediante ``_QSS_TEMPLATE``.

Se entregan seis temas equilibrados::

    Claros    : "Mostrador Limpio", "Laboratorio Minimal", "Arena Suave"
    Oscuros   : "Grafito Pro", "Midnight Slate", "Placa Madre Emerald"

El tema por defecto es **"Mostrador Limpio"** (modo claro).

Agregar un tema solo requiere añadir una entrada a ``PALETAS_TEMAS`` y, si se
desea, a ``TEMAS_ORDEN``. ``GestorTemas`` expone la API de lectura/aplicación
y ``construir_qss`` produce el stylesheet listo para ``setStyleSheet``.

Se mantienen ``LIGHT_QSS`` / ``DARK_QSS`` por compatibilidad.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# --------------------------------------------------------------------------
# Plantilla QSS completa. Cada ``%(key)s`` se resuelve con la paleta del tema.
# --------------------------------------------------------------------------
_QSS_TEMPLATE = """
* {
    outline: none;
}

QMainWindow, QDialog, QWidget {
    background-color: %(bg)s;
    color: %(fg)s;
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 14px;
}

QScrollArea, QScrollArea > QWidget > QWidget {
    background-color: transparent;
    border: none;
}

/* ---------- Paneles y tarjetas ---------- */
QFrame#Sidebar {
    background-color: %(sidebar_bg)s;
    border-right: 1px solid %(sidebar_border)s;
}

QFrame#Card, QFrame#Panel {
    background-color: %(card_bg)s;
    border: 1px solid %(card_border)s;
    border-radius: 12px;
}

QFrame#SubBar {
    background-color: %(subcard_bg)s;
    border: 1px solid %(subcard_border)s;
    border-radius: 10px;
}

QFrame#Divider {
    background-color: transparent;
    border: none;
}

QFrame#HLine {
    background-color: %(divider)s;
    border: none;
    max-height: 1px;
    min-height: 1px;
}

/* ---------- Textos ---------- */
QLabel {
    background-color: transparent;
    color: %(label_fg)s;
    background: transparent;
}

QLabel#Title {
    font-size: 22px;
    font-weight: 700;
    color: %(title)s;
}

QLabel#Subtitle {
    font-size: 15px;
    font-weight: 600;
    color: %(cardtitle)s;
}

QLabel#Breadcrumb {
    font-size: 12px;
    color: %(breadcrumb)s;
}

QLabel#BrandTitle {
    font-size: 17px;
    font-weight: 800;
    color: %(brand)s;
}

QLabel#CardTitle {
    font-size: 13px;
    font-weight: 700;
    color: %(cardtitle)s;
}

QLabel#CardSub {
    font-size: 12px;
    color: %(cardsub)s;
}

QLabel#CardLink {
    font-size: 12px;
    font-weight: 700;
    color: %(cardlink)s;
}

QLabel#MetricValue {
    font-size: 20px;
    font-weight: 700;
    color: %(metric)s;
}

QLabel#FolioBadge {
    font-size: 12px;
    font-weight: 700;
    color: %(folio)s;
}

QLabel#Dim {
    font-size: 12px;
    color: %(label_dim)s;
}

/* ---------- Botones base ---------- */
QPushButton {
    background-color: %(btn_bg)s;
    color: %(btn_fg)s;
    border: 1px solid %(btn_border)s;
    border-radius: 10px;
    padding: 9px 16px;
    font-weight: 600;
    text-align: center;
}

QPushButton:hover {
    background-color: %(btn_hover_bg)s;
    border-color: %(btn_hover_border)s;
    color: %(btn_hover_fg)s;
}

QPushButton:pressed {
    background-color: %(btn_pressed_bg)s;
}

QPushButton:disabled {
    background-color: %(btn_disabled_bg)s;
    color: %(btn_disabled_fg)s;
    border-color: %(btn_disabled_border)s;
}

/* --- Jerarquía: PRINCIPAL (relleno del acento) --- */
QPushButton#PrimaryBtn {
    background-color: %(primary_bg)s;
    border-color: %(primary_border)s;
    color: %(primary_fg)s;
    font-weight: 700;
    padding: 10px 20px;
}

QPushButton#PrimaryBtn:hover {
    background-color: %(primary_hover_bg)s;
    border-color: %(primary_hover_border)s;
    color: %(primary_fg)s;
}

QPushButton#PrimaryBtn:pressed {
    background-color: %(primary_pressed_bg)s;
}

/* --- Jerarquía: SECUNDARIO (borde definido / fondo sutil) --- */
QPushButton#SecondaryBtn {
    background-color: %(secondary_bg)s;
    border: 1px solid %(secondary_border)s;
    color: %(secondary_fg)s;
    font-weight: 600;
}

QPushButton#SecondaryBtn:hover {
    background-color: %(secondary_hover_bg)s;
    border-color: %(secondary_hover_border)s;
    color: %(secondary_hover_fg)s;
}

QPushButton#SecondaryBtn:pressed {
    background-color: %(secondary_pressed_bg)s;
}

/* --- Jerarquía: CRÍTICO / PELIGRO --- */
QPushButton#DangerBtn {
    background-color: %(danger_bg)s;
    border: 1px solid %(danger_border)s;
    color: %(danger_fg)s;
    font-weight: 700;
}

QPushButton#DangerBtn:hover {
    background-color: %(danger_hover_bg)s;
    border-color: %(danger_hover_border)s;
    color: %(danger_fg)s;
}

QPushButton#DangerBtn:pressed {
    background-color: %(danger_pressed_bg)s;
}

/* --- Botones compactos para filas de tabla --- */
QPushButton#AccBtn {
    background-color: transparent;
    border: 1px solid %(secondary_border)s;
    color: %(secondary_fg)s;
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#AccBtn:hover {
    background-color: %(secondary_hover_bg)s;
    border-color: %(secondary_hover_border)s;
    color: %(secondary_hover_fg)s;
}

QPushButton#AccDangerBtn {
    background-color: transparent;
    border: 1px solid %(danger_border)s;
    color: %(danger_fg)s;
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#AccDangerBtn:hover {
    background-color: %(danger_hover_bg)s;
    border-color: %(danger_hover_border)s;
    color: %(danger_fg)s;
}

/* --- Botones solo icono (sin texto) --- */
QPushButton#IconBtn {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 8px;
    color: %(icon)s;
}

QPushButton#IconBtn:hover {
    background-color: %(icon_hover_bg)s;
    border-color: %(icon_hover_border)s;
    color: %(accent)s;
}

QPushButton#IconBtn:pressed {
    background-color: %(icon_hover_border)s;
}

/* --- Botón de engranaje --- */
QPushButton#GearBtn {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 8px;
    color: %(icon)s;
}

QPushButton#GearBtn:hover {
    background-color: %(icon_hover_bg)s;
    border-color: %(icon_hover_border)s;
    color: %(accent)s;
}

/* --- Navegación lateral --- */
QPushButton#NavBtn {
    text-align: left;
    padding: 11px 16px;
    background-color: transparent;
    color: %(nav_fg)s;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 10px;
    font-weight: 600;
}

QPushButton#NavBtn:hover {
    background-color: %(nav_hover_bg)s;
    color: %(nav_hover_fg)s;
}

QPushButton#NavBtn[active="true"] {
    background-color: %(nav_active_bg)s;
    color: %(nav_active_fg)s;
    border-left: 3px solid %(nav_active_border)s;
    font-weight: 700;
}

/* --- Pestañas de etapa --- */
QPushButton#StageTab {
    background-color: transparent;
    color: %(stage_fg)s;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton#StageTab:hover {
    color: %(stage_hover)s;
}

QPushButton#StageTab[active="true"] {
    color: %(stage_active)s;
    border-bottom: 2px solid %(stage_active_border)s;
    font-weight: 700;
}

/* ---------- Inputs ---------- */
QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QDoubleSpinBox, QSpinBox,
QDateEdit, QTimeEdit {
    background-color: %(input_bg)s;
    color: %(input_fg)s;
    border: 1px solid %(input_border)s;
    border-radius: 10px;
    padding: 9px 13px;
    selection-background-color: %(accent)s;
    selection-color: %(primary_fg)s;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus,
QDoubleSpinBox:focus, QSpinBox:focus, QDateEdit:focus, QTimeEdit:focus {
    border: 1px solid %(input_focus)s;
    background-color: %(input_focus_bg)s;
}

QLineEdit:disabled, QComboBox:disabled, QTextEdit:disabled,
QPlainTextEdit:disabled, QDoubleSpinBox:disabled, QSpinBox:disabled {
    background-color: %(input_disabled_bg)s;
    color: %(input_disabled_fg)s;
}

QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: %(input_disabled_bg)s;
}

/* Selector desplegable del combo */
QComboBox QAbstractItemView {
    background-color: %(card_bg)s;
    color: %(fg)s;
    border: 1px solid %(card_border)s;
    border-radius: 8px;
    selection-background-color: %(accent_soft)s;
    selection-color: %(accent)s;
    outline: none;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 6px;
}

/* Botones de aumento/decremento de spinboxes */
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
    background-color: %(subcard_bg)s;
    border: 1px solid %(subcard_border)s;
    width: 24px;
    border-radius: 6px;
    margin: 1px;
}

QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {
    background-color: %(accent_soft)s;
}

QAbstractSpinBox::up-arrow, QAbstractSpinBox::down-arrow {
    background-color: transparent;
    color: %(accent)s;
    width: 8px;
    height: 8px;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
}

QAbstractSpinBox::up-arrow { border-bottom: 3px solid %(accent)s; }
QAbstractSpinBox::down-arrow { border-top: 3px solid %(accent)s; }

/* ---------- Tablas ---------- */
QTableWidget {
    background-color: %(table_bg)s;
    alternate-background-color: %(table_alt)s;
    color: %(fg)s;
    gridline-color: %(grid)s;
    border: 1px solid %(table_border)s;
    border-radius: 10px;
    selection-background-color: %(sel_bg)s;
    selection-color: %(sel_fg)s;
}

QTableWidget::item {
    padding: 9px 12px;
    border: none;
}

QTableWidget::item:selected {
    background-color: %(sel_bg)s;
    color: %(sel_fg)s;
}

QHeaderView::section {
    background-color: %(header_bg)s;
    color: %(header_fg)s;
    padding: 11px 14px;
    border: none;
    border-bottom: 1px solid %(header_border)s;
    border-right: 1px solid %(header_border)s;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
}

/* ---------- Pestañas ---------- */
QTabWidget::pane {
    border: 1px solid %(table_border)s;
    border-radius: 12px;
    background-color: %(card_bg)s;
    top: -1px;
}

QTabBar::tab {
    background-color: %(tab_bg)s;
    color: %(tab_fg)s;
    padding: 9px 18px;
    border-top-left-radius: 9px;
    border-top-right-radius: 9px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:hover {
    color: %(accent)s;
}

QTabBar::tab:selected {
    background-color: %(tab_sel_bg)s;
    color: %(tab_sel_fg)s;
    font-weight: 700;
}

/* ---------- Scrollbars elegantes ---------- */
QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background-color: %(scroll_handle)s;
    border-radius: 6px;
    min-height: 40px;
    border: none;
}

QScrollBar::handle:vertical:hover {
    background-color: %(scroll_handle_hover)s;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: transparent;
    border: none;
}

QScrollBar:horizontal {
    background: transparent;
    height: 12px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background-color: %(scroll_handle)s;
    border-radius: 6px;
    min-width: 40px;
    border: none;
}

QScrollBar::handle:horizontal:hover {
    background-color: %(scroll_handle_hover)s;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
    background: transparent;
    border: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
    border: none;
}

/* ---------- Tooltips ---------- */
QToolTip {
    background-color: %(tooltip_bg)s;
    color: %(tooltip_fg)s;
    border: 1px solid %(card_border)s;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ---------- Otros controles ---------- */
QProgressBar {
    background-color: %(progress_bg)s;
    border: 1px solid %(card_border)s;
    border-radius: 8px;
    height: 10px;
    text-align: center;
    color: %(label_fg)s;
}

QProgressBar::chunk {
    background-color: %(accent)s;
    border-radius: 8px;
}

QSlider::groove:horizontal {
    background-color: %(progress_bg)s;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: %(accent)s;
    width: 18px;
    height: 18px;
    border-radius: 9px;
    margin: -6px 0;
}

QSlider::handle:horizontal:hover {
    background-color: %(primary_hover_bg)s;
}

QCheckBox, QRadioButton {
    color: %(label_fg)s;
    spacing: 8px;
    font-size: 14px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid %(input_border)s;
    background-color: %(input_bg)s;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: %(accent)s;
    border-color: %(accent)s;
}

QRadioButton::indicator { border-radius: 9px; }

QGroupBox {
    border: 1px solid %(card_border)s;
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 12px;
    color: %(cardtitle)s;
    font-weight: 700;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    color: %(accent)s;
}

QMenu {
    background-color: %(card_bg)s;
    color: %(fg)s;
    border: 1px solid %(card_border)s;
    border-radius: 10px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 28px 8px 14px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: %(accent_soft)s;
    color: %(accent)s;
}

QMenu::separator {
    height: 1px;
    background: %(divider)s;
    margin: 4px 8px;
}

QToolButton {
    background-color: transparent;
    color: %(icon)s;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 8px;
}

QToolButton:hover {
    background-color: %(icon_hover_bg)s;
    border-color: %(icon_hover_border)s;
}

QStatusBar {
    background-color: %(subcard_bg)s;
    color: %(label_dim)s;
    border-top: 1px solid %(subcard_border)s;
}

QSplitter::handle {
    background-color: %(divider)s;
}

QSplitter::handle:hover {
    background-color: %(accent)s;
}

QSizeGrip {
    background-color: transparent;
}

QListWidget, QListView {
    background-color: %(input_bg)s;
    color: %(fg)s;
    border: 1px solid %(input_border)s;
    border-radius: 10px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 8px 10px;
    border-radius: 6px;
}

QListWidget::item:selected {
    background-color: %(accent_soft)s;
    color: %(accent)s;
}

QDialogButtonBox QPushButton {
    min-width: 84px;
}

QLabel#BrandSub {
    font-size: 10px;
    color: %(label_dim)s;
    letter-spacing: 0.5px;
}

QLabel#NavCount {
    font-size: 11px;
    font-weight: 700;
    color: %(nav_active_fg)s;
}
"""

# --------------------------------------------------------------------------
# Valores por defecto para cualquier clave omitida en una paleta.
# --------------------------------------------------------------------------
_PALETTE_DEFAULTS: Dict[str, str] = {
    "bg": "#f4f6f9",
    "fg": "#1e293b",
    "sidebar_bg": "#ffffff",
    "sidebar_border": "#e5e7eb",
    "sidebar_fg": "#475569",
    "card_bg": "#ffffff",
    "subcard_bg": "#f8fafc",
    "card_border": "#e5e7eb",
    "subcard_border": "#e5e7eb",
    "divider": "#e5e7eb",
    "label_fg": "#374151",
    "label_dim": "#94a3b8",
    "title": "#0f172a",
    "breadcrumb": "#94a3b8",
    "brand": "#1d4ed8",
    "cardtitle": "#111827",
    "cardsub": "#6b7280",
    "cardlink": "#1d4ed8",
    "metric": "#1d4ed8",
    "folio": "#111827",
    "icon": "#475569",
    "accent": "#1d4ed8",
    "accent_soft": "#dbeafe",
    "accent_border": "#bfdbfe",
    "btn_bg": "#ffffff",
    "btn_fg": "#374151",
    "btn_border": "#e5e7eb",
    "btn_hover_bg": "#f3f4f6",
    "btn_hover_border": "#1d4ed8",
    "btn_hover_fg": "#1d4ed8",
    "btn_pressed_bg": "#e2e8f0",
    "btn_disabled_bg": "#f1f5f9",
    "btn_disabled_fg": "#94a3b8",
    "btn_disabled_border": "#e2e8f0",
    "icon_hover_bg": "#f3f4f6",
    "icon_hover_border": "#e5e7eb",
    "primary_bg": "#1d4ed8",
    "primary_border": "#1d4ed8",
    "primary_fg": "#ffffff",
    "primary_hover_bg": "#1e40af",
    "primary_hover_border": "#1e40af",
    "primary_pressed_bg": "#1e3a8a",
    "secondary_bg": "#ffffff",
    "secondary_border": "#e5e7eb",
    "secondary_fg": "#374151",
    "secondary_hover_bg": "#f3f4f6",
    "secondary_hover_border": "#1d4ed8",
    "secondary_hover_fg": "#1d4ed8",
    "secondary_pressed_bg": "#e2e8f0",
    "danger_bg": "#dc2626",
    "danger_border": "#dc2626",
    "danger_fg": "#ffffff",
    "danger_hover_bg": "#b91c1c",
    "danger_hover_border": "#b91c1c",
    "danger_pressed_bg": "#991b1b",
    "nav_fg": "#475569",
    "nav_hover_bg": "#f3f4f6",
    "nav_hover_fg": "#1d4ed8",
    "nav_active_bg": "#dbeafe",
    "nav_active_fg": "#1d4ed8",
    "nav_active_border": "#1d4ed8",
    "stage_fg": "#6b7280",
    "stage_hover": "#1d4ed8",
    "stage_active": "#1d4ed8",
    "stage_active_border": "#1d4ed8",
    "input_bg": "#ffffff",
    "input_fg": "#111827",
    "input_border": "#e5e7eb",
    "input_focus": "#1d4ed8",
    "input_focus_bg": "#ffffff",
    "input_disabled_bg": "#f1f5f9",
    "input_disabled_fg": "#94a3b8",
    "table_bg": "#ffffff",
    "table_alt": "#f9fafb",
    "grid": "#e5e7eb",
    "table_border": "#e5e7eb",
    "header_bg": "#f9fafb",
    "header_fg": "#6b7280",
    "header_border": "#e5e7eb",
    "sel_bg": "#dbeafe",
    "sel_fg": "#1e40af",
    "tab_bg": "#e5e7eb",
    "tab_fg": "#475569",
    "tab_sel_bg": "#1d4ed8",
    "tab_sel_fg": "#ffffff",
    "scroll_handle": "#cbd5e1",
    "scroll_handle_hover": "#94a3b8",
    "tooltip_bg": "#1f2937",
    "tooltip_fg": "#f9fafb",
    "progress_bg": "#e5e7eb",
}


def _paleta(**valores: str) -> Dict[str, str]:
    """Completa una paleta con los valores por defecto."""
    return {**_PALETTE_DEFAULTS, **valores}


# --------------------------------------------------------------------------
# Los seis temas profesionales.
# --------------------------------------------------------------------------
PALETAS_TEMAS: Dict[str, Dict[str, str]] = {
    # 1) Claro — mostrador limpio, acento azul acero.
    "Mostrador Limpio": _paleta(
        bg="#f4f6f9", fg="#1e293b",
        sidebar_bg="#ffffff", sidebar_border="#e5e7eb", sidebar_fg="#475569",
        card_bg="#ffffff", subcard_bg="#f8fafc",
        card_border="#e5e7eb", subcard_border="#e5e7eb", divider="#e5e7eb",
        label_fg="#475569", label_dim="#94a3b8",
        title="#0f172a", breadcrumb="#94a3b8", brand="#1d4ed8",
        cardtitle="#111827", cardsub="#6b7280", cardlink="#1d4ed8",
        metric="#1d4ed8", folio="#111827", icon="#475569",
        accent="#1d4ed8", accent_soft="#dbeafe", accent_border="#bfdbfe",
        btn_bg="#ffffff", btn_fg="#374151", btn_border="#e5e7eb",
        btn_hover_bg="#f3f4f6", btn_hover_border="#1d4ed8", btn_hover_fg="#1d4ed8",
        btn_pressed_bg="#e2e8f0",
        icon_hover_bg="#f3f4f6", icon_hover_border="#e5e7eb",
        primary_bg="#1d4ed8", primary_border="#1d4ed8", primary_fg="#ffffff",
        primary_hover_bg="#1e40af", primary_hover_border="#1e40af",
        primary_pressed_bg="#1e3a8a",
        secondary_bg="#ffffff", secondary_border="#e5e7eb", secondary_fg="#374151",
        secondary_hover_bg="#f3f4f6", secondary_hover_border="#1d4ed8",
        secondary_hover_fg="#1d4ed8",
        danger_bg="#dc2626", danger_border="#dc2626", danger_fg="#ffffff",
        danger_hover_bg="#b91c1c", danger_hover_border="#b91c1c",
        nav_fg="#475569", nav_hover_bg="#f3f4f6", nav_hover_fg="#1d4ed8",
        nav_active_bg="#dbeafe", nav_active_fg="#1d4ed8",
        nav_active_border="#1d4ed8",
        stage_fg="#6b7280", stage_hover="#1d4ed8", stage_active="#1d4ed8",
        stage_active_border="#1d4ed8",
        input_bg="#ffffff", input_fg="#111827", input_border="#e5e7eb",
        input_focus="#1d4ed8", input_focus_bg="#ffffff",
        table_bg="#ffffff", table_alt="#f9fafb", grid="#e5e7eb",
        table_border="#e5e7eb", header_bg="#f9fafb", header_fg="#6b7280",
        header_border="#e5e7eb", sel_bg="#dbeafe", sel_fg="#1e40af",
        tab_bg="#e5e7eb", tab_fg="#475569", tab_sel_bg="#1d4ed8",
        tab_sel_fg="#ffffff",
        scroll_handle="#cbd5e1", scroll_handle_hover="#94a3b8",
        tooltip_bg="#1f2937", tooltip_fg="#f9fafb",
    ),
    # 2) Claro — laboratorio minimal, bordes grises, acento azul vivo.
    "Laboratorio Minimal": _paleta(
        bg="#fafafa", fg="#18181b",
        sidebar_bg="#ffffff", sidebar_border="#e5e7eb", sidebar_fg="#525252",
        card_bg="#ffffff", subcard_bg="#f5f5f5",
        card_border="#e5e7eb", subcard_border="#e5e7eb", divider="#e5e7eb",
        label_fg="#525252", label_dim="#a3a3a3",
        title="#171717", breadcrumb="#a3a3a3", brand="#007aff",
        cardtitle="#171717", cardsub="#737373", cardlink="#007aff",
        metric="#007aff", folio="#171717", icon="#525252",
        accent="#007aff", accent_soft="#e0f2fe", accent_border="#bfdbfe",
        btn_bg="#ffffff", btn_fg="#404040", btn_border="#e5e7eb",
        btn_hover_bg="#f5f5f5", btn_hover_border="#007aff", btn_hover_fg="#007aff",
        btn_pressed_bg="#e5e5e5",
        icon_hover_bg="#f5f5f5", icon_hover_border="#e5e7eb",
        primary_bg="#007aff", primary_border="#007aff", primary_fg="#ffffff",
        primary_hover_bg="#0056cc", primary_hover_border="#0056cc",
        primary_pressed_bg="#004099",
        secondary_bg="#ffffff", secondary_border="#e5e7eb", secondary_fg="#404040",
        secondary_hover_bg="#f5f5f5", secondary_hover_border="#007aff",
        secondary_hover_fg="#007aff",
        danger_bg="#dc2626", danger_border="#dc2626", danger_fg="#ffffff",
        danger_hover_bg="#b91c1c", danger_hover_border="#b91c1c",
        nav_fg="#525252", nav_hover_bg="#f5f5f5", nav_hover_fg="#007aff",
        nav_active_bg="#e0f2fe", nav_active_fg="#007aff",
        nav_active_border="#007aff",
        stage_fg="#737373", stage_hover="#007aff", stage_active="#007aff",
        stage_active_border="#007aff",
        input_bg="#ffffff", input_fg="#171717", input_border="#e5e7eb",
        input_focus="#007aff", input_focus_bg="#ffffff",
        table_bg="#ffffff", table_alt="#fafafa", grid="#e5e7eb",
        table_border="#e5e7eb", header_bg="#fafafa", header_fg="#737373",
        header_border="#e5e7eb", sel_bg="#e0f2fe", sel_fg="#0056cc",
        tab_bg="#e5e7eb", tab_fg="#525252", tab_sel_bg="#007aff",
        tab_sel_fg="#ffffff",
        scroll_handle="#e5e7eb", scroll_handle_hover="#a3a3a3",
        tooltip_bg="#171717", tooltip_fg="#fafafa",
    ),
    # 3) Claro anti-fatiga — arena suave, texto café, acento terracota.
    "Arena Suave": _paleta(
        bg="#f7f5f0", fg="#3b2f2a",
        sidebar_bg="#fbf8f2", sidebar_border="#e7decf", sidebar_fg="#6b5b50",
        card_bg="#fcfaf5", subcard_bg="#f2eadf",
        card_border="#e7decf", subcard_border="#e7decf", divider="#e7decf",
        label_fg="#6b5b50", label_dim="#a89a8e",
        title="#4a3a30", breadcrumb="#a89a8e", brand="#c2410c",
        cardtitle="#4a3a30", cardsub="#8a786c", cardlink="#c2410c",
        metric="#c2410c", folio="#4a3a30", icon="#6b5b50",
        accent="#c2410c", accent_soft="#fbe8dd", accent_border="#f0cdb8",
        btn_bg="#ffffff", btn_fg="#5b4a3f", btn_border="#e0d5c2",
        btn_hover_bg="#f2eadf", btn_hover_border="#c2410c", btn_hover_fg="#c2410c",
        btn_pressed_bg="#e5d8c5",
        icon_hover_bg="#f2eadf", icon_hover_border="#e7decf",
        primary_bg="#c2410c", primary_border="#c2410c", primary_fg="#ffffff",
        primary_hover_bg="#9a3408", primary_hover_border="#9a3408",
        primary_pressed_bg="#7c2d12",
        secondary_bg="#ffffff", secondary_border="#e0d5c2", secondary_fg="#5b4a3f",
        secondary_hover_bg="#f2eadf", secondary_hover_border="#c2410c",
        secondary_hover_fg="#c2410c",
        danger_bg="#dc2626", danger_border="#dc2626", danger_fg="#ffffff",
        danger_hover_bg="#b91c1c", danger_hover_border="#b91c1c",
        nav_fg="#6b5b50", nav_hover_bg="#f2eadf", nav_hover_fg="#c2410c",
        nav_active_bg="#fbe8dd", nav_active_fg="#c2410c",
        nav_active_border="#c2410c",
        stage_fg="#8a786c", stage_hover="#c2410c", stage_active="#c2410c",
        stage_active_border="#c2410c",
        input_bg="#ffffff", input_fg="#4a3a30", input_border="#e0d5c2",
        input_focus="#c2410c", input_focus_bg="#ffffff",
        table_bg="#ffffff", table_alt="#fbf8f2", grid="#e7decf",
        table_border="#e7decf", header_bg="#fbf8f2", header_fg="#8a786c",
        header_border="#e7decf", sel_bg="#fbe8dd", sel_fg="#9a3408",
        tab_bg="#e7decf", tab_fg="#6b5b50", tab_sel_bg="#c2410c",
        tab_sel_fg="#ffffff",
        scroll_handle="#d9cbae", scroll_handle_hover="#b8a07f",
        tooltip_bg="#4a3a30", tooltip_fg="#fbf8f2",
    ),
    # 4) Oscuro elegante — grafito pro, acento azul eléctrico.
    "Grafito Pro": _paleta(
        bg="#18181b", fg="#fafafa",
        sidebar_bg="#1c1c1f", sidebar_border="#27272a", sidebar_fg="#d4d4d8",
        card_bg="#27272a", subcard_bg="#2a2a2e",
        card_border="#3f3f46", subcard_border="#3f3f46", divider="#3f3f46",
        label_fg="#d4d4d8", label_dim="#a1a1aa",
        title="#fafafa", breadcrumb="#a1a1aa", brand="#3b82f6",
        cardtitle="#fafafa", cardsub="#a1a1aa", cardlink="#60a5fa",
        metric="#60a5fa", folio="#fafafa", icon="#d4d4d8",
        accent="#3b82f6", accent_soft="#1e3a5f", accent_border="#1e3a8a",
        btn_bg="#27272a", btn_fg="#e5e5e5", btn_border="#3f3f46",
        btn_hover_bg="#3f3f46", btn_hover_border="#3b82f6", btn_hover_fg="#60a5fa",
        btn_pressed_bg="#4b4b4f",
        btn_disabled_bg="#2a2a2e", btn_disabled_fg="#71717a",
        btn_disabled_border="#3f3f46",
        icon_hover_bg="#3f3f46", icon_hover_border="#3f3f46",
        primary_bg="#3b82f6", primary_border="#3b82f6", primary_fg="#ffffff",
        primary_hover_bg="#2563eb", primary_hover_border="#2563eb",
        primary_pressed_bg="#1d4ed8",
        secondary_bg="#27272a", secondary_border="#3f3f46", secondary_fg="#e5e5e5",
        secondary_hover_bg="#3f3f46", secondary_hover_border="#3b82f6",
        secondary_hover_fg="#60a5fa",
        danger_bg="#dc2626", danger_border="#dc2626", danger_fg="#ffffff",
        danger_hover_bg="#b91c1c", danger_hover_border="#b91c1c",
        nav_fg="#d4d4d8", nav_hover_bg="#27272a", nav_hover_fg="#60a5fa",
        nav_active_bg="#1e3a5f", nav_active_fg="#60a5fa",
        nav_active_border="#3b82f6",
        stage_fg="#a1a1aa", stage_hover="#60a5fa", stage_active="#60a5fa",
        stage_active_border="#3b82f6",
        input_bg="#18181b", input_fg="#fafafa", input_border="#3f3f46",
        input_focus="#3b82f6", input_focus_bg="#1c1c20",
        input_disabled_bg="#2a2a2e", input_disabled_fg="#71717a",
        table_bg="#1c1c1f", table_alt="#18181b", grid="#27272a",
        table_border="#2a2a2e", header_bg="#27272a", header_fg="#a1a1aa",
        header_border="#3f3f46", sel_bg="#1e3a5f", sel_fg="#93c5fd",
        tab_bg="#27272a", tab_fg="#a1a1aa", tab_sel_bg="#3b82f6",
        tab_sel_fg="#ffffff",
        scroll_handle="#4b4b4f", scroll_handle_hover="#71717a",
        tooltip_bg="#27272a", tooltip_fg="#e5e5e5",
        progress_bg="#3f3f46",
    ),
    # 5) Oscuro tech — midnight slate, acento cian.
    "Midnight Slate": _paleta(
        bg="#0f172a", fg="#e2e8f0",
        sidebar_bg="#0b1220", sidebar_border="#1e293b", sidebar_fg="#cbd5e1",
        card_bg="#1e293b", subcard_bg="#16202f",
        card_border="#334155", subcard_border="#334155", divider="#334155",
        label_fg="#cbd5e1", label_dim="#94a3b8",
        title="#f8fafc", breadcrumb="#94a3b8", brand="#06b6d4",
        cardtitle="#f8fafc", cardsub="#94a3b8", cardlink="#22d3ee",
        metric="#22d3ee", folio="#f8fafc", icon="#cbd5e1",
        accent="#06b6d4", accent_soft="#0e3a40", accent_border="#155e63",
        btn_bg="#1e293b", btn_fg="#e2e8f0", btn_border="#334155",
        btn_hover_bg="#334155", btn_hover_border="#06b6d4", btn_hover_fg="#22d3ee",
        btn_pressed_bg="#3b4a63",
        btn_disabled_bg="#16202f", btn_disabled_fg="#64748b",
        btn_disabled_border="#334155",
        icon_hover_bg="#334155", icon_hover_border="#334155",
        primary_bg="#06b6d4", primary_border="#06b6d4", primary_fg="#04141a",
        primary_hover_bg="#0891b2", primary_hover_border="#0891b2",
        primary_pressed_bg="#0e7490",
        secondary_bg="#1e293b", secondary_border="#334155", secondary_fg="#e2e8f0",
        secondary_hover_bg="#334155", secondary_hover_border="#06b6d4",
        secondary_hover_fg="#22d3ee",
        danger_bg="#dc2626", danger_border="#dc2626", danger_fg="#ffffff",
        danger_hover_bg="#b91c1c", danger_hover_border="#b91c1c",
        nav_fg="#cbd5e1", nav_hover_bg="#1e293b", nav_hover_fg="#22d3ee",
        nav_active_bg="#0e3a40", nav_active_fg="#22d3ee",
        nav_active_border="#06b6d4",
        stage_fg="#94a3b8", stage_hover="#22d3ee", stage_active="#22d3ee",
        stage_active_border="#06b6d4",
        input_bg="#0f172a", input_fg="#f8fafc", input_border="#334155",
        input_focus="#06b6d4", input_focus_bg="#122034",
        input_disabled_bg="#16202f", input_disabled_fg="#64748b",
        table_bg="#111c33", table_alt="#0f172a", grid="#1e293b",
        table_border="#1c2a3c", header_bg="#1e293b", header_fg="#94a3b8",
        header_border="#334155", sel_bg="#0e3a40", sel_fg="#67e8f9",
        tab_bg="#1e293b", tab_fg="#94a3b8", tab_sel_bg="#06b6d4",
        tab_sel_fg="#04141a",
        scroll_handle="#334155", scroll_handle_hover="#64748b",
        tooltip_bg="#1e293b", tooltip_fg="#e2e8f0",
        progress_bg="#334155",
    ),
    # 6) Oscuro laboratorio — placa madre emerald, acento verde.
    "Placa Madre Emerald": _paleta(
        bg="#0f1715", fg="#e6f0ec",
        sidebar_bg="#0b1210", sidebar_border="#16221f", sidebar_fg="#cbd5cf",
        card_bg="#16221f", subcard_bg="#121c17",
        card_border="#244036", subcard_border="#244036", divider="#244036",
        label_fg="#cbd5cf", label_dim="#94a89e",
        title="#f0fbf6", breadcrumb="#94a89e", brand="#10b981",
        cardtitle="#f0fbf6", cardsub="#94a89e", cardlink="#34d399",
        metric="#34d399", folio="#f0fbf6", icon="#cbd5cf",
        accent="#10b981", accent_soft="#0e3a2b", accent_border="#155e40",
        btn_bg="#16221f", btn_fg="#e6f0ec", btn_border="#244036",
        btn_hover_bg="#244036", btn_hover_border="#10b981", btn_hover_fg="#34d399",
        btn_pressed_bg="#2c5040",
        btn_disabled_bg="#121c17", btn_disabled_fg="#5f8075",
        btn_disabled_border="#244036",
        icon_hover_bg="#244036", icon_hover_border="#244036",
        primary_bg="#10b981", primary_border="#10b981", primary_fg="#04140f",
        primary_hover_bg="#059669", primary_hover_border="#059669",
        primary_pressed_bg="#047857",
        secondary_bg="#16221f", secondary_border="#244036", secondary_fg="#e6f0ec",
        secondary_hover_bg="#244036", secondary_hover_border="#10b981",
        secondary_hover_fg="#34d399",
        danger_bg="#dc2626", danger_border="#dc2626", danger_fg="#ffffff",
        danger_hover_bg="#b91c1c", danger_hover_border="#b91c1c",
        nav_fg="#cbd5cf", nav_hover_bg="#16221f", nav_hover_fg="#34d399",
        nav_active_bg="#0e3a2b", nav_active_fg="#34d399",
        nav_active_border="#10b981",
        stage_fg="#94a89e", stage_hover="#34d399", stage_active="#34d399",
        stage_active_border="#10b981",
        input_bg="#0f1715", input_fg="#f0fbf6", input_border="#244036",
        input_focus="#10b981", input_focus_bg="#10201a",
        input_disabled_bg="#121c17", input_disabled_fg="#5f8075",
        table_bg="#101c17", table_alt="#0f1715", grid="#16221f",
        table_border="#121c17", header_bg="#16221f", header_fg="#94a89e",
        header_border="#244036", sel_bg="#0e3a2b", sel_fg="#6ee7b7",
        tab_bg="#16221f", tab_fg="#94a89e", tab_sel_bg="#10b981",
        tab_sel_fg="#04140f",
        scroll_handle="#244036", scroll_handle_hover="#4b6b5e",
        tooltip_bg="#16221f", tooltip_fg="#e6f0ec",
        progress_bg="#244036",
    ),
}

# Orden del selector (el primero es el tema por defecto).
TEMAS_ORDEN: List[str] = [
    "Mostrador Limpio",
    "Laboratorio Minimal",
    "Arena Suave",
    "Grafito Pro",
    "Midnight Slate",
    "Placa Madre Emerald",
]

TEMA_POR_DEFECTO = "Mostrador Limpio"

# Temas considerados oscuros (para iconos, contraste, etc.).
TEMAS_OSCUROS = frozenset({"Grafito Pro", "Midnight Slate", "Placa Madre Emerald"})


def construir_qss(tema: str) -> str:
    """Devuelve el stylesheet QSS completo para el tema indicado."""
    nombre = tema if tema in PALETAS_TEMAS else TEMA_POR_DEFECTO
    return _QSS_TEMPLATE % PALETAS_TEMAS[nombre]


# Estilos ya resueltos (compatibilidad con importaciones previas).
TEMAS: Dict[str, str] = {nombre: construir_qss(nombre) for nombre in PALETAS_TEMAS}

LIGHT_QSS = TEMAS[TEMA_POR_DEFECTO]
DARK_QSS = TEMAS["Grafito Pro"]


def es_tema_oscuro(tema: str) -> bool:
    return tema in TEMAS_OSCUROS


def nombre_tema(tema: str) -> str:
    return tema if tema in PALETAS_TEMAS else TEMA_POR_DEFECTO


class GestorTemas:
    """Gestor limpio y centralizado de los temas de la aplicación.

    Encapsula la lista, el tema actual y la generación del stylesheet. Si se
    provee un objeto con ``get(seccion, clave, default)`` y ``set(...)``
    (como ``ConfigManager``), el gestor también lee y persiste la elección.
    """

    def __init__(self, config: Optional[object] = None) -> None:
        self._config = config
        self._actual: Optional[str] = None

    # --- Lectura ---
    def lista(self) -> List[str]:
        return list(TEMAS_ORDEN)

    def _leer(self) -> str:
        if self._config is not None:
            try:
                valor = self._config.get("apariencia", "tema", TEMA_POR_DEFECTO)
                return str(valor) if valor else TEMA_POR_DEFECTO
            except Exception:
                pass
        return TEMA_POR_DEFECTO

    def actual(self) -> str:
        if self._actual is None:
            self._actual = nombre_tema(self._leer())
        return self._actual

    def es_oscuro(self, tema: Optional[str] = None) -> bool:
        return es_tema_oscuro(tema or self.actual())

    def qss(self, tema: Optional[str] = None) -> str:
        return construir_qss(tema or self.actual())

    # --- Aplicación ---
    def aplicar(self, widget) -> None:
        """Aplica el stylesheet al widget (por ejemplo, la ventana principal)."""
        widget.setStyleSheet(self.qss())

    def seleccionar(self, nombre: str) -> bool:
        """Cambia el tema actual y lo persiste, si hay configuración.

        Devuelve ``True`` si el cambio fue efectivo.
        """
        nombre = nombre_tema(nombre)
        if nombre == self.actual():
            return False
        self._actual = nombre
        if self._config is not None:
            try:
                self._config.set("apariencia", "tema", nombre)
                self._config.save()
            except Exception:
                pass
        return True
