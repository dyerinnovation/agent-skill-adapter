import uuid
from fastapi import APIRouter, HTTPException

from src.models.config import settings
from src.models.schemas import EvalRequest, EvalResult, EvalScore
from src.services.skill_loader import load_skills
from src.services.evaluator import evaluate_output
from src.services.trainer import SkillTrainer
from src.services.data_generator import generate_training_data

router = APIRouter()


@router.post("/run", response_model=EvalResult)
async def run_evaluation(request: EvalRequest):
    """Run evaluation against rubrics."""
    # Load skill
    skills = load_skills(settings.skills_dir)
    skill = None
    for s in skills:
        if s.id == request.skill_id:
            skill = s
            break
    
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill {request.skill_id} not found")
    
    # Generate eval ID
    eval_id = str(uuid.uuid4())
    
    # Prepare prompts
    prompts = request.prompts
    if not prompts:
        # Generate sample prompts from skill
        samples = generate_training_data(skill, num_samples=request.num_samples)
        prompts = [s["prompt"] for s in samples[:request.num_samples]]
    
    # Initialize model if adapter path provided
    all_scores: list[EvalScore] = []
    
    if request.model_path:
        trainer = SkillTrainer()
        trainer.load_adapter(request.model_path)
        
        # Generate responses and evaluate
        for prompt in prompts:
            response = trainer.generate(prompt)
            scores, _ = evaluate_output(response, skill.rubrics)
            all_scores.extend(scores)
    else:
        # No model - just evaluate empty output as baseline
        for _ in prompts:
            scores, _ = evaluate_output("", skill.rubrics)
            all_scores.extend(scores)
    
    # Compute aggregate score
    if all_scores:
        aggregate_score = sum(s.score for s in all_scores) / len(all_scores)
    else:
        aggregate_score = 0.0
    
    return EvalResult(
        eval_id=eval_id,
        skill_id=request.skill_id,
        scores=all_scores,
        aggregate_score=aggregate_score,
    )


@router.get("/results/{eval_id}", response_model=EvalResult)
async def get_results(eval_id: str):
    """Get evaluation results."""
    # In a real implementation, this would fetch from storage
    # For now, return a placeholder
    return EvalResult(
        eval_id=eval_id,
        skill_id="unknown",
        scores=[],
        aggregate_score=0.0,
    )
