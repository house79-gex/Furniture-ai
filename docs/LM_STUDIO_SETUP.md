# Guida Setup LM Studio + Llama 3.2 3B Instruct

## Panoramica

Questa guida spiega come configurare LM Studio con Llama 3.2 3B Instruct per utilizzare l'intelligenza artificiale in FurnitureAI.

## Requisiti di Sistema

### Minimi (Llama 3.2 3B)
- **RAM**: 8GB (minimo 4GB liberi)
- **Spazio Disco**: 4GB per il modello
- **CPU**: Qualsiasi CPU moderna (Intel/AMD)
- **GPU**: Opzionale (accelera le risposte)

### Consigliati (Llama 3.1 8B)
- **RAM**: 16GB (minimo 8GB liberi)
- **Spazio Disco**: 8GB per il modello
- **CPU**: CPU 8+ core
- **GPU**: NVIDIA con 8GB+ VRAM (RTX 3060 o superiore)

## Passo 1: Download e Installazione LM Studio

### Windows
1. Vai su https://lmstudio.ai/
2. Click **Download for Windows**
3. Esegui installer `LMStudio-Setup.exe`
4. Segui procedura guidata
5. Avvia LM Studio

### macOS
1. Vai su https://lmstudio.ai/
2. Click **Download for Mac**
3. Apri file `.dmg`
4. Trascina LM Studio in Applicazioni
5. Avvia LM Studio

### Linux
1. Vai su https://lmstudio.ai/
2. Download versione Linux (AppImage)
3. Rendi eseguibile: `chmod +x LMStudio-*.AppImage`
4. Avvia: `./LMStudio-*.AppImage`

## Passo 2: Download Modello Llama 3.2 3B Instruct

### In LM Studio

1. **Scheda "Discover"** (icona bussola)
2. **Cerca**: `Llama 3.2 3B Instruct`
3. **Risultati consigliati**:
   - `bartowski/Llama-3.2-3B-Instruct-GGUF` ✅ CONSIGLIATO
   - `TheBloke/Llama-3.2-3B-Instruct-GGUF`
4. **Scegli quantizzazione**:
   - **Q4_K_M** (2.3GB) - Veloce, qualità buona ✅ CONSIGLIATO
   - **Q5_K_M** (2.8GB) - Qualità migliore, più lento
   - **Q8_0** (3.8GB) - Massima qualità, richiede più RAM

### Quantizzazioni Spiegate

- **Q4**: 4 bit per peso, veloce, usa ~3GB RAM
- **Q5**: 5 bit per peso, miglior bilanciamento qualità/velocità
- **Q8**: 8 bit per peso, quasi qualità originale, usa ~5GB RAM
- **K_M**: Variante "Medium" con mix di quantizzazioni per layer

**Per FurnitureAI consigliamo Q4_K_M**: ottimo compromesso velocità/qualità.

5. **Click Download** sul modello scelto
6. **Attendi completamento** (barra progresso in basso)

## Passo 3: Avvio Server Locale

### Configurazione Server

1. **Scheda "Local Server"** (icona server)
2. **Seleziona modello**:
   - Dropdown: `Llama-3.2-3B-Instruct-Q4_K_M.gguf`
3. **Configurazione parametri**:
   - **Context Length**: 4096 (default)
   - **Temperature**: 0.3 (creatività moderata)
   - **Max Tokens**: 2000 (lunghezza risposta)
4. **Porta**: 1234 (default FurnitureAI)
5. **Click "Start Server"**

### Verifica Server Attivo

Dovresti vedere:
```
✓ Server running on http://localhost:1234
✓ Model loaded: Llama-3.2-3B-Instruct-Q4_K_M.gguf
```

### Test Manuale (Opzionale)

Nella scheda **Chat** di LM Studio:
```
Input: "Suggerisci dimensioni per un mobile base cucina standard italiano"

Output atteso: "Per un mobile base cucina standard italiano, le dimensioni tipiche sono:
- Larghezza: 60 cm (modulo standard)
- Altezza: 90 cm (con zoccolo 10 cm + base 80 cm)
- Profondità: 60 cm
..."
```

## Passo 4: Configurazione FurnitureAI

### In Fusion 360

1. **Apri Fusion 360**
2. **Workspace Design** → Pannello **CREA**
3. **Cerca comando**: "Configura IA"
4. **Click "Configura IA"**

### Dialog Configurazione

1. **Endpoint IA**: `http://localhost:1234`
2. **Modello**: `llama-3.2-3b-instruct`
3. **Click "Testa Connessione"**

**Output Atteso**:
```
✓ Connessione riuscita!
IA disponibile su http://localhost:1234
```

4. **Click OK** per salvare

### File Config Creato

Verrà creato automaticamente:
```
~/.furniture_ai/config.json
```

Contenuto:
```json
{
  "ai_endpoint": "http://localhost:1234",
  "ai_model": "llama-3.2-3b-instruct",
  "tlg_path": "",
  "xilog_output_path": ""
}
```

## Passo 5: Test Funzionalità IA

### Test 1: Wizard Mobili con IA

1. **Pannello CREA** → **Wizard Mobili**
2. **Abilita checkbox**: "Usa IA per suggerimenti"
3. **Descrizione**: "mobile base cucina 80cm con 2 ante e 1 cassetto"
4. **Click "Ottieni Suggerimenti IA"**

