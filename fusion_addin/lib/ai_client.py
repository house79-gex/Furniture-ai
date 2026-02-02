"""
Client per l'integrazione con IA locale (Ollama/LM Studio)
"""

import json
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    requests = None


class AIClient:
    """Client per comunicare con endpoint IA locale"""
    
    def __init__(self, endpoint: str = 'http://localhost:11434'):
        """
        Inizializza client IA
        
        Args:
            endpoint: URL endpoint IA locale (es. Ollama)
        """
        self.endpoint = endpoint.rstrip('/')
        self.model = 'llama3'  # Modello default
        
        if requests is None:
            raise ImportError('Il modulo requests è richiesto per l\'integrazione IA. '
                            'Installare con: pip install requests')
    
    def get_furniture_suggestions(self, description: str) -> Optional[str]:
        """
        Ottiene suggerimenti per parametri mobili da descrizione testuale
        
        Args:
            description: Descrizione testuale del mobile
            
        Returns:
            Stringa con suggerimenti o None in caso di errore
        """
        try:
            prompt = f"""Sei un esperto falegname. Analizza questa descrizione di mobile e fornisci suggerimenti tecnici concisi:

Descrizione: {description}

Fornisci suggerimenti su:
- Dimensioni consigliate
- Numero e posizionamento ripiani
- Ferramenta necessaria (cerniere, guide cassetti)
- Accorgimenti costruttivi

Rispondi in italiano in modo conciso (max 200 parole)."""

            response = requests.post(
                f'{self.endpoint}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                return None
                
        except Exception as e:
            return None
    
    def parse_description_to_params(self, description: str) -> Optional[Dict[str, Any]]:
        """
        Converte descrizione testuale in parametri mobili
        
        Args:
            description: Descrizione testuale del mobile
            
        Returns:
            Dict con parametri estratti o None
        """
        try:
            prompt = f"""Estrai parametri numerici da questa descrizione di mobile.
            
Descrizione: {description}

Restituisci SOLO un oggetto JSON con questi campi (usa valori di default se non specificati):
{{
    "larghezza": 80.0,
    "altezza": 90.0,
    "profondita": 60.0,
    "num_ripiani": 2,
    "num_ante": 0,
    "num_cassetti": 0,
    "num_cerniere": 2
}}

Rispondi SOLO con JSON valido, niente altro."""

            response = requests.post(
                f'{self.endpoint}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                
                # Cerca JSON nella risposta
                try:
                    # Trova primo { e ultimo }
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = response_text[start:end]
                        return json.loads(json_str)
                except:
                    pass
            
            return None
            
        except Exception as e:
            return None
    
    def validate_parameters(self, params: Dict[str, Any]) -> Optional[str]:
        """
        Valida coerenza parametri con IA
        
        Args:
            params: Parametri del mobile
            
        Returns:
            Stringa con eventuali warning/suggerimenti o None
        """
        try:
            prompt = f"""Sei un esperto falegname. Analizza questi parametri di un mobile e segnala eventuali problemi o migliorie:

Parametri:
- Larghezza: {params.get('larghezza')} cm
- Altezza: {params.get('altezza')} cm
- Profondità: {params.get('profondita')} cm
- Numero ripiani: {params.get('num_ripiani')}
- Numero ante: {params.get('num_ante')}
- Numero cassetti: {params.get('num_cassetti')}
- Spessore pannello: {params.get('spessore_pannello')} cm

Rispondi in italiano in modo conciso (max 100 parole) SOLO se ci sono problemi o suggerimenti importanti, altrimenti rispondi "OK"."""

            response = requests.post(
                f'{self.endpoint}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('response', '').strip()
                return result if result and result != 'OK' else None
            else:
                return None
                
        except Exception as e:
            return None
