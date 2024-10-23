# tests/test_helpers.py
import pytest
from Rufus.utils.helpers import compute_similarity


def test_compute_similarity():
    """Test the similarity computation between two texts."""
    text1 = "This is a sample text."
    text2 = "This is a sample text."
    similarity_score = compute_similarity(text1, text2)
    assert similarity_score == 1.0  # They should be identical

    text3 = "This is another sample."
    similarity_score = compute_similarity(text1, text3)
    assert similarity_score < 1.0  # Should be less than 1 for different texts
