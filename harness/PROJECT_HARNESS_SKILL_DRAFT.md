# Project Harness Skill Draft

## Purpose

This repository acts as a **project-specific direct HWP extraction harness**.

The goal is not only to extract one document, but to improve the extraction logic over repeated runs while preserving verifiable evidence.

## Core loop

1. Run the sample pipeline
2. Inspect direct extraction outputs
3. Inspect oracle coverage / unresolved mappings / fallback usage / warnings
4. Select the next upgrade target
5. Implement the smallest safe improvement
6. Re-run and compare

## Required artifacts per run

- extracted XML
- extracted IR
- main generated HTML
- generated payload/state
- runtime verification report
- review summary
- upgrade targets

## What counts as a good upgrade

- reduces oracle mismatches
- reduces fallback usage
- reduces remaining reference scaffolding
- improves editability/binding correctness
- preserves or improves runtime-contract pass status

## What not to do

- do not widen into multi-format support before the sample is strong
- do not hide gaps by weakening verification silently
- do not overwrite the oracle/reference role of `today_major_economy/`

## Promotion path

If this harness becomes stable enough, this draft can be promoted into:
- a reusable local project skill
- a stronger automated upgrade pipeline
- a broader document-family extraction harness
