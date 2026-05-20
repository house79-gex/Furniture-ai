"""
Definizione pannelli in cm (logica pura, senza geometria CAD).

Sistema di riferimento (FreeCAD):
- Origine: basso-sinistra-anteriore (davanti del mobile).
- X = larghezza, Y = profondità (0 = fronte, P = retro), Z = altezza.

Regole allineate a FurnitureAI-Professional (cabinet_generator):
- Fondo/Cielo: larghezza interna (L - 2S), tra i fianchi, profondità piena.
- Ripiani: stessa larghezza, arretrati dal fronte, accorciati sul retro (schienale + scanalatura).
- Ante: generate davanti alla carcassa se num_ante > 0.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .constants import (
    DEFAULT_DOOR_THICKNESS_CM,
    DOOR_GAP_BETWEEN_CM,
    DOOR_GAP_BOTTOM_CM,
    DOOR_GAP_SIDE_CM,
    DOOR_GAP_TOP_CM,
    GROOVE_OFFSET_CM,
    SHELF_FRONT_SETBACK_CM,
)
from .models import normalize_params


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


def _back_inset_cm(params: Dict[str, Any]) -> float:
    """
    Distanza dal retro (y=P) alla faccia interna utile ripiani/divisori (cm).
    Equivalente back_inset in CabinetGenerator (mm).
    """
    tipo = params.get("tipo_schienale", "A filo dietro")
    if "Incastrato" in str(tipo):
        return float(params.get("groove_offset_cm", GROOVE_OFFSET_CM))
    if tipo == "Arretrato custom":
        return float(params.get("arretramento_schienale", 0.8))
    return 0.0


def _schienale_position_y(params: Dict[str, Any], P: float, S: float, Ss: float) -> float:
    """Coordinata Y (fronte del pannello schienale), cm."""
    tipo = params.get("tipo_schienale", "A filo dietro")
    if "Incastrato" in str(tipo):
        groove = float(params.get("groove_offset_cm", GROOVE_OFFSET_CM))
        return P - groove - Ss
    if tipo == "Arretrato custom":
        arr = float(params.get("arretramento_schienale", 0.8))
        return P - Ss - arr
    return P - Ss


def _shelf_zone(params: Dict[str, Any], P: float, S: float, Ss: float) -> Tuple[float, float]:
    """Restituisce (y_fronte, profondità_utile) ripiano in cm."""
    setback = float(params.get("shelf_front_setback", SHELF_FRONT_SETBACK_CM))
    inset = _back_inset_cm(params)
    y_front = setback
    y_back_inner = P - inset - Ss
    depth = y_back_inner - y_front
    return y_front, max(0.0, depth)


def _door_panels(
    params: Dict[str, Any],
    L: float,
    H: float,
    S: float,
    Hz: float,
) -> List[Dict[str, Any]]:
    """Genera specifiche ante davanti alla carcassa."""
    num_ante = int(params.get("num_ante", 0))
    if num_ante <= 0:
        return []

    door_t = float(params.get("spessore_anta", DEFAULT_DOOR_THICKNESS_CM))
    inner_w = L - 2 * S
    carcass_h = H - Hz - 2 * S
    gap_s = DOOR_GAP_SIDE_CM
    gap_t = DOOR_GAP_TOP_CM
    gap_b = DOOR_GAP_BOTTOM_CM
    gap_mid = DOOR_GAP_BETWEEN_CM

    total_gaps = 2 * gap_s + max(0, num_ante - 1) * gap_mid
    door_w = (inner_w - total_gaps) / num_ante
    door_h = max(0.1, carcass_h - gap_t - gap_b)
    z0 = Hz + S + gap_b

    panels: List[Dict[str, Any]] = []
    for i in range(num_ante):
        x = S + gap_s + i * (door_w + gap_mid)
        panels.append(_box(f"Anta_{i + 1}", door_w, door_t, door_h, x, -door_t, z0))
    return panels


def build_panel_specs(raw_params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Calcola elenco pannelli per mobile base / pensile / armadio.
    """
    params = normalize_params(raw_params)
    panels: List[Dict[str, Any]] = []

    L = params["larghezza"]
    H = params["altezza"]
    P = params["profondita"]
    S = params["spessore_pannello"]
    Ss = params["spessore_schienale"]
    Hz = float(params.get("altezza_zoccolo", 0.0)) if params.get("con_zoccolo") else 0.0

    inner_L = L - 2 * S

    # Fianchi (profondità piena)
    panels.append(_box("Fianco_SX", S, P, H, 0, 0, 0))
    panels.append(_box("Fianco_DX", S, P, H, L - S, 0, 0))

    # Fondo e cielo — tra i fianchi (non larghezza piena)
    panels.append(_box("Fondo", inner_L, P, S, S, 0, Hz))
    panels.append(_box("Cielo", inner_L, P, S, S, 0, H - S))

    # Ripiani intermedi
    num_ripiani = int(params.get("num_ripiani", 0))
    if num_ripiani > 0:
        y_front, shelf_depth = _shelf_zone(params, P, S, Ss)
        if shelf_depth > 0.1:
            altezza_interna = H - 2 * S - Hz
            interasse = altezza_interna / (num_ripiani + 1)
            for i in range(num_ripiani):
                z_pos = Hz + S + interasse * (i + 1)
                panels.append(
                    _box(f"Ripiano_{i + 1}", inner_L, shelf_depth, S, S, y_front, z_pos)
                )

    # Schienale
    y_sch = _schienale_position_y(params, P, S, Ss)
    panels.append(_box("Schienale", inner_L, Ss, H - 2 * S, S, y_sch, S))

    # Zoccolo
    if params.get("con_zoccolo") and Hz > 0:
        panels.append(_box("Zoccolo", inner_L, Hz, S, S, 5, -Hz))

    # Ante
    panels.extend(_door_panels(params, L, H, S, Hz))

    return panels
