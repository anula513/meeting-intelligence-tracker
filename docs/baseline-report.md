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
Baseline run on 2026-10-12: one run per transcript, 8 test transcripts. All three targets passed (decision precision 85%, decision recall 92%, invented owners 0), and no unverified quotes. The problems below are what the numbers hide.

### 1. Scoring problem (the metric, not the model)

The scorer matches a model item to a key item when their source quotes overlap. In several cases the model found the right item but quoted a neighboring turn instead of the turn the key quoted. For example, it quoted "Jonas, can you push the config fix?" where the key quoted "Yes, I'll push the config fix tonight." The scorer counted that as one miss plus one extra item.

Affected transcripts:
- incident-retro: both action items scored as wrong (0% precision and recall) even though the task and owner appear to be correct.
- sprint-planning: Marcus's index-rebuild task (one miss, one extra).
- launch-readiness: the staged-vs-all-at-once rollout decision (one miss, one extra).

Effect: the reported action item numbers (76% precision, 81% recall) and decision numbers are lower than the model's real accuracy. These baseline numbers were not changed. A fix is planned: match on owner and task text, or accept a quote from the adjacent turn, and then report both strict and adjusted scores.

### 2. Real model mistakes

- design-review: the model extracted "Agreed, not now." (a deferred dark-theme idea) as a decision. Likely cause: the prompt does not say that ideas deferred with "not now" or "at some point" are not decisions.
- sprint-planning: the model turned the unresolved autocomplete decision into an action item ("Let's leave autocomplete open and look at it again in the next planning"). Likely cause: the prompt does not say an unresolved decision must not also appear as a task.

### 3. Limitations

- One run per transcript, and the model is not deterministic, so results could vary on a rerun.
- Only 8 test transcripts, so a single error moves the percentages noticeably.
- "Invented owner" uses a strict definition (the key's owner is null but the model gave one).

### 4. Next steps

1. Add two prompt rules: deferred ideas are not decisions, and unresolved decisions never become action items.
2. Fix the scorer's matching and report strict and adjusted numbers.
3. Move these 8 transcripts to dev, since they have now been used to tune the prompt.
4. Write 3 to 5 new transcripts and keys as a fresh test set, and report the final score on those.

