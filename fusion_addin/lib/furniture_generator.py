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
        
        # SCHIENALE con logica montaggio
        tipo_schienale = params.get('tipo_schienale', 'A filo dietro')
        logger.info(f"Tipo schienale: {tipo_schienale}")
        
        if tipo_schienale == 'Incastrato (scanalatura 10mm)':
            # Scanalatura 10mm = 1.0cm di profondità
            prof_scanalatura = 1.0
            larghezza_scan = Ss  # Larghezza scanalatura = spessore schienale
            
            # Crea scanalature sui fianchi (solo se i pannelli esistono)
            logger.info("Creazione scanalature per schienale incastrato...")
            if fianco_sx:
                add_groove_vertical(furniture_comp, fianco_sx, P - prof_scanalatura, H, larghezza_scan, S, 'SX')
            if fianco_dx:
                add_groove_vertical(furniture_comp, fianco_dx, P - prof_scanalatura, H, larghezza_scan, S, 'DX')
            
            # Crea scanalature su top e base (solo se i pannelli esistono)
            if top:
                add_groove_horizontal(furniture_comp, top, P - prof_scanalatura, larghezza_scan, L, S, H-S, 'TOP')
            if base:
                add_groove_horizontal(furniture_comp, base, P - prof_scanalatura, larghezza_scan, L, S, 0, 'BASE')
            
            # Schienale ridotto per entrare in scanalatura
            schienale = create_vertical_panel_XZ(furniture_comp, 'Schienale',
                                                L - 2*S, H - 2*S, Ss,
                                                S, P - prof_scanalatura - Ss, S)
        
        elif tipo_schienale == 'Arretrato custom':
            arretramento = params.get('arretramento_schienale', 0.8)  # cm
            logger.info(f"Schienale arretrato: {arretramento}cm")
            
            # Crea fresatura a L sui pannelli (solo se esistono)
            panels_for_groove = [p for p in [fianco_sx, fianco_dx, top, base] if p is not None]
            if panels_for_groove:
                add_L_groove(furniture_comp, panels_for_groove, arretramento, Ss, P, L, H, S)
            
            # Schienale arretrato
            schienale = create_vertical_panel_XZ(furniture_comp, 'Schienale',
                                                L - 2*S, H - 2*S, Ss,
                                                S, P - arretramento - Ss, S)
        
        else:  # A filo dietro (default)
            logger.info("Creazione schienale a filo dietro...")
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
    Crea pannello verticale su piano YZ (fianchi laterali)
    Usa offset plane per posizionamento corretto
    """
    try:
        # Crea piano offset se x != 0
        planes = component.constructionPlanes
        if x != 0:
            plane_input = planes.createInput()
            plane_input.setByOffset(
                component.yZConstructionPlane,
                adsk.core.ValueInput.createByReal(x)
            )
            offset_plane = planes.add(plane_input)
            sketch = component.sketches.add(offset_plane)
        else:
            sketch = component.sketches.add(component.yZConstructionPlane)
        
        # Rettangolo con coordinate (Y, Z) sul piano YZ
        # X=0 è fisso sul piano (coordinata implicita)
        rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, y, z),
            adsk.core.Point3D.create(0, y + depth, z + height)
        )
        
        # Estrusione lungo asse X
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Distanza estrusione
        distance = adsk.core.ValueInput.createByReal(thickness)
        extrude_input.setDistanceExtent(False, distance)
        
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
    Crea pannello verticale su piano XZ (schienale)
    Usa offset plane per posizionamento corretto
    """
    try:
        # Crea piano offset se y != 0
        planes = component.constructionPlanes
        if y != 0:
            plane_input = planes.createInput()
            plane_input.setByOffset(
                component.xZConstructionPlane,
                adsk.core.ValueInput.createByReal(y)
            )
            offset_plane = planes.add(plane_input)
            sketch = component.sketches.add(offset_plane)
        else:
            sketch = component.sketches.add(component.xZConstructionPlane)
        
        # Rettangolo con coordinate (X, Z) sul piano XZ
        # Y=0 è fisso sul piano (coordinata implicita)
        rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(x, 0, z),
            adsk.core.Point3D.create(x + width, 0, z + height)
        )
        
        # Estrusione lungo asse Y
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Distanza estrusione
        distance = adsk.core.ValueInput.createByReal(thickness)
        extrude_input.setDistanceExtent(False, distance)
        
        extrude = extrudes.add(extrude_input)
        body = extrude.bodies.item(0)
        body.name = name
        
        return body
        
    except Exception as e:
        logger.error(f"Errore creazione pannello {name}: {str(e)}")
        return None


