"""
Dialog wizard mobili (PySide) per FreeCAD 1.1.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide import QtCore, QtGui as QtWidgets  # type: ignore

from furniture_core.models import FURNITURE_TYPES, default_params_for_type
from furniture_core.parser_nl import parse_description
from furniture_core.validation import validate_cabinet_params
from furniture_core.models import normalize_params


class FurnitureWizardDialog(QtWidgets.QDialog):
    """Wizard parametri mobile — campi allineati all'add-in Fusion."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FurnitureAI — Wizard mobili")
        self.resize(450, 520)
        self._result_params: Optional[Dict[str, Any]] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        self.combo_tipo = QtWidgets.QComboBox()
        self.combo_tipo.addItems(FURNITURE_TYPES)
        layout.addWidget(QtWidgets.QLabel("Tipo mobile"))
        layout.addWidget(self.combo_tipo)

        form = QtWidgets.QFormLayout()
        self.spin_l = self._spin(80, 20, 300)
        self.spin_h = self._spin(90, 20, 300)
        self.spin_p = self._spin(60, 20, 100)
        self.spin_sp = self._spin(1.8, 1.0, 5.0, step=0.1)
        self.spin_ss = self._spin(0.6, 0.3, 2.0, step=0.1)
        self.spin_ripiani = QtWidgets.QSpinBox()
        self.spin_ripiani.setRange(0, 10)
        self.spin_ripiani.setValue(2)

        form.addRow("Larghezza (cm)", self.spin_l)
        form.addRow("Altezza (cm)", self.spin_h)
        form.addRow("Profondità (cm)", self.spin_p)
        form.addRow("Spessore pannello (cm)", self.spin_sp)
        form.addRow("Spessore schienale (cm)", self.spin_ss)
        form.addRow("N. ripiani", self.spin_ripiani)
        layout.addLayout(form)

        self.chk_zoccolo = QtWidgets.QCheckBox("Zoccolo")
        self.chk_zoccolo.setChecked(True)
        self.spin_zoccolo = self._spin(10, 5, 20)
        layout.addWidget(self.chk_zoccolo)
        layout.addWidget(QtWidgets.QLabel("Altezza zoccolo (cm)"))
        layout.addWidget(self.spin_zoccolo)

        layout.addWidget(QtWidgets.QLabel("Descrizione (parser testuale)"))
        self.edit_desc = QtWidgets.QPlainTextEdit()
        self.edit_desc.setPlaceholderText(
            'Es: "mobile cucina largo 80cm alto 90cm con 2 ripiani e 2 ante"'
        )
        self.edit_desc.setMaximumHeight(80)
        layout.addWidget(self.edit_desc)

        btn_parse = QtWidgets.QPushButton("Applica descrizione")
        btn_parse.clicked.connect(self._on_parse_description)
        layout.addWidget(btn_parse)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.combo_tipo.currentTextChanged.connect(self._on_type_changed)

    @staticmethod
    def _spin(value: float, min_v: float, max_v: float, step: float = 1.0) -> QtWidgets.QDoubleSpinBox:
        w = QtWidgets.QDoubleSpinBox()
        w.setRange(min_v, max_v)
        w.setSingleStep(step)
        w.setDecimals(1)
        w.setValue(value)
        return w

    def _on_type_changed(self, tipo: str) -> None:
        defaults = default_params_for_type(tipo)
        self.spin_l.setValue(defaults["larghezza"])
        self.spin_h.setValue(defaults["altezza"])
        self.spin_p.setValue(defaults["profondita"])
        self.spin_ripiani.setValue(defaults["num_ripiani"])
        self.chk_zoccolo.setChecked(bool(defaults.get("con_zoccolo", False)))

    def _on_parse_description(self) -> None:
        text = self.edit_desc.toPlainText().strip()
        if not text:
            return
        parsed = parse_description(text, self.combo_tipo.currentText())
        self.spin_l.setValue(parsed["larghezza"])
        self.spin_h.setValue(parsed["altezza"])
        self.spin_p.setValue(parsed["profondita"])
        self.spin_ripiani.setValue(parsed["num_ripiani"])
        self.chk_zoccolo.setChecked(parsed.get("con_zoccolo", False))

    def _collect_params(self) -> Dict[str, Any]:
        return normalize_params(
            {
                "tipo_mobile": self.combo_tipo.currentText(),
                "larghezza": self.spin_l.value(),
                "altezza": self.spin_h.value(),
                "profondita": self.spin_p.value(),
                "spessore_pannello": self.spin_sp.value(),
                "spessore_schienale": self.spin_ss.value(),
                "num_ripiani": self.spin_ripiani.value(),
                "con_zoccolo": self.chk_zoccolo.isChecked(),
                "altezza_zoccolo": self.spin_zoccolo.value(),
            }
        )

    def _on_accept(self) -> None:
        params = self._collect_params()
        errors = validate_cabinet_params(params)
        if errors:
            QtWidgets.QMessageBox.warning(self, "FurnitureAI", "\n".join(errors))
            return
        self._result_params = params
        self.accept()

    def get_params(self) -> Optional[Dict[str, Any]]:
        return self._result_params
