"""
Modelli dati e default per mobili parametrici.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

FURNITURE_TYPES: List[str] = [
    "Mobile Base",
    "Pensile",
    "Anta",
    "Cassetto",
    "Armadio",
]

_DEFAULTS_BY_TYPE: Dict[str, Dict[str, Any]] = {
    "Mobile Base": {
        "larghezza": 80.0,
        "altezza": 90.0,
        "profondita": 60.0,
        "con_zoccolo": True,
        "altezza_zoccolo": 10.0,
    },
    "Pensile": {
        "larghezza": 80.0,
        "altezza": 70.0,
        "profondita": 35.0,
        "con_zoccolo": False,
        "altezza_zoccolo": 0.0,
    },
    "Armadio": {
        "larghezza": 120.0,
        "altezza": 220.0,
        "profondita": 60.0,
        "num_ripiani": 3,
        "con_zoccolo": True,
        "altezza_zoccolo": 10.0,
    },
    "Anta": {
        "larghezza": 40.0,
        "altezza": 70.0,
        "profondita": 1.8,
        "num_ripiani": 0,
    },
    "Cassetto": {
        "larghezza": 50.0,
        "altezza": 20.0,
        "profondita": 50.0,
        "num_ripiani": 0,
    },
}

_BASE_DEFAULTS: Dict[str, Any] = {
    "tipo_mobile": "Mobile Base",
    "larghezza": 80.0,
    "altezza": 90.0,
    "profondita": 60.0,
    "spessore_pannello": 1.8,
    "spessore_schienale": 0.6,
    "num_ripiani": 2,
    "sistema_32mm": True,
    "fori_ripiani": True,
    "spinatura": True,
    "num_cerniere": 0,
    "num_ante": 0,
    "num_cassetti": 0,
    "tipo_schienale": "A filo dietro",
    "arretramento_schienale": 0.8,
    "groove_offset_cm": 1.0,
    "shelf_front_setback": 0.3,
    "spessore_anta": 1.8,
    "con_zoccolo": True,
    "altezza_zoccolo": 10.0,
}


def default_params_for_type(tipo: str) -> Dict[str, Any]:
    """Restituisce parametri di default per il tipo mobile."""
    params = deepcopy(_BASE_DEFAULTS)
    params["tipo_mobile"] = tipo
    overrides = _DEFAULTS_BY_TYPE.get(tipo, {})
    params.update(overrides)
    return params


def normalize_params(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Unisce input utente con default e tipi coerenti."""
    tipo = raw.get("tipo_mobile", _BASE_DEFAULTS["tipo_mobile"])
    params = default_params_for_type(tipo)
    params.update(raw)
    params["tipo_mobile"] = tipo

    for key in (
        "larghezza",
        "altezza",
        "profondita",
        "spessore_pannello",
        "spessore_schienale",
        "altezza_zoccolo",
        "arretramento_schienale",
        "groove_offset_cm",
        "shelf_front_setback",
        "spessore_anta",
    ):
        if key in params and params[key] is not None:
            params[key] = float(params[key])

    for key in ("num_ripiani", "num_ante", "num_cassetti", "num_cerniere"):
        if key in params and params[key] is not None:
            params[key] = int(params[key])

    for key in ("sistema_32mm", "fori_ripiani", "spinatura", "con_zoccolo"):
        if key in params:
            params[key] = bool(params[key])

    if params.get("num_ante", 0) > 0 and params.get("num_cerniere", 0) == 0:
        params["num_cerniere"] = params["num_ante"] * 2

    return params
