import re
import string
from .preprocessing_service import extract_word
from .detection_service import NFA, AutomatonState
from .dictionary_service import cached_dictionaries
from .fuzzy_matching_service import FuzzyMatcher


class LeetspeakReversalAutomaton:
    """NFA-based leetspeak reversal: detects and converts leet chars to normal letters"""
    def __init__(self, leet_data):
        self.transition_map = {}
        if leet_data and "character_substitutions" in leet_data:
            for char, subs in leet_data["character_substitutions"].items():
                for sub in (subs if isinstance(subs, list) else [subs]):
                    self.transition_map[sub.lower()] = char.lower()
        
        # Build NFA to detect leetspeak patterns
        self.nfa = NFA()
        letters = "abcdefghijklmnopqrstuvwxyz"
        leet_chars = "".join(set(self.transition_map.keys()))
        
        self.nfa.add_state("START")
        self.nfa.add_state("LETTER")
        self.nfa.add_state("LEET", is_final=True)
        self.nfa.add_state("MIXED", is_final=True)
        self.nfa.set_start("START")
        
        self.nfa.add_transition("START", letters, "LETTER")
        self.nfa.add_transition("LETTER", letters, "LETTER")
        self.nfa.add_transition("START", leet_chars, "LEET")
        self.nfa.add_transition("LETTER", leet_chars, "MIXED")
        self.nfa.add_transition("LEET", leet_chars + letters, "MIXED")
        self.nfa.add_transition("MIXED", leet_chars + letters, "MIXED")

    def detect(self, token: str) -> bool:
        """Detect if token contains leetspeak characters"""
        return self.nfa.run(token.lower())

    def reverse(self, token: str) -> str:
        """Convert leetspeak characters to normal letters using transition map"""
        return "".join(self.transition_map.get(c, c) for c in token.lower())


class DuplicationNormalizationAutomaton:
    """NFA-based duplication normalization: detects and normalizes character duplications"""
    def __init__(self):
        self.nfa = NFA()
        all_chars = "abcdefghijklmnopqrstuvwxyz"
        
        self.nfa.add_state("START")
        self.nfa.set_start("START")
        
        # Build NFA to detect 2+ consecutive duplicates
        for char in all_chars:
            state1 = f"{char}_1"
            state2 = f"{char}_2+"
            
            self.nfa.add_state(state1)
            self.nfa.add_state(state2, is_final=True)
            
            self.nfa.add_transition("START", char, state1)
            self.nfa.add_transition(state1, char, state2)
            self.nfa.add_transition(state2, char, state2)
            
            # Allow transitions to other characters
            for other_char in all_chars:
                if other_char != char:
                    other_state1 = f"{other_char}_1"
                    self.nfa.add_transition(state1, other_char, other_state1)
                    self.nfa.add_transition(state2, other_char, other_state1)
                    self.nfa.add_transition("START", other_char, other_state1)

    def detect(self, token: str) -> bool:
        """Detect if token has 2+ consecutive duplicate characters"""
        return self.nfa.run(token.lower())

    def normalize(self, token: str) -> str:
        """Normalize duplications: keep max 2 consecutive (for common doubles), else 1"""
        output_buffer = []
        last_out_char = None
        consecutive_count = 0
        common_doubles = {'l', 's', 'n', 'm', 'r', 't', 'p', 'd', 'g', 'c', 'b', 'f'}
        
        for char in token.lower():
            if char == last_out_char:
                consecutive_count += 1
            else:
                consecutive_count = 1
            
            # Keep max 2 for common doubles, max 1 for others
            max_allowed = 2 if char in common_doubles else 1
            
            if consecutive_count <= max_allowed:
                output_buffer.append(char)
            # else: skip (consecutive_count > max_allowed)
            
            last_out_char = char
        
        return "".join(output_buffer)


class LeetspeakReversalAutomaton:
    """NFA-based leetspeak reversal: detects and converts leet chars to normal letters"""
    def __init__(self, leet_data):
