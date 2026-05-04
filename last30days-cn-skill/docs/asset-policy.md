# Asset Policy

## Goal
Keep this repository focused on source code and reproducible workflows.

## What stays in Git
- Small, representative sample assets used for documentation/examples.
- Source code and text artifacts needed to run and maintain the skill.

## What does not stay in Git
- Vendored dependency bundles (`vendor/`, `scripts/lib/vendor/`, `node_modules/`).
- Runtime outputs and generated slides (`assets/xhs_30days_share/`, logs).
- Large media collections not required for core functionality.

## Current examples kept
- `assets/dog-original.jpeg`
- `assets/dog-as-human.png`

## Large assets handling
Store non-essential large assets in GitHub Releases or Git LFS, and reference them from docs.
