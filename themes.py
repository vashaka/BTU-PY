# Centralized light/dark themes for the PyQt app

LIGHT = """
QMainWindow, QWidget#root {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #b8fffd, stop:1 #ffbad3);
    color: #0f172a;
}

QScrollArea, QScrollArea > QWidget > QWidget {
    background: transparent;
    border: none;
}

QLabel[role="pageTitle"] {
    font-size: 32px;
    font-weight: bold;
    color: #0f172a;
    margin-bottom: 8px;
}

QLabel[role="sectionTitle"] {
    font-size: 13px;
    font-weight: bold;
    color: #111827;
    margin-top: 4px;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 4px;
}

QLabel[role="muted"] {
    color: #6b7280;
    font-size: 13px;
}

QLabel[role="error"] {
    color: #dc2626;
    font-size: 13px;
    font-weight: bold;
}

QLabel[role="success"] {
    color: #0d9488;
    font-size: 11px;
    font-weight: bold;
}

QLabel[role="stat"] {
    font-size: 14px;
    font-weight: bold;
    color: #0d9488;
}

QLabel[role="substat"] {
    font-size: 13px;
    color: #374151;
}

QLabel[role="avatar"] {
    border: 2px solid #0d9488;
    border-radius: 40px;
    background-color: #f1f5f9;
    color: #94a3b8;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #99f6e4;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 2px solid #0d9488;
}

QLineEdit:read-only {
    background-color: #f8fafc;
    color: #475569;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #d1d5db;
    selection-background-color: #ccfbf1;
    selection-color: #0f766e;
}

QListWidget {
    background-color: #f8fafc;
    color: #0f172a;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 4px;
    font-size: 12px;
}

QListWidget::item {
    padding: 6px 8px;
    border-radius: 6px;
}

QListWidget::item:selected {
    background-color: #ccfbf1;
    color: #0f766e;
}

QTableWidget {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    gridline-color: #e5e7eb;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    border: none;
    border-bottom: 1px solid #e5e7eb;
    padding: 6px;
    font-weight: bold;
    font-size: 12px;
}

QProgressBar {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background: #f1f5f9;
    height: 14px;
    text-align: center;
}

QProgressBar::chunk {
    background: #0d9488;
    border-radius: 5px;
}

QPushButton {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #f1f5f9;
}

QPushButton:disabled {
    background-color: #f3f4f6;
    color: #9ca3af;
    border-color: #e5e7eb;
}

QPushButton[btnRole="primary"] {
    background-color: #0d9488;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 14px;
}

QPushButton[btnRole="primary"]:hover {
    background-color: #0f766e;
}

QPushButton[btnRole="primary"]:disabled {
    background-color: #99f6e4;
    color: #ffffff;
}

QPushButton[btnRole="secondary"] {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #d1d5db;
    font-size: 12px;
    padding: 7px 12px;
}

QPushButton[btnRole="secondary"]:hover {
    background-color: #f8fafc;
    border-color: #0d9488;
}

QPushButton[btnRole="danger"] {
    background-color: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
    font-size: 12px;
}

QPushButton[btnRole="danger"]:hover {
    background-color: #fee2e2;
}

QPushButton[btnRole="ghost"] {
    background: transparent;
    border: none;
    color: #6b7280;
    font-size: 12px;
    font-weight: bold;
    padding: 4px 8px;
}

QPushButton[btnRole="ghost"]:hover {
    color: #dc2626;
}

QPushButton[btnRole="link"] {
    background: transparent;
    border: none;
    color: #0d9488;
    font-size: 13px;
    font-weight: bold;
    padding: 2px 6px;
}

QPushButton[btnRole="link"]:hover {
    color: #0f766e;
}

QPushButton[btnRole="chip"] {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #d1d5db;
    border-radius: 12px;
    font-size: 11px;
    padding: 5px 12px;
}

QPushButton[btnRole="chip"]:hover {
    background-color: #f0fdfa;
    border-color: #0d9488;
}

QPushButton[btnRole="chipActive"] {
    background-color: #0d9488;
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-size: 11px;
    padding: 5px 12px;
}
"""

