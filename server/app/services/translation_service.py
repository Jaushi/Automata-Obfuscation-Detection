from .preprocessing_service import normalize_input
from .deobfuscation_service import DeobfuscationService
import string
import re

def word_tokenize_preserve_hyphens(text: str) -> list:
    """Tokenize while preserving hyphens within words and attached punctuation"""
    # Match: word + optional attached trailing punctuation, OR standalone punctuation
    tokens = re.findall(r"[(\[{]*[a-z0-9@!$|€*-]+[?.,;:!)\]}]*", text)
    return [t for t in tokens if t.strip()]

def _join(tokens: list[str]) -> str:
    """Join tokens intelligently without adding unnecessary spaces."""
    result = ""
    opening_brackets = {'(', '[', '{', '"', "'"}
    closing_brackets = {')', ']', '}', '"', "'", '.', ',', '!', '?', ';', ':'}
    
    for i, token in enumerate(tokens):
        # Add space before token if needed
        if i > 0:
            prev_token = tokens[i-1]
            # Don't add space if current is closing punct or previous is opening punct
            if token not in closing_brackets and prev_token not in opening_brackets:
                result += " "
        
        result += token
    
    return result.strip()

def translate_to_clean_text(deobfuscated_text: str) -> str:
    """
    Final step: Convert deobfuscated text into properly formatted clean text.
    This handles punctuation spacing and final presentation.
    Preserves hyphens within words (real-time stays as real-time).
    """
    tokens = word_tokenize_preserve_hyphens(deobfuscated_text)
    return _join(tokens)

def process_and_translate(text: str):
    """Full pipeline: normalize → tokenize → deobfuscate → translate"""
    # Normalize
    clean = normalize_input(text)
    
    # Tokenize with hyphen preservation
    tokens = word_tokenize_preserve_hyphens(clean)
    
    # Deobfuscate
    service = DeobfuscationService()
    translated = [service.deobfuscate(t) for t in tokens]
    
    return _join(translated)