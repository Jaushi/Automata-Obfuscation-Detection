import re
from .dictionary_service import cached_dictionaries, get_filipino_words, get_english_words
from .fuzzy_matching_service import FuzzyMatcher

class DeobfuscationService:  
    def __init__(self):
        leet_obj = cached_dictionaries.get('leetspeak_map')
        self.leet_data = leet_obj.data if leet_obj else {}
        
        net_obj = cached_dictionaries.get('netspeak_patterns')
        self.netspeak_data = net_obj.data if net_obj else {}
        
        protected_obj = cached_dictionaries.get('english_protected_words')
        self.protected_data = protected_obj.data if protected_obj else {}
        
        self._build_leet_map()
        self._build_netspeak_map()
        self._build_primary_dict()
        self._build_secondary_dict()
        self._build_tertiary_dict()
        self._build_protected_words()
        
        self.primary_dict_list = list(self.primary_dict)
        self.secondary_dict_list = list(self.secondary_dict)
        self.tertiary_dict_list = list(self.tertiary_dict)
        
        self.fuzzy_matcher = FuzzyMatcher(threshold=75)
        
        self._log_initialization()
    
    def _build_leet_map(self) -> None:
        self.leet_map = {}
        if self.leet_data and "character_substitutions" in self.leet_data:
            for char, subs in self.leet_data["character_substitutions"].items():
                for sub in (subs if isinstance(subs, list) else [subs]):
                    self.leet_map[sub.lower()] = char.lower()
    
    def _build_netspeak_map(self) -> None:
        self.netspeak_map = {}
        
        if not self.netspeak_data or 'filipino_netspeak' not in self.netspeak_data:
            return
        
        ns = self.netspeak_data['filipino_netspeak']
        
        acronyms = ns.get('acronyms', {})
        for full_form, abbrevs in acronyms.items():
            full_lower = full_form.lower()
            if isinstance(abbrevs, list):
                for abbrev in abbrevs:
                    self.netspeak_map[abbrev.lower()] = full_lower
            elif isinstance(abbrevs, str):
                self.netspeak_map[abbrevs.lower()] = full_lower
        
        shortcuts = ns.get('filipino_shortcuts', {})
        for full_word, variations in shortcuts.items():
            full_lower = full_word.lower()
            if isinstance(variations, list):
                for var in variations:
                    self.netspeak_map[var.lower()] = full_lower
            elif isinstance(variations, str):
                self.netspeak_map[variations.lower()] = full_lower
        
        common_phrases = ns.get('common_phrases', {})
        for standard_phrase, variations in common_phrases.items():
            standard_lower = standard_phrase.lower()
            if isinstance(variations, list):
                for var in variations:
                    self.netspeak_map[var.lower()] = standard_lower
            elif isinstance(variations, str):
                self.netspeak_map[variations.lower()] = standard_lower
        
        slang = ns.get('common_slang', {})
        for standard_form, variations in slang.items():
            standard_lower = standard_form.lower()
            if isinstance(variations, list):
                for var in variations:
                    if isinstance(var, str):
                        self.netspeak_map[var.lower()] = standard_lower
            elif isinstance(variations, str):
                self.netspeak_map[variations.lower()] = standard_lower
        
        filipino_english = ns.get('filipino_english', {})
        for standard_form, variations in filipino_english.items():
            standard_lower = standard_form.lower()
            if isinstance(variations, list):
                for var in variations:
                    if isinstance(var, str):
                        self.netspeak_map[var.lower()] = standard_lower
            elif isinstance(variations, str):
                self.netspeak_map[variations.lower()] = standard_lower
    
    def _build_primary_dict(self) -> None:
        self.primary_dict = set()
        self.primary_dict.update(self.netspeak_map.values())
        
        if isinstance(self.leet_data, dict):
            leet_examples = self.leet_data.get("filipino_leet_examples", {})
            self.primary_dict.update(leet_examples.keys())
    
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
    
    def _log_initialization(self) -> None:
        print(f"[DEBUG] DeobfuscationService loaded:")
        print(f"  - {len(self.netspeak_map)} netspeak mappings")
        print(f"  - {len(self.primary_dict)} words in PRIMARY dictionary")
        print(f"  - {len(self.secondary_dict)} words in SECONDARY dictionary (Filipino)")
        print(f"  - {len(self.tertiary_dict)} words in TERTIARY dictionary (English)")
        print(f"  - {len(self.protected_words)} protected English words")
        print(f"  - Fuzzy matcher threshold: {self.fuzzy_matcher.threshold}")
    
    def _is_protected_word(self, word: str) -> bool:
        return word.lower() in self.protected_words
    
    def _reverse_leetspeak(self, token: str) -> str:
        return "".join(self.leet_map.get(c, c) for c in token)
    
    def _normalize_duplication(self, token: str) -> str:
        common_doubles = set("lsmnor")
        
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
            
            max_allowed = 2 if char in common_doubles else 1
            
            if consecutive_count <= max_allowed:
                output.append(char)
            
            last_char = char
        
        return "".join(output)
    
    def _has_obvious_obfuscation(self, token: str) -> bool:
        token_lower = token.lower()
        leet_chars = ['0', '1', '3', '4', '5', '7', '8', '@', '$']
        has_leet = any(c in token_lower for c in leet_chars)
        
        has_excessive_dup = False
        for i in range(len(token_lower) - 2):
            if token_lower[i] == token_lower[i+1] == token_lower[i+2]:
                if token_lower[i] not in 'ls':
                    has_excessive_dup = True
                    break
        
        return has_leet or has_excessive_dup
    
    def _try_vowel_insertion(self, token: str) -> list:
        """Try inserting vowels at each position to find valid words"""
        vowels = 'aeiou'
        candidates = []
        
        for i in range(len(token) + 1):
            for vowel in vowels:
                candidate = token[:i] + vowel + token[i:]
                if candidate in self.primary_dict or candidate in self.secondary_dict:
                    candidates.append(candidate)
        
        return candidates
    
    def deobfuscate(self, token: str, use_fuzzy: bool = True, obf_type: str = 'unknown') -> str:
        if not token:
            return token
        
        match = re.match(r"^([(\[{]*)([\w@$|€]+)([!?.,;:)\]}]*)$", token)
        if not match:
            return token
        
        prefix, core_word, suffix = match.groups()
        
        if not core_word:
            return token
        
        core_lower = core_word.lower()
        
        # DEBUG: Check specific problematic words
        if core_lower in ['or', 'of', 'in', 'at', 'pinas']:
            print(f"[DEBUG] Token '{core_lower}':")
            print(f"  - In primary? {core_lower in self.primary_dict}")
            print(f"  - In secondary? {core_lower in self.secondary_dict}")
            print(f"  - In tertiary? {core_lower in self.tertiary_dict}")
            print(f"  - Is protected? {self._is_protected_word(core_lower)}")
        
        # GUARD: Protected words never change
        if self._is_protected_word(core_lower):
            return token
        
        # Step 1: Netspeak lookup
        if core_lower in self.netspeak_map:
            return prefix + self.netspeak_map[core_lower] + suffix
        
        # Step 2: Check primary and secondary dictionaries
        if core_lower in self.primary_dict or core_lower in self.secondary_dict:
            return prefix + core_lower + suffix
        
        # Step 2.5: Check tertiary (English) - accept ALL English words
        # This prevents "or" → "oro", "of" → wrong match, etc.
        if core_lower in self.tertiary_dict:
            return prefix + core_lower + suffix
        
        # Step 3: Apply transformations
        transformed = core_lower
        
        if obf_type in ['leetspeak', 'unknown']:
            transformed = self._reverse_leetspeak(transformed)
        
        if obf_type in ['character_duplication', 'unknown']:
            transformed = self._normalize_duplication(transformed)
        
        # Step 3.5: Try vowel insertion (for vowel omission like ganya -> ganyan)
        if obf_type in ['vowel_omission', 'morphology', 'unknown']:
            vowel_candidates = self._try_vowel_insertion(transformed)
            if vowel_candidates:
                print(f"[DEBUG] Vowel insertion: '{transformed}' -> '{vowel_candidates[0]}'")
                return prefix + vowel_candidates[0] + suffix
        
        # Step 4: Check if transformation created valid word
        if transformed != core_lower:
            if transformed in self.netspeak_map:
                return prefix + self.netspeak_map[transformed] + suffix
            
            if transformed in self.primary_dict or transformed in self.secondary_dict:
                return prefix + transformed + suffix
        
        # Step 5: Fuzzy matching
        # Only try fuzzy if word is NOT already valid somewhere
        is_already_valid = (
            transformed in self.primary_dict or 
            transformed in self.secondary_dict or
            transformed in self.tertiary_dict  # Accept any English word, not just protected
        )
        
        if is_already_valid:
            return prefix + transformed + suffix
        
        # Trigger fuzzy if:
        # 1. Has obvious obfuscation (leetspeak/duplication), OR
        # 2. Short word (3-6 chars) AND not in any dictionary
        is_short_unknown = (3 <= len(transformed) <= 6)
        
        should_try_fuzzy = (
            use_fuzzy and 
            len(transformed) >= 3 and
            (self._has_obvious_obfuscation(core_lower) or is_short_unknown)
        )
        
        if should_try_fuzzy:
            fuzzy_match = self.fuzzy_matcher.get_best_match(transformed, self.primary_dict_list)
            if fuzzy_match and fuzzy_match.get('confidence', 0) >= 0.75:
                return prefix + fuzzy_match['word'] + suffix
            
            fuzzy_match = self.fuzzy_matcher.get_best_match(transformed, self.secondary_dict_list)
            if fuzzy_match and fuzzy_match.get('confidence', 0) >= 0.75:
                return prefix + fuzzy_match['word'] + suffix
        
        # Return transformed or original
        if transformed != core_lower:
            return prefix + transformed + suffix
        
        return token
    
    def deobfuscate_text(self, text: str, use_fuzzy: bool = True) -> str:
        from .preprocessing_service import word_tokenize, normalize_input
        
        if not text:
            return text
        
        normalized = normalize_input(text)
        tokens = word_tokenize(normalized)
        deobfuscated_tokens = [self.deobfuscate(token, use_fuzzy=use_fuzzy) for token in tokens]
        
        return " ".join(deobfuscated_tokens)  