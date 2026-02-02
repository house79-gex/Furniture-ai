"""
Test per XilogGenerator
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from postprocessor.xilog_generator import XilogGenerator
from tlg_parser.tlg_library import TLGLibrary


class TestXilogGenerator(unittest.TestCase):
    """Test per generatore codice Xilog"""
    
    def setUp(self):
        """Setup test"""
        self.tlg = TLGLibrary()
        self.gen = XilogGenerator(self.tlg)
    
    def test_header_generation(self):
        """Test generazione header"""
        self.gen.add_header('Test_Part', (800, 600, 18))
        code = self.gen.generate()
        
        self.assertIn('PROGRAMMA: Test_Part', code)
        self.assertIn('L=800.0 W=600.0 T=18.0', code)
        self.assertIn('G90', code)
        self.assertIn('G71', code)
    
    def test_drilling_generation(self):
        """Test generazione foratura"""
        holes = [
            {'x': 50, 'y': 50, 'diameter': 8.0, 'depth': 40.0},
            {'x': 100, 'y': 100, 'diameter': 8.0, 'depth': 40.0},
        ]
        
        self.gen.add_drilling(holes, face=1, optimized=True)
        code = self.gen.generate()
        
        self.assertIn('XBO', code)
        self.assertIn('X=50.00 Y=50.00', code)
        self.assertIn('P=40.00', code)
        self.assertIn('XBOE', code)
    
    def test_face_change(self):
        """Test cambio faccia"""
        self.gen.add_face_change(2)
        code = self.gen.generate()
        
        self.assertIn('F=2', code)
    
    def test_routing_generation(self):
        """Test generazione fresatura"""
        path = [(10, 10), (100, 10), (100, 100), (10, 100), (10, 10)]
        
        self.gen.add_routing(path, depth=5.0, tool_diameter=8.0)
        code = self.gen.generate()
        
        self.assertIn('XGIN', code)
        self.assertIn('XG0', code)
        self.assertIn('XL2P', code)
        self.assertIn('XGOUT', code)
    
    def test_dowel_holes(self):
        """Test fori spinatura"""
        positions = [(50, 50), (750, 50)]
        
        self.gen.add_dowel_holes(positions)
        code = self.gen.generate()
        
        self.assertIn('Ø8', code)  # Default diameter
    
    def test_hinge_holes(self):
        """Test fori cerniere"""
        positions = [(50, 150), (50, 450)]
        
        self.gen.add_hinge_holes(positions)
        code = self.gen.generate()
        
        self.assertIn('Ø35', code)  # Hinge diameter
    
    def test_safety_notes(self):
        """Test note sicurezza"""
        self.gen.add_safety_notes()
        code = self.gen.generate()
        
        self.assertIn('NOTE SICUREZZA', code)
        self.assertIn('Verificare fissaggio', code)
    
    def test_footer(self):
        """Test footer"""
        self.gen.add_footer()
        code = self.gen.generate()
        
        self.assertIn('M30', code)


class TestTLGLibrary(unittest.TestCase):
    """Test per libreria TLG"""
    
    def setUp(self):
        """Setup test"""
        self.tlg = TLGLibrary()
    
    def test_default_library_loaded(self):
        """Test caricamento libreria default"""
        self.assertGreater(len(self.tlg.tools), 0)
    
    def test_select_drill_tool(self):
        """Test selezione punta"""
        # Cerca punta Ø8 verticale
        tool = self.tlg.select_drill_tool(8.0, face=1, depth=40.0)
        
        self.assertIsNotNone(tool)
        self.assertEqual(tool['type'], 'drill')
        self.assertAlmostEqual(tool['diameter'], 8.0, places=1)
        self.assertEqual(tool['orientation'], 'vertical')
    
    def test_select_hinge_drill(self):
        """Test selezione punta cerniere"""
        tool = self.tlg.select_drill_tool(35.0, face=1, depth=13.0)
        
        self.assertIsNotNone(tool)
        self.assertAlmostEqual(tool['diameter'], 35.0, places=1)
    
    def test_select_horizontal_drill(self):
        """Test selezione punta orizzontale"""
        tool = self.tlg.select_drill_tool(8.0, face=2, depth=50.0)
        
        self.assertIsNotNone(tool)
        self.assertEqual(tool['orientation'], 'horizontal_x')
    
    def test_select_routing_tool(self):
        """Test selezione fresa"""
        tool = self.tlg.select_routing_tool(8.0, face=1)
        
        self.assertIsNotNone(tool)
        self.assertEqual(tool['type'], 'router')
    
    def test_get_tool_by_number(self):
        """Test recupero utensile per numero"""
        tool = self.tlg.get_tool_by_number(3)
        
        self.assertIsNotNone(tool)
        self.assertEqual(tool['number'], 3)
    
    def test_list_tools_by_type(self):
        """Test lista utensili per tipo"""
        drills = self.tlg.list_tools_by_type('drill')
        routers = self.tlg.list_tools_by_type('router')
        
        self.assertGreater(len(drills), 0)
        self.assertGreater(len(routers), 0)


if __name__ == '__main__':
    unittest.main()
