"""
Sistema Modulare per FurnitureAI
Gestisce la creazione di progetti complessi con multipli moduli (cucine, armadi)
"""

import adsk.core
import adsk.fusion
from typing import Dict, Any, List, Optional
from . import logging_utils, furniture_generator

logger = logging_utils.get_logger()


class ModularProject:
    """Gestisce progetti modulari con multipli cabinet"""
    
    def __init__(self, design: adsk.fusion.Design, project_name: str = 'Progetto_Modulare'):
        """
        Inizializza un progetto modulare
        
        Args:
            design: Design Fusion 360
            project_name: Nome del progetto
        """
        self.design = design
        self.project_name = project_name
        self.modules = []  # Lista di ComponentOccurrence
        self.root_component = design.rootComponent
        
    def add_cabinet_module(self, params: Dict[str, Any], 
                          position_x: float = 0, 
                          position_y: float = 0, 
                          position_z: float = 0,
                          module_name: Optional[str] = None) -> Optional[adsk.fusion.Occurrence]:
        """
        Aggiunge un modulo cabinet al progetto
        
        Args:
            params: Parametri del mobile
            position_x: Posizione X globale (cm)
            position_y: Posizione Y globale (cm)
            position_z: Posizione Z globale (cm)
            module_name: Nome opzionale per il modulo
            
        Returns:
            ComponentOccurrence del modulo creato o None se errore
        """
        try:
            # Genera nome modulo
            if not module_name:
                module_name = 'Modulo_{}'.format(len(self.modules) + 1)
            
            logger.info('Creazione modulo {} a posizione ({}, {}, {})'.format(
                module_name, position_x, position_y, position_z))
            
            # Crea nuovo componente
            occurrences = self.root_component.occurrences
            transform = adsk.core.Matrix3D.create()
            
            # Imposta traslazione (valori in cm, già unità interne Fusion 360)
            transform.translation = adsk.core.Vector3D.create(position_x, position_y, position_z)
            
            # Crea occurrence
            new_occurrence = occurrences.addNewComponent(transform)
            new_component = new_occurrence.component
            new_component.name = module_name
            
            # Genera geometria nel nuovo componente
            result = furniture_generator.generate_furniture_in_component(new_component, params)
            
            if result['success']:
                self.modules.append(new_occurrence)
                logger.info('Modulo {} creato con successo: {} elementi'.format(
                    module_name, len(result['components'])))
                return new_occurrence
            else:
                logger.error('Errore creazione modulo {}: {}'.format(
                    module_name, result['error']))
                # Rimuovi occurrence fallita
                new_occurrence.deleteMe()
                return None
                
        except Exception as e:
            logger.error('Errore aggiunta modulo cabinet: {}'.format(str(e)))
            return None
    
    def auto_layout_linear(self, modules_params: List[Dict[str, Any]], 
                          direction: str = 'X',
                          spacing: float = 0) -> bool:
        """
        Crea un layout lineare di moduli
        
        Args:
            modules_params: Lista di dizionari con parametri per ogni modulo
            direction: Direzione layout ('X', 'Y', o 'Z')
            spacing: Spaziatura tra moduli (cm)
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            logger.info('Creazione layout lineare: {} moduli in direzione {}'.format(
                len(modules_params), direction))
            
            current_pos = {'X': 0, 'Y': 0, 'Z': 0}
            
            for i, params in enumerate(modules_params):
                # Nome modulo
                module_name = params.get('nome_modulo', 'Modulo_{}'.format(i + 1))
                
                # Crea modulo alla posizione corrente
                occurrence = self.add_cabinet_module(
                    params,
                    position_x=current_pos['X'],
                    position_y=current_pos['Y'],
                    position_z=current_pos['Z'],
                    module_name=module_name
                )
                
                if occurrence:
                    # Calcola posizione per il prossimo modulo
                    if direction == 'X':
                        current_pos['X'] += params['larghezza'] + spacing
                    elif direction == 'Y':
                        current_pos['Y'] += params['profondita'] + spacing
                    elif direction == 'Z':
                        current_pos['Z'] += params['altezza'] + spacing
                else:
                    logger.warning('Modulo {} non creato'.format(module_name))
            
            logger.info('Layout completato: {} moduli creati'.format(len(self.modules)))
            return len(self.modules) > 0
            
        except Exception as e:
            logger.error('Errore creazione layout lineare: {}'.format(str(e)))
            return False
    
    def auto_layout_grid(self, modules_params: List[Dict[str, Any]],
                        rows: int, cols: int,
                        spacing_x: float = 0,
                        spacing_y: float = 0) -> bool:
        """
        Crea un layout a griglia di moduli
        
        Args:
            modules_params: Lista di dizionari con parametri per ogni modulo
            rows: Numero di righe
            cols: Numero di colonne
            spacing_x: Spaziatura tra colonne (cm)
            spacing_y: Spaziatura tra righe (cm)
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            logger.info('Creazione layout griglia: {}x{} = {} moduli'.format(
                rows, cols, len(modules_params)))
            
            module_index = 0
            y_pos = 0
            
            for row in range(rows):
                x_pos = 0
                max_depth = 0
                
                for col in range(cols):
                    if module_index >= len(modules_params):
                        break
                    
                    params = modules_params[module_index]
                    module_name = params.get('nome_modulo', 'Modulo_R{}_C{}'.format(row + 1, col + 1))
                    
                    # Crea modulo
                    occurrence = self.add_cabinet_module(
                        params,
                        position_x=x_pos,
                        position_y=y_pos,
                        position_z=0,
                        module_name=module_name
                    )
                    
                    if occurrence:
                        # Aggiorna posizioni
                        x_pos += params['larghezza'] + spacing_x
                        max_depth = max(max_depth, params['profondita'])
                    
                    module_index += 1
                
                # Passa alla riga successiva
                y_pos += max_depth + spacing_y
            
            logger.info('Layout griglia completato: {} moduli creati'.format(len(self.modules)))
            return len(self.modules) > 0
            
        except Exception as e:
            logger.error('Errore creazione layout griglia: {}'.format(str(e)))
            return False
    
    def auto_layout_l_shape(self, modules_left: List[Dict[str, Any]],
                           modules_right: List[Dict[str, Any]],
                           spacing: float = 0) -> bool:
        """
        Crea un layout a L con due file di moduli
        
        Args:
            modules_left: Lista parametri moduli per lato sinistro
            modules_right: Lista parametri moduli per lato destro
            spacing: Spaziatura tra moduli (cm)
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            logger.info('Creazione layout L: {} moduli sinistra, {} moduli destra'.format(
                len(modules_left), len(modules_right)))
            
            # Crea lato sinistro (lungo X)
            x_pos = 0
            for i, params in enumerate(modules_left):
                module_name = params.get('nome_modulo', 'Modulo_SX_{}'.format(i + 1))
                
                occurrence = self.add_cabinet_module(
                    params,
                    position_x=x_pos,
                    position_y=0,
                    position_z=0,
                    module_name=module_name
                )
                
                if occurrence:
                    x_pos += params['larghezza'] + spacing
            
            # Punto di partenza lato destro
            if modules_left:
                last_module_width = modules_left[-1]['larghezza']
                last_module_depth = modules_left[-1]['profondita']
                right_x = x_pos - last_module_width - spacing
                right_y = last_module_depth + spacing
            else:
                right_x = 0
                right_y = 0
            
            # Crea lato destro (lungo Y)
            y_pos = right_y
            for i, params in enumerate(modules_right):
                module_name = params.get('nome_modulo', 'Modulo_DX_{}'.format(i + 1))
                
                occurrence = self.add_cabinet_module(
                    params,
                    position_x=right_x,
                    position_y=y_pos,
                    position_z=0,
                    module_name=module_name
                )
                
                if occurrence:
                    y_pos += params['profondita'] + spacing
            
            logger.info('Layout L completato: {} moduli totali'.format(len(self.modules)))
            return len(self.modules) > 0
            
        except Exception as e:
            logger.error('Errore creazione layout L: {}'.format(str(e)))
            return False
    
    def get_modules_count(self) -> int:
        """
        Restituisce il numero di moduli nel progetto
        
        Returns:
            Numero di moduli
        """
        return len(self.modules)
    
    def get_modules(self) -> List[adsk.fusion.Occurrence]:
        """
        Restituisce la lista di tutti i moduli
        
        Returns:
            Lista di ComponentOccurrence
        """
        return self.modules.copy()
    
    def clear_modules(self) -> bool:
        """
        Rimuove tutti i moduli dal progetto
        
        Returns:
            True se successo, False altrimenti
        """
        try:
            for occurrence in self.modules:
                if occurrence.isValid:
                    occurrence.deleteMe()
            
            self.modules.clear()
            logger.info('Tutti i moduli rimossi')
            return True
            
        except Exception as e:
            logger.error('Errore rimozione moduli: {}'.format(str(e)))
            return False
