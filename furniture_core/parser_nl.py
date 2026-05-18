"""
Parser descrizioni in linguaggio naturale (senza IA).
"""

from __future__ import annotations

import re
from typing import Any, Dict

from .models import default_params_for_type, normalize_params


def parse_description(description: str, tipo_mobile: str = "Mobile Base") -> Dict[str, Any]:
    """
    Estrae parametri da testo libero (regex).
    Compatibile con i formati supportati dall'add-in Fusion.
    """
    desc_lower = description.lower()
    params = default_params_for_type(tipo_mobile)

    width_match = re.search(r"(?:larg|l[=:]?\s*)(\d+(?:\.\d+)?)\s*(?:cm)?", desc_lower)
    if width_match:
        params["larghezza"] = float(width_match.group(1))

    height_match = re.search(r"(?:alt|h[=:]?\s*)(\d+(?:\.\d+)?)\s*(?:cm)?", desc_lower)
    if height_match:
        params["altezza"] = float(height_match.group(1))

    depth_match = re.search(r"(?:prof|p[=:]?\s*)(\d+(?:\.\d+)?)\s*(?:cm)?", desc_lower)
    if depth_match:
        params["profondita"] = float(depth_match.group(1))

    if "pensile" in desc_lower or "sospeso" in desc_lower:
        params["tipo_mobile"] = "Pensile"
        params["con_zoccolo"] = False
    elif "armadio" in desc_lower:
        params["tipo_mobile"] = "Armadio"
    elif "cassetto" in desc_lower:
        params["tipo_mobile"] = "Cassetto"
    elif "anta" in desc_lower and "ante" not in desc_lower:
        params["tipo_mobile"] = "Anta"

    if "pensile" in desc_lower:
        params.setdefault("altezza", 70.0)
        params.setdefault("profondita", 35.0)
    elif "cucina" in desc_lower or "base" in desc_lower:
        params.setdefault("altezza", 90.0)
        params.setdefault("profondita", 60.0)
    elif "armadio" in desc_lower:
        params.setdefault("altezza", 220.0)

    shelves_match = re.search(r"(\d+)\s*ripian", desc_lower)
    if shelves_match:
        params["num_ripiani"] = int(shelves_match.group(1))

    doors_match = re.search(r"(\d+)\s*ant", desc_lower)
    if doors_match:
        params["num_ante"] = int(doors_match.group(1))
        params["num_cerniere"] = params["num_ante"] * 2

    drawers_match = re.search(r"(\d+)\s*cassett", desc_lower)
    if drawers_match:
        params["num_cassetti"] = int(drawers_match.group(1))

    if "incastr" in desc_lower:
        params["tipo_schienale"] = "Incastrato (scanalatura 10mm)"

    return normalize_params(params)
