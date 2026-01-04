from .preprocessing_service import normalize_input, word_tokenize
from .deobfuscation_service import DeobfuscationService
import string

def _join(tokens: list[str]) -> str:
    #Join tokens while keeping punctuation attached properly.
    opening_punct = {'"', "'", '(', '[', '{', '«', '¿', '¡', '`'}
    
    out: list[str] = []
    i = 0

    while i < len(tokens):
        t = tokens[i]
        if not t:
            i += 1
            continue

        is_punct = all(ch in string.punctuation for ch in t)
        
        if is_punct:
            has_opening = any(ch in opening_punct for ch in t)
            # Opening punctuation: attach to next word token
            if has_opening:
                # Look ahead for the next non-punctuation token
                j = i + 1
                while j < len(tokens) and tokens[j] and all(ch in string.punctuation for ch in tokens[j]):
                    j += 1
                # If we found a word token, attach opening punct to it
                if j < len(tokens) and tokens[j]:
                    out.append(t + tokens[j])
                    tokens[j] = ''  # Mark as consumed
                    i += 1
                    continue
            # Closing punctuation: attach to previous
            if out:
                out[-1] = out[-1] + t
            else:
                out.append(t)
        else:
            # Regular word (skip if already consumed)
            out.append(t)
        i += 1
    return " ".join(out).strip()

def translate_to_clean_text(deobfuscated_text: str) -> str:
    """
    Final step: Convert deobfuscated text into properly formatted clean text.
    This handles punctuation spacing and final presentation.
    """
    tokens = word_tokenize(deobfuscated_text)
    return _join(tokens)


def process_and_translate(text: str):
    """Full pipeline: normalize → tokenize → deobfuscate → translate"""
    # Normalize
    clean = normalize_input(text)

    # Tokenize
    tokens = word_tokenize(clean)

    # Deobfuscate
    service = DeobfuscationService()
    translated = [service.deobfuscate(t) for t in tokens]

    return _join(translated)