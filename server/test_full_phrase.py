from app.services.detection_service import DetectionService
from app.services.fuzzy_matching_service import FuzzyMatcher

ds = DetectionService()
fm = FuzzyMatcher()

# Test individual words
print("Individual word matching:")
print("\n1. heLL0:")
matches = fm.match_word('heLL0', ds.taglish_dictionary, limit=5)
for m in matches:
    print(f"   {m['word']}: {m['score']:.1f}%")

print("\n2. mg4:")
matches = fm.match_word('mg4', ds.taglish_dictionary, limit=5)
for m in matches:
    print(f"   {m['word']}: {m['score']:.1f}%")

print("\n3. ka5a5ayan:")
matches = fm.match_word('ka5a5ayan', ds.taglish_dictionary, limit=5)
for m in matches:
    print(f"   {m['word']}: {m['score']:.1f}%")

# Test full phrase
print("\n\nFull phrase detection:")
result = ds.detect_with_fuzzy('heLL0 mg4 ka5a5ayan')
print(f'Deobfuscated: {result["deobfuscated"]}')
print(f'Confidence: {result["confidence"]:.1%}')
print('Matches:')
for m in result['fuzzy_matches']:
    print(f'  {m["original"]} -> {m["match"]} ({m["score"]:.1%})')
