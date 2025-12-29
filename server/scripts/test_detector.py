import importlib, traceback
from app.services.dictionary_service import load_and_cache_dictionaries, cached_dictionaries
from app.services.translation_service import process_and_translate

try:
    m = importlib.import_module('app.services.detection_service2')
    TaglishAutomataDetector = getattr(m, 'TaglishAutomataDetector', None)
    print('Imported detection module; TaglishAutomataDetector present =', TaglishAutomataDetector is not None)
except Exception:
    print('Exception importing app.services.detection_service2:')
    traceback.print_exc()
    TaglishAutomataDetector = None

if __name__ == '__main__':
    try:
        load_and_cache_dictionaries()
        print('Loaded dictionaries.')
    except Exception as e:
        print('Error loading dictionaries:', e)

    nets = cached_dictionaries.get('netspeak_patterns')
    shortcuts = {}
    if nets and getattr(nets, 'data', None):
        shortcuts = nets.data.get('filipino_shortcuts') or nets.data.get('filipino_netspeak', {}).get('filipino_shortcuts', {})

    text = 'm4h4l k1t4 q'
    try:
        translated = process_and_translate(text)
        print('Translated:', translated)
    except Exception as e:
        print('Translation error:', e)

    try:
        det = TaglishAutomataDetector(shortcuts)
        print('Detector:', det.detect(text))
    except Exception as e:
        print('Detector error:', e)
