# AGENT_RECAP — FurnitureAI

> **Scopo:** handoff per continuare il lavoro su un altro PC o in una nuova sessione agente.  
> **Ultimo aggiornamento:** 2026-05-19  
> **Repository:** https://github.com/house79-gex/Furniture-ai  
> **Branch principale:** `main` (commit di riferimento: `41630d7`)

---

## Contesto utente

| Aspetto | Dettaglio |
|---------|-----------|
| **Uso** | Personale (falegnameria / mobili semplici) |
| **CAD attuale** | Fusion 360 (esperto); **FreeCAD 1.0.2** installato e workbench funzionante |
| **Obiettivo** | FreeCAD come piattaforma principale; Fusion in manutenzione |
| **CNC** | SCM Record 130TV (NUM 1050), post-processore **Xilog Plus** |
| **Linguaggio UI** | Italiano |
| **PC sviluppo** | Windows; repo locale anche in `Documents\github copilot\Furniture-ai` |
| **Install FreeCAD** | Junction: `%APPDATA%\FreeCAD\Mod\Furniture-ai` → cartella clone repo |

---

## Decisioni architetturali (non invertire senza motivo)

1. **`furniture_core/`** = unico cervello condiviso (parametri, validazione, parser, `panel_specs`, `assembly_spec`, cutlist, Xilog). **Nessuna** dipendenza da `adsk` / `FreeCAD`.
2. **`freecad_addon/FurnitureAI/`** = destinazione principale nuove feature; comportamento **allineato a Fusion** (assiemi, wizard, moduli).
3. **`fusion_addin/`** = manutenzione; geometria ancora in `furniture_generator.py` (da unificare a `panel_specs`).
4. **Struttura FreeCAD** = `App::Part` mobile → `App::Part` per pannello → `Part::Feature` solido (equivalente Component + corpi nominati Fusion).
5. **Non** refactorare `WoodWorkingWizard/` senza richiesta esplicita.

---

## Struttura repository (aggiornata)

```text
Furniture-ai/
├── furniture_core/
│   ├── models.py, validation.py, parser_nl.py
│   ├── panel_specs.py      # geometria logica pannelli (cm)
│   ├── assembly_spec.py    # nome assieme, moduli, wrap panel_specs
│   ├── cutlist.py, xilog_export.py
├── freecad_addon/
│   ├── __init__.py
│   └── FurnitureAI/
│       ├── InitGui.py, FurnitureAICommands.py
│       ├── wizard_dialog.py    # UI allineata Fusion
│       └── freecad_geometry.py # assiemi FreeCAD
├── InitGui.py              # shim Mod/ (fix __file__ + import package)
├── fusion_addin/
├── postprocessor/, tlg_parser/
└── docs/
    ├── AGENT_RECAP.md      # questo file
    └── FREECAD_INSTALL.md
```

---

## Sessione 2026-05-19 — completato

### Fix installazione FreeCAD

| Problema | Soluzione |
|----------|-----------|
| `furniture_core` non importabile | Junction `Mod\Furniture-ai` → repo completo |
| `relative import` / workbench assente | `InitGui.py` root: `importlib.import_module("FurnitureAI.InitGui")` + `__init__.py` |
| `name '__file__' is not defined` | Fallback `inspect.stack()` in `InitGui.py` (root e workbench) |

**CAD testato:** FreeCAD **1.0.2** (non solo 1.1). Workbench visibile dopo fix.

### Allineamento Fusion → FreeCAD

| Fusion | FreeCAD (ora) |
|--------|----------------|
| Component + corpi `Fianco_SX`, … | `App::Part` mobile + sotto-assiemi pannello |
| `ModularProject.add_cabinet_module` | Comando **Aggiungi modulo** (`FurnitureAI_AddModule`) |
| Wizard (32mm, fori, ante, schienale, zoccolo) | `wizard_dialog.py` stessi gruppi |
| Posizione schienale per tipo montaggio | `panel_specs._schienale_position_y()` |

### Comandi workbench

| Comando | ID |
|---------|-----|
| Wizard mobili | `FurnitureAI_Wizard` |
| Aggiungi modulo | `FurnitureAI_AddModule` |
| Lista taglio | `FurnitureAI_Cutlist` |
| Export Xilog | `FurnitureAI_Xilog` |

