"""
Logica condivisa FurnitureAI (indipendente da Fusion 360 / FreeCAD).
"""

from .models import (
    FURNITURE_TYPES,
    default_params_for_type,
    normalize_params,
)
from .validation import validate_cabinet_params
from .parser_nl import parse_description
from .panel_specs import build_panel_specs
from .cutlist import panels_to_cutlist, export_csv, export_excel

__all__ = [
    "FURNITURE_TYPES",
    "default_params_for_type",
    "normalize_params",
    "validate_cabinet_params",
    "parse_description",
    "build_panel_specs",
    "panels_to_cutlist",
    "export_csv",
    "export_excel",
]
