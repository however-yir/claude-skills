---
name: local-ai-systems-studio
description: Use when turning a local AI idea, issue, or workflow request into a concrete system plan and the main uncertainty is still about the local stack itself. Covers task scoping, local model and tool evaluation, deployment choices such as MLX, GGUF, Ollama, LM Studio, or vLLM, hardware fit, workflow direction, and issue-to-plan conversion. Trigger this for local LLM selection, tool comparison, deployment tradeoffs, setup planning, and "how should I build this locally" requests. If the stack is already known and the main work is deeper workflow orchestration, use ai-agent-workflow instead.
argument-hint: "[local AI question or workflow idea]"
version: "1.0.0"
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, WebFetch, WebSearch, Glob, Grep
---

# Local AI Systems Studio

Use this skill when the user is trying to build, improve, or choose a local AI workflow end to end and the main uncertainty is still about the local stack, deployment path, or tool choice.

This skill combines four jobs into one coherent operating flow:
- frame the real problem
- evaluate candidate models and tools
- choose a practical local deployment path
- turn the decision into an execution plan

It should usually be the first stop when the user is still deciding between local runtimes, serving tools, or model formats.

## Inputs

Useful inputs for this skill include:
- the task or problem the local AI system should solve
- current hardware constraints such as Mac, RAM, GPU, or offline requirements
- preferred tools such as LM Studio, Ollama, MLX, GGUF, vLLM, MCP, or local scripts
- quality bar, latency expectations, privacy requirements, and maintenance tolerance
- any existing workflow draft, issue, bug report, or prompt stack

## Outputs

Strong outputs from this skill usually include:
- a clarified job-to-be-done statement
- model and tool comparison with practical tradeoffs
- a recommended local deployment path
- a workflow design or system architecture outline
- a phased execution plan with risks, dependencies, and next steps
- explicit notes about what should stay simple and what deserves more engineering

## Non-goals

This skill is not the best fit for:
- pure cloud-only AI stack decisions with no local component
- deep prompt-system design once the local stack is already known
- detailed agent orchestration work where the main challenge is workflow composition rather than local tool choice
- one-off copywriting or content generation tasks
- deep code changes inside a single existing backend module
- highly specialized model training or research benchmarking beyond practical deployment decisions

## Workflow

1. Frame the task.
Clarify what the system should repeatedly do:
- generate
- summarize
- extract
- retrieve
- route
- evaluate
- assist through tools

2. Decide the control surface.
Choose whether this is best handled by:
- a prompt-only flow
- a local app such as LM Studio or Ollama
- an MLX or GGUF model path
- a reusable skill
- an MCP integration
- a scripted workflow with checkpoints

3. Evaluate candidate tools and models.
Compare based on:
- hardware fit
- speed and latency
- output quality
- context needs
- privacy or offline requirements
- setup and maintenance cost

4. Recommend the local stack.
Explain the stack choice in practical terms, such as:
- MLX for Apple Silicon efficiency
- GGUF for broad local compatibility
- LM Studio for GUI-first workflows
- Ollama for simple serving and APIs
- vLLM when throughput and serving matter more than simplicity

5. Convert the decision into a plan.
Turn the chosen direction into:
- milestones
- configuration tasks
- testing checkpoints
- failure risks
- the smallest next action that unlocks progress

If the stack is now clear but the workflow still needs deeper decomposition, hand off to `ai-agent-workflow`.

## Examples

### Example 1: Local tool choice
User request:
> I want to run Qwen locally on my Mac and build a document workflow. Should I use LM Studio, Ollama, MLX, or something else?

Good use of this skill:
- identify whether the user cares most about GUI convenience, scripting, speed, or offline privacy
- compare tool paths honestly
- recommend one primary stack and one fallback
- turn the decision into a short setup and validation plan

### Example 2: Workflow architecture
User request:
> Help me build a local AI workflow that reads PDFs, extracts tasks, and generates a clean summary.

Good use of this skill:
- anchor the answer in local stack fit first
- define the repeatable stages clearly
- separate model work from tool work
- choose the simplest stack that meets the quality bar
- add lightweight validation instead of unnecessary agent complexity

### Example 3: Issue to execution plan
User request:
> My local AI workflow is too slow and unreliable. Help me figure out what to fix first.

Good use of this skill:
- frame the issue as latency, model fit, tool orchestration, or validation weakness
- compare likely bottlenecks
- recommend the highest-leverage fixes first
- output a concrete plan instead of generic AI advice

## Pairing With Other Skills

Use these when appropriate:
- `ai-agent-workflow` when the local stack is already chosen and the workflow now needs deeper prompt and tool orchestration detail
- `mcp-server-builder` for real tool integration work
- `prompt-optimizer` when prompt quality is the main bottleneck
- `deep-research` when model or tool selection depends on structured external research
- `skill-creator` if the finished workflow should become a reusable public skill

## Triggers

Common requests that should trigger this skill:
- "How should I build this local AI workflow?"
- "Which local model and tool stack should I choose?"
- "Should I use MLX, GGUF, LM Studio, or Ollama?"
- "Which local stack fits my Mac and my workflow?"
- "Turn this local AI idea into an execution plan"
- "Help me evaluate tools for a local agent workflow"

## Reference

Read [references/checklist.md](references/checklist.md) when you need a compact end-to-end checklist for local AI system planning.
