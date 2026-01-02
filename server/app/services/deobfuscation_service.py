import re
from .dictionary_service import cached_dictionaries, get_filipino_words
from .fuzzy_matching_service import FuzzyMatcher


class DeobfuscationService:  
    def __init__(self):
        leet_obj = cached_dictionaries.get('leetspeak_map')
        self.leet_data = leet_obj.data if leet_obj else {}
        
        net_obj = cached_dictionaries.get('netspeak_patterns')
        self.netspeak_data = net_obj.data if net_obj else {}
        
        # Load English protected words dictionary
        protected_obj = cached_dictionaries.get('english_protected_words')
        self.protected_data = protected_obj.data if protected_obj else {}
        
        self._build_leet_map()
        self._build_netspeak_map()
        self._build_primary_dict()
        self._build_secondary_dict()
        self._build_protected_words()  # Load protected English words
        
        self.primary_dict_list = list(self.primary_dict)
        self.secondary_dict_list = list(self.secondary_dict)
        
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
        
        # Process filipino_shortcuts
        shortcuts = ns.get('filipino_shortcuts', {})
        for root, abbrevs in shortcuts.items():
            if isinstance(abbrevs, list):
                for abbrev in abbrevs:
                    self.netspeak_map[abbrev.lower()] = root.lower()
            elif isinstance(abbrevs, str):
                self.netspeak_map[abbrevs.lower()] = root.lower()
        
        # Process acronyms
        acronyms = ns.get('acronyms', {})
        for abbrev, full in acronyms.items():
            if isinstance(full, list):
                if full:
                    self.netspeak_map[abbrev.lower()] = full[0].lower()
            elif isinstance(full, str):
                self.netspeak_map[abbrev.lower()] = full.lower()
        
        # Process common_slang
        slang = ns.get('common_slang', {})
        for meaning, slang_terms in slang.items():
            if isinstance(slang_terms, list):
                for term in slang_terms:
                    if isinstance(term, str):
                        self.netspeak_map[term.lower()] = meaning.lower()
            elif isinstance(slang_terms, str):
                self.netspeak_map[slang_terms.lower()] = meaning.lower()
        
        # Process filipino_english (NEW - this was missing!)
        filipino_english = ns.get('filipino_english', {})
        for meaning, english_terms in filipino_english.items():
            if isinstance(english_terms, list):
                for term in english_terms:
                    if isinstance(term, str):
                        self.netspeak_map[term.lower()] = meaning.lower()
            elif isinstance(english_terms, str):
                self.netspeak_map[english_terms.lower()] = meaning.lower()
        
        # Process leetspeak examples
        leet_examples = self.leet_data.get("filipino_leet_examples", {})
        for root, variations in leet_examples.items():
            if isinstance(variations, list):
                for var in variations:
                    self.netspeak_map[var.lower()] = root.lower()
    
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
    
    def _build_protected_words(self) -> None:
        """Load protected English words from dictionary file"""
        self.protected_words = set()
        
        if not self.protected_data:
            print("[WARNING] No protected words dictionary loaded")
            return
        
        # Extract words from categories
        categories = self.protected_data.get('categories', {})
        
        for category_name, category_data in categories.items():
            if isinstance(category_data, dict):
                # Handle nested structure (e.g., function_words with subcategories)
                for subcategory_name, words in category_data.items():
                    if isinstance(words, list):
                        self.protected_words.update(w.lower() for w in words)
            elif isinstance(category_data, list):
                # Handle flat list
                self.protected_words.update(w.lower() for w in category_data)
        
        # Add special cases
        special_cases = self.protected_data.get('special_cases', {})
        if 'words' in special_cases:
            self.protected_words.update(w.lower() for w in special_cases['words'])
    
    def _log_initialization(self) -> None:
        print(f"[DEBUG] DeobfuscationService loaded:")
        print(f"  - {len(self.netspeak_map)} netspeak mappings")
        print(f"  - {len(self.primary_dict)} words in PRIMARY dictionary")
        print(f"  - {len(self.secondary_dict)} words in SECONDARY dictionary (Tagalog + particles)")
        print(f"  - {len(self.protected_words)} protected English words")
    
    def _is_protected_word(self, word: str) -> bool:
        """Check if word is protected from deobfuscation"""
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
        """
        Check if token has obvious obfuscation markers.
        Returns True if the token clearly needs deobfuscation.
        """
        token_lower = token.lower()
        
        # Check for leetspeak characters
        has_leet = any(c in token_lower for c in ['0', '1', '3', '4', '5', '7', '8', '@', '$'])
        
        # Check for excessive duplication (3+ same chars in a row)
        has_excessive_dup = False
        for i in range(len(token_lower) - 2):
            if token_lower[i] == token_lower[i+1] == token_lower[i+2]:
                if token_lower[i] not in 'ls':
                    has_excessive_dup = True
                    break
        
        return has_leet or has_excessive_dup
    
    def deobfuscate(self, token: str, use_fuzzy: bool = True) -> str:
        if not token:
            return token
        
        # Extract and preserve punctuation
        match = re.match(r"^([(\[{]*)([\w@$|€]+)([!?.,;:)\]}]*)$", token)
        if not match:
            return token
        
        prefix, core_word, suffix = match.groups()
        
        if not core_word:
            return token
        
        core_lower = core_word.lower()
        
        # GUARD 1: Protect words from the protected dictionary
        if self._is_protected_word(core_lower):
            return token
        
        # Step 1: Direct netspeak lookup
        if core_lower in self.netspeak_map:
            return prefix + self.netspeak_map[core_lower] + suffix
        
        # Step 2: Check if word is already valid
        if core_lower in self.primary_dict or core_lower in self.secondary_dict:
            return prefix + core_lower + suffix
        
        # GUARD 2: Only apply transformations if there's obvious obfuscation
        if not self._has_obvious_obfuscation(core_lower):
            # No obfuscation detected - leave it alone if it looks normal
            if re.fullmatch(r'[a-z]{2,}', core_lower):
                return token
        
        # Step 3: Apply transformations (reverse leet + normalize duplication)
        transformed = self._reverse_leetspeak(core_lower)
        transformed = self._normalize_duplication(transformed)
        
        # Step 4: Check if transformation created a known word
        if transformed != core_lower:
            if transformed in self.netspeak_map:
                return prefix + self.netspeak_map[transformed] + suffix
            
            if transformed in self.primary_dict or transformed in self.secondary_dict:
                return prefix + transformed + suffix
        
        # Step 5: Fuzzy matching as last resort
        if use_fuzzy and len(transformed) >= 3 and transformed != core_lower:
            if transformed not in self.primary_dict and transformed not in self.secondary_dict:
                # Try PRIMARY dictionary first
                fuzzy_match = self.fuzzy_matcher.get_best_match(
                    transformed, 
                    self.primary_dict_list
                )
                if fuzzy_match and fuzzy_match.get('confidence', 0) >= 0.85:
                    return prefix + fuzzy_match['word'] + suffix
                
                # Fall back to SECONDARY dictionary
                fuzzy_match = self.fuzzy_matcher.get_best_match(
                    transformed, 
                    self.secondary_dict_list
                )
                if fuzzy_match and fuzzy_match.get('confidence', 0) >= 0.80:
                    return prefix + fuzzy_match['word'] + suffix
        
        # No match found - return transformed version if different
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