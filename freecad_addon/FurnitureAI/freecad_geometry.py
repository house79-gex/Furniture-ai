"""
Generazione assiemi in FreeCAD — struttura allineata a Fusion 360.

Fusion: Component (mobile) → corpi/pannelli nominati (Fianco_SX, Base, …).
FreeCAD: App::Part (mobile) → App::Part figlio per ogni pannello → Part::Feature solido.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import FreeCAD as App
import Part

from furniture_core.assembly_spec import (
    build_cabinet_assembly_spec,
    safe_object_name,
    suggest_module_name,
)
from furniture_core.models import normalize_params
from furniture_core.validation import validate_cabinet_params


def _cm_to_mm(value: float) -> float:
    return value * 10.0


def _existing_object_names(doc: App.Document) -> List[str]:
    return [obj.Name for obj in doc.Objects]


def _unique_name(doc: App.Document, base: str) -> str:
    base = safe_object_name(base)
    names = set(_existing_object_names(doc))
    if base not in names:
        return base
    n = 2
    while f"{base}_{n}" in names:
        n += 1
    return f"{base}_{n}"


def _create_panel_part(
    doc: App.Document,
    spec: Dict[str, Any],
    parent: App.DocumentObject,
) -> App.DocumentObject:
    """
    Crea un sotto-assieme pannello (come corpo nominato in Fusion).
    """
    panel_name = _unique_name(doc, spec["name"])
    panel_asm = doc.addObject("App::Part", panel_name)
    panel_asm.Label = spec["name"]

    sx = _cm_to_mm(spec["size_x"])
    sy = _cm_to_mm(spec["size_y"])
    sz = _cm_to_mm(spec["size_z"])
    solid = doc.addObject("Part::Feature", "Solido")
    solid.Shape = Part.makeBox(sx, sy, sz)
    solid.Placement.Base = App.Vector(
        _cm_to_mm(spec["pos_x"]),
        _cm_to_mm(spec["pos_y"]),
        _cm_to_mm(spec["pos_z"]),
    )
    panel_asm.addObject(solid)
    parent.addObject(panel_asm)
    return panel_asm


def build_cabinet_assembly_in_document(
    doc: App.Document,
    raw_params: Dict[str, Any],
    assembly_name: Optional[str] = None,
    position_cm: Tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Tuple[App.DocumentObject, List[str]]:
    """
    Crea un assieme mobile nell'albero documento (equivalente Fusion Component).

    Restituisce (assieme_mobile, nomi_pannelli).
    """
    errors = validate_cabinet_params(normalize_params(raw_params))
    if errors:
        raise ValueError("; ".join(errors))

    spec = build_cabinet_assembly_spec(raw_params, assembly_name=assembly_name, position_cm=position_cm)
    asm_name = _unique_name(doc, spec["assembly_name"])

    mobile = doc.addObject("App::Part", asm_name)
    mobile.Label = spec.get("assembly_label", asm_name)
    mobile.Placement.Base = App.Vector(
        _cm_to_mm(position_cm[0]),
        _cm_to_mm(position_cm[1]),
        _cm_to_mm(position_cm[2]),
    )

    created: List[str] = []
    for panel in spec["panels"]:
        _create_panel_part(doc, panel, mobile)
        created.append(panel["name"])

    doc.recompute()
    return mobile, created


def build_cabinet_in_document(
    doc: App.Document,
    raw_params: Dict[str, Any],
    group_name: str = "Mobile_FurnitureAI",
) -> Tuple[App.DocumentObject, List[str]]:
    """
    Compatibilità: crea assieme mobile (nome derivato da group_name o tipo).
    """
    return build_cabinet_assembly_in_document(doc, raw_params, assembly_name=group_name)


def add_cabinet_module_to_document(
    doc: App.Document,
    raw_params: Dict[str, Any],
    position_cm: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    module_name: Optional[str] = None,
) -> Tuple[App.DocumentObject, List[str]]:
    """
    Aggiunge un modulo mobile posizionato (equivalente ModularProject.add_cabinet_module).
    """
    if not module_name:
        module_name = suggest_module_name(_existing_object_names(doc))
    return build_cabinet_assembly_in_document(
        doc, raw_params, assembly_name=module_name, position_cm=position_cm
    )
