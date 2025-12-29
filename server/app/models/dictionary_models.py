from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class DictionaryModel:
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def is_valid(self) -> bool:
        return self.error is None and bool(self.data)

@dataclass
class NetspeakPatterns(DictionaryModel):
    name: str = "netspeak_patterns"

@dataclass
class LeetspeakMap(DictionaryModel):
    name: str = "leetspeak_map"

@dataclass
class MorphologyPatterns(DictionaryModel):
    name: str = "morphology_patterns"