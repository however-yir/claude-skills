# Showcase Examples

These examples are designed to show how this skill turns loose AI ideas into reusable systems instead of one-off prompts.

They also make the routing boundary visible in a GitHub-friendly way:

- use this skill after the stack direction is already mostly known
- route local stack choice and hardware-fit questions to `local-ai-systems-studio`
- route skill authoring and skill benchmarking requests to `skill-creator`

## Example 1: Workflow Architecture After The Stack Is Chosen

**Prompt**

`I already decided to use OpenAI API and MCP for this document workflow. Help me structure the stages, tool calls, checks, and outputs so it becomes reusable.`

**A strong output should include**

- clear stage separation between extraction, summarization, and review
- tool and prompt boundaries
- stable input and output definitions
- a lightweight validation step for quality control

**Why this showcases the skill**

It shows the skill can design a repeatable AI workflow once the core stack decision is already made.

**Route elsewhere if**

- the user is still deciding between LM Studio, Ollama, MLX, GGUF, or hardware options
- the main request is model/tool evaluation rather than workflow design

## Example 2: Skill vs Script vs MCP Decision

**Prompt**

`I have a repeatable content workflow. Tell me whether it should become a prompt, a skill, a script, or an MCP server.`

**A strong output should include**

- honest comparison of control surfaces
- recommendation based on reuse, maintenance cost, and tool needs
- clear next step instead of abstract theory
- explanation of tradeoffs the user will actually feel

**Why this showcases the skill**

This is the kind of decision-oriented output that makes a workflow skill feel mature rather than merely descriptive.

**Route elsewhere if**

- the next concrete ask becomes `write the skill for me`
- the user wants to benchmark or improve an existing skill description
- the work is now primarily about the skill artifact, not the workflow decision

## Example 3: Agent Evaluation Loop

**Prompt**

`Design a practical eval loop for my agent so I can compare prompts and know whether quality is improving.`

**A strong output should include**

- measurable success criteria
- failure categories
- compare-and-revise loop design
- a minimal evaluation process before heavier automation

**Why this showcases the skill**

It proves the skill is about system reliability, not just prompt writing.

**Route elsewhere if**

- the evaluation target is a skill package rather than an agent workflow
- the user wants trigger-rate testing or skill-description optimization specifically
