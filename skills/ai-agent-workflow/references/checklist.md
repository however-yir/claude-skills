# AI Agent Workflow Checklist

## Frame the Problem

- What is the repeatable task?
- What input format does it start with?
- What output format must be stable?
- What errors matter most?

## Choose the Mechanism

- Prompt only
- Prompt plus references
- Prompt plus tools
- MCP integration
- Custom skill
- Scripted substep

## Add Reliability

- Define validation criteria.
- Add explicit output shape.
- Include revision or comparison steps if quality matters.
- Avoid hidden assumptions about user context or file layout.
