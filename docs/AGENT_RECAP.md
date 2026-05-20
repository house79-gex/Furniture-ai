# AGENT_RECAP — FurnitureAI (solo FreeCAD)

> **Scopo:** handoff per continuare il lavoro su un altro PC o in una nuova sessione agente.  
> **Ultimo aggiornamento:** 2026-05-19  
> **Commit di riferimento:** `c11422d`  
> **Repository:** https://github.com/house79-gex/Furniture-ai  
> **Riferimento Fusion avanzato:** https://github.com/house79-gex/FurnitureAI-Professional.git (non in questo repo)

---

## Contesto utente

| Aspetto | Dettaglio |
|---------|-----------|
| **Uso** | Personale — falegnameria |
| **CAD** | **FreeCAD 1.0.2+** (workbench principale) |
| **Fusion** | Solo in repo **FurnitureAI-Professional** (separato) |
| **CNC** | SCM Record 130TV, post-processore **Xilog Plus** |
| **Install Mod** | Junction `%APPDATA%\FreeCAD\Mod\Furniture-ai` → clone repo |

---

## Decisioni architetturali

1. **Questo repo = solo FreeCAD** — rimossi `fusion_addin/`, `WoodWorkingWizard/`, doc legacy Fusion.
2. **`furniture_core/`** = unica fonte geometrica (`panel_specs.py` allineato a Professional `cabinet_generator`).
3. **Assiemi FreeCAD** = `App::Part` mobile → `App::Part` per pannello → `Part::Feature` solido.
4. **Coordinate (cm):** origine basso-sinistra-**anteriore**; X=larghezza, Y=profondità (0=fronte), Z=altezza.
5. **Professional** va consultato per feature future (fori PartDesign, profili DXF ante, layout L/griglia).

---

## Regole geometriche implementate

| Elemento | Regola |
|----------|--------|
| **Fondo / Cielo** | Larghezza `L − 2S`, tra i fianchi; profondità piena `P` |
| **Ripiani** | Larghezza `L − 2S`; arretramento fronte default **0,3 cm** (3 mm); profondità `P − inset_retro − Ss − setback_fronte` |
| **Schienale** | `A filo` / `Incastrato` (scanalatura 1 cm) / `Arretrato custom` |
| **Ante** | Se `num_ante > 0`: pannelli `Anta_1…N` davanti (`y < 0`), giochi e spessore anta configurabili |
| **Zoccolo** | Larghezza interna `L − 2S` |

File: `furniture_core/panel_specs.py`, costanti in `furniture_core/constants.py`.

---

## Struttura repository

```text
Furniture-ai/
├── furniture_core/
├── freecad_addon/FurnitureAI/
│   ├── FurnitureAICommands.py
│   ├── wizard_dialog.py      # UI scura stile Professional
│   ├── ui_style.py
│   ├── freecad_geometry.py
│   └── Resources/icons/FurnitureAI.svg
├── postprocessor/, tlg_parser/
├── InitGui.py                # shim Mod/ (__file__ + inspect fallback)
├── tests/
│   ├── test_furniture_core.py  # 11 test
│   └── test_xilog_export.py
└── docs/
    ├── AGENT_RECAP.md
    ├── FREECAD_INSTALL.md
    └── XILOG_EXPORT.md
```

---

## Comandi workbench

| Comando | ID |
|---------|-----|
| 🪑 Wizard mobili | `FurnitureAI_Wizard` |
| 📦 Aggiungi modulo | `FurnitureAI_AddModule` |
| 📋 Lista taglio | `FurnitureAI_Cutlist` |
| ⚙ Export Xilog | `FurnitureAI_Xilog` |

---

## Test

```powershell
python -m unittest tests.test_furniture_core tests.test_xilog_export -v
```

Attesi: **13 test OK**.

---

## Limitazioni / prossimi passi

| Area | Stato |
|------|--------|
| Ante | Box semplici con giochi; **no** profili DXF / bugna (c’è in Professional) |
| Fori 32 mm / spinatura | Flag wizard; **no** geometria fori |
| Cassetti | Parametro; **no** geometria |
| Layout modulare | Solo fila X; Professional ha L/griglia |
| Materiali | Non implementati |
| Icone PNG multi-size | Solo SVG + emoji menu (PNG Professional non nel clone) |

### Roadmap priorità alta

1. [ ] Fori PartDesign da `furniture_core` (regole hardware)
2. [ ] Portare logica ante avanzata da Professional (`door_designer`, profili DXF)
3. [ ] Layout modulare griglia/L
4. [ ] Icone PNG 16/32/64 per comando (come `resources/icons/icone.md` in Professional)

---

## File chiave

| File | Ruolo |
|------|--------|
| `furniture_core/panel_specs.py` | **Fonte verità** geometria pannelli |
| `furniture_core/constants.py` | Default mm→cm (setback, giochi ante) |
| `freecad_addon/FurnitureAI/freecad_geometry.py` | Assiemi FreeCAD |
| `freecad_addon/FurnitureAI/wizard_dialog.py` | UI wizard |
| `InitGui.py` | Entry Mod — non rompere fallback `__file__` |

---

## Installazione rapida

```powershell
git clone https://github.com/house79-gex/Furniture-ai.git
cmd /c mklink /J "%APPDATA%\FreeCAD\Mod\Furniture-ai" "C:\percorso\Furniture-ai"
```

Riavviare FreeCAD → Workbench **FurnitureAI**.

---

## Prompt per riprendere

```text
Leggi docs/AGENT_RECAP.md. Repo solo FreeCAD; Professional è repo separato.
Continua roadmap (fori PartDesign o ante DXF). Rispondi in italiano.
```

---

*Aggiornare a ogni milestone.*
