from .preprocessing_service import normalize_input, word_tokenize
from .deobfuscation_service import DeobfuscationService

def process_and_translate(text: str):
    
    # Normalize
    clean = normalize_input(text)
    
    # Tokenize 
    tokens = word_tokenize(clean)
    
    # Deobfuscate 
    service = DeobfuscationService()
    translated = [service.deobfuscate(t) for t in tokens]
    
    return " ".join(translated)
