"""
Lista taglio da specifiche pannelli (senza CAD).
"""

from __future__ import annotations

import csv
from typing import Any, Dict, List


def panels_to_cutlist(panels: List[Dict[str, Any]], materiale: str = "Legno") -> List[Dict[str, Any]]:
    """Converte pannelli (cm) in righe lista taglio."""
    cutlist: List[Dict[str, Any]] = []

    for panel in panels:
        dims = sorted(
            [panel["size_x"], panel["size_y"], panel["size_z"]],
            reverse=True,
        )
        lunghezza, larghezza, spessore = dims[0], dims[1], dims[2]
        cutlist.append(
            {
                "nome": panel["name"],
                "lunghezza": round(lunghezza, 1),
                "larghezza": round(larghezza, 1),
                "spessore": round(spessore, 1),
                "materiale": materiale,
                "quantita": 1,
                "area_m2": round((lunghezza * larghezza) / 10000.0, 3),
            }
        )

    return cutlist


def export_csv(cutlist: List[Dict[str, Any]], filepath: str) -> None:
    """Esporta lista taglio in CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Nome", "Lunghezza (cm)", "Larghezza (cm)", "Spessore (cm)", "Materiale", "Quantita", "Area m2"]
        )
        for item in cutlist:
            writer.writerow(
                [
                    item["nome"],
                    item["lunghezza"],
                    item["larghezza"],
                    item["spessore"],
                    item["materiale"],
                    item["quantita"],
                    item["area_m2"],
                ]
            )


def export_excel(cutlist: List[Dict[str, Any]], filepath: str) -> None:
    """Esporta lista taglio in Excel; fallback CSV se openpyxl manca."""
    try:
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Lista Taglio"
        ws.append(
            ["Nome", "Lunghezza (cm)", "Larghezza (cm)", "Spessore (cm)", "Materiale", "Quantita", "Area m2"]
        )
        for item in cutlist:
            ws.append(
                [
                    item["nome"],
                    item["lunghezza"],
                    item["larghezza"],
                    item["spessore"],
                    item["materiale"],
                    item["quantita"],
                    item["area_m2"],
                ]
            )
        wb.save(filepath)
    except ImportError:
        export_csv(cutlist, filepath.replace(".xlsx", ".csv"))
