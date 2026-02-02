# Parametri di Test per FurnitureAI

Questo file contiene esempi di parametri da usare per testare l'add-in FurnitureAI in Fusion 360.

## Test 1: Mobile Base Cucina Standard

**Tipo:** Mobile Base  
**Descrizione IA:** "Mobile base cucina largo 80cm con 2 ripiani e 2 ante"

### Parametri:
- **Larghezza (L):** 80.0 cm
- **Altezza (H):** 90.0 cm
- **Profondità (P):** 60.0 cm
- **Spessore pannello:** 1.8 cm (18mm)
- **Spessore schienale:** 0.6 cm (6mm)
- **Numero ripiani:** 2
- **Sistema 32mm:** Attivo
- **Fori reggi-ripiano:** Attivo (Ø5mm)
- **Spinatura Ø8:** Attivo
- **Numero cerniere:** 4 (2 per anta)
- **Numero ante:** 2
- **Con zoccolo:** Sì
- **Altezza zoccolo:** 10.0 cm

### Componenti attesi:
- Fianco_SX
- Fianco_DX
- Top
- Base
- Ripiano_1
- Ripiano_2
- Schienale
- Zoccolo

---

## Test 2: Pensile Sospeso

**Tipo:** Pensile  
**Descrizione IA:** "Pensile sospeso 120x80x35 con 1 ripiano e 2 ante"

### Parametri:
- **Larghezza (L):** 120.0 cm
- **Altezza (H):** 80.0 cm
- **Profondità (P):** 35.0 cm
- **Spessore pannello:** 1.8 cm (18mm)
- **Spessore schienale:** 0.6 cm (6mm)
- **Numero ripiani:** 1
- **Sistema 32mm:** Attivo
- **Fori reggi-ripiano:** Attivo (Ø5mm)
- **Spinatura Ø8:** Attivo
- **Numero cerniere:** 4 (2 per anta)
- **Numero ante:** 2
- **Con zoccolo:** No

### Componenti attesi:
- Fianco_SX
- Fianco_DX
- Top
- Base
- Ripiano_1
- Schienale

---

## Test 3: Mobile Base Minimo

**Tipo:** Mobile Base  
**Descrizione IA:** "Mobile base semplice 60x70x50 senza ripiani"

### Parametri:
- **Larghezza (L):** 60.0 cm
- **Altezza (H):** 70.0 cm
- **Profondità (P):** 50.0 cm
- **Spessore pannello:** 1.8 cm (18mm)
- **Spessore schienale:** 0.6 cm (6mm)
- **Numero ripiani:** 0
- **Sistema 32mm:** Disattivo
- **Fori reggi-ripiano:** Disattivo
- **Spinatura Ø8:** Attivo
- **Numero cerniere:** 0
- **Numero ante:** 0
- **Con zoccolo:** Sì
- **Altezza zoccolo:** 10.0 cm

### Componenti attesi:
- Fianco_SX
- Fianco_DX
- Top
- Base
- Schienale
- Zoccolo

---

## Test 4: Armadio Grande

**Tipo:** Armadio  
**Descrizione IA:** "Armadio 200x220x60 con 3 ripiani"

### Parametri:
- **Larghezza (L):** 200.0 cm
- **Altezza (H):** 220.0 cm
- **Profondità (P):** 60.0 cm
- **Spessore pannello:** 1.8 cm (18mm)
- **Spessore schienale:** 0.6 cm (6mm)
- **Numero ripiani:** 3
- **Sistema 32mm:** Attivo
- **Fori reggi-ripiano:** Attivo (Ø5mm)
- **Spinatura Ø8:** Attivo
- **Numero cerniere:** 6 (2 per anta su 3 ante)
- **Numero ante:** 3
- **Con zoccolo:** Sì
- **Altezza zoccolo:** 15.0 cm

### Componenti attesi:
- Fianco_SX
- Fianco_DX
- Top
- Base
- Ripiano_1
- Ripiano_2
- Ripiano_3
- Schienale
- Zoccolo

---

## Test 5: Validazione Limiti

### Test dimensioni minime (devono funzionare):
- L: 20 cm, H: 20 cm, P: 20 cm

### Test dimensioni massime (devono funzionare):
- L: 300 cm, H: 300 cm, P: 100 cm

### Test errori (devono essere rifiutati):
- L: 10 cm (< 20) → Errore
- L: 350 cm (> 300) → Errore
- P: 110 cm (> 100) → Errore
- Spessore pannello: 0.5 cm (< 1.0) → Errore
- Spessore pannello: 6.0 cm (> 5.0) → Errore
- Numero ripiani: 11 (> 10) → Errore

---

## Note per Testing

### Workflow di test manuale:
1. Avviare Fusion 360
2. Caricare/Attivare add-in FurnitureAI
3. Aprire comando "Wizard Mobili" dal pannello FurnitureAI
4. Inserire parametri da uno dei test sopra
5. Verificare che:
   - Non ci siano errori durante la generazione
   - Tutti i componenti attesi vengano creati
   - Le dimensioni corrispondano ai parametri inseriti
   - Il mobile sia posizionato correttamente nell'origine

### Test con IA (opzionale):
1. Configurare endpoint IA (Ollama/LM Studio)
2. Attivare "Usa IA per suggerimenti"
3. Inserire descrizione testuale
4. Verificare che i suggerimenti siano sensati
5. Se IA non disponibile, verificare che vengano usati suggerimenti di fallback

### Verifica dimensioni:
- Usare strumento "Misura" di Fusion 360
- Verificare spessori pannelli
- Verificare posizionamento ripiani (se sistema 32mm attivo, devono essere multipli di 3.2cm)

### Test post-processore (separato):
- Esportare componenti in codice Xilog Plus
- Verificare sintassi codice generato
- Controllare coordinate e profondità fori
