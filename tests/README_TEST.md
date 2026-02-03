# Test FurnitureAI

Questa directory contiene script di test per verificare il corretto funzionamento dell'add-in FurnitureAI.

## Test Disponibili

### test_furniture_generation.py

Script di test per verificare:
1. Generazione corretta dei mobili con geometria non deformata
2. Creazione automatica del file di configurazione IA
3. Configurazione corretta per LM Studio

### Come Eseguire i Test in Fusion 360

1. Apri Fusion 360
2. Vai su **Utilities** > **ADD-INS** > **Scripts and Add-Ins**
3. Seleziona la tab **Scripts**
4. Clicca su **+** (Add) e seleziona il file di test
5. Seleziona lo script e clicca **Run**

Oppure:

1. Apri la console Python in Fusion 360 (**Utilities** > **ADD-INS** > **Scripts and Add-Ins** > **Script Editor**)
2. Copia e incolla il contenuto dello script di test
3. Esegui con F5

## Test Manuali

### Test 1: Geometria Pannelli

1. Avvia Fusion 360
2. Carica l'add-in FurnitureAI
3. Vai su **CREA** > **Wizard Mobili**
4. Inserisci parametri:
   - Larghezza: 80 cm
   - Altezza: 90 cm
   - Profondità: 60 cm
   - Spessore pannello: 1.8 cm
   - N. ripiani: 2
5. Clicca **OK**
6. **Verifica visivamente** che:
   - Fianchi siano verticali e rettangolari (non trapezoidali)
   - Base e top siano orizzontali e rettangolari
   - Schienale sia verticale e rettangolare
   - Ripiani siano orizzontali e rettangolari

### Test 2: Comandi UI in Assembly Mode

1. Crea un nuovo design in modalità **Assembly**
2. Verifica che nel pannello **CREA** appaiano i comandi:
   - Wizard Mobili (promoted/sempre visibile)
   - Lista Taglio
   - Ottimizza Taglio
   - Genera Disegni
   - Designer Ante
   - Gestione Materiali
   - Configura IA
3. Abilita la modifica del componente root (Edit Component)
4. Verifica che i comandi rimangano attivi/cliccabili

### Test 3: Configurazione IA

1. Vai su **CREA** > **Configura IA**
2. Verifica che appaia il dialog con:
   - Campo Endpoint (default: http://localhost:1234)
   - Campo Modello (default: llama-3.2-3b-instruct)
   - Pulsante "Testa Connessione"
3. Se hai LM Studio avviato su localhost:1234, clicca "Testa Connessione"
4. Verifica che rilevi la disponibilità dell'IA
5. Clicca **OK** per salvare
6. Verifica che il file `~/.furniture_ai/config.json` sia stato creato con i valori corretti

### Test 4: IA nel Wizard

1. Vai su **CREA** > **Wizard Mobili**
2. Espandi il gruppo **Assistente IA**
3. Verifica presenza dell'indicatore di stato IA (disponibile/non disponibile)
4. Inserisci una descrizione: "mobile base cucina largo 80cm con 2 ripiani"
5. Clicca **Compila da Descrizione**
6. Verifica che i campi vengano compilati automaticamente (anche con fallback se IA non disponibile)

### Test 5: Gestione Materiali

1. Crea un mobile con il wizard
2. Vai su **CREA** > **Gestione Materiali**
3. Verifica il dialog con opzioni:
   - Materiale unico / Materiali differenziati
   - Dropdown materiali (Rovere, Noce, Laccato, ecc.)
4. Seleziona un materiale e clicca **OK**
5. Verifica che i materiali vengano applicati ai componenti

## Checklist Test Completo

Prima di considerare l'implementazione completa, verifica:

- [ ] Mobili generati hanno pannelli rettangolari (no deformazioni)
- [ ] Tutti i comandi appaiono nel pannello CREA (Design e Assembly)
- [ ] Comandi restano attivi in Assembly dopo Edit Component
- [ ] File `~/.furniture_ai/config.json` viene creato automaticamente
- [ ] Config ha valori default per LM Studio (endpoint e modello)
- [ ] Dialog "Configura IA" permette di modificare endpoint e modello
- [ ] Wizard mostra indicatore stato IA
- [ ] Pulsante "Compila da Descrizione" funziona (anche con fallback)
- [ ] Dialog "Gestione Materiali" applica materiali correttamente

## Note

- I test richiedono che l'add-in FurnitureAI sia installato e attivo in Fusion 360
- Per testare l'integrazione IA completa, è necessario avere LM Studio o Ollama in esecuzione
- I test di fallback funzionano anche senza server IA attivo
