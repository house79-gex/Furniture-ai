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
        
        # USA ROOT COMPONENT DIRETTAMENTE (funziona sia Part che Assembly)
        furniture_comp = design.rootComponent
        
        components_created = []
        
        # Dimensioni in cm
        L = params['larghezza']
        H = params['altezza']
        P = params['profondita']
        S = params['spessore_pannello']
        Ss = params['spessore_schienale']
        
        logger.info('Dimensioni: L={}, H={}, P={}, S={}'.format(L, H, P, S))
        
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
                logger.info('Creazione ripiano {} a z={}...'.format(i+1, z_pos))
                ripiano = create_horizontal_panel_XY(furniture_comp, 'Ripiano_{}'.format(i+1),
                                                    L-2*S, P, S, S, 0, z_pos)
                if ripiano:
                    components_created.append('Ripiano_{}'.format(i+1))
        
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
        
        logger.info('Mobile creato: {} componenti'.format(len(components_created)))
        
        return {
            'success': True,
            'components': components_created,
            'error': None
        }
        
    except Exception as e:
        logger.error('Errore generazione mobile: {}'.format(str(e)))
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
        logger.error('Errore creazione pannello {}: {}'.format(name, str(e)))
        return None


def create_vertical_panel_YZ(component: adsk.fusion.Component, name: str,
                             depth: float, height: float, thickness: float,
                             x_pos: float, y_offset: float, z_offset: float) -> adsk.fusion.BRepBody:
    """
    Crea pannello verticale frontale (piano YZ) - GEOMETRIA CORRETTA
    
    Args:
        component: Componente Fusion 360
        name: Nome del pannello
        depth: Profondità (dimensione Y locale)
        height: Altezza (dimensione Z locale)
        thickness: Spessore (estrusione lungo X)
        x_pos: Posizione globale X del piano
        y_offset: Offset Y per traslazione finale
        z_offset: Offset Z per traslazione finale
    """
    try:
        planes = component.constructionPlanes
        
        # 1. Crea piano YZ offset alla posizione X globale
        plane_input = planes.createInput()
        plane_input.setByOffset(
            component.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(x_pos)
        )
        yz_plane = planes.add(plane_input)
        
        # 2. Sketch con coordinate LOCALI - sempre da (0,0) a (depth, height)
        sketch = component.sketches.add(yz_plane)
        rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(0, depth, height)
        )
        
        # 3. Estrusione lungo X
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, 
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(thickness)
        extrude_input.setDistanceExtent(False, distance)
        
        extrude = extrudes.add(extrude_input)
        body = extrude.bodies.item(0)
        body.name = name
        
        # 4. Traslazione per offset Y,Z se necessario
        if y_offset != 0 or z_offset != 0:
            move_feats = component.features.moveFeatures
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, y_offset, z_offset)
            bodies = adsk.core.ObjectCollection.create()
            bodies.add(body)
            move_input = move_feats.createInput(bodies, transform)
            move_feats.add(move_input)
        
        return body
        
    except Exception as e:
        logger.error('Errore creazione pannello {}: {}'.format(name, str(e)))
        return None


def create_vertical_panel_XZ(component: adsk.fusion.Component, name: str,
                             width: float, height: float, thickness: float,
                             x_offset: float, y_pos: float, z_offset: float) -> adsk.fusion.BRepBody:
    """
    Crea pannello verticale laterale (piano XZ) - GEOMETRIA CORRETTA
    
    Args:
        component: Componente Fusion 360
        name: Nome del pannello
        width: Larghezza (dimensione X locale)
        height: Altezza (dimensione Z locale)
        thickness: Spessore (estrusione lungo Y)
        x_offset: Offset X per traslazione finale
        y_pos: Posizione globale Y del piano
        z_offset: Offset Z per traslazione finale
    """
    try:
        planes = component.constructionPlanes
        
        # 1. Crea piano XZ offset alla posizione Y globale
        plane_input = planes.createInput()
        plane_input.setByOffset(
            component.xZConstructionPlane,
            adsk.core.ValueInput.createByReal(y_pos)
        )
        xz_plane = planes.add(plane_input)
        
        # 2. Sketch con coordinate LOCALI - sempre da (0,0) a (width, height)
        sketch = component.sketches.add(xz_plane)
        rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(width, 0, height)
        )
        
        # 3. Estrusione lungo Y
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, 
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(thickness)
        extrude_input.setDistanceExtent(False, distance)
        
        extrude = extrudes.add(extrude_input)
        body = extrude.bodies.item(0)
        body.name = name
        
        # 4. Traslazione per offset X,Z se necessario
        if x_offset != 0 or z_offset != 0:
            move_feats = component.features.moveFeatures
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(x_offset, 0, z_offset)
            bodies = adsk.core.ObjectCollection.create()
            bodies.add(body)
            move_input = move_feats.createInput(bodies, transform)
            move_feats.add(move_input)
        
        return body
        
    except Exception as e:
        logger.error('Errore creazione pannello {}: {}'.format(name, str(e)))
        return None


