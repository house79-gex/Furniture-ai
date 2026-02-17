# Guida Test Manuali - Fix Posizionamento + Ante + IA Check

## Panoramica Modifiche

Questa PR implementa 4 fix critici:
1. **Posizionamento schienale corretto** - Estrusione verso -Y per schienale arretrato
2. **Generazione ante** - Nuova funzionalità per creare ante frontali
3. **IA check robusto** - Non blocca avvio se server IA offline
4. **UI completa** - Verificati tutti i 7 comandi registrati

## Test da Eseguire

### Test 1: Posizionamento Schienale Corretto ✅

**Obiettivo**: Verificare che lo schienale sia posizionato correttamente arretrato

**Procedura**:
1. Avviare Fusion 360
2. Aprire il Wizard Mobili (CREA → FurnitureAI → Wizard Mobili)
3. Inserire parametri:
   - Larghezza: 80 cm
   - Altezza: 90 cm
   - Profondità: 60 cm
   - Spessore pannello: 1.8 cm
   - Spessore schienale: 0.6 cm
   - Numero ripiani: 2
   - Numero ante: 0
4. Generare il mobile

**Risultato Atteso**:
- Fianco SX: da (0, 0, 0) a (1.8, 60, 90)
- Fianco DX: da (78.2, 0, 0) a (80, 60, 90)
- **Schienale**: da (1.8, 59.4, 1.8) a (78.2, 60, 88.2)
  - ⚠️ IMPORTANTE: Y=59.4 (arretrato di 0.6cm verso interno), NON Y=60
  - Lo schienale deve essere DIETRO i fianchi, non a filo con la profondità massima

**Come Verificare**:
- Selezionare il corpo "Schienale" nella timeline
- Controllare le coordinate nel pannello Proprietà
- Guardare la vista laterale: lo schienale deve essere arretrato

---

### Test 2: Generazione Ante ✅

**Obiettivo**: Verificare che le ante vengano generate correttamente

**Procedura**:
1. Avviare Fusion 360
2. Aprire il Wizard Mobili
3. Inserire parametri:
   - Larghezza: 80 cm
   - Altezza: 90 cm
   - Profondità: 60 cm
   - Spessore pannello: 1.8 cm
   - Spessore schienale: 0.6 cm
   - Numero ripiani: 2
   - **Numero ante: 2** ← FONDAMENTALE
4. Generare il mobile

**Risultato Atteso**:
- Mobile completo con fianchi, base, top, ripiani, schienale
- **+ 2 ante frontali**:
  - Anta_1: da (0.2, -1.8, 0.2) a (~39.9, -1.8, 89.8)
  - Anta_2: da (40.1, -1.8, 0.2) a (79.8, -1.8, 89.8)
  - ⚠️ Y=-1.8 (DAVANTI al mobile, posizione negativa)
  - Gap 2mm tra ante e ai bordi

**Come Verificare**:
- Timeline deve mostrare corpi "Anta_1" e "Anta_2"
- Vista frontale: 2 pannelli rettangolari che coprono la facciata
- Vista isometrica: ante DAVANTI ai fianchi (Y negativo)
- Gap visibili di ~2mm tra le ante

**Test Aggiuntivo - 1 Anta**:
- Ripetere con num_ante=1
- Deve creare 1 sola anta che copre tutta la larghezza (con gap)

**Test Aggiuntivo - 3 Ante**:
- Ripetere con num_ante=3
- Deve creare 3 ante equamente distribuite

---

### Test 3: UI Completa - 7 Comandi Visibili ✅

**Obiettivo**: Verificare che tutti i comandi siano registrati nell'interfaccia

**Procedura**:
1. Avviare Fusion 360
2. Andare al menu CREA
3. Cercare il pannello "FurnitureAI"

**Risultato Atteso**:
Devono essere visibili **7 comandi**:
1. ✅ **Wizard Mobili** (promoted - sempre visibile)
2. ✅ **Lista Taglio** (dropdown)
3. ✅ **Ottimizza Taglio** (dropdown)
4. ✅ **Genera Disegni** (dropdown)
5. ✅ **Designer Ante** (dropdown)
6. ✅ **Gestione Materiali** (dropdown)
7. ✅ **Configura IA** (dropdown)

**Come Verificare**:
- Click su ogni comando per verificare che apra un dialog o mostri un messaggio
- Nessun errore nella console Python

---

### Test 4: IA Check Non Blocca Avvio ✅

**Obiettivo**: Verificare che l'add-in funzioni anche senza server IA

**Procedura A - Server IA Spento**:
1. **Spegnere** LM Studio o Ollama (se in esecuzione)
2. Riavviare Fusion 360
3. Verificare che l'add-in FurnitureAI si carichi senza errori
4. Aprire il Wizard Mobili
5. Creare un mobile normalmente

**Risultato Atteso A**:
- Add-in si carica senza errori bloccanti
- Log mostra: `[WARN] IA non raggiungibile` o `[WARN] IA timeout`
- Log mostra: `[INFO] IA non disponibile, utilizzo fallback locale`
- Wizard funziona normalmente (eventualmente senza suggerimenti IA)
- Generazione mobile funziona perfettamente

