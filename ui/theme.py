"""Identidad global ABCell: superficies oscuras, lima y acciones semánticas.

QSS compartido por QApplication, incluidas las ventanas secundarias. Las
medidas son lógicas (HiDPI). Los tamaños de contenido se calculan en layouts.py.
"""
from typing import Dict, List, Optional

TEMA_POR_DEFECTO = "Lima Pro"
_BASE = {
    "bg": "#0c111b", "fg": "#edf2f7", "sidebar_bg": "#101722",
    "sidebar_border": "#273344", "card_bg": "#151e2c", "subcard_bg": "#1a2636",
    "card_border": "#2b394c", "label_fg": "#dce4ee", "cardsub": "#a8b7ca",
    "title": "#f6f9fc", "brand": "#c5f467", "metric": "#c5f467",
    "accent": "#c5f467", "accent_soft": "#253623", "accent_border": "#66883c",
    "btn_bg": "#1d2a3b", "btn_fg": "#edf2f7", "btn_border": "#3c5068",
    "btn_hover_bg": "#2a3c50", "primary_bg": "#c5f467", "primary_fg": "#14200b",
    "primary_hover_bg": "#d7ff8a", "secondary_fg": "#edf2f7",
    "danger_bg": "#692f3c", "danger_fg": "#fff0f2", "danger_border": "#b75b6e",
    "danger_hover_bg": "#873b4c", "nav_fg": "#b9c6d8", "nav_active_bg": "#253623",
    "nav_active_fg": "#d4ff89", "stage_fg": "#b9c6d8", "stage_active": "#d4ff89",
    "icon": "#c2cfdf", "input_bg": "#0f1826", "input_fg": "#f0f5fa",
    "input_border": "#3b5069", "table_bg": "#131d2b", "table_alt": "#182434",
    "header_bg": "#202e40", "header_fg": "#c3d1e2", "sel_bg": "#2a4329",
    "sel_fg": "#e4ffc6", "warning_bg": "#f5b84b", "warning_fg": "#271a05",
}

# Seis variantes oscuras, todas con la misma jerarquía y el acento lima.
PALETAS_TEMAS: Dict[str, Dict[str, str]] = {
    "Lima Pro": dict(_BASE),
    "Grafito Pro": {**_BASE, "bg": "#101419", "card_bg": "#1b222b", "sidebar_bg": "#151a21"},
    "Midnight Slate": {**_BASE, "bg": "#090f1d", "card_bg": "#131f35", "sidebar_bg": "#0d1628"},
    "Esmeralda Oscura": {**_BASE, "bg": "#0b1616", "card_bg": "#142727", "sidebar_bg": "#0e1e1e"},
    "Carbón": {**_BASE, "bg": "#101112", "card_bg": "#202326", "sidebar_bg": "#16191b"},
    "Pizarra": {**_BASE, "bg": "#141b26", "card_bg": "#202d3e", "sidebar_bg": "#182231"},
}
TEMAS_ORDEN: List[str] = list(PALETAS_TEMAS)
TEMAS_OSCUROS = frozenset(TEMAS_ORDEN)
_ALIASES = {"Mostrador Limpio": "Lima Pro", "Laboratorio Minimal": "Lima Pro",
            "Arena Suave": "Lima Pro", "Placa Madre Emerald": "Esmeralda Oscura",
            "Claro": "Lima Pro", "Oscuro": "Lima Pro", "Azul": "Midnight Slate"}

