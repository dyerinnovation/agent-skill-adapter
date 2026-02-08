"""Rubric-based evaluation service."""
from __future__ import annotations

import re
from src.models.schemas import RubricItem, EvalScore


def evaluate_output(output: str, rubrics: list[RubricItem]) -> tuple[list[EvalScore], float]:
    """
    Evaluate output text against rubrics.
    
    Args:
        output: Generated text to evaluate
        rubrics: List of rubric items to check
    
    Returns:
        Tuple of (list of scores, weighted aggregate score)
    """
    scores: list[EvalScore] = []
    total_weight = 0.0
    weighted_sum = 0.0
    
    for rubric in rubrics:
        score_val = _score_rubric(output, rubric)
        scores.append(
            EvalScore(
                rubric=rubric.name,
                score=score_val,
                detail=rubric.description,
            )
        )
        weighted_sum += score_val * rubric.weight
        total_weight += rubric.weight
    
    aggregate = weighted_sum / total_weight if total_weight > 0 else 0.0
    return scores, aggregate


def _score_rubric(output: str, rubric: RubricItem) -> float:
    """
    Score a single rubric item.
    
    Uses simple heuristics for structural checks:
    - Section presence checks
    - Format validation
    - Length checks
    
    Returns a score between 0.0 and 1.0
    """
    desc_lower = rubric.description.lower()
    output_lower = output.lower()
    
    # Check for section presence
    if "must include" in desc_lower or "should include" in desc_lower:
        # Extract what should be included (simple keyword matching)
        keywords = _extract_keywords(rubric.description)
        matches = sum(1 for kw in keywords if kw.lower() in output_lower)
        return min(1.0, matches / max(1, len(keywords)))
    
    # Check for format requirements
    if "format" in desc_lower:
        if "markdown" in desc_lower and _has_markdown_formatting(output):
            return 1.0
        if "json" in desc_lower and _is_valid_json_like(output):
            return 1.0
        if "list" in desc_lower or "bullet" in desc_lower:
            if re.search(r"^[\s]*[-*]\s", output, re.MULTILINE):
                return 1.0
        return 0.5
    
    # Check for length constraints
    if "at least" in desc_lower and "words" in desc_lower:
        word_count = len(output.split())
        match = re.search(r"(\d+)\s+words", desc_lower)
        if match:
            min_words = int(match.group(1))
            return 1.0 if word_count >= min_words else word_count / min_words
    
    # Default: presence check - if rubric mentions specific terms, check if they appear
    keywords = _extract_keywords(rubric.description)
    if keywords:
        matches = sum(1 for kw in keywords if kw.lower() in output_lower)
        return min(1.0, matches / len(keywords))
    
    # Fallback: assume passed if no specific criteria
    return 0.7


def _extract_keywords(text: str) -> list[str]:
    """Extract key terms from rubric description (simple heuristic)."""
    # Remove common words and extract capitalized terms or quoted terms
    quoted = re.findall(r"\"([^\"]+)\"", text)
    if quoted:
        return quoted
    
    # Extract words that might be important (longer words, capitalized)
    words = text.split()
    keywords = [
        w.strip(".,!?;:")
        for w in words
        if len(w) > 5 and not w.lower() in {"should", "include", "ensure", "provide"}
    ]
    return keywords[:5]  # Limit to 5 keywords


def _has_markdown_formatting(text: str) -> bool:
    """Check if text has markdown formatting."""
    patterns = [
        r"^#{1,6}\s",  # Headers
        r"\*\*.*\*\*",  # Bold
        r"\*.*\*",  # Italic
        r"```",  # Code blocks
        r"^\s*[-*]\s",  # Lists
    ]
    return any(re.search(p, text, re.MULTILINE) for p in patterns)


def _is_valid_json_like(text: str) -> bool:
    """Simple check for JSON-like structure."""
    stripped = text.strip()
    return (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]"))
