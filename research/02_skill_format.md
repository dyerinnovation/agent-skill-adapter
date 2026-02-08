# Agent Skill Format Specification

## What is a SKILL.md?
A SKILL.md is a markdown document that defines an agent capability. It specifies what the agent should do, what tools it can use, what output format to produce, and constraints on behavior.

## Structure
```markdown
# Skill Name
Description of what this skill does.

## Triggers
When this skill should activate (keywords, contexts).

## Tools
- tool_name: description of how to use it

## Output Format
Expected structure of the response.

## Constraints
- Must not do X
- Always do Y
- Format requirements
```

## Parsing Strategy
1. Extract sections by heading level
2. Convert "Constraints" into boolean rubric items
3. Convert "Output Format" into structural validators
4. Convert "Tools" into tool-usage checkers

## Example Rubric Extraction
From a constraint "Always include a Sources section with URLs":
- `has_sources_section`: Check output contains "## Sources" or "Sources:"
- `sources_contain_urls`: Check sources section has valid URLs
