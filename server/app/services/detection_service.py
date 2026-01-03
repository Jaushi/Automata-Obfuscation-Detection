import re
from typing import Optional, Dict

from .preprocessing_service import normalize_input, word_tokenize
from .dictionary_service import load_and_cache_dictionaries, cached_dictionaries


class AutomatonState:
    def __init__(self, name, is_final=False):
        self.name = name
        self.is_final = is_final
        self.transitions = {}   # char -> set[state]
        self.epsilon = set()    # ε-transitions

class NFA:
    def __init__(self):
        self.states = {}
        self.start_state = None

    def add_state(self, name, is_final=False):
        if name not in self.states:
            self.states[name] = AutomatonState(name, is_final)
        else:
            self.states[name].is_final |= is_final
        return self.states[name]

    def set_start(self, name):
        self.start_state = name

    def add_transition(self, from_state, symbols, to_state):
        for sym in symbols:
            self.states[from_state].transitions.setdefault(sym, set()).add(to_state)

    def add_epsilon(self, from_state, to_state):
        self.states[from_state].epsilon.add(to_state)

    def _epsilon_closure(self, states):
        stack = list(states)
        closure = set(states)
        while stack:
            s = stack.pop()
            for nxt in self.states[s].epsilon:
                if nxt not in closure:
                    closure.add(nxt)
                    stack.append(nxt)
        return closure

    def run(self, text: str) -> bool:
        if not self.start_state:
            return False

        current_states = self._epsilon_closure({self.start_state})

        for char in text.lower():
            next_states = set()
            for state in current_states:
                if char in self.states[state].transitions:
                    next_states |= self.states[state].transitions[char]

            if not next_states:
                return False

            current_states = self._epsilon_closure(next_states)

        return any(self.states[s].is_final for s in current_states)

class VowelOmissionDetector:
    def __init__(self):
        self.nfa = NFA()
        consonants = "bcdfghjklmnpqrstvwxyz"

        self.nfa.add_state("START")
        self.nfa.add_state("C1")
        self.nfa.add_state("C2")
        self.nfa.add_state("MATCH", is_final=True)
        self.nfa.set_start("START")

        self.nfa.add_transition("START", consonants, "C1")
        self.nfa.add_transition("C1", consonants, "C2")
        self.nfa.add_transition("C2", consonants, "MATCH")
        self.nfa.add_transition("MATCH", consonants, "MATCH")

    def detect(self, token: str) -> bool:
        return self.nfa.run(token)

class CharDuplicationDetector:
    def __init__(self):
        self.nfa = NFA()
        letters = "abcdefghijklmnopqrstuvwxyz"

        self.nfa.add_state("START")
        self.nfa.set_start("START")

        # One state per character
        for ch in letters:
            self.nfa.add_state(f"ONE_{ch}")
            self.nfa.add_state(f"TWO_{ch}")
            self.nfa.add_state(f"MATCH_{ch}", is_final=True)

            self.nfa.add_transition("START", ch, f"ONE_{ch}")
            self.nfa.add_transition(f"ONE_{ch}", ch, f"TWO_{ch}")
            self.nfa.add_transition(f"TWO_{ch}", ch, f"MATCH_{ch}")
            self.nfa.add_transition(f"MATCH_{ch}", ch, f"MATCH_{ch}")

        # Reset on different character
        for ch1 in letters:
            for ch2 in letters:
                if ch1 != ch2:
                    self.nfa.add_transition(f"ONE_{ch1}", ch2, f"ONE_{ch2}")
                    self.nfa.add_transition(f"TWO_{ch1}", ch2, f"ONE_{ch2}")
                    self.nfa.add_transition(f"MATCH_{ch1}", ch2, f"ONE_{ch2}")

    def detect(self, token: str) -> bool:
        return self.nfa.run(token)


