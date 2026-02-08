"""Load and parse SKILL.md files into structured rubrics."""
from pathlib import Path


def load_skills(skills_dir: str) -> list[dict]:
    """Load all SKILL.md files from the given directory."""
    skills = []
    for skill_dir in Path(skills_dir).iterdir():
        if skill_dir.is_dir():
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                skills.append(parse_skill(skill_md))
    return skills


def parse_skill(path: Path) -> dict:
    """Parse a SKILL.md file into a structured dict."""
    content = path.read_text()
    return {
        "id": path.parent.name,
        "path": str(path),
        "content": content,
        "rubrics": extract_rubrics(content),
    }


def extract_rubrics(content: str) -> list[dict]:
    """Extract verifiable rubric items from skill content."""
    # TODO: implement rubric extraction from constraints/output format sections
    return []
