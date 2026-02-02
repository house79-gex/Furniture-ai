# FurnitureAI - Add-in Fusion 360 per Progettazione Mobili

Add-in completo per Autodesk Fusion 360 per la progettazione parametrica di mobili in legno con integrazione IA locale e post-processore Xilog Plus per CNC SCM Record 130TV (NUM 1050).

## 🎯 Caratteristiche Principali

### Add-in Fusion 360
- **Wizard parametrico** con interfaccia in italiano per progettazione guidata
- **5 template mobili**: Mobile Base, Pensile, Anta, Cassetto, Armadio
- **Sistema 32mm** per foratura standardizzata
- **Ferramenta automatica**: cerniere Ø35, spinatura Ø8, fori reggi-ripiano Ø5
- **Generazione 3D parametrica** con componenti separati (fianchi, ripiani, ante, schienali, zoccolo)
- **Validazioni automatiche** di dimensioni, spessori e interassi

### Post-processore Xilog Plus
- Generazione codice ottimizzato per **SCM Record 130TV** (NUM 1050)
- Supporto comandi: **XB, XBO, XBR, XG0, XL2P, XA2P, XGIN/XGOUT**
- **Gestione multi-faccia** (F=1..5) con trasformazione coordinate
- **Auto-selezione utensili** da libreria TLG
- Supporto forature standard: Ø5, Ø6, Ø8, Ø10, Ø12, Ø16, Ø35
- Ottimizzazione percorsi e movimenti

### Integrazione IA Locale
- Supporto **Ollama/LM Studio** con modelli leggeri (Llama 3 8B/3B quantizzati)
- **Parsing descrizioni testuali** → parametri mobili
- **Suggerimenti tecnici** automatici (ferramenta, dimensioni, accorgimenti)
- **Validazione coerenza** parametri con feedback IA
- Funziona su hardware consumer (testato su i7-7700, 32GB RAM, GTX 1050 Ti)

## 📋 Prerequisiti

### Software
- **Autodesk Fusion 360** (versione corrente)
- **Python 3.7+** (incluso in Fusion 360)
- **Ollama** o **LM Studio** per IA locale (opzionale)

### Hardware Minimo
- Sistema operativo: Windows 10/11 o macOS 10.14+
- RAM: 8GB (16GB+ consigliati)
- Per IA locale: 16GB+ RAM, GPU opzionale per accelerazione

## 🚀 Installazione

### 1. Installazione Add-in Fusion 360

#### Windows
1. Scarica/clona questa repository
2. Copia la cartella `fusion_addin` in:
   ```
   %APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FurnitureAI
   ```
3. Avvia Fusion 360
4. Vai su **Utilità** → **ADD-INS** → **Scripts and Add-Ins**
5. Seleziona tab **Add-Ins**
6. Clicca **FurnitureAI** e premi **Run**

#### macOS
1. Scarica/clona questa repository
2. Copia la cartella `fusion_addin` in:
   ```
   ~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/FurnitureAI
   ```
3. Avvia Fusion 360
4. Vai su **Utilità** → **ADD-INS** → **Scripts and Add-Ins**
5. Seleziona tab **Add-Ins**
6. Clicca **FurnitureAI** e premi **Run**

### 2. Installazione Dipendenze Python (Opzionale per IA)

Per abilitare l'integrazione IA, installa il modulo `requests`:

```bash
# Trova il Python di Fusion 360
# Windows: C:\Users\<username>\AppData\Local\Autodesk\webdeploy\production\<hash>\Python\python.exe
# macOS: /Users/<username>/Library/Application Support/Autodesk/webdeploy/production/<hash>/Python.framework/Versions/Current/bin/python3

# Installa requests
<path-to-fusion-python> -m pip install requests
```

### 3. Configurazione IA Locale (Opzionale)

**NOTA IMPORTANTE:** L'integrazione IA è completamente **opzionale**. L'add-in funziona perfettamente anche **offline** senza IA configurata. Se l'IA non è disponibile, vengono automaticamente forniti suggerimenti di fallback basati su regole standard.

#### Installazione Ollama
1. Scarica Ollama da https://ollama.ai
2. Installa e avvia il servizio
3. Scarica modello consigliato:
   ```bash
   ollama pull llama3:8b
   ```