_QSS = """
QWidget {
    background: %(bg)s; color: %(fg)s;
    font-family: "Segoe UI", "Noto Sans", "DejaVu Sans", sans-serif; font-size: 14px;
    selection-background-color: %(sel_bg)s; selection-color: %(sel_fg)s;
}
QMainWindow, QDialog, QMessageBox, QInputDialog { background: %(bg)s; }
QLabel { background: transparent; color: %(label_fg)s; border: none; padding: 1px 0; }
QLabel#Title { font-size: 24px; font-weight: 700; color: %(title)s; padding: 4px 0 8px; }
QLabel#BrandTitle { font-size: 19px; font-weight: 700; color: %(brand)s; }
QLabel#CardTitle { font-size: 16px; font-weight: 600; color: %(title)s; }
QLabel#CardSub, QLabel#Breadcrumb { color: %(cardsub)s; font-size: 13px; }
QLabel#MetricValue { color: %(metric)s; font-size: 25px; font-weight: 700; padding: 6px 0; }
QLabel#FolioBadge { color: %(accent)s; font-size: 15px; font-weight: 600; }
QFrame#Sidebar { background: %(sidebar_bg)s; border-right: 1px solid %(sidebar_border)s; }
QFrame#Card, QFrame#Panel { background: %(card_bg)s; border: 1px solid %(card_border)s; border-radius: 14px; }
QFrame#SubBar { background: %(subcard_bg)s; border: 1px solid %(card_border)s; border-radius: 12px; }
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: %(bg)s; }
QPushButton {
    background: %(btn_bg)s; color: %(btn_fg)s; border: 1px solid %(btn_border)s;
    border-radius: 9px; padding: 10px 18px; min-height: 22px; font-size: 14px; font-weight: 600;
}
QPushButton:hover { background: %(btn_hover_bg)s; border-color: %(accent_border)s; }
QPushButton:pressed { background: %(accent_soft)s; border-color: %(accent)s; }
QPushButton:focus { border: 2px solid %(accent)s; padding: 9px 17px; }
QPushButton:disabled { background: #202b39; color: #93a2b5; border-color: #344153; }
QPushButton#PrimaryBtn { background: %(primary_bg)s; color: %(primary_fg)s; border-color: %(primary_bg)s; }
QPushButton#PrimaryBtn:hover { background: %(primary_hover_bg)s; border-color: %(primary_hover_bg)s; }
QPushButton#WarningBtn { background: %(warning_bg)s; color: %(warning_fg)s; border-color: %(warning_bg)s; }
QPushButton#WarningBtn:hover { background: #ffd088; border-color: #ffd088; }
QPushButton#DangerBtn, QPushButton#AccDangerBtn {
    background: %(danger_bg)s; color: %(danger_fg)s; border-color: %(danger_border)s;
}
QPushButton#DangerBtn:hover, QPushButton#AccDangerBtn:hover { background: %(danger_hover_bg)s; }
QPushButton#NavBtn { text-align: left; background: transparent; color: %(nav_fg)s; border-color: transparent; padding: 12px 16px; }
QPushButton#NavBtn:hover { background: %(subcard_bg)s; border-color: %(card_border)s; }
QPushButton#NavBtn[active="true"] { background: %(nav_active_bg)s; color: %(nav_active_fg)s; border-color: %(accent_border)s; }
QPushButton#StageTab { color: %(stage_fg)s; background: %(card_bg)s; }
QPushButton#StageTab[active="true"] { color: %(primary_fg)s; background: %(primary_bg)s; border-color: %(primary_bg)s; }
QPushButton#IconBtn, QPushButton#GearBtn { padding: 10px; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
    background: %(input_bg)s; color: %(input_fg)s; border: 1px solid %(input_border)s;
    border-radius: 8px; padding: 10px 12px; min-height: 22px; font-size: 14px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QTextEdit:focus, QPlainTextEdit:focus { border: 2px solid %(accent)s; padding: 9px 11px; }
QLineEdit:disabled, QComboBox:disabled { color: #93a2b5; background: #202b39; }
QComboBox { padding-right: 36px; }
QComboBox:focus { padding-right: 35px; }
QComboBox::drop-down { width: 30px; border: none; background: transparent; }
QComboBox::down-arrow { image: none; width: 0; height: 0; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid %(accent)s; }
QComboBox QAbstractItemView { background: %(card_bg)s; color: %(input_fg)s; border: 1px solid %(input_border)s; padding: 6px; selection-background-color: %(sel_bg)s; selection-color: %(sel_fg)s; }
QComboBox QAbstractItemView::item { padding: 10px; min-height: 24px; }
QSpinBox::up-button, QDoubleSpinBox::up-button { width: 24px; border: none; }
QSpinBox::down-button, QDoubleSpinBox::down-button { width: 24px; border: none; }
QTableWidget, QTableView {
    background: %(table_bg)s; alternate-background-color: %(table_alt)s; color: %(fg)s;
    border: 1px solid %(card_border)s; border-radius: 8px; gridline-color: %(card_border)s;
    selection-background-color: %(sel_bg)s; selection-color: %(sel_fg)s;
}
QTableWidget::item { padding: 10px 12px; border-bottom: 1px solid %(card_border)s; }
QTableWidget::item:selected { background: %(sel_bg)s; color: %(sel_fg)s; }
QHeaderView { background: %(header_bg)s; }
QHeaderView::section { background: %(header_bg)s; color: %(header_fg)s; font-size: 12px; font-weight: 700; padding: 14px 12px; border: none; border-bottom: 1px solid %(card_border)s; border-right: 1px solid %(card_border)s; }
QTableCornerButton::section { background: %(header_bg)s; border: none; }
QTabWidget::pane { background: %(card_bg)s; border: 1px solid %(card_border)s; border-radius: 10px; top: -1px; }
QTabBar::tab { background: %(subcard_bg)s; color: %(cardsub)s; padding: 14px 20px; margin: 0 6px 6px 0; border: 1px solid %(card_border)s; border-radius: 8px; min-height: 22px; }
QTabBar::tab:selected { background: %(accent_soft)s; color: %(accent)s; border-color: %(accent_border)s; }
QTabBar::tab:hover { color: %(fg)s; }
QMenu { background: %(card_bg)s; color: %(fg)s; border: 1px solid %(input_border)s; padding: 8px; }
QMenu::item { padding: 12px 32px; min-height: 22px; border-radius: 6px; }
QMenu::item:selected { background: %(sel_bg)s; color: %(sel_fg)s; }
QToolTip { background: %(subcard_bg)s; color: %(fg)s; border: 1px solid %(input_border)s; padding: 10px; }
QScrollBar:vertical { background: %(bg)s; width: 14px; margin: 0; }
QScrollBar:horizontal { background: %(bg)s; height: 14px; margin: 0; }
QScrollBar::handle { background: #52657b; border-radius: 6px; min-width: 32px; min-height: 32px; }
QScrollBar::handle:hover { background: #799164; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QCheckBox { spacing: 10px; color: %(fg)s; padding: 6px; }
QCheckBox::indicator { width: 22px; height: 22px; border: 1px solid %(input_border)s; background: %(input_bg)s; border-radius: 5px; }
QCheckBox::indicator:checked { background: %(accent)s; border-color: %(accent)s; }
QGroupBox { border: 1px solid %(card_border)s; border-radius: 10px; margin-top: 16px; padding: 18px; }
QGroupBox::title { color: %(accent)s; subcontrol-origin: margin; left: 16px; padding: 0 6px; }
"""


