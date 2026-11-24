LIGHT_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #f4f6f9;
    color: #1e293b;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
}

QFrame#SubBar {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

QLabel {
    background-color: transparent;
    color: #334155;
}

QLabel#Title {
    font-size: 21px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#Breadcrumb {
    font-size: 12px;
    color: #64748b;
}

QLabel#BrandTitle {
    font-size: 18px;
    font-weight: 800;
    color: #0f172a;
}

QLabel#CardTitle {
    font-size: 13px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#CardSub {
    font-size: 12px;
    color: #64748b;
}

QLabel#CardLink {
    font-size: 12px;
    font-weight: 700;
    color: #0284c7;
}

QLabel#MetricValue {
    font-size: 19px;
    font-weight: 700;
    color: #0284c7;
}

QLabel#FolioBadge {
    font-size: 13px;
    font-weight: 700;
    color: #0f172a;
}

QPushButton {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #0284c7;
    color: #0284c7;
}

QPushButton#PrimaryBtn {
    background-color: #0284c7;
    border-color: #0284c7;
    color: #ffffff;
    font-weight: 700;
}

QPushButton#PrimaryBtn:hover {
    background-color: #0369a1;
    border-color: #0369a1;
    color: #ffffff;
}

QPushButton#NavBtn {
    text-align: left;
    padding: 12px 16px;
    background-color: transparent;
    color: #475569;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 10px;
    font-weight: 600;
}

QPushButton#NavBtn:hover {
    background-color: #f0f9ff;
    color: #0284c7;
}

QPushButton#NavBtn[active="true"] {
    background-color: #e0f2fe;
    color: #0284c7;
    border-left: 3px solid #0284c7;
    font-weight: 700;
}

QPushButton#StageTab {
    background-color: transparent;
    color: #64748b;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton#StageTab:hover {
    color: #0284c7;
}

QPushButton#StageTab[active="true"] {
    color: #0284c7;
    border-bottom: 2px solid #0284c7;
    font-weight: 700;
}

QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QDoubleSpinBox, QSpinBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 9px 14px;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #0284c7;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    color: #1e293b;
    gridline-color: #e2e8f0;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    selection-background-color: #e0f2fe;
    selection-color: #0369a1;
}

QTableWidget::item {
    padding: 9px 12px;
}

QHeaderView::section {
    background-color: #ffffff;
    color: #64748b;
    padding: 12px 14px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-size: 11px;
    font-weight: 700;
}

QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #e2e8f0;
    color: #475569;
    padding: 9px 18px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 6px;
}

QTabBar::tab:selected {
    background-color: #0284c7;
    color: #ffffff;
    font-weight: 700;
}
"""

DARK_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

QFrame#Sidebar {
    background-color: #111827;
    border-right: 1px solid #1e293b;
}

QFrame#Card, QFrame#SubBar {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
}

QLabel {
    background-color: transparent;
    color: #e2e8f0;
}

QLabel#Title {
    font-size: 21px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#Breadcrumb {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#BrandTitle {
    font-size: 18px;
    font-weight: 800;
    color: #f8fafc;
}

QLabel#CardTitle {
    font-size: 13px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#CardSub {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#CardLink {
    font-size: 12px;
    font-weight: 700;
    color: #38bdf8;
}

QLabel#MetricValue {
    font-size: 19px;
    font-weight: 700;
    color: #38bdf8;
}

QLabel#FolioBadge {
    font-size: 13px;
    font-weight: 700;
    color: #f8fafc;
}

QPushButton {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #2563eb;
    border-color: #3b82f6;
    color: #ffffff;
}

QPushButton#PrimaryBtn {
    background-color: #0284c7;
    border-color: #0284c7;
    color: #ffffff;
    font-weight: 700;
}

QPushButton#PrimaryBtn:hover {
    background-color: #0369a1;
    color: #ffffff;
}

QPushButton#NavBtn {
    text-align: left;
    padding: 12px 16px;
    background-color: transparent;
    color: #cbd5e1;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 10px;
    font-weight: 600;
}

QPushButton#NavBtn:hover {
    background-color: #1e293b;
    color: #38bdf8;
}

QPushButton#NavBtn[active="true"] {
    background-color: #0f2942;
    color: #38bdf8;
    border-left: 3px solid #38bdf8;
    font-weight: 700;
}

QPushButton#StageTab {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton#StageTab[active="true"] {
    color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
    font-weight: 700;
}

QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QDoubleSpinBox, QSpinBox {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 9px 14px;
}

QTableWidget {
    background-color: #111827;
    alternate-background-color: #0f172a;
    color: #e2e8f0;
    gridline-color: #1e293b;
    border: 1px solid #1f2937;
    border-radius: 10px;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 9px 12px;
}

QHeaderView::section {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 12px 14px;
    border: none;
    border-bottom: 1px solid #334155;
    font-size: 11px;
    font-weight: 700;
}

QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 12px;
    background-color: #1e293b;
}

QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 9px 18px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 6px;
}

QTabBar::tab:selected {
    background-color: #0284c7;
    color: #ffffff;
    font-weight: 700;
}
"""
