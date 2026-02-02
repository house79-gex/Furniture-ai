"""
Parser per file TLG (Tool Library) di SCM
Supporta formato TLG testuale e XML
"""

import os
import re
from typing import List, Dict, Any, Optional
try:
    import xml.etree.ElementTree as ET
except ImportError:
    ET = None


class TLGLibrary:
    """Libreria utensili TLG"""
    
    def __init__(self, tlg_path: Optional[str] = None):
        """
        Inizializza libreria
        
        Args:
            tlg_path: Percorso file TLG (opzionale)
        """
        self.tools = []
        
        if tlg_path and os.path.exists(tlg_path):
            self.load_from_file(tlg_path)
        else:
            # Carica libreria di default
            self._load_default_library()
    
    def _load_default_library(self):
        """Carica libreria utensili di default per SCM Record 130TV"""
        # Gruppo foratura verticale T=1..12
        vertical_drills = [
            {'number': 1, 'type': 'drill', 'diameter': 5.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 2, 'type': 'drill', 'diameter': 6.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 3, 'type': 'drill', 'diameter': 8.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 4, 'type': 'drill', 'diameter': 10.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 5, 'type': 'drill', 'diameter': 12.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 6, 'type': 'drill', 'diameter': 16.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 7, 'type': 'drill', 'diameter': 35.0, 'orientation': 'vertical', 'max_depth': 15},  # Cerniere
            {'number': 8, 'type': 'drill', 'diameter': 5.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 9, 'type': 'drill', 'diameter': 6.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 10, 'type': 'drill', 'diameter': 8.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 11, 'type': 'drill', 'diameter': 10.0, 'orientation': 'vertical', 'max_depth': 70},
            {'number': 12, 'type': 'drill', 'diameter': 12.0, 'orientation': 'vertical', 'max_depth': 70},
        ]
        
        # Foratura orizzontale X (facce 2 e 3)
        horizontal_x_drills = [
            {'number': 42, 'type': 'drill', 'diameter': 8.0, 'orientation': 'horizontal_x', 'face': 2, 'max_depth': 60},
            {'number': 43, 'type': 'drill', 'diameter': 8.0, 'orientation': 'horizontal_x', 'face': 3, 'max_depth': 60},
            {'number': 62, 'type': 'drill', 'diameter': 5.0, 'orientation': 'horizontal_x', 'face': 2, 'max_depth': 60},
            {'number': 63, 'type': 'drill', 'diameter': 5.0, 'orientation': 'horizontal_x', 'face': 3, 'max_depth': 60},
        ]
        
        # Foratura orizzontale Y (facce 4 e 5)
        horizontal_y_drills = [
            {'number': 64, 'type': 'drill', 'diameter': 8.0, 'orientation': 'horizontal_y', 'face': 4, 'max_depth': 60},
            {'number': 65, 'type': 'drill', 'diameter': 8.0, 'orientation': 'horizontal_y', 'face': 5, 'max_depth': 60},
        ]
        
        # Mandrino principale T=101..196 (HSK63F)
        main_spindle_tools = [
            {'number': 101, 'type': 'router', 'diameter': 6.0, 'orientation': 'vertical', 'max_depth': 100},
            {'number': 102, 'type': 'router', 'diameter': 8.0, 'orientation': 'vertical', 'max_depth': 100},
            {'number': 103, 'type': 'router', 'diameter': 10.0, 'orientation': 'vertical', 'max_depth': 100},
            {'number': 104, 'type': 'router', 'diameter': 12.0, 'orientation': 'vertical', 'max_depth': 100},
            {'number': 105, 'type': 'router', 'diameter': 16.0, 'orientation': 'vertical', 'max_depth': 100},
            {'number': 106, 'type': 'router', 'diameter': 20.0, 'orientation': 'vertical', 'max_depth': 80},
            {'number': 110, 'type': 'drill', 'diameter': 35.0, 'orientation': 'vertical', 'max_depth': 15},  # Cerniere
        ]
        
        # Aggregato serratura T=280
        lock_aggregate = [
            {'number': 280, 'type': 'lock', 'diameter': 16.0, 'orientation': 'vertical', 'max_depth': 50},
        ]
        
        self.tools = (vertical_drills + horizontal_x_drills + horizontal_y_drills + 
                     main_spindle_tools + lock_aggregate)
    
    def load_from_file(self, tlg_path: str) -> bool:
        """
        Carica libreria da file TLG
        
        Args:
            tlg_path: Percorso file
            
        Returns:
            True se successo
        """
        try:
            if tlg_path.endswith('.xml'):
                return self._load_xml(tlg_path)
            else:
                return self._load_text(tlg_path)
        except Exception as e:
            return False
    
    def _load_xml(self, xml_path: str) -> bool:
        """Carica da XML"""
        if not ET:
            return False
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            self.tools = []
            
            for tool_elem in root.findall('.//Tool'):
                tool = {
                    'number': int(tool_elem.get('number', 0)),
                    'type': tool_elem.get('type', 'drill'),
                    'diameter': float(tool_elem.get('diameter', 0)),
                    'orientation': tool_elem.get('orientation', 'vertical'),
                    'max_depth': float(tool_elem.get('max_depth', 100)),
                }
                
                face = tool_elem.get('face')
                if face:
                    tool['face'] = int(face)
                
                self.tools.append(tool)
            
            return True
            
        except Exception as e:
            return False
    
    def _load_text(self, text_path: str) -> bool:
        """Carica da formato testo TLG"""
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.tools = []
            
            # Pattern base: T=<num> D=<diam> TYPE=<type> ...
            pattern = r'T=(\d+)\s+D=([\d.]+)\s+TYPE=(\w+)(?:\s+ORIENT=(\w+))?(?:\s+DEPTH=([\d.]+))?'
            
            for match in re.finditer(pattern, content, re.IGNORECASE):
                tool = {
                    'number': int(match.group(1)),
                    'diameter': float(match.group(2)),
                    'type': match.group(3).lower(),
                    'orientation': match.group(4) if match.group(4) else 'vertical',
                    'max_depth': float(match.group(5)) if match.group(5) else 100.0,
                }
                self.tools.append(tool)
            
            return len(self.tools) > 0
            
        except Exception as e:
            return False
    
    def select_drill_tool(self, diameter: float, face: int = 1, 
                         depth: float = 50.0) -> Optional[Dict[str, Any]]:
        """
        Seleziona utensile per foratura
        
        Args:
            diameter: Diametro richiesto
            face: Faccia di lavoro (1-5)
            depth: Profondità richiesta
            
        Returns:
            Dict utensile o None
        """
        candidates = []
        
        for tool in self.tools:
            # Solo punte
            if tool['type'] != 'drill':
                continue
            
            # Verifica diametro (tolleranza ±0.1mm)
            if abs(tool['diameter'] - diameter) > 0.1:
                continue
            
            # Verifica profondità
            if depth > tool.get('max_depth', 100):
                continue
            
            # Verifica orientamento e faccia
            if face == 1:
                if tool['orientation'] == 'vertical':
                    candidates.append(tool)
            elif face in [2, 3]:
                if tool['orientation'] == 'horizontal_x':
                    if tool.get('face') == face:
                        candidates.append(tool)
            elif face in [4, 5]:
                if tool['orientation'] == 'horizontal_y':
                    if tool.get('face') == face:
                        candidates.append(tool)
        
        # Restituisci primo candidato valido
        return candidates[0] if candidates else None
    
    def select_routing_tool(self, diameter: float, face: int = 1) -> Optional[Dict[str, Any]]:
        """
        Seleziona utensile per fresatura
        
        Args:
            diameter: Diametro fresa
            face: Faccia di lavoro
            
        Returns:
            Dict utensile o None
        """
        candidates = []
        
        for tool in self.tools:
            if tool['type'] != 'router':
                continue
            
            # Verifica diametro (tolleranza ±0.5mm)
            if abs(tool['diameter'] - diameter) > 0.5:
                continue
            
            # Preferisci utensili appropriati per faccia
            if face == 1 and tool['orientation'] == 'vertical':
                candidates.append(tool)
            elif face in [2, 3, 4, 5]:
                candidates.append(tool)
        
        return candidates[0] if candidates else None
    
    def get_tool_by_number(self, number: int) -> Optional[Dict[str, Any]]:
        """Ottiene utensile per numero"""
        for tool in self.tools:
            if tool['number'] == number:
                return tool
        return None
    
    def list_tools_by_type(self, tool_type: str) -> List[Dict[str, Any]]:
        """Lista utensili per tipo"""
        return [t for t in self.tools if t['type'] == tool_type]
