import re
import string


def normalize_input(raw_text: str) -> str:
    """
    Normalize text while PRESERVING symbol separators for detection.
    
    Preserves: - . _ | * @ (needed for symbol separation detection)
    
    Args:
        raw_text: Raw input text
        
    Returns:
        Normalized text with consistent spacing and formatting
    """
    text = raw_text.lower()
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    text = text.replace('"', '"').replace('"', '"')  # Normalize quotes
    text = text.replace('—', '-')  # Em-dash to hyphen
    return text


def word_tokenize(clean_text: str) -> list[str]:
    """
    Tokenize text, keeping symbol-separated patterns and leetspeak intact.
    
    Preserves:
    - Symbol separators: - . _ | * (for detection)
    - Leetspeak char @: $!|€ (for leet detection)
    - Valid punctuation: ! ? . , ; : (attaches to words)
    
    Args:
        clean_text: Normalized text from normalize_input()
        
    Returns:
        List of tokens with separators and leetspeak chars preserved
        
    Examples:
        "k-m-u-s-t-a p@ss" → ["k-m-u-s-t-a", "p@ss"]
        "hello, world!" → ["hello,", "world!"]
    """
    tokens = []
    # Pattern with 3 groups:
    # 1. Symbol-separated patterns with optional @ and punctuation
    # 2. Regular words with optional @ and punctuation
    # 3. Standalone punctuation
    pattern = r'([a-z0-9@]+(?:[-._|*@]+[a-z0-9@]+)*[!?.,;:]*)|([a-z0-9@]+[!?.,;:]*)|([^\s])'
    
    for match in re.finditer(pattern, clean_text):
        symbol_sep, word, punct = match.groups()
        
        if symbol_sep:
            # Symbol-separated - keep @ and separators, remove trailing invalid chars
            cleaned = symbol_sep.rstrip('_-.|*')
            if cleaned:
                tokens.append(cleaned)
        elif word:
            # Regular word - keep @ and punctuation
            cleaned = word.rstrip('_-.|*')
            if cleaned:
                tokens.append(cleaned)
        elif punct and punct not in string.whitespace:
            # Standalone punctuation - only attach valid ones
            if punct not in '_-.|*@':
                if tokens and punct in '!?.,;:':
                    tokens[-1] += punct
                else:
                    tokens.append(punct)
    
    return [t for t in tokens if t.strip()]


def word_tokenize_preserve_hyphens(text: str) -> list[str]:
    """
    Tokenize while preserving hyphens and symbol separators.
    
    This is the PRIMARY tokenization function. Use this for all tokenization.
    
    Args:
        text: Text to tokenize (should be normalized first)
        
    Returns:
        List of tokens
    """
    return word_tokenize(text)