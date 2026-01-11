import re
from typing import Optional, Dict, Set, List

from .preprocessing_service import normalize_input, word_tokenize
from .dictionary_service import load_and_cache_dictionaries, cached_dictionaries


class AutomatonState:
    """Represents a single state in a finite automaton."""
    def __init__(self, state_id: str, is_accepting: bool = False):
        self.state_id = state_id
        self.is_accepting = is_accepting
        self.transitions: Dict[str, Set[str]] = {}
        self.epsilon_transitions: Set[str] = set()
    
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
        if from_state not in self.states:
            self.add_state(from_state)
        if to_state not in self.states:
            self.add_state(to_state)
        
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
    
    def is_accepted(self, text: str) -> bool:
        """Check if text is accepted by the NFA."""
        if not self.initial_state:
            return False
        
        # Start with epsilon closure of initial state
        current_states = self._get_epsilon_closure({self.initial_state})
        
        # Process each character
        for char in text:
            next_states: Set[str] = set()
            
            # Find all possible transitions from current states
            for state in current_states:
                if char in self.states[state].transitions:
                    next_states.update(self.states[state].transitions[char])
            
            # No valid transitions = reject
            if not next_states:
                return False
            
            # Apply epsilon closure to next states
            current_states = self._get_epsilon_closure(next_states)
        
        # Accept only if we END in an accepting state
        return any(self.states[s].is_accepting for s in current_states)


class VowelOmissionDetector:
    """Detects words with 3+ consecutive consonants."""
    
    def __init__(self):
        self.vowels = "aeiou"
        self.consonants = "bcdfghjklmnpqrstvwxyz"
        self.nfa = self._build()
    
    def _build(self) -> NFA:
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("C1")
        nfa.add_state("C2", is_accepting=True)

        nfa.set_initial_state("START")
        
        nfa.add_transition("START", self.vowels, "START")
        nfa.add_transition("START", self.consonants, "C1")

        nfa.add_transition("C1", self.consonants, "C2")
        nfa.add_transition("C1", self.vowels, "START")
        
        nfa.add_transition("C2", self.consonants, "C2")
        nfa.add_transition("C2", self.vowels, "C2") # absorbing accepting state

        return nfa
    
    def is_accepted(self, token: str) -> bool:
        return self.nfa.is_accepted(token)


class CharDuplicationDetector:
    """Detects words with 2+ consecutive identical characters."""
    
    def __init__(self, min_duplicates: int = 2):
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.min_duplicates = min_duplicates
        self.nfa = self._build()
    
    def _build(self) -> NFA:
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("DUP_FOUND", is_accepting=True)  #accepting state
        nfa.set_initial_state("START")
        
        for letter in self.alphabet:
            state_once = f"{letter}_1"
            state_twice = f"{letter}_2"
            
            nfa.add_state(state_once)
            nfa.add_state(state_twice, is_accepting=True)  # 2+ duplicates = accepting
            
            # Same letter transitions
            nfa.add_transition("START", letter, state_once)
            nfa.add_transition(state_once, letter, state_twice)
            nfa.add_transition(state_twice, letter, "DUP_FOUND")  # 3+ goes to DUP_FOUND
            
            # Different letter transitions (restart count)
            for other_letter in self.alphabet:
                if other_letter != letter:
                    nfa.add_transition(state_once, other_letter, f"{other_letter}_1")
                    nfa.add_transition(state_twice, other_letter, "DUP_FOUND")

            nfa.add_transition("DUP_FOUND", self.alphabet, "DUP_FOUND")
        return nfa
    
    def is_accepted(self, token: str) -> bool:
        return self.nfa.is_accepted(token)
    