**Output Atteso**:
```
Suggerimenti IA:

• Tipo: Mobile base cucina
• Dimensioni tipiche: L 80cm, H 90cm, P 60cm
• Con zoccolo 10cm
• Ante: 2 (apertura a battente)
• Cerniere: 4 (2 per anta)
• Cassetto: 1 con guide a sfera

Accorgimenti costruttivi:
• Spessore pannello: 18mm standard
• Schienale: 6mm
• Sistema 32mm per fori reggipiano
...
```

### Test 2: Parametri Automatici

1. Dopo suggerimenti IA, i campi dovrebbero popolarsi:
   - **Larghezza**: 80
   - **Altezza**: 90
   - **Profondità**: 60
   - **Num Ripiani**: 2
   - **Num Ante**: 2

2. **Click "Genera Mobile"**
3. **Verifica**: Mobile 3D creato con pannelli rettangolari (non deformati)

## Troubleshooting

### Problema: "Connessione fallita"

**Cause**:
1. LM Studio non avviato → Avvia LM Studio e Start Server
2. Modello non caricato → Seleziona modello in Local Server
3. Porta diversa → Verifica porta sia 1234

**Verifica Manuale**:
```bash
# Windows PowerShell / Linux/macOS Terminal
curl http://localhost:1234/v1/models

# Output atteso:
{
  "object": "list",
  "data": [{"id": "llama-3.2-3b-instruct", ...}]
}
```

### Problema: Risposte lente (>30 secondi)

**Soluzioni**:
1. **Usa GPU se disponibile**:
   - LM Studio → Settings → GPU: Seleziona GPU
2. **Riduci context length**:
   - Local Server → Context Length: 2048 (invece di 4096)
3. **Usa modello più piccolo**:
   - Llama 3.2 1B invece di 3B

### Problema: Risposte incoerenti / sbagliate

**Soluzioni**:
1. **Abbassa temperature**:
   - Local Server → Temperature: 0.1 (più deterministico)
2. **Aumenta max tokens**:
   - Local Server → Max Tokens: 3000
3. **Usa modello più grande**:
   - Llama 3.1 8B per qualità superiore

### Problema: Errore "Out of Memory"

**Soluzioni**:
1. **Chiudi altre applicazioni** (browser, IDE)
2. **Usa quantizzazione più bassa**:
   - Q4 invece di Q5/Q8
3. **Aggiungi RAM** (se possibile)

### Problema: GPU non rilevata

**Windows**:
1. Installa NVIDIA CUDA Toolkit 11.8+
2. Riavvia LM Studio
3. Settings → GPU: Dovrebbe apparire

**Linux**:
1. Installa driver NVIDIA proprietari
2. Installa CUDA Toolkit
3. Riavvia

## Modelli Alternativi

### Se Llama 3.2 3B non funziona bene

1. **Llama 3.1 8B Instruct** (8GB RAM):
   - Cerca: `bartowski/Llama-3.1-8B-Instruct-GGUF`
   - Download: `Q4_K_M` (4.8GB)
   - Config FurnitureAI: `llama-3.1-8b-instruct`

2. **Llama 2 7B** (compatibilità massima):
   - Cerca: `TheBloke/Llama-2-7B-Chat-GGUF`
   - Download: `Q4_K_M`
   - Config FurnitureAI: `llama-2-7b-chat`

3. **Mistral 7B** (alternativa veloce):
   - Cerca: `TheBloke/Mistral-7B-Instruct-v0.2-GGUF`
   - Download: `Q4_K_M`
   - Config FurnitureAI: `mistral-7b-instruct`

## Ollama (Alternativa a LM Studio)

### Installazione Ollama

**Linux/macOS**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows**:
Download installer da https://ollama.ai/download

### Avvio Llama 3.2

```bash
# Download e avvia modello
ollama run llama3.2:3b

# Server parte automaticamente su porta 11434
```

### Config FurnitureAI per Ollama

1. **Configura IA** in Fusion 360
2. **Endpoint**: `http://localhost:11434`
3. **Modello**: `llama3.2:3b`

## Supporto e Risorse

### Link Utili
- **LM Studio**: https://lmstudio.ai/
- **Llama Models**: https://llama.meta.com/
- **Community Discord**: Discord LM Studio
- **GitHub FurnitureAI**: https://github.com/house79-gex/Furniture-ai

### Performance Benchmark

| Modello | RAM | Tempo Risposta | Qualità |
|---------|-----|----------------|---------|
| Llama 3.2 1B Q4 | 2GB | 3-5s | Basica |
| Llama 3.2 3B Q4 | 4GB | 5-15s | Buona ✅ |
| Llama 3.1 8B Q4 | 8GB | 10-20s | Ottima |
| Llama 3.1 8B Q5 | 10GB | 15-25s | Eccellente |

**CPU**: Intel i7 8th gen, 16GB RAM
**Con GPU (RTX 3060 12GB)**: Tempi ridotti 70% (3-7s per Llama 3.2 3B)

## Conclusione

Setup completato! Ora puoi:
- ✅ Usare IA per suggerimenti mobili
- ✅ Generare layout cucine automatici (in futuro)
- ✅ Parametri intelligenti da descrizione testuale
- ✅ Lavorare completamente offline

Buon lavoro con FurnitureAI! 🪑✨
