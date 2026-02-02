# Guida Uso FurnitureAI

## Introduzione

FurnitureAI è un add-in per Fusion 360 che semplifica la progettazione di mobili in legno attraverso un wizard guidato, generazione parametrica 3D, e integrazione con IA locale per suggerimenti automatici.

## Interfaccia Utente

### Pannello FurnitureAI

Dopo l'installazione, il pannello FurnitureAI appare nella scheda **SOLID** o **TOOLS** con due comandi:

1. **Wizard Mobili**: Apre il wizard di progettazione guidata
2. **Configura IA**: Configura l'endpoint IA locale

## Wizard Mobili - Guida Completa

### Tipo Mobile

Seleziona uno dei 5 template predefiniti:

#### 1. Mobile Base
Mobile da terra con:
- Zoccolo regolabile
- Ripiani interni
- Ante e/o cassetti opzionali
- Uso tipico: cucina, bagno, soggiorno

**Esempio**: Mobile base cucina 80x90x60 con 2 ripiani e 2 ante

#### 2. Pensile
Mobile sospeso senza zoccolo:
- Più leggero
- Profondità ridotta (tipicamente 30-40cm)
- Ante a battente o vetro
- Uso tipico: pensili cucina, librerie alte

**Esempio**: Pensile cucina 120x80x35 con 2 ante

#### 3. Anta
Pannello per porta mobile:
- Fori cerniere preconfigurati
- Contorno sagomato opzionale
- Spessore personalizzabile
- Uso: ricambio o personalizzazione

**Esempio**: Anta 40x80 con 2 cerniere

#### 4. Cassetto
Cassetto completo con:
- Fianchi, fondo, fronte
- Predisposizione per guide
- Incastri opzionali
- Uso: cassetti modulari

**Esempio**: Cassetto 70x40x15

#### 5. Armadio
Mobile alto per guardaroba:
- Dimensioni maggiorate (H > 180cm)
- Ripiani spaziati
- Predisposizione per appendiabiti
- Zoccolo rinforzato

**Esempio**: Armadio 100x220x60 con 3 ripiani

### Dimensioni

Imposta le tre dimensioni principali:

- **Larghezza (L)**: 20-300 cm (default: 80 cm)
- **Altezza (H)**: 20-300 cm (default: 90 cm)
- **Profondità (P)**: 20-100 cm (default: 60 cm)

**Suggerimenti**:
- Mobili base: H=85-95 cm, P=55-65 cm
- Pensili: H=70-90 cm, P=30-40 cm
- Armadi: H=200-240 cm, P=55-65 cm

### Parametri

#### Spessore Pannello
Spessore dei pannelli principali (fianchi, ripiani, top, base):
- Range: 1.0-5.0 cm
- Default: 1.8 cm (standard)
- Comune: 1.6 cm, 1.8 cm, 2.5 cm

#### Spessore Schienale
Spessore del pannello posteriore:
- Range: 0.3-2.0 cm
- Default: 0.6 cm
- Comune: 0.4 cm, 0.6 cm

#### Numero Ripiani
Ripiani interni (esclusi top e base):
- Range: 0-10
- Default: 2
- Con Sistema 32mm: interassi multipli di 32mm

#### Sistema 32mm
Standard europeo per foratura ripiani:
- ✅ **Attivo**: Fori ogni 32mm sui fianchi
- ❌ **Disattivo**: Solo fori per ripiani fissi

**Quando usare**:
- ✅ Ripiani regolabili
- ✅ Conformità a standard
- ❌ Ripiani fissi permanenti

### Fori e Ferramenta

#### Fori Reggi-Ripiano (Ø5)
Fori per supporti ripiani regolabili:
- Diametro: 5mm
- Profondità: 12mm
- Passo: 32mm (se Sistema 32mm attivo)

#### Spinatura (Ø8)
Spinotti per assemblaggio pannelli:
- Diametro: 8mm
- Profondità: 40mm
- Posizioni: angoli e punti critici

**Quando usare**:
- ✅ Assemblaggio smontabile
- ✅ Resistenza strutturale
- ❌ Assembly incollato permanente

