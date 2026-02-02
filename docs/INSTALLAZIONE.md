# Guida Installazione FurnitureAI

## Installazione Completa Passo-Passo

### Prerequisiti

1. **Autodesk Fusion 360** installato
2. **Python 3.7+** (incluso con Fusion 360)
3. **Git** (per clonare repository) oppure scaricare ZIP

### Passo 1: Scaricare Repository

#### Opzione A: Con Git
```bash
git clone https://github.com/house79-gex/Furniture-ai.git
cd Furniture-ai
```

#### Opzione B: Download ZIP
1. Vai su https://github.com/house79-gex/Furniture-ai
2. Clicca "Code" → "Download ZIP"
3. Estrai in una cartella locale

### Passo 2: Installare Add-in in Fusion 360

#### Windows

1. Apri Esplora File e naviga a:
   ```
   %APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns
   ```
   
2. Se la cartella non esiste, creala

3. Copia l'intera cartella `fusion_addin` nella directory AddIns e rinominala in `FurnitureAI`:
   ```
   %APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FurnitureAI
   ```

4. Verifica che la struttura sia:
   ```
   AddIns\
     └── FurnitureAI\
         ├── FurnitureAI.py
         ├── FurnitureAI.manifest
         └── lib\
             ├── __init__.py
             ├── ui_manager.py
             ├── furniture_wizard.py
             ├── furniture_generator.py
             ├── ai_client.py
             └── config_manager.py
   ```

#### macOS

1. Apri Finder e vai a:
   ```
   ~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns
   ```
   
   Suggerimento: Premi Cmd+Shift+G e incolla il percorso

2. Se la cartella non esiste, creala

3. Copia l'intera cartella `fusion_addin` e rinominala in `FurnitureAI`

4. Verifica la struttura come sopra

### Passo 3: Avviare Add-in in Fusion 360

1. Avvia/riavvia **Fusion 360**

2. Vai su **Utilità** (nella barra superiore) → **ADD-INS**

3. Nella finestra che si apre, seleziona tab **Add-Ins**

4. Dovresti vedere **FurnitureAI** nella lista

5. Seleziona **FurnitureAI** e clicca **Run**

6. (Opzionale) Spunta **Run on Startup** per avvio automatico

7. Clicca **Close**

8. Verifica che nel pannello **SOLID** (o **TOOLS**) sia apparso il pannello **FurnitureAI**

### Passo 4: Installare Dipendenze Python per IA (Opzionale)

L'integrazione IA richiede il modulo `requests`. Per installarlo:

#### Windows

1. Trova il Python di Fusion 360:
   ```
   C:\Users\<TUO_USERNAME>\AppData\Local\Autodesk\webdeploy\production\<HASH>\Python\python.exe
   ```
   
   Il `<HASH>` è un codice lungo alfanumerico. Usa Esplora File per trovarlo.

2. Apri **Prompt dei comandi** come Amministratore

3. Esegui:
   ```cmd
   "C:\Users\<TUO_USERNAME>\AppData\Local\Autodesk\webdeploy\production\<HASH>\Python\python.exe" -m pip install requests
   ```

#### macOS

1. Trova il Python di Fusion 360:
   ```
   /Users/<TUO_USERNAME>/Library/Application Support/Autodesk/webdeploy/production/<HASH>/Python.framework/Versions/Current/bin/python3
   ```

2. Apri **Terminale**

3. Esegui:
   ```bash
   "/Users/<TUO_USERNAME>/Library/Application Support/Autodesk/webdeploy/production/<HASH>/Python.framework/Versions/Current/bin/python3" -m pip install requests
   ```

### Passo 5: Configurare IA Locale (Opzionale)

#### Installare Ollama

1. Vai su https://ollama.ai

2. Scarica installer per il tuo sistema operativo

3. Installa Ollama

4. Apri Terminale/Prompt e scarica modello:
   ```bash
   ollama pull llama3:8b
   ```
   
   Oppure per hardware limitato:
   ```bash
   ollama pull llama3:3b
   ```

5. Verifica che Ollama sia in esecuzione:
   ```bash
   ollama list
   ```

#### Configurare in FurnitureAI

1. In Fusion 360, vai al pannello **FurnitureAI**

2. Clicca **Configura IA**

3. Inserisci endpoint: `http://localhost:11434`

4. Salva

## Verifica Installazione

### Test 1: Avvio Add-in
- ✅ Add-in appare in lista ADD-INS
- ✅ Pannello FurnitureAI visibile in Fusion 360
- ✅ Pulsanti "Wizard Mobili" e "Configura IA" cliccabili

### Test 2: Wizard Mobili
1. Clicca **Wizard Mobili**
2. Seleziona "Mobile Base"
3. Imposta dimensioni: L=80cm, H=90cm, P=60cm
4. Clicca OK
5. ✅ Mobile generato nel design

### Test 3: IA (se configurata)
1. Nel wizard, attiva **Usa IA per suggerimenti**
2. Descrivi: "mobile base 80x90x60 con 2 ripiani"
3. ✅ Appare finestra con suggerimenti

## Risoluzione Problemi

### Add-in non appare nella lista

**Causa**: Percorso installazione errato

**Soluzione**:
1. Verifica percorso esatto con:
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FurnitureAI`
   - macOS: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/FurnitureAI`
2. Verifica che `FurnitureAI.manifest` sia nella directory
3. Riavvia Fusion 360

### Errore "Module not found"

**Causa**: Dipendenze Python mancanti

**Soluzione**:
1. Installa `requests` come descritto in Passo 4
2. Verifica installazione:
   ```bash
   <path-to-fusion-python> -c "import requests; print(requests.__version__)"
   ```

### IA non risponde

**Causa**: Ollama non in esecuzione o endpoint errato

**Soluzione**:
1. Verifica Ollama:
   ```bash
   curl http://localhost:11434/api/version
   ```
2. Se non risponde, avvia Ollama
3. Verifica modello scaricato:
   ```bash
   ollama list
   ```
4. Controlla endpoint in "Configura IA"

### Errore durante generazione mobile

**Causa**: Parametri non validi

**Soluzione**:
1. Verifica dimensioni entro limiti:
   - Larghezza: 20-300 cm
   - Altezza: 20-300 cm
   - Profondità: 20-100 cm
2. Con Sistema 32mm, regola altezza per interassi multipli di 32mm

## Supporto

Per problemi o domande:
1. Apri issue su GitHub: https://github.com/house79-gex/Furniture-ai/issues
2. Includi:
   - Sistema operativo e versione
   - Versione Fusion 360
   - Log errore completo
   - Parametri usati

## Disinstallazione

Per disinstallare:

1. In Fusion 360: **Utilità** → **ADD-INS** → Seleziona **FurnitureAI** → **Remove**

2. Elimina cartella:
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FurnitureAI`
   - macOS: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/FurnitureAI`

3. (Opzionale) Elimina configurazione:
   - Windows/macOS: `~/.furniture_ai/config.json`
