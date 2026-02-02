"""
Utility per logging in Fusion 360
Supporta logging verso la console di testo di Fusion e output standard
"""

try:
    import adsk.core
    _ADSK_AVAILABLE = True
except ImportError:
    _ADSK_AVAILABLE = False

import sys
from datetime import datetime
from typing import Optional


class FusionLogger:
    """Logger per add-in Fusion 360"""
    
    def __init__(self, name: str = "FurnitureAI"):
        """
        Inizializza logger
        
        Args:
            name: Nome del logger (prefix per i messaggi)
        """
        self.name = name
        self._ui: Optional['adsk.core.UserInterface'] = None
        
        if _ADSK_AVAILABLE:
            try:
                app = adsk.core.Application.get()
                self._ui = app.userInterface
            except:
                self._ui = None
        else:
            self._ui = None
    
    def _format_message(self, level: str, message: str) -> str:
        """Formatta messaggio con timestamp e livello"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp}] [{self.name}] {level}: {message}"
    
    def _write_to_text_palette(self, message: str):
        """Scrive nella Text Palette di Fusion 360"""
        if self._ui:
            try:
                # Ottieni o crea palette di testo
                text_palette = self._ui.palettes.itemById('TextCommands')
                if text_palette:
                    text_palette.writeText(message + '\n')
            except:
                pass
    
    def info(self, message: str):
        """Log messaggio informativo"""
        formatted = self._format_message('INFO', message)
        print(formatted)
        self._write_to_text_palette(formatted)
    
    def warning(self, message: str):
        """Log warning"""
        formatted = self._format_message('WARNING', message)
        print(formatted)
        self._write_to_text_palette(formatted)
    
    def error(self, message: str):
        """Log errore"""
        formatted = self._format_message('ERROR', message)
        print(formatted, file=sys.stderr)
        self._write_to_text_palette(formatted)
    
    def debug(self, message: str):
        """Log debug"""
        formatted = self._format_message('DEBUG', message)
        print(formatted)
        self._write_to_text_palette(formatted)
    
    def show_message(self, title: str, message: str):
        """Mostra message box all'utente"""
        if self._ui:
            try:
                self._ui.messageBox(message, title)
            except:
                pass


# Istanza globale di default
_default_logger: Optional[FusionLogger] = None


def get_logger(name: str = "FurnitureAI") -> FusionLogger:
    """
    Ottiene istanza logger (singleton pattern)
    
    Args:
        name: Nome logger
        
    Returns:
        Istanza FusionLogger
    """
    global _default_logger
    if _default_logger is None or _default_logger.name != name:
        _default_logger = FusionLogger(name)
    return _default_logger
