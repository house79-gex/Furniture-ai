# AGENT_RECAP — FurnitureAI

> **Scopo:** handoff per continuare il lavoro su un altro PC o in una nuova sessione agente.  
> **Ultimo aggiornamento:** 2026-05-18  
> **Repository:** https://github.com/house79-gex/Furniture-ai  
> **Branch principale:** `main` (commit di riferimento: `0cdde15` o successivo)

---

## Contesto utente

| Aspetto | Dettaglio |
|---------|-----------|
| **Uso** | Personale (falegnameria / mobili semplici, non architettura complessa) |
| **CAD attuale** | Fusion 360 (già esperto), versione free con limitazioni |
| **Obiettivo** | FreeCAD 1.1 come piattaforma principale a lungo termine (più aperto, Python libero) |
| **CNC** | SCM Record 130TV (NUM 1050), post-processore **Xilog Plus** |
| **Linguaggio UI** | Italiano |
| **Repo** | Utente ha chiesto di renderlo **privato** — vedi `docs/REPO_PRIVATO.md` (non ancora verificato da agente se completato) |

---

## Decisioni architetturali (non invertire senza motivo)

1. **`furniture_core/`** = unico “cervello” condiviso (parametri, validazione, parser testo, pannelli, cutlist, export Xilog). **Nessuna dipendenza** da `adsk` o `FreeCAD` dentro il core.
2. **`fusion_addin/`** = UI + geometria Fusion (manutenzione, non sviluppo massiccio nuovo).
3. **`freecad_addon/FurnitureAI/`** = workbench FreeCAD 1.1 (destinazione principale nuove feature).
4. **`postprocessor/` + `tlg_parser/`** = già Python puro, riusati da core e esempi.
5. **Non** puntare a clone AutoCAD; interfaccia “familiare” Draft è opzionale e secondaria.

---

## Struttura repository

```text
Furniture-ai/
├── furniture_core/           # LOGICA CONDIVISA (priorità refactor futuro)
│   ├── models.py             # default per tipo mobile, normalize_params
│   ├── validation.py         # limiti L/H/P, spessori, ripiani
│   ├── parser_nl.py          # regex: "largo 80cm", "2 ripiani", ecc.
│   ├── panel_specs.py        # elenco pannelli (cm) senza CAD
│   ├── cutlist.py            # CSV/Excel da panel_specs
│   └── xilog_export.py       # .xilog multi-pannello da parametri
├── freecad_addon/FurnitureAI/
│   ├── InitGui.py            # registra workbench
│   ├── FurnitureAICommands.py # Wizard, Cutlist, Xilog
│   ├── wizard_dialog.py      # PySide2 dialog
│   └── freecad_geometry.py   # Part.makeBox → App::Part
├── Init.py / InitGui.py      # SHIM: installare TUTTA la repo in Mod/
├── fusion_addin/             # Add-in Autodesk Fusion 360
├── postprocessor/            # XilogGenerator
├── tlg_parser/               # TLGLibrary
├── WoodWorkingWizard/        # Codice legacy / nesting (preesistente)
├── tests/
│   ├── test_furniture_core.py
│   └── test_xilog_export.py
└── docs/
    ├── AGENT_RECAP.md        # questo file
    ├── FREECAD_INSTALL.md
    └── REPO_PRIVATO.md
```

---

## Cosa è stato implementato (sessione 2026-05-18)

### Commit principali su `main`

| Commit | Contenuto |
|--------|-----------|
| `fb016e8` | `furniture_core`, workbench FreeCAD, shim `InitGui.py`, test core |
| `0cdde15` | Export Xilog da wizard + `furniture_core/xilog_export.py` |

### FreeCAD 1.1 — comandi workbench

| Comando | ID | Funzione |
|---------|-----|----------|
| Wizard mobili | `FurnitureAI_Wizard` | Dialog parametri → genera `App::Part` con pannelli box |
| Lista taglio | `FurnitureAI_Cutlist` | Export CSV da `panel_specs` |
| Export Xilog | `FurnitureAI_Xilog` | File `.xilog` multi-pannello (spinatura, fori 32mm se flag attivi) |

### Fusion 360

- `fusion_addin/lib/furniture_generator.py` → `validate_parameters()` delega a `furniture_core` se importabile.
- Resto add-in **invariato** rispetto a prima del refactor (wizard, AI, geometria Fusion).

### Test (eseguire senza CAD)

```powershell
cd Furniture-ai
python -m unittest tests.test_furniture_core tests.test_xilog_export -v
```

