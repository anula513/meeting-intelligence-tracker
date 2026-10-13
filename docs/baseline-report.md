# Evaluation Report

Date: 2026-10-12

Made by `python score.py --report`. A model item matches a key item when their source quotes overlap (one contains the other). "Fully correct" means matched AND owner equal AND, for decisions, status equal. PASS/FAIL uses fully correct decisions.

Invented owner = the key's owner is null but the model gave one. This is stricter than the charter's definition (an owner that never appears in the transcript).

Eval set: 10 planned (charter says 15, to revisit).

## Dev practice numbers (inflated, the prompt was tuned on these two)

Transcripts: 2 (micro-averaged)

| Metric | Found | Fully correct | Target | Result |
|---|---|---|---|---|
| Decision precision | 100% | 100% | >= 80% | PASS |
| Decision recall | 100% | 100% | >= 70% | PASS |
| Action item precision | 100% | 100% | - | - |
| Action item recall | 100% | 100% | - | - |
| Decision owner accuracy (matched) | 100% | | | |
| Decision status accuracy (matched) | 100% | | | |
| Action item owner accuracy (matched) | 100% | | | |
| Invented owners | 0 | | = 0 | PASS |
| Unverified quotes | 0 | | | |

## Test baseline

Transcripts: 8 (micro-averaged)

| Metric | Found | Fully correct | Target | Result |
|---|---|---|---|---|
| Decision precision | 85% | 85% | >= 80% | PASS |
| Decision recall | 92% | 92% | >= 70% | PASS |
| Action item precision | 76% | 76% | - | - |
| Action item recall | 81% | 81% | - | - |
| Decision owner accuracy (matched) | 100% | | | |
| Decision status accuracy (matched) | 100% | | | |
| Action item owner accuracy (matched) | 100% | | | |
| Invented owners | 0 | | = 0 | PASS |
| Unverified quotes | 0 | | | |

## Per transcript (fully correct)

| Transcript | Split | Dec P | Dec R | Action P | Action R | Invented owners | Unverified |
|---|---|---|---|---|---|---|---|
| 2026-09-15_beta-launch-planning | dev | 100% | 100% | 100% | 100% | 0 | 0 |
| 2026-09-22_vendor-sync | dev | 100% | 100% | 100% | 100% | 0 | 0 |
| 2026-09-29_design-review | test | 50% | 100% | 100% | 100% | 0 | 0 |
| 2026-09-30_budget-check | test | 100% | 100% | 100% | 100% | 0 | 0 |
| 2026-10-01_sprint-planning | test | 100% | 100% | 60% | 75% | 0 | 0 |
| 2026-10-02_incident-retro | test | 100% | 100% | 0% | 0% | 0 | 0 |
| 2026-10-03_team-standup | test | 100% | 100% | 100% | 100% | 0 | 0 |
| 2026-10-05_vendor-call | test | 100% | 100% | 100% | 100% | 0 | 0 |
| 2026-10-06_hiring-sync | test | 100% | 100% | 100% | 100% | 0 | 0 |
| 2026-10-07_launch-readiness | test | 50% | 50% | 100% | 100% | 0 | 0 |

## What failed and why

<!-- Fill this in by hand. -->
