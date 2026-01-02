import re
from typing import Optional, Dict

from .preprocessing_service import normalize_input, word_tokenize
from .dictionary_service import load_and_cache_dictionaries, cached_dictionaries

class AutomatonState:
    def __init__(self, name, is_final=False):
        self.name = name
        self.is_final = is_final
        self.transitions = {}

class NFA:
    def __init__(self):
        self.states = {}
        self.start_state = None

    def add_state(self, name, is_final=False):
        state = AutomatonState(name, is_final)
        self.states[name] = state
        return state

    def set_start(self, name):
        self.start_state = name

    def add_transition(self, from_state, symbols, to_state):
        for sym in symbols:
            self.states[from_state].transitions.setdefault(sym, set()).add(to_state)

    def run(self, input_text: str) -> bool:
        if not self.start_state or self.start_state not in self.states:
            return False
        current = {self.start_state}
        for char in input_text.lower():
            next_states = set()
            for state in current:
                if char in self.states[state].transitions:
                    next_states |= self.states[state].transitions[char]
            if not next_states:
                break
            current = next_states
        return any(self.states[s].is_final for s in current)


class VowelOmissionAutomaton:
    def __init__(self):
        self.nfa = NFA()
        consonants = "bcdfghjklmnpqrstvwxyz"
        
        self.nfa.add_state("START")
        self.nfa.add_state("C1")
        self.nfa.add_state("C2")
        self.nfa.add_state("OBF", is_final=True)
        self.nfa.set_start("START")
        
        self.nfa.add_transition("START", consonants, "C1")
        self.nfa.add_transition("C1", consonants, "C2")
        self.nfa.add_transition("C2", consonants, "OBF")
        self.nfa.add_transition("OBF", consonants, "OBF")

    def detect(self, token: str) -> bool:
        return self.nfa.run(token)


class CharacterDuplicationAutomaton:
    """Detects repeated characters (e.g., 'hellooo', 'yessss')"""
    def __init__(self):
        self.pattern = re.compile(r'(.)\1{2,}')  # 3+ repeated chars
    
    def detect(self, token: str) -> bool:
        return bool(self.pattern.search(token.lower()))


class LeetspeakAutomaton:
    def __init__(self, leet_data):
        self.nfa = NFA()
        letters = "abcdefghijklmnopqrstuvwxyz"
        
        leet_chars = set()
        if leet_data and 'character_substitutions' in leet_data:
            for subs in leet_data['character_substitutions'].values():
                leet_chars.update(subs if isinstance(subs, list) else [subs])
        
        self.nfa.add_state("START")
        self.nfa.add_state("LETTER")
        self.nfa.add_state("LEET", is_final=True)
        self.nfa.set_start("START")
        
        leet_str = "".join(leet_chars)
        self.nfa.add_transition("START", letters, "LETTER")
        self.nfa.add_transition("LETTER", letters, "LETTER")
        self.nfa.add_transition("START", leet_str, "LEET")
        self.nfa.add_transition("LETTER", leet_str, "LEET")
        self.nfa.add_transition("LEET", letters + leet_str, "LEET")

    def detect(self, token: str) -> bool:
        return self.nfa.run(token)


