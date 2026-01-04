from .dictionary_service import cached_dictionaries, get_filipino_words, get_english_words
from .fuzzy_matching_service import FuzzyMatcher
import re

class DeobfuscationService:  
    def __init__(self):
        leet_obj = cached_dictionaries.get('leetspeak_map')
        self.leet_data = leet_obj.data if leet_obj else {}
        
        abbrev_obj = cached_dictionaries.get('netspeak_patterns')
        self.abbrev_data = abbrev_obj.data if abbrev_obj else {}
        
        protected_obj = cached_dictionaries.get('english_protected_words')
        self.protected_data = protected_obj.data if protected_obj else {}
        
        morph_obj = cached_dictionaries.get('morphology_patterns')
        morph_data = morph_obj.data if morph_obj else {}
        self.morph_corrections_data = morph_data.get('morphological_corrections', {})

        
        self._build_leet_map()
        self._build_abbreviation_map()
        self._build_morpho_corrections_map()
        self._build_primary_dict()
        self._build_secondary_dict()
        self._build_tertiary_dict()
        self._build_protected_words()
        
        self.primary_dict_list = list(self.primary_dict)
        self.secondary_dict_list = list(self.secondary_dict)
        self.tertiary_dict_list = list(self.tertiary_dict)
        
        self.fuzzy_matcher = FuzzyMatcher(threshold=75)
        
    
    def _build_leet_map(self) -> None:
        self.leet_map = {}

        if self.leet_data and "character_substitutions" in self.leet_data:
            for char, subs in self.leet_data["character_substitutions"].items():
                for sub in (subs if isinstance(subs, list) else [subs]):
                    self.leet_map[sub.lower()] = char.lower()
    
    def _build_abbreviation_map(self) -> None:
        """Build mapping of abbreviations to their full forms."""
        self.abbreviation_map = {}

        if not self.abbrev_data or 'filipino_netspeak' not in self.abbrev_data:
            return
        
        ns = self.abbrev_data['filipino_netspeak']
        
        for key in ['acronyms', 'filipino_shortcuts', 'common_phrases', 'common_slang', 'filipino_english']:
            data = ns.get(key, {})
            for full_form, variations in data.items():
                full_lower = full_form.lower()
                if isinstance(variations, list):
                    for var in variations:
                        if isinstance(var, str):
                            self.abbreviation_map[var.lower()] = full_lower
                elif isinstance(variations, str):
                    self.abbreviation_map[variations.lower()] = full_lower
    
    def _build_morpho_corrections_map(self) -> None:
        self.morpho_corrections = {}
        
        if not self.morph_corrections_data:
            return
        
        for correct_form, incorrect_forms in self.morph_corrections_data.items():
            if isinstance(incorrect_forms, list):
                for incorrect in incorrect_forms:
                    self.morpho_corrections[incorrect.lower()] = correct_form.lower()
            else:
                self.morpho_corrections[str(incorrect_forms).lower()] = correct_form.lower()
    
    def _build_primary_dict(self) -> None:
        self.primary_dict = set()
        self.primary_dict.update(self.abbreviation_map.values())
        
        if isinstance(self.leet_data, dict):
            leet_examples = self.leet_data.get("filipinish_leet_examples", {})
            self.primary_dict.update(leet_examples.keys())
        
        self.primary_dict.update(self.morpho_corrections.values())
    
    def _build_secondary_dict(self) -> None:
        self.secondary_dict = set()
        
        try:
            filipino_words = get_filipino_words()
            if isinstance(filipino_words, (list, set)):
                self.secondary_dict.update(filipino_words)
        except Exception as e:
            print(f"[WARNING] Failed to load Filipino words: {e}")
    
    def _build_tertiary_dict(self) -> None:
        self.tertiary_dict = set()
        
        try:
            english_words = get_english_words()
            if isinstance(english_words, (list, set)):
                self.tertiary_dict.update(english_words)
        except Exception as e:
            print(f"[WARNING] Failed to load English words: {e}")
    
    def _build_protected_words(self) -> None:
        self.protected_words = set()
        
        if not self.protected_data:
            return
        
        categories = self.protected_data.get('categories', {})
        for category_name, category_data in categories.items():
            if isinstance(category_data, dict):
                for subcategory_name, words in category_data.items():
                    if isinstance(words, list):
                        self.protected_words.update(w.lower() for w in words)
            elif isinstance(category_data, list):
                self.protected_words.update(w.lower() for w in category_data)
        
        for key, value in self.protected_data.items():
            if key != 'categories' and isinstance(value, list):
                self.protected_words.update(w.lower() for w in value)
        
        special_cases = self.protected_data.get('special_cases', {})
        if 'words' in special_cases:
            self.protected_words.update(w.lower() for w in special_cases['words'])
    
    def _is_protected_word(self, word: str) -> bool:
        return word.lower() in self.protected_words
    
    def _reverse_leetspeak(self, token: str) -> str:
        return "".join(self.leet_map.get(c, c) for c in token)
    
    def _normalize_duplication(self, token: str) -> str:
        """Normalize repeated characters (reduce 3+ consecutive chars to 1)."""
        if len(token) < 2:
            return token
        
        output = []
        last_char = None
        consecutive_count = 0
        
        for char in token:
            if char == last_char:
                consecutive_count += 1
            else:
                consecutive_count = 1
            
            if consecutive_count <= 1:
                output.append(char)
            
            last_char = char
        
        return "".join(output)
    
    def _try_vowel_insertion(self, token: str) -> list:
        """Try inserting vowels at each position and return valid candidates."""
        vowels = 'aeiou'
        candidates = []
        
        for i in range(len(token) + 1):
            for vowel in vowels:
                candidate = token[:i] + vowel + token[i:]
                if candidate in self.primary_dict or candidate in self.secondary_dict:
                    candidates.append(candidate)
        
        return candidates
    
    
    def deobfuscate(self, token: str, use_fuzzy: bool = True, signals: dict = None) -> str:
        """
        Deobfuscate a single token based on detected signals.
        
        Args:
            token: The token to deobfuscate
            use_fuzzy: Whether to use fuzzy matching as fallback
            signals: Detected obfuscation signals from DetectionAutomata
            
        Returns:
            Deobfuscated token or original if no correction found
        """
        if not token:
            return token
        
        signals = signals or {}
        
        # Extract prefix/suffix (punctuation, brackets, etc.)
        match = re.match(r"^([(\[{]*)([\w@$|€]+)([!?.,;:)\]}]*)$", token)
        if not match:
            return token
        
        prefix, core_word, suffix = match.groups()
        
        if not core_word:
            return token
        
        core_lower = core_word.lower()
        
        # Protected words never change
        if self._is_protected_word(core_lower):
            return token
        
        # STEP 1: Check abbreviation map (exact match - highest confidence)
        if core_lower in self.abbreviation_map:
            return prefix + self.abbreviation_map[core_lower] + suffix
        
        # STEP 2: Check if already valid word in any dictionary
        if core_lower in self.primary_dict or core_lower in self.secondary_dict or core_lower in self.tertiary_dict:
            return prefix + core_lower + suffix
        
        # STEP 3: Apply ALL transformations based on detected signals
        # Order: most destructive first, validate after each transformation
        transformed = core_lower
        
        # Morphological corrections (most specific)
        if signals.get('morphology') and transformed in self.morpho_corrections:
            transformed = self.morpho_corrections[transformed]
            if self._is_valid_word(transformed):
                return prefix + transformed + suffix
        
        # Leetspeak (obvious visual substitutions)
        if signals.get('leetspeak'):
            transformed = self._reverse_leetspeak(transformed)
            if self._is_valid_word(transformed):
                return prefix + transformed + suffix
        
        # Character duplication (spacing issues)
        if signals.get('char_duplication'):
            transformed = self._normalize_duplication(transformed)
            if self._is_valid_word(transformed):
                return prefix + transformed + suffix
        
        # Vowel omission (requires guessing - last resort)
        if signals.get('vowel_omission'):
            vowel_candidates = self._try_vowel_insertion(transformed)
            if vowel_candidates:
                transformed = vowel_candidates[0]
                if self._is_valid_word(transformed):
                    return prefix + transformed + suffix
        
        # STEP 4: Final validation after all transformations
        if self._is_valid_word(transformed):
            return prefix + transformed + suffix
        
        # STEP 5: Fall back to fuzzy matching
        if use_fuzzy and len(transformed) >= 3 and any(signals.values()):
            fuzzy_match = self.fuzzy_matcher.get_best_match(transformed, self.primary_dict_list)
            if fuzzy_match and fuzzy_match.get('confidence', 0) >= 0.75:
                return prefix + fuzzy_match['word'] + suffix
            
            fuzzy_match = self.fuzzy_matcher.get_best_match(transformed, self.secondary_dict_list)
            if fuzzy_match and fuzzy_match.get('confidence', 0) >= 0.75:
                return prefix + fuzzy_match['word'] + suffix
        
        # STEP 6: Return transformed or original
        if transformed != core_lower:
            return prefix + transformed + suffix
        
        return token
    
    def _is_valid_word(self, word: str) -> bool:
        """Check if word exists in any dictionary."""
        return (
            word in self.primary_dict or
            word in self.secondary_dict or
            word in self.tertiary_dict
        )
    
    def deobfuscate_text(self, text: str, use_fuzzy: bool = True) -> str:
        """
        Deobfuscate entire text by tokenizing and deobfuscating each token.
        
        Args:
            text: Input text
            use_fuzzy: Whether to use fuzzy matching
            
        Returns:
            Deobfuscated text
        """
        from .preprocessing_service import word_tokenize, normalize_input
        
        if not text:
            return text
        
        normalized = normalize_input(text)
        tokens = word_tokenize(normalized)
        deobfuscated_tokens = [self.deobfuscate(token, use_fuzzy=use_fuzzy) for token in tokens]
        
        return " ".join(deobfuscated_tokens)