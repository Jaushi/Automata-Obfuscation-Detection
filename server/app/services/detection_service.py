import re
from .preprocessing_service import normalize_input, word_tokenize, extract_word
from .dictionary_service import load_and_cache_dictionaries, cached_dictionaries


# Automata template
class AutomatonState:
    def __init__(self, name, is_final=False):
        self.name = name
        self.is_final = is_final
        self.transitions = {}
# Automaton NFA Implementation
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

    def run(self, input_text: str):
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


# Automata Implementations
class VowelOmissionAutomaton:
    """NFA: Detect 3+ consecutive consonants"""
    def __init__(self):
        self.nfa = NFA()
        consonants = "bcdfghjklmnpqrstvwxyz"
        
        # States
        self.nfa.add_state("START")
        self.nfa.add_state("C1")
        self.nfa.add_state("C2")
        self.nfa.add_state("OBF", is_final=True)
        self.nfa.set_start("START")
        
        # Transitions
        self.nfa.add_transition("START", consonants, "C1")
        self.nfa.add_transition("C1", consonants, "C2")
        self.nfa.add_transition("C2", consonants, "OBF")
        self.nfa.add_transition("OBF", consonants, "OBF")  # stay in final state

    def detect(self, token: str) -> bool:
        return self.nfa.run(token)
    
class CharacterDuplicationAutomaton:
    """NFA: Detect 2+ consecutive duplicate characters (lengthening)"""
    def __init__(self):
        self.nfa = NFA()
        all_chars = "abcdefghijklmnopqrstuvwxyz"
        
        # Create START state
        self.nfa.add_state("START")
        self.nfa.set_start("START")
        
        # For each character, create a state chain that detects 2+ repetitions
        for char in all_chars:
            # States: CHAR_1 (first occurrence), CHAR_2+ (second+ occurrence, FINAL)
            state1 = f"{char}_1"
            state2 = f"{char}_2+"
            
            self.nfa.add_state(state1)
            self.nfa.add_state(state2, is_final=True)
            
            # START -> first occurrence of char
            self.nfa.add_transition("START", char, state1)
            
            # First -> second occurrence (now it's lengthened!)
            self.nfa.add_transition(state1, char, state2)
            
            # Keep accepting more of the same character
            self.nfa.add_transition(state2, char, state2)
            
            # Allow transitions to other characters' first states
            # Also allow transitions from state2 back to START to detect new sequences
            for other_char in all_chars:
                if other_char != char:
                    other_state1 = f"{other_char}_1"
                    self.nfa.add_transition(state1, other_char, other_state1)
                    self.nfa.add_transition(state2, other_char, other_state1)
                    # Allow START to accept any character at any point (for detecting duplication anywhere)
                    self.nfa.add_transition("START", other_char, other_state1)
        
    def detect(self, token: str) -> bool:
        """Detect if a token has 2+ consecutive duplicate characters"""
        return self.nfa.run(token.lower())


class LeetspeakAutomaton:
    #Detects leetspeak patterns based on character substitutions
    def __init__(self, leet_data):
        self.nfa = NFA()
        letters = "abcdefghijklmnopqrstuvwxyz"
        
        # Extract leet chars from dictionary
        leet_chars = set()
        if leet_data and 'character_substitutions' in leet_data:
            for subs in leet_data['character_substitutions'].values():
                if isinstance(subs, list):
                    leet_chars.update(subs)
                else:
                    leet_chars.add(subs)
        
        self.nfa.add_state("START")
        self.nfa.add_state("LETTER")
        self.nfa.add_state("LEET", is_final=True)
        self.nfa.set_start("START")
        
        self.nfa.add_transition("START", letters, "LETTER")
        self.nfa.add_transition("LETTER", letters, "LETTER")
        self.nfa.add_transition("START", "".join(leet_chars), "LEET")
        self.nfa.add_transition("LETTER", "".join(leet_chars), "LEET")
        self.nfa.add_transition("LEET", letters + "".join(leet_chars), "LEET")

    def detect(self, token: str) -> bool:
        return self.nfa.run(token)
    
class MorphologyResult:
    def __init__(self):
        self.valid = False
        self.prefix = None
        self.suffix = None
        self.lengthening = False

    def __bool__(self):
        return self.valid