class MorphologyAutomaton:
    def __init__(self, morph_data: Optional[Dict] = None):
        self.letters = "abcdefghijklmnopqrstuvwxyz"
        self.vowels = "aeiou"
        self.consonants = "bcdfghjklmnpqrstvwxyz"
        
        self.morph_data = morph_data or {}
        affixes = self.morph_data.get('affixes', {})
        
        # Filter out infixes from prefixes
        all_prefixes = affixes.get('prefixes', {})
        infixes_set = set(affixes.get('infixes', {}).keys())
        self.prefixes = [p for p in all_prefixes.keys() if p not in infixes_set]
        
        self.suffixes = list(affixes.get('suffixes', {}).keys())
        
        # Fallback defaults
        if not self.prefixes:
            self.prefixes = ['mag', 'nag', 'pag', 'ma', 'ka', 'pang', 'mang']
        if not self.suffixes:
            self.suffixes = ['an', 'han', 'in', 'hin']
        
        # Load validation rules
        rules = self.morph_data.get('validation_rules', {})
        self.min_word_length = rules.get('min_word_length', 2)
        self.min_root_after_prefix = rules.get('min_root_after_prefix', 2)
        self.min_root_before_suffix = rules.get('min_root_before_suffix', 2)
        
        # Build NFAs
        self.prefix_nfa = self._build_prefix_nfa()
        self.suffix_nfa = self._build_suffix_nfa()
        self.um_infix_nfa = self._build_um_infix_nfa()
        self.in_infix_nfa = self._build_in_infix_nfa()
        
        # Compile regex patterns
        obf_patterns = self.morph_data.get('obfuscation_patterns', {})
        
        lengthening = obf_patterns.get('lengthening', {})
        self.vowel_lengthening = re.compile(lengthening.get('vowel_lengthening', r'[aeiou]{2,}'))
        self.consonant_lengthening = re.compile(lengthening.get('consonant_lengthening', r'([bcdfghjklmnpqrstvwxyz])\1{1,}'))
        
        reduplication = obf_patterns.get('reduplication', {})
        self.full_reduplication = re.compile(reduplication.get('full_reduplication', r'^([a-z]{2,})\1+$'))
        self.cv_reduplication = re.compile(reduplication.get('cv_reduplication', r'^([bcdfghjklmnpqrstvwxyz][aeiou])\1[a-z]*$'))
        
        vowel_omission = obf_patterns.get('vowel_omission', {})
        self.consonant_cluster = re.compile(vowel_omission.get('consonant_cluster', r'[bcdfghjklmnpqrstvwxyz]{3,}'))
        self.all_consonants = re.compile(vowel_omission.get('all_consonants', r'^[bcdfghjklmnpqrstvwxyz]{2,}$'))
    
    def _build_prefix_nfa(self) -> NFA:
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("ROOT", is_final=True)
        nfa.set_start("START")
        
        for prefix in self.prefixes:
            if len(prefix) < 2:
                continue
            
            prev = "START"
            for i, ch in enumerate(prefix):
                state = f"P_{prefix}_{i}"
                if state not in nfa.states:
                    nfa.add_state(state)
                nfa.add_transition(prev, ch, state)
                prev = state
            
            # Must have min_root_after_prefix chars after prefix
            for _ in range(self.min_root_after_prefix):
                next_state = f"{prev}_ROOT"
                if next_state not in nfa.states:
                    nfa.add_state(next_state)
                nfa.add_transition(prev, self.letters, next_state)
                prev = next_state
            
            nfa.states[prev].is_final = True
            nfa.add_transition(prev, self.letters, prev)
        
        # Root without prefix
        nfa.add_transition("START", self.letters, "ROOT")
        nfa.add_transition("ROOT", self.letters, "ROOT")
        
        return nfa
    
    def _build_suffix_nfa(self) -> NFA:
        nfa = NFA()
        nfa.add_state("START")
        nfa.set_start("START")
        nfa.add_transition("START", self.letters, "START")
        
        for suffix in self.suffixes:
            prev = "START"
            for i, ch in enumerate(suffix):
                state = f"S_{suffix}_{i}"
                is_final = (i == len(suffix) - 1)
                if state not in nfa.states:
                    nfa.add_state(state, is_final=is_final)
                nfa.add_transition(prev, ch, state)
                prev = state
        
        return nfa
    
    def _build_um_infix_nfa(self) -> NFA:
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("C")
        nfa.add_state("U")
        nfa.add_state("M")
        nfa.add_state("ROOT", is_final=True)
        nfa.set_start("START")
        
        nfa.add_transition("START", self.consonants, "C")
        nfa.add_transition("C", "u", "U")
        nfa.add_transition("U", "m", "M")
        nfa.add_transition("M", self.letters, "ROOT")
        nfa.add_transition("ROOT", self.letters, "ROOT")
        
        return nfa
    
    def _build_in_infix_nfa(self) -> NFA:
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("C")
        nfa.add_state("I")
        nfa.add_state("N")
        nfa.add_state("ROOT", is_final=True)
        nfa.set_start("START")
        
        nfa.add_transition("START", self.consonants, "C")
        nfa.add_transition("C", "i", "I")
        nfa.add_transition("I", "n", "N")
        nfa.add_transition("N", self.letters, "ROOT")
        nfa.add_transition("ROOT", self.letters, "ROOT")
        
        return nfa
    
    def detect(self, token: str) -> bool:
        if not token or len(token) < self.min_word_length:
            return False
        
        t = token.lower()
        
        # Check affixes
        if self.prefix_nfa.run(t) or self.suffix_nfa.run(t):
            return True
        if self.um_infix_nfa.run(t) or self.in_infix_nfa.run(t):
            return True
        
        # Check obfuscation patterns
        patterns = [
            self.vowel_lengthening.search(t),
            self.consonant_lengthening.search(t),
            self.full_reduplication.match(t),
            self.cv_reduplication.match(t),
            self.consonant_cluster.search(t),
            len(t) >= 3 and self.all_consonants.match(t)
        ]
        
        return any(patterns)


