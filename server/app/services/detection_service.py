import re
from typing import Optional, Dict, Set, List

from .preprocessing_service import normalize_input, word_tokenize
from .dictionary_service import load_and_cache_dictionaries, cached_dictionaries


class AutomatonState:
    """Represents a single state in a finite automaton."""
    def __init__(self, state_id: str, is_accepting: bool = False):
        self.state_id = state_id
        self.is_accepting = is_accepting
        self.transitions: Dict[str, Set[str]] = {}  # char -> {next_state_ids}
        self.epsilon_transitions: Set[str] = set()  # epsilon paths
    
    def __repr__(self):
        return f"State({self.state_id}, accepting={self.is_accepting})"


class NFA:
    """Non-Deterministic Finite Automaton with epsilon transitions."""
    
    def __init__(self):
        self.states: Dict[str, AutomatonState] = {}
        self.initial_state: Optional[str] = None
    
    def add_state(self, state_id: str, is_accepting: bool = False) -> AutomatonState:
        """Add or retrieve a state."""
        if state_id not in self.states:
            self.states[state_id] = AutomatonState(state_id, is_accepting)
        else:
            self.states[state_id].is_accepting |= is_accepting
        return self.states[state_id]
    
    def set_initial_state(self, state_id: str):
        """Set the starting state."""
        self.initial_state = state_id
    
    def add_transition(self, from_state: str, symbols: str, to_state: str):
        """Add transition(s) for given symbol(s)."""
        for symbol in symbols:
            self.states[from_state].transitions.setdefault(symbol, set()).add(to_state)
    
    def add_epsilon_transition(self, from_state: str, to_state: str):
        """Add epsilon transition (no symbol consumed)."""
        self.states[from_state].epsilon_transitions.add(to_state)
    
    def _get_epsilon_closure(self, state_set: Set[str]) -> Set[str]:
        """Find all states reachable via epsilon transitions."""
        stack = list(state_set)
        closure = set(state_set)
        
        while stack:
            current = stack.pop()
            for next_state in self.states[current].epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        
        return closure
    
    def matches(self, text: str) -> bool:
        """Check if text matches the automaton."""
        if not self.initial_state:
            return False
        
        current_states = self._get_epsilon_closure({self.initial_state})
        
        for char in text.lower():
            next_states: Set[str] = set()
            
            for state in current_states:
                if char in self.states[state].transitions:
                    next_states.update(self.states[state].transitions[char])
            
            if not next_states:
                return False
            
            current_states = self._get_epsilon_closure(next_states)
        
        return any(self.states[s].is_accepting for s in current_states)


class VowelOmissionDetector:
    """
    Detects words with 3+ consecutive consonants (vowel omission).
    Examples: txt, plz, thx, strng
    """
    
    def __init__(self):
        self.vowels = "aeiou"
        self.consonants = "bcdfghjklmnpqrstvwxyz"
        self.nfa = self._build_nfa()
    
    def _build_nfa(self) -> NFA:
        nfa = NFA()
        
        nfa.add_state("START")
        nfa.add_state("C1")
        nfa.add_state("C2")
        nfa.add_state("C3_PLUS", is_accepting=True)
        nfa.set_initial_state("START")
        
        nfa.add_transition("START", self.consonants, "C1")
        nfa.add_transition("START", self.vowels, "START")
        
        nfa.add_transition("C1", self.consonants, "C2")
        nfa.add_transition("C1", self.vowels, "START")
        
        nfa.add_transition("C2", self.consonants, "C3_PLUS")
        nfa.add_transition("C2", self.vowels, "START")
        
        nfa.add_transition("C3_PLUS", self.consonants, "C3_PLUS")
        nfa.add_transition("C3_PLUS", self.vowels, "START")
        
        return nfa
    
    def detect(self, token: str) -> bool:
        return self.nfa.matches(token)


