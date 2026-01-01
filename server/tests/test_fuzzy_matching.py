import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.fuzzy_matching_service import FuzzyMatcher
from app.services.detection_service import DetectionService
from app.services.dictionary_service import load_and_cache_dictionaries


@pytest.fixture(scope="module", autouse=True)
def setup_dictionaries():
    """Load dictionaries before running tests"""
    load_and_cache_dictionaries()


class TestFuzzyMatcher:
    """Test suite for FuzzyMatcher class"""
    
    def test_fuzzy_matcher_initialization(self):
        """Test FuzzyMatcher initializes with correct threshold"""
        fm = FuzzyMatcher(threshold=80)
        assert fm.threshold == 80
        
    def test_match_word_exact_match(self):
        """Test matching when word exists in dictionary"""
        fm = FuzzyMatcher(threshold=75)
        dictionary = ['kumusta', 'salamat', 'mahal']
        matches = fm.match_word('kumusta', dictionary, limit=1)
        
        assert len(matches) > 0
        assert matches[0]['word'] == 'kumusta'
        assert matches[0]['score'] == 100
        
    def test_match_word_close_match(self):
        """Test fuzzy matching with similar word"""
        fm = FuzzyMatcher(threshold=75)
        dictionary = ['kumusta', 'salamat', 'mahal']
        matches = fm.match_word('kumust4', dictionary, limit=1)
        
        assert len(matches) > 0
        assert matches[0]['word'] == 'kumusta'
        assert matches[0]['score'] >= 75
        assert matches[0]['confidence'] >= 0.75
        
    def test_match_word_no_match(self):
        """Test when no word matches threshold"""
        fm = FuzzyMatcher(threshold=90)
        dictionary = ['kumusta', 'salamat', 'mahal']
        matches = fm.match_word('xyz123', dictionary, limit=1)
        
        assert len(matches) == 0
        
    def test_match_word_multiple_matches(self):
        """Test returning multiple matches"""
        fm = FuzzyMatcher(threshold=70)
        dictionary = ['kumusta', 'salamat', 'mahal', 'ako', 'ikaw']
        matches = fm.match_word('kumust', dictionary, limit=3)
        
        assert len(matches) <= 3
        assert all(m['score'] >= 70 for m in matches)
        
    def test_get_best_match(self):
        """Test getting single best match"""
        fm = FuzzyMatcher(threshold=75)
        dictionary = ['kumusta', 'salamat', 'mahal']
        match = fm.get_best_match('kumust4', dictionary)
        
        assert match is not None
        assert match['word'] == 'kumusta'
        assert 'confidence' in match
        
    def test_get_best_match_no_result(self):
        """Test best match returns None when no match"""
        fm = FuzzyMatcher(threshold=95)
        dictionary = ['kumusta', 'salamat', 'mahal']
        match = fm.get_best_match('xyz123', dictionary)
        
        assert match is None
        
    def test_deobfuscate_text_simple(self):
        """Test deobfuscating simple text"""
        fm = FuzzyMatcher(threshold=75)
        dictionary = ['kumusta', 'salamat', 'mahal', 'ako', 'ikaw']
        
        result = fm.deobfuscate_text('kumust4 salamut', dictionary)
        assert 'kumusta' in result
        assert 'salamat' in result
        
    def test_deobfuscate_text_mixed(self):
        """Test deobfuscating text with both matched and unmatched words"""
        fm = FuzzyMatcher(threshold=75)
        dictionary = ['kumusta', 'salamat', 'mahal']
        
        result = fm.deobfuscate_text('kumust4 xyz salamut', dictionary)
        assert 'kumusta' in result
        assert 'salamat' in result
        assert 'xyz' in result  # Unmatched word stays