class NetspeakAutomaton:
    def __init__(self, netspeak_data):
        self.nfa = NFA()
        letters = "abcdefghijklmnopqrstuvwxyz0123456789"
        
        self.nfa.add_state("START")
        self.nfa.add_state("SHORT", is_final=True)
        self.nfa.set_start("START")
        
        self.nfa.add_transition("START", letters, "SHORT")
        self.nfa.add_transition("SHORT", letters, "SHORT")
        
        self.dict_lookup = set()
        
        if netspeak_data and 'filipino_netspeak' in netspeak_data:
            ns = netspeak_data['filipino_netspeak']
            
            shortcuts = ns.get('filipino_shortcuts', {})
            for root, abbrevs in shortcuts.items():
                self.dict_lookup.add(root.lower())
                if isinstance(abbrevs, list):
                    self.dict_lookup.update(v.lower() for v in abbrevs)
                else:
                    self.dict_lookup.add(abbrevs.lower())
            
            acronyms = ns.get('acronyms', {})
            self.dict_lookup.update(k.lower() for k in acronyms.keys())
            
            slang = ns.get('common_slang', {})
            for meaning, slang_terms in slang.items():
                if isinstance(slang_terms, list):
                    self.dict_lookup.update(term.lower() for term in slang_terms if isinstance(term, str))
                else:
                    self.dict_lookup.add(slang_terms.lower())

    def detect(self, token: str) -> bool:
        token_clean = token.lower().strip('.,!?;:()[]{}"\'-')
        if not (2 <= len(token_clean) <= 6):
            return False
        return self.nfa.run(token_clean) and token_clean in self.dict_lookup


class DetectionService:
    def __init__(self):
        try:
            load_and_cache_dictionaries()
        except Exception as e:
            print(f"Warning: {e}")
        
        # Load dictionary data
        leet_obj = cached_dictionaries.get('leetspeak_map')
        leet_data = leet_obj.data if leet_obj else {}
        
        net_obj = cached_dictionaries.get('netspeak_patterns')
        net_data = net_obj.data if net_obj else {}
        
        morph_obj = cached_dictionaries.get('morphology_patterns')
        morph_data = morph_obj.data if morph_obj else {}
        
        # Initialize automatons
        self.vowel = VowelOmissionAutomaton()
        self.duplication = CharacterDuplicationAutomaton()  # FIXED: Added missing automaton
        self.leet = LeetspeakAutomaton(leet_data)
        self.morph = MorphologyAutomaton(morph_data)  # FIXED: Pass morph_data
        self.netspeak = NetspeakAutomaton(net_data)

    def analyze(self, text: str, language: str = 'unknown') -> dict:
        tokens = word_tokenize(normalize_input(text))
        
        signals = {
            'vowel_omission': any(self.vowel.detect(t) for t in tokens),
            'character_duplication': any(self.duplication.detect(t) for t in tokens),
            'leetspeak': any(self.leet.detect(t) for t in tokens),
            'morphology': any(self.morph.detect(t) for t in tokens),
            'netspeak': any(self.netspeak.detect(t) for t in tokens)
        }
        
        detected = any(signals.values())
        confidence = sum(signals.values()) * 0.20
        
        return {
            'isObfuscated': detected,
            'confidence': min(confidence, 1.0),
            'patterns': ['taglish_obfuscation'] if detected else [],
            'taglish_signals': signals,
            'debug_tokens': tokens
        }