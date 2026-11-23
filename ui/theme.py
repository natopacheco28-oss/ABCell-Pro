DARK_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QFrame#Sidebar {
    background-color: #111827;
    border-right: 1px solid #1f2937;
}

QFrame#Card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
}

QLabel#Title {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#Subtitle {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#MetricValue {
    font-size: 22px;
    font-weight: 700;
    color: #38bdf8;
}

QPushButton {
    background-color: #1e293b;
    color: #e2e8f0;
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

QPushButton#NavBtn {
    text-align: left;
    padding: 10px 14px;
    background-color: transparent;
    border: none;
    border-radius: 8px;
}

QPushButton#NavBtn:hover, QPushButton#NavBtn[active="true"] {
    background-color: #1d4ed8;
    color: #ffffff;
}

QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QDoubleSpinBox, QSpinBox {
    background-color: #0b1120;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #38bdf8;
}

QTableWidget {
    background-color: #0b1120;
    alternate-background-color: #111827;
    color: #e2e8f0;
    gridline-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}

QHeaderView::section {
    background-color: #1e293b;
    color: #f8fafc;
    padding: 7px;
    border: none;
    border-bottom: 1px solid #334155;
    font-weight: 700;
}

QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 8px;
    background-color: #0f172a;
}

QTabBar::tab {
    background-color: #1e293b;
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

QLabel#Title {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#Subtitle {
    font-size: 12px;
    color: #475569;
}

QLabel#MetricValue {
    font-size: 22px;
    font-weight: 700;
    color: #0284c7;
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

QPushButton#NavBtn {
    text-align: left;
    padding: 10px 14px;
    background-color: transparent;
    border: none;
    border-radius: 8px;
}

QPushButton#NavBtn:hover, QPushButton#NavBtn[active="true"] {
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

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #2563eb;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f1f5f9;
    color: #0f172a;
    gridline-color: #e2e8f0;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 7px;
    border: none;
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
