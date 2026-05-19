"""
Specifica assieme mobile (logica pura) — allineata a Fusion Component + corpi nominati.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from .models import normalize_params
from .panel_specs import build_panel_specs


def safe_object_name(label: str) -> str:
    """Nome sicuro per oggetti CAD (senza spazi)."""
    name = re.sub(r"[^\w]", "_", label.strip())
    return name or "Mobile"


def cabinet_assembly_label(params: Dict[str, Any]) -> str:
    """Etichetta assieme mobile (come nome componente Fusion)."""
    params = normalize_params(params)
    return safe_object_name(params.get("tipo_mobile", "Mobile_Base"))


def suggest_module_name(existing_names: List[str], prefix: str = "Modulo") -> str:
    """Genera Modulo_1, Modulo_2, … evitando collisioni."""
    used = set(existing_names)
    n = 1
    while True:
        candidate = f"{prefix}_{n}"
        if candidate not in used:
            return candidate
        n += 1


def build_cabinet_assembly_spec(
    raw_params: Dict[str, Any],
    assembly_name: Optional[str] = None,
    position_cm: Tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Dict[str, Any]:
    """
    Struttura assieme per un mobile singolo.

    Restituisce:
        assembly_name, label, position_cm, panels (da panel_specs)
    """
    params = normalize_params(raw_params)
    label = assembly_name or cabinet_assembly_label(params)
    name = safe_object_name(label)

    return {
        "assembly_name": name,
        "assembly_label": label.replace("_", " "),
        "position_cm": position_cm,
        "params": params,
        "panels": build_panel_specs(params),
    }
