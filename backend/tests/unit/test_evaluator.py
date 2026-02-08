"""Unit tests for evaluator module."""
import pytest

from src.models.schemas import RubricItem
from src.services.evaluator import (
    evaluate_output,
    _score_rubric,
    _extract_keywords,
    _has_markdown_formatting,
    _is_valid_json_like,
)


@pytest.fixture
def sample_rubrics():
    """Sample rubric items for testing."""
    return [
        RubricItem(
            name="format_check",
            description="Output must be in markdown format",
            weight=1.0,
            category="structural",
        ),
        RubricItem(
            name="content_check",
            description="Must include proper error handling",
            weight=2.0,
            category="behavioral",
        ),
        RubricItem(
            name="length_check",
            description="Response should be at least 50 words",
            weight=1.0,
            category="structural",
        ),
    ]


def test_evaluate_output_basic(sample_rubrics):
    """Test basic output evaluation."""
    output = """# Test Output

This is a **properly formatted** markdown response.
It includes proper error handling mechanisms.
""" + " word" * 50  # Add enough words
    
    scores, aggregate = evaluate_output(output, sample_rubrics)
    
    assert len(scores) == 3
    assert all(score.score >= 0.0 and score.score <= 1.0 for score in scores)
    assert aggregate >= 0.0 and aggregate <= 1.0
    
    # Check that scores have required fields
    for score in scores:
        assert score.rubric
        assert score.detail


def test_evaluate_output_empty():
    """Test evaluating empty output."""
    rubrics = [
        RubricItem(
            name="test",
            description="Must include content",
            weight=1.0,
            category="behavioral",
        )
    ]
    
    scores, aggregate = evaluate_output("", rubrics)
    
    assert len(scores) == 1
    assert scores[0].score < 1.0
    assert aggregate < 1.0


def test_evaluate_output_no_rubrics():
    """Test evaluation with no rubrics."""
    scores, aggregate = evaluate_output("Some output", [])
    
    assert scores == []
    assert aggregate == 0.0


def test_score_rubric_markdown_format():
    """Test scoring markdown format rubric."""
    rubric = RubricItem(
        name="format",
        description="Output must be in markdown format",
        weight=1.0,
        category="structural",
    )
    
    markdown_output = """# Title

**Bold text** and *italic*.

- List item
"""
    plain_output = "Just plain text."
    
    markdown_score = _score_rubric(markdown_output, rubric)
    plain_score = _score_rubric(plain_output, rubric)
    
    assert markdown_score == 1.0
    assert plain_score < 1.0


def test_score_rubric_json_format():
    """Test scoring JSON format rubric."""
    rubric = RubricItem(
        name="format",
        description="Output must be in JSON format",
        weight=1.0,
        category="structural",
    )
    
    json_output = '{"key": "value"}'
    non_json_output = "Not JSON"
    
    json_score = _score_rubric(json_output, rubric)
    non_json_score = _score_rubric(non_json_output, rubric)
    
    assert json_score == 1.0
    assert non_json_score < 1.0


def test_is_valid_json_like_object():
    """Test detecting JSON object."""
    assert _is_valid_json_like('{"key": "value"}')
    assert not _is_valid_json_like('{"incomplete"')


def test_has_markdown_formatting_headers():
    """Test detecting markdown headers."""
    assert _has_markdown_formatting("# Header")
    assert not _has_markdown_formatting("Not a header")