class CharDuplicationDetector:
    """
    Detects words with 3+ consecutive identical characters.
    Examples: hellooo, yesss, nooooo
    """
    
    def __init__(self):
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.nfa = self._build_nfa()
    
    def _build_nfa(self) -> NFA:
        nfa = NFA()
        nfa.add_state("START")
        nfa.set_initial_state("START")
        
        for letter in self.alphabet:
            state_once = f"{letter}_once"
            state_twice = f"{letter}_twice"
            state_thrice = f"{letter}_thrice"
            
            nfa.add_state(state_once)
            nfa.add_state(state_twice)
            nfa.add_state(state_thrice, is_accepting=True)
            
            nfa.add_transition("START", letter, state_once)
            nfa.add_transition(state_once, letter, state_twice)
            nfa.add_transition(state_twice, letter, state_thrice)
            nfa.add_transition(state_thrice, letter, state_thrice)
            
            # Switch to different letter - restart count
            for other_letter in self.alphabet:
                if other_letter != letter:
                    nfa.add_transition(state_once, other_letter, f"{other_letter}_once")
                    nfa.add_transition(state_twice, other_letter, f"{other_letter}_once")
                    nfa.add_transition(state_thrice, other_letter, f"{other_letter}_once")
        
        return nfa
    
    def detect(self, token: str) -> bool:
        # Remove non-letter characters to check for consecutive duplicates
        letters_only = ''.join(c for c in token if c.isalpha())
        return self.nfa.matches(letters_only)


class LeetspeakDetector:
    """
    Detects leetspeak/1337 speak patterns.
    Examples: h3ll0, p4ssw0rd, l33t
    """
    
    def __init__(self, leet_data: Dict = None):
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.leet_chars = self._extract_leet_chars(leet_data)
        self.nfa = self._build_nfa()
    
    def _extract_leet_chars(self, leet_data: Dict) -> str:
        """Extract all leetspeak substitution symbols from config."""
        chars = set()
        if leet_data and 'character_substitutions' in leet_data:
            for substitutions in leet_data['character_substitutions'].values():
                if isinstance(substitutions, list):
                    chars.update(substitutions)
                else:
                    chars.add(substitutions)
        return "".join(chars)
    
    def _build_nfa(self) -> NFA:
        nfa = NFA()
        
        nfa.add_state("START")
        nfa.add_state("NORMAL_WORD")
        nfa.add_state("LEET_FOUND", is_accepting=True)
        nfa.set_initial_state("START")
        
        nfa.add_transition("START", self.alphabet, "NORMAL_WORD")
        nfa.add_transition("START", self.leet_chars, "LEET_FOUND")
        
        nfa.add_transition("NORMAL_WORD", self.alphabet, "NORMAL_WORD")
        nfa.add_transition("NORMAL_WORD", self.leet_chars, "LEET_FOUND")
        
        nfa.add_transition("LEET_FOUND", self.alphabet + self.leet_chars, "LEET_FOUND")
        
        return nfa
    
    def detect(self, token: str) -> bool:
        return self.nfa.matches(token)


