# Guida Export Xilog Plus

## Panoramica

Questa guida spiega come esportare i mobili generati con FurnitureAI in codice Xilog Plus per CNC SCM Record 130TV (NUM 1050).

## Post-processore Xilog Plus

Il post-processore converte operazioni di lavorazione in codice Xilog Plus compatibile con il controllo NUM 1050.

### Comandi Supportati

#### Foratura
- **XB**: Foratura singola
- **XBO/XBOE**: Foratura ottimizzata (batch)
- **XBR**: Foratura con uscita ritardata

#### Fresatura
- **XG0**: Movimento rapido
- **XG1**: Movimento lineare interpolato
- **XL2P**: Linea 2D
- **XA2P**: Arco 2D
- **XGIN/XGOUT**: Inizio/fine lavorazione

#### Gestione Facce
- **F=1..5**: Cambio faccia lavorazione

### Libreria Utensili TLG

#### Utensili Predefiniti

**Gruppo Foratura Verticale (F=1)**
```
T=1,8,9   : Ø5 mm  (fori reggi-ripiano)
T=2,9,10  : Ø6 mm
T=3,10,11 : Ø8 mm  (spinatura)
T=4,11,12 : Ø10 mm
T=5,12    : Ø12 mm
T=6       : Ø16 mm
T=7       : Ø35 mm (cerniere)
```

**Foratura Orizzontale X (F=2,3)**
```
T=42      : Ø8 mm  (faccia 2 - retro)
T=43      : Ø8 mm  (faccia 3 - fronte)
T=62      : Ø5 mm  (faccia 2)
T=63      : Ø5 mm  (faccia 3)
```

**Foratura Orizzontale Y (F=4,5)**
```
T=64      : Ø8 mm  (faccia 4 - destra)
T=65      : Ø8 mm  (faccia 5 - sinistra)
```

**Mandrino Principale (F=1)**
```
T=101     : Fresa Ø6 mm
T=102     : Fresa Ø8 mm
T=103     : Fresa Ø10 mm
T=104     : Fresa Ø12 mm
T=105     : Fresa Ø16 mm
T=106     : Fresa Ø20 mm
T=110     : Punta Ø35 mm (cerniere)
```

**Aggregato Serratura**
```
T=280     : Ø16 mm (serrature)
```

## Uso da Python

### Esempio Base

```python
from postprocessor.xilog_generator import XilogGenerator
from tlg_parser.tlg_library import TLGLibrary

# Inizializza libreria utensili
tlg = TLGLibrary()

# Crea generatore
gen = XilogGenerator(tlg)

# Header programma
gen.add_header('Fianco_Mobile', (800, 600, 18))

# Fori spinatura Ø8
dowel_holes = [
    {'x': 50, 'y': 50, 'diameter': 8.0, 'depth': 40.0},
    {'x': 750, 'y': 50, 'diameter': 8.0, 'depth': 40.0},
    {'x': 50, 'y': 550, 'diameter': 8.0, 'depth': 40.0},
    {'x': 750, 'y': 550, 'diameter': 8.0, 'depth': 40.0}
]
gen.add_drilling(dowel_holes, face=1, optimized=True)

# Fori sistema 32mm Ø5
shelf_holes = []
for y in range(100, 550, 32):
    shelf_holes.append({
        'x': 32, 'y': y, 'diameter': 5.0, 'depth': 12.0
    })
gen.add_drilling(shelf_holes, face=1, optimized=True)

# Contorno pannello
contour = [
    (10, 10), (790, 10), (790, 590), (10, 590), (10, 10)
]
gen.add_routing(contour, depth=5.0, tool_diameter=8.0)

# Footer
gen.add_safety_notes()
gen.add_footer()

# Salva file
gen.save_to_file('output/fianco_mobile.xilog')

# Oppure stampa
print(gen.generate())
```

### Esempio con Cerniere

```python
gen = XilogGenerator(TLGLibrary())
gen.add_header('Anta_Cucina', (400, 800, 18))

# Fori cerniere Ø35
hinge_positions = [
    (22, 100),  # Cerniera superiore
    (22, 400),  # Cerniera centrale
    (22, 700)   # Cerniera inferiore
]
gen.add_hinge_holes(hinge_positions, diameter=35.0, depth=13.0)

# Contorno con raggi
contour = [
    (5, 5), (395, 5), (395, 795), (5, 795), (5, 5)
]
gen.add_routing(contour, depth=3.0, tool_diameter=8.0)

gen.add_safety_notes()
gen.add_footer()
gen.save_to_file('output/anta_cucina.xilog')
```

### Esempio Multi-Faccia

