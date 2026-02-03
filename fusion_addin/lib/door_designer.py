"""
Designer Ante Custom per FurnitureAI
Crea ante con diversi stili: piatta, bugna, cornice, vetro, profilo custom
"""

import adsk.core
import adsk.fusion
import math
from typing import Dict, Any, Optional
from . import logging_utils

logger = logging_utils.get_logger()


class DoorDesigner:
    """Designer per ante custom"""
    
    # Tipi di ante supportati
    DOOR_TYPES = {
        'piatta': 'Anta piatta liscia',
        'bugna': 'Anta con bugna (pannello rialzato)',
        'cornice': 'Anta con cornice perimetrale',
        'vetro': 'Anta con inserto vetro',
        'custom': 'Anta con profilo custom'
    }
    
    def __init__(self, component: adsk.fusion.Component):
        """
        Inizializza il designer ante
        
        Args:
            component: Componente Fusion 360 dove creare l'anta
        """
        self.component = component
        
    def create_door(self, door_type: str, width: float, height: float, 
                   thickness: float, params: Optional[Dict[str, Any]] = None) -> Optional[adsk.fusion.BRepBody]:
        """
        Crea un'anta del tipo specificato
        
        Args:
            door_type: Tipo di anta ('piatta', 'bugna', 'cornice', 'vetro', 'custom')
            width: Larghezza anta (cm)
            height: Altezza anta (cm)
            thickness: Spessore anta (cm)
            params: Parametri aggiuntivi specifici per tipo
            
        Returns:
            BRepBody dell'anta creata o None se errore
        """
        try:
            logger.info('Creazione anta tipo {} ({}x{}x{})'.format(
                door_type, width, height, thickness))
            
            if door_type == 'piatta':
                return self.create_flat_door(width, height, thickness)
            elif door_type == 'bugna':
                return self.create_raised_panel_door(width, height, thickness, params)
            elif door_type == 'cornice':
                return self.create_frame_door(width, height, thickness, params)
            elif door_type == 'vetro':
                return self.create_glass_door(width, height, thickness, params)
            elif door_type == 'custom':
                return self.create_custom_profile_door(width, height, thickness, params)
            else:
                logger.error('Tipo anta non supportato: {}'.format(door_type))
                return None
                
        except Exception as e:
            logger.error('Errore creazione anta: {}'.format(str(e)))
            return None
    
    def create_flat_door(self, width: float, height: float, 
                        thickness: float) -> Optional[adsk.fusion.BRepBody]:
        """
        Crea anta piatta liscia
        
        Args:
            width: Larghezza (cm)
            height: Altezza (cm)
            thickness: Spessore (cm)
            
        Returns:
            BRepBody dell'anta o None
        """
        try:
            # Crea sketch sul piano XY
            sketch = self.component.sketches.add(self.component.xYConstructionPlane)
            
            # Rettangolo
            rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(0, 0, 0),
                adsk.core.Point3D.create(width, height, 0)
            )
            
            # Estrusione
            profile = sketch.profiles.item(0)
            extrudes = self.component.features.extrudeFeatures
            extrude_input = extrudes.createInput(profile, 
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            distance = adsk.core.ValueInput.createByReal(thickness)
            extrude_input.setDistanceExtent(False, distance)
            
            extrude = extrudes.add(extrude_input)
            body = extrude.bodies.item(0)
            body.name = 'Anta_Piatta'
            
            logger.info('Anta piatta creata')
            return body
            
        except Exception as e:
            logger.error('Errore creazione anta piatta: {}'.format(str(e)))
            return None
    
    def create_raised_panel_door(self, width: float, height: float, 
                                thickness: float, 
                                params: Optional[Dict[str, Any]] = None) -> Optional[adsk.fusion.BRepBody]:
        """
        Crea anta con bugna (pannello rialzato centrale)
        
        Args:
            width: Larghezza (cm)
            height: Altezza (cm)
            thickness: Spessore (cm)
            params: Parametri:
                - border_width: Larghezza bordo (default 5 cm)
                - raise_height: Altezza rialzo centrale (default 0.5 cm)
                
        Returns:
            BRepBody dell'anta o None
        """
        try:
            if params is None:
                params = {}
            
            border_width = params.get('border_width', 5.0)
            raise_height = params.get('raise_height', 0.5)
            
            logger.info('Creazione anta bugna: bordo={}, rialzo={}'.format(
                border_width, raise_height))
            
            # 1. Pannello base
            base_door = self.create_flat_door(width, height, thickness)
            if not base_door:
                return None
            
            # 2. Crea pannello rialzato centrale
            panel_width = width - 2 * border_width
            panel_height = height - 2 * border_width
            
            if panel_width <= 0 or panel_height <= 0:
                logger.warning('Dimensioni pannello centrale non valide')
                return base_door
            
            # Sketch per pannello centrale
            sketch = self.component.sketches.add(self.component.xYConstructionPlane)
            
            # Offset per centrare il pannello
            x_offset = border_width
            y_offset = border_width
            
            rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(x_offset, y_offset, 0),
                adsk.core.Point3D.create(x_offset + panel_width, y_offset + panel_height, 0)
            )
            
            # Estrusione rialzata
            profile = sketch.profiles.item(0)
            extrudes = self.component.features.extrudeFeatures
            extrude_input = extrudes.createInput(profile, 
                adsk.fusion.FeatureOperations.JoinFeatureOperation)
            
            # Imposta offset iniziale alla superficie dell'anta
            extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
                adsk.core.ValueInput.createByReal(thickness)
            )
            
            distance = adsk.core.ValueInput.createByReal(raise_height)
            extrude_input.setDistanceExtent(False, distance)
            
            extrude = extrudes.add(extrude_input)
            
            base_door.name = 'Anta_Bugna'
            logger.info('Anta con bugna creata')
            return base_door
            
        except Exception as e:
            logger.error('Errore creazione anta bugna: {}'.format(str(e)))
            return None
    
    def create_frame_door(self, width: float, height: float, 
                         thickness: float,
                         params: Optional[Dict[str, Any]] = None) -> Optional[adsk.fusion.BRepBody]:
        """
        Crea anta con cornice perimetrale
        
        Args:
            width: Larghezza (cm)
            height: Altezza (cm)
            thickness: Spessore (cm)
            params: Parametri:
                - frame_width: Larghezza cornice (default 6 cm)
                - frame_depth: Profondità cornice (default 1 cm)
                
        Returns:
            BRepBody dell'anta o None
        """
        try:
            if params is None:
                params = {}
            
            frame_width = params.get('frame_width', 6.0)
            frame_depth = params.get('frame_depth', 1.0)
            
            logger.info('Creazione anta cornice: larghezza={}, profondità={}'.format(
                frame_width, frame_depth))
            
            # 1. Pannello base
            base_door = self.create_flat_door(width, height, thickness)
            if not base_door:
                return None
            
            # 2. Crea cornice perimetrale con sweep
            # Sketch path rettangolare
            sketch_path = self.component.sketches.add(self.component.xYConstructionPlane)
            
            # Rettangolo per path con offset per centrare la cornice
            path_offset = frame_width / 2
            
            lines = sketch_path.sketchCurves.sketchLines
            line1 = lines.addByTwoPoints(
                adsk.core.Point3D.create(path_offset, path_offset, 0),
                adsk.core.Point3D.create(width - path_offset, path_offset, 0)
            )
            line2 = lines.addByTwoPoints(
                line1.endSketchPoint,
                adsk.core.Point3D.create(width - path_offset, height - path_offset, 0)
            )
            line3 = lines.addByTwoPoints(
                line2.endSketchPoint,
                adsk.core.Point3D.create(path_offset, height - path_offset, 0)
            )
            line4 = lines.addByTwoPoints(
                line3.endSketchPoint,
                line1.startSketchPoint
            )
            
            # Crea path
            path = self.component.features.createPath(line1, True)
            
            # Sketch profilo cornice (rettangolare semplice)
            # Piano verticale per profilo
            planes = self.component.constructionPlanes
            plane_input = planes.createInput()
            plane_input.setByOffset(
                self.component.xZConstructionPlane,
                adsk.core.ValueInput.createByReal(path_offset)
            )
            profile_plane = planes.add(plane_input)
            
            sketch_profile = self.component.sketches.add(profile_plane)
            profile_rect = sketch_profile.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(path_offset, thickness, 0),
                adsk.core.Point3D.create(path_offset, thickness + frame_depth, frame_width)
            )
            
            # Sweep
            profile = sketch_profile.profiles.item(0)
            sweeps = self.component.features.sweepFeatures
            sweep_input = sweeps.createInput(profile, path, 
                adsk.fusion.FeatureOperations.JoinFeatureOperation)
            sweep_input.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
            
            sweep = sweeps.add(sweep_input)
            
            base_door.name = 'Anta_Cornice'
            logger.info('Anta con cornice creata')
            return base_door
            
        except Exception as e:
            logger.error('Errore creazione anta cornice: {}'.format(str(e)))
            # Restituisci almeno il pannello base
            return None
    
    def create_glass_door(self, width: float, height: float, 
                         thickness: float,
                         params: Optional[Dict[str, Any]] = None) -> Optional[adsk.fusion.BRepBody]:
        """
        Crea anta con telaio e inserto vetro
        
        Args:
            width: Larghezza (cm)
            height: Altezza (cm)
            thickness: Spessore (cm)
            params: Parametri:
                - frame_width: Larghezza telaio (default 4 cm)
                - glass_thickness: Spessore vetro (default 0.4 cm)
                
        Returns:
            BRepBody dell'anta o None
        """
        try:
            if params is None:
                params = {}
            
            frame_width = params.get('frame_width', 4.0)
            glass_thickness = params.get('glass_thickness', 0.4)
            
            logger.info('Creazione anta vetro: telaio={}, vetro={}'.format(
                frame_width, glass_thickness))
            
            # 1. Crea telaio esterno (pannello pieno con foro centrale)
            sketch = self.component.sketches.add(self.component.xYConstructionPlane)
            
            # Rettangolo esterno
            outer_rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(0, 0, 0),
                adsk.core.Point3D.create(width, height, 0)
            )
            
            # Rettangolo interno (foro)
            inner_rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(frame_width, frame_width, 0),
                adsk.core.Point3D.create(width - frame_width, height - frame_width, 0)
            )
            
            # Estrusione telaio (profilo con foro)
            # Il profilo corretto è quello esterno meno quello interno
            profile = None
            for prof in sketch.profiles:
                # Cerca il profilo anello (quello tra i due rettangoli)
                if prof.profileLoops.count == 2:
                    profile = prof
                    break
            
            if not profile:
                logger.error('Profilo telaio non trovato')
                return None
            
            extrudes = self.component.features.extrudeFeatures
            extrude_input = extrudes.createInput(profile, 
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            distance = adsk.core.ValueInput.createByReal(thickness)
            extrude_input.setDistanceExtent(False, distance)
            
            extrude = extrudes.add(extrude_input)
            frame_body = extrude.bodies.item(0)
            frame_body.name = 'Anta_Vetro_Telaio'
            
            # 2. Crea inserto vetro
            sketch_glass = self.component.sketches.add(self.component.xYConstructionPlane)
            
            glass_rect = sketch_glass.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(frame_width, frame_width, 0),
                adsk.core.Point3D.create(width - frame_width, height - frame_width, 0)
            )
            
            # Estrusione vetro (centrata nello spessore)
            glass_profile = sketch_glass.profiles.item(0)
            glass_extrude_input = extrudes.createInput(glass_profile, 
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            
            # Offset iniziale per centrare il vetro
            glass_offset = (thickness - glass_thickness) / 2
            glass_extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
                adsk.core.ValueInput.createByReal(glass_offset)
            )
            
            glass_distance = adsk.core.ValueInput.createByReal(glass_thickness)
            glass_extrude_input.setDistanceExtent(False, glass_distance)
            
            glass_extrude = extrudes.add(glass_extrude_input)
            glass_body = glass_extrude.bodies.item(0)
            glass_body.name = 'Anta_Vetro_Inserto'
            
            logger.info('Anta vetro creata (telaio + inserto)')
            return frame_body  # Restituisce il telaio principale
            
        except Exception as e:
            logger.error('Errore creazione anta vetro: {}'.format(str(e)))
            return None
    
    def create_custom_profile_door(self, width: float, height: float, 
                                  thickness: float,
                                  params: Optional[Dict[str, Any]] = None) -> Optional[adsk.fusion.BRepBody]:
        """
        Crea anta con profilo custom (placeholder per implementazione futura)
        
        Args:
            width: Larghezza (cm)
            height: Altezza (cm)
            thickness: Spessore (cm)
            params: Parametri:
                - profile_sketch: Sketch del profilo (da implementare)
                
        Returns:
            BRepBody dell'anta o None
        """
        try:
            logger.info('Creazione anta profilo custom (non ancora implementato)')
            # Per ora ritorna anta piatta
            return self.create_flat_door(width, height, thickness)
            
        except Exception as e:
            logger.error('Errore creazione anta custom: {}'.format(str(e)))
            return None
    
    @staticmethod
    def get_door_types() -> Dict[str, str]:
        """
        Restituisce i tipi di ante disponibili
        
        Returns:
            Dizionario tipo->descrizione
        """
        return DoorDesigner.DOOR_TYPES.copy()
