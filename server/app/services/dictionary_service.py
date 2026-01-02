import json
import logging
import urllib.request
from typing import Set
from ..models import NetspeakPatterns, LeetspeakMap, MorphologyPatterns  
import os
logging.basicConfig(level=logging.INFO)

DICTIONARY_FILES = {
    'netspeak_patterns': 'app/dictionaries/netspeak_patterns.json',
    'leetspeak_map': 'app/dictionaries/leetspeak_map.json',
    'morphology_patterns': 'app/dictionaries/morphology_patterns.json'
}

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
    global filipino_word_set
    try:
        base_dir = os.path.dirname(__file__)
        dict_path = os.path.abspath(
            os.path.join(base_dir, '..', 'dictionaries', 'tagalog_dict.json')
        )

        with open(dict_path, encoding='utf-8') as f:
            data = json.load(f)

        words = set()

        def extract(obj):
            if isinstance(obj, str):
                w = ''.join(c for c in obj.lower() if c.isalnum())
                if len(w) >= 2:
                    words.add(w)

            elif isinstance(obj, dict):
                if "word" in obj:
                    extract(obj["word"])
                else:
                    for v in obj.values():
                        extract(v)

            elif isinstance(obj, list):
                for item in obj:
                    extract(item)

        extract(data)

        filipino_word_set = words
        logging.info(f"Loaded {len(filipino_word_set)} Tagalog words (LOCAL)")

    except Exception as e:
        logging.error(f"Failed to load local Tagalog dictionary: {e}")
        filipino_word_set = set()

def get_filipino_words() -> Set[str]:
    """Get the set of Tagalog/Filipino words for fuzzy matching"""
    return filipino_word_set