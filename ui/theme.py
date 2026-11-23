DARK_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #0b1120;
    color: #e2e8f0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QFrame#Sidebar {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}

QFrame#Card {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
}

QLabel {
    background-color: transparent;
    color: #e2e8f0;
}

QLabel#Title {
    font-size: 19px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#BrandTitle {
    font-size: 16px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#Subtitle {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#MetricValue {
    font-size: 21px;
    font-weight: 700;
    color: #38bdf8;
}

QLabel#FolioBadge {
    font-size: 14px;
    font-weight: 700;
    color: #f8fafc;
}

QPushButton {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 7px;
    padding: 7px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #2563eb;
    border-color: #3b82f6;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #1d4ed8;
}

QPushButton#PrimaryBtn {
    background-color: #2563eb;
    border-color: #3b82f6;
    color: #ffffff;
}

QPushButton#PrimaryBtn:hover {
    background-color: #3b82f6;
}

QPushButton#NavBtn {
    text-align: left;
    padding: 10px 14px;
    background-color: transparent;
    color: #cbd5e1;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

QPushButton#NavBtn:hover {
    background-color: #1e293b;
    color: #ffffff;
}

QPushButton#NavBtn[active="true"] {
    background-color: #2563eb;
    color: #ffffff;
}

QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QDoubleSpinBox, QSpinBox {
    background-color: #090e1a;
    color: #f8fafc;
    border: 1px solid #283548;
    border-radius: 6px;
    padding: 6px 10px;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 22px;
}

QTableWidget {
    background-color: #090e1a;
    alternate-background-color: #0f172a;
    color: #e2e8f0;
    gridline-color: #1e293b;
    border: 1px solid #1f2937;
    border-radius: 8px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #111827;
    color: #f1f5f9;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #1e293b;
    border-bottom: 1px solid #334155;
    font-weight: 700;
}

QTabWidget::pane {
    border: 1px solid #1f2937;
    border-radius: 8px;
    background-color: #0b1120;
}

QTabBar::tab {
    background-color: #111827;
    color: #94a3b8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 700;
}
"""

LIGHT_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
}

QLabel {
    background-color: transparent;
    color: #0f172a;
}

QLabel#Title {
    font-size: 19px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#BrandTitle {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#Subtitle {
    font-size: 12px;
    color: #475569;
}

QLabel#MetricValue {
    font-size: 21px;
    font-weight: 700;
    color: #0284c7;
}

QLabel#FolioBadge {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
}

QPushButton {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 7px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #2563eb;
    border-color: #2563eb;
    color: #ffffff;
}

QPushButton#PrimaryBtn {
    background-color: #2563eb;
    border-color: #2563eb;
    color: #ffffff;
}

QPushButton#NavBtn {
    text-align: left;
    padding: 10px 14px;
    background-color: transparent;
    color: #334155;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

QPushButton#NavBtn:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}

QPushButton#NavBtn[active="true"] {
    background-color: #2563eb;
    color: #ffffff;
}

QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QDoubleSpinBox, QSpinBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #2563eb;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f1f5f9;
    color: #0f172a;
    gridline-color: #e2e8f0;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #cbd5e1;
    font-weight: 700;
}

QTabWidget::pane {
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background-color: #f8fafc;
}

QTabBar::tab {
    background-color: #e2e8f0;
    color: #334155;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 700;
}
"""
