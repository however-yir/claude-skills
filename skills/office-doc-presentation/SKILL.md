---
name: office-doc-presentation
description: Use when creating or improving Word, WPS, PPT, PDF, report, proposal, summary, or presentation materials. Trigger this for document cleanup, report drafting, slide deck structuring, PDF conversion, meeting summaries, project presentations, and polished office-style deliverables.
argument-hint: "[document type: Word/PPT/PDF/report/proposal]"
version: "1.0.0"
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob
---

# Office Doc Presentation

Use this skill for office-style deliverables where structure, polish, readability, and presentation quality matter at least as much as raw information.

This skill is designed for WPS and Word style documents, PPT decks, PDF-ready summaries, interview materials, and project presentations.

## Inputs

Useful inputs for this skill include:
- raw notes, transcripts, PDFs, docs, or screenshots
- target artifact such as Word, WPS, PPT, PDF, report, or proposal
- audience and purpose, such as class presentation, interview, manager update, or formal submission
- preferred tone, length, and level of formality
- any existing template, branding, or structure requirement

## Outputs

Strong outputs from this skill usually include:
- a clean outline or slide storyline
- rewritten content with better hierarchy and scanability
- a polished office-style draft for Word, WPS, PPT, or PDF
- recommendations for visuals, diagrams, or section order when helpful
- explicit assumptions when source material is incomplete

## Non-goals

This skill is not the best fit for:
- raw research with no deliverable shape yet
- deep software engineering fixes inside codebases
- highly native social content like Xiaohongshu posts
- advanced visual web UI implementation as the primary task

## Workflow

1. Identify the artifact.
Decide whether the deliverable is primarily:
- Word or WPS document
- PPT deck
- PDF export
- mixed set such as report plus slides

2. Clarify audience and purpose.
Always anchor the structure to:
- who will read it
- what decision or impression it should create
- how formal it should feel
- whether it should inform, persuade, summarize, or present

3. Build the structure before polishing.
For docs:
- title
- summary
- sections
- evidence
- conclusion

For slides:
- storyline
- section pages
- high-signal bullets
- visuals
- takeaway page

4. Polish the output.
Improve:
- hierarchy
- spacing
- wording
- scanability
- consistency across headings, bullets, and page rhythm

## Examples

### Example 1: PDF to clean summary
User request:
> Turn this PDF into a clean meeting summary I can send in WPS.

Good use of this skill:
- identify the audience first
- convert dense source material into a clear summary structure
- rewrite for scanability instead of copying the original phrasing

### Example 2: Project presentation deck
User request:
> Help me make a PPT for my recruitment recommendation system.

Good use of this skill:
- build a clear story from problem to solution to architecture to results
- keep one core message per page
- recommend diagrams or screenshots where they strengthen the narrative

### Example 3: Proposal cleanup
User request:
> Polish this proposal and make it feel formal enough for submission as a PDF.

Good use of this skill:
- tighten hierarchy, wording, and consistency
- remove rambling sections and improve executive readability
- prepare the content to export cleanly into PDF format

## Pairing With Other Skills

Use these when useful:
- `doc-to-markdown` to normalize messy source content
- `ppt-creator` for deck generation
- `pdf-creator` for final output format
- `technical-writer` and `docs-write` for sharper language
- `board-deck-builder` for more executive or formal slide structure
- `mermaid-tools` for diagrams and flows

## Triggers

Common requests that should trigger this skill:
- "Help me整理成 Word"
- "Make this into a PPT"
- "Turn this PDF into a clean summary"
- "Polish this report"
- "Help me做项目汇报"
- "Make this look suitable for WPS or office use"

## Reference

Read [references/checklist.md](references/checklist.md) when you need a quick structure checklist for docs and slides.
