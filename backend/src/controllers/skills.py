from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_skills():
    """List all loaded skills."""
    return {"skills": []}


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """Get details for a specific skill."""
    return {"skill_id": skill_id}