```python
gen = XilogGenerator(TLGLibrary())
gen.add_header('Pannello_Complesso', (600, 400, 18))

# Faccia 1 (superiore) - foratura verticale
gen.add_face_change(1)
top_holes = [
    {'x': 50, 'y': 50, 'diameter': 8.0, 'depth': 40.0},
    {'x': 550, 'y': 50, 'diameter': 8.0, 'depth': 40.0}
]
gen.add_drilling(top_holes, face=1)

# Faccia 2 (anteriore) - foratura orizzontale
gen.add_face_change(2)
front_holes = [
    {'x': 100, 'y': 9, 'diameter': 8.0, 'depth': 50.0},
    {'x': 500, 'y': 9, 'diameter': 8.0, 'depth': 50.0}
]
gen.add_drilling(front_holes, face=2)

gen.add_safety_notes()
gen.add_footer()
gen.save_to_file('output/pannello_multi.xilog')
```

## API Reference

### XilogGenerator

#### __init__(tlg_library=None)
Inizializza generatore.
- `tlg_library`: Istanza TLGLibrary (opzionale)

#### add_header(part_name, dimensions)
Aggiunge intestazione programma.
- `part_name`: Nome pezzo (str)
- `dimensions`: Tuple (L, W, T) in mm

#### add_face_change(face)
Cambia faccia di lavoro.
- `face`: Numero faccia 1-5 (int)

#### add_drilling(holes, face=1, optimized=True)
Aggiunge operazioni di foratura.
- `holes`: Lista di dict con 'x', 'y', 'diameter', 'depth'
- `face`: Faccia di lavoro (default 1)
- `optimized`: Se True usa XBO (default True)

#### add_routing(path, depth, tool_diameter, face=1)
Aggiunge fresatura/contorno.
- `path`: Lista di tuple (x, y)
- `depth`: Profondità in mm
- `tool_diameter`: Diametro fresa in mm
- `face`: Faccia di lavoro

#### add_groove(start_x, start_y, length, width, depth, orientation='X')
Aggiunge scanalatura.
- `start_x, start_y`: Punto inizio
- `length`: Lunghezza in mm
- `width`: Larghezza in mm
- `depth`: Profondità in mm
- `orientation`: 'X' o 'Y'

#### add_dowel_holes(positions, diameter=8.0, depth=40.0)
Aggiunge fori spinatura.
- `positions`: Lista di tuple (x, y)
- `diameter`: Diametro spine (default 8mm)
- `depth`: Profondità (default 40mm)

#### add_hinge_holes(positions, diameter=35.0, depth=13.0)
Aggiunge fori cerniere.
- `positions`: Lista di tuple (x, y)
- `diameter`: Diametro (default 35mm)
- `depth`: Profondità (default 13mm)

#### add_safety_notes()
Aggiunge note di sicurezza.

#### add_footer()
Aggiunge footer programma (M30).

#### generate()
Genera codice completo.
- Returns: Stringa con codice Xilog

#### save_to_file(filename)
Salva programma su file.
- `filename`: Path file output
- Returns: True se successo

### TLGLibrary

#### __init__(tlg_path=None)
Inizializza libreria utensili.
- `tlg_path`: Path file TLG (opzionale)

#### load_from_file(tlg_path)
Carica libreria da file.
- `tlg_path`: Path file TLG o XML
- Returns: True se successo

#### select_drill_tool(diameter, face=1, depth=50.0)
Seleziona utensile per foratura.
- `diameter`: Diametro richiesto
- `face`: Faccia di lavoro
- `depth`: Profondità richiesta
- Returns: Dict utensile o None

#### select_routing_tool(diameter, face=1)
Seleziona utensile per fresatura.
- `diameter`: Diametro fresa
- `face`: Faccia di lavoro
- Returns: Dict utensile o None

#### get_tool_by_number(number)
Ottiene utensile per numero.
- `number`: Numero utensile
- Returns: Dict utensile o None

## Formato File TLG

### TLG Testuale

```
T=1 D=5.0 TYPE=drill ORIENT=vertical DEPTH=70
T=2 D=6.0 TYPE=drill ORIENT=vertical DEPTH=70
T=3 D=8.0 TYPE=drill ORIENT=vertical DEPTH=70
T=42 D=8.0 TYPE=drill ORIENT=horizontal_x DEPTH=60
T=101 D=6.0 TYPE=router ORIENT=vertical DEPTH=100
```

