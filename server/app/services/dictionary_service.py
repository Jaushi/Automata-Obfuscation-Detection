import json
import logging
from ..models import NetspeakPatterns, LeetspeakMap, MorphologyPatterns  

logging.basicConfig(level=logging.INFO)

DICTIONARY_FILES = {
    'netspeak_patterns': 'server/app/dictionaries/netspeak_patterns.json',
    'leetspeak_map': 'server/app/dictionaries/leetspeak_map.json',
    'morphology_patterns': 'server/app/dictionaries/morphology_patterns.json'
}

cached_dictionaries = {} 

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