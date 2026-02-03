"""
Gestore configurazione add-in
"""

import json
import os
from typing import Dict, Any


_DEFAULT_CONFIG = {
    'ai_endpoint': 'http://localhost:1234',  # LM Studio default endpoint
    'ai_model': 'llama-3.2-3b-instruct',     # LM Studio default model
    'tlg_path': '',
    'xilog_output_path': ''
}


def get_config_path() -> str:
    """Restituisce il percorso del file di configurazione"""
    # Usa directory home dell'utente
    home = os.path.expanduser('~')
    config_dir = os.path.join(home, '.furniture_ai')
    
    # Crea directory se non esiste
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
        except:
            pass
    
    return os.path.join(config_dir, 'config.json')


def load_config() -> Dict[str, Any]:
    """Carica configurazione da file, crea file con default se non esiste"""
    config_path = get_config_path()
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge con default per eventuali nuovi campi
                return {**_DEFAULT_CONFIG, **config}
        else:
            # Crea file config con default se non esiste
            save_config(_DEFAULT_CONFIG)
            return _DEFAULT_CONFIG.copy()
    except:
        # In caso di errore, prova a salvare config default
        try:
            save_config(_DEFAULT_CONFIG)
        except:
            pass
        return _DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> bool:
    """Salva configurazione su file"""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False


def update_config(updates: Dict[str, Any]) -> bool:
    """Aggiorna configurazione con nuovi valori"""
    config = load_config()
    config.update(updates)
    return save_config(config)
