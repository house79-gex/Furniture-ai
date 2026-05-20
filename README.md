# FurnitureAI — Workbench FreeCAD per mobili

Workbench **FreeCAD 1.0+** per progettazione parametrica di mobili in legno, allineato alla logica di [FurnitureAI-Professional](https://github.com/house79-gex/FurnitureAI-Professional) (Fusion 360).

## Caratteristiche

- **Wizard mobili** con parametri professionali (fianchi, fondo/cielo tra i fianchi, ripiani arretrati, schienale, zoccolo, **ante**)
- **Assiemi** stile Fusion: un `App::Part` per mobile, sotto-assiemi per ogni pannello
- **Moduli multipli** in fila (cucine modulari)
- **Lista taglio** CSV e **export Xilog Plus** (SCM Record 130TV)
- Logica condivisa in `furniture_core/` (Python puro, testabile senza CAD)

## Installazione FreeCAD (Windows)

```powershell
git clone https://github.com/house79-gex/Furniture-ai.git C:\CAD\Furniture-ai
New-Item -ItemType Directory -Force -Path "$env:APPDATA\FreeCAD\Mod"
cmd /c mklink /J "%APPDATA%\FreeCAD\Mod\Furniture-ai" "C:\CAD\Furniture-ai"
```

Riavviare FreeCAD → **Visualizza → Workbench → FurnitureAI**

📖 Dettagli: [docs/FREECAD_INSTALL.md](docs/FREECAD_INSTALL.md)

## Utilizzo rapido

1. **Wizard mobili** — imposta dimensioni o descrizione testuale → OK
2. Verificare nell'albero: `Mobile_Base` → `Fondo`, `Cielo`, `Fianco_SX`, `Ripiano_1`, `Anta_1`, …
3. **Lista taglio** / **Export Xilog** dai parametri wizard

## Regole geometriche (allineate Professional)

| Elemento | Regola |
|----------|--------|
| Fondo / Cielo | Larghezza `L − 2×spessore` (tra i fianchi) |
| Ripiani | Stessa larghezza; **3 mm** arretramento fronte; retro accorciato per schienale + scanalatura |
| Ante | Davanti alla carcassa; larghezza ripartita con giochi standard |
| Schienale | Posizione in base a montaggio (a filo / incastrato / arretrato) |

## Test

```powershell
python -m unittest tests.test_furniture_core tests.test_xilog_export -v
```

## Struttura progetto

```text
furniture_core/          # Logica mobili (cm)
freecad_addon/FurnitureAI/  # Workbench GUI
postprocessor/           # Xilog Plus
tlg_parser/              # Libreria utensili
InitGui.py               # Entry Mod/ (shim)
docs/AGENT_RECAP.md      # Handoff per agenti / altro PC
```

## Fusion 360

L'add-in Fusion avanzato è nel repository separato **FurnitureAI-Professional**. Questo repo è **solo FreeCAD**.

## Licenza

MIT — vedi [LICENSE](LICENSE)