### TLG XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ToolLibrary>
  <Tool number="1" type="drill" diameter="5.0" orientation="vertical" max_depth="70" />
  <Tool number="2" type="drill" diameter="6.0" orientation="vertical" max_depth="70" />
  <Tool number="3" type="drill" diameter="8.0" orientation="vertical" max_depth="70" />
  <Tool number="42" type="drill" diameter="8.0" orientation="horizontal_x" face="2" max_depth="60" />
  <Tool number="101" type="router" diameter="6.0" orientation="vertical" max_depth="100" />
</ToolLibrary>
```

## Workflow Completo

### 1. Genera Mobile in Fusion 360
```
FurnitureAI Wizard → Mobile Base 80x90x60
```

### 2. Esporta Componenti
Per ogni componente (fianco, ripiano, etc.):
- Estrai dimensioni
- Identifica operazioni (fori, contorni)

### 3. Genera Codice Xilog
```python
for component in mobile.components:
    gen = XilogGenerator(tlg)
    gen.add_header(component.name, component.dimensions)
    
    # Aggiungi operazioni
    gen.add_dowel_holes(component.dowel_positions)
    gen.add_hinge_holes(component.hinge_positions)
    gen.add_drilling(component.shelf_holes)
    gen.add_routing(component.contour)
    
    gen.add_safety_notes()
    gen.add_footer()
    gen.save_to_file(f'output/{component.name}.xilog')
```

### 4. Carica su CNC
- Trasferisci file `.xilog` a CNC via USB/rete
- Verifica programma in modalità simulazione
- Monta utensili corretti
- Fissa pezzo
- Esegui programma

## Ottimizzazioni

### Foratura Ottimizzata (XBO)
Raggruppa fori stesso diametro:
```python
# Automatico con optimized=True
gen.add_drilling(holes, optimized=True)
```

Output:
```
XBO
  X=50.00 Y=50.00 P=40.00
  X=100.00 Y=50.00 P=40.00
  X=150.00 Y=50.00 P=40.00
XBOE
```

### Minimizzazione Movimenti
Ordina fori per percorso minimo:
```python
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, leaves_list

def optimize_drilling_order(holes):
    """Ottimizza ordine fori per percorso minimo"""
    if len(holes) <= 1:
        return holes
    
    coords = [(h['x'], h['y']) for h in holes]
    dist_matrix = squareform(pdist(coords))
    tree = linkage(dist_matrix, method='single')
    order = leaves_list(tree)
    
    return [holes[i] for i in order]

# Usa prima di add_drilling
holes_optimized = optimize_drilling_order(holes)
gen.add_drilling(holes_optimized)
```

## Test e Validazione

### Test Unit
```bash
cd tests
python test_postprocessor.py
```

### Validazione Sintassi
```python
def validate_xilog_syntax(code):
    """Valida sintassi base Xilog"""
    errors = []
    
    if 'G90' not in code:
        errors.append('Manca G90 (programmazione assoluta)')
    
    if 'M30' not in code:
        errors.append('Manca M30 (fine programma)')
    
    # Verifica XBO chiuso
    xbo_count = code.count('XBO')
    xboe_count = code.count('XBOE')
    if xbo_count != xboe_count:
        errors.append(f'XBO non bilanciati: {xbo_count} vs {xboe_count}')
    
    return errors

# Usa dopo generazione
code = gen.generate()
errors = validate_xilog_syntax(code)
if errors:
    print('Errori:', errors)
```

## Limitazioni

1. **Asse C**: Non supportato (CNC ha C non continuo)
2. **Lavorazioni 3D**: Solo 2.5D (foratura + contorni 2D)
3. **Aggregati speciali**: Limitato a serratura (T=280)
4. **Profondità max**: Vedi limiti utensili TLG

## Risoluzione Problemi

### Utensile non trovato
**Problema**: `select_drill_tool` ritorna None

**Soluzione**:
1. Verifica diametro disponibile in libreria
2. Controlla profondità richiesta vs max_depth
3. Verifica faccia compatibile con orientamento

### Coordinate errate
**Problema**: Fori fuori pezzo

**Soluzione**:
1. Verifica dimensioni pezzo in header
2. Coordinate relative a origine corretta
3. Controlla trasformazioni facce

### Codice non eseguibile su CNC
**Problema**: CNC rifiuta programma

**Soluzione**:
1. Valida sintassi con funzione di test
2. Verifica versione NUM 1050 compatibile
3. Controlla comandi specifici macchina

## Risorse

- **Esempi**: `examples/xilog_output/`
- **Script**: `examples/generate_examples.py`
- **Test**: `tests/test_postprocessor.py`
- **Manuale NUM 1050**: Consultare documentazione SCM

---

**Per supporto**: GitHub Issues o documentazione SCM Group
