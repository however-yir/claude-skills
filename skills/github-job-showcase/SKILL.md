---
name: github-job-showcase
description: Use when packaging GitHub projects for jobs, internships, interviews, or public portfolio use. Trigger this for README rewrites, project positioning, resume bullets, interview story extraction, repo cleanup, feature highlight framing, and turning raw coursework or side projects into stronger showcase material.
argument-hint: "[repo link or project description]"
version: "1.0.0"
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# GitHub Job Showcase

Use this skill when the work is about presenting your projects better, not merely coding them.

This skill is especially useful for student projects, capstone systems, recommendation platforms, AI demos, and portfolio repositories that have real work inside them but weak external framing.

## Inputs

Useful inputs for this skill include:
- the repository link or local project folder
- current README, resume bullets, or portfolio text if they exist
- the target audience such as recruiters, interviewers, internship applications, or GitHub visitors
- the strongest technical evidence in the repo, such as architecture, algorithms, roles, or deployment
- the type of deliverable needed, such as README rewrite, summary paragraph, or interview talking points

## Outputs

Strong outputs from this skill usually include:
- a one-sentence project positioning statement
- 3 to 6 concrete highlights tied to visible repo evidence
- README or portfolio copy with stronger external framing
- resume-friendly bullets and interview talking points
- honest wording that upgrades clarity without inflating claims

## Non-goals

This skill is not the best fit for:
- implementing large new features inside the codebase
- visual social content as the primary output
- vague hype that is not supported by repo evidence
- generic career advice disconnected from an actual project artifact

## Workflow

1. Identify the evidence.
Start from what the repo can actually prove:
- business flow
- feature depth
- architecture choices
- algorithms
- deployment or operations
- user roles
- measurable outcomes

2. Position the project.
Decide how the project should be framed:
- engineering foundation
- algorithm plus system integration
- AI exploration
- full-stack delivery
- operational maturity
- domain problem solving

3. Rewrite for external readers.
Produce the right artifact for the context:
- README structure
- resume bullets
- project summary paragraph
- interview talking points
- feature highlight list
- portfolio or showcase copy

4. Keep claims honest.
Do not inflate. If a project is a learning project, present it strongly but truthfully. Emphasize the strongest real evidence.

## Good Showcase Output

Strong output usually includes:
- a crisp one-sentence project positioning
- 3 to 6 specific highlights
- stack plus architecture evidence
- what problem it solves
- what makes it more than CRUD
- how to talk about it in interviews

## Examples

### Example 1: README rewrite
User request:
> Rewrite this README so my recruitment system feels stronger for internship applications.

Good use of this skill:
- identify what the repo already proves
- improve project positioning and highlight structure
- avoid pretending the project is larger than it is

### Example 2: Resume bullet extraction
User request:
> 提炼这个仓库的简历项目描述，控制在 3 条以内。

Good use of this skill:
- turn visible implementation work into compact bullets
- emphasize architecture, recommendation logic, and multi-role workflow where real
- keep each bullet interview-defensible

### Example 3: Interview prep packaging
User request:
> Help me package this AI demo into something I can explain clearly in interviews.

Good use of this skill:
- extract problem, solution, technical choices, and tradeoffs
- build talking points that match the actual repository scope
- frame learning projects as engineering evidence, not fake production products

## Pairing With Other Skills

Use these when useful:
- `github-ops` for repo hygiene and GitHub-side work
- `docs-write` and `technical-writer` for README and docs polish
- `frontend-design` and `ui-designer` for visual showcase pages
- `ppt-creator` or `office-doc-presentation` for interview decks
- `xiaohongshu-content-studio` if the repo will also be packaged into public content

## Triggers

Common requests that should trigger this skill:
- "帮我包装 GitHub 项目"
- "Rewrite this README for jobs"
- "提炼项目亮点"
- "把这个仓库改得更适合面试"
- "写成简历项目描述"

## Reference

Read [references/checklist.md](references/checklist.md) when you need a quick project-packaging checklist.