class TestDetectionService:
    """Test suite for DetectionService with fuzzy matching"""
    
    def test_detection_service_initialization(self):
        """Test DetectionService initializes correctly"""
        ds = DetectionService()
        assert ds.fuzzy_matching_service is not None
        assert ds.taglish_dictionary is not None
        assert len(ds.taglish_dictionary) > 0
        
    def test_dictionary_loading(self):
        """Test dictionary loads words from JSON files"""
        ds = DetectionService()
        
        # Should contain words from netspeak patterns
        assert any('kumusta' in word or 'ako' in word for word in ds.taglish_dictionary)
        
    def test_detect_with_fuzzy_obfuscated(self):
        """Test detecting obfuscated text"""
        ds = DetectionService()
        result = ds.detect_with_fuzzy('kumust4 k4 salamut')
        
        assert result['is_obfuscated'] is True
        assert 'fuzzy_matches' in result
        assert len(result['fuzzy_matches']) > 0
        assert 'original_text' in result
        assert result['original_text'] == 'kumust4 k4 salamut'
        
    def test_detect_with_fuzzy_clean_text(self):
        """Test detecting clean (non-obfuscated) text"""
        ds = DetectionService()
        result = ds.detect_with_fuzzy('hello world')
        
        assert 'fuzzy_matches' in result
        assert 'is_obfuscated' in result
        
    def test_detect_with_fuzzy_confidence(self):
        """Test confidence calculation"""
        ds = DetectionService()
        result = ds.detect_with_fuzzy('kumust4 salamut')
        
        assert 'confidence' in result
        assert 0 <= result['confidence'] <= 1
        
    def test_detect_with_fuzzy_deobfuscation(self):
        """Test deobfuscated text generation"""
        ds = DetectionService()
        result = ds.detect_with_fuzzy('kumust4 salamut')
        
        if result['fuzzy_matches']:
            assert 'deobfuscated' in result
            assert result['deobfuscated'] != result['original_text']
            
    def test_detect_with_fuzzy_match_details(self):
        """Test fuzzy match details structure"""
        ds = DetectionService()
        result = ds.detect_with_fuzzy('kumust4')
        
        if result['fuzzy_matches']:
            match = result['fuzzy_matches'][0]
            assert 'original' in match
            assert 'corrected' in match
            assert 'confidence' in match
            assert match['original'] == 'kumust4'


class TestFuzzyMatchingIntegration:
    """Integration tests for complete fuzzy matching workflow"""
    
    def test_filipino_obfuscated_text(self):
        """Test with real Filipino obfuscated text"""
        ds = DetectionService()
        test_cases = [
            ('kumust4 k4', 'kumusta'),
            ('salamut po', 'salamat'),
            ('mhl kita', 'mahal'),
        ]
        
        for obfuscated, expected_word in test_cases:
            result = ds.detect_with_fuzzy(obfuscated)
            assert result['is_obfuscated'] or expected_word.lower() in obfuscated.lower()
            
    def test_multiple_obfuscations(self):
        """Test text with multiple obfuscations"""
        ds = DetectionService()
        result = ds.detect_with_fuzzy('kumust4 k4 n4 salamut')
        
        assert 'fuzzy_matches' in result
        if result['fuzzy_matches']:
            assert len(result['fuzzy_matches']) >= 1
            
    def test_threshold_sensitivity(self):
        """Test different threshold levels"""
        ds = DetectionService()
        
        # Lower threshold - more matches
        ds.fuzzy_matching_service.threshold = 70
        result_low = ds.detect_with_fuzzy('kumst')
        
        # Higher threshold - fewer matches
        ds.fuzzy_matching_service.threshold = 90
        result_high = ds.detect_with_fuzzy('kumst')
        
        assert len(result_low['fuzzy_matches']) >= len(result_high['fuzzy_matches'])
        
    def test_empty_text(self):
        """Test with empty text"""
        ds = DetectionService()
        result = ds.detect_with_fuzzy('')
        
        assert 'fuzzy_matches' in result
        assert result['fuzzy_matches'] == []
        
    def test_special_characters(self):
        """Test text with special characters"""
        ds = DetectionService()
        result = ds.detect_with_fuzzy('kumust4! k4? salamut.')
        
        assert 'original_text' in result
        assert result['is_obfuscated'] is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
