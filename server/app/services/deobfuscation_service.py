import re
import string
from .dictionary_service import cached_dictionaries

class DeobfuscationService:
   
    def __init__(self):
        self.leet_data = cached_dictionaries.get('leetspeak_map').data or {}
        self.morph_data = cached_dictionaries.get('morphology_patterns').data
        self.netspeak_data = cached_dictionaries.get('netspeak_patterns').data or {}
        
        self.transition_map = {}
        if self.leet_data and "character_substitutions" in self.leet_data:
            for char, subs in self.leet_data["character_substitutions"].items():
                for sub in subs:
                    self.transition_map[sub] = char

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
        
        shortcuts = {}
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

        for root_word, variations in shortcuts.items():
            if core_word in variations:
                return prefix + root_word + suffix
            
        if core_word.lower() in acronyms:
            return prefix + acronyms[core_word.lower()] + suffix
        
        for root_word, variations in leet_examples.items():
            if core_word in variations:
                return prefix + root_word + suffix

        if core_word in common_slang:
            return prefix + common_slang[core_word] + suffix
        
        # Single-letter mappings are now stored in the netspeak dictionaries
        # (e.g., "ko": ["q"]) so no hardcoded fallback here.

        output_buffer = []
        last_out_char = None
        consecutive_count = 0
        
        for char in core_word:
            translated_char = self.transition_map.get(char, char)

            if translated_char == last_out_char:
                consecutive_count += 1
            else:
                consecutive_count = 1

            if consecutive_count > 2:
                continue
            
            output_buffer.append(translated_char)
            last_out_char = translated_char

        decoded_word = "".join(output_buffer)

        return prefix + decoded_word + suffix