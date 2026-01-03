import re
import string
from .detection_service import DetectionService
from .deobfuscation_service import DeobfuscationService
from .preprocessing_service import normalize_input, word_tokenize

class AnalysisService:
    """Main service combining detection and deobfuscation in one pipeline"""

    def __init__(self):
        self.detector = DetectionService()
        self.deobfuscator = DeobfuscationService()
    
    def analyze(self, text: str, language: str = 'unknown', use_fuzzy: bool = True) -> dict:
        """Analyze text: detect obfuscation types and deobfuscate intelligently"""
        
        # Step 1: Detect what types of obfuscation are present
        detection_result = self.detector.analyze(text, language)
        signals = detection_result.get('taglish_signals', {})
        
        # Step 2: Deobfuscate with knowledge of what was detected
        if detection_result.get('isObfuscated'):
            deobfuscated = self._deobfuscate(text, signals, use_fuzzy=use_fuzzy)
        else:
            deobfuscated = text
        
        return {
            'original': text,
            'deobfuscated': deobfuscated,
            'detection': detection_result,
            'obfuscation_types': self._get_obfuscation_types(signals)
        }
    
    def _get_obfuscation_types(self, signals: dict) -> list:
        """Extract which types of obfuscation were detected"""
        types = []
        if signals.get('netspeak'):
            types.append('netspeak')
        if signals.get('leetspeak'):
            types.append('leetspeak')
        if signals.get('character_duplication'):
            types.append('character_duplication')
        if signals.get('vowel_omission'):
            types.append('vowel_omission')
        if signals.get('morphology'):
            types.append('morphology')
        return types
    
    def _deobfuscate(self, text: str, signals: dict, use_fuzzy: bool = True) -> str:
        """Deobfuscate with awareness of detected patterns"""
        normalized = normalize_input(text)
        tokens = word_tokenize(normalized)
        deobfuscated_tokens = []
        
        for token in tokens:
            if not token or token.isspace():
                continue
                
            token_obf_type = self._get_token_obfuscation_type(token)
            fixed_token = self.deobfuscator.deobfuscate(
                token, 
                use_fuzzy=use_fuzzy,
                obf_type=token_obf_type
            )
            deobfuscated_tokens.append(fixed_token)
        
        return " ".join(deobfuscated_tokens)  
    
    def _get_token_obfuscation_type(self, token: str) -> str:
        """Identify what type of obfuscation this token contains"""
        # Check in priority order: netspeak > leet > duplication > vowel omission > morphology
        token_clean = token.lower().strip('.,!?;:()[]{}"\'-')
        
        # Netspeak first (most specific - exact dictionary match)
        if self.detector.netspeak.detect(token_clean):
            return 'netspeak'
        
        # Then obvious obfuscations
        if self.detector.leet.detect(token_clean):
            return 'leetspeak'
        
        if self.detector.duplication.detect(token_clean):
            return 'character_duplication'
        
        if self.detector.vowel.detect(token_clean):
            return 'vowel_omission'
        
        # Morphology last (broadest match)
        if self.detector.morph.detect(token_clean):
            return 'morphology'
        
        return 'unknown'