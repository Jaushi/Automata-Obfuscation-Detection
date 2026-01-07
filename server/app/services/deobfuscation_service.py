from .dictionary_service import cached_dictionaries, get_filipino_words, get_english_words
from .fuzzy_matching_service import FuzzyMatcher
import re

class DeobfuscationService:  
    def __init__(self):
        self.vowels = "aeiou"
        self.consonants = "bcdfghjklmnpqrstvwxyz"
        
        leet_obj = cached_dictionaries.get('leetspeak_map')
        self.leet_data = leet_obj.data if leet_obj else {}
        
        abbrev_obj = cached_dictionaries.get('netspeak_patterns')
        self.abbrev_data = abbrev_obj.data if abbrev_obj else {}
        
        protected_obj = cached_dictionaries.get('english_protected_words')
        self.protected_data = protected_obj.data if protected_obj else {}
        
        morph_obj = cached_dictionaries.get('morphology_patterns')
        morph_data = morph_obj.data if morph_obj else {}
        self.morph_corrections_data = morph_data.get('morphological_corrections', {})
        
        # Load affix data for dynamic morphology handling
        affixes = morph_data.get('affixes', {})
        self.prefixes = list(affixes.get('prefixes', []))
        self.suffixes = list(affixes.get('suffixes', []))
        self.min_root_length = morph_data.get('validation_rules', {}).get('min_root_after_prefix', 2)
        
        self._build_leet_map()
        self._build_netspeak_map()
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
    
    def _build_netspeak_map(self) -> None:
        """Build mapping of netspeaks to their full forms."""
        self.netspeak_map = {}
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
                            self.netspeak_map[var.lower()] = full_lower
                elif isinstance(variations, str):
                    self.netspeak_map[variations.lower()] = full_lower
    
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
        self.primary_dict.update(self.netspeak_map.values())
        if isinstance(self.leet_data, dict):
            leet_examples = self.leet_data.get("filipino_leet_examples", {})
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
        """Simply replace leet characters with their mapped values."""
        leet_map = {}
        if self.leet_data and 'character_substitutions' in self.leet_data:
            for char, substitutions in self.leet_data['character_substitutions'].items():
                subs_list = substitutions if isinstance(substitutions, list) else [substitutions]
                for sub in subs_list:
                    leet_map[sub.lower()] = char.lower()
        
        reversed_token = "".join(leet_map.get(c.lower(), c.lower()) for c in token)
        return reversed_token if self._is_valid_word(reversed_token) else reversed_token
    
    def _normalize_duplication(self, token: str) -> str:
        """Normalize repeated characters (reduce 3+ consecutive chars to 2)."""
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
            
            if consecutive_count <= 2:
                output.append(char)
            
            last_char = char
        
        return "".join(output)
    
    def _try_vowel_insertion(self, token: str) -> list:
        """Try fuzzy matching by inserting vowels between consonants."""
        candidates = []
        variations = {token}
        
        for i in range(len(token) - 1):
            curr_is_consonant = token[i].lower() not in self.vowels
            next_is_consonant = token[i + 1].lower() not in self.vowels
            
            if curr_is_consonant and next_is_consonant:
                for vowel in "aeiou":
                    variant = token[:i + 1] + vowel + token[i + 1:]
                    variations.add(variant)
        
        for dict_list in [self.primary_dict_list, self.secondary_dict_list, self.tertiary_dict_list]:
            for variant in sorted(variations):
                fuzzy_match = self.fuzzy_matcher.get_best_match(variant, dict_list)
                if fuzzy_match and fuzzy_match.get('confidence', 0) >= 0.75:
                    candidates.append(fuzzy_match['word'])
                    break
            if candidates:
                break
        
        return candidates
    
    def _identify_affixes(self, word: str) -> dict:
        """Identify which affixes are present and extract the root."""
        word_lower = word.lower()
        
        # Try circumfix first
        for circumfix_name, (prefix, suffix) in self.circumfixes.items():
            if word_lower.startswith(prefix) and word_lower.endswith(suffix):
                root = word_lower[len(prefix):-len(suffix)] if suffix else word_lower[len(prefix):]
                if len(root) >= self.min_root_length:
                    return {'type': 'circumfix', 'prefix': prefix, 'suffix': suffix, 'infix': None, 'root': root}
        
        # Try prefix+suffix combination
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                if word_lower.startswith(prefix) and word_lower.endswith(suffix):
                    root = word_lower[len(prefix):-len(suffix)]
                    if len(root) >= self.min_root_length:
                        return {'type': 'prefix+suffix', 'prefix': prefix, 'suffix': suffix, 'infix': None, 'root': root}
        
        # Try prefix only
        for prefix in self.prefixes:
            if word_lower.startswith(prefix):
                root = word_lower[len(prefix):]
                if len(root) >= self.min_root_length:
                    return {'type': 'prefix', 'prefix': prefix, 'suffix': None, 'infix': None, 'root': root}
        
        # Try suffix only
        for suffix in self.suffixes:
            if word_lower.endswith(suffix):
                root = word_lower[:-len(suffix)]
                if len(root) >= self.min_root_length:
                    return {'type': 'suffix', 'prefix': None, 'suffix': suffix, 'infix': None, 'root': root}
        
        # Try infix
        for infix in self.infixes:
            for i in range(1, len(word_lower)):
                if word_lower[i:i+len(infix)] == infix and word_lower[i-1] in self.consonants:
                    root = word_lower[:i] + word_lower[i+len(infix):]
                    if len(root) >= self.min_root_length:
                        return {'type': 'infix', 'prefix': None, 'suffix': None, 'infix': infix, 'infix_position': i, 'root': root}
        
        return None
    
    def _is_english_root(self, root: str) -> bool:
        """Check if root is an English word."""
        return root.lower() in self.tertiary_dict
    
    def _reconstruct_with_affixes(self, clean_root: str, affix_info: dict) -> str:
        """Reconstruct word with affixes, applying hyphen rules for English roots."""
        is_english = self._is_english_root(clean_root)
        hyphen = '-' if is_english else ''
        
        prefix = affix_info.get('prefix')
        suffix = affix_info.get('suffix')
        infix = affix_info.get('infix')
        
        if affix_info['type'] == 'prefix':
            return f"{prefix}{hyphen}{clean_root}" if is_english else f"{prefix}{clean_root}"
        elif affix_info['type'] == 'suffix':
            return f"{clean_root}{hyphen}{suffix}" if is_english else f"{clean_root}{suffix}"
        elif affix_info['type'] == 'prefix+suffix':
            result = f"{prefix}{hyphen}{clean_root}" if is_english else f"{prefix}{clean_root}"
            result += f"{hyphen}{suffix}" if is_english else suffix
            return result
        elif affix_info['type'] == 'circumfix':
            result = f"{prefix}{hyphen}" if is_english else prefix
            result += clean_root
            result += f"{hyphen}{suffix}" if (suffix and is_english) else (suffix or '')
            return result
        elif affix_info['type'] == 'infix':
            pos = affix_info['infix_position']
            return clean_root[:pos] + infix + clean_root[pos:] if pos <= len(clean_root) else clean_root + infix
        
        return clean_root
    
    def _reverse_single_word_obfuscation(self, word: str, signals: dict = None) -> str:
        """Reverse obfuscation on a word (used for roots in morphological words)."""
        signals = signals or {}
        transformed = word.lower()
        
        if signals.get('leetspeak'):
            transformed = self._reverse_leetspeak(transformed)
        
        if signals.get('char_duplication'):
            transformed = self._normalize_duplication(transformed)
        
        if signals.get('vowel_omission'):
            candidates = self._try_vowel_insertion(transformed)
            if candidates:
                transformed = candidates[0]
        
        return transformed if self._is_valid_word(transformed) else word
    
    def _reverse_morphological_obfuscation(self, word: str, signals: dict = None) -> str:
        """Handle morphological words by extracting root, cleaning it, and reattaching affixes."""
        signals = signals or {}
        word_lower = word.lower()
        
        if word_lower in self.morph_corrections:
            return self.morph_corrections[word_lower]
        
        affix_info = self._identify_affixes(word_lower)
        if not affix_info:
            return word
        
        root = affix_info['root']
        clean_root = self._reverse_single_word_obfuscation(root, signals)
        
        return self._reconstruct_with_affixes(clean_root, affix_info)
    
    def deobfuscate(self, token: str, use_fuzzy: bool = True, signals: dict = None) -> str:
        """Deobfuscate a single token based on detected signals."""
        if not token:
            return token
        
        signals = signals or {}
    
        match = re.match(r"^([(\[{]*)([\w@$|€*]+)([\?\!.,;:)\]}]*)$", token)
        if not match:
            return token
        
        prefix, core_word, suffix = match.groups()
        core_lower = core_word.lower()
        
        if self._is_protected_word(core_lower):
            return token
        
        if core_lower in self.primary_dict or core_lower in self.secondary_dict or core_lower in self.tertiary_dict:
            return prefix + core_lower + suffix
        
        # STEP 1: Check netspeak FIRST (before any other transformations)
        if signals.get('netspeak') and core_lower in self.netspeak_map:
            return prefix + self.netspeak_map[core_lower] + suffix
        
        # STEP 2: Apply other transformations
        transformed = core_lower
        
        if signals.get('morphology'):
            transformed = self._reverse_morphological_obfuscation(transformed, signals)
        
        if signals.get('leetspeak'):
            transformed = self._reverse_leetspeak(transformed)
        
        if signals.get('char_duplication'):
            transformed = self._normalize_duplication(transformed)
        
        if signals.get('vowel_omission'):
            candidates = self._try_vowel_insertion(transformed)
            if candidates:
                transformed = candidates[0]
        
        # STEP 3: Valid word check
        if self._is_valid_word(transformed):
            return prefix + transformed + suffix
        
        # STEP 4: Fuzzy matching (last resort, 0.90+ only)
        if use_fuzzy and len(transformed) >= 4 and any(signals.values()) and not signals.get('netspeak'):
            for dict_list in [self.primary_dict_list, self.secondary_dict_list, self.tertiary_dict_list]:
                match = self.fuzzy_matcher.get_best_match(transformed, dict_list)
                if match and match.get('confidence', 0) >= 0.90:
                    return prefix + match['word'] + suffix
        
        # STEP 5: Return transformed or original
        return prefix + transformed + suffix if transformed != core_lower else token
    
    def _is_valid_word(self, word: str) -> bool:
        """Check if word exists in any dictionary."""
        return (
            word in self.primary_dict or
            word in self.secondary_dict or
            word in self.tertiary_dict
        )
    
    def deobfuscate_text(self, text: str, use_fuzzy: bool = True) -> str:
        """Deobfuscate entire text by tokenizing, detecting signals, and deobfuscating each token."""
        from .preprocessing_service import word_tokenize_preserve_hyphens, normalize_input, _join
        
        if not text:
            return text
        
        normalized = normalize_input(text)
        tokens = word_tokenize_preserve_hyphens(normalized)
        deobfuscated_tokens = []
        
        for token in tokens:
            # Detect signals for this token
            signals = self._detect_signals(token)
            # Deobfuscate with detected signals
            deobfuscated = self.deobfuscate(token, use_fuzzy=use_fuzzy, signals=signals)
            deobfuscated_tokens.append(deobfuscated)
        
        # Use your existing _join() function that already handles punctuation spacing
        return _join(deobfuscated_tokens)