class MorphologyDetector:
    """
    Detects Filipino morphological patterns (affixes).
    Examples: nag-work (nag- prefix), kumain (um- infix), pangalan (pang- circumfix)
    """
    
    def __init__(self, morph_data: Dict = None):
        morph_data = morph_data or {}
        affixes = morph_data.get("affixes", {})
        
        self.prefixes = list(affixes.get("prefixes", []))
        self.suffixes = list(affixes.get("suffixes", []))
        self.infixes = list(affixes.get("infixes", []))
        self.circumfixes = affixes.get("circumfixes", {})
        
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.vowels = "aeiou"
        self.consonants = "bcdfghjklmnpqrstvwxyz"
        self.min_root_length = morph_data.get("validation_rules", {}).get("min_root_after_prefix", 2)
        
        # Handle 'um' appearing in both prefix and infix
        self.has_um_prefix = "um" in self.prefixes
        self.has_um_infix = "um" in self.infixes
        if self.has_um_prefix and self.has_um_infix:
            self.infixes = [affix for affix in self.infixes if affix != "um"]
        
        self.nfa = self._build_nfa()
    
    def _build_root_chain(self, from_state: str, chain_id: str, nfa: NFA) -> str:
        """Create a chain of states for minimum root length."""
        prev_state = from_state
        
        for i in range(1, self.min_root_length + 1):
            new_state = f"{chain_id}_ROOT{i}"
            is_accepting = (i == self.min_root_length)
            nfa.add_state(new_state, is_accepting=is_accepting)
            nfa.add_transition(prev_state, self.alphabet, new_state)
            prev_state = new_state
        
        nfa.add_transition(prev_state, self.alphabet, prev_state)
        return prev_state
    
    def _build_nfa(self) -> NFA:
        nfa = NFA()
        nfa.add_state("START")
        nfa.set_initial_state("START")
        
        # Build prefix paths
        for prefix in self.prefixes:
            if prefix == "um" and self.has_um_infix:
                continue
            
            prev_state = "START"
            for idx, char in enumerate(prefix):
                new_state = f"PFX_{prefix}_CH{idx}"
                nfa.add_state(new_state)
                nfa.add_transition(prev_state, char, new_state)
                prev_state = new_state
            
            self._build_root_chain(prev_state, f"PFX_{prefix}", nfa)
        
        # Build root-only paths (for suffix matching)
        root_states = []
        for i in range(1, self.min_root_length + 1):
            root_state = f"ROOT{i}"
            is_accepting = (i == self.min_root_length)
            nfa.add_state(root_state, is_accepting=is_accepting)
            root_states.append(root_state)
            
            if i == 1:
                nfa.add_transition("START", self.alphabet, root_state)
            else:
                nfa.add_transition(root_states[i - 2], self.alphabet, root_state)
        
        nfa.add_transition(root_states[-1], self.alphabet, root_states[-1])
        
        # Build suffix paths
        for suffix in self.suffixes:
            prev_state = root_states[-1]
            for idx, char in enumerate(suffix):
                new_state = f"SFX_{suffix}_CH{idx}"
                is_accepting = (idx == len(suffix) - 1)
                nfa.add_state(new_state, is_accepting=is_accepting)
                nfa.add_transition(prev_state, char, new_state)
                prev_state = new_state
        
        # Build infix paths
        infix_start = "INFIX_START"
        nfa.add_state(infix_start)
        nfa.add_transition("START", self.consonants, infix_start)
        
        for infix in self.infixes:
            prev_state = infix_start
            for idx, char in enumerate(infix):
                new_state = f"IFX_{infix}_CH{idx}"
                nfa.add_state(new_state)
                nfa.add_transition(prev_state, char, new_state)
                prev_state = new_state
            
            self._build_root_chain(prev_state, f"IFX_{infix}", nfa)
        
        # Build circumfix paths
        for circumfix_name, (prefix, suffix) in self.circumfixes.items():
            prev_state = "START"
            for idx, char in enumerate(prefix):
                new_state = f"CFX_{circumfix_name}_PFX{idx}"
                nfa.add_state(new_state)
                nfa.add_transition(prev_state, char, new_state)
                prev_state = new_state
            
            root_final = self._build_root_chain(prev_state, f"CFX_{circumfix_name}", nfa)
            
            for idx, char in enumerate(suffix):
                new_state = f"CFX_{circumfix_name}_SFX{idx}"
                is_accepting = (idx == len(suffix) - 1)
                nfa.add_state(new_state, is_accepting=is_accepting)
                nfa.add_transition(root_final, char, new_state)
                root_final = new_state
        
        return nfa
    
    def detect(self, word: str) -> bool:
        return self.nfa.matches(word)


