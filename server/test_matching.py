from app.services.fuzzy_matching_service import FuzzyMatcher
from app.services.detection_service import DetectionService

ds = DetectionService()
fm = FuzzyMatcher(threshold=70)

print("Testing fuzzy matching improvements:\n")

# Test heLL0
matches_hello = fm.match_word('heLL0', list(ds.taglish_dictionary), limit=5)
print('heLL0 matches:')
for m in matches_hello:
    print(f"  {m['word']}: {m['score']:.1f}%")

# Test mg4
matches_mg4 = fm.match_word('mg4', list(ds.taglish_dictionary), limit=5)
print('\nmg4 matches:')
for m in matches_mg4:
    print(f"  {m['word']}: {m['score']:.1f}%")

# Check if words are in dictionary
print(f"\nDictionary check:")
print(f"  'mga' in dict: {'mga' in ds.taglish_dictionary}")
print(f"  'hello' in dict: {'hello' in ds.taglish_dictionary}")
print(f"  'hell' in dict: {'hell' in ds.taglish_dictionary}")
print(f"  'kababayan' in dict: {'kababayan' in ds.taglish_dictionary}")
