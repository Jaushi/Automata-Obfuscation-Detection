import json
import os
import logging
from app.services.fuzzy_matching_service import FuzzyMatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetectionService:
    """Service for detecting obfuscated code patterns"""
    
    def __init__(self):
        self.patterns = [
            'variable_name_obfuscation',
            'string_encryption',
            'control_flow_flattening',
            'dead_code_insertion'
        ]
        self.fuzzy_matching_service = FuzzyMatcher(threshold=75)
        self.taglish_dictionary = self._load_dictionary()
    
    def _load_english_words_nltk(self):
        """Load English words using NLTK library"""
        try:
            import nltk
            # Try to find the words corpus
            try:
                nltk.data.find('corpora/words')
            except LookupError:
                logger.info("Downloading NLTK words corpus...")
                nltk.download('words', quiet=True)
            
            from nltk.corpus import words
            english_words = set(w.lower() for w in words.words())
            logger.info(f"✅ Loaded {len(english_words)} English words from NLTK")
            return english_words
        except Exception as e:
            logger.warning(f"Could not load NLTK words: {e}")
            return set()
    
    def _load_english_words_enchant(self):
        """Load English words using PyEnchant library"""
        try:
            import enchant
            en_dict = enchant.Dict("en_US")
    
            common_english = {
                'hello', 'world', 'people', 'miss', 'you', 'all', 'good', 'morning',
                'night', 'love', 'like', 'want', 'need', 'have', 'make', 'think',
                'know', 'time', 'life', 'work', 'right', 'come', 'look', 'day',
                'great', 'thanks', 'please', 'sorry', 'help', 'friend', 'family'
            }
            logger.info(f"✅ PyEnchant available for spell checking ({len(common_english)} common words)")
            return common_english
        except Exception as e:
            logger.warning(f"Could not load PyEnchant: {e}")
            return set()
    
    def _load_filipino_words_json(self):
        """Load Filipino/Taglish words from existing JSON dictionaries"""
        dictionary_words = set()
        
        # Path to dictionaries folder
        dict_path = os.path.join(os.path.dirname(__file__), '..', 'dictionaries')
        
        try:
            # Load netspeak patterns
            with open(os.path.join(dict_path, 'netspeak_patterns.json'), 'r', encoding='utf-8') as f:
                netspeak = json.load(f)
                filipino_netspeak = netspeak.get('filipino_netspeak', {})
                
                # Extract root words from shortcuts
                shortcuts = filipino_netspeak.get('filipino_shortcuts', {})
                dictionary_words.update(shortcuts.keys())
                
                # Extract acronym expansions
                acronyms = filipino_netspeak.get('acronyms', {})
                dictionary_words.update(acronyms.keys())
                
                # Extract common slang
                common_slang = filipino_netspeak.get('common_slang', {})
                dictionary_words.update(common_slang.keys())
            
            # Load leetspeak patterns
            with open(os.path.join(dict_path, 'leetspeak_map.json'), 'r', encoding='utf-8') as f:
                leetspeak = json.load(f)
                
                # Extract root words from filipino leet examples
                filipino_leet = leetspeak.get('filipino_leet_examples', {})
                dictionary_words.update(filipino_leet.keys())
            
            # Load morphology patterns
            with open(os.path.join(dict_path, 'morphology_patterns.json'), 'r', encoding='utf-8') as f:
                morphology = json.load(f)
                filipino_patterns = morphology.get('filipino_text_patterns', {})
                
                # Extract taglish fillers
                fillers = filipino_patterns.get('taglish_fillers', [])
                dictionary_words.update(fillers)
                
                # Extract shortcuts
                shortcuts = filipino_patterns.get('taglish_shortcuts', [])
                dictionary_words.update(shortcuts)
            
            logger.info(f"Loaded {len(dictionary_words)} Filipino/Taglish words from JSON")
            return dictionary_words
            
        except Exception as e:
            logger.error(f"Error loading Filipino dictionaries: {e}")
            return set()
    
    def _load_dictionary(self):
        """
        Hybrid approach: Load words from multiple sources with fallback
        
        Priority:
        1. Filipino words from JSON dictionaries (always loaded)
        2. English words from NLTK (preferred)
        3. English words from PyEnchant (fallback)
        4. Minimal hardcoded fallback (last resort)
        """
        all_words = set()
        
        # 1. Load Filipino words from JSON dictionaries (primary source)
        filipino_words = self._load_filipino_words_json()
        all_words.update(filipino_words)
        
        # 2. Try loading English words from NLTK
        english_words_nltk = self._load_english_words_nltk()
        if english_words_nltk:
            all_words.update(english_words_nltk)
        else:
            # 3. Fallback to PyEnchant
            english_words_enchant = self._load_english_words_enchant()
            if english_words_enchant:
                all_words.update(english_words_enchant)
            else:
                # 4. Last resort: minimal hardcoded English words
                logger.warning("Using minimal fallback English dictionary")
                fallback_english = {
                    'hello', 'world', 'people', 'miss', 'you', 'all', 'love',
                    'good', 'great', 'night', 'day', 'time', 'life', 'work'
                }
                all_words.update(fallback_english)
        
        logger.info(f"Total dictionary size: {len(all_words)} words")
        return list(all_words)
    
    def detect_with_fuzzy(self, text: str) -> dict:
        """
        Enhanced detection with fuzzy matching for obfuscated text
        
        Args:
            text: Text to analyze for obfuscation
            
        Returns:
            Dictionary with detection results and fuzzy matches
        """
        # Apply fuzzy matching
        words = text.split()
        fuzzy_corrections = []
        
        for word in words:
            # Skip if word is already in dictionary
            if word.lower() in [d.lower() for d in self.taglish_dictionary]:
                continue
            
            # Try fuzzy matching
            matches = self.fuzzy_matching_service.match_word(
                word, 
                self.taglish_dictionary,
                limit=1
            )
            
            if matches and matches[0]['score'] >= 70:  # Lowered from 75 to catch short words like "mga"
                fuzzy_corrections.append({
                    'original': word,
                    'match': matches[0]['word'],
                    'score': matches[0]['confidence']
                })
        
        # Build result
        result = {
            'is_obfuscated': len(fuzzy_corrections) > 0,
            'confidence': sum(m['score'] for m in fuzzy_corrections) / len(words) if words else 0,
            'original_text': text,
            'fuzzy_matches': fuzzy_corrections
        }
        
        # Generate deobfuscated version if corrections found
        if fuzzy_corrections:
            result['deobfuscated'] = self.fuzzy_matching_service.deobfuscate_text(
                text, 
                self.taglish_dictionary
            )
        
        return result
    
    def analyze(self, code: str, language: str = 'unknown') -> dict:
        """
        Analyze code for obfuscation patterns
        
        Args:
            code: Source code to analyze
            language: Programming language of the code
            
        Returns:
            Dictionary containing detection results
        """
        # Basic heuristics for demonstration
        detected_patterns = []
        
        # Check for short variable names
        if self._has_short_variable_names(code):
            detected_patterns.append('variable_name_obfuscation')
        
        # Check for unusual character sequences
        if self._has_unusual_patterns(code):
            detected_patterns.append('string_encryption')
        
        is_obfuscated = len(detected_patterns) > 0
        confidence = min(len(detected_patterns) * 0.3, 1.0)
        
        return {
            'isObfuscated': is_obfuscated,
            'confidence': confidence,
            'patterns': detected_patterns,
            'language': language
        }
    
    def _has_short_variable_names(self, code: str) -> bool:
        """Check for prevalence of single-character variable names"""
        # Simple heuristic: look for single-letter variables
        single_char_vars = sum(1 for line in code.split('\n') 
                              if any(f' {c} ' in line for c in 'abcdefghijklmnopqrstuvwxyz'))
        return single_char_vars > 5
    
    def _has_unusual_patterns(self, code: str) -> bool:
        """Check for unusual character patterns"""
        # Check for hex patterns or base64-like strings
        hex_count = code.count('\\x')
        return hex_count > 3