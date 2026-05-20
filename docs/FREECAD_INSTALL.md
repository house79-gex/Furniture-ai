# FurnitureAI su FreeCAD 1.1

## Installazione (Windows)

1. Clona il repository (intera cartella):

```text
git clone https://github.com/house79-gex/Furniture-ai.git
```

2. Collega la cartella del repository alla cartella Mod di FreeCAD:

**Opzione A — collegamento simbolico (consigliata)**

```powershell
mklink /D "%APPDATA%\FreeCAD\Mod\Furniture-ai" "C:\percorso\Furniture-ai"
```

**Opzione B — copia**

Copia l'intera cartella `Furniture-ai` in:

```text
%APPDATA%\FreeCAD\Mod\Furniture-ai
```

3. Riavvia FreeCAD 1.1.

4. Menu **Visualizza → Workbench → FurnitureAI**.

## Utilizzo

1. Workbench **FurnitureAI** → **Wizard mobili** (crea il documento se assente).
2. Imposta dimensioni o incolla una descrizione testuale → **Applica descrizione**.
3. **OK** → assieme mobile con **Fondo/Cielo tra i fianchi**, ripiani arretrati, **ante** se impostate, un sotto-assieme per pannello.
4. **Aggiungi modulo** → secondo mobile in fila (`Modulo_1`, `Modulo_2`, …) come layout modulare Fusion.
5. **Lista taglio** → CSV da `furniture_core`.
6. **Export Xilog** → file `.xilog` per SCM Record 130TV.

**Albero modello (esempio):**
```text
Mobile_Base
├── Fianco_SX → Solido
├── Fianco_DX → Solido
├── Base → Solido
└── …
```

## Struttura

```text
Furniture-ai/
├── furniture_core/       # logica conmotione (Fusion + FreeCAD)
├── freecad_addon/        # workbench GUI
├── fusion_addin/         # add-in Autodesk
├── postprocessor/        # Xilog Plus
└── InitGui.py            # shim per Mod/
```

## Note

- Serve l'intera repository in `Mod/`, non solo la sottocartella `freecad_addon`, perché `furniture_core` è alla root.
- Il post-processore Xilog resta utilizzabile da script Python come in Fusion (`examples/generate_examples.py`).
- **FreeCAD 1.0** è supportato (testato con 1.0.2). FreeCAD 1.1 consigliato per sviluppo futuro.

## Risoluzione problemi

### Workbench "FurnitureAI" non compare

1. Verificare il collegamento in `%APPDATA%\FreeCAD\Mod\Furniture-ai` (deve contenere `InitGui.py` nella root).
2. Riavviare FreeCAD completamente.
3. Aprire **Report view** e cercare errori su `Furniture-ai` o `relative import`.

### `ModuleNotFoundError: furniture_core`

Il workbench non è stato caricato. Selezionare prima **Visualizza → Workbench → FurnitureAI**, oppure in console:

```python
import sys
sys.path.insert(0, r"C:\Users\xilog\AppData\Roaming\FreeCAD\Mod\Furniture-ai")
from furniture_core.panel_specs import build_panel_specs
```

### Errori all'avvio da altri addon

In `Mod\` possono esserci addon di terze parti (es. `sheetmetal`, `InventorLoader`). Per isolare FurnitureAI, rinominare temporaneamente le altre cartelle in `Mod\_disabilitato\`.
