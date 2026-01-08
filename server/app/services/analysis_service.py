from .detection_service import DetectionService
from .deobfuscation_service import DeobfuscationService
from .preprocessing_service import normalize_input, word_tokenize_preserve_hyphens
from .translation_service import translate_to_clean_text


class AnalysisService:
    """High-level coordinator for detection and deobfuscation."""
    
    def __init__(self):
        self.detector = DetectionService()
        self.deobfuscator = DeobfuscationService()
    
    def analyze(self, text: str, language: str = 'unknown', use_fuzzy: bool = True) -> dict:
        """Analyze text: detect obfuscation and apply corrections based on signals."""
        detection_result = self.detector.analyze(text, language)
        signals = detection_result.get('detected_signals', {})
        
        deobfuscated, transformations = (
            self._deobfuscate(text, use_fuzzy) 
            if detection_result.get('isObfuscated') 
            else (text, [])
        )
        
        return {
            'original': text,
            'deobfuscated': deobfuscated,
            'detection': detection_result,
            'obfuscation_types': self._get_obfuscation_types(signals),
            'transformations': transformations
        }
    
    def _get_obfuscation_types(self, signals: dict) -> list:
        """Extract detected obfuscation types from signals."""
        type_map = {
            'netspeak': 'netspeak',
            'phonetic': 'phonetic',
            'leetspeak': 'leetspeak',
            'char_duplication': 'char_duplication',
            'vowel_omission': 'vowel_omission',
            'symbol_separation': 'symbol_separation'
        }
        return [v for k, v in type_map.items() if signals.get(k)]
    
    def _get_token_signals(self, token: str) -> dict:
        """Detect which obfuscation patterns apply to this token."""
        token_clean = token.lower().strip('.,!?;:()[]{}"\'-')
        
        return {
            'netspeak': self.detector.netspeak.is_accepted(token_clean),
            'leetspeak': self.detector.leetspeak.is_accepted(token_clean),
            'char_duplication': self.detector.char_duplication.is_accepted(token_clean),
            'vowel_omission': self.detector.vowel_omission.is_accepted(token_clean),
            'symbol_separation': self.detector.symbol_separation.is_accepted(token_clean),
            'phonetic': self.detector.phonetic.is_accepted(token_clean)['has_phonetic']
        }
    
    def _deobfuscate(self, text: str, use_fuzzy: bool = True) -> tuple:
        """Deobfuscate text using signal-driven approach, preserving newlines."""
        lines = text.split('\n')
        all_transformations = []
        deobfuscated_lines = []
        
        for line in lines:
            # Preserve empty lines
            if not line.strip():
                deobfuscated_lines.append(line)
                continue
            
            normalized = normalize_input(line)
            tokens = word_tokenize_preserve_hyphens(normalized)
            deobfuscated_tokens = []
            
            for token in tokens:
                if not token or token.isspace():
                    deobfuscated_tokens.append(token)
                    continue
                
                token_signals = self._get_token_signals(token)
                token_lower = token.lower()
                is_valid = self.deobfuscator._is_valid_word(token_lower)
                has_signals = any(token_signals.values())
                
                # Skip only if valid AND no obfuscation signals detected
                if is_valid and not has_signals:
                    deobfuscated_tokens.append(token)
                    continue
                
                try:
                    fixed_token = self.deobfuscator.deobfuscate(
                        token,
                        use_fuzzy=use_fuzzy,
                        signals=token_signals
                    )
                    deobfuscated_tokens.append(fixed_token)
                    
                    if token != fixed_token:
                        all_transformations.append({
                            'original': token,
                            'corrected': fixed_token
                        })
                
                except Exception as e:
                    print(f"[WARNING] Deobfuscation failed for '{token}': {e}")
                    deobfuscated_tokens.append(token)
            
            deobfuscated_lines.append(" ".join(deobfuscated_tokens))
        
        return "\n".join(deobfuscated_lines), all_transformations