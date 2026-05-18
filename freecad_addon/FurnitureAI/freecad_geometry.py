"""
Generazione geometria 3D in FreeCAD (Part).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import FreeCAD as App
import Part

from furniture_core.panel_specs import build_panel_specs
from furniture_core.validation import validate_cabinet_params
from furniture_core.models import normalize_params


def _cm_to_mm(value: float) -> float:
    return value * 10.0


def build_cabinet_in_document(
    doc: App.Document,
    raw_params: Dict[str, Any],
    group_name: str = "Mobile_FurnitureAI",
) -> Tuple[App.DocumentObject, List[str]]:
    """
    Crea un App::Part con pannelli box.
    Restituisce (gruppo, nomi_pannelli_creati).
    """
    errors = validate_cabinet_params(normalize_params(raw_params))
    if errors:
        raise ValueError("; ".join(errors))

    params = normalize_params(raw_params)
    panels = build_panel_specs(params)

    part = doc.addObject("App::Part", group_name)
    created: List[str] = []

    for spec in panels:
        sx = _cm_to_mm(spec["size_x"])
        sy = _cm_to_mm(spec["size_y"])
        sz = _cm_to_mm(spec["size_z"])
        box = Part.makeBox(sx, sy, sz)
        obj = doc.addObject("Part::Feature", spec["name"])
        obj.Shape = box
        obj.Placement.Base = App.Vector(
            _cm_to_mm(spec["pos_x"]),
            _cm_to_mm(spec["pos_y"]),
            _cm_to_mm(spec["pos_z"]),
        )
        part.addObject(obj)
        created.append(spec["name"])

    doc.recompute()
    return part, created
