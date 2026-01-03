from rapidfuzz import fuzz, process
from typing import List, Dict, Optional


class FuzzyMatcher:
    # Fuzzy string matching for spell correction and partial word matches

    def __init__(self, threshold: int = 75):
        self.threshold = threshold

    def match_word(self, word: str, dictionary: List[str], limit: int = 3) -> List[Dict]:
        # Find fuzzy matches for a word in the dictionary
        if not word or not dictionary:
            return []

        raw_matches = process.extract(word.lower(), dictionary, scorer=fuzz.ratio, limit=limit * 3)

        results = []
        for match, base_score, _ in raw_matches:
            adjusted_score = base_score

            # Penalty for length mismatch
            len_diff = abs(len(match) - len(word))
            adjusted_score -= len_diff * 3

            # Bonus for longer words
            if len(match) >= 4:
                adjusted_score += (len(match) - 3) * 2

            # Bonus for prefix match
            if len(word) >= 2 and len(match) >= 2:
                prefix_matches = sum(1 for a, b in zip(word[:3], match[:3]) if a == b)
                adjusted_score += prefix_matches * 5

            # Bonus for exact length
            if len(match) == len(word):
                adjusted_score += 5

            # Lower threshold for short words
            effective_threshold = max(65, self.threshold - 10) if len(word) <= 3 else self.threshold
            adjusted_score = min(100, max(0, adjusted_score))

            if adjusted_score >= effective_threshold:
                results.append({
                    'word': match,
                    'score': adjusted_score,
                    'confidence': adjusted_score / 100
                })

        results.sort(key=lambda x: (x['score'], len(x['word'])), reverse=True)
        return results[:limit]

    def get_best_match(self, word: str, dictionary: List[str]) -> Optional[Dict]:
        # Get single best match for a word
        matches = self.match_word(word, dictionary, limit=1)
        return matches[0] if matches else None