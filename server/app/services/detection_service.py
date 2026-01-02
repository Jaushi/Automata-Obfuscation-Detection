from .preprocessing_service import normalize_input, word_tokenize
from .dictionary_service import load_and_cache_dictionaries, cached_dictionaries




class AutomatonState:
    # Single state in a finite automaton
    def __init__(self, name, is_final=False):
        self.name = name
        self.is_final = is_final
        self.transitions = {}


class NFA:
    # Non-Deterministic Finite Automaton for pattern matching
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






#DETECTION AUTOMATONS


class VowelOmissionAutomaton:
    # Detects 3+ consecutive consonants (e.g., "strng" for "strong")
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






class LeetspeakAutomaton:
    # Detects leetspeak (e.g., "h3ll0" for "hello", "p4ss" for "pass")
    def __init__(self, leet_data):
        self.nfa = NFA()
        letters = "abcdefghijklmnopqrstuvwxyz"
       
        # Extract leet chars from dictionary
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
    """
    Detects Tagalog morphological obfuscation using NFAs only.
    Covers prefixes, suffixes, and the -um- infix.
    """


    def __init__(self):
        self.letters = "abcdefghijklmnopqrstuvwxyz"
        self.vowels = "aeiou"
        self.consonants = "".join(c for c in self.letters if c not in self.vowels)


        self.prefix_nfa = self._build_prefix_nfa()
        self.suffix_nfa = self._build_suffix_nfa()
        self.um_infix_nfa = self._build_um_infix_nfa()




    # PREFIXES: mag-, nag-, pag-, grabe-, sobrang-


    def _build_prefix_nfa(self):
        nfa = NFA()
        nfa.add_state("START")
        nfa.add_state("ROOT", is_final=True)
        nfa.set_start("START")


        prefixes = ["mag", "nag", "pag", "grabe", "sobrang"]


        for prefix in prefixes:
            prev = "START"
            for i, ch in enumerate(prefix):
                state = f"P_{prefix}_{i}"
                if state not in nfa.states:
                    nfa.add_state(state)
                nfa.add_transition(prev, ch, state)
                prev = state


            nfa.add_transition(prev, self.letters, "ROOT")


        nfa.add_transition("START", self.letters, "ROOT")
        nfa.add_transition("ROOT", self.letters, "ROOT")


        return nfa




    # SUFFIXES: -an/-han, -in/-hin, -ng, -asyon, -siyon


    def _build_suffix_nfa(self):
        nfa = NFA()
        nfa.add_state("START")
        nfa.set_start("START")


        suffixes = [
            "an", "han",
            "in", "hin",
            "ng",
            "asyon", "siyon"
        ]


        # Scan through the root
        nfa.add_transition("START", self.letters, "START")


        for suffix in suffixes:
            prev = "START"
            for i, ch in enumerate(suffix):
                state = f"S_{suffix}_{i}"
                is_final = (i == len(suffix) - 1)
                if state not in nfa.states:
                    nfa.add_state(state, is_final=is_final)
                nfa.add_transition(prev, ch, state)
                prev = state


        return nfa




    # INFIX: -um- (after first consonant)
    # e.g. sulat → sumulat


    def _build_um_infix_nfa(self):
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


    # DETECTION


    def detect(self, token: str) -> bool:
        t = token.lower()
        return (
            self.prefix_nfa.run(t) or
            self.suffix_nfa.run(t) or
            self.um_infix_nfa.run(t)
        )




class NetspeakAutomaton:
    # Detects internet abbreviations and acronyms (e.g., "btw", "hbd", "lol")
    def __init__(self, netspeak_data):
        self.nfa = NFA()
        letters = "abcdefghijklmnopqrstuvwxyz0123456789"
       
        self.nfa.add_state("START")
        self.nfa.add_state("SHORT", is_final=True)
        self.nfa.set_start("START")
       
        self.nfa.add_transition("START", letters, "SHORT")
        self.nfa.add_transition("SHORT", letters, "SHORT")
       
        # Build dictionary from netspeak data
        self.dict_lookup = set()
       
        if netspeak_data and 'filipino_netspeak' in netspeak_data:
            ns = netspeak_data['filipino_netspeak']
           
            # Shortcuts
            shortcuts = ns.get('filipino_shortcuts', {})
            for root, abbrevs in shortcuts.items():
                self.dict_lookup.add(root.lower())
                if isinstance(abbrevs, list):
                    self.dict_lookup.update(v.lower() for v in abbrevs)
                else:
                    self.dict_lookup.add(abbrevs.lower())
           
            # Acronyms
            acronyms = ns.get('acronyms', {})
            self.dict_lookup.update(k.lower() for k in acronyms.keys())
           
            # Slang
            slang = ns.get('common_slang', {})
            for meaning, slang_terms in slang.items():
                if isinstance(slang_terms, list):
                    self.dict_lookup.update(term.lower() for term in slang_terms if isinstance(term, str))
                else:
                    self.dict_lookup.add(slang_terms.lower())


    def detect(self, token: str) -> bool:
        # Clean and validate token
        token_clean = token.lower().strip('.,!?;:()[]{}"\'-')
       
        if not (2 <= len(token_clean) <= 6):
            return False
       
        return self.nfa.run(token_clean) and token_clean in self.dict_lookup




class DetectionService:
    # Main service: analyzes text for obfuscation patterns
    def __init__(self):
        try:
            load_and_cache_dictionaries()
        except Exception as e:
            print(f"Warning: {e}")


        leet_obj = cached_dictionaries.get('leetspeak_map')
        leet_data = leet_obj.data if leet_obj else {}


        net_obj = cached_dictionaries.get('netspeak_patterns')
        net_data = net_obj.data if net_obj else {}


        self.vowel = VowelOmissionAutomaton()
        self.leet = LeetspeakAutomaton(leet_data)
        self.morph = MorphologyAutomaton()
        self.netspeak = NetspeakAutomaton(net_data)


    def analyze(self, text: str, language: str = 'unknown') -> dict:
        # Analyze text for obfuscation patterns
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



