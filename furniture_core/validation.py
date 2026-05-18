"""
Validazione parametri mobili (logica conmotione, senza dipendenze CAD).
"""

from __future__ import annotations

from typing import Any, Dict, List


def validate_cabinet_params(params: Dict[str, Any]) -> List[str]:
    """Restituisce lista errori; lista vuota se tutto ok."""
    errors: List[str] = []

    larghezza = float(params.get("larghezza", 0))
    altezza = float(params.get("altezza", 0))
    profondita = float(params.get("profondita", 0))

    if larghezza < 20.0 or larghezza > 300.0:
        errors.append("Larghezza deve essere tra 20 e 300 cm")
    if altezza < 20.0 or altezza > 300.0:
        errors.append("Altezza deve essere tra 20 e 300 cm")
    if profondita < 20.0 or profondita > 100.0:
        errors.append("Profondità deve essere tra 20 e 100 cm")

    sp_p = float(params.get("spessore_pannello", 0))
    sp_s = float(params.get("spessore_schienale", 0))
    if sp_p < 1.0 or sp_p > 5.0:
        errors.append("Spessore pannello deve essere tra 1.0 e 5.0 cm")
    if sp_s < 0.3 or sp_s > 2.0:
        errors.append("Spessore schienale deve essere tra 0.3 e 2.0 cm")

    num_ripiani = int(params.get("num_ripiani", 0))
    if num_ripiani < 0 or num_ripiani > 10:
        errors.append("Numero ripiani deve essere tra 0 e 10")

    return errors
