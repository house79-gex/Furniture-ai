"""
Script di esempio per generazione codice Xilog Plus
"""

import sys
import os

# Aggiungi path per import moduli
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from postprocessor.xilog_generator import XilogGenerator
from tlg_parser.tlg_library import TLGLibrary


def generate_base_cabinet_example():
    """Genera esempio mobile base"""
    
    # Inizializza libreria utensili
    tlg = TLGLibrary()
    
    # Crea generatore
    gen = XilogGenerator(tlg)
    
    # Dimensioni pezzo (L, W, T in mm)
    dimensions = (800, 600, 18)
    
    # Header
    gen.add_header('Mobile_Base_80x90x60', dimensions)
    
    # Fori spinatura Ø8 agli angoli
    dowel_positions = [
        (50, 50), (750, 50), (50, 550), (750, 550)
    ]
    gen.add_dowel_holes(dowel_positions, diameter=8.0, depth=40.0)
    
    # Fori cerniere Ø35
    hinge_positions = [
        (50, 150), (50, 450)
    ]
    gen.add_hinge_holes(hinge_positions)
    
    # Fori sistema 32mm (Ø5 per reggi-ripiano)
    shelf_holes = []
    for y in range(100, 550, 32):  # Ogni 32mm
        shelf_holes.append({'x': 32, 'y': y, 'diameter': 5.0, 'depth': 12.0})
    
    gen.add_drilling(shelf_holes, face=1, optimized=True)
    
    # Fresatura contorno
    contour = [
        (10, 10), (790, 10), (790, 590), (10, 590), (10, 10)
    ]
    gen.add_routing(contour, depth=5.0, tool_diameter=8.0)
    
    # Note sicurezza e footer
    gen.add_safety_notes()
    gen.add_footer()
    
    # Salva file
    output_path = os.path.join(os.path.dirname(__file__), 
                               'xilog_output', 'mobile_base_esempio.xilog')
    gen.save_to_file(output_path)
    
    print(f'File generato: {output_path}')
    print('\nCodice generato:')
    print('=' * 60)
    print(gen.generate())


def generate_door_example():
    """Genera esempio anta"""
    
    tlg = TLGLibrary()
    gen = XilogGenerator(tlg)
    
    dimensions = (400, 800, 18)
    
    gen.add_header('Anta_40x80', dimensions)
    
    # Fori cerniere
    hinge_positions = [(22, 100), (22, 700)]
    gen.add_hinge_holes(hinge_positions)
    
    # Contorno con raggi
    contour = [
        (5, 5), (395, 5), (395, 795), (5, 795), (5, 5)
    ]
    gen.add_routing(contour, depth=3.0, tool_diameter=8.0)
    
    gen.add_safety_notes()
    gen.add_footer()
    
    output_path = os.path.join(os.path.dirname(__file__),
                               'xilog_output', 'anta_esempio.xilog')
    gen.save_to_file(output_path)
    
    print(f'File generato: {output_path}')


if __name__ == '__main__':
    print('Generazione esempi codice Xilog Plus\n')
    generate_base_cabinet_example()
    print('\n' + '=' * 60 + '\n')
    generate_door_example()