class LeetspeakDetector:
    def __init__(self, leet_data):
        self.nfa = NFA()
        letters = "abcdefghijklmnopqrstuvwxyz"

        leet_chars = set()
        if leet_data and 'character_substitutions' in leet_data:
            for subs in leet_data['character_substitutions'].values():
                leet_chars.update(subs if isinstance(subs, list) else [subs])

        leet_str = "".join(leet_chars)

        self.nfa.add_state("START")
        self.nfa.add_state("LETTER")
        self.nfa.add_state("MATCH", is_final=True)
        self.nfa.set_start("START")

        self.nfa.add_transition("START", letters, "LETTER")
        self.nfa.add_transition("LETTER", letters, "LETTER")
        self.nfa.add_transition("START", leet_str, "MATCH")
        self.nfa.add_transition("LETTER", leet_str, "MATCH")
        self.nfa.add_transition("MATCH", letters + leet_str, "MATCH")

    def detect(self, token: str) -> bool:
        return self.nfa.run(token)

class MorphologyDetector:
    """
    Detects Filipino morphological patterns (prefixes, suffixes, infixes)
    using separate NFAs.
    """
    def __init__(self, morph_data=None):
        self.letters = "abcdefghijklmnopqrstuvwxyz"
        self.consonants = "bcdfghjklmnpqrstvwxyz"

        morph_data = morph_data or {}
        affixes = morph_data.get("affixes", {})

        self.prefixes = list(affixes.get("prefixes", {}).keys())
        self.suffixes = list(affixes.get("suffixes", {}).keys())
        self.infixes = list(affixes.get("infixes", {}).keys())

        self.prefix_nfa = self._build_prefix_nfa()
        self.suffix_nfa = self._build_suffix_nfa()
        self.infix_nfa = self._build_infix_nfa()

    # ---------- PREFIX ----------
    def _build_prefix_nfa(self) -> NFA:
        """
        nag-, mag-, pag-, ka-, etc.
        """
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("ROOT", is_final=True)
        nfa.set_start("START")

        for prefix in self.prefixes:
            prev = "START"
            for i, ch in enumerate(prefix):
                state = f"P_{prefix}_{i}"
                nfa.add_state(state)
                nfa.add_transition(prev, ch, state)
                prev = state

            # after prefix → root
            nfa.add_transition(prev, self.letters, "ROOT")

        nfa.add_transition("ROOT", self.letters, "ROOT")
        return nfa

    # ---------- SUFFIX ----------
    def _build_suffix_nfa(self) -> NFA:
        """
        -an, -in, -han, etc.
        """
        nfa = NFA()
        nfa.add_state("START")
        nfa.set_start("START")

        # root loop
        nfa.add_transition("START", self.letters, "START")

        for suffix in self.suffixes:
            prev = "START"
            for i, ch in enumerate(suffix):
                state = f"S_{suffix}_{i}"
                is_final = (i == len(suffix) - 1)
                nfa.add_state(state, is_final=is_final)
                nfa.add_transition(prev, ch, state)
                prev = state

        return nfa

    # ---------- INFIX ----------
    def _build_infix_nfa(self) -> NFA:
        """
        um, in, etc.
        Pattern: consonant + infix + root
        """
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("C")
        nfa.set_start("START")

        nfa.add_transition("START", self.consonants, "C")

        for infix in self.infixes:
            prev = "C"
            for i, ch in enumerate(infix):
                state = f"INF_{infix}_{i}"
                nfa.add_state(state)
                nfa.add_transition(prev, ch, state)
                prev = state

            root_state = f"ROOT_{infix}"
            nfa.add_state(root_state, is_final=True)
            nfa.add_transition(prev, self.letters, root_state)
            nfa.add_transition(root_state, self.letters, root_state)

        return nfa

    def detect(self, token: str) -> bool:
        if len(token) < 3:
            return False

        t = token.lower()
        return (
            self.prefix_nfa.run(t) or
            self.suffix_nfa.run(t) or
            self.infix_nfa.run(t)
        )