class AbbreviationDetector:
    """
    Detects abbreviations and common shorthand.
    Examples: u, ty, lol, omg, ty vm
    """
    
    def __init__(self, abbrev_data: Dict = None):
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.space = " "
        
        self.single_abbrevs, self.multi_abbrevs = self._extract_abbreviations(abbrev_data)
        self.nfa = self._build_nfa()
    
    def _extract_abbreviations(self, abbrev_data: Dict) -> tuple:
        """Extract abbreviations from data dictionary."""
        all_terms = set()
        
        if abbrev_data and "filipinish_netspeak" in abbrev_data:
            ns = abbrev_data["filipinish_netspeak"]
            categories = [
                "filipinish_shortcuts",
                "acronyms",
                "common_slang",
                "filipinish_english",
                "common_phrases",
            ]
            
            for category in categories:
                data = ns.get(category, {})
                for root_word, abbreviations in data.items():
                    all_terms.add(root_word.lower())
                    
                    if isinstance(abbreviations, list):
                        for abbrev in abbreviations:
                            all_terms.add(str(abbrev).lower())
                    elif abbreviations:
                        all_terms.add(str(abbreviations).lower())
        
        # Separate into single and multi-word
        single_word = set()
        multi_word = set()
        
        for term in all_terms:
            term = term.strip()
            if self.space in term:
                multi_word.add(term)
            elif 1 <= len(term) <= 6:  # Reasonable length for shortcuts
                single_word.add(term)
        
        return single_word, multi_word
    
    def _build_nfa(self) -> NFA:
        nfa = NFA()
        nfa.add_state("START")
        nfa.set_initial_state("START")
        
        # Build single-word abbreviation paths
        for abbrev in self.single_abbrevs:
            prev_state = "START"
            for idx, char in enumerate(abbrev):
                new_state = f"ABBR_{abbrev}_CH{idx}"
                is_accepting = (idx == len(abbrev) - 1)
                nfa.add_state(new_state, is_accepting=is_accepting)
                nfa.add_transition(prev_state, char, new_state)
                prev_state = new_state
        
        # Build multi-word phrase paths (includes spaces)
        for phrase in self.multi_abbrevs:
            prev_state = "START"
            phrase_id = phrase.replace(self.space, "_")
            
            for idx, char in enumerate(phrase):
                new_state = f"PHRASE_{phrase_id}_CH{idx}"
                is_accepting = (idx == len(phrase) - 1)
                nfa.add_state(new_state, is_accepting=is_accepting)
                nfa.add_transition(prev_state, char, new_state)
                prev_state = new_state
        
        return nfa
    
    def detect_single(self, token: str) -> bool:
        """Detect single-word abbreviation (with punctuation stripping)."""
        cleaned = token.lower().strip('.,!?;:()[]{}"\'-')
        return self.nfa.matches(cleaned)
    
    def detect_multi(self, text: str) -> bool:
        """Detect multi-word phrases (preserves spaces)."""
        return self.nfa.matches(text.lower())
    
    def detect(self, token: str, is_multi: bool = False) -> bool:
        """Wrapper detection method."""
        return self.detect_multi(token) if is_multi else self.detect_single(token)