Attesi: **8 test OK**.

---

## Installazione FreeCAD 1.1 (altro PC)

```powershell
git clone https://github.com/house79-gex/Furniture-ai.git C:\CAD\Furniture-ai
mklink /D "%APPDATA%\FreeCAD\Mod\Furniture-ai" "C:\CAD\Furniture-ai"
```

- Riavviare FreeCAD → **Visualizza → Workbench → FurnitureAI**
- Serve il **clone completo** (non solo `freecad_addon/`) per `furniture_core` e `postprocessor`.

Dettagli: `docs/FREECAD_INSTALL.md`

### Installazione Fusion (invariata)

Copiare `fusion_addin` in:

```text
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FurnitureAI
```

---

## Limitazioni note (Fusion e FreeCAD)

| Area | Stato |
|------|--------|
| Fori 3D reali (cerniere, 32mm, spinatura) | **Non** creati nel modello Fusion (stub documentati nel README) |
| Ante / cassetti 3D | Parametri accettati, geometria **non** generata |
| FreeCAD wizard | Solo pannelli box (fianchi, base, top, ripiani, schienale, zoccolo) |
| Xilog export | Programma **indicativo** per pannello (fori angolo / 32mm su fianchi); **non** CAM completo da geometria reale |
| `ai_client` | Ancora in `fusion_addin/lib/` — **non** spostato in `furniture_core` |

---

## Roadmap consigliata (prossime sessioni)

### Priorità alta

1. [ ] **Spostare parser/AI fallback** da `fusion_addin/lib/ai_client.py` → `furniture_core` (Fusion importa dal core).
2. [ ] **Fori PartDesign** su FreeCAD: Hole + pattern da regole `hardware_rules` nel core.
3. [ ] **Ante e cassetti** in `panel_specs` + `freecad_geometry`.
4. [ ] Testare workbench su FreeCAD **1.1** reale dell’utente; fix PySide2/PySide6 se crash.

### Priorità media

5. [ ] Macro Draft “interfaccia familiare” (snap, griglia, toolbar) — opzionale.
6. [ ] Export Xilog **per singolo pannello** selezionato nell’albero.
7. [ ] Integrare `cutlist` da geometria FreeCAD (bbox) oltre che da `panel_specs`.

### Priorità bassa / manutenzione Fusion

8. [ ] Allineare `furniture_generator` Fusion a `panel_specs` (stesse posizioni pannelli).
9. [ ] Verificare repo **privato** su GitHub (Settings → Danger Zone).

---

## File chiave da leggere prima di modificare

| File | Perché |
|------|--------|
| `furniture_core/panel_specs.py` | Geometria logica pannelli (cm) |
| `freecad_addon/FurnitureAI/freecad_geometry.py` | Creazione Part in FreeCAD |
| `furniture_core/xilog_export.py` | Bridge verso post-processore |
| `postprocessor/xilog_generator.py` | API comandi Xilog |
| `fusion_addin/lib/furniture_wizard.py` | UI Fusion (riferimento campi wizard) |
| `fusion_addin/lib/furniture_generator.py` | Geometria Fusion (da allineare al core) |

---

## Convenzioni codice

- **Commenti e doc utente:** italiano.
- **Codice (nomi variabili, classi):** inglese.
- **Unità wizard:** cm; **FreeCAD interno:** mm (`× 10` in `freecad_geometry.py`).
- **Non** fare refactor drive-by su `WoodWorkingWizard/` senza richiesta esplicita.
- **Commit:** solo se l’utente chiede (in questa sessione ha chiesto commit+push per il recap).

---

## Clone rapido su altro PC

```powershell
git clone https://github.com/house79-gex/Furniture-ai.git
cd Furniture-ai
git pull origin main
python -m unittest tests.test_furniture_core tests.test_xilog_export -q
```

Se il repo è **privato**, serve `gh auth login` o credenziali GitHub (PAT / SSH).

---

## Prompt suggerito per riprendere

```text
Leggi docs/AGENT_RECAP.md nel repo Furniture-ai.
Continua da roadmap priorità alta: [scegliere task, es. fori PartDesign su FreeCAD].
FreeCAD 1.1, uso personale, rispondi in italiano.
```

---

## Stato git atteso

- Branch: `main`
- Remote: `origin` → `https://github.com/house79-gex/Furniture-ai.git`
- Feature branch locale `feature/freecad-workbench` può essere eliminato dopo merge (già mergiato in `main`).

---

*Fine recap — aggiornare questo file a ogni milestone significativa.*
