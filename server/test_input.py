import sys
sys.path.insert(0, '.')

from app.services.detection_service import DetectionService

# Test with multiple inputs
test_cases = [
    "Hel70 Pipol I m1ss y0u 4lL",  # English leetspeak (should work now!)
    "kumust4 k4 n4 p0",  # Filipino obfuscated
    "salamut mhl kita",  # Filipino typos
    "G00d m0rning w0rld",  # English obfuscated
]

print("\n" + "="*70)
print("🚀 TESTING HYBRID DICTIONARY APPROACH")
print("="*70)

ds = DetectionService()

print(f"\n📚 Dictionary loaded with {len(ds.taglish_dictionary)} words\n")

for test_text in test_cases:

    ds = DetectionService()
    result = ds.detect_with_fuzzy(test_text)

    print("\n" + "="*60)
    print("🔍 FUZZY MATCHING TEST")
    print("="*60)
    print(f"\n📝 Input: {result['original_text']}")
    print(f"\n🔎 Obfuscated: {result['is_obfuscated']}")
    print(f"📊 Confidence: {result['confidence']:.2%}")

    print(f"\n✨ Fuzzy Matches ({len(result['fuzzy_matches'])}):")
    if result['fuzzy_matches']:
        for match in result['fuzzy_matches']:
            print(f"   • \"{match['original']}\" → \"{match['corrected']}\" ({match['confidence']:.1%})")
    else:
        print("   No matches found")

    if 'deobfuscated' in result:
        print(f"\n✅ Deobfuscated: {result['deobfuscated']}")
        
    print("\n" + "="*60)
