from .dictionary_service import cached_dictionaries, get_filipino_words, get_english_words
from .fuzzy_matching_service import FuzzyMatcher
import re
from itertools import product


class DeobfuscationService:  
    def __init__(self):
        self.vowels = "aeiou"
        self.consonants = "bcdfghjklmnpqrstvwxyz"
        self.separators = "-._|*"
        
        # Load cached data
        self._load_cached_data()
        
        # Build lookup maps
        self._build_leet_map()
        self._build_netspeak_map()
        self._build_dictionaries()
        self._build_english_words()
        
        # Convert dicts to lists for fuzzy matching
        self.primary_dict_list = list(self.primary_dict)
        self.secondary_dict_list = list(self.secondary_dict)
        self.tertiary_dict_list = list(self.tertiary_dict)
        
        self.fuzzy_matcher = FuzzyMatcher(threshold=75)
    
    def _load_cached_data(self) -> None:
        """Load all cached dictionary data."""
        leet_obj = cached_dictionaries.get('leetspeak_map')
        self.leet_data = leet_obj.data if leet_obj else {}
        
        abbrev_obj = cached_dictionaries.get('netspeak_patterns')
        self.abbrev_data = abbrev_obj.data if abbrev_obj else {}
        
        english_obj = cached_dictionaries.get('english_words')
        self.english_words = english_obj.data if english_obj else {}
    
    def _build_leet_map(self) -> None:
        """Map leet substitutions back to original characters."""
        self.leet_map = {}
        if self.leet_data and "character_substitutions" in self.leet_data:
            for char, subs in self.leet_data["character_substitutions"].items():
                for sub in (subs if isinstance(subs, list) else [subs]):
                    self.leet_map[sub.lower()] = char.lower()
    
    def _build_netspeak_map(self) -> None:
        """Map netspeaks to their full forms."""
        self.netspeak_map = {}
        if not self.abbrev_data or 'filipino_netspeak' not in self.abbrev_data:
            return
        
        ns = self.abbrev_data['filipino_netspeak']
        for category in ['acronyms', 'filipino_shortcuts', 'common_phrases', 'common_slang', 'filipino_english']:
            for full_form, variations in ns.get(category, {}).items():
                full_lower = full_form.lower()
                var_list = variations if isinstance(variations, list) else [variations]
                for var in var_list:
                    if isinstance(var, str):
                        self.netspeak_map[var.lower()] = full_lower
    
    def _build_dictionaries(self) -> None:
        """Build primary, secondary, and tertiary word dictionaries."""
        self.primary_dict = set(self.netspeak_map.values())
        if isinstance(self.leet_data, dict):
            self.primary_dict.update(self.leet_data.get("filipino_leet_examples", {}).keys())
        
        self.secondary_dict = set()
        try:
            words = get_filipino_words()
            if isinstance(words, (list, set)):
                self.secondary_dict.update(words)
        except Exception as e:
            print(f"[WARNING] Failed to load Filipino words: {e}")
        
        self.tertiary_dict = set()
        try:
            words = get_english_words()
            if isinstance(words, (list, set)):
                self.tertiary_dict.update(words)
        except Exception as e:
            print(f"[WARNING] Failed to load English words: {e}")
    
    def _build_english_words(self) -> None:
        """Extract words that should not be modified."""
        self.english_words = set()
        if not self.english_words:
            return
        # If english_words is a dict with categories, flatten all lists
        if isinstance(self.english_words, dict):
            for v in self.english_words.values():
                if isinstance(v, list):
                    self.english_words.update(w.lower() for w in v)
                elif isinstance(v, dict):
                    for vv in v.values():
                        if isinstance(vv, list):
                            self.english_words.update(w.lower() for w in vv)
        elif isinstance(self.english_words, list):
            self.english_words.update(w.lower() for w in self.english_words)
    
    def _is_valid_word(self, word: str) -> bool:
        """Check if word exists in any dictionary."""
        return word in (self.primary_dict | self.secondary_dict | self.tertiary_dict)
    
    def _is_english_word(self, word: str) -> bool:
        """Check if word should not be modified."""
        return word.lower() in self.english_words
    
    def _reverse_leetspeak(self, token: str) -> str:
        """Replace leet characters with original letters."""
        return "".join(self.leet_map.get(c.lower(), c.lower()) for c in token)
    
    def _normalize_duplication(self, token: str) -> str:
        """Remove all duplicate consecutive characters."""
        if len(token) < 2:
            return token
        
        output = []
        consecutive_count = 0
        last_char = None
        
        for char in token:
            if char == last_char:
                consecutive_count += 1
            else:
                consecutive_count = 1
                last_char = char
            
            # Keep only the first occurrence (consecutive_count == 1)
            if consecutive_count == 1:
                output.append(char)
        
        return "".join(output)
    
    def _reverse_symbol_separation(self, token: str) -> str:
        """Remove symbol separators (k-m-u-s-t-a → kumusta)."""
        cleaned = token
        for sep in self.separators:
            cleaned = cleaned.replace(sep, "")
        return cleaned
    
    def _try_vowel_insertion(self, token: str) -> list:
        """Generate candidates by inserting vowels at consonant pairs."""
        # Find consonant pair positions
        positions = [i for i in range(len(token) - 1) 
                    if token[i] not in self.vowels and token[i+1] not in self.vowels]
        
        if not positions:
            return []
        
        # Limit to 4 positions to prevent explosion
        positions = positions[:4]
        total_combos = 5 ** len(positions)
        
        # Common Filipino vowel patterns
        common_patterns = [
            ['a'] * len(positions),
            ['u'] * len(positions),
            ['a', 'a', 'i'],
            ['u', 'a', 'i'],
            ['a', 'i', 'a'],
        ]
        
        candidates = []
        
        # Try common patterns first
        for pattern in common_patterns:
            if len(pattern) != len(positions):
                continue
            
            variant = token
            for pos_idx in range(len(positions) - 1, -1, -1):
                pos = positions[pos_idx]
                variant = variant[:pos+1] + pattern[pos_idx] + variant[pos+1:]
            
            if self._is_valid_word(variant):
                return [variant]
        
        # If too many combinations, skip brute force
        if total_combos > 1000:
            return []
        
        # Try all combinations
        for vowel_combo in product("aeiou", repeat=len(positions)):
            variant = token
            for pos_idx in range(len(positions) - 1, -1, -1):
                pos = positions[pos_idx]
                variant = variant[:pos+1] + vowel_combo[pos_idx] + variant[pos+1:]
            
            if self._is_valid_word(variant):
                candidates.append(variant)
        
        return candidates
    
    def _phonetic_reconstruct(self, token: str) -> str:
        """Reconstruct phonetically obfuscated words."""
        variations = {token}
        result = token.lower()
        
        # Pattern 1: trailing h (gandah → ganda)
        if result.endswith('h') and len(result) > 1 and result[-2] in self.vowels:
            variations.add(result[:-1])
        
        # Pattern 2: f → ph (fone → phone)
        if 'f' in result:
            if result.startswith('f') and len(result) > 1 and result[1] in self.vowels:
                variations.add('ph' + result[1:])
            else:
                variations.add(re.sub(r'([aeiou])f([aeiou])', r'\1ph\2', result))
        
        # Pattern 3: d → th (dis → this)
        if result.startswith('d') and len(result) > 1 and result[1] in self.vowels:
            variations.add('th' + result[1:])
        
        # Pattern 4: u → oo (fud → food)
        if 'u' in result and len(result) >= 3:
            variations.add(re.sub(r'([bcdfghjklmnpqrstvwxyz])u([bcdfghjklmnpqrstvwxyz])', r'\1oo\2', result))
        
        # Pattern 5: au → ayo/yo (kau → kayo/kyo)
        if 'au' in result:
            variations.add(re.sub(r'([bcdfghjklmnpqrstvwxyz])au', r'\1ayo', result))
            variations.add(re.sub(r'([bcdfghjklmnpqrstvwxyz])au', r'\1yo', result))
        
        # Return first valid match or original
        for variant in sorted(variations, key=len):
            if self._is_valid_word(variant):
                return variant
        
        return token
    
    def deobfuscate(self, token: str, use_fuzzy: bool = True, signals: dict = None) -> str:
        """ Deobfuscate token based on pre-detected signals."""
        if not token:
            return token
        
        signals = signals or {}
        
        # Parse punctuation
        match = re.match(r"^([(\[{]*)([a-z0-9@$|€*._-]+)([\?\!.,;:)\]}]*)$", token)
        if not match:
            return token
        
        leading_punctuation, core_word, trailing_punctuation = match.groups()
        core_lower = core_word.lower()
        
        # Skip valid words
        if self._is_english_word(core_lower) or self._is_valid_word(core_lower):
            return token
        
        transformed = core_lower
        
        # STEP 1: Netspeak (check original)
        if signals.get('netspeak') and core_lower in self.netspeak_map:
            return leading_punctuation + self.netspeak_map[core_lower] + trailing_punctuation
        
        # STEP 2: Symbol Separation
        if signals.get('symbol_separation'):
            transformed = self._reverse_symbol_separation(transformed)
            # After symbol separation, re-detect signals and re-apply deobfuscation if needed
            if not self._is_valid_word(transformed):
                try:
                    from .detection_service import DetectionService
                    detector = DetectionService()
                    signal_detectors = {
                        'netspeak': detector.netspeak,
                        'char_duplication': detector.char_duplication,
                        'leetspeak': detector.leetspeak,
                        'vowel_omission': detector.vowel_omission,
                        'phonetic': detector.phonetic,
                        'symbol_separation': detector.symbol_separation,
                    }
                    new_signals = signals.copy()
                    for sig_type, sig_detector in signal_detectors.items():
                        if new_signals.get(sig_type):
                            continue
                        if sig_type == 'phonetic':
                            detected = sig_detector.is_accepted(transformed).get('has_phonetic', False)
                        else:
                            detected = sig_detector.is_accepted(transformed)
                        if sig_type == 'vowel_omission' and len(transformed) <= 3:
                            continue
                        if detected:
                            new_signals[sig_type] = detected
                    # If any new signal is detected, recursively deobfuscate with new signals
                    if any(new_signals[k] and not signals.get(k) for k in new_signals):
                        print(f"[DEBUG] Recursive deobfuscate: token='{transformed}', Signals: {new_signals}")
                        return self.deobfuscate(transformed, use_fuzzy=use_fuzzy, signals=new_signals)
                except Exception as e:
                    print(f"[WARNING] Re-detection failed: {e}")
        
        # STEP 3: Leetspeak
        if signals.get('leetspeak'):
            transformed = self._reverse_leetspeak(transformed)
            if transformed in self.netspeak_map:
                return leading_punctuation + self.netspeak_map[transformed] + trailing_punctuation
        
        # STEP 4: Character Duplication
        if signals.get('char_duplication'):
            transformed = self._normalize_duplication(transformed)
        
        # STEP 5: Vowel Omission
        if signals.get('vowel_omission'):
            candidates = self._try_vowel_insertion(transformed)
            if candidates:
                transformed = candidates[0]
        
        # STEP 6: Phonetic
        phonetic_signal = signals.get('phonetic')
        has_phonetic = (
            phonetic_signal.get('has_phonetic', False)
            if isinstance(phonetic_signal, dict)
            else phonetic_signal
        )
        
        if has_phonetic:
            transformed = self._phonetic_reconstruct(transformed)
        
        # STEP 7: Validate and check netspeak again
        if self._is_valid_word(transformed):
            return leading_punctuation + transformed + trailing_punctuation
        
        if transformed in self.netspeak_map:
            return leading_punctuation + self.netspeak_map[transformed] + trailing_punctuation
        
        # STEP 8: Fuzzy matching (last resort)
        if use_fuzzy and len(transformed) >= 3 and any(signals.values()):
            for dict_list in [self.primary_dict_list, self.secondary_dict_list, self.tertiary_dict_list]:
                match = self.fuzzy_matcher.get_best_match(transformed, dict_list)
                if match and match.get('confidence', 0) >= 0.90:
                    return leading_punctuation + match['word'] + trailing_punctuation
        
        return leading_punctuation + transformed + trailing_punctuation if transformed != core_lower else token