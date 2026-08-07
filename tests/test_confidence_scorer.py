import pytest
import sys
import os

# Add src to Python path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.classifiers.confidence_scorer import calculate_confidence_score, determine_sensitivity_level

def test_calculate_confidence_score():
    # High confidence (patterns + context keywords)
    patterns = {'my_ic': ['900101-14-5555']}
    comprehend = []
    
    score = calculate_confidence_score(pattern_matches=patterns, comprehend_matches=comprehend, context_keywords_found=True)
    assert score == 0.7  # 0.4 (pattern) + 0.3 (context)
    
def test_determine_sensitivity_level():
    patterns = {'my_ic': ['900101-14-5555']}
    assert determine_sensitivity_level(patterns, []) == 'RESTRICTED'
    
    patterns = {'email': ['test@test.com']}
    assert determine_sensitivity_level(patterns, []) == 'CONFIDENTIAL'
    
    assert determine_sensitivity_level({}, []) == 'PUBLIC'
