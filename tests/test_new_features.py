#!/usr/bin/env python3
"""
Test per nuove funzionalita AI integration
"""

import sys
import os
import importlib.util

# Aggiungi path per importare moduli
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lib_path = os.path.join(repo_root, 'fusion_addin', 'lib')


def import_module_from_path(module_name, file_path):
    """Importa modulo direttamente da file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_furniture_description():
    """Test parse_furniture_description method"""
    print("\nTesting parse_furniture_description...")
    
    try:
        ai_client_module = import_module_from_path(
            'ai_client',
            os.path.join(lib_path, 'ai_client.py')
        )
        
        # Crea client con fallback
        client = ai_client_module.AIClient(enable_fallback=True)
        
        # Test 1: Mobile cucina completo
        desc1 = "mobile base cucina largo 80cm alto 90cm profondo 60cm con 2 ripiani e 2 ante"
        result1 = client.parse_furniture_description(desc1)
        print("Test 1 - Mobile cucina completo:")
        print("  Input:", desc1)
        print("  Output:", result1)
        assert result1.get('larghezza') == 80.0
        assert result1.get('altezza') == 90.0
        assert result1.get('profondita') == 60.0
        assert result1.get('num_ripiani') == 2
        assert result1.get('num_ante') == 2
        print("  ✓ PASS")
        
        # Test 2: Pensile con schienale incastrato
        desc2 = "pensile L 120 H 70 con 1 ripiano e schienale incastrato"
        result2 = client.parse_furniture_description(desc2)
        print("\nTest 2 - Pensile con schienale incastrato:")
        print("  Input:", desc2)
        print("  Output:", result2)
        assert result2.get('larghezza') == 120.0
        assert result2.get('altezza') == 70.0
        assert result2.get('num_ripiani') == 1
        assert result2.get('tipo_schienale') == 'Incastrato (scanalatura 10mm)'
        print("  ✓ PASS")
        
        # Test 3: Mobile cucina con default
        desc3 = "mobile cucina largo 90cm con 3 ripiani"
        result3 = client.parse_furniture_description(desc3)
        print("\nTest 3 - Mobile cucina con default:")
        print("  Input:", desc3)
        print("  Output:", result3)
        assert result3.get('larghezza') == 90.0
        assert result3.get('altezza') == 90.0  # Default cucina
        assert result3.get('profondita') == 60.0  # Default cucina
        assert result3.get('num_ripiani') == 3
        print("  ✓ PASS")
        
        # Test 4: Pensile con default
        desc4 = "pensile largo 60cm"
        result4 = client.parse_furniture_description(desc4)
        print("\nTest 4 - Pensile con default:")
        print("  Input:", desc4)
        print("  Output:", result4)
        assert result4.get('larghezza') == 60.0
        assert result4.get('altezza') == 70.0  # Default pensile
        assert result4.get('profondita') == 35.0  # Default pensile
        print("  ✓ PASS")
        
        # Test 5: Con cassetti
        desc5 = "mobile L100cm H90cm P60cm con 3 cassetti"
        result5 = client.parse_furniture_description(desc5)
        print("\nTest 5 - Mobile con cassetti:")
        print("  Input:", desc5)
        print("  Output:", result5)
        assert result5.get('larghezza') == 100.0
        assert result5.get('altezza') == 90.0
        assert result5.get('profondita') == 60.0
        assert result5.get('num_cassetti') == 3
        print("  ✓ PASS")
        
        print("\n✓ All parse_furniture_description tests passed!")
        return True
        
    except Exception as e:
        print("✗ Test failed:", e)
        import traceback
        traceback.print_exc()
        return False


def test_cutlist_generator():
    """Test CutListGenerator"""
    print("\nTesting CutListGenerator...")
    
    try:
        cutlist_module = import_module_from_path(
            'cutlist_generator',
            os.path.join(lib_path, 'cutlist_generator.py')
        )
        
        # Crea generatore
        generator = cutlist_module.CutListGenerator()
        print("✓ CutListGenerator instantiated")
        
        # Verifica metodi esistano
        assert hasattr(generator, 'analyze_bodies')
        assert hasattr(generator, 'export_excel')
        assert hasattr(generator, 'export_csv')
        print("✓ All required methods present")
        
        # Test export CSV (senza bodies reali)
        test_cutlist = [
            {
                'nome': 'Fianco_SX',
                'lunghezza': 90.0,
                'larghezza': 60.0,
                'spessore': 1.8,
                'materiale': 'Legno',
                'quantita': 1,
                'area_m2': 0.54
            },
            {
                'nome': 'Base',
                'lunghezza': 80.0,
                'larghezza': 60.0,
                'spessore': 1.8,
                'materiale': 'Legno',
                'quantita': 1,
                'area_m2': 0.48
            }
        ]
        
        test_csv_path = '/tmp/test_cutlist.csv'
        generator.export_csv(test_cutlist, test_csv_path)
        
        # Verifica file creato
        assert os.path.exists(test_csv_path)
        print("✓ CSV export works")
        
        # Verifica contenuto
        with open(test_csv_path, 'r') as f:
            content = f.read()
            assert 'Fianco_SX' in content
            assert 'Base' in content
            assert '90.0' in content
        print("✓ CSV content correct")
        
        # Cleanup
        os.remove(test_csv_path)
        
        print("\n✓ CutListGenerator tests passed!")
        return True
        
    except Exception as e:
        print("✗ Test failed:", e)
        import traceback
        traceback.print_exc()
        return False


def main():
    """Esegue tutti i test"""
    print("=" * 60)
    print("FurnitureAI - New Features Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("parse_furniture_description", test_parse_furniture_description()))
    results.append(("CutListGenerator", test_cutlist_generator()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print("{} {}: {}".format(symbol, name, status))
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
