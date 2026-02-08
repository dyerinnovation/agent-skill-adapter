"""Generate synthetic training data from skill specifications."""
from __future__ import annotations

import random
from typing import Any
from src.models.schemas import SkillInfo


def generate_training_data(
    skill: SkillInfo,
    num_samples: int = 100,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """
    Generate synthetic (prompt, response) pairs from skill specs.
    
    Args:
        skill: SkillInfo containing skill details and rubrics
        num_samples: Number of training samples to generate
        seed: Random seed for reproducibility
    
    Returns:
        List of {"prompt": str, "response": str} dictionaries
    """
    if seed is not None:
        random.seed(seed)
    
    samples: list[dict[str, Any]] = []
    
    # Extract trigger patterns and constraints from rubrics
    triggers = _extract_triggers(skill)
    constraints = _extract_constraints(skill)
    
    for i in range(num_samples):
        # Generate a prompt based on skill triggers
        prompt = _generate_prompt(skill, triggers, i)
        
        # Generate a response that satisfies constraints
        response = _generate_response(skill, constraints, i)
        
        samples.append({
            "prompt": prompt,
            "response": response,
        })
    
    return samples


def _extract_triggers(skill: SkillInfo) -> list[str]:
    """Extract trigger patterns from skill description and rubrics."""
    triggers: list[str] = []
    
    # Default trigger based on skill ID
    triggers.append(f"Use the {skill.id} skill")
    triggers.append(f"Apply {skill.id}")
    triggers.append(f"Execute {skill.id}")
    
    # Extract from description
    if skill.description:
        # Simple heuristic: look for action verbs
        action_words = ["create", "generate", "build", "implement", "design", "develop"]
        desc_lower = skill.description.lower()
        for action in action_words:
            if action in desc_lower:
                triggers.append(f"{action.capitalize()} using {skill.id}")
    
    return triggers


def _extract_constraints(skill: SkillInfo) -> list[str]:
    """Extract constraints from rubrics."""
    constraints: list[str] = []
    
    for rubric in skill.rubrics:
        if rubric.category == "behavioral":
            constraints.append(rubric.description)
        elif rubric.category == "structural":
            # Structural rubrics define output format
            constraints.append(rubric.description)
    
    return constraints if constraints else ["Provide a detailed response"]


def _generate_prompt(skill: SkillInfo, triggers: list[str], index: int) -> str:
    """Generate a prompt for the skill."""
    # Vary the trigger pattern
    trigger = triggers[index % len(triggers)]
    
    # Add some variety to the prompt
    variations = [
        f"{trigger} to solve this problem.",
        f"Please {trigger.lower()} for the following task.",
        f"I need help with {skill.id}. {trigger}.",
        f"{trigger} with the following requirements.",
    ]
    
    base_prompt = variations[index % len(variations)]
    
    # Add a task-specific component based on skill description
    if skill.description:
        task_detail = f" Task: {skill.description[:100]}"
    else:
        task_detail = f" Task: Complete the {skill.id} operation."
    
    return base_prompt + task_detail


def _generate_response(skill: SkillInfo, constraints: list[str], index: int) -> str:
    """Generate a response that satisfies constraints."""
    response_parts: list[str] = []
    
    # Start with a header
    response_parts.append(f"# {skill.id} Response\n")
    
    # Address each constraint
    for i, constraint in enumerate(constraints):
        constraint_lower = constraint.lower()
        
        # Generate section based on constraint type
        if "format" in constraint_lower:
            if "markdown" in constraint_lower:
                response_parts.append("## Formatted Output\n")
                response_parts.append("- Item 1\n- Item 2\n- Item 3\n")
            elif "json" in constraint_lower:
                response_parts.append("```json\n{\"result\": \"example\"}\n```\n")
            elif "list" in constraint_lower:
                response_parts.append("- Point A\n- Point B\n- Point C\n")
        
        elif "include" in constraint_lower:
            # Extract what should be included
            response_parts.append(f"## Section {i+1}\n")
            response_parts.append(f"This section addresses: {constraint}\n")
        
        else:
            # Generic constraint handling
            response_parts.append(f"## Constraint {i+1}\n")
            response_parts.append(f"Addressing: {constraint[:50]}...\n")
    
    # Add a conclusion
    response_parts.append("\n## Summary\n")
    response_parts.append(f"The {skill.id} skill has been successfully applied ")
    response_parts.append(f"with {len(constraints)} constraint(s) satisfied.\n")
    
    return "".join(response_parts)