#### Configurazione in FurnitureAI
1. In Fusion 360, apri il pannello **FurnitureAI**
2. Clicca **Configura IA**
3. Inserisci endpoint: `http://localhost:11434` (default Ollama)
4. Salva configurazione

#### Comportamento IA Stub
L'add-in include un **sistema di fallback intelligente**:
- Se l'IA non è disponibile o non risponde entro 2 secondi, vengono usati suggerimenti standard
- Parsing della descrizione testuale tramite regex (estrae dimensioni, numero ripiani/ante/cassetti)
- Suggerimenti tecnici basati su best practices dell'industria del mobile
- **Nessun blocco dell'esecuzione** se l'IA fallisce

Vantaggi del sistema di fallback:
- Funziona completamente offline
- Risposta istantanea (nessun timeout)
- Basato su standard consolidati del settore arredo
- Nessuna dipendenza da servizi esterni

## 📖 Utilizzo

### Wizard Mobili

1. In Fusion 360, vai al pannello **CREATE** → **FurnitureAI**
2. Clicca **Wizard Mobili**
3. Seleziona **Tipo Mobile** (Base, Pensile, Anta, Cassetto, Armadio)
4. Inserisci **Dimensioni**:
   - Larghezza (L): 20-300 cm
   - Altezza (H): 20-300 cm
   - Profondità (P): 20-100 cm
5. Configura **Parametri**:
   - Spessore pannello: 1.0-5.0 cm (default 1.8 cm)
   - Spessore schienale: 0.3-2.0 cm (default 0.6 cm)
   - Numero ripiani: 0-10
   - Sistema 32mm: attiva per foratura standardizzata
6. **Fori e Ferramenta**:
   - Fori reggi-ripiano Ø5 (sistema 32mm)
   - Spinatura Ø8 (assemblaggio)
   - Cerniere Ø35 (per ante)
7. **Ante e Cassetti**: specifica quantità
8. **Zoccolo**: attiva e imposta altezza

#### Utilizzo IA (Opzionale)
1. Nella sezione **Assistente IA**, attiva **Usa IA per suggerimenti**
2. Descrivi il mobile in linguaggio naturale, es:
   ```
   Mobile base cucina largo 80cm con 2 ripiani e 2 ante
   ```
3. L'IA fornirà suggerimenti su dimensioni, ferramenta e accorgimenti
4. Clicca **OK** per generare il mobile

### Generazione Codice Xilog Plus

Il post-processore può essere usato in due modi:

#### 1. Da Script Python
```python
from postprocessor.xilog_generator import XilogGenerator
from tlg_parser.tlg_library import TLGLibrary

# Inizializza
tlg = TLGLibrary()  # Usa libreria default
gen = XilogGenerator(tlg)

# Definisci pezzo
gen.add_header('Mobile_Base', (800, 600, 18))

# Aggiungi lavorazioni
gen.add_dowel_holes([(50, 50), (750, 50)], diameter=8.0, depth=40.0)
gen.add_hinge_holes([(50, 150), (50, 450)])

# Genera codice
gen.add_safety_notes()
gen.add_footer()
gen.save_to_file('output.xilog')
```

#### 2. Esegui Esempi
```bash
cd examples
python generate_examples.py
```

Questo genera file di esempio in `examples/xilog_output/`.

### Libreria Utensili TLG

La libreria TLG predefinita include:

**Gruppo Foratura Verticale (T=1..12)**
- T=1,8: Ø5 mm
- T=2,9: Ø6 mm
- T=3,10: Ø8 mm
- T=4,11: Ø10 mm
- T=5,12: Ø12 mm
- T=6: Ø16 mm
- T=7: Ø35 mm (cerniere)

**Foratura Orizzontale X (T=42,43,62,63)**
- T=42,43: Ø8 mm (facce 2,3)
- T=62,63: Ø5 mm (facce 2,3)

**Foratura Orizzontale Y (T=64,65)**
- T=64,65: Ø8 mm (facce 4,5)

**Mandrino Principale (T=101..196)**
- T=101-106: Frese Ø6-20 mm
- T=110: Punta Ø35 mm

**Aggregato Serratura (T=280)**
- T=280: Ø16 mm

Per usare libreria TLG personalizzata:
```python
tlg = TLGLibrary('/path/to/serr0142.tlg')
```

## 📁 Struttura Repository