#### Numero Cerniere (Ø35)
Cerniere per ante a battente:
- Diametro: 35mm (standard Blum, Salice)
- Profondità: 13mm
- Range: 0-10
- Tipico: 2-4 per anta (in base ad altezza)

**Guida**:
- Anta H < 60cm: 2 cerniere
- Anta H 60-120cm: 3 cerniere
- Anta H > 120cm: 4+ cerniere

### Ante e Cassetti

#### Numero Ante
Ante a battente verticali:
- Range: 0-10
- Larghezza automatica: L / num_ante
- Con cerniere pre-forate se > 0

**Configurazioni comuni**:
- 0: mobile aperto (scaffale)
- 1: anta unica
- 2: ante doppie (più comune)
- 3-4: armadi larghi

#### Numero Cassetti
Cassetti frontali orizzontali:
- Range: 0-10
- Altezza automatica: (H - spessori) / num_cassetti
- Con guide laterali

### Zoccolo

#### Aggiungi Zoccolo
Base rialzata sotto mobile:
- ✅ **Con zoccolo**: mobile rialzato
- ❌ **Senza zoccolo**: mobile a terra

**Quando usare**:
- ✅ Mobili base (cucina, bagno)
- ✅ Protezione umidità pavimento
- ❌ Pensili sospesi

#### Altezza Zoccolo
Altezza dello zoccolo:
- Range: 5-20 cm
- Default: 10 cm
- Standard: 10-12 cm

### Assistente IA

#### Descrivi il Mobile
Campo di testo per descrizione in linguaggio naturale:

**Esempi**:
```
Mobile base cucina largo 80cm con 2 ripiani e 2 ante
```
```
Pensile sospeso 120x80x35 con anta unica in vetro
```
```
Armadio guardaroba 100x220x60 con 3 ripiani per abiti
```

#### Usa IA per Suggerimenti
- ✅ **Attivo**: IA analizza descrizione e fornisce suggerimenti
- ❌ **Disattivo**: solo parametri manuali

**Cosa fa l'IA**:
1. Estrae dimensioni da descrizione
2. Suggerisce numero ripiani appropriato
3. Consiglia ferramenta necessaria
4. Evidenzia accorgimenti costruttivi

## Esempi d'Uso

### Esempio 1: Mobile Base Cucina Standard

**Obiettivo**: Mobile base cucina 80x90x60 con 2 ripiani regolabili e 2 ante

**Parametri**:
- Tipo: Mobile Base
- Larghezza: 80 cm
- Altezza: 90 cm
- Profondità: 60 cm
- Spessore pannello: 1.8 cm
- Numero ripiani: 2
- Sistema 32mm: ✅
- Fori ripiani: ✅
- Spinatura: ✅
- Numero cerniere: 4 (2 per anta)
- Numero ante: 2
- Zoccolo: ✅, 10 cm

**Risultato**:
- Mobile completo con fianchi, top, base, 2 ripiani, schienale, zoccolo
- Fori sistema 32mm per regolazione ripiani
- 4 fori cerniere Ø35 per 2 ante
- Fori spinatura per assemblaggio

### Esempio 2: Pensile con IA

**Obiettivo**: Pensile cucina con aiuto IA

**Descrizione IA**:
```
Pensile cucina sospeso largo 120cm alto 80cm profondo 35cm con 2 ante
```

**IA Suggerisce**:
- Dimensioni: 120x80x35 cm
- 1 ripiano interno per stabilità
- 4 cerniere (2 per anta, ante larghe)
- Nessuno zoccolo (pensile)
- Spessore schienale 0.6 cm (ridotto)

**Parametri Finali** (dopo suggerimenti IA):
- Tipo: Pensile
- Dimensioni: 120x80x35 cm
- Ripiani: 1
- Ante: 2
- Cerniere: 4
- Zoccolo: ❌

### Esempio 3: Armadio Guardaroba

**Obiettivo**: Armadio 2 ante con appendiabiti

**Parametri**:
- Tipo: Armadio
- Dimensioni: 100x220x60 cm
- Ripiani: 3 (2 sopra, 1 basso per scarpe)
- Sistema 32mm: ❌ (ripiani fissi)
- Ante: 2
- Cerniere: 8 (4 per anta, alte)
- Zoccolo: ✅, 12 cm (rinforzato)

