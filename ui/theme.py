"""Sistema de temas de la aplicación.

Cada tema se define como un diccionario de colores (paleta) que se expande
en un stylesheet QSS completo mediante _QSS_TEMPLATE. Agregar un nuevo tema
solo requiere añadir una entrada a PALETAS_TEMAS.

El tema por defecto es "Claro" (modo claro).
"""

_QSS_TEMPLATE = """
QMainWindow, QDialog, QWidget {
    background-color: %(bg)s;
    color: %(fg)s;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

QFrame#Sidebar {
    background-color: %(sidebar_bg)s;
    border-right: 1px solid %(sidebar_border)s;
}

QFrame#Card {
    background-color: %(card_bg)s;
    border: 1px solid %(card_border)s;
    border-radius: 14px;
}

QFrame#SubBar {
    background-color: %(card_bg)s;
    border: 1px solid %(card_border)s;
    border-radius: 12px;
}

QLabel {
    background-color: transparent;
    color: %(label_fg)s;
}

QLabel#Title {
    font-size: 21px;
    font-weight: 700;
    color: %(title)s;
}

QLabel#Breadcrumb {
    font-size: 12px;
    color: %(breadcrumb)s;
}

QLabel#BrandTitle {
    font-size: 18px;
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
    font-size: 19px;
    font-weight: 700;
    color: %(metric)s;
}

QLabel#FolioBadge {
    font-size: 13px;
    font-weight: 700;
    color: %(folio)s;
}

QPushButton {
    background-color: %(btn_bg)s;
    color: %(btn_fg)s;
    border: 1px solid %(btn_border)s;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: %(btn_hover_bg)s;
    border-color: %(btn_hover_border)s;
    color: %(btn_hover_fg)s;
}

QPushButton#PrimaryBtn {
    background-color: %(primary_bg)s;
    border-color: %(primary_border)s;
    color: %(primary_fg)s;
    font-weight: 700;
}

QPushButton#PrimaryBtn:hover {
    background-color: %(primary_hover_bg)s;
    border-color: %(primary_hover_border)s;
    color: %(primary_fg)s;
}

QPushButton#GearBtn {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 8px;
}

QPushButton#GearBtn:hover {
    background-color: %(gear_hover_bg)s;
}

QPushButton#NavBtn {
    text-align: left;
    padding: 12px 16px;
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

QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QDoubleSpinBox, QSpinBox {
    background-color: %(input_bg)s;
    color: %(input_fg)s;
    border: 1px solid %(input_border)s;
    border-radius: 10px;
    padding: 9px 14px;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid %(input_focus)s;
}

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
}

QHeaderView::section {
    background-color: %(header_bg)s;
    color: %(header_fg)s;
    padding: 12px 14px;
    border: none;
    border-bottom: 1px solid %(header_border)s;
    font-size: 11px;
    font-weight: 700;
}

QTabWidget::pane {
    border: 1px solid %(table_border)s;
    border-radius: 12px;
    background-color: %(card_bg)s;
}

QTabBar::tab {
    background-color: %(tab_bg)s;
    color: %(tab_fg)s;
    padding: 9px 18px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 6px;
}

QTabBar::tab:selected {
    background-color: %(tab_sel_bg)s;
    color: %(tab_sel_fg)s;
    font-weight: 700;
}
"""