=======
class DeobfuscationService:
    """Service for deobfuscating obfuscated text using finite state automata"""
    def __init__(self):
        leet_obj = cached_dictionaries.get('leetspeak_map')
        self.leet_data = leet_obj.data if leet_obj else {}
        
        morph_obj = cached_dictionaries.get('morphology_patterns')
        self.morph_data = morph_obj.data if morph_obj else {}
        
        net_obj = cached_dictionaries.get('netspeak_patterns')
        self.netspeak_data = net_obj.data if net_obj else {}
        
        # Reversal automata (NFA-based) - ONLY FOR DEOBFUSCATION
        self.rev_leet = LeetspeakReversalAutomaton(self.leet_data)
        self.rev_duplication = DuplicationNormalizationAutomaton()
        
        # Initialize FuzzyMatcher with threshold of 85 for final refinement
        self.fuzzy_matcher = FuzzyMatcher(threshold=85)
        
        # Build word dictionary for fuzzy matching
        from .dictionary_service import get_filipino_words
        self.word_dict = set()
        if self.netspeak_data and 'filipino_netspeak' in self.netspeak_data:
            ns = self.netspeak_data['filipino_netspeak']
            shortcuts = ns.get('filipino_shortcuts', {})
            self.word_dict.update(shortcuts.keys())
            self.word_dict.update(ns.get('acronyms', {}).keys())
            self.word_dict.update(ns.get('common_slang', {}).keys())
        
        # Add Filipino dictionary words for fuzzy matching
        filipino_words = get_filipino_words()
        self.word_dict.update(filipino_words)
    
    def deobfuscate(self, token: str) -> str:
        # netspeak JSON may nest shortcuts under a top-level key like 'filipino_netspeak'
        match = re.match(r"^([^\w]*)([\w@]+)([^\w]*)$", token)

        prefix, core_word, suffix = "", token, ""
        if match:
            prefix = match.group(1)
            core_word = match.group(2)
            suffix = match.group(3)
        
        if not core_word:
            return token
        
        """Deobfuscate a single token, preserving punctuation"""
        if not token:
            return token
        
        # Extract prefix, core word, and suffix (preserve punctuation)
        match = re.match(r"^([^\w]*)([\w@$!|€]+)([^\w]*)$", token)
        prefix, core_word, suffix = "", token, ""
        if match:
            prefix = match.group(1)
            core_word = match.group(2)
            suffix = match.group(3)
        
        if not core_word:
            return token
        
        core_lower = core_word.lower()
        
        # Check netspeak shortcuts, acronyms, and slang first
        shortcuts = {}
        common_slang = {}
        acronyms = {}
        leet_examples = {}

        common_slang = {}
        acronyms = {}
        leet_examples = {}
        
        if isinstance(self.netspeak_data, dict):
            inner = self.netspeak_data.get("filipino_netspeak", {})

            if isinstance(inner, dict):
                shortcuts = inner.get("filipino_shortcuts", {})
                common_slang = inner.get("common_slang", {})
                acronyms = inner.get("acronyms", {})
            else:
                # if structure is flat
                shortcuts = self.netspeak_data.get("filipino_shortcuts", {})

        if isinstance(self.leet_data, dict):
            leet_examples = self.leet_data.get("filipino_leet_examples", {})

            inner = self.netspeak_data.get("filipino_netspeak", {})
            if isinstance(inner, dict):
                shortcuts = inner.get("filipino_shortcuts", {})
                common_slang = inner.get("common_slang", {})
                acronyms = inner.get("acronyms", {})
        
        if isinstance(self.leet_data, dict):
            leet_examples = self.leet_data.get("filipino_leet_examples", {})
        
        # Check shortcuts
        for root_word, variations in shortcuts.items():
            if core_lower in variations:
                return prefix + root_word + suffix
        
        # Check acronyms
        if core_lower in acronyms:
            return prefix + acronyms[core_lower] + suffix
        
        # Check leet examples
        for root_word, variations in leet_examples.items():
            if core_lower in variations:
                return prefix + root_word + suffix
        
        # Check common slang
        if core_lower in common_slang:
            return prefix + common_slang[core_lower] + suffix
        
        # ========== NFA-BASED DEOBFUSCATION ==========
        result = core_lower
        
        # Apply leetspeak reversal if detected
        if self.rev_leet.detect(result):
            result = self.rev_leet.reverse(result)
        
        # Apply duplication normalization if detected
        if self.rev_duplication.detect(result):
            result = self.rev_duplication.normalize(result)
        
        # Re-check duplication after transformations
        if self.rev_duplication.detect(result):
            result = self.rev_duplication.normalize(result)
        
        # ========== FUZZY MATCHING REFINEMENT (FINAL STEP) ==========
        # Only apply fuzzy matching if result not already in dictionary
        if self.word_dict and result not in self.word_dict:
            match = self.fuzzy_matcher.get_best_match(result, list(self.word_dict))
            if match:
                result = match['word']
        
        return prefix + result + suffix