**Personalizzazioni Post-Generazione**:
- Aggiungere bastone appendiabiti manualmente
- Cassetti interni opzionali
- Mensole aggiuntive

## Output e Export

### Componenti Generati

Dopo OK, il wizard crea un componente Fusion con:

1. **Fianco_SX**: Fianco sinistro
2. **Fianco_DX**: Fianco destro
3. **Top**: Piano superiore
4. **Base**: Piano inferiore
5. **Ripiano_N**: Ripiani interni (se presenti)
6. **Schienale**: Pannello posteriore
7. **Zoccolo**: Base rialzata (se presente)

### Esportazione per CNC

Per generare codice Xilog Plus:

1. Esporta componenti come DXF/DWG
2. Usa script Python in `examples/generate_examples.py`
3. Ottieni file `.xilog` per CNC SCM Record 130TV

**Vedi**: `docs/XILOG_EXPORT.md` per guida completa

## Suggerimenti e Best Practices

### Dimensionamento

1. **Proporzioni**: Rapporto H/P ottimale 1.5-2.0 per stabilità
2. **Larghezza**: Max 200cm senza montanti centrali
3. **Profondità**: Base 55-65cm, Pensile 30-40cm

### Ferramenta

1. **Cerniere**: Calcola 1 cerniera ogni 30-40cm di altezza anta
2. **Sistema 32mm**: Sempre consigliato per flessibilità
3. **Spinatura**: Obbligatoria per mobili > 150cm altezza

### IA

1. **Descrizioni dettagliate**: Includi dimensioni, uso, caratteristiche
2. **Linguaggio naturale**: Scrivi come parleresti a un falegname
3. **Iterazione**: Prova diverse formulazioni se risultato non soddisfacente

### Performance

1. **Mobili complessi**: Dividi in sotto-componenti
2. **Molti fori**: Usa Sistema 32mm per ottimizzazione
3. **Ante multiple**: Genera separatamente se > 4 ante

## Risoluzione Problemi

### Mobile non generato

**Cause comuni**:
- Dimensioni fuori range
- Interassi non multipli di 32mm con Sistema 32mm
- Troppi ripiani per altezza disponibile

**Soluzione**:
- Verifica limiti dimensioni
- Disattiva Sistema 32mm o regola altezza
- Riduci numero ripiani

### IA non risponde

**Cause**:
- Ollama non in esecuzione
- Endpoint errato
- Modello non scaricato

**Soluzione**:
- Verifica: `curl http://localhost:11434/api/version`
- Controlla configurazione: **Configura IA**
- Scarica modello: `ollama pull llama3:8b`

### Fori mancanti

**Cause**:
- Opzioni fori disattivate
- Sistema 32mm disattivato

**Soluzione**:
- Attiva: **Fori ripiani**, **Spinatura**, **Num. cerniere**
- Attiva **Sistema 32mm** per fori reggi-ripiano

## Personalizzazioni Avanzate

### Modifica Parametri Post-Generazione

1. Usa **Modifica parametri** in Fusion per dimensioni
2. Aggiungi fori manualmente con **Foro** tool
3. Modifica componenti individualmente

### Template Personalizzati

Crea template riutilizzabili:

1. Genera mobile con parametri desiderati
2. Salva come componente
3. Inserisci in nuovi design con **Inserisci → Componente**

### Integrazione CAM

Per lavorazioni CNC direttamente da Fusion:

1. Genera mobile con wizard
2. Passa a workspace **MANUFACTURE**
3. Crea setup per ogni componente
4. Genera toolpath per forature e contorni
5. Post-processa con post-processore Xilog

## Risorse Aggiuntive

- **README.md**: Overview completo
- **INSTALLAZIONE.md**: Guida installazione dettagliata
- **examples/**: Esempi codice e output
- **GitHub Issues**: Supporto e domande

## Feedback

Aiutaci a migliorare FurnitureAI:
- Segnala bug su GitHub Issues
- Suggerisci miglioramenti
- Condividi i tuoi progetti!

---

**Buona progettazione con FurnitureAI! 🪑🤖**
