#!/usr/bin/env python3
"""
Script di test per verificare la generazione corretta dei mobili
Testa che i pannelli vengano creati rettangolari e verticali
"""

# Questo script è un esempio di test manuale per Fusion 360
# Per eseguirlo, copiare il contenuto nella console Python di Fusion 360

import adsk.core
import adsk.fusion
import traceback

def test_furniture_generation():
    """Test generazione mobile con parametri standard"""
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        
        if not design:
            ui.messageBox('Errore: Nessun design attivo')
            return False
        
        # Importa il modulo furniture_generator
        # Nota: questo assume che l'add-in sia già caricato
        import sys
        import os
        
        # Aggiungi path dell'add-in se necessario
        addon_path = os.path.join(os.path.expanduser('~'), 
                                  'AppData', 'Roaming', 'Autodesk', 
                                  'Autodesk Fusion 360', 'API', 'AddIns',
                                  'FurnitureAI', 'fusion_addin', 'lib')
        
        if addon_path not in sys.path:
            sys.path.append(addon_path)
        
        import furniture_generator
        
        # Parametri test: L=80, H=90, P=60, S=1.8
        test_params = {
            'larghezza': 80.0,
            'altezza': 90.0,
            'profondita': 60.0,
            'spessore_pannello': 1.8,
            'spessore_schienale': 0.6,
            'num_ripiani': 2,
            'con_zoccolo': False
        }
        
        ui.messageBox('Inizio test generazione mobile...\n\n'
                     'Parametri:\n'
                     'L=80cm, H=90cm, P=60cm, S=1.8cm\n'
                     '2 ripiani\n\n'
                     'Verifica che i pannelli siano rettangolari e verticali.')
        
        # Genera mobile
        result = furniture_generator.generate_furniture(design, test_params)
        
        if result['success']:
            msg = 'TEST SUPERATO! ✓\n\n'
            msg += 'Mobile creato con successo\n'
            msg += 'Componenti creati: {}\n\n'.format(len(result['components']))
            msg += 'Componenti:\n'
            for comp in result['components']:
                msg += '  - {}\n'.format(comp)
            msg += '\nVerifica visivamente che:\n'
            msg += '1. I fianchi siano verticali (piano YZ)\n'
            msg += '2. Base e top siano orizzontali (piano XY)\n'
            msg += '3. Lo schienale sia verticale (piano XZ)\n'
            msg += '4. Tutti i pannelli siano rettangolari (no trapezi/deformazioni)'
            
            ui.messageBox(msg)
            return True
        else:
            msg = 'TEST FALLITO! ✗\n\n'
            msg += 'Errore: {}'.format(result['error'])
            ui.messageBox(msg)
            return False
            
    except Exception as e:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('ERRORE TEST:\n{}'.format(traceback.format_exc()))
        return False


def test_config_creation():
    """Test creazione automatica config.json"""
    try:
        import os
        import json
        
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Path config
        home = os.path.expanduser('~')
        config_dir = os.path.join(home, '.furniture_ai')
        config_file = os.path.join(config_dir, 'config.json')
        
        # Verifica esistenza directory e file
        dir_exists = os.path.exists(config_dir)
        file_exists = os.path.exists(config_file)
        
        msg = 'TEST CONFIGURAZIONE IA\n\n'
        msg += 'Directory config: {}\n'.format('✓ Esiste' if dir_exists else '✗ Non esiste')
        msg += 'File config.json: {}\n\n'.format('✓ Esiste' if file_exists else '✗ Non esiste')
        
        if file_exists:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    msg += 'Contenuto config:\n'
                    msg += '  - Endpoint: {}\n'.format(config.get('ai_endpoint', 'N/A'))
                    msg += '  - Modello: {}\n'.format(config.get('ai_model', 'N/A'))
                    
                    # Verifica valori corretti per LM Studio
                    if config.get('ai_endpoint') == 'http://localhost:1234':
                        msg += '\n✓ Endpoint corretto per LM Studio'
                    else:
                        msg += '\n⚠ Endpoint non configurato per LM Studio'
                    
                    if config.get('ai_model') == 'llama-3.2-3b-instruct':
                        msg += '\n✓ Modello default corretto'
                    else:
                        msg += '\n⚠ Modello non configurato con default LM Studio'
            except:
                msg += '✗ Errore lettura config'
        
        ui.messageBox(msg)
        return file_exists
        
    except Exception as e:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('ERRORE TEST CONFIG:\n{}'.format(str(e)))
        return False


# Esegui test
if __name__ == '__main__':
    print("=== TEST FURNITURE GENERATION ===")
    test_furniture_generation()
    print("\n=== TEST CONFIG CREATION ===")
    test_config_creation()
