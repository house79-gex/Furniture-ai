#!/usr/bin/env python3
"""
Script di verifica per FurnitureAI Add-in
Testa che tutti i moduli possano essere importati e che le funzioni base siano definite
Nota: Non testa la funzionalità Fusion 360 (richiede l'ambiente Fusion)
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


def test_imports():
    """Testa che tutti i moduli possano essere importati"""
    print("Testing imports...")
    
    try:
        # Test config_manager (non dipende da adsk)
        config_manager = import_module_from_path(
            'config_manager',
            os.path.join(lib_path, 'config_manager.py')
        )
        print("✓ config_manager imported")
        
        # Test logging_utils (ha dipendenze adsk opzionali)
        logging_utils = import_module_from_path(
            'logging_utils',
            os.path.join(lib_path, 'logging_utils.py')
        )
        print("✓ logging_utils imported")
        
        # Verifica funzioni logging_utils
        assert hasattr(logging_utils, 'FusionLogger')
        assert hasattr(logging_utils, 'get_logger')
        print("✓ logging_utils functions present")
        
        # Test config functions
        assert hasattr(config_manager, 'load_config')
        assert hasattr(config_manager, 'save_config')
        assert hasattr(config_manager, 'get_config_path')
        print("✓ config_manager functions present")
        
        print("\nAll imports successful!")
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_client():
    """Testa AI client senza dipendenze Fusion"""
    print("\nTesting AI client...")
    
    try:
        ai_client = import_module_from_path(
            'ai_client',
            os.path.join(lib_path, 'ai_client.py')
        )
        print("✓ ai_client imported")
        
        # Crea client senza requests (deve funzionare con fallback)
        client = ai_client.AIClient(enable_fallback=True)
        print("✓ AIClient instantiated")
        
        # Test fallback parsing
        test_desc = "mobile base largo 80cm alto 90cm con 2 ripiani"
        params = client._parse_description_fallback(test_desc)
        print(f"✓ Fallback parsing works: {params}")
        
        # Verifica parametri estratti
        assert params['larghezza'] == 80.0
        assert params['altezza'] == 90.0
        assert params['num_ripiani'] == 2
        print("✓ Parsed parameters correct")
        
        # Test suggerimenti fallback
        suggestions = client._get_fallback_suggestions(test_desc)
        assert suggestions is not None
        assert len(suggestions) > 0
        print("✓ Fallback suggestions work")
        
        print("\nAI client tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ AI client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_manager():
    """Testa config manager"""
    print("\nTesting config manager...")
    
    try:
        config_manager = import_module_from_path(
            'config_manager_test',
            os.path.join(lib_path, 'config_manager.py')
        )
        print("✓ config_manager imported")
        
        # Test caricamento config default
        config = config_manager.load_config()
        assert config is not None
        assert 'ai_endpoint' in config
        print(f"✓ Default config loaded: {config}")
        
        print("\nConfig manager tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Config manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Esegue tutti i test"""
    print("=" * 60)
    print("FurnitureAI Add-in - Verification Script")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("AI Client", test_ai_client()))
    results.append(("Config Manager", test_config_manager()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
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
