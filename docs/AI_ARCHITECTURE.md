# Architettura IA Multimodale - FurnitureAI

## Panoramica

FurnitureAI integra un'architettura IA multimodale per supportare diverse modalità di input e intelligenza:

- **LLM (Large Language Model)**: Generazione automatica layout cucine, suggerimenti parametri
- **Vision**: Analisi piante 2D, riconoscimento stili da foto
- **Speech**: Comandi vocali, trascrizione descrizioni

## Architettura

```
fusion_addin/lib/ai/
├── __init__.py           # Modulo principale
├── llm_client.py         # Client LLM (Llama 3.1/3.2)
├── vision_client.py      # Client Vision (LLaVA - futuro)
└── speech_client.py      # Client Speech (Whisper - futuro)
```

## Modelli Consigliati

### 1. LLM - Layout e Suggerimenti ✅ ATTIVO

**Modello**: Llama 3.2 3B Instruct (già funzionante) o Llama 3.1 8B Instruct (consigliato)

**Endpoint**: LM Studio (default) o Ollama

**Funzionalità**:
- Generazione layout cucine da descrizione testuale
- Suggerimenti parametri mobili intelligenti
- Validazione coerenza dimensioni
- Calcolo ferramenta necessaria

**Esempio Input**:
```
"Cucina a L, 4x3 metri, con isola centrale, 5 moduli base, 4 pensili, stile moderno minimalista"
```

**Esempio Output**:
```json
{
  "layout_type": "L-shape",
  "room_dimensions": {"width": 400, "depth": 300},
  "modules": [
    {"type": "base", "width": 60, "position": {"wall": "north", "x": 0}},
    {"type": "base", "width": 80, "position": {"wall": "north", "x": 60}, "features": ["sink"]},
    ...
  ],
  "worktop": {"material": "laminato", "thickness": 2},
  "style": {"door_type": "flat", "finish": "opaco", "color": "bianco"}
}
```

**Modelli Testati**:
- ✅ Llama 3.2 3B Instruct (veloce, 4GB RAM, buoni risultati)
- ✅ Llama 3.1 8B Instruct (migliore qualità, 8GB RAM)
- ⚠️ Llama 2 7B (funziona ma meno accurato)

### 2. Vision - Analisi Piante e Stili 🔮 FUTURO

**Modello**: LLaVA 1.6 13B (non ancora implementato)

**Funzionalità Pianificate**:
- Upload pianta 2D → riconoscimento dimensioni, porte, finestre
- Upload foto cucina → estrazione stile, colori, materiali
- Estrazione quote da disegni tecnici (OCR + Vision)
- Confronto stili per compatibilità

**Esempio Vision Input**: Foto cucina moderna
**Esempio Vision Output**:
```json
{
  "door_style": "modern_flat",
  "material": "matte_lacquer",
  "color": "#FFFFFF",
  "handles": "integrated_groove",
  "finish": "opaco"
}
```

**Requisiti**:
- GPU con 16GB+ VRAM per LLaVA 13B
- Oppure LLaVA 7B quantizzato (8GB VRAM)

### 3. Speech - Comandi Vocali 🔮 FUTURO

**Modello**: Whisper Medium (non ancora implementato)

**Funzionalità Pianificate**:
- Registrazione comando vocale → parametri mobile
- Trascrizione descrizione parlata → testo per LLM
- Supporto multilingua (italiano primario)

**Esempio Speech Input**: 
```
[Registra] "Crea un pensile largo 80 centimetri, alto 70, profondità 35, con 2 ante"
```

**Esempio Speech Output**:
```json
{
  "larghezza": 80,
  "altezza": 70,
  "profondita": 35,
  "num_ante": 2
}
```

**Requisiti**:
- Whisper Medium: ~5GB RAM
- Libreria `faster-whisper` per inferenza veloce

## Setup LM Studio (ATTIVO)

### Installazione

1. **Download LM Studio**: https://lmstudio.ai/
2. **Avvia LM Studio**
3. **Download Modello**:
   - Cerca "Llama 3.2 3B Instruct" (veloce, 4GB)
   - Oppure "Llama 3.1 8B Instruct" (migliore qualità, 8GB)
4. **Avvia Server Locale**:
   - Tab "Local Server"
   - Porta: 1234 (default)
   - Seleziona modello
   - Click "Start Server"

### Configurazione FurnitureAI

1. Apri Fusion 360
2. Pannello CREA → **Configura IA**
3. Inserisci:
   - **Endpoint**: `http://localhost:1234`
   - **Modello**: `llama-3.2-3b-instruct`
4. Click **Testa Connessione**
5. Salva

### Verifica Funzionamento

