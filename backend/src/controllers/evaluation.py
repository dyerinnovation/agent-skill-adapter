from fastapi import APIRouter

router = APIRouter()


@router.post("/run")
async def run_evaluation():
    """Run evaluation against rubrics."""
    return {"status": "queued"}


@router.get("/results/{eval_id}")
async def get_results(eval_id: str):
    """Get evaluation results."""
    return {"eval_id": eval_id, "results": []}
