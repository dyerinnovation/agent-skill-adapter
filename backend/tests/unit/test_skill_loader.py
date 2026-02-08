"""Unit tests for skill_loader module."""
import tempfile
from pathlib import Path

import pytest

from src.models.schemas import RubricItem, SkillInfo
from src.services.skill_loader import (
    load_skills,
    parse_skill,
    extract_rubrics,
    _extract_description,
    _split_sections,
    _extract_list_items,
)


@pytest.fixture
def sample_skill_md():
    """Sample SKILL.md content."""
    return """# Test Skill

This is a test skill description.
It spans multiple lines.

## Context

Some context here.

## Constraints

- Must include proper formatting
- Should validate input data
- Must handle edge cases

## Output Format

- Response must be in JSON format
- Include all required fields
- Use proper indentation

## Examples

Example content here.
"""


@pytest.fixture
def temp_skills_dir(sample_skill_md):
    """Create a temporary skills directory with test skills."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_path = Path(tmpdir)
        
        # Create skill1
        skill1_dir = skills_path / "skill1"
        skill1_dir.mkdir()
        (skill1_dir / "SKILL.md").write_text(sample_skill_md)
        
        # Create skill2
        skill2_dir = skills_path / "skill2"
        skill2_dir.mkdir()
        (skill2_dir / "SKILL.md").write_text("# Skill 2\n\nSimple skill.")
        
        # Create a directory without SKILL.md
        skill3_dir = skills_path / "skill3"
        skill3_dir.mkdir()
        
        yield str(skills_path)


def test_load_skills_empty_dir():
    """Test loading skills from empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills = load_skills(tmpdir)
        assert skills == []


def test_load_skills_nonexistent_dir():
    """Test loading skills from nonexistent directory."""
    skills = load_skills("/nonexistent/path")
    assert skills == []


def test_load_skills(temp_skills_dir):
    """Test loading multiple skills."""
    skills = load_skills(temp_skills_dir)
    assert len(skills) == 2
    assert {s.id for s in skills} == {"skill1", "skill2"}


def test_parse_skill(temp_skills_dir):
    """Test parsing a SKILL.md file."""
    skill_path = Path(temp_skills_dir) / "skill1" / "SKILL.md"
    skill = parse_skill(skill_path)
    
    assert skill.id == "skill1"
    assert skill.path == str(skill_path)
    assert "test skill description" in skill.description.lower()
    assert len(skill.rubrics) > 0


def test_extract_description(sample_skill_md):
    """Test extracting description from SKILL.md."""
    description = _extract_description(sample_skill_md)
    assert "test skill description" in description.lower()
    assert "multiple lines" in description.lower()


def test_extract_description_no_title():
    """Test extracting description when there's no title."""
    content = "Just some text without a title."
    description = _extract_description(content)
    assert description == ""


def test_extract_description_empty():
    """Test extracting description from empty content."""
    description = _extract_description("")
    assert description == ""


def test_extract_rubrics(sample_skill_md):
    """Test extracting rubrics from SKILL.md."""
    rubrics = extract_rubrics(sample_skill_md)
    
    # Should extract from Constraints and Output Format sections
    assert len(rubrics) == 6  # 3 constraints + 3 output format items
    
    # Check categories
    behavioral = [r for r in rubrics if r.category == "behavioral"]
    structural = [r for r in rubrics if r.category == "structural"]
    
    assert len(behavioral) == 3
    assert len(structural) == 3
    
    # Check that rubrics have required fields
    for rubric in rubrics:
        assert rubric.name
        assert rubric.description
        assert rubric.weight == 1.0


def test_extract_rubrics_no_constraints():
    """Test extracting rubrics when there are no constraint sections."""
    content = """# Test Skill

Description here.

## Examples

Some examples.
"""
    rubrics = extract_rubrics(content)
    assert len(rubrics) == 0


def test_split_sections(sample_skill_md):
    """Test splitting markdown into sections."""
    sections = _split_sections(sample_skill_md)
    
    assert "Context" in sections
    assert "Constraints" in sections
    assert "Output Format" in sections
    assert "Examples" in sections
    
    # Check that section bodies contain expected content
    assert "Some context" in sections["Context"]
    assert "Must include" in sections["Constraints"]


def test_split_sections_empty():
    """Test splitting empty content."""
    sections = _split_sections("")
    assert sections == {}


def test_extract_list_items():
    """Test extracting list items from section body."""
    body = """Some intro text.

- Item 1
- Item 2
* Item 3

Not a list item.
"""
    items = _extract_list_items(body)
    assert len(items) == 3
    assert "Item 1" in items
    assert "Item 2" in items
    assert "Item 3" in items


def test_extract_list_items_no_lists():
    """Test extracting list items when there are none."""
    body = "Just regular text.\nNo lists here."
    items = _extract_list_items(body)
    assert items == []


def test_extract_list_items_indented():
    """Test extracting indented list items."""
    body = """
  - Indented item 1
    - Nested item (should still match)
"""
    items = _extract_list_items(body)
    assert len(items) == 2