**Procedura B - Server IA Acceso**:
1. **Avviare** LM Studio su http://127.0.0.1:1234 (o Ollama su default port)
2. Caricare un modello (es. llama-3.2-3b-instruct)
3. Riavviare Fusion 360
4. Verificare log

**Risultato Atteso B**:
- Add-in si carica con successo
- Log mostra: `[OK] IA disponibile: 1 modelli trovati` (o simile)
- Wizard ha funzionalità IA abilitate
- Suggerimenti IA funzionano (se implementati)

**Come Verificare**:
- Aprire console Python di Fusion 360 (Strumenti → Macro → Script e componenti aggiuntivi)
- Cercare messaggi con prefisso `[OK]`, `[WARN]`, `[INFO]`
- Verificare che NON ci siano eccezioni o errori bloccanti

---

## Log Attesi

### Log Normale (con IA)
```
[INFO] Verifica IA endpoint: http://localhost:1234
[OK] IA disponibile: 1 modelli trovati
[INFO] Inizio generazione mobile...
[INFO] Dimensioni: L=80, H=90, P=60, S=1.8
[INFO] Creazione fianco SX...
[INFO] Pannello verticale YZ Fianco_SX creato: 60x90 cm (sp=1.8) @ x=0
[INFO] Creazione fianco DX...
[INFO] Pannello verticale YZ Fianco_DX creato: 60x90 cm (sp=1.8) @ x=78.2
[INFO] Creazione base...
[INFO] Pannello Base creato: 80x60x1.8 cm @ (0,0,0)
[INFO] Creazione top...
[INFO] Pannello Top creato: 80x60x1.8 cm @ (0,0,88.2)
[INFO] Creazione ripiano 1 a z=30.733333333333334...
[INFO] Pannello Ripiano_1 creato: 76.4x60x1.8 cm @ (1.8,0,30.73)
[INFO] Creazione ripiano 2 a z=59.46666666666667...
[INFO] Pannello Ripiano_2 creato: 76.4x60x1.8 cm @ (1.8,0,59.47)
[INFO] Creazione schienale...
[INFO] Pannello verticale XZ Schienale creato: 76.4x86.4 cm (sp=0.6) @ y=59.4
[INFO] Creazione 2 ante...
[INFO] Anta Anta_1 creata base: 39.8x89.6 cm (sp=1.8)
[INFO] Anta Anta_1 posizionata: @ (0.2,-1.8,0.2)
[INFO] Anta Anta_2 creata base: 39.8x89.6 cm (sp=1.8)
[INFO] Anta Anta_2 posizionata: @ (40.2,-1.8,0.2)
[INFO] Mobile creato: 10 componenti
```

### Log Senza IA
```
[INFO] Verifica IA endpoint: http://localhost:1234
[WARN] IA non raggiungibile: http://localhost:1234 (verifica server attivo)
[INFO] IA non disponibile, utilizzo fallback locale
[INFO] Inizio generazione mobile...
[... resto normale ...]
```

---

## Checklist Finale

Prima di approvare la PR, verificare:

- [ ] Test 1: Schienale posizionato a Y=59.4 (arretrato), non Y=60
- [ ] Test 2: Ante generate correttamente con num_ante=1, 2, 3
- [ ] Test 2: Ante posizionate a Y negativo (davanti al mobile)
- [ ] Test 2: Gap 2mm visibili tra ante
- [ ] Test 3: Tutti i 7 comandi visibili nel menu FurnitureAI
- [ ] Test 4: Add-in funziona senza server IA (log WARN ma non errori)
- [ ] Test 4: Add-in rileva server IA quando presente (log OK)
- [ ] Nessun errore Python nella console
- [ ] Nessun alert CodeQL
- [ ] Sintassi Python valida

---

## Troubleshooting

### Problema: Schienale ancora a Y=60
- Verificare che `create_vertical_panel_XZ()` usi `setOneSideExtent` con `NegativeExtentDirection`
- Controllare log per "Pannello verticale XZ Schienale creato"

### Problema: Ante non generate
- Verificare parametro `num_ante` > 0 nel wizard
- Controllare log per "Creazione N ante..."
- Verificare che `create_door_panel()` esista e sia chiamata

### Problema: Add-in non si carica
- Controllare log per eccezioni durante import
- Verificare sintassi Python: `python3 -m py_compile fusion_addin/lib/*.py`

### Problema: IA check fallisce sempre
- Verificare URL endpoint: default `http://localhost:1234`
- Verificare server IA in esecuzione: aprire browser su http://localhost:1234/v1/models
- Timeout troppo basso? Dovrebbe essere 5s, sufficiente per rete locale

---

## Note Implementazione

### Costanti Utilizzate
```python
GAP_ANTE_CM = 0.2  # Gap tra ante: 2mm = 0.2cm
SPESSORE_ANTA_DEFAULT_CM = 1.8  # Spessore ante: 18mm = 1.8cm
REQUEST_TIMEOUT = 5  # Timeout richieste HTTP IA: 5 secondi
```

### Funzioni Skeleton (Implementazione Futura)
```python
add_shelf_holes_32mm()  # TODO: Fori sistema 32mm per reggipiani
add_back_panel_groove()  # TODO: Scanalatura per schienale incastrato
```

Queste funzioni sono placeholder e non fanno nulla attualmente. Ritornano `True` per non bloccare la generazione del mobile. Saranno implementate in PR future.
