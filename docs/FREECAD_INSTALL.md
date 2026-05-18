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

1. Crea un nuovo documento.
2. Workbench **FurnitureAI** → **Wizard mobili**.
3. Imposta dimensioni o incolla una descrizione testuale → **Applica descrizione**.
4. **OK** per generare pannelli (Part) raggruppati in `Mobile_FurnitureAI`.
5. **Lista taglio** esporta CSV dalla stessa logica di `furniture_core`.
6. **Export Xilog** genera un file `.xilog` multi-pannello per SCM Record 130TV (spinatura e fori 32 mm se attivi nel wizard).

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