```python
# In Fusion 360 Python Console
from fusion_addin.lib.ai import LLMClient

llm = LLMClient()
layout = llm.generate_kitchen_layout("cucina lineare 3 metri con lavello centrale")
print(layout)
```

## Roadmap Implementazione

### Fase 1: LLM Base ✅ COMPLETATA
- [x] Client LLM generico
- [x] Integrazione LM Studio/Ollama
- [x] Generazione layout cucine
- [x] Suggerimenti parametri mobili
- [x] Fallback senza IA

### Fase 2: LLM Avanzato (Q1 2026)
- [ ] Fine-tuning su dataset mobili italiani
- [ ] Ottimizzazione posizionamento moduli
- [ ] Calcolo automatico listino prezzi
- [ ] Esportazione preventivi PDF

### Fase 3: Vision (Q2 2026)
- [ ] Integrazione LLaVA 1.6
- [ ] Upload e analisi piante 2D
- [ ] Riconoscimento stili da foto
- [ ] OCR dimensioni quotate

### Fase 4: Speech (Q3 2026)
- [ ] Integrazione Whisper
- [ ] Comando vocale mobile
- [ ] Dettatura descrizione
- [ ] Multilingua (italiano, inglese, tedesco)

### Fase 5: Multimodale Completo (Q4 2026)
- [ ] Workflow ibrido: voice → LLM → vision → 3D
- [ ] AR preview su tablet
- [ ] Agente autonomo progettazione completa

## Performance e Requisiti

### LLM (Llama 3.2 3B) - Attivo
- **RAM**: 4GB
- **VRAM**: 0GB (CPU only)
- **Tempo risposta**: 5-15 secondi
- **Qualità**: Buona per layout base

### LLM (Llama 3.1 8B) - Consigliato
- **RAM**: 8GB
- **VRAM**: 8GB (GPU) oppure 0GB (CPU, più lento)
- **Tempo risposta**: 3-10 secondi (GPU) / 15-30 secondi (CPU)
- **Qualità**: Ottima per layout complessi

### Vision (LLaVA 13B) - Futuro
- **RAM**: 16GB
- **VRAM**: 16GB (GPU necessaria)
- **Tempo risposta**: 5-15 secondi per immagine

### Speech (Whisper Medium) - Futuro
- **RAM**: 5GB
- **VRAM**: 0GB (CPU)
- **Tempo risposta**: 1-3 secondi per 10 secondi audio

## API e Integrazioni

### LLM API

```python
from fusion_addin.lib.ai import LLMClient

# Inizializza
llm = LLMClient(endpoint='http://localhost:1234', model='llama-3.1-8b-instruct')

# Genera layout cucina
layout = llm.generate_kitchen_layout("cucina a L con isola")

# Ottimizza posizionamento
optimized = llm.optimize_module_placement(layout['modules'], 400, 300)

# Suggerisci ferramenta
hardware = llm.suggest_hardware({
    'larghezza': 80, 'altezza': 90, 'profondita': 60,
    'num_ante': 2, 'num_cassetti': 3, 'num_ripiani': 2
})
```

### Vision API (Futuro)

```python
from fusion_addin.lib.ai import VisionClient

vision = VisionClient()

# Analizza pianta
dimensions = vision.analyze_floor_plan("pianta_cucina.jpg")

# Analizza stile
style = vision.analyze_style_photo("foto_cucina_moderna.jpg")
```

### Speech API (Futuro)

```python
from fusion_addin.lib.ai import SpeechClient

speech = SpeechClient()

# Trascrivi audio
text = speech.transcribe("comando_vocale.wav", language='it')

# Comando vocale live
command = speech.voice_to_command(duration=5)
```

## Troubleshooting

### LM Studio non si connette
1. Verifica che LM Studio sia avviato
2. Controlla porta 1234 (tab Local Server)
3. Verifica firewall non blocchi localhost:1234

### Risposte LLM incoerenti
1. Usa modello più grande (8B invece di 3B)
2. Abbassa temperatura (0.3 → 0.1)
3. Fornisci descrizione più dettagliata

### Memoria insufficiente
1. Usa modelli quantizzati (Q4, Q5)
2. Riduci max_tokens nelle chiamate
3. Chiudi altre applicazioni

## Risorse

- **LM Studio**: https://lmstudio.ai/
- **Ollama**: https://ollama.ai/
- **Llama Models**: https://llama.meta.com/
- **LLaVA**: https://llava-vl.github.io/
- **Whisper**: https://github.com/openai/whisper

## Licenza e Privacy

- Tutti i modelli IA girano **localmente** sul PC dell'utente
- Nessun dato inviato a server esterni
- Privacy completa su progetti e misure
- Modelli open-source (Llama, LLaVA, Whisper)
