"""
Export Xilog Plus da parametri mobile (indipendente da CAD).
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from .models import normalize_params
from .panel_specs import build_panel_specs

# Permette import postprocessor dalla root repository
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from postprocessor.xilog_generator import XilogGenerator  # noqa: E402
from tlg_parser.tlg_library import TLGLibrary  # noqa: E402


def _panel_dimensions_mm(spec: Dict[str, Any]) -> Tuple[float, float, float]:
    """Restituisce (L, W, T) in mm dal box pannello (cm → mm)."""
    dims_mm = sorted(
        [
            spec["size_x"] * 10.0,
            spec["size_y"] * 10.0,
            spec["size_z"] * 10.0,
        ],
        reverse=True,
    )
    return dims_mm[0], dims_mm[1], dims_mm[2]


def _corner_dowel_positions(l_mm: float, w_mm: float, margin: float = 50.0) -> List[Tuple[float, float]]:
    """Posizioni spinatura agli angoli del pannello (faccia superiore)."""
    return [
        (margin, margin),
        (l_mm - margin, margin),
        (margin, w_mm - margin),
        (l_mm - margin, w_mm - margin),
    ]


def _shelf_hole_rows(l_mm: float, w_mm: float, step_mm: float = 32.0) -> List[Dict[str, Any]]:
    """Fori reggi-ripiano Ø5 lungo il bordo (sistema 32 mm)."""
    holes: List[Dict[str, Any]] = []
    y = 100.0
    while y < w_mm - 50.0:
        holes.append({"x": 32.0, "y": y, "diameter": 5.0, "depth": 12.0})
        holes.append({"x": l_mm - 32.0, "y": y, "diameter": 5.0, "depth": 12.0})
        y += step_mm
    return holes


def generate_xilog_for_cabinet(
    raw_params: Dict[str, Any],
    tlg_path: Optional[str] = None,
) -> str:
    """
    Genera codice Xilog per tutti i pannelli del mobile.
    """
    params = normalize_params(raw_params)
    panels = build_panel_specs(params)

    tlg = TLGLibrary(tlg_path) if tlg_path else TLGLibrary()
    gen = XilogGenerator(tlg)

    gen.program_lines.extend([
        "; ================================================================",
        "; FurnitureAI — programma multi-pannello",
        "; Mobile: {} — L={} H={} P={} cm".format(
            params.get("tipo_mobile", "Mobile"),
            params["larghezza"],
            params["altezza"],
            params["profondita"],
        ),
        "; ================================================================",
        "",
        "G90",
        "G71",
        "",
    ])

    use_dowel = bool(params.get("spinatura", False))
    use_shelf = bool(params.get("fori_ripiani", False)) and bool(params.get("sistema_32mm", False))

    for spec in panels:
        name = spec["name"]
        l_mm, w_mm, t_mm = _panel_dimensions_mm(spec)

        gen.program_lines.extend([
            "",
            "; ----------------------------------------------------------------",
            "; PANNELLO: {}".format(name),
            "; ----------------------------------------------------------------",
        ])
        gen.add_header(name, (l_mm, w_mm, t_mm))

        if use_dowel and t_mm >= 15.0:
            gen.add_dowel_holes(_corner_dowel_positions(l_mm, w_mm))

        if use_shelf and name.startswith("Fianco"):
            gen.add_drilling(_shelf_hole_rows(l_mm, w_mm), face=1, optimized=True)

        if params.get("num_cerniere", 0) > 0 and name.startswith("Anta"):
            gen.add_hinge_holes([(50.0, 150.0), (50.0, w_mm - 150.0)])

    gen.add_safety_notes()
    gen.add_footer()
    return gen.generate()


def save_xilog_for_cabinet(
    raw_params: Dict[str, Any],
    filepath: str,
    tlg_path: Optional[str] = None,
) -> bool:
    """Salva file .xilog per il mobile."""
    try:
        content = generate_xilog_for_cabinet(raw_params, tlg_path=tlg_path)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except OSError:
        return False