class LeetspeakDetector:
    """Detects leetspeak/1337 speak patterns."""
    
    def __init__(self, leet_data: Dict = None):
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.leet_chars = self._extract_leet_chars(leet_data)
        self.nfa = self._build()
    
    def _extract_leet_chars(self, leet_data: Dict) -> str:
        """Extract all leetspeak substitution symbols"""
        chars = set()
        if leet_data and 'character_substitutions' in leet_data:
            for substitutions in leet_data['character_substitutions'].values():
                if isinstance(substitutions, list):
                    chars.update(substitutions)
                else:
                    chars.add(substitutions)
        return "".join(chars)
    
    def _build(self) -> NFA:
        nfa = NFA()
        
        # States
        nfa.add_state("START")
        nfa.add_state("CHAR")
        nfa.add_state("LEET_FOUND", is_accepting=True)
        nfa.set_initial_state("START")
        
        nfa.add_transition("START", self.alphabet, "CHAR")
        nfa.add_transition("START", self.leet_chars, "CHAR")

        nfa.add_transition("CHAR", self.alphabet, "CHAR")
        nfa.add_transition("CHAR", self.leet_chars, "LEET_FOUND")
        
        nfa.add_transition("LEET_FOUND", self.alphabet, "LEET_FOUND")
        nfa.add_transition("LEET_FOUND", self.leet_chars, "LEET_FOUND")
        
        return nfa
    
    def is_accepted(self, token: str) -> bool:
        return self.nfa.is_accepted(token)

class SymbolSeparationDetector:
    """
    Detects symbol-separated obfuscation like k-m-u-s-t-a, h-e-l-l-o, h_3_l_l_0.
    Pattern: letter/digit + (separator + letter/digit)+ with at least 2+ items separated.
    """
    def __init__(self):
        self.alphanumeric = "abcdefghijklmnopqrstuvwxyz0123456789"
        self.separators = "-._|*"
        self.nfa = self._build()
    
    def _build(self) -> NFA:
        nfa = NFA()
        
        # States
        nfa.add_state("START")
        nfa.add_state("ALPHANUM")
        nfa.add_state("SYMBOL")
        nfa.add_state("MATCHED", is_accepting=True)
        nfa.set_initial_state("START")
        

        nfa.add_transition("START", self.separators, "SYMBOL")
        nfa.add_transition("START", self.alphanumeric, "ALPHANUM")

        nfa.add_transition("ALPHANUM", self.separators, "SYMBOL")
        nfa.add_transition("SYMBOL", self.separators, "SYMBOL")
        nfa.add_transition("SYMBOL", self.alphanumeric, "MATCHED")
        
        nfa.add_transition("MATCHED", self.separators, "SYMBOL")
        nfa.add_transition("MATCHED", self.alphanumeric, "MATCHED")
        
        return nfa
    
    def is_accepted(self, token: str) -> bool:
        return self.nfa.is_accepted(token)


class NetspeakDetector:
    """Detects single-word netspeaks and common shorthand."""
    
    def __init__(self, netspeak_data: Dict = None):
        self.single_netspeak = self._extract_netspeaks(netspeak_data)
        self.nfa = self._build()
    
    def _extract_netspeaks(self, netspeak_data: Dict) -> set:
        """Extract single-word netspeaks from dictionary."""
        terms = set()
        if netspeak_data and "filipino_netspeak" in netspeak_data:
            ns = netspeak_data["filipino_netspeak"]
            categories = ["filipino_shortcuts", "acronyms", "common_slang", 
                         "filipino_english", "common_phrases"]
            
            for category in categories:
                for root_word, variants in ns.get(category, {}).items():
                    terms.add(root_word.lower())
                    if isinstance(variants, list):
                        terms.update(str(v).lower() for v in variants)
                    elif variants:
                        terms.add(str(variants))
        
        return {t.strip() for t in terms}
    
    def _build(self) -> NFA:
        """Build NFA for single-word netspeak detection."""
        nfa = NFA()
        nfa.add_state("START")
        nfa.set_initial_state("START")

        for netspeak in self.single_netspeak:
            PREV_STATE = "START"

            for idx, char in enumerate(netspeak):
                NEW_STATE = f"NS_{netspeak}_{idx}"
                is_accepting = (idx == len(netspeak) - 1)

                nfa.add_state(NEW_STATE, is_accepting=is_accepting)
                nfa.add_transition(PREV_STATE, char, NEW_STATE)
                PREV_STATE = NEW_STATE

        return nfa
    
    def is_accepted(self, token: str) -> bool:
        return self.nfa.is_accepted(token) and token in self.single_netspeak


