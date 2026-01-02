import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services.dictionary_service import load_and_cache_dictionaries
from app.services.deobfuscation_service import DeobfuscationService

load_and_cache_dictionaries()
print(DeobfuscationService().deobfuscate('h3LLO'))
