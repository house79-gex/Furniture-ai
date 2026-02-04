"""
LLM Client per layout automatico cucine
Modello: Llama 3.1 8B Instruct (LM Studio/Ollama)
"""

try:
    import requests
except ImportError:
    requests = None

import json
from typing import Dict, Any, List, Optional


class LLMClient:
    """Client per generazione layout cucine con LLM locale"""
    
    def __init__(self, endpoint: str = 'http://localhost:1234', model: str = 'llama-3.1-8b-instruct'):
        """
        Inizializza client LLM
        
        Args:
            endpoint: URL endpoint IA locale (LM Studio o Ollama)
            model: Nome del modello LLM
        """
        self.endpoint = endpoint.rstrip('/')
        self.model = model
    
    def generate_kitchen_layout(self, description: str) -> Dict[str, Any]:
        """
        Genera layout cucina da descrizione testuale
        
        Input: "cucina a L 4x3m con isola, 5 basi, 4 pensili, stile moderno"
        Output: JSON con moduli posizionati
        
        Args:
            description: Descrizione testuale della cucina
            
        Returns:
            Dict con layout strutturato della cucina
        """
        prompt = """Sei un progettista di cucine. Genera layout dettagliato da questa descrizione:

Descrizione: {description}

Output JSON:
{{
  "layout_type": "L-shape|linear|U-shape|island",
  "room_dimensions": {{"width": <cm>, "depth": <cm>}},
  "modules": [
    {{
      "type": "base|wall_cabinet|tall",
      "width": <cm>,
      "position": {{"wall": "north|south|east|west", "x": <cm>}},
      "features": ["sink"|"hob"|"oven"|"fridge"|"dishwasher"],
      "doors": <num>,
      "drawers": <num>
    }}
  ],
  "worktop": {{"material": "...", "thickness": 2}},
  "style": {{"door_type": "flat|shaker|glass", "finish": "...", "color": "..."}}
}}

Standard italiani: base H=90 P=60, pensile H=70 P=35, interasse 60cm.""".format(description=description)

        if requests is None:
            return self._fallback_layout(description)
        
        try:
            response = requests.post(
                '{}/v1/chat/completions'.format(self.endpoint),
                json={
                    'model': self.model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.3,
                    'max_tokens': 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Estrai JSON dalla risposta
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    layout = json.loads(content[start:end])
                    return layout
        except Exception:
            pass
        
        return self._fallback_layout(description)
    
    def _fallback_layout(self, description: str) -> Dict[str, Any]:
        """Layout base se IA non disponibile"""
        return {
            "layout_type": "linear",
            "room_dimensions": {"width": 400, "depth": 300},
            "modules": [
                {"type": "base", "width": 60, "position": {"wall": "north", "x": 0}, "features": [], "doors": 2, "drawers": 0},
                {"type": "base", "width": 80, "position": {"wall": "north", "x": 60}, "features": ["sink"], "doors": 2, "drawers": 0},
                {"type": "base", "width": 60, "position": {"wall": "north", "x": 140}, "features": ["hob"], "doors": 0, "drawers": 3},
                {"type": "wall_cabinet", "width": 60, "position": {"wall": "north", "x": 0}, "features": [], "doors": 2, "drawers": 0},
                {"type": "wall_cabinet", "width": 80, "position": {"wall": "north", "x": 60}, "features": [], "doors": 2, "drawers": 0},
            ],
            "worktop": {"material": "laminato", "thickness": 2},
            "style": {"door_type": "flat", "finish": "opaco", "color": "bianco"}
        }
    
    def optimize_module_placement(self, modules: List[Dict[str, Any]], room_width: float, room_depth: float) -> List[Dict[str, Any]]:
        """
        Ottimizza posizionamento moduli in base a vincoli ergonomici
        
        Args:
            modules: Lista moduli da posizionare
            room_width: Larghezza stanza in cm
            room_depth: Profondità stanza in cm
            
        Returns:
            Lista moduli con posizioni ottimizzate
        """
        # TODO: Implementare logica ottimizzazione con LLM
        # Per ora ritorna moduli invariati
        return modules
    
    def suggest_hardware(self, furniture_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggerisce ferramenta necessaria per il mobile
        
        Args:
            furniture_params: Parametri del mobile
            
        Returns:
            Dict con lista ferramenta consigliata
        """
        prompt = """Sei un esperto falegname. Suggerisci la ferramenta necessaria per questo mobile:

Parametri mobile:
- Larghezza: {width} cm
- Altezza: {height} cm
- Profondità: {depth} cm
- Numero ante: {doors}
- Numero cassetti: {drawers}
- Numero ripiani: {shelves}

Output JSON:
{{
  "cerniere": {{"tipo": "...", "quantita": <num>}},
  "guide_cassetti": {{"tipo": "...", "quantita": <num>}},
  "maniglie": {{"tipo": "...", "quantita": <num>}},
  "reggipiano": {{"quantita": <num>}},
  "viti": {{"tipo": "...", "quantita": <num>}},
  "tasselli": {{"quantita": <num>}},
  "note": "..."
}}""".format(
            width=furniture_params.get('larghezza', 80),
            height=furniture_params.get('altezza', 90),
            depth=furniture_params.get('profondita', 60),
            doors=furniture_params.get('num_ante', 0),
            drawers=furniture_params.get('num_cassetti', 0),
            shelves=furniture_params.get('num_ripiani', 2)
        )
        
        if requests is None:
            return self._fallback_hardware(furniture_params)
        
        try:
            response = requests.post(
                '{}/v1/chat/completions'.format(self.endpoint),
                json={
                    'model': self.model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.3,
                    'max_tokens': 1000
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Estrai JSON
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])
        except Exception:
            pass
        
        return self._fallback_hardware(furniture_params)
    
    def _fallback_hardware(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ferramenta standard se IA non disponibile"""
        num_ante = params.get('num_ante', 0)
        num_cassetti = params.get('num_cassetti', 0)
        num_ripiani = params.get('num_ripiani', 2)
        
        return {
            "cerniere": {"tipo": "cerniera 110°", "quantita": num_ante * 2},
            "guide_cassetti": {"tipo": "guide a sfera", "quantita": num_cassetti},
            "maniglie": {"tipo": "maniglia standard", "quantita": num_ante + num_cassetti},
            "reggipiano": {"quantita": num_ripiani * 4},
            "viti": {"tipo": "viti 4x30mm", "quantita": 50},
            "tasselli": {"quantita": 8},
            "note": "Quantità calcolate in base a parametri standard"
        }
