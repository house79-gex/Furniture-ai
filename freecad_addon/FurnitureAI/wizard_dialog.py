"""
Dialog wizard mobili (PySide) per FreeCAD — campi allineati all'add-in Fusion.
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

SCHIENALE_TYPES = [
    "A filo dietro",
    "Incastrato (scanalatura 10mm)",
    "Arretrato custom",
]


class FurnitureWizardDialog(QtWidgets.QDialog):
    """Wizard parametri mobile — stessi gruppi logici del wizard Fusion."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FurnitureAI — Wizard mobili")
        self.resize(450, 620)
        self._result_params: Optional[Dict[str, Any]] = None
        self._build_ui()

    def _build_ui(self) -> None:
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)

        # --- Tipo mobile ---
        g_tipo = QtWidgets.QGroupBox("Tipo mobile")
        lt = QtWidgets.QVBoxLayout(g_tipo)
        self.combo_tipo = QtWidgets.QComboBox()
        self.combo_tipo.addItems(FURNITURE_TYPES)
        lt.addWidget(self.combo_tipo)
        layout.addWidget(g_tipo)

        # --- Dimensioni ---
        g_dim = QtWidgets.QGroupBox("Dimensioni (cm)")
        form = QtWidgets.QFormLayout(g_dim)
        self.spin_l = self._spin(80, 20, 300)
        self.spin_h = self._spin(90, 20, 300)
        self.spin_p = self._spin(60, 20, 100)
        self.spin_sp = self._spin(1.8, 1.0, 5.0, step=0.1)
        self.spin_ss = self._spin(0.6, 0.3, 2.0, step=0.1)
        self.spin_ripiani = QtWidgets.QSpinBox()
        self.spin_ripiani.setRange(0, 10)
        self.spin_ripiani.setValue(2)
        form.addRow("Larghezza (L)", self.spin_l)
        form.addRow("Altezza (H)", self.spin_h)
        form.addRow("Profondità (P)", self.spin_p)
        form.addRow("Spessore pannello", self.spin_sp)
        form.addRow("Spessore schienale", self.spin_ss)
        form.addRow("N. ripiani", self.spin_ripiani)
        layout.addWidget(g_dim)

        # --- Parametri / 32mm ---
        g_param = QtWidgets.QGroupBox("Parametri")
        lp = QtWidgets.QVBoxLayout(g_param)
        self.chk_32 = QtWidgets.QCheckBox("Sistema 32 mm")
        self.chk_32.setChecked(True)
        lp.addWidget(self.chk_32)
        layout.addWidget(g_param)

        # --- Fori e ferramenta ---
        g_fori = QtWidgets.QGroupBox("Fori e ferramenta")
        lf = QtWidgets.QVBoxLayout(g_fori)
        self.chk_fori_rip = QtWidgets.QCheckBox("Fori reggi-ripiano (Ø5)")
        self.chk_fori_rip.setChecked(True)
        self.chk_spinatura = QtWidgets.QCheckBox("Spinatura Ø8")
        self.chk_spinatura.setChecked(True)
        self.spin_cerniere = QtWidgets.QSpinBox()
        self.spin_cerniere.setRange(0, 10)
        self.spin_cerniere.setValue(0)
        lf.addWidget(self.chk_fori_rip)
        lf.addWidget(self.chk_spinatura)
        lf.addWidget(QtWidgets.QLabel("N. cerniere Ø35"))
        lf.addWidget(self.spin_cerniere)
        layout.addWidget(g_fori)

        # --- Ante e cassetti ---
        g_ante = QtWidgets.QGroupBox("Ante e cassetti")
        la = QtWidgets.QFormLayout(g_ante)
        self.spin_ante = QtWidgets.QSpinBox()
        self.spin_ante.setRange(0, 10)
        self.spin_cassetti = QtWidgets.QSpinBox()
        self.spin_cassetti.setRange(0, 10)
        la.addRow("N. ante", self.spin_ante)
        la.addRow("N. cassetti", self.spin_cassetti)
        layout.addWidget(g_ante)

        # --- Schienale ---
        g_sch = QtWidgets.QGroupBox("Schienale")
        ls = QtWidgets.QFormLayout(g_sch)
        self.combo_schienale = QtWidgets.QComboBox()
        self.combo_schienale.addItems(SCHIENALE_TYPES)
        self.spin_arretramento = self._spin(0.8, 0.0, 5.0, step=0.1)
        self.spin_arretramento.setEnabled(False)
        ls.addRow("Montaggio", self.combo_schienale)
        ls.addRow("Arretramento (custom)", self.spin_arretramento)
        layout.addWidget(g_sch)

        # --- Zoccolo ---
        g_zoc = QtWidgets.QGroupBox("Zoccolo")
        lz = QtWidgets.QVBoxLayout(g_zoc)
        self.chk_zoccolo = QtWidgets.QCheckBox("Aggiungi zoccolo")
        self.chk_zoccolo.setChecked(True)
        self.spin_zoccolo = self._spin(10, 5, 20)
        lz.addWidget(self.chk_zoccolo)
        lz.addWidget(QtWidgets.QLabel("Altezza zoccolo (cm)"))
        lz.addWidget(self.spin_zoccolo)
        layout.addWidget(g_zoc)

        # --- Descrizione testuale ---
        layout.addWidget(QtWidgets.QLabel("Descrizione (parser testuale)"))
        self.edit_desc = QtWidgets.QPlainTextEdit()
        self.edit_desc.setPlaceholderText(
            'Es: "mobile base cucina largo 80cm con 2 ripiani e 2 ante"'
        )
        self.edit_desc.setMaximumHeight(80)
        layout.addWidget(self.edit_desc)
        btn_parse = QtWidgets.QPushButton("Applica descrizione")
        btn_parse.clicked.connect(self._on_parse_description)
        layout.addWidget(btn_parse)

        layout.addStretch()
        scroll.setWidget(container)

        outer = QtWidgets.QVBoxLayout(self)
        outer.addWidget(scroll)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

        self.combo_tipo.currentTextChanged.connect(self._on_type_changed)
        self.combo_schienale.currentTextChanged.connect(self._on_schienale_type_changed)
        self.spin_ante.valueChanged.connect(self._sync_cerniere)

    @staticmethod
    def _spin(value: float, min_v: float, max_v: float, step: float = 1.0) -> QtWidgets.QDoubleSpinBox:
        w = QtWidgets.QDoubleSpinBox()
        w.setRange(min_v, max_v)
        w.setSingleStep(step)
        w.setDecimals(1)
        w.setValue(value)
        return w

    def _on_schienale_type_changed(self, text: str) -> None:
        self.spin_arretramento.setEnabled(text == "Arretrato custom")

    def _sync_cerniere(self) -> None:
        if self.spin_ante.value() > 0 and self.spin_cerniere.value() == 0:
            self.spin_cerniere.setValue(self.spin_ante.value() * 2)

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
        if parsed.get("num_ante"):
            self.spin_ante.setValue(parsed["num_ante"])
        if parsed.get("num_cassetti"):
            self.spin_cassetti.setValue(parsed["num_cassetti"])
        if parsed.get("tipo_schienale"):
            idx = self.combo_schienale.findText(parsed["tipo_schienale"])
            if idx >= 0:
                self.combo_schienale.setCurrentIndex(idx)

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
                "sistema_32mm": self.chk_32.isChecked(),
                "fori_ripiani": self.chk_fori_rip.isChecked(),
                "spinatura": self.chk_spinatura.isChecked(),
                "num_cerniere": self.spin_cerniere.value(),
                "num_ante": self.spin_ante.value(),
                "num_cassetti": self.spin_cassetti.value(),
                "tipo_schienale": self.combo_schienale.currentText(),
                "arretramento_schienale": self.spin_arretramento.value(),
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
