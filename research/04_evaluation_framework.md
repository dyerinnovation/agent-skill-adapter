# Evaluation Framework

## Purpose
Measure how well a fine-tuned model follows a given Agent Skill, both during training (reward signal) and post-training (quality gate).

## Rubric Types

### Structural Rubrics
- Output contains required sections
- JSON/YAML output is valid
- Required fields present

### Behavioral Rubrics
- Correct tool usage (calls expected tools)
- No forbidden actions
- Follows conversation flow

### Content Rubrics
- Response addresses the prompt
- Factual consistency (via LLM judge)
- Style/tone matching

## Scoring
Each rubric item produces a score in [0, 1]. Items are weighted and aggregated:

```
reward = Σ(weight_i × score_i) / Σ(weight_i)
```

## LLM-as-Judge (optional)
For content rubrics that can't be verified programmatically, use a judge model to score. Configurable via `SKILL_ADAPTER_JUDGE_MODEL`.

## Metrics
- **Skill compliance rate**: % of rubric items passed (score > 0.5)
- **Average reward**: Mean reward across evaluation set
- **Regression check**: Compare against base model on same eval set