def nombre_tema(tema: str) -> str:
    tema = _ALIASES.get(tema, tema)
    return tema if tema in PALETAS_TEMAS else TEMA_POR_DEFECTO


def construir_qss(tema: str) -> str:
    return _QSS % PALETAS_TEMAS[nombre_tema(tema)]


def es_tema_oscuro(tema: str) -> bool:
    return True


TEMAS = {nombre: construir_qss(nombre) for nombre in TEMAS_ORDEN}
LIGHT_QSS = DARK_QSS = TEMAS[TEMA_POR_DEFECTO]  # Compatibilidad de imports anteriores.


class GestorTemas:
    def __init__(self, config: Optional[object] = None) -> None:
        self._config = config
        self._actual = None

    def lista(self) -> List[str]:
        return list(TEMAS_ORDEN)

    def actual(self) -> str:
        if self._actual is None:
            valor = self._config.get("apariencia", "tema", TEMA_POR_DEFECTO) if self._config else TEMA_POR_DEFECTO
            self._actual = nombre_tema(str(valor))
        return self._actual

    def es_oscuro(self, tema=None) -> bool:
        return True

    def qss(self, tema=None) -> str:
        return construir_qss(tema or self.actual())

    def aplicar(self, widget) -> None:
        widget.setStyleSheet(self.qss())

    def seleccionar(self, nombre: str) -> bool:
        nombre = nombre_tema(nombre)
        if nombre == self.actual():
            return False
        self._actual = nombre
        if self._config:
            self._config.set("apariencia", "tema", nombre)
            self._config.save()
        return True
