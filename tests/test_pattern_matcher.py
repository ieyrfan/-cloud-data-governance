import pytest
import sys
import os

# Add src to Python path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.classifiers.pattern_matcher import is_luhn_valid, find_sensitive_patterns

def test_luhn_valid_credit_card():
    # Valid test CC number according to Luhn algorithm
    assert is_luhn_valid("49927398716") == True
    # Invalid
    assert is_luhn_valid("49927398717") == False

def test_find_sensitive_patterns_my_ic():
    text = "User provided the IC number 900101-14-5555 for registration."
    results = find_sensitive_patterns(text)
    assert '900101-14-5555' in results['my_ic']
    
def test_find_sensitive_patterns_my_phone():
    text = "Call me at 012-3456789 or 011-12345678."
    results = find_sensitive_patterns(text)
    assert '012-3456789' in results['my_phone']
    assert '011-12345678' in results['my_phone']

def test_find_sensitive_patterns_email():
    text = "Contact support@example.com for more info."
    results = find_sensitive_patterns(text)
    assert 'support@example.com' in results['email']

def test_find_sensitive_patterns_no_match():
    text = "This is a clean document with no sensitive data."
    results = find_sensitive_patterns(text)
    assert len(results['my_ic']) == 0
    assert len(results['my_phone']) == 0
    assert len(results['email']) == 0
    assert len(results['credit_card']) == 0
