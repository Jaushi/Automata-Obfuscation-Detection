import re
import string
from .detection_service import DetectionService
from .deobfuscation_service import DeobfuscationService
from .preprocessing_service import normalize_input
from .translation_service import word_tokenize_preserve_hyphens

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
        """
        # STEP 1: Detect obfuscation patterns
        detection_result = self.detector.analyze(text, language)
        signals = detection_result.get('detected_signals', {})
        
        transformations = []
        
        # STEP 2: Only deobfuscate if obfuscation was detected
        if detection_result.get('isObfuscated'):
            deobfuscated, transformations = self._deobfuscate(text, use_fuzzy=use_fuzzy)
        else:
            deobfuscated = text
        
        return {
            'original': text,
            'deobfuscated': deobfuscated,
            'detection': detection_result,
            'obfuscation_types': self._get_obfuscation_types(signals),
            'transformations': transformations
        }
    
    def _get_obfuscation_types(self, signals: dict) -> list:
        """Extract detected obfuscation types from signals"""
        types = []
        
        if signals.get('netspeak'):
            types.append('netspeak')
        if signals.get('leetspeak'):
            types.append('leetspeak')
        if signals.get('char_duplication'):
            types.append('char_duplication')
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
            'netspeak': self.detector.netspeak.detect_single(token_clean),
            'leetspeak': self.detector.leetspeak.detect(token_clean),
            'char_duplication': self.detector.char_duplication.detect(token_clean),
            'vowel_omission': self.detector.vowel_omission.detect(token_clean),
            'morphology': self.detector.morphology.detect(token_clean)
        }
        
        return signals
    
    def _deobfuscate(self, text: str, use_fuzzy: bool = True) -> tuple:
        """Deobfuscate text, but skip words already in dictionary."""
        lines = text.split('\n')
        deobfuscated_lines = []
        transformations = []
        
        for line in lines:
            normalized = normalize_input(line)
            tokens = word_tokenize_preserve_hyphens(normalized)
            deobfuscated_tokens = []
            
            for token in tokens:
                if not token or token.isspace():
                    deobfuscated_tokens.append(token)
                    continue
                
                # ADD THIS DEBUG
                token_lower = token.lower()
                is_valid = self.deobfuscator._is_valid_word(token_lower)
                print(f"[DEBUG TOKEN] '{token}' -> valid_word: {is_valid}")
                
                # Skip if word is already in dictionary
                if is_valid:
                    deobfuscated_tokens.append(token)
                    continue
                
                # ADD THIS DEBUG
                token_signals = self._get_token_signals(token)
                print(f"[DEBUG SIGNALS] '{token}' -> {token_signals}")
                
                try:
                    fixed_token = self.deobfuscator.deobfuscate(
                        token,
                        use_fuzzy=use_fuzzy,
                        signals=token_signals
                    )
                    deobfuscated_tokens.append(fixed_token)
                    
                    if token != fixed_token:
                        print(f"[DEBUG TRANSFORM] '{token}' -> '{fixed_token}'")
                        transformations.append({
                            'original': token,
                            'corrected': fixed_token
                        })
                
                except Exception as e:
                    print(f"[WARNING] Deobfuscation failed for '{token}': {e}")
                    deobfuscated_tokens.append(token)
            
            deobfuscated_lines.append(" ".join(deobfuscated_tokens))
        
        return "\n".join(deobfuscated_lines), transformations