# --------------------------------------------------------------------------
# Paletas de colores por tema
# --------------------------------------------------------------------------
PALETAS_TEMAS = {
    "Claro": {
        "bg": "#f4f6f9",
        "fg": "#1e293b",
        "sidebar_bg": "#ffffff",
        "sidebar_border": "#e2e8f0",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "label_fg": "#334155",
        "title": "#0f172a",
        "breadcrumb": "#64748b",
        "brand": "#0f172a",
        "cardtitle": "#0f172a",
        "cardsub": "#64748b",
        "cardlink": "#0284c7",
        "metric": "#0284c7",
        "folio": "#0f172a",
        "btn_bg": "#ffffff",
        "btn_fg": "#334155",
        "btn_border": "#cbd5e1",
        "btn_hover_bg": "#f1f5f9",
        "btn_hover_border": "#0284c7",
        "btn_hover_fg": "#0284c7",
        "primary_bg": "#0284c7",
        "primary_border": "#0284c7",
        "primary_hover_bg": "#0369a1",
        "primary_hover_border": "#0369a1",
        "primary_fg": "#ffffff",
        "gear_hover_bg": "#f1f5f9",
        "nav_fg": "#475569",
        "nav_hover_bg": "#f0f9ff",
        "nav_hover_fg": "#0284c7",
        "nav_active_bg": "#e0f2fe",
        "nav_active_fg": "#0284c7",
        "nav_active_border": "#0284c7",
        "stage_fg": "#64748b",
        "stage_hover": "#0284c7",
        "stage_active": "#0284c7",
        "stage_active_border": "#0284c7",
        "input_bg": "#ffffff",
        "input_fg": "#0f172a",
        "input_border": "#cbd5e1",
        "input_focus": "#0284c7",
        "table_bg": "#ffffff",
        "table_alt": "#f8fafc",
        "grid": "#e2e8f0",
        "table_border": "#e2e8f0",
        "sel_bg": "#e0f2fe",
        "sel_fg": "#0369a1",
        "header_bg": "#ffffff",
        "header_fg": "#64748b",
        "header_border": "#e2e8f0",
        "tab_bg": "#e2e8f0",
        "tab_fg": "#475569",
        "tab_sel_bg": "#0284c7",
        "tab_sel_fg": "#ffffff",
    },
    "Oscuro": {
        "bg": "#0f172a",
        "fg": "#e2e8f0",
        "sidebar_bg": "#111827",
        "sidebar_border": "#1e293b",
        "card_bg": "#1e293b",
        "card_border": "#334155",
        "label_fg": "#e2e8f0",
        "title": "#f8fafc",
        "breadcrumb": "#94a3b8",
        "brand": "#f8fafc",
        "cardtitle": "#f8fafc",
        "cardsub": "#94a3b8",
        "cardlink": "#38bdf8",
        "metric": "#38bdf8",
        "folio": "#f8fafc",
        "btn_bg": "#1e293b",
        "btn_fg": "#f1f5f9",
        "btn_border": "#334155",
        "btn_hover_bg": "#2563eb",
        "btn_hover_border": "#3b82f6",
        "btn_hover_fg": "#ffffff",
        "primary_bg": "#0284c7",
        "primary_border": "#0284c7",
        "primary_hover_bg": "#0369a1",
        "primary_hover_border": "#0369a1",
        "primary_fg": "#ffffff",
        "gear_hover_bg": "#1e293b",
        "nav_fg": "#cbd5e1",
        "nav_hover_bg": "#1e293b",
        "nav_hover_fg": "#38bdf8",
        "nav_active_bg": "#0f2942",
        "nav_active_fg": "#38bdf8",
        "nav_active_border": "#38bdf8",
        "stage_fg": "#94a3b8",
        "stage_hover": "#38bdf8",
        "stage_active": "#38bdf8",
        "stage_active_border": "#38bdf8",
        "input_bg": "#0f172a",
        "input_fg": "#f8fafc",
        "input_border": "#334155",
        "input_focus": "#3b82f6",
        "table_bg": "#111827",
        "table_alt": "#0f172a",
        "grid": "#1e293b",
        "table_border": "#1f2937",
        "sel_bg": "#0284c7",
        "sel_fg": "#ffffff",
        "header_bg": "#1e293b",
        "header_fg": "#94a3b8",
        "header_border": "#334155",
        "tab_bg": "#0f172a",
        "tab_fg": "#94a3b8",
        "tab_sel_bg": "#0284c7",
        "tab_sel_fg": "#ffffff",
    },
    "Azul": {
        "bg": "#eef4fb",
        "fg": "#1e3a5f",
        "sidebar_bg": "#ffffff",
        "sidebar_border": "#dbeafe",
        "card_bg": "#ffffff",
        "card_border": "#dbeafe",
        "label_fg": "#334155",
        "title": "#0f172a",
        "breadcrumb": "#64748b",
        "brand": "#0f172a",
        "cardtitle": "#0f172a",
        "cardsub": "#64748b",
        "cardlink": "#1d4ed8",
        "metric": "#1d4ed8",
        "folio": "#0f172a",
        "btn_bg": "#ffffff",
        "btn_fg": "#1e3a5f",
        "btn_border": "#bfdbfe",
        "btn_hover_bg": "#eff6ff",
        "btn_hover_border": "#1d4ed8",
        "btn_hover_fg": "#1d4ed8",
        "primary_bg": "#1d4ed8",
        "primary_border": "#1d4ed8",
        "primary_hover_bg": "#1e40af",
        "primary_hover_border": "#1e40af",
        "primary_fg": "#ffffff",
        "gear_hover_bg": "#eff6ff",
        "nav_fg": "#475569",
        "nav_hover_bg": "#eff6ff",
        "nav_hover_fg": "#1d4ed8",
        "nav_active_bg": "#dbeafe",
        "nav_active_fg": "#1d4ed8",
        "nav_active_border": "#1d4ed8",
        "stage_fg": "#64748b",
        "stage_hover": "#1d4ed8",
        "stage_active": "#1d4ed8",
        "stage_active_border": "#1d4ed8",
        "input_bg": "#ffffff",
        "input_fg": "#0f172a",
        "input_border": "#bfdbfe",
        "input_focus": "#1d4ed8",
        "table_bg": "#ffffff",
        "table_alt": "#f5f9ff",
        "grid": "#dbeafe",
        "table_border": "#dbeafe",
        "sel_bg": "#dbeafe",
        "sel_fg": "#1e40af",
        "header_bg": "#ffffff",
        "header_fg": "#64748b",
        "header_border": "#dbeafe",
        "tab_bg": "#dbeafe",
        "tab_fg": "#475569",
        "tab_sel_bg": "#1d4ed8",
        "tab_sel_fg": "#ffffff",
    },
}

# Orden en que aparecen los temas en el selector (el primero es el default).
TEMAS_ORDEN = ["Claro", "Oscuro", "Azul"]

TEMA_POR_DEFECTO = "Claro"

# Temas considerados "oscuros" (para decidir el color del icono, etc.).
TEMAS_OSCUROS = frozenset({"Oscuro"})


def construir_qss(tema: str) -> str:
    """Devuelve el stylesheet QSS completo para un tema dado."""
    nombre = tema if tema in PALETAS_TEMAS else TEMA_POR_DEFECTO
    return _QSS_TEMPLATE % PALETAS_TEMAS[nombre]


# Estilos ya resueltos (mantenidos para compatibilidad con importaciones previas).
TEMAS = {nombre: construir_qss(nombre) for nombre in PALETAS_TEMAS}

LIGHT_QSS = TEMAS["Claro"]
DARK_QSS = TEMAS["Oscuro"]


def es_tema_oscuro(tema: str) -> bool:
    return tema in TEMAS_OSCUROS
