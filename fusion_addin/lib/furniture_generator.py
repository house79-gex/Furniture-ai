"""
Generatore di mobili parametrici per Fusion 360 - VERSIONE CORRETTA
"""

import adsk.core
import adsk.fusion
import math
from typing import Dict, Any, List
from . import logging_utils

logger = logging_utils.get_logger()


def validate_parameters(params: Dict[str, Any]) -> List[str]:
    """Valida i parametri del mobile"""
    errors = []
    
    # Dimensioni minime e massime
    if params.get('larghezza', 0) < 20.0 or params.get('larghezza', 0) > 300.0:
        errors.append('Larghezza deve essere tra 20 e 300 cm')
    
    if params.get('altezza', 0) < 20.0 or params.get('altezza', 0) > 300.0:
        errors.append('Altezza deve essere tra 20 e 300 cm')
    
    if params.get('profondita', 0) < 20.0 or params.get('profondita', 0) > 100.0:
        errors.append('Profondità deve essere tra 20 e 100 cm')
    
    # Spessori
    if params.get('spessore_pannello', 0) < 1.0 or params.get('spessore_pannello', 0) > 5.0:
        errors.append('Spessore pannello deve essere tra 1.0 e 5.0 cm')
    
    if params.get('spessore_schienale', 0) < 0.3 or params.get('spessore_schienale', 0) > 2.0:
        errors.append('Spessore schienale deve essere tra 0.3 e 2.0 cm')
    
    # Numero ripiani
    if params.get('num_ripiani', 0) < 0 or params.get('num_ripiani', 0) > 10:
        errors.append('Numero ripiani deve essere tra 0 e 10')
    
    return errors