DARK = """
QMainWindow, QWidget#root {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0f172a, stop:1 #1e1b4b);
    color: #f1f5f9;
}

QScrollArea, QScrollArea > QWidget > QWidget {
    background: transparent;
    border: none;
}

QLabel[role="pageTitle"] {
    font-size: 32px;
    font-weight: bold;
    color: #f8fafc;
    margin-bottom: 8px;
}

QLabel[role="sectionTitle"] {
    font-size: 13px;
    font-weight: bold;
    color: #e2e8f0;
    margin-top: 4px;
    border-bottom: 1px solid #334155;
    padding-bottom: 4px;
}

QLabel[role="muted"] {
    color: #94a3b8;
    font-size: 13px;
}

QLabel[role="error"] {
    color: #f87171;
    font-size: 13px;
    font-weight: bold;
}

QLabel[role="success"] {
    color: #2dd4bf;
    font-size: 11px;
    font-weight: bold;
}

QLabel[role="stat"] {
    font-size: 14px;
    font-weight: bold;
    color: #2dd4bf;
}

QLabel[role="substat"] {
    font-size: 13px;
    color: #cbd5e1;
}

QLabel[role="avatar"] {
    border: 2px solid #2dd4bf;
    border-radius: 40px;
    background-color: #1e293b;
    color: #64748b;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #475569;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #134e4a;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 2px solid #2dd4bf;
}

QLineEdit:read-only {
    background-color: #0f172a;
    color: #94a3b8;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #475569;
    selection-background-color: #134e4a;
    selection-color: #5eead4;
}

QListWidget {
    background-color: #0f172a;
    color: #f1f5f9;
    border: 1px solid #475569;
    border-radius: 10px;
    padding: 4px;
    font-size: 12px;
}

QListWidget::item {
    padding: 6px 8px;
    border-radius: 6px;
}

QListWidget::item:selected {
    background-color: #134e4a;
    color: #5eead4;
}

QTableWidget {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #475569;
    border-radius: 10px;
    gridline-color: #334155;
}

QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    border: none;
    border-bottom: 1px solid #334155;
    padding: 6px;
    font-weight: bold;
    font-size: 12px;
}

QProgressBar {
    border: 1px solid #475569;
    border-radius: 6px;
    background: #0f172a;
    height: 14px;
}

QProgressBar::chunk {
    background: #2dd4bf;
    border-radius: 5px;
}

QPushButton {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #475569;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #334155;
}

QPushButton:disabled {
    background-color: #1e293b;
    color: #64748b;
    border-color: #334155;
}

QPushButton[btnRole="primary"] {
    background-color: #14b8a6;
    color: #0f172a;
    border: none;
    font-weight: bold;
}

QPushButton[btnRole="primary"]:hover {
    background-color: #2dd4bf;
}

QPushButton[btnRole="secondary"] {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #475569;
    font-size: 12px;
}

QPushButton[btnRole="secondary"]:hover {
    background-color: #334155;
    border-color: #2dd4bf;
}

QPushButton[btnRole="danger"] {
    background-color: #450a0a;
    color: #fca5a5;
    border: 1px solid #7f1d1d;
    font-size: 12px;
}

QPushButton[btnRole="danger"]:hover {
    background-color: #7f1d1d;
}

QPushButton[btnRole="ghost"] {
    background: transparent;
    border: none;
    color: #94a3b8;
    font-size: 12px;
    padding: 4px 8px;
}

QPushButton[btnRole="ghost"]:hover {
    color: #f87171;
}

QPushButton[btnRole="link"] {
    background: transparent;
    border: none;
    color: #2dd4bf;
    font-size: 13px;
    font-weight: bold;
}

QPushButton[btnRole="link"]:hover {
    color: #5eead4;
}

QPushButton[btnRole="chip"] {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #475569;
    border-radius: 12px;
    font-size: 11px;
    padding: 5px 12px;
}

QPushButton[btnRole="chip"]:hover {
    background-color: #334155;
    border-color: #2dd4bf;
}

QPushButton[btnRole="chipActive"] {
    background-color: #14b8a6;
    color: #0f172a;
    border: none;
    border-radius: 12px;
    font-size: 11px;
    padding: 5px 12px;
}
"""


def get_stylesheet(dark=False):
    return DARK if dark else LIGHT


def apply_theme(app_or_window, dark=False):
    stylesheet = get_stylesheet(dark)
    app_or_window.setStyleSheet(stylesheet)