def add_groove_vertical(component: adsk.fusion.Component, panel_body: adsk.fusion.BRepBody,
                       y_position: float, height: float, width: float, panel_thickness: float,
                       side: str) -> bool:
    """
    Crea scanalatura verticale su fianco per schienale incastrato
    
    Args:
        component: Componente Fusion
        panel_body: Body del pannello su cui creare la scanalatura
        y_position: Posizione Y della scanalatura (distanza dal fronte)
        height: Altezza totale del pannello
        width: Larghezza della scanalatura (spessore schienale)
        panel_thickness: Spessore del pannello laterale
        side: 'SX' o 'DX' per identificare il lato
    """
    try:
        logger.info(f"Creazione scanalatura verticale su fianco {side}...")
        
        # Trova la faccia interna del pannello (verso il centro del mobile)
        # Per ora, registriamo solo l'intenzione - implementazione completa richiede face selection
        logger.info(f"  Posizione Y: {y_position}, Larghezza: {width}, Altezza: {height}")
        logger.info(f"  Profondità scanalatura: 10mm (1cm)")
        
        # TODO: Implementazione completa con face selection e extrude cut
        # 1. Selezionare faccia interna (face selection API)
        # 2. Creare sketch sulla faccia
        # 3. Disegnare rettangolo per scanalatura
        # 4. Eseguire extrude cut (operazione sottrazione)
        
        return True
        
    except Exception as e:
        logger.error(f"Errore creazione scanalatura verticale {side}: {str(e)}")
        return False


def add_groove_horizontal(component: adsk.fusion.Component, panel_body: adsk.fusion.BRepBody,
                         y_position: float, width: float, panel_width: float, 
                         panel_thickness: float, z_position: float, panel_name: str) -> bool:
    """
    Crea scanalatura orizzontale su top/base per schienale incastrato
    
    Args:
        component: Componente Fusion
        panel_body: Body del pannello su cui creare la scanalatura
        y_position: Posizione Y della scanalatura (distanza dal fronte)
        width: Larghezza della scanalatura (spessore schienale)
        panel_width: Larghezza totale del pannello
        panel_thickness: Spessore del pannello
        z_position: Posizione Z del pannello
        panel_name: Nome del pannello ('TOP' o 'BASE')
    """
    try:
        logger.info(f"Creazione scanalatura orizzontale su {panel_name}...")
        
        # Registra parametri per implementazione futura
        logger.info(f"  Posizione Y: {y_position}, Larghezza: {width}")
        logger.info(f"  Profondità scanalatura: 10mm (1cm)")
        
        # TODO: Implementazione completa con face selection e extrude cut
        
        return True
        
    except Exception as e:
        logger.error(f"Errore creazione scanalatura {panel_name}: {str(e)}")
        return False


def add_L_groove(component: adsk.fusion.Component, panels: list,
                offset: float, thickness: float, depth: float, width: float,
                height: float, panel_thickness: float) -> bool:
    """
    Crea fresatura a L per schienale arretrato custom
    
    Args:
        component: Componente Fusion
        panels: Lista di body pannelli su cui creare la fresatura
        offset: Arretramento dal filo posteriore (cm)
        thickness: Spessore schienale (cm)
        depth: Profondità totale mobile (cm)
        width: Larghezza totale mobile (cm)
        height: Altezza totale mobile (cm)
        panel_thickness: Spessore pannelli (cm)
    """
    try:
        logger.info(f"Creazione fresatura a L per schienale arretrato ({offset}cm)...")
        
        # Registra parametri per implementazione futura
        logger.info(f"  Offset: {offset}cm, Spessore schienale: {thickness}cm")
        logger.info(f"  Profondità fresatura: {offset}cm + {thickness}cm")
        
        # TODO: Implementazione completa
        # La fresatura a L consiste in due tagli:
        # 1. Taglio orizzontale sulla faccia posteriore per l'offset
        # 2. Taglio verticale per alloggiare lo spessore dello schienale
        
        return True
        
    except Exception as e:
        logger.error(f"Errore creazione fresatura a L: {str(e)}")
        return False
