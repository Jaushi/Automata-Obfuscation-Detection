import re
from .dictionary_service import cached_dictionaries

class DeobfuscationService:
   
    def __init__(self):
        self.leet_data = cached_dictionaries.get('leetspeak_map').data
        self.morph_data = cached_dictionaries.get('morphology_patterns').data
        self.netspeak_data = cached_dictionaries.get('netspeak_patterns').data
        
        self.transition_map = {}
        if self.leet_data and "character_substitutions" in self.leet_data:
            for char, subs in self.leet_data["character_substitutions"].items():
                for sub in subs:
                    self.transition_map[sub] = char

    def deobfuscate(self, token: str) -> str:
        for root_word, variations in self.netspeak_data.get("filipino_shortcuts", {}).items():
            if token in variations:
                return root_word

        output_buffer = []
        last_out_char = None
        
        for char in token:
            translated_char = self.transition_map.get(char, char)

            if translated_char == last_out_char:
                continue
            
            output_buffer.append(translated_char)
            last_out_char = translated_char

        return "".join(output_buffer)