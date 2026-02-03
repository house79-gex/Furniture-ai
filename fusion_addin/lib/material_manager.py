"""
Gestore Materiali per FurnitureAI
Gestisce l'applicazione di materiali ai componenti del mobile
"""

import adsk.core
import adsk.fusion
from typing import Dict, List, Optional
from . import logging_utils

logger = logging_utils.get_logger()


class MaterialManager:
    """Gestisce i materiali per i mobili"""
    
    # Preset materiali disponibili
    PRESET_MATERIALS = {
        'Rovere': {
            'library': 'Fusion 360 Material Library',
            'material': 'Wood - Oak',
            'description': 'Rovere naturale',
            'appearance': 'Oak'
        },
        'Noce': {
            'library': 'Fusion 360 Material Library',
            'material': 'Wood - Walnut',
            'description': 'Noce naturale',
            'appearance': 'Walnut'
        },
        'Laccato Bianco': {
            'library': 'Fusion 360 Material Library',
            'material': 'Paint - Enamel Glossy (White)',
            'description': 'Laccato bianco lucido',
            'appearance': 'White Enamel'
        },
        'Laccato Nero': {
            'library': 'Fusion 360 Material Library',
            'material': 'Paint - Enamel Glossy (Black)',
            'description': 'Laccato nero lucido',
            'appearance': 'Black Enamel'
        },
        'Melaminico Bianco': {
            'library': 'Fusion 360 Material Library',
            'material': 'Paint - Enamel Glossy (White)',
            'description': 'Melaminico bianco',
            'appearance': 'White Enamel'
        },
        'Melaminico Grigio': {
            'library': 'Fusion 360 Material Library',
            'material': 'Paint - Enamel Glossy (Gray)',
            'description': 'Melaminico grigio',
            'appearance': 'Gray Enamel'
        },
        'Vetro Trasparente': {
            'library': 'Fusion 360 Material Library',
            'material': 'Glass',
            'description': 'Vetro trasparente',
            'appearance': 'Glass - Clear'
        },
        'Metallo Alluminio': {
            'library': 'Fusion 360 Material Library',
            'material': 'Aluminum - 6061',
            'description': 'Alluminio anodizzato',
            'appearance': 'Aluminum - Anodized'
        }
    }
    
    def __init__(self, design: adsk.fusion.Design):
        """
        Inizializza il gestore materiali
        
        Args:
            design: Design Fusion 360
        """
        self.design = design
        self.app = adsk.core.Application.get()
        
    def get_material_from_library(self, preset_name: str) -> Optional[adsk.core.Material]:
        """
        Ottiene un materiale dalla libreria Fusion 360
        
        Args:
            preset_name: Nome del preset materiale
            
        Returns:
            Materiale o None se non trovato
        """
        try:
            if preset_name not in self.PRESET_MATERIALS:
                logger.warning('Preset materiale {} non trovato'.format(preset_name))
                return None
            
            preset = self.PRESET_MATERIALS[preset_name]
            
            # Cerca nella libreria materiali
            material_libs = self.app.materialLibraries
            for lib in material_libs:
                if preset['library'] in lib.name:
                    for mat in lib.materials:
                        if preset['material'] in mat.name:
                            logger.info('Materiale trovato: {}'.format(mat.name))
                            return mat
            
            logger.warning('Materiale {} non trovato in libreria'.format(preset['material']))
            return None
            
        except Exception as e:
            logger.error('Errore ricerca materiale: {}'.format(str(e)))
            return None
    
    def apply_material_uniform(self, component: adsk.fusion.Component, 
                              preset_name: str) -> bool:
        """
        Applica lo stesso materiale a tutti i corpi del componente
        
        Args:
            component: Componente Fusion 360
            preset_name: Nome del preset materiale
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            material = self.get_material_from_library(preset_name)
            if not material:
                logger.warning('Impossibile applicare materiale: non trovato')
                return False
            
            # Applica a tutti i corpi
            count = 0
            for body in component.bRepBodies:
                body.material = material
                count += 1
                logger.info('Materiale {} applicato a {}'.format(preset_name, body.name))
            
            logger.info('Materiale {} applicato a {} corpi'.format(preset_name, count))
            return True
            
        except Exception as e:
            logger.error('Errore applicazione materiale uniforme: {}'.format(str(e)))
            return False
    
    def apply_materials_differentiated(self, component: adsk.fusion.Component,
                                       materials_map: Dict[str, str]) -> bool:
        """
        Applica materiali differenziati per tipo di componente
        
        Args:
            component: Componente Fusion 360
            materials_map: Dizionario tipo->preset_name
                          Es: {'fianco': 'Rovere', 'anta': 'Laccato Bianco', 'schienale': 'Melaminico Bianco'}
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            # Carica materiali
            materials = {}
            for comp_type, preset_name in materials_map.items():
                mat = self.get_material_from_library(preset_name)
                if mat:
                    materials[comp_type] = mat
                else:
                    logger.warning('Materiale {} per {} non trovato'.format(preset_name, comp_type))
            
            if not materials:
                logger.warning('Nessun materiale valido da applicare')
                return False
            
            # Applica materiali in base al nome del corpo
            count = 0
            for body in component.bRepBodies:
                body_name = body.name.lower()
                
                # Determina tipo componente dal nome
                comp_type = None
                if 'fianco' in body_name or 'lato' in body_name:
                    comp_type = 'fianco'
                elif 'ripiano' in body_name or 'mensola' in body_name:
                    comp_type = 'ripiano'
                elif 'anta' in body_name or 'sportello' in body_name:
                    comp_type = 'anta'
                elif 'schienale' in body_name or 'retro' in body_name:
                    comp_type = 'schienale'
                elif 'base' in body_name or 'top' in body_name:
                    comp_type = 'struttura'
                elif 'cassetto' in body_name:
                    comp_type = 'cassetto'
                elif 'zoccolo' in body_name:
                    comp_type = 'zoccolo'
                
                # Applica materiale se trovato
                if comp_type and comp_type in materials:
                    body.material = materials[comp_type]
                    count += 1
                    logger.info('Materiale {} applicato a {} ({})'.format(
                        materials_map.get(comp_type), body.name, comp_type))
                elif 'corpo' in materials:
                    # Materiale di default per il corpo
                    body.material = materials['corpo']
                    count += 1
                    logger.info('Materiale corpo applicato a {}'.format(body.name))
            
            logger.info('Materiali differenziati applicati a {} corpi'.format(count))
            return True
            
        except Exception as e:
            logger.error('Errore applicazione materiali differenziati: {}'.format(str(e)))
            return False
    
    def apply_appearance(self, component: adsk.fusion.Component,
                        preset_name: str) -> bool:
        """
        Applica un'apparenza a tutti i corpi del componente
        (alternativa se i materiali non sono disponibili)
        
        Args:
            component: Componente Fusion 360
            preset_name: Nome del preset materiale
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            if preset_name not in self.PRESET_MATERIALS:
                logger.warning('Preset {} non trovato'.format(preset_name))
                return False
            
            preset = self.PRESET_MATERIALS[preset_name]
            appearance_name = preset.get('appearance')
            
            if not appearance_name:
                logger.warning('Apparenza non definita per preset {}'.format(preset_name))
                return False
            
            # Cerca apparenza in libreria
            appearance_libs = self.app.materialLibraries
            appearance = None
            
            for lib in appearance_libs:
                for app in lib.appearances:
                    if appearance_name in app.name:
                        appearance = app
                        break
                if appearance:
                    break
            
            if not appearance:
                logger.warning('Apparenza {} non trovata'.format(appearance_name))
                return False
            
            # Applica a tutti i corpi
            count = 0
            for body in component.bRepBodies:
                body.appearance = appearance
                count += 1
                logger.info('Apparenza {} applicata a {}'.format(appearance_name, body.name))
            
            logger.info('Apparenza applicata a {} corpi'.format(count))
            return True
            
        except Exception as e:
            logger.error('Errore applicazione apparenza: {}'.format(str(e)))
            return False
    
    @staticmethod
    def get_preset_names() -> List[str]:
        """
        Restituisce la lista dei nomi dei preset disponibili
        
        Returns:
            Lista di nomi preset
        """
        return list(MaterialManager.PRESET_MATERIALS.keys())
    
    @staticmethod
    def get_preset_description(preset_name: str) -> str:
        """
        Restituisce la descrizione di un preset
        
        Args:
            preset_name: Nome del preset
            
        Returns:
            Descrizione o stringa vuota
        """
        preset = MaterialManager.PRESET_MATERIALS.get(preset_name)
        if preset:
            return preset.get('description', '')
        return ''
