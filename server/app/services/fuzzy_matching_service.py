from rapidfuzz import fuzz, process
from typing import List, Dict, Optional

class FuzzyMatcher:
    def __init__(self, threshold: int = 80):
        self.threshold = threshold

    def match_word(self, word: str, dictionary: list[str], limit: int = 3):
        matches = process.extract(
            word.lower(),
            dictionary,
            scorer = fuzz.ratio,
            limit=limit * 3  # Get more candidates for better filtering
        )
        
        results = []
        for match, score, _ in matches: 
            # Calculate adjusted score with bonuses/penalties
            adjusted_score = score
            
            # Penalty for words that are shorter than input (prefer complete words)
            if len(match) < len(word):
                # Penalize by 5% per missing character
                penalty = (len(word) - len(match)) * 5
                adjusted_score -= penalty
            
            # Strong bonus for longer words (prefer complete words)
            if len(match) >= 4:
                length_bonus = (len(match) - 3) * 4
                adjusted_score += length_bonus
            
            # Bonus if the beginning matches well
            if len(word) >= 3 and len(match) >= 3:
                prefix_match = sum(1 for a, b in zip(word[:3].lower(), match[:3].lower()) if a == b)
                adjusted_score += prefix_match * 3
            
            # Exact length match bonus
            if len(match) == len(word):
                adjusted_score += 2
            
            # STRICT threshold - don't lower for short words
            # Short words need HIGHER confidence, not lower
            effective_threshold = self.threshold
            if len(word) <= 4:
                effective_threshold = max(90, self.threshold)  # Minimum 90% for short words
            
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
        matches = self.match_word(word, dictionary, limit = 1)
        return matches[0] if matches else None

    def deobfuscate_text(self, text: str, dictionary: List[str]) -> str: 
        words = text.split()
        deobfuscated = []

        for word in words: 
            if word.lower() in [d.lower() for d in dictionary]:
                deobfuscated.append(word)
            else:
                match = self.get_best_match(word, dictionary)
                if match: 
                    deobfuscated.append(match['word'])
                else:
                    deobfuscated.append(word)

        return ' '.join(deobfuscated)