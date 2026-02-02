"""
Generatore di mobili parametrici per Fusion 360
"""

import adsk.core
import adsk.fusion
import math
from typing import Dict, Any, List


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
    
    # Sistema 32mm - interassi multipli di 32mm
    if params.get('sistema_32mm'):
        altezza_interna = params.get('altezza', 0) - 2 * params.get('spessore_pannello', 0)
        num_ripiani = params.get('num_ripiani', 0)
        if num_ripiani > 0:
            interasse = altezza_interna / (num_ripiani + 1)
            if abs(interasse % 3.2 - 0) > 0.5 and abs(interasse % 3.2 - 3.2) > 0.5:
                errors.append('Con sistema 32mm, gli interassi devono essere multipli di 32mm. '
                            'Regolare altezza o numero ripiani.')
    
    return errors


def generate_furniture(design: adsk.fusion.Design, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera il mobile parametrico in Fusion 360
    
    Args:
        design: Design attivo di Fusion 360
        params: Parametri del mobile
        
    Returns:
        Dict con 'success', 'components', 'error'
    """
    try:
        root_comp = design.rootComponent
        
        # Crea nuovo componente per il mobile
        occurrence = root_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        furniture_comp = occurrence.component
        furniture_comp.name = 'Mobile_{}'.format(params.get('tipo_mobile', 'Base').replace(' ', '_'))
        
        components_created = []
        
        # Converti dimensioni da cm a cm (valori interni Fusion)
        larghezza = params['larghezza']
        altezza = params['altezza']
        profondita = params['profondita']
        spessore = params['spessore_pannello']
        spessore_schienale = params['spessore_schienale']
        
        # Crea fianchi laterali
        fianco_sx = create_panel(furniture_comp, 'Fianco_SX',
                                profondita, altezza, spessore,
                                0, 0, 0)
        components_created.append('Fianco_SX')
        
        fianco_dx = create_panel(furniture_comp, 'Fianco_DX',
                                profondita, altezza, spessore,
                                larghezza - spessore, 0, 0)
        components_created.append('Fianco_DX')
        
        # Crea top e base
        top = create_panel(furniture_comp, 'Top',
                          larghezza, profondita, spessore,
                          0, altezza - spessore, 0)
        components_created.append('Top')
        
        base = create_panel(furniture_comp, 'Base',
                           larghezza, profondita, spessore,
                           0, 0, 0)
        components_created.append('Base')
        
        # Crea ripiani interni
        num_ripiani = params.get('num_ripiani', 0)
        if num_ripiani > 0:
            altezza_interna = altezza - 2 * spessore
            interasse = altezza_interna / (num_ripiani + 1)
            
            for i in range(num_ripiani):
                y_pos = spessore + interasse * (i + 1)
                ripiano = create_panel(furniture_comp, 'Ripiano_{}'.format(i + 1),
                                      larghezza - 2 * spessore, profondita, spessore,
                                      spessore, y_pos, 0)
                components_created.append('Ripiano_{}'.format(i + 1))
                
                # Aggiungi fori sistema 32mm se richiesto
                if params.get('sistema_32mm') and params.get('fori_ripiani'):
                    add_shelf_holes(furniture_comp, fianco_sx, y_pos, spessore, profondita)
                    add_shelf_holes(furniture_comp, fianco_dx, y_pos, spessore, profondita)
        
        # Crea schienale
        schienale = create_panel(furniture_comp, 'Schienale',
                                larghezza - 2 * spessore, altezza - 2 * spessore, spessore_schienale,
                                spessore, spessore, profondita - spessore_schienale)
        components_created.append('Schienale')
        
        # Aggiungi fori per cerniere se richiesto
        num_cerniere = params.get('num_cerniere', 0)
        if num_cerniere > 0 and params.get('num_ante', 0) > 0:
            add_hinge_holes(furniture_comp, fianco_sx, num_cerniere, altezza)
            add_hinge_holes(furniture_comp, fianco_dx, num_cerniere, altezza)
        
        # Aggiungi spinatura se richiesta
        if params.get('spinatura'):
            add_dowel_holes(furniture_comp, [fianco_sx, fianco_dx], [top, base])
        
        # Crea zoccolo se richiesto
        if params.get('con_zoccolo'):
            altezza_zoccolo = params.get('altezza_zoccolo', 10.0)
            zoccolo = create_panel(furniture_comp, 'Zoccolo',
                                  larghezza - 2 * spessore, altezza_zoccolo, spessore,
                                  spessore, -altezza_zoccolo, 5.0)
            components_created.append('Zoccolo')
        
        return {
            'success': True,
            'components': components_created,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'components': [],
            'error': str(e)
        }


def create_panel(component: adsk.fusion.Component, name: str,
                width: float, height: float, thickness: float,
                x: float, y: float, z: float) -> adsk.fusion.BRepBody:
    """
    Crea un pannello rettangolare
    
    Args:
        component: Componente in cui creare il pannello
        name: Nome del pannello
        width: Larghezza in cm
        height: Altezza in cm
        thickness: Spessore in cm
        x, y, z: Posizione in cm
        
    Returns:
        BRepBody del pannello creato
    """
    sketches = component.sketches
    xy_plane = component.xYConstructionPlane
    sketch = sketches.add(xy_plane)
    
    # Disegna rettangolo
    lines = sketch.sketchCurves.sketchLines
    rect = lines.addTwoPointRectangle(
        adsk.core.Point3D.create(x, y, z),
        adsk.core.Point3D.create(x + width, y + height, z)
    )
    
    # Estrusione
    profile = sketch.profiles.item(0)
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(thickness)
    extrude_input.setDistanceExtent(False, distance)
    extrude_feature = extrudes.add(extrude_input)
    
    body = extrude_feature.bodies.item(0)
    body.name = name
    
    return body


def add_shelf_holes(component: adsk.fusion.Component, panel_body: adsk.fusion.BRepBody,
                   y_pos: float, spacing: float, depth: float):
    """Aggiunge fori sistema 32mm per reggi-ripiano"""
    # Implementazione semplificata - fori Ø5 distanziati 32mm
    holes = component.features.holeFeatures
    
    # Fori sui lati del pannello
    num_holes = int(depth / 3.2)  # Un foro ogni 32mm
    for i in range(num_holes):
        z_pos = 3.2 * (i + 1)
        # TODO: Aggiungere effettivamente i fori quando il pannello è accessibile
        pass


def add_hinge_holes(component: adsk.fusion.Component, panel_body: adsk.fusion.BRepBody,
                   num_cerniere: int, altezza: float):
    """Aggiunge fori per cerniere Ø35"""
    # Implementazione semplificata - distribuisce cerniere uniformemente
    if num_cerniere == 0:
        return
    
    interasse = altezza / (num_cerniere + 1)
    for i in range(num_cerniere):
        y_pos = interasse * (i + 1)
        # TODO: Aggiungere fori Ø35 alla profondità corretta
        pass


def add_dowel_holes(component: adsk.fusion.Component, 
                   side_panels: List[adsk.fusion.BRepBody],
                   horizontal_panels: List[adsk.fusion.BRepBody]):
    """Aggiunge fori per spinatura Ø8"""
    # Implementazione semplificata - spinatura standard
    # TODO: Aggiungere fori Ø8 per spinatura
    pass