class NetspeakDetector:
    """
    Detects Filipino netspeak using a PURE NFA:
    - single-token abbreviations (u, lol, omg)
    - multi-token phrases (thank you, oh my god)
    """

    def __init__(self, netspeak_data):
        self.nfa = NFA()

        terms = set()
        if netspeak_data and "filipino_netspeak" in netspeak_data:
            ns = netspeak_data["filipino_netspeak"]
            for key in [
                "filipino_shortcuts",
                "acronyms",
                "common_slang",
                "filipino_english",
                "common_phrases",
            ]:
                data = ns.get(key, {})
                for root, abbrevs in data.items():
                    terms.add(root.lower())
                    if isinstance(abbrevs, list):
                        for a in abbrevs:
                            terms.add(str(a).lower())
                    elif abbrevs:
                        terms.add(str(abbrevs).lower())

        self.single_tokens = set()
        self.multi_tokens = set()

        for t in terms:
            t = t.strip()
            if " " in t:
                self.multi_tokens.add(t)
            elif 1 <= len(t) <= 6:
                self.single_tokens.add(t)

        self._build_nfa()

    # --------------------------------------------------

    def _build_nfa(self):
        self.nfa.add_state("START")
        self.nfa.set_start("START")

        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789 '"

        # Σ* scan (allows match anywhere in text)
        self.nfa.add_transition("START", alphabet, "START")

        # ---- SINGLE TOKEN WORDS ----
        for word in self.single_tokens:
            prev = "START"
            for i, ch in enumerate(word):
                state = f"SINGLE_{word}_{i}"
                is_final = (i == len(word) - 1)
                self.nfa.add_state(state, is_final=is_final)
                self.nfa.add_transition(prev, ch, state)
                prev = state

        # ---- MULTI TOKEN PHRASES ----
        for phrase in self.multi_tokens:
            prev = "START"
            for i, ch in enumerate(phrase):
                state = f"MULTI_{phrase}_{i}"
                is_final = (i == len(phrase) - 1)
                self.nfa.add_state(state, is_final=is_final)
                self.nfa.add_transition(prev, ch, state)
                prev = state

    # --------------------------------------------------
    # PUBLIC API (IMPORTANT PART)

    def detect_single_token(self, token: str) -> bool:
        token = token.lower().strip('.,!?;:()[]{}"\'-')
        return self.nfa.run(token)

    def detect_multi_token(self, text: str) -> bool:
        # RAW TEXT — spaces preserved
        return self.nfa.run(text.lower())
    
    def detect(self, token: str, *, multi: bool = False) -> bool:
        return (
            self.detect_multi_token(token)
            if multi
            else self.detect_single_token(token)
        )


class DetectionService:
    """
    Main detection service - uses NFAs to find obfuscation patterns
    
    This service coordinates multiple specialized detectors:
    - VowelOmissionDetector: txt, plz, thx
    - CharDuplicationDetector: hellooo, yesss
    - LeetspeakDetector: h3ll0, p4ssw0rd
    - MorphologyDetector: Filipino affixes (nag-, -um-, -in)
    - NetspeakDetector: u, ty, lol, omg
    """
    def __init__(self):
        # Load dictionaries
        try:
            load_and_cache_dictionaries()
        except Exception as e:
            print(f"Warning: {e}")
        
        leet_data = cached_dictionaries.get('leetspeak_map')
        net_data = cached_dictionaries.get('netspeak_patterns')
        morph_data = cached_dictionaries.get('morphology_patterns')
        
        # DEBUG: Check what was loaded
        print(f"[DEBUG DetectionService] leet_data: {leet_data}")
        print(f"[DEBUG DetectionService] net_data: {net_data}")
        print(f"[DEBUG DetectionService] morph_data: {morph_data}")
        
        if net_data:
            print(f"[DEBUG DetectionService] net_data.data keys: {net_data.data.keys() if hasattr(net_data, 'data') else 'NO DATA ATTR'}")
        
        # Initialize all detectors
        self.vowel = VowelOmissionDetector()
        self.duplication = CharDuplicationDetector()
        self.leet = LeetspeakDetector(leet_data.data if leet_data else {})
        self.morph = MorphologyDetector(morph_data.data if morph_data else {})
        self.netspeak = NetspeakDetector(net_data.data if net_data else {})

    def analyze(self, text: str, language: str = 'unknown') -> dict:
        tokens = word_tokenize(normalize_input(text))

        # MULTI-token netspeak → run on RAW TEXT
        has_multi_token_netspeak = self.netspeak.detect_multi_token(text)

        signals = {
            'vowel_omission': any(self.vowel.detect(t) for t in tokens),
            'character_duplication': any(self.duplication.detect(t) for t in tokens),
            'leetspeak': any(self.leet.detect(t) for t in tokens),
            'morphology': any(self.morph.detect(t) for t in tokens),

            # SINGLE-token netspeak → run per token
            'netspeak': (
                has_multi_token_netspeak or
                any(self.netspeak.detect_single_token(t) for t in tokens)
            )
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
