class DetectionService:
    """Service for detecting obfuscated code patterns"""
    
    def __init__(self):
        self.patterns = [
            'variable_name_obfuscation',
            'string_encryption',
            'control_flow_flattening',
            'dead_code_insertion'
        ]
    
    def analyze(self, code: str, language: str = 'unknown') -> dict:
        """
        Analyze code for obfuscation patterns
        
        Args:
            code: Source code to analyze
            language: Programming language of the code
            
        Returns:
            Dictionary containing detection results
        """
        # Basic heuristics for demonstration
        detected_patterns = []
        
        # Check for short variable names
        if self._has_short_variable_names(code):
            detected_patterns.append('variable_name_obfuscation')
        
        # Check for unusual character sequences
        if self._has_unusual_patterns(code):
            detected_patterns.append('string_encryption')
        
        is_obfuscated = len(detected_patterns) > 0
        confidence = min(len(detected_patterns) * 0.3, 1.0)
        
        return {
            'isObfuscated': is_obfuscated,
            'confidence': confidence,
            'patterns': detected_patterns,
            'language': language
        }
    
    def _has_short_variable_names(self, code: str) -> bool:
        """Check for prevalence of single-character variable names"""
        # Simple heuristic: look for single-letter variables
        single_char_vars = sum(1 for line in code.split('\n') 
                              if any(f' {c} ' in line for c in 'abcdefghijklmnopqrstuvwxyz'))
        return single_char_vars > 5
    
    def _has_unusual_patterns(self, code: str) -> bool:
        """Check for unusual character patterns"""
        # Check for hex patterns or base64-like strings
        hex_count = code.count('\\x')
        return hex_count > 3
