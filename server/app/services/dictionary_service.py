import json
import logging
import urllib.request
from typing import Set
from ..models import NetspeakPatterns, LeetspeakMap
import os

logging.basicConfig(level=logging.INFO)

DICTIONARY_FILES = {
    'netspeak_patterns': 'app/dictionaries/netspeak_patterns.json',
    'leetspeak_map': 'app/dictionaries/leetspeak_map.json',
    #'morphology_patterns': 'app/dictionaries/morphology_patterns.json',
    'english_words': 'app/dictionaries/english_words.json'
}

cached_dictionaries = {} 
filipino_word_set: Set[str] = set()
english_word_set: Set[str] = set()

def load_and_cache_dictionaries():
    model_classes = {
        'netspeak_patterns': NetspeakPatterns,
        'leetspeak_map': LeetspeakMap,
        #'morphology_patterns': MorphologyPatterns
    }
    for name, file_path in DICTIONARY_FILES.items():
        if name == 'english_words':
            load_english_dictionary()
            continue
            
        data = load_dictionary(file_path)
        model_class = model_classes[name]
        if "error" in data:
            logging.error(f"Failed to load {name}: {data['error']}")
            cached_dictionaries[name] = model_class(name=name, error=data["error"])
        else:
            cached_dictionaries[name] = model_class(name=name, data=data)
    
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

def load_english_dictionary():
    """Load English words from ALL npm wordlist sizes + local fallback"""
    global english_word_set
    words = set()
    
    # All available wordlist sizes
    npm_wordlists = [
        'english-words-10.json',
        'english-words-20.json',
        'english-words-35.json',
        'english-words-40.json',
        'english-words-50.json',
        'english-words-55.json',
        'english-words-60.json',
        'english-words-70.json',
    ]
    
    # STEP 1: Load from npm wordlist-english (all sizes)
    npm_loaded = 0
    try:
        base_dir = os.path.dirname(__file__)
        npm_base_path = os.path.abspath(
            os.path.join(
                base_dir,
                '..', '..',
                'node_modules',
                'wordlist-english'
            )
        )
        
        for wordlist_file in npm_wordlists:
            npm_dict_path = os.path.join(npm_base_path, wordlist_file)
            
            try:
                with open(npm_dict_path, encoding='utf-8') as f:
                    npm_data = json.load(f)
                
                # Extract words from this wordlist
                for word in npm_data:
                    if isinstance(word, str):
                        w = word.lower().strip()
                        if len(w) >= 2:
                            words.add(w)
                
                npm_loaded += len(npm_data)
                logging.info(f"Loaded {wordlist_file}: {len(npm_data)} words")
            
            except FileNotFoundError:
                logging.debug(f"Wordlist not found: {wordlist_file}")
            except Exception as e:
                logging.warning(f"Failed to load {wordlist_file}: {e}")
        
        logging.info(f"Total from npm wordlist-english: {len(words)} unique words")
    
    except Exception as e:
        logging.warning(f"Failed to load npm wordlists: {e}")
    
    # STEP 2: Load from local dictionary and merge
    try:
        base_dir = os.path.dirname(__file__)
        local_dict_path = os.path.abspath(
            os.path.join(base_dir, '..', 'dictionaries', 'english_words.json')
        )

        with open(local_dict_path, encoding='utf-8') as f:
            local_data = json.load(f)

        # Extract words from local JSON
        def extract(obj):
            if isinstance(obj, str):
                w = obj.lower().strip()
                if len(w) >= 2:
                    words.add(w)
            elif isinstance(obj, dict):
                for v in obj.values():
                    extract(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item)

        before_local = len(words)
        extract(local_data)
        added_local = len(words) - before_local
        
        logging.info(f"Added {added_local} local English words")

    except FileNotFoundError:
        logging.debug(f"Local English dictionary not found")
    except Exception as e:
        logging.warning(f"Failed to load local English dictionary: {e}")
    
    english_word_set = words
    logging.info(f"✓ Final English word set: {len(english_word_set)} total unique words")

def load_filipino_dictionary():
    """Load Filipino/Tagalog words from local dictionary"""
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
        logging.error(f"Failed to load Tagalog dictionary: {e}")
        filipino_word_set = set()

def get_filipino_words() -> Set[str]:
    """Get the set of Tagalog/Filipino words for fuzzy matching"""
    return filipino_word_set

def get_english_words() -> Set[str]:
    """Get the set of English words (npm + local) for fuzzy matching"""
    return english_word_set