class PhoneticDetector:
    """Detects Filipino phonetic obfuscation patterns."""
    
    def __init__(self):
        self.vowels = "aeiou"
        self.consonants = "bcdfghjklmnpqrstvwxyz"
        self.alphabet = self.vowels + self.consonants
        
        self.nfa_au = self._build_au_nfa()
        self.nfa_f = self._build_f_nfa()
        self.nfa_d = self._build_d_nfa()
        self.nfa_u = self._build_u_nfa()
        self.nfa_h = self._build_h_nfa()
    
    def _build_au_nfa(self) -> NFA:
        """Detect 'au' (ayo→au obfuscation). Examples: kau, pau, tau."""
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("MIDDLE")
        nfa.add_state("A_FOUND")
        nfa.add_state("AU_FOUND", is_accepting=True)
        
        nfa.set_initial_state("START")
        
        nfa.add_transition("START", self.alphabet, "MIDDLE")
        nfa.add_transition("START", "a", "A_FOUND")

        nfa.add_transition("MIDDLE", self.alphabet, "MIDDLE")
        nfa.add_transition("MIDDLE", "a", "A_FOUND")

        nfa.add_transition("A_FOUND", "u", "AU_FOUND")
        nfa.add_transition("AU_FOUND", self.alphabet, "AU_FOUND")
        
        return nfa
    
    def _build_f_nfa(self) -> NFA:
        """Detect 'ph'→'f' pattern. Examples: fone, foto."""
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("BEFORE_F")
        nfa.add_state("F_FOUND", is_accepting=True)
        nfa.set_initial_state("START")
        
        nfa.add_transition("START", self.alphabet, "BEFORE_F")
        nfa.add_transition("START", "f", "F_FOUND")

        nfa.add_transition("BEFORE_F", self.alphabet, "BEFORE_F")
        nfa.add_transition("BEFORE_F", "f", "F_FOUND")

        nfa.add_transition("F_FOUND", self.alphabet, "F_FOUND")
        
        return nfa
    
    def _build_d_nfa(self) -> NFA:
        """Detect 'th'→'d' pattern. Examples: dis, dat."""
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("D_FOUND")
        nfa.add_state("D_VOWEL", is_accepting=True)

        nfa.set_initial_state("START")
        nfa.add_transition("START", "d", "D_FOUND")
    
        nfa.add_transition("D_FOUND", self.vowels, "D_VOWEL")
        nfa.add_transition("D_VOWEL", self.alphabet, "D_VOWEL")
        
        return nfa
    
    def _build_u_nfa(self) -> NFA:
        """Detect 'oo'→'u' pattern. Examples: fud, gud."""
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("BEFORE_U")
        nfa.add_state("U_FOUND")
        nfa.add_state("U_CONSONANT", is_accepting=True)
        nfa.set_initial_state("START")
        
        nfa.add_transition("START", self.consonants, "BEFORE_U")
        nfa.add_transition("BEFORE_U", self.consonants, "BEFORE_U")
        nfa.add_transition("BEFORE_U", "u", "U_FOUND")
        nfa.add_transition("U_FOUND", self.consonants, "U_CONSONANT")
        nfa.add_transition("U_CONSONANT", self.alphabet, "U_CONSONANT")
        
        return nfa
    
    def _build_h_nfa(self) -> NFA:
        """Detect trailing 'h'. Examples: gandah, ayh."""
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("MIDDLE")
        nfa.add_state("VOWEL_BEFORE_H")
        nfa.add_state("TRAILING_H", is_accepting=True)
        nfa.set_initial_state("START")
        
        nfa.add_transition("START", self.alphabet, "MIDDLE")
        nfa.add_transition("MIDDLE", self.alphabet, "MIDDLE")
        nfa.add_transition("MIDDLE", self.vowels, "VOWEL_BEFORE_H")
        nfa.add_transition("VOWEL_BEFORE_H", self.vowels, "VOWEL_BEFORE_H")
        nfa.add_transition("VOWEL_BEFORE_H", "h", "TRAILING_H")
        
        return nfa
    
    def is_accepted(self, token: str) -> dict:
        """Check all phonetic patterns."""
        patterns = {
            'au': self.nfa_au.is_accepted(token),
            'f': self.nfa_f.is_accepted(token),
            'd': self.nfa_d.is_accepted(token),
            'u': self.nfa_u.is_accepted(token),
            'h': self.nfa_h.is_accepted(token)
        }
        #print(f"[DEBUG PHONETIC] Testing token='{token}', letters_only='{token}', patterns={patterns}")
        return {'has_phonetic': any(patterns.values()), 'patterns': patterns}


class DetectionService:
    """Main detection service using NFAs."""
    
    def __init__(self, dictionaries: Dict[str, Set[str]] = None):
        try:
            load_and_cache_dictionaries()
        except Exception as e:
            print(f"[WARNING] Dictionary loading failed: {e}")
        
        self.primary_dict = dictionaries.get('primary', set()) if dictionaries else set()
        self.secondary_dict = dictionaries.get('secondary', set()) if dictionaries else set()
        self.tertiary_dict = dictionaries.get('tertiary', set()) if dictionaries else set()
        
        leet_data = cached_dictionaries.get('leetspeak_map')
        netspeak_data = cached_dictionaries.get('netspeak_patterns')
        
        self.vowel_omission = VowelOmissionDetector()
        self.char_duplication = CharDuplicationDetector()
        self.leetspeak = LeetspeakDetector(leet_data.data if leet_data else {})
        self.symbol_separation = SymbolSeparationDetector()
        self.netspeak = NetspeakDetector(netspeak_data.data if netspeak_data else {})
        self.phonetic = PhoneticDetector()

    def _is_valid_word(self, word: str) -> bool:
        """Check if word exists in dictionaries."""
        return word in (self.primary_dict | self.secondary_dict | self.tertiary_dict)
    
    def _calculate_confidence(self, signals: Dict[str, bool]) -> float:
        """Calculate confidence score based on signals."""
        weights = {
            'netspeak': 0.30,
            'phonetic': 0.20,
            'leetspeak': 0.25,
            'char_duplication': 0.20,
            'vowel_omission': 0.15,
            'symbol_separation': 0.10
        }
        return min(sum(weights.get(s, 0.1) for s, d in signals.items() if d), 1.0)

    def analyze(self, text: str, language: str = 'unknown') -> Dict:
        """Analyze text for obfuscation patterns."""
        if not text or not text.strip():
            return self._empty_result()
        
        text_lower = text.lower()
        
        if self._is_valid_word(text_lower):
            return {
                'isObfuscated': False,
                'status': 'valid',
                'confidence': 0.0,
                'patterns': [],
                'detected_signals': {k: False for k in ['vowel_omission', 'char_duplication', 
                                                        'leetspeak', 'symbol_separation', 'netspeak', 'phonetic']}
            }
        
        
        try:
            tokens = word_tokenize(normalize_input(text_lower))
            if not tokens:
                return self._empty_result()
            
            signals = {
                'vowel_omission': any(self.vowel_omission.is_accepted(t) for t in tokens),
                'char_duplication': any(self.char_duplication.is_accepted(t) for t in tokens),
                'leetspeak': any(self.leetspeak.is_accepted(t) for t in tokens),
                'symbol_separation': any(self.symbol_separation.is_accepted(t) for t in tokens),
                'netspeak': all(self.netspeak.is_accepted(t) for t in tokens) if len(tokens) > 1 else any(self.netspeak.is_accepted(t) for t in tokens),
                'phonetic': any(self.phonetic.is_accepted(t)['has_phonetic'] for t in tokens)
            }
            

            is_obfuscated = any(signals.values())
            confidence = self._calculate_confidence(signals) if is_obfuscated else 0.0
            print(f"[DEBUG] Text: '{text}', Tokens: {tokens}, Signals: {signals}")

            return {
                'isObfuscated': is_obfuscated,
                'status': 'obfuscated' if is_obfuscated else 'unknown',
                'confidence': confidence,
                'patterns': ['taglish_obfuscation'] if is_obfuscated else [],
                'detected_signals': signals
            }
        
        except Exception as e:
            print(f"[ERROR] Detection failed: {e}")
            return self._empty_result()
    
    def _empty_result(self) -> Dict:
        """Return empty/error result."""
        return {
            'isObfuscated': False,
            'status': 'empty',
            'confidence': 0.0,
            'patterns': [],
            'detected_signals': {k: False for k in ['vowel_omission', 'char_duplication', 
                                                    'leetspeak', 'symbol_separation', 'netspeak', 'phonetic']}
        }