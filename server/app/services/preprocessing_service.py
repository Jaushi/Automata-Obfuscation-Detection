import re

# Normalization
def normalize_input(raw_text: str) -> str:
    text = raw_text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    text = text.replace('—', '-').replace('“', '"').replace('”', '"')
    return text

# Tokenization
def word_tokenize(clean_text: str) -> list[str]:
    return re.findall(r"[a-z0-9@!$|]+|[^\s]", clean_text)