### Test (senza CAD)

```powershell
cd Furniture-ai
python -m unittest tests.test_furniture_core tests.test_xilog_export -v
```

Attesi: **10 test OK** (inclusi `assembly_spec`, schienale arretrato).

---

## Installazione FreeCAD (Windows)

```powershell
git clone https://github.com/house79-gex/Furniture-ai.git C:\CAD\Furniture-ai
New-Item -ItemType Directory -Force -Path "$env:APPDATA\FreeCAD\Mod"
cmd /c mklink /J "%APPDATA%\FreeCAD\Mod\Furniture-ai" "C:\CAD\Furniture-ai"
```

Riavviare FreeCAD → **Visualizza → Workbench → FurnitureAI**.

Dettagli e troubleshooting: `docs/FREECAD_INSTALL.md`

### Verifica rapida in console FreeCAD

Dopo aver selezionato workbench **FurnitureAI**:

```python
from furniture_core.panel_specs import build_panel_specs
print(len(build_panel_specs({"tipo": "Mobile Base", "larghezza": 80, "altezza": 90, "profondita": 60})))
# Atteso: 8
```

---

## Limitazioni note

| Area | Stato |
|------|--------|
| Fori 3D (32mm, spinatura, cerniere) | Flag wizard sì; geometria **no** (Fusion e FreeCAD) |
| Ante / cassetti 3D | Parametri sì; geometria **no** |
| Layout modulare FreeCAD | Solo fila lineare (`Modulo_N`); Fusion ha anche griglia/L |
| Materiali FreeCAD | Non implementati |
| `furniture_generator.py` Fusion | Non ancora usa solo `panel_specs` |
| `ai_client` | Solo in `fusion_addin/lib/` |

---

## Roadmap — prossime sessioni

### Priorità alta

1. [ ] **Fori PartDesign** su FreeCAD (Hole + pattern da regole in `furniture_core`)
2. [ ] **Ante e cassetti** in `panel_specs` + `freecad_geometry`
3. [ ] **Refactor Fusion** `furniture_generator` → loop su `build_panel_specs` (una fonte geometrica)
4. [ ] Layout modulare **griglia / L** in FreeCAD (portare logica da `modular_system.py`)

### Priorità media

5. [ ] Spostare parser/AI fallback in `furniture_core`
6. [ ] Export Xilog per singolo pannello selezionato
7. [ ] Upgrade/test su **FreeCAD 1.1** quando disponibile

### Manutenzione

8. [ ] Verificare repo **privato** (`docs/REPO_PRIVATO.md`)
9. [ ] Materiali FreeCAD (opzionale)

---

## File chiave

| File | Ruolo |
|------|--------|
| `furniture_core/panel_specs.py` | Posizioni/dimensioni pannelli (cm) |
| `furniture_core/assembly_spec.py` | Nomi assieme e moduli |
| `freecad_addon/FurnitureAI/freecad_geometry.py` | Creazione assiemi FreeCAD |
| `freecad_addon/FurnitureAI/wizard_dialog.py` | UI wizard |
| `InitGui.py` (root repo) | Entry point Mod/ — **non rompere `__file__` fallback** |
| `fusion_addin/lib/furniture_wizard.py` | Riferimento UI Fusion |
| `fusion_addin/lib/modular_system.py` | Riferimento layout modulare Fusion |

---

## Convenzioni

- Commenti/doc utente: **italiano**; codice: **inglese**
- Unità wizard: **cm**; FreeCAD interno: **mm** (`× 10`)
- Commit: solo su richiesta utente
- Aggiornare **questo file** a ogni milestone

---

## Prompt per riprendere

```text
Leggi docs/AGENT_RECAP.md nel repo Furniture-ai.
Continua dalla roadmap (es. fori PartDesign su FreeCAD).
FreeCAD 1.0.2+ sul PC utente, rispondi in italiano.
```

---

## Stato git

- Branch: `main`
- Remote: `origin` → `https://github.com/house79-gex/Furniture-ai.git`
- Ultima milestone: `41630d7` — allineamento assiemi FreeCAD + fix workbench (2026-05-19)

---

*Fine recap — aggiornare a ogni milestone significativa.*
