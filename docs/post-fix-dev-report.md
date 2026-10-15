# Evaluation Report

Date: 2026-10-14

Made by `python score.py --report`.

- **Strict:** a model item matches a key item when their source quotes overlap (one contains the other). "Fully correct" means matched AND owner equal AND, for decisions, status equal. PASS/FAIL uses strict fully correct decisions.
- **Adjusted (informational only):** strict, plus leftover items whose quotes are in adjacent turns. Action items also need the same non-null owner. Decisions also need the same owner (both null is allowed) and the same status.

Invented owner = the key's owner is null but the model gave one. This is stricter than the charter's definition (an owner that never appears in the transcript).

Eval set: 10 planned (charter says 15, to revisit).

## Dev practice numbers (inflated, the prompt was tuned on these two)

Transcripts: 10 (micro-averaged)

| Metric | Strict | Adjusted | Target | Result (strict) |
|---|---|---|---|---|
| Decision precision (found) | 95% | 100% | - | - |
| Decision recall (found) | 95% | 100% | - | - |
| Decision precision (fully correct) | 95% | 100% | >= 80% | PASS |
| Decision recall (fully correct) | 95% | 100% | >= 70% | PASS |
| Decision owner accuracy (matched) | 100% | 100% | - | - |
| Decision status accuracy (matched) | 100% | 100% | - | - |
| Action item precision (found) | 81% | 100% | - | - |
| Action item recall (found) | 81% | 100% | - | - |
| Action item precision (fully correct) | 81% | 100% | - | - |
| Action item recall (fully correct) | 81% | 100% | - | - |
| Action item owner accuracy (matched) | 100% | 100% | - | - |
| Invented owners | 0 | | = 0 | PASS |
| Unverified quotes | 0 | | | |
| Must-not-extract hits | 0 | | - | - |

## Test baseline

Transcripts: 4 (micro-averaged)

| Metric | Strict | Adjusted | Target | Result (strict) |
|---|---|---|---|---|
| Decision precision (found) | 100% | 100% | - | - |
| Decision recall (found) | 100% | 100% | - | - |
| Decision precision (fully correct) | 100% | 100% | >= 80% | PASS |
| Decision recall (fully correct) | 100% | 100% | >= 70% | PASS |
| Decision owner accuracy (matched) | 100% | 100% | - | - |
| Decision status accuracy (matched) | 100% | 100% | - | - |
| Action item precision (found) | 80% | 100% | - | - |
| Action item recall (found) | 80% | 100% | - | - |
| Action item precision (fully correct) | 80% | 100% | - | - |
| Action item recall (fully correct) | 80% | 100% | - | - |
| Action item owner accuracy (matched) | 100% | 100% | - | - |
| Invented owners | 0 | | = 0 | PASS |
| Unverified quotes | 0 | | | |
| Must-not-extract hits | 0 | | - | - |

## Per transcript (strict, fully correct)

| Transcript | Split | Dec P | Dec R | Action P | Action R | Invented owners | Unverified | Adjusted pairs |
|---|---|---|---|---|---|---|---|---|
| 2026-09-15_beta-launch-planning | dev | 100% | 100% | 100% | 100% | 0 | 0 | 0 |
| 2026-09-22_vendor-sync | dev | 100% | 100% | 100% | 100% | 0 | 0 | 0 |
| 2026-09-29_design-review | dev | 100% | 100% | 100% | 100% | 0 | 0 | 0 |
| 2026-09-30_budget-check | dev | 100% | 100% | 100% | 100% | 0 | 0 | 0 |
| 2026-10-01_sprint-planning | dev | 100% | 100% | 75% | 75% | 0 | 0 | 1 |
| 2026-10-02_incident-retro | dev | 100% | 100% | 0% | 0% | 0 | 0 | 2 |
| 2026-10-03_team-standup | dev | 100% | 100% | 100% | 100% | 0 | 0 | 0 |
| 2026-10-05_vendor-call | dev | 100% | 100% | 100% | 100% | 0 | 0 | 0 |
| 2026-10-06_hiring-sync | dev | 100% | 100% | 100% | 100% | 0 | 0 | 0 |
| 2026-10-07_launch-readiness | dev | 50% | 50% | 50% | 50% | 0 | 0 | 2 |
| 2026-10-14_roadmap-review | test | 100% | 100% | 100% | 100% | 0 | 0 | 0 |
| 2026-10-15_support-escalation | test | 100% | 100% | 100% | 100% | 0 | 0 | 0 |
| 2026-10-16_partner-kickoff | test | 100% | 100% | 0% | 0% | 0 | 0 | 1 |
| 2026-10-19_brainstorm-session | test | 100% | 100% | 100% | 100% | 0 | 0 | 0 |

## What failed and why

<!-- Fill this in by hand. -->
