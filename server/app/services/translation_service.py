from .preprocessing_service import normalize_input, word_tokenize
from .deobfuscation_service import DeobfuscationService
import string


def _smart_join(tokens: list[str]) -> str:
    """Join tokens while keeping punctuation attached to preceding word.

    Rules:
    - If a token consists entirely of punctuation characters (from string.punctuation),
      attach it to the previous token without a space.
    - Otherwise separate tokens with a single space.
    """
    out: list[str] = []
    for t in tokens:
        if t and all(ch in string.punctuation for ch in t) and out:
            # attach to previous token
            out[-1] = out[-1] + t
        else:
            out.append(t)
    return " ".join(out)


def process_and_translate(text: str):
    # Normalize
    clean = normalize_input(text)

    # Tokenize
    tokens = word_tokenize(clean)

    # Deobfuscate
    service = DeobfuscationService()
    translated = [service.deobfuscate(t) for t in tokens]

    return _smart_join(translated)
