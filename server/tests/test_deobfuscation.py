import pytest
from app.services.deobfuscation_service import DeobfuscationService
from app.services.dictionary_service import load_and_cache_dictionaries

@pytest.fixture(scope="module", autouse=True)
def setup_dictionaries():
    load_and_cache_dictionaries()

def test_leetspeak_transitions():
    service = DeobfuscationService()
    assert service.deobfuscate("m4h4l") == "mahal"
    assert service.deobfuscate("k1t4") == "kita"

def test_repetition_filtering():
    service = DeobfuscationService()
    assert service.deobfuscate("mahal kl") == "mahal kl"
    assert service.deobfuscate("helloooo") == "helo" 

def test_netspeak_shortcuts():
    service = DeobfuscationService()
    assert service.deobfuscate("aq") == "ako"
    assert service.deobfuscate("bkt") == "bakit"