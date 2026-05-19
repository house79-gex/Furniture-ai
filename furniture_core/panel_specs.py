"""
Definizione pannelli in cm (logica pura, senza geometria CAD).
"""

from __future__ import annotations

from typing import Any, Dict, List

from .models import normalize_params


def _schienale_position_y(params: Dict[str, Any], P: float, S: float, Ss: float) -> float:
    """Coordinata Y anteriore del schienale (cm), allineata ai tipi wizard Fusion."""
    tipo = params.get("tipo_schienale", "A filo dietro")
    if tipo == "Arretrato custom":
        arr = float(params.get("arretramento_schienale", 0.8))
        return P - Ss - arr
    if "Incastrato" in str(tipo):
        # Scanalatura standard 10 mm nel fianco
        return P - S - Ss
    return P - Ss


def _box(name: str, sx: float, sy: float, sz: float, x: float, y: float, z: float) -> Dict[str, Any]:
    return {
        "name": name,
        "size_x": sx,
        "size_y": sy,
        "size_z": sz,
        "pos_x": x,
        "pos_y": y,
        "pos_z": z,
    }


def build_panel_specs(raw_params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Calcola elenco pannelli per mobile base / pensile / armadio.
    Sistema di riferimento: origine in basso-sinistra-anteriore, unità cm.
    """
    params = normalize_params(raw_params)
    panels: List[Dict[str, Any]] = []

    L = params["larghezza"]
    H = params["altezza"]
    P = params["profondita"]
    S = params["spessore_pannello"]
    Ss = params["spessore_schienale"]

    panels.append(_box("Fianco_SX", S, P, H, 0, 0, 0))
    panels.append(_box("Fianco_DX", S, P, H, L - S, 0, 0))
    panels.append(_box("Base", L, P, S, 0, 0, 0))
    panels.append(_box("Top", L, P, S, 0, 0, H - S))

    num_ripiani = int(params.get("num_ripiani", 0))
    if num_ripiani > 0:
        altezza_interna = H - 2 * S
        interasse = altezza_interna / (num_ripiani + 1)
        for i in range(num_ripiani):
            z_pos = S + interasse * (i + 1)
            panels.append(_box(f"Ripiano_{i + 1}", L - 2 * S, P, S, S, 0, z_pos))

    # Schienale (posizione Y in base al montaggio, come wizard Fusion)
    y_schienale = _schienale_position_y(params, P, S, Ss)
    panels.append(_box("Schienale", L - 2 * S, Ss, H - 2 * S, S, y_schienale, S))

    if params.get("con_zoccolo"):
        Hz = float(params.get("altezza_zoccolo", 10.0))
        panels.append(_box("Zoccolo", L - 2 * S, Hz, S, S, 5, -Hz))

    return panels