```
Furniture-ai/
├── fusion_addin/              # Add-in Fusion 360
│   ├── FurnitureAI.py        # Entry point
│   ├── FurnitureAI.manifest  # Manifest add-in
│   └── lib/                  # Moduli Python
│       ├── ui_manager.py     # Gestione UI
│       ├── furniture_wizard.py # Wizard parametrico
│       ├── furniture_generator.py # Generazione 3D
│       ├── ai_client.py      # Client IA locale
│       └── config_manager.py # Configurazione
├── postprocessor/            # Post-processore Xilog Plus
│   └── xilog_generator.py   # Generatore codice
├── tlg_parser/               # Parser libreria utensili
│   └── tlg_library.py       # Gestione TLG
├── examples/                 # Esempi e test
│   ├── generate_examples.py # Script generazione esempi
│   └── xilog_output/        # Output esempio
│       ├── mobile_base_esempio.xilog
│       └── anta_esempio.xilog
├── docs/                     # Documentazione
└── README.md                 # Questo file
```

## 🔧 Specifiche Tecniche CNC

**SCM Record 130TV (NUM 1050)**
- Controllo: NUM 1050
- Assi: X, Y, Z, C (C non continuo)
- Campo lavoro: 2930 x 1300 mm
- Passaggio pezzo Z: 280 mm
- Mandrino principale: 14kW HSK63F, 12 posizioni
- Gruppo foratura: 18 mandrini verticali
- Aggregato serratura: 3kW, Ø16 max

**Facce di Lavoro**
- F=1: Faccia superiore (foratura verticale)
- F=2: Faccia anteriore (foratura orizzontale X, retro)
- F=3: Faccia posteriore (foratura orizzontale X, fronte)
- F=4: Faccia destra (foratura orizzontale Y)
- F=5: Faccia sinistra (foratura orizzontale Y)

## 🤖 Configurazione IA

### Modelli Consigliati (Hardware Consumer)

**Per i7-7700, 32GB RAM, GTX 1050 Ti:**
- **Llama 3 8B Q4**: Ottimo compromesso qualità/velocità
- **Llama 3.1 3B Q8**: Ultra veloce, qualità buona
- **Phi-3 Mini 3.8B**: Eccellente per task tecnici

### Endpoint Supportati
- Ollama: `http://localhost:11434`
- LM Studio: `http://localhost:1234`
- Personalizzato: configurabile da UI

### Funzioni IA

1. **Parsing Descrizioni**: Converte testo → parametri numerici
2. **Suggerimenti Tecnici**: Ferramenta, dimensioni, best practices
3. **Validazione Coerenza**: Analizza parametri per problemi potenziali

**Fallback automatico:** Tutte le funzioni sopra sono disponibili anche senza IA, utilizzando parsing basato su regex e regole standard.

## 📝 Esempi e Test

### File di Test
Nella cartella `examples/` trovi il file `parametri_test.md` con 5 configurazioni di test complete:
1. **Mobile Base Cucina Standard** (80x90x60, 2 ripiani, 2 ante)
2. **Pensile Sospeso** (120x80x35, 1 ripiano, 2 ante)
3. **Mobile Base Minimo** (60x70x50, nessun ripiano)
4. **Armadio Grande** (200x220x60, 3 ripiani)
5. **Test Validazione Limiti** (dimensioni minime/massime)

### Test Manuale Rapido
1. Avvia Fusion 360
2. Carica add-in FurnitureAI (Scripts and Add-Ins → Add-Ins → Run)
3. Vai al pannello CREATE → FurnitureAI
4. Clicca "Wizard Mobili"
5. Usa parametri default o uno dei test dal file `parametri_test.md`
6. Clicca OK
7. Verifica che i componenti vengano creati correttamente

### Esempio 1: Mobile Base Cucina

```
Descrizione IA: "Mobile base cucina 80x90x60 con 2 ripiani e 2 ante"

Parametri generati:
- Larghezza: 80 cm
- Altezza: 90 cm
- Profondità: 60 cm
- Ripiani: 2
- Ante: 2
- Cerniere: 4 (2 per anta)
- Sistema 32mm: attivo
- Spinatura: attiva
```

### Esempio 2: Pensile Sospeso

```
Descrizione IA: "Pensile sospeso 120x80x35 con 1 ripiano e 2 ante"

Parametri generati:
- Larghezza: 120 cm
- Altezza: 80 cm
- Profondità: 35 cm
- Ripiani: 1
- Ante: 2
- Zoccolo: disattivato (pensile)
```

