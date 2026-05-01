"""Tests for weighted_comparison module."""
import copy
import sys
import os

# Add kbt-core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kbt-core'))

from normalized_values import with_normalized_value


def test_with_weighted_comparison_basic():
    """Test basic weighted comparison calculation."""
    items = [
        {'value': 10, 'score': 2.0},
        {'value': 20, 'score': 3.0},
        {'value': 30, 'score': 5.0},
    ]
    
    # Total score = 2.0 + 3.0 + 5.0 = 10.0
    # Expected weighted values:
    # item 0: 10 * 2.0 / 10.0 = 2.0
    # item 1: 20 * 3.0 / 10.0 = 6.0
    # item 2: 30 * 5.0 / 10.0 = 15.0
    
    result = with_normalized_value(items, 'value', 'weighted_', 'score')
    
    assert result[0] == 10.0  # total_score
    assert items[0]['weighted_value'] == 2.0
    assert items[1]['weighted_value'] == 6.0
    assert items[2]['weighted_value'] == 15.0


def test_with_weighted_comparison_returns_tuple():
    """Test that function returns a tuple with (total_score, function)."""
    items = [
        {'value': 10, 'score': 1.0},
    ]
    
    result = with_normalized_value(items, 'value', 'weighted_', 'score')
    
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert result[0] == 1.0  # total_score
    assert result[1] == with_normalized_value  # function reference


def test_with_weighted_comparison_empty_list():
    """Test behavior with empty list - returns (0, function) without error."""
    items = []
    
    result = with_normalized_value(items, 'value', 'weighted_', 'score')
    
    # Empty list produces total_score of 0, no iteration so no division by zero
    assert result[0] == 0
    assert result[1] == with_normalized_value
    assert items == []

