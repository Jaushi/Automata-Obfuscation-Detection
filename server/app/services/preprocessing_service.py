import re
import string

# Normalization
def normalize_input(raw_text: str) -> str:
    text = raw_text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    text = text.replace('—', '-').replace('"', '"').replace('"', '"')
    return text

# Tokenization - split words from punctuation, preserve valid punctuation
def word_tokenize(clean_text: str) -> list[str]:
    """Tokenize text, separating words from punctuation but keeping valid punctuation attached."""
    tokens = []
    # Match words (alphanumeric + some special chars) and punctuation separately
    pattern = r'([a-z0-9@!$|]+)|([^\s])'
    for match in re.finditer(pattern, clean_text):
        word, punct = match.groups()
        if word:
            tokens.append(word)
        elif punct and punct not in string.whitespace:
            # Attach valid punctuation to previous token if exists
            if tokens and punct in '!?.,;:':
                tokens[-1] += punct
            else:
                tokens.append(punct)
    return tokens

def extract_word(token: str) -> str:
    """Extract word part from token, including leetspeak chars, removing only punctuation."""
    # Include alphanumeric + common leetspeak chars (@, 1, 3, 4, 0, $, !, |, etc.)
    match = re.search(r'[a-z0-9@$!|€]+', token.lower())
    return match.group() if match else ''
