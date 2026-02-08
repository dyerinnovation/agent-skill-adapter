from fastapi import APIRouter, HTTPException

from src.models.config import settings
from src.models.schemas import SkillInfo
from src.services.skill_loader import load_skills

router = APIRouter()


@router.get("/", response_model=list[SkillInfo])
async def list_skills():
    """List all loaded skills."""
    skills = load_skills(settings.skills_dir)
    return skills


@router.get("/{skill_id}", response_model=SkillInfo)
async def get_skill(skill_id: str):
    """Get details for a specific skill."""
    skills = load_skills(settings.skills_dir)
    for skill in skills:
        if skill.id == skill_id:
            return skill
    raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")