## 🐛 Risoluzione Problemi

### Add-in non appare in Fusion 360
- Verifica percorso installazione (vedi sezione Installazione)
- Assicurati che la cartella si chiami esattamente `FurnitureAI`
- Controlla permessi cartella (deve essere leggibile)
- Riavvia Fusion 360
- Controlla il log di Fusion 360 (Help → Text Commands → mostra eventuali errori)

### Errore "mobile creato ma senza geometria"
- **Risolto nella versione corrente**: la geometria ora viene creata correttamente
- Se persiste, controlla che i parametri siano nei limiti validi (20-300cm L/H, 20-100cm P)
- Verifica dimensioni nel browser di Fusion 360

### Errore importazione moduli
- Verifica installazione Python dependencies
- Usa Python incluso in Fusion 360

### IA non risponde
- **Comportamento normale:** Se l'IA non è disponibile, vengono usati automaticamente suggerimenti di fallback
- Non è necessario che l'IA funzioni per usare l'add-in
- Per verificare endpoint Ollama: `curl http://localhost:11434/api/version`
- Se vuoi usare l'IA, verifica che Ollama/LM Studio sia in esecuzione
- Verifica endpoint configurato nel pannello "Configura IA"

### Fori non visibili nel modello
- **Nota implementazione corrente:** Le funzioni per fori (reggipiano, cerniere, spinatura) sono implementate come stub documentati
- I fori non vengono effettivamente creati nel modello 3D in questa versione
- Le posizioni e specifiche sono calcolate e documentate per export futuro
- Per aggiungere fori reali: necessario implementare face selection e hole features nell'API Fusion 360

### Codice Xilog non valido
- Verifica dimensioni pezzo
- Controlla libreria TLG
- Valida profondità vs. max_depth utensile

## ⚙️ Stato Implementazione e Limitazioni

### ✅ Funzionalità Operative (v1.0)
- ✅ Wizard parametrico completo con UI in italiano
- ✅ Generazione geometria 3D base (fianchi, top, base, ripiani, schienale, zoccolo)
- ✅ Validazione parametri (dimensioni, spessori, numero ripiani)
- ✅ Sistema configurazione (salvataggio/caricamento config locale)
- ✅ AI client con fallback intelligente (funziona offline)
- ✅ Parsing descrizioni testuali (con e senza IA)
- ✅ Suggerimenti tecnici standard (ferramenta, dimensioni)
- ✅ Logging verso console Fusion 360
- ✅ Post-processore Xilog Plus (separato, già funzionante)

### 🚧 Limitazioni Correnti
- ⚠️ **Fori non creati fisicamente**: Le funzioni `add_shelf_holes`, `add_hinge_holes`, `add_dowel_holes` calcolano le posizioni ma non creano i fori nel modello 3D. Questo richiede implementazione complessa di face selection nell'API Fusion 360.
- ⚠️ **Ante e cassetti**: I parametri sono accettati ma i componenti non vengono generati (futura implementazione)
- ⚠️ **Sistema 32mm**: Validazione presente, ma i fori non sono creati fisicamente

### 🎯 Roadmap Futura
1. Implementazione completa fori 3D (hole features con face selection)
2. Generazione ante battenti con cerniere posizionate
3. Generazione cassetti con guide
4. Integrazione diretta con post-processore Xilog
5. Export automatico file .xilog da wizard
6. Preview 3D in tempo reale durante modifica parametri

### 📌 Note per Sviluppatori
- Il codice è strutturato per facilitare l'aggiunta dei fori reali
- Le posizioni sono già calcolate nelle funzioni stub
- Per implementare fori: vedere API `HoleFeature` di Fusion 360
- Esempio workflow: sketch su faccia → hole feature → pattern se necessario

## 🤝 Contributi

Contributi benvenuti! Apri issue o pull request su GitHub.

## 📄 Licenza

MIT License - Vedi file LICENSE per dettagli

## 👤 Autore

House79 - FurnitureAI Project

## 🔗 Collegamenti Utili

- [Autodesk Fusion 360 API](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A)
- [Ollama](https://ollama.ai)
- [LM Studio](https://lmstudio.ai)
- [SCM Group](https://www.scmgroup.com)

---

**Nota**: Questo add-in è fornito "as-is" senza garanzie. Testare sempre il codice generato prima dell'esecuzione su CNC reale.
