"""
Stile UI workbench — ispirato a FurnitureAI-Professional (toolbar a pannelli, dialog scuro).
"""

WIZARD_STYLESHEET = """
QDialog, QWidget {
    background-color: #2b2b2b;
    color: #e8e8e8;
    font-family: "Segoe UI", sans-serif;
    font-size: 9pt;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: #7eb8da;
}
QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 4px;
    color: #f0f0f0;
}
QPushButton {
    background-color: #3d6b8e;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover { background-color: #4d7b9e; }
QCheckBox { spacing: 6px; }
"""


def apply_wizard_style(dialog) -> None:
    """Applica foglio di stile al dialog wizard."""
    try:
        dialog.setStyleSheet(WIZARD_STYLESHEET)
    except Exception:
        pass