def generate_furniture_in_component(component: adsk.fusion.Component, 
                                    params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera il mobile in un componente specifico (per sistema modulare)
    
    Args:
        component: Componente in cui creare il mobile
        params: Parametri del mobile
        
    Returns:
        Dizionario con risultati (success, components, error)
    """
    try:
        logger.info("Generazione mobile in componente {}...".format(component.name))
        
        components_created = []
        
        # Dimensioni in cm
        L = params['larghezza']
        H = params['altezza']
        P = params['profondita']
        S = params['spessore_pannello']
        Ss = params['spessore_schienale']
        
        logger.info('Dimensioni: L={}, H={}, P={}, S={}'.format(L, H, P, S))
        
        # FIANCO SINISTRO (verticale, piano YZ, posizione x=0)
        logger.info("Creazione fianco SX...")
        fianco_sx = create_vertical_panel_YZ(component, 'Fianco_SX', P, H, S, 0, 0, 0)
        if fianco_sx:
            components_created.append('Fianco_SX')
        
        # FIANCO DESTRO (verticale, piano YZ, posizione x=L-S)
        logger.info("Creazione fianco DX...")
        fianco_dx = create_vertical_panel_YZ(component, 'Fianco_DX', P, H, S, L-S, 0, 0)
        if fianco_dx:
            components_created.append('Fianco_DX')
        
        # BASE (orizzontale, piano XY, posizione z=0)
        logger.info("Creazione base...")
        base = create_horizontal_panel_XY(component, 'Base', L, P, S, 0, 0, 0)
        if base:
            components_created.append('Base')
        
        # TOP (orizzontale, piano XY, posizione z=H-S)
        logger.info("Creazione top...")
        top = create_horizontal_panel_XY(component, 'Top', L, P, S, 0, 0, H-S)
        if top:
            components_created.append('Top')
        
        # RIPIANI INTERNI
        num_ripiani = params.get('num_ripiani', 0)
        if num_ripiani > 0:
            altezza_interna = H - 2*S
            interasse = altezza_interna / (num_ripiani + 1)
            
            for i in range(num_ripiani):
                z_pos = S + interasse * (i + 1)
                logger.info('Creazione ripiano {} a z={}...'.format(i+1, z_pos))
                ripiano = create_horizontal_panel_XY(component, 'Ripiano_{}'.format(i+1),
                                                    L-2*S, P, S, S, 0, z_pos)
                if ripiano:
                    components_created.append('Ripiano_{}'.format(i+1))
        
        # SCHIENALE (verticale, piano XZ, posizione y=P-Ss)
        logger.info("Creazione schienale...")
        schienale = create_vertical_panel_XZ(component, 'Schienale', 
                                            L-2*S, H-2*S, Ss, S, P-Ss, S)
        if schienale:
            components_created.append('Schienale')
        
        # ZOCCOLO (opzionale)
        if params.get('con_zoccolo'):
            Hz = params.get('altezza_zoccolo', 10.0)
            logger.info("Creazione zoccolo...")
            zoccolo = create_horizontal_panel_XY(component, 'Zoccolo',
                                                L-2*S, Hz, S, S, 5, -Hz)
            if zoccolo:
                components_created.append('Zoccolo')
        
        logger.info('Mobile creato in componente: {} elementi'.format(len(components_created)))
        
        return {
            'success': True,
            'components': components_created,
            'error': None
        }
        
    except Exception as e:
        logger.error('Errore generazione mobile in componente: {}'.format(str(e)))
        return {
            'success': False,
            'components': [],
            'error': str(e)
        }
