"""
Modulo IA Multimodale - FurnitureAI
Architettura per integrazione LLM, Vision e Speech
"""

from .llm_client import LLMClient
from .vision_client import VisionClient
from .speech_client import SpeechClient

__all__ = ['LLMClient', 'VisionClient', 'SpeechClient']