def generate_furniture(design: adsk.fusion.Design, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera il mobile parametrico in Fusion 360
    """
    try:
        logger.info("Inizio generazione mobile...")
        root_comp = design.rootComponent
        
        # Crea nuovo componente per il mobile
        occurrence = root_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        furniture_comp = occurrence.component
        furniture_comp.name = 'Mobile_{}'.format(params.get('tipo_mobile', 'Base').replace(' ', '_'))
        
        components_created = []
        
        # Dimensioni in cm
        L = params['larghezza']
        H = params['altezza']
        P = params['profondita']
        S = params['spessore_pannello']
        Ss = params['spessore_schienale']
        
        logger.info(f"Dimensioni: L={L}, H={H}, P={P}, S={S}")
        
        # FIANCO SINISTRO (verticale, piano YZ, posizione x=0)
        logger.info("Creazione fianco SX...")
        fianco_sx = create_vertical_panel_YZ(furniture_comp, 'Fianco_SX', P, H, S, 0, 0, 0)
        if fianco_sx:
            components_created.append('Fianco_SX')
        
        # FIANCO DESTRO (verticale, piano YZ, posizione x=L-S)
        logger.info("Creazione fianco DX...")
        fianco_dx = create_vertical_panel_YZ(furniture_comp, 'Fianco_DX', P, H, S, L-S, 0, 0)
        if fianco_dx:
            components_created.append('Fianco_DX')
        
        # BASE (orizzontale, piano XY, posizione z=0)
        logger.info("Creazione base...")
        base = create_horizontal_panel_XY(furniture_comp, 'Base', L, P, S, 0, 0, 0)
        if base:
            components_created.append('Base')
        
        # TOP (orizzontale, piano XY, posizione z=H-S)
        logger.info("Creazione top...")
        top = create_horizontal_panel_XY(furniture_comp, 'Top', L, P, S, 0, 0, H-S)
        if top:
            components_created.append('Top')
        
        # RIPIANI INTERNI
        num_ripiani = params.get('num_ripiani', 0)
        if num_ripiani > 0:
            altezza_interna = H - 2*S
            interasse = altezza_interna / (num_ripiani + 1)
            
            for i in range(num_ripiani):
                z_pos = S + interasse * (i + 1)
                logger.info(f"Creazione ripiano {i+1} a z={z_pos}...")
                ripiano = create_horizontal_panel_XY(furniture_comp, f'Ripiano_{i+1}',
                                                    L-2*S, P, S, S, 0, z_pos)
                if ripiano:
                    components_created.append(f'Ripiano_{i+1}')
        
        # SCHIENALE (verticale, piano XZ, posizione y=P-Ss)
        logger.info("Creazione schienale...")
        schienale = create_vertical_panel_XZ(furniture_comp, 'Schienale', 
                                            L-2*S, H-2*S, Ss, S, P-Ss, S)
        if schienale:
            components_created.append('Schienale')
        
        # ZOCCOLO (opzionale)
        if params.get('con_zoccolo'):
            Hz = params.get('altezza_zoccolo', 10.0)
            logger.info("Creazione zoccolo...")
            zoccolo = create_horizontal_panel_XY(furniture_comp, 'Zoccolo',
                                                L-2*S, Hz, S, S, 5, -Hz)
            if zoccolo:
                components_created.append('Zoccolo')
        
        logger.info(f"Mobile creato: {len(components_created)} componenti")
        
        return {
            'success': True,
            'components': components_created,
            'error': None
        }
        
    except Exception as e:
        logger.error(f"Errore generazione mobile: {str(e)}")
        return {
            'success': False,
            'components': [],
            'error': str(e)
        }


def create_horizontal_panel_XY(component: adsk.fusion.Component, name: str,
                               width: float, depth: float, thickness: float,
                               x: float, y: float, z: float) -> adsk.fusion.BRepBody:
    """
    Crea pannello orizzontale (piano XY)
    """
    try:
        sketches = component.sketches
        xy_plane = component.xYConstructionPlane
        
        # Crea sketch
        sketch = sketches.add(xy_plane)
        
        # Rettangolo nel piano XY
        rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(x, y, 0),
            adsk.core.Point3D.create(x + width, y + depth, 0)
        )
        
        # Estrusione verso l'alto (direzione Z)
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Distanza estrusione
        distance = adsk.core.ValueInput.createByReal(thickness)
        extrude_input.setDistanceExtent(False, distance)
        
        # Offset iniziale Z
        if z != 0:
            extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
                adsk.core.ValueInput.createByReal(z)
            )
        
        extrude = extrudes.add(extrude_input)
        body = extrude.bodies.item(0)
        body.name = name
        
        return body
        
    except Exception as e:
        logger.error(f"Errore creazione pannello {name}: {str(e)}")
        return None


def create_vertical_panel_YZ(component: adsk.fusion.Component, name: str,
                             depth: float, height: float, thickness: float,
                             x: float, y: float, z: float) -> adsk.fusion.BRepBody:
    """
    Crea pannello verticale frontale (piano YZ)
    """
    try:
        sketches = component.sketches
        yz_plane = component.yZConstructionPlane
        
        # Crea sketch sul piano YZ
        sketch = sketches.add(yz_plane)
        
        # Rettangolo nel piano YZ
        rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, y, z),
            adsk.core.Point3D.create(0, y + depth, z + height)
        )
        
        # Estrusione lungo X
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Distanza estrusione
        distance = adsk.core.ValueInput.createByReal(thickness)
        extrude_input.setDistanceExtent(False, distance)
        
        # Offset iniziale X
        if x != 0:
            extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
                adsk.core.ValueInput.createByReal(x)
            )
        
        extrude = extrudes.add(extrude_input)
        body = extrude.bodies.item(0)
        body.name = name
        
        return body
        
    except Exception as e:
        logger.error(f"Errore creazione pannello {name}: {str(e)}")
        return None


def create_vertical_panel_XZ(component: adsk.fusion.Component, name: str,
                             width: float, height: float, thickness: float,
                             x: float, y: float, z: float) -> adsk.fusion.BRepBody:
    """
    Crea pannello verticale laterale (piano XZ)
    """
    try:
        sketches = component.sketches
        xz_plane = component.xZConstructionPlane
        
        # Crea sketch sul piano XZ
        sketch = sketches.add(xz_plane)
        
        # Rettangolo nel piano XZ
        rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(x, 0, z),
            adsk.core.Point3D.create(x + width, 0, z + height)
        )
        
        # Estrusione lungo Y
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Distanza estrusione
        distance = adsk.core.ValueInput.createByReal(thickness)
        extrude_input.setDistanceExtent(False, distance)
        
        # Offset iniziale Y
        if y != 0:
            extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
                adsk.core.ValueInput.createByReal(y)
            )
        
        extrude = extrudes.add(extrude_input)
        body = extrude.bodies.item(0)
        body.name = name
        
        return body
        
    except Exception as e:
        logger.error(f"Errore creazione pannello {name}: {str(e)}")
        return None
