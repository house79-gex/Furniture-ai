"""
Client per l'integrazione con IA locale (Ollama/LM Studio)
Client non bloccante con suggerimenti di fallback se IA non disponibile
"""

import json
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    requests = None


class AIClient:
    """Client per comunicare con endpoint IA locale (non bloccante)"""
    
    def __init__(self, endpoint: str = 'http://localhost:11434', enable_fallback: bool = True):
        """
        Inizializza client IA
        
        Args:
            endpoint: URL endpoint IA locale (es. Ollama)
            enable_fallback: Se True, usa suggerimenti di fallback se IA non disponibile
        """
        self.endpoint = endpoint.rstrip('/')
        self.model = 'llama3'  # Modello default
        self.enable_fallback = enable_fallback
        self._ai_available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Verifica se l'endpoint IA è disponibile (non bloccante)"""
        if requests is None:
            return False
        
        try:
            response = requests.get(f'{self.endpoint}/api/version', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def is_available(self) -> bool:
        """Restituisce se l'IA è disponibile"""
        return self._ai_available
    
    def get_furniture_suggestions(self, description: str) -> Optional[str]:
        """
        Ottiene suggerimenti per parametri mobili da descrizione testuale
        
        Args:
            description: Descrizione testuale del mobile
            
        Returns:
            Stringa con suggerimenti o None in caso di errore
        """
        # Se IA non disponibile, usa suggerimenti di fallback
        if not self._ai_available or requests is None:
            if self.enable_fallback:
                return self._get_fallback_suggestions(description)
            return None
        
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
                # Fallback in caso di errore
                if self.enable_fallback:
                    return self._get_fallback_suggestions(description)
                return None
                
        except Exception as e:
            # Fallback in caso di eccezione
            if self.enable_fallback:
                return self._get_fallback_suggestions(description)
            return None
    
    def _get_fallback_suggestions(self, description: str) -> str:
        """Fornisce suggerimenti di fallback standard quando IA non disponibile"""
        desc_lower = description.lower()
        
        suggestions = "Suggerimenti standard (IA non disponibile):\n\n"
        
        # Analisi dimensioni dalla descrizione
        if 'pensile' in desc_lower or 'sospeso' in desc_lower:
            suggestions += "• Tipo: Pensile sospeso\n"
            suggestions += "• Dimensioni tipiche: L 60-120cm, H 60-80cm, P 30-35cm\n"
            suggestions += "• Senza zoccolo\n"
        elif 'base' in desc_lower or 'cucina' in desc_lower:
            suggestions += "• Tipo: Mobile base\n"
            suggestions += "• Dimensioni tipiche: L 60-120cm, H 85-90cm, P 55-60cm\n"
            suggestions += "• Con zoccolo 10cm\n"
        elif 'armadio' in desc_lower:
            suggestions += "• Tipo: Armadio\n"
            suggestions += "• Dimensioni tipiche: L 100-240cm, H 200-250cm, P 55-65cm\n"
        else:
            suggestions += "• Dimensioni tipiche: L 80cm, H 90cm, P 60cm\n"
        
        # Suggerimenti ripiani
        if 'ripian' in desc_lower:
            import re
            match = re.search(r'(\d+)\s*ripian', desc_lower)
            if match:
                num = match.group(1)
                suggestions += f"• Ripiani: {num} (equispaziati)\n"
            else:
                suggestions += "• Ripiani: 2-3 consigliati\n"
        else:
            suggestions += "• Ripiani: 2 consigliati\n"
        
        # Suggerimenti ante/cassetti
        if 'ante' in desc_lower or 'anta' in desc_lower:
            import re
            match = re.search(r'(\d+)\s*ant', desc_lower)
            if match:
                num = int(match.group(1))
                suggestions += f"• Ante: {num}\n"
                suggestions += f"• Cerniere: {num * 2} (2 per anta)\n"
            else:
                suggestions += "• Ante: 2 consigliate\n"
                suggestions += "• Cerniere: 4 (2 per anta)\n"
        
        if 'cassett' in desc_lower:
            import re
            match = re.search(r'(\d+)\s*cassett', desc_lower)
            if match:
                num = match.group(1)
                suggestions += f"• Cassetti: {num}\n"
                suggestions += "• Guide cassetto a sfera consigliate\n"
        
        # Suggerimenti generali
        suggestions += "\nAccorgimenti costruttivi:\n"
        suggestions += "• Spessore pannello: 18mm standard\n"
        suggestions += "• Schienale: 6mm\n"
        suggestions += "• Sistema 32mm per fori reggipiano\n"
        suggestions += "• Spinatura Ø8 per assemblaggio\n"
        
        return suggestions
    
    def parse_description_to_params(self, description: str) -> Optional[Dict[str, Any]]:
        """
        Converte descrizione testuale in parametri mobili
        
        Args:
            description: Descrizione testuale del mobile
            
        Returns:
            Dict con parametri estratti o None
        """
        # Se IA non disponibile, usa parsing semplice di fallback
        if not self._ai_available or requests is None:
            if self.enable_fallback:
                return self._parse_description_fallback(description)
            return None
        
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
            
            # Fallback se risposta non valida
            if self.enable_fallback:
                return self._parse_description_fallback(description)
            return None
            
        except Exception as e:
            # Fallback in caso di errore
            if self.enable_fallback:
                return self._parse_description_fallback(description)
            return None
    
    def _parse_description_fallback(self, description: str) -> Dict[str, Any]:
        """Parsing semplice della descrizione senza IA"""
        import re
        
        desc_lower = description.lower()
        params = {
            "larghezza": 80.0,
            "altezza": 90.0,
            "profondita": 60.0,
            "num_ripiani": 2,
            "num_ante": 0,
            "num_cassetti": 0,
            "num_cerniere": 0
        }
        
        # Estrai dimensioni numeriche (es: "80cm", "80 cm", "largo 80")
        width_match = re.search(r'(?:larg|l[=:]?\s*)(\d+(?:\.\d+)?)\s*(?:cm)?', desc_lower)
        if width_match:
            params["larghezza"] = float(width_match.group(1))
        
        height_match = re.search(r'(?:alt|h[=:]?\s*)(\d+(?:\.\d+)?)\s*(?:cm)?', desc_lower)
        if height_match:
            params["altezza"] = float(height_match.group(1))
        
        depth_match = re.search(r'(?:prof|p[=:]?\s*)(\d+(?:\.\d+)?)\s*(?:cm)?', desc_lower)
        if depth_match:
            params["profondita"] = float(depth_match.group(1))
        
        # Tipo mobile
        if 'pensile' in desc_lower:
            params["altezza"] = params.get("altezza", 70.0)
            params["profondita"] = params.get("profondita", 35.0)
        elif 'armadio' in desc_lower:
            params["altezza"] = params.get("altezza", 220.0)
        
        # Ripiani
        shelves_match = re.search(r'(\d+)\s*ripian', desc_lower)
        if shelves_match:
            params["num_ripiani"] = int(shelves_match.group(1))
        
        # Ante
        doors_match = re.search(r'(\d+)\s*ant', desc_lower)
        if doors_match:
            params["num_ante"] = int(doors_match.group(1))
            params["num_cerniere"] = params["num_ante"] * 2  # 2 cerniere per anta
        
        # Cassetti
        drawers_match = re.search(r'(\d+)\s*cassett', desc_lower)
        if drawers_match:
            params["num_cassetti"] = int(drawers_match.group(1))
        
        return params
    
    def validate_parameters(self, params: Dict[str, Any]) -> Optional[str]:
        """
        Valida coerenza parametri con IA
        
        Args:
            params: Parametri del mobile
            
        Returns:
            Stringa con eventuali warning/suggerimenti o None
        """
        # Se IA non disponibile, salta validazione (validazione base già fatta)
        if not self._ai_available or requests is None:
            return None
        
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
