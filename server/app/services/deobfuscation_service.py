import re
from .dictionary_service import cached_dictionaries, get_filipino_words
from .fuzzy_matching_service import FuzzyMatcher




class DeobfuscationService:  
    def __init__(self):


        # Load dictionaries
        leet_obj = cached_dictionaries.get('leetspeak_map')
        self.leet_data = leet_obj.data if leet_obj else {}
       
        net_obj = cached_dictionaries.get('netspeak_patterns')
        self.netspeak_data = net_obj.data if net_obj else {}
       
        # Build leetspeak transition map
        self._build_leet_map()
       
        # Build netspeak expansion map
        self._build_netspeak_map()
       
        # Build PRIMARY dictionary (netspeak + leet expansions)
        self._build_primary_dict()
       
        # Build SECONDARY dictionary (Tagalog words)
        self._build_secondary_dict()
       
        # Convert to lists for fuzzy matcher
        self.primary_dict_list = list(self.primary_dict)
        self.secondary_dict_list = list(self.secondary_dict)
       
        self.fuzzy_matcher = FuzzyMatcher(threshold=75)
       
        self._log_initialization()
   
    def _build_leet_map(self) -> None:
        # Build leetspeak character substitution map
        self.leet_map = {}
        if self.leet_data and "character_substitutions" in self.leet_data:
            for char, subs in self.leet_data["character_substitutions"].items():
                for sub in (subs if isinstance(subs, list) else [subs]):
                    self.leet_map[sub.lower()] = char.lower()
   
    def _build_netspeak_map(self) -> None:
        # Build netspeak abbreviation expansion map
        self.netspeak_map = {}
       
        if not self.netspeak_data or 'filipino_netspeak' not in self.netspeak_data:
            return
       
        ns = self.netspeak_data['filipino_netspeak']
       
        # Add shortcuts (abbreviations to root words)
        shortcuts = ns.get('filipino_shortcuts', {})
        for root, abbrevs in shortcuts.items():
            if isinstance(abbrevs, list):
                for abbrev in abbrevs:
                    self.netspeak_map[abbrev.lower()] = root.lower()
            elif isinstance(abbrevs, str):
                self.netspeak_map[abbrevs.lower()] = root.lower()
       
        # Add acronyms
        acronyms = ns.get('acronyms', {})
        for abbrev, full in acronyms.items():
            if isinstance(full, list):
                if full:
                    self.netspeak_map[abbrev.lower()] = full[0].lower()
            elif isinstance(full, str):
                self.netspeak_map[abbrev.lower()] = full.lower()
       
        # Add common slang
        slang = ns.get('common_slang', {})
        for meaning, slang_terms in slang.items():
            if isinstance(slang_terms, list):
                for term in slang_terms:
                    if isinstance(term, str):
                        self.netspeak_map[term.lower()] = meaning.lower()
            elif isinstance(slang_terms, str):
                self.netspeak_map[slang_terms.lower()] = meaning.lower()
       
        # Add leet examples
        leet_examples = self.leet_data.get("filipino_leet_examples", {})
        for root, variations in leet_examples.items():
            if isinstance(variations, list):
                for var in variations:
                    self.netspeak_map[var.lower()] = root.lower()
   
    def _build_primary_dict(self) -> None:
        # Build primary dictionary (high priority: netspeak + leet expansions)
        self.primary_dict = set()
        self.primary_dict.update(self.netspeak_map.values())
       
        # Add leet example roots
        if isinstance(self.leet_data, dict):
            leet_examples = self.leet_data.get("filipino_leet_examples", {})
            self.primary_dict.update(leet_examples.keys())
   
    def _build_secondary_dict(self) -> None:
        # Build secondary dictionary (Tagalog words + Filipino particles)
        self.secondary_dict = set()
       
        # Load Tagalog dictionary
        try:
            filipino_words = get_filipino_words()
            if isinstance(filipino_words, (list, set)):
                self.secondary_dict.update(filipino_words)
        except Exception as e:
            print(f"[WARNING] Failed to load Filipino words: {e}")


   
    def _log_initialization(self) -> None:
        # Log initialization statistics
        print(f"[DEBUG] DeobfuscationService loaded:")
        print(f"  - {len(self.netspeak_map)} netspeak mappings")
        print(f"  - {len(self.primary_dict)} words in PRIMARY dictionary")
        print(f"  - {len(self.secondary_dict)} words in SECONDARY dictionary (Tagalog + particles)")
   
    def _is_plain_english(self, word: str) -> bool:
        return bool(re.fullmatch(r"[a-z]{3,}", word))


    def _reverse_leetspeak(self, token: str) -> str:
        # Convert leetspeak characters to normal letters
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
   
   
    def deobfuscate(self, token: str, use_fuzzy: bool = True) -> str:
        # Deobfuscate a single token with optional fuzzy matching
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
       
        # Step 1: Direct netspeak lookup
        if core_lower in self.netspeak_map:
            return prefix + self.netspeak_map[core_lower] + suffix
       
        # Step 2: Check if word is already valid (in PRIMARY or SECONDARY dict)
        if core_lower in self.primary_dict or core_lower in self.secondary_dict:
            return prefix + core_lower + suffix
       
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
        if use_fuzzy and len(transformed) >= 3:
            if transformed not in self.primary_dict and transformed not in self.secondary_dict:
                # Try PRIMARY dictionary first
                fuzzy_match = self.fuzzy_matcher.get_best_match(
                    transformed,
                    self.primary_dict_list
                )
                if fuzzy_match and fuzzy_match.get('confidence', 0) >= 0.80:
                    return prefix + fuzzy_match['word'] + suffix
               
                # Fall back to SECONDARY dictionary with lower threshold
                fuzzy_match = self.fuzzy_matcher.get_best_match(
                    transformed,
                    self.secondary_dict_list
                )
                if fuzzy_match and fuzzy_match.get('confidence', 0) >= 0.75:
                    return prefix + fuzzy_match['word'] + suffix
       
        # No match found, return transformed version
        return prefix + transformed + suffix
   
    def deobfuscate_text(self, text: str, use_fuzzy: bool = True) -> str:
        # Deobfuscate entire text
        from .preprocessing_service import word_tokenize, normalize_input
       
        if not text:
            return text
       
        normalized = normalize_input(text)
        tokens = word_tokenize(normalized)
        deobfuscated_tokens = [self.deobfuscate(token, use_fuzzy=use_fuzzy) for token in tokens]
       
        return " ".join(deobfuscated_tokens)

