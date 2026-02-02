"""
Post-processore Xilog Plus per SCM Record 130TV (NUM 1050)

Genera codice Xilog Plus per CNC SCM Record 130TV con:
- NUM 1050 controllo 4 assi + Asse C (non continuo)
- Campo lavoro: 2930x1300 mm, passaggio pezzo Z 280mm
- Mandrino principale 14kW HSK63F 12 posizioni
- Gruppo foratura 18 mandrini verticali
- Aggregato serratura 3kW Ø16
"""

from typing import List, Dict, Any, Tuple
import math


class XilogGenerator:
    """Generatore codice Xilog Plus"""
    
    def __init__(self, tlg_library=None):
        """
        Inizializza generatore
        
        Args:
            tlg_library: Istanza TLGLibrary per selezione utensili
        """
        self.tlg_library = tlg_library
        self.program_lines = []
        self.current_face = 1
        
    def add_header(self, part_name: str, dimensions: Tuple[float, float, float]):
        """
        Aggiunge intestazione programma
        
        Args:
            part_name: Nome pezzo
            dimensions: Tuple (L, W, T) in mm
        """
        L, W, T = dimensions
        
        self.program_lines.extend([
            '; ================================================================',
            f'; PROGRAMMA: {part_name}',
            '; Generato da FurnitureAI per SCM Record 130TV (NUM 1050)',
            '; ================================================================',
            f'; DIMENSIONI PEZZO: L={L:.1f} W={W:.1f} T={T:.1f} mm',
            '; ================================================================',
            '',
            '; Inizializzazione',
            'G90 ; Programmazione assoluta',
            'G71 ; Unità in mm',
            '',
        ])
    
    def add_face_change(self, face: int):
        """
        Cambia faccia di lavoro
        
        Args:
            face: Numero faccia (1-5)
                F=1: Faccia superiore (foratura verticale)
                F=2: Faccia anteriore (foratura orizzontale X, retro)
                F=3: Faccia posteriore (foratura orizzontale X, fronte)
                F=4: Faccia destra (foratura orizzontale Y)
                F=5: Faccia sinistra (foratura orizzontale Y)
        """
        if face != self.current_face:
            self.program_lines.extend([
                '',
                f'; ---- CAMBIO FACCIA F={face} ----',
                f'F={face}',
                '',
            ])
            self.current_face = face
    
    def add_drilling(self, holes: List[Dict[str, Any]], face: int = 1, optimized: bool = True):
        """
        Aggiunge operazioni di foratura
        
        Args:
            holes: Lista di dict con 'x', 'y', 'z', 'diameter', 'depth'
            face: Faccia di lavoro
            optimized: Se True usa XBO (ottimizzato), altrimenti XB
        """
        if not holes:
            return
        
        self.add_face_change(face)
        
        # Raggruppa per diametro
        holes_by_diameter = {}
        for hole in holes:
            diameter = hole['diameter']
            if diameter not in holes_by_diameter:
                holes_by_diameter[diameter] = []
            holes_by_diameter[diameter].append(hole)
        
        # Genera codice per ogni gruppo
        for diameter, hole_group in holes_by_diameter.items():
            # Seleziona utensile
            tool = self._select_tool(diameter, face)
            
            self.program_lines.extend([
                f'; Foratura Ø{diameter} mm (T={tool})',
                f'T={tool} ; Seleziona utensile',
                '',
            ])
            
            if optimized:
                # XBO - Foratura ottimizzata
                self.program_lines.append(f'XBO ; Foratura ottimizzata Ø{diameter}')
                for hole in hole_group:
                    x, y, z = hole['x'], hole['y'], hole.get('z', 0)
                    depth = hole['depth']
                    self.program_lines.append(
                        f'  X={x:.2f} Y={y:.2f} Z={z:.2f} P={depth:.2f}'
                    )
                self.program_lines.append('XBOE ; Fine foratura ottimizzata')
            else:
                # XB - Foratura singola
                for hole in hole_group:
                    x, y, z = hole['x'], hole['y'], hole.get('z', 0)
                    depth = hole['depth']
                    self.program_lines.append(
                        f'XB X={x:.2f} Y={y:.2f} Z={z:.2f} P={depth:.2f} ; Foro singolo'
                    )
            
            self.program_lines.append('')
    
    def add_routing(self, path: List[Tuple[float, float]], depth: float, 
                   tool_diameter: float, face: int = 1):
        """
        Aggiunge operazione di fresatura/contorno
        
        Args:
            path: Lista di punti (x, y)
            depth: Profondità fresatura
            tool_diameter: Diametro fresa
            face: Faccia di lavoro
        """
        if not path or len(path) < 2:
            return
        
        self.add_face_change(face)
        
        # Seleziona utensile per fresatura
        tool = self._select_routing_tool(tool_diameter, face)
        
        self.program_lines.extend([
            f'; Fresatura/Contorno (T={tool}, Ø{tool_diameter}mm)',
            f'T={tool}',
            '',
            'XGIN ; Inizio lavorazione',
        ])
        
        # Primo punto - ingresso
        x0, y0 = path[0]
        self.program_lines.append(f'XG0 X={x0:.2f} Y={y0:.2f} ; Posizionamento')
        self.program_lines.append(f'XG1 Z={depth:.2f} ; Discesa')
        
        # Percorso
        for x, y in path[1:]:
            self.program_lines.append(f'XL2P X={x:.2f} Y={y:.2f} ; Linea')
        
        # Uscita
        self.program_lines.extend([
            'XG0 Z=0 ; Risalita',
            'XGOUT ; Fine lavorazione',
            '',
        ])
    
    def add_groove(self, start_x: float, start_y: float, length: float,
                  width: float, depth: float, orientation: str = 'X'):
        """
        Aggiunge scanalatura
        
        Args:
            start_x, start_y: Punto inizio
            length: Lunghezza scanalatura
            width: Larghezza scanalatura
            depth: Profondità
            orientation: 'X' o 'Y'
        """
        self.program_lines.extend([
            f'; Scanalatura L={length:.1f} W={width:.1f} P={depth:.1f}',
            f'XG0 X={start_x:.2f} Y={start_y:.2f}',
        ])
        
        if orientation == 'X':
            end_x = start_x + length
            self.program_lines.append(f'XL2P X={end_x:.2f} Y={start_y:.2f}')
        else:  # Y
            end_y = start_y + length
            self.program_lines.append(f'XL2P X={start_x:.2f} Y={end_y:.2f}')
        
        self.program_lines.append('')
    
    def add_dowel_holes(self, positions: List[Tuple[float, float]], 
                       diameter: float = 8.0, depth: float = 40.0):
        """
        Aggiunge fori per spinatura
        
        Args:
            positions: Lista di posizioni (x, y)
            diameter: Diametro spine (default 8mm)
            depth: Profondità fori (default 40mm)
        """
        holes = [
            {'x': x, 'y': y, 'diameter': diameter, 'depth': depth}
            for x, y in positions
        ]
        self.add_drilling(holes, face=1, optimized=True)
    
    def add_hinge_holes(self, positions: List[Tuple[float, float]], 
                       diameter: float = 35.0, depth: float = 13.0):
        """
        Aggiunge fori per cerniere
        
        Args:
            positions: Lista di posizioni (x, y)
            diameter: Diametro foro (default 35mm per cerniere standard)
            depth: Profondità (default 13mm)
        """
        holes = [
            {'x': x, 'y': y, 'diameter': diameter, 'depth': depth}
            for x, y in positions
        ]
        self.add_drilling(holes, face=1, optimized=True)
    
    def add_safety_notes(self):
        """Aggiunge note di sicurezza"""
        self.program_lines.extend([
            '',
            '; ================================================================',
            '; NOTE SICUREZZA',
            '; ================================================================',
            '; - Verificare fissaggio pezzo prima di avviare programma',
            '; - Controllare utensili montati e condizioni',
            '; - Verificare assenza ostacoli nell\'area di lavoro',
            '; - Utilizzare aspirazione trucioli',
            '; ================================================================',
            '',
        ])
    
    def add_footer(self):
        """Aggiunge footer programma"""
        self.program_lines.extend([
            '',
            '; Fine programma',
            'M30 ; Stop programma',
            '',
        ])
    
    def generate(self) -> str:
        """
        Genera codice completo
        
        Returns:
            Stringa con codice Xilog Plus
        """
        return '\n'.join(self.program_lines)
    
    def _select_tool(self, diameter: float, face: int) -> int:
        """
        Seleziona utensile appropriato per foratura
        
        Args:
            diameter: Diametro foro
            face: Faccia di lavoro
            
        Returns:
            Numero utensile
        """
        if self.tlg_library:
            tool = self.tlg_library.select_drill_tool(diameter, face)
            if tool:
                return tool['number']
        
        # Selezione di default basata su faccia
        if face == 1:
            # Verticale - gruppo foratura T=1..12
            if diameter <= 5:
                return 1
            elif diameter <= 8:
                return 2
            elif diameter <= 10:
                return 3
            elif diameter <= 35:
                return 4
            else:
                return 101  # Mandrino principale
        elif face in [2, 3]:
            # Orizzontale X
            return 42 if face == 2 else 43
        elif face in [4, 5]:
            # Orizzontale Y
            return 64 if face == 4 else 65
        else:
            return 101  # Default mandrino principale
    
    def _select_routing_tool(self, diameter: float, face: int) -> int:
        """Seleziona utensile per fresatura"""
        if self.tlg_library:
            tool = self.tlg_library.select_routing_tool(diameter, face)
            if tool:
                return tool['number']
        
        # Default: mandrino principale
        return 101
    
    def save_to_file(self, filename: str) -> bool:
        """
        Salva programma su file
        
        Args:
            filename: Nome file output
            
        Returns:
            True se successo
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.generate())
            return True
        except Exception as e:
            return False
