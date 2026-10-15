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
Result: FAIL. One invented owner. In support-escalation, the key says the owner of "read the new refund policy" is null (it was said to everyone), but the model wrote "Everyone" as the owner.

Why: my prompt told the model never to guess an owner but never said that group words (everyone, we, someone, the team) are not a person.

Fix: I added one rule to prompts.py (commit 614da07). After it, all 14 meetings had 0 invented owners. That result is dev-only, because the prompt was tuned using these meetings. This FAIL stays in the record as the held-out result. A real fix claim needs a new set of meetings I have not tuned on.

Other findings: strict action items were 60% fully correct and adjusted were 80%. The gap is the quote-turn labeling difference, not model errors. Decisions were 100% / 100% across the 4 meetings. Earlier, support-escalation gave 1 decision on one run and 2 on another with the same prompt. After the fix, 5 of 5 runs gave 2 decisions (docs/variance-support-escalation.md). Five runs cannot rule out a rare outcome.