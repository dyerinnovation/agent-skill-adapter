"""Load and parse SKILL.md files into structured rubrics."""
from __future__ import annotations

import re
from pathlib import Path

from src.models.schemas import RubricItem, SkillInfo


def load_skills(skills_dir: str) -> list[SkillInfo]:
    """Load all SKILL.md files from the given directory."""
    skills: list[SkillInfo] = []
    skills_path = Path(skills_dir)
    if not skills_path.exists():
        return skills
    for skill_dir in skills_path.iterdir():
        if skill_dir.is_dir():
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                skills.append(parse_skill(skill_md))
    return skills


def parse_skill(path: Path) -> SkillInfo:
    """Parse a SKILL.md file into a SkillInfo."""
    content = path.read_text()
    description = _extract_description(content)
    rubrics = extract_rubrics(content)
    return SkillInfo(
        id=path.parent.name,
        path=str(path),
        description=description,
        rubrics=rubrics,
    )


def _extract_description(content: str) -> str:
    """Extract first paragraph after the title as description."""
    lines = content.strip().splitlines()
    desc_lines: list[str] = []
    past_title = False
    for line in lines:
        if line.startswith("# ") and not past_title:
            past_title = True
            continue
        if past_title:
            if line.strip() == "":
                if desc_lines:
                    break
                continue
            if line.startswith("#"):
                break
            desc_lines.append(line.strip())
    return " ".join(desc_lines)


def extract_rubrics(content: str) -> list[RubricItem]:
    """Extract verifiable rubric items from Constraints and Output Format sections."""
    rubrics: list[RubricItem] = []
    sections = _split_sections(content)

    for section_name, section_body in sections.items():
        lower = section_name.lower()
        if "constraint" in lower:
            category = "behavioral"
        elif "output" in lower and "format" in lower:
            category = "structural"
        else:
            continue

        items = _extract_list_items(section_body)
        for i, item in enumerate(items):
            rubrics.append(
                RubricItem(
                    name=f"{section_name}_{i}",
                    description=item,
                    weight=1.0,
                    category=category,
                )
            )

    return rubrics


def _split_sections(content: str) -> dict[str, str]:
    """Split markdown into {heading: body} pairs."""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in content.splitlines():
        match = re.match(r"^#{1,3}\s+(.+)$", line)
        if match:
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines)
            current_heading = match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines)

    return sections


def _extract_list_items(body: str) -> list[str]:
    """Extract markdown list items (- or *) from section body."""
    items: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^\s*[-*]\s+(.+)$", line)
        if match:
            items.append(match.group(1).strip())
    return items
