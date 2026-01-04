import re
import string
from .detection_service import DetectionService
from .deobfuscation_service import DeobfuscationService
from .preprocessing_service import normalize_input, word_tokenize

class AnalysisService:
    """
    High-level coordinator for detection and deobfuscation.
    Deobfuscation is signal-driven: uses detection results to guide corrections.
    """
    
    def __init__(self):
        self.detector = DetectionService()
        self.deobfuscator = DeobfuscationService()
    
    def analyze(self, text: str, language: str = 'unknown', use_fuzzy: bool = True) -> dict:
        """
        Analyze text: detect obfuscation and apply corrections based on signals.
        
        Args:
            text: Input text to analyze
            language: Language hint (default: 'unknown')
            use_fuzzy: Enable fuzzy matching in deobfuscation
            
        Returns:
            dict with original, deobfuscated, detection results, and types
        """
        # STEP 1: Detect obfuscation patterns (global level)
        detection_result = self.detector.analyze(text, language)
        signals = detection_result.get('taglish_signals', {})
        
        # STEP 2: Only trigger deobfuscator if obfuscation was detected
        if detection_result.get('isObfuscated'):
            deobfuscated = self._deobfuscate(text, use_fuzzy=use_fuzzy)
        else:
            deobfuscated = text
        
        final_output = ' '.join(final_output.split())
        
        return {
            'original': text,
            'deobfuscated': deobfuscated,
            'detection': detection_result,
            'obfuscation_types': self._get_obfuscation_types(signals)
        }
    
    def _get_obfuscation_types(self, signals: dict) -> list:
        """Extract detected obfuscation types from signals"""
        types = []
        
        if signals.get('abbreviation'):
            types.append('abbreviation')
        if signals.get('leetspeak'):
            types.append('leetspeak')
        if signals.get('character_duplication'):
            types.append('character_duplication')
        if signals.get('vowel_omission'):
            types.append('vowel_omission')
        if signals.get('morphology'):
            types.append('morphology')
        
        return types
    
    def _get_token_signals(self, token: str) -> dict:
        """
        Detect which obfuscation patterns apply to THIS specific token.
        Returns dict of signals for signal-driven deobfuscation.
        
        Args:
            token: Single token to analyze
            
        Returns:
            dict with per-token detection signals
        """
        token_clean = token.lower().strip('.,!?;:()[]{}"\'-')
        
        signals = {
            'abbreviation': self.detector.abbreviation.detect_single(token_clean),
            'leetspeak': self.detector.leetspeak.detect(token_clean),
            'character_duplication': self.detector.char_duplication.detect(token_clean),
            'vowel_omission': self.detector.vowel_omission.detect(token_clean),
            'morphology': self.detector.morphology.detect(token_clean)
        }
        
        return signals
    
    def _deobfuscate(self, text: str, use_fuzzy: bool = True) -> str:
        """
        Deobfuscate text with signal-driven approach.
        Each token's corrections are guided by its detected signals.
        
        Args:
            text: Text to deobfuscate
            use_fuzzy: Enable fuzzy matching
            
        Returns:
            Deobfuscated text
        """
        normalized = normalize_input(text)
        tokens = word_tokenize(normalized)
        deobfuscated_tokens = []
        
        for token in tokens:
            if not token or token.isspace():
                continue
            
            try:
                # Get per-token detection signals
                token_signals = self._get_token_signals(token)
                
                # Deobfuscate based on detected signals
                fixed_token = self.deobfuscator.deobfuscate(
                    token,
                    use_fuzzy=use_fuzzy,
                    signals=token_signals  # ← Pass signals, not obf_type
                )
                deobfuscated_tokens.append(fixed_token)
            
            except Exception as e:
                print(f"[WARNING] Deobfuscation failed for '{token}': {e}")
                deobfuscated_tokens.append(token)
        
        return " ".join(deobfuscated_tokens)