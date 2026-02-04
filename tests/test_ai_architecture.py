#!/usr/bin/env python3
"""
Test per architettura IA multimodale
Verifica che i moduli AI possano essere importati e abbiano le funzioni base
"""

import sys
import os
import importlib.util

# Aggiungi path per importare moduli
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ai_path = os.path.join(repo_root, 'fusion_addin', 'lib', 'ai')


def import_module_from_path(module_name, file_path):
    """Importa modulo direttamente da file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_llm_client():
    """Testa LLM client"""
    print("Testing LLM client...")
    
    try:
        llm_client = import_module_from_path(
            'llm_client',
            os.path.join(ai_path, 'llm_client.py')
        )
        print("✓ llm_client imported")
        
        # Crea client
        client = llm_client.LLMClient()
        print("✓ LLMClient instantiated")
        
        # Verifica metodi
        assert hasattr(client, 'generate_kitchen_layout')
        assert hasattr(client, 'optimize_module_placement')
        assert hasattr(client, 'suggest_hardware')
        print("✓ LLMClient methods present")
        
        # Test fallback layout
        layout = client._fallback_layout("cucina lineare")
        assert layout is not None
        assert 'layout_type' in layout
        assert 'modules' in layout
        assert len(layout['modules']) > 0
        print(f"✓ Fallback layout works: {layout['layout_type']}")
        
        # Test fallback hardware
        hardware = client._fallback_hardware({
            'larghezza': 80, 'altezza': 90, 'profondita': 60,
            'num_ante': 2, 'num_cassetti': 3, 'num_ripiani': 2
        })
        assert hardware is not None
        assert 'cerniere' in hardware
        assert hardware['cerniere']['quantita'] == 4  # 2 ante * 2
        print(f"✓ Fallback hardware works: {hardware['cerniere']['quantita']} cerniere")
        
        print("\nLLM client tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ LLM client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vision_client():
    """Testa Vision client"""
    print("\nTesting Vision client...")
    
    try:
        vision_client = import_module_from_path(
            'vision_client',
            os.path.join(ai_path, 'vision_client.py')
        )
        print("✓ vision_client imported")
        
        # Crea client
        client = vision_client.VisionClient()
        print("✓ VisionClient instantiated")
        
        # Verifica metodi
        assert hasattr(client, 'analyze_floor_plan')
        assert hasattr(client, 'analyze_style_photo')
        assert hasattr(client, 'extract_dimensions_from_image')
        print("✓ VisionClient methods present")
        
        # Test placeholder floor plan
        plan = client.analyze_floor_plan("test.jpg")
        assert plan is not None
        assert 'room_width' in plan
        assert 'suggested_layout' in plan
        print(f"✓ Floor plan analysis placeholder: {plan['suggested_layout']}")
        
        # Test placeholder style
        style = client.analyze_style_photo("test.jpg")
        assert style is not None
        assert 'door_style' in style
        print(f"✓ Style analysis placeholder: {style['door_style']}")
        
        print("\nVision client tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Vision client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_speech_client():
    """Testa Speech client"""
    print("\nTesting Speech client...")
    
    try:
        speech_client = import_module_from_path(
            'speech_client',
            os.path.join(ai_path, 'speech_client.py')
        )
        print("✓ speech_client imported")
        
        # Crea client
        client = speech_client.SpeechClient()
        print("✓ SpeechClient instantiated")
        
        # Verifica metodi
        assert hasattr(client, 'transcribe')
        assert hasattr(client, 'voice_to_command')
        assert hasattr(client, 'detect_language')
        print("✓ SpeechClient methods present")
        
        # Test placeholder transcription
        text = client.transcribe("test.wav")
        assert text is not None
        print(f"✓ Transcription placeholder works")
        
        # Test placeholder language detection
        lang = client.detect_language("test.wav")
        assert lang == "it"
        print(f"✓ Language detection placeholder: {lang}")
        
        print("\nSpeech client tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Speech client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_module():
    """Testa modulo AI principale"""
    print("\nTesting AI module...")
    
    try:
        ai_module = import_module_from_path(
            'ai',
            os.path.join(ai_path, '__init__.py')
        )
        print("✓ ai module imported")
        
        # Verifica exports
        assert hasattr(ai_module, 'LLMClient')
        assert hasattr(ai_module, 'VisionClient')
        assert hasattr(ai_module, 'SpeechClient')
        print("✓ AI module exports correct")
        
        print("\nAI module tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ AI module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Esegue tutti i test"""
    print("=" * 60)
    print("FurnitureAI - AI Architecture Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("AI Module", test_ai_module()))
    results.append(("LLM Client", test_llm_client()))
    results.append(("Vision Client", test_vision_client()))
    results.append(("Speech Client", test_speech_client()))
    
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
        print("✓ All AI architecture tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