class DetectionService:
    """
    Main detection automata using NFAs for obfuscation pattern detection.
    
    Handles:
    - VowelOmissionDetector: txt, plz, thx
    - CharDuplicationDetector: hellooo, yesss
    - LeetspeakDetector: h3ll0, p4ssw0rd
    - MorphologyDetector: Filipino affixes (nag-, -um-, -in)
    - AbbreviationDetector: u, ty, lol, omg
    
    Returns early if word is already valid (in dictionaries).
    Only detects obfuscation patterns for invalid words.
    """
    
    def __init__(self, dictionaries: Dict[str, Set[str]] = None):
        """
        Args:
            dictionaries: Dict with 'primary', 'secondary', 'tertiary' word sets
        """
        try:
            load_and_cache_dictionaries()
        except Exception as e:
            print(f"[WARNING] Dictionary loading failed: {e}")
        
        self.primary_dict = dictionaries.get('primary', set()) if dictionaries else set()
        self.secondary_dict = dictionaries.get('secondary', set()) if dictionaries else set()
        self.tertiary_dict = dictionaries.get('tertiary', set()) if dictionaries else set()
        
        leet_data = cached_dictionaries.get('leetspeak_map')
        abbrev_data = cached_dictionaries.get('netspeak_patterns')
        morph_data = cached_dictionaries.get('morphology_patterns')
        
        self.vowel_omission = VowelOmissionDetector()
        self.char_duplication = CharDuplicationDetector()
        self.leetspeak = LeetspeakDetector(leet_data.data if leet_data else {})
        self.morphology = MorphologyDetector(morph_data.data if morph_data else {})
        self.abbreviation = AbbreviationDetector(abbrev_data.data if abbrev_data else {})
    
    def _is_valid_word(self, word: str) -> bool:
        """Check if word exists in any dictionary."""
        return (
            word in self.primary_dict or
            word in self.secondary_dict or
            word in self.tertiary_dict
        )
    
    def _calculate_confidence(self, signals: Dict[str, bool]) -> float:
        """
        Calculate confidence score based on detected signals.
        
        Weights by specificity:
        - Abbreviation: 0.30 (high - exact matches)
        - Leetspeak: 0.25 (high - obvious patterns)
        - Char duplication: 0.20 (medium-high)
        - Vowel omission: 0.15 (medium)
        - Morphology: 0.10 (low - can be legitimate)
        """
        weights = {
            'abbreviation': 0.30,
            'leetspeak': 0.25,
            'char_duplication': 0.20,
            'vowel_omission': 0.15,
            'morphology': 0.10
        }
        
        total_confidence = sum(
            weights.get(signal_type, 0.1)
            for signal_type, detected in signals.items()
            if detected
        )
        
        return min(total_confidence, 1.0)
    
    def analyze(self, text: str, language: str = 'unknown') -> Dict:
        """
        Analyze text for obfuscation patterns.
        
        Returns early if word is already valid (not obfuscated).
        Only detects patterns if word is NOT in dictionary.
        
        Args:
            text: Input text to analyze
            language: Language hint (default: 'unknown')
            
        Returns:
            Dictionary with detection results and confidence scores
        """
        if not text or not text.strip():
            return {
                'isObfuscated': False,
                'confidence': 0.0,
                'patterns': [],
                'detected_signals': {
                    'vowel_omission': False,
                    'char_duplication': False,
                    'leetspeak': False,
                    'morphology': False,
                    'abbreviation': False
                }
            }
        
        text_lower = text.lower()
        
        # STEP 1: If already a valid word, no obfuscation
        if self._is_valid_word(text_lower):
            return {
                'isObfuscated': False,
                'confidence': 0.0,
                'patterns': [],
                'detected_signals': {
                    'vowel_omission': False,
                    'char_duplication': False,
                    'leetspeak': False,
                    'morphology': False,
                    'abbreviation': False
                }
            }
        
        # STEP 2: Only if invalid, check for obfuscation patterns
        try:
            tokens = word_tokenize(normalize_input(text_lower))
            
            if not tokens:
                return {
                    'isObfuscated': False,
                    'confidence': 0.0,
                    'patterns': [],
                    'detected_signals': {
                        'vowel_omission': False,
                        'char_duplication': False,
                        'leetspeak': False,
                        'morphology': False,
                        'abbreviation': False
                    }
                }
            
            # Check multi-token abbreviations (with spaces)
            has_multi_abbrev = self.abbreviation.detect_multi(text_lower)
            
            # Detect all obfuscation patterns
            signals = {
                'vowel_omission': any(self.vowel_omission.detect(t) for t in tokens),
                'char_duplication': any(self.char_duplication.detect(t) for t in tokens),
                'leetspeak': any(self.leetspeak.detect(t) for t in tokens),
                'morphology': any(self.morphology.detect(t) for t in tokens),
                'abbreviation': has_multi_abbrev or any(self.abbreviation.detect_single(t) for t in tokens)
            }
            
            is_obfuscated = any(signals.values())
            confidence = self._calculate_confidence(signals) if is_obfuscated else 0.0
            
            return {
                'isObfuscated': is_obfuscated,
                'confidence': confidence,
                'patterns': ['taglish_obfuscation'] if is_obfuscated else [],
                'detected_signals': signals
            }
        
        except Exception as e:
            print(f"[ERROR] Detection failed: {e}")
            return {
                'isObfuscated': False,
                'confidence': 0.0,
                'patterns': [],
                'detected_signals': {
                    'vowel_omission': False,
                    'char_duplication': False,
                    'leetspeak': False,
                    'morphology': False,
                    'abbreviation': False
                }
            }
