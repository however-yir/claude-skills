---
name: java-fullstack-engineering
description: Use when working on Java full-stack engineering tasks, especially Spring Boot, MyBatis or JPA, SQL, Vue or React admin systems, backend APIs, performance issues, refactors, or interview-grade project hardening. Trigger this for feature development, bug fixes, code review, schema tuning, API cleanup, and turning student or side projects into stronger engineering work.
argument-hint: "[bug, feature, or refactoring task]"
version: "1.0.0"
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch
---

# Java Fullstack Engineering

Use this skill when the task is primarily about shipping, fixing, hardening, or explaining a Java full-stack project rather than exploring AI workflows or producing presentation materials.

This skill is optimized for projects like campus systems, management backends, recommendation platforms, and Spring Boot plus frontend applications. It keeps the work grounded in engineering quality: correctness, maintainability, API clarity, database safety, and verification.

## Inputs

Useful inputs for this skill include:
- repository or module context
- stack details such as Spring Boot, MyBatis, JPA, Vue, React, MySQL, Redis
- bug reports, failing behavior, stack traces, or screenshots
- performance symptoms such as slow SQL, slow endpoints, or heavy pages
- API contracts, schema notes, or interview-presentation goals

## Outputs

Strong outputs from this skill usually include:
- a focused code or config change
- a short explanation of the behavior change
- engineering reasoning for the chosen approach
- verification notes such as tests, build status, or manual checks
- remaining risks, edge cases, or follow-up suggestions

## Non-goals

This skill is not the best fit for:
- purely visual frontend polish with no engineering depth
- broad AI workflow architecture or prompt-system design
- marketing copy, slides, or portfolio packaging as the primary task
- vague ideation without a concrete codebase or engineering target

## Workflow

1. Orient quickly.
Read the entry files, stack files, and affected slice before proposing changes. Prefer `rg`, focused file reads, and config inspection over guessing.

2. Identify the engineering axis.
Classify the task as one or more of:
- business logic or bug fix
- API or controller contract
- persistence or SQL
- performance or caching
- frontend integration
- test gap
- project hardening for interview or production readiness

3. Apply the right depth.
For simple fixes, change the smallest safe surface.
For medium tasks, explain the behavior change and verify with targeted commands.
For bigger refactors, keep a clear boundary and avoid mixing unrelated cleanups.

4. Verify the result.
Whenever possible:
- run the narrowest relevant test
- compile or lint the touched module
- inspect SQL, API responses, or logs if behavior depends on data flow
- call out anything you could not verify

## Examples

### Example 1: Spring Boot bug fix
User request:
> Help me fix this Spring Boot login bug. The controller returns 200 but the frontend still thinks auth failed.

Good use of this skill:
- inspect controller, service, DTO, and frontend caller together
- verify response shape and error handling contract
- patch the smallest safe surface
- explain the user-facing fix and verification status

### Example 2: SQL and API cleanup
User request:
> Clean up these REST APIs and optimize the recruitment list query.

Good use of this skill:
- review controller naming, request parameters, DTO boundaries, and mapper SQL
- identify N+1 or poor index usage
- tighten response consistency and query performance together only where they are coupled

### Example 3: Interview-grade hardening
User request:
> Make this campus recruitment recommendation system look more production-ready for interviews.

Good use of this skill:
- surface architecture strengths already present
- strengthen validation, error handling, test coverage, and API clarity
- avoid fake complexity and keep claims tied to real code evidence

## Pairing With Other Skills

Use these when the task naturally narrows:
- `code-reviewer` for bug risk and regression review
- `performance-profiler` for slow interfaces, SQL, or rendering
- `qa-expert` for tests and edge cases
- `api-design-reviewer` for controller and contract cleanup
- `database-designer` for schema, index, and relation work
- `observability-designer` for logs, metrics, tracing, and alerting
- `ast-grep` and `codegraph` for large refactors or codebase understanding

## Triggers

Common requests that should trigger this skill:
- "Help me fix this Spring Boot bug"
- "Refactor this Java backend"
- "Optimize this MySQL query"
- "Clean up these REST APIs"
- "Review this campus recruitment recommendation system"
- "Make this project more interview-ready"

## Reference

Read [references/checklist.md](references/checklist.md) when you need a compact implementation and review checklist.
