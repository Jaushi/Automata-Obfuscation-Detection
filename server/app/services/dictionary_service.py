import json
import logging
import urllib.request
from typing import Set
from ..models import NetspeakPatterns, LeetspeakMap, MorphologyPatterns  

logging.basicConfig(level=logging.INFO)

DICTIONARY_FILES = {
    'netspeak_patterns': 'app/dictionaries/netspeak_patterns.json',
    'leetspeak_map': 'app/dictionaries/leetspeak_map.json',
    'morphology_patterns': 'app/dictionaries/morphology_patterns.json'
}

TAGALOG_DICTIONARY_URL = "https://raymelon.github.io/tagalog-dictionary-scraper/tagalog_dict.json"

cached_dictionaries = {} 
filipino_word_set: Set[str] = set()

def load_and_cache_dictionaries():
    model_classes = {
        'netspeak_patterns': NetspeakPatterns,
        'leetspeak_map': LeetspeakMap,
        'morphology_patterns': MorphologyPatterns
    }
    for name, file_path in DICTIONARY_FILES.items():
        data = load_dictionary(file_path)
        model_class = model_classes[name]
        if "error" in data:
            logging.error(f"Failed to load {name}: {data['error']}")
            cached_dictionaries[name] = model_class(name=name, error=data["error"])
        else:
            cached_dictionaries[name] = model_class(name=name, data=data)
    
    # Load Filipino dictionary from URL
    load_filipino_dictionary()

def load_dictionary(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": f"Dictionary file not found: {file_path}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON in file: {file_path}"}
    except Exception as e:
        return {"error": str(e)}

def load_filipino_dictionary():
    """Load Tagalog dictionary from remote URL (GitHub Pages API) for fuzzy matching"""
    global filipino_word_set
    try:
        with urllib.request.urlopen(TAGALOG_DICTIONARY_URL, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # Data is a simple array of words (strings)
            words = set()
            for word in data:
                if isinstance(word, str):
                    word_clean = word.lower().strip()
                    # Remove punctuation, keep only alphanumeric
                    word_clean = ''.join(c for c in word_clean if c.isalnum())
                    if word_clean and len(word_clean) >= 2:  # Only words with 2+ chars
                        words.add(word_clean)
            
            filipino_word_set = words
            logging.info(f"Loaded {len(filipino_word_set)} Tagalog words from dictionary")
    except Exception as e:
        logging.warning(f"Failed to load Tagalog dictionary from URL: {e}")
        filipino_word_set = set()

def get_filipino_words() -> Set[str]:
    """Get the set of Tagalog/Filipino words for fuzzy matching"""
    return filipino_word_set