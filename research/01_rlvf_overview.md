# RLVF: Reinforcement Learning from Verifiable Feedback

## Summary
RLVF replaces human preference labels with programmatic verifiers. Instead of training a reward model from human comparisons (RLHF), we define rubrics that automatically score model outputs against skill specifications.

## Key Insight
Agent Skills (SKILL.md files) contain structured requirements: expected output formats, tool usage patterns, and behavioral constraints. These are directly convertible to verifiable rubrics.

## Pipeline
1. **Skill Parsing** — Extract requirements from SKILL.md into structured rubrics
2. **Synthetic Data Generation** — Generate (prompt, response) pairs using the base model
3. **Rubric Evaluation** — Score each response against extracted rubrics (0-1 per criterion)
4. **Reward Computation** — Aggregate rubric scores into a scalar reward
5. **Policy Optimization** — Fine-tune with GRPO/DPO using computed rewards

## Advantages over RLHF
- No human labelers needed
- Deterministic, reproducible rewards
- Scales linearly with number of skills
- Can iterate rapidly (change rubric → retrain)

## References
- Lightman et al., "Let's Verify Step by Step" (2023)
- DeepSeek-R1 technical report (2025) — GRPO without reward model
- OpenAI process reward models