class MorphologyAutomaton:
    # Morphological patterns detection (prefixes, suffixes, lengthening)
    def __init__(self, morph_data=None, shortcuts=None):
        self.nfa = NFA()

        letters = "abcdefghijklmnopqrstuvwxyz"
        vowels = "aeiou"
        consonants = "bcdfghjklmnpqrstvwxyz"

        # STATES
        self.nfa.add_state("START")
        self.nfa.add_state("PREFIX")
        self.nfa.add_state("ROOT")
        self.nfa.add_state("SUFFIX", is_final=True)
        self.nfa.add_state("LENGTHY", is_final=True)
        self.nfa.add_state("ROOT_FINAL", is_final=True)

        self.nfa.set_start("START")

        # ---------- PREFIXES ----------
        for p in ["mag", "nag", "pag"]:
            prev = "START"
            for c in p:
                state = f"{p}_{c}"
                if state not in self.nfa.states:
                    self.nfa.add_state(state)
                self.nfa.add_transition(prev, c, state)
                prev = state
            self.nfa.add_transition(prev, letters, "ROOT")

        # intensifiers
        for p in ["grabe", "sobrang"]:
            prev = "START"
            for c in p:
                state = f"{p}_{c}"
                if state not in self.nfa.states:
                    self.nfa.add_state(state)
                self.nfa.add_transition(prev, c, state)
                prev = state
            self.nfa.add_transition(prev, letters, "ROOT")

        # ---------- ROOT ----------
        self.nfa.add_transition("START", letters, "ROOT")
        self.nfa.add_transition("ROOT", letters, "ROOT")
        self.nfa.add_transition("ROOT", letters, "ROOT_FINAL")

        # ---------- SUFFIX ----------
        for s in "kmnp":  # ko, mo, na, pa
            self.nfa.add_transition("ROOT", s, "SUFFIX")
        self.nfa.add_transition("SUFFIX", letters, "SUFFIX")

    def detect(self, token: str) -> bool:
        """ONE TOKEN → ONE NFA RUN"""
        return self.nfa.run(token.lower())


class NetspeakAutomaton:
    """NFA: Detect short abbreviations (2-4 chars) from dictionary"""
    def __init__(self, netspeak_data):
        self.nfa = NFA()
        letters = "abcdefghijklmnopqrstuvwxyz0"
        
        self.nfa.add_state("START")
        self.nfa.add_state("SHORT", is_final=True)
        self.nfa.set_start("START")
        
        self.nfa.add_transition("START", letters, "SHORT")
        self.nfa.add_transition("SHORT", letters, "SHORT")
        
        # Build dictionary lookup for validation
        self.dict_lookup = set()
        if netspeak_data and 'filipino_netspeak' in netspeak_data:
            ns = netspeak_data['filipino_netspeak']
            
            # Add all abbreviations
            shortcuts = ns.get('filipino_shortcuts', {})
            for abbrevs in shortcuts.values():
                for abbrev in (abbrevs if isinstance(abbrevs, list) else [abbrevs]):
                    self.dict_lookup.add(abbrev.lower())
            
            # Add acronyms
            self.dict_lookup.update(ns.get('acronyms', {}).keys())
            
            # Add slang
            self.dict_lookup.update(ns.get('common_slang', {}).keys())

    def detect(self, token: str) -> bool:
        token_lower = token.lower()
        # NFA checks if short form + dictionary confirms it exists
        return 2 <= len(token_lower) <= 5 and self.nfa.run(token_lower) and token_lower in self.dict_lookup


class DetectionService:
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
        self.duplication = CharacterDuplicationAutomaton()
        self.leet = LeetspeakAutomaton(leet_data)
        self.morph = MorphologyAutomaton()  
        self.netspeak = NetspeakAutomaton(net_data)

    def analyze(self, code: str, language: str = 'unknown') -> dict:
        tokens = word_tokenize(normalize_input(code))
        
        # Extract words for detection (strip punctuation)
        words = [extract_word(t) for t in tokens if extract_word(t)]
        
        # Debug: Check each word for duplication
        duplication_details = {}
        for w in words:
            result = self.duplication.detect(w)
            if result or len(w) > 5:  # Log interesting words
                duplication_details[w] = result

        signals = {
            'vowel_omission': any(self.vowel.detect(w) for w in words),
            'character_duplication': any(self.duplication.detect(w) for w in words),
            'leetspeak': any(self.leet.detect(w) for w in words),
            'morphology': any(self.morph.detect(w) for w in words),
            'netspeak': any(self.netspeak.detect(w) for w in words)
        }

        detected = any(signals.values())
        confidence = sum(signals.values()) * 0.20

        return {
            'isObfuscated': detected,
            'confidence': min(confidence, 1.0),
            'patterns': ['taglish_obfuscation'] if detected else [],
            'taglish_signals': signals,
            'debug_tokens': tokens,
            'debug_duplication': duplication_details
        }