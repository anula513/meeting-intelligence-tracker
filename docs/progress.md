# Progress Log

## 2026-09-30
- Done: repo created and cloned, CLAUDE.md written, setup files added, virtual environment built, packages installed, Sprint 0 docs added
- Next: plan step 2 (sample transcripts)
- Blockers: none

## 2026-10-09
- Done: steps 7-12 of the Sprint 1 plan
  - 7-10: extractor with structured outputs, quote check, command line, run on both samples
  - 11 (partly): labeling guide written; 2 dev keys in eval/keys/
  - 12: score.py (precision, recall, owner/status accuracy, invented owners, no API calls), run_eval.py (runs the extractor on every keyed transcript, asks before calling the API), tests/test_score.py
- Finding: the first beta-launch run had 2 stitched quotes and a duplicate action item. Cause: prompt gaps (quotes were not limited to one turn, the owner rule only covered action items, nothing said to avoid duplicates). Fixed by prompt changes. Unverified quotes went from 2 to 0.
- Dev practice numbers (inflated, the prompt was tuned on these two): decisions 7/7 and action items 5/5 fully correct, 0 invented owners, 0 unverified quotes. These are not the baseline.
- Invented owner is counted with a stricter rule than the charter's: the key's owner is null but the model gave one.
- Eval set: 10 planned (charter says 15, to revisit).
- AI usage: the 8 test transcripts were drafted by Claude. I hand-label their answer keys.
- Next: hand-label the 8 test keys, run run_eval.py, then score.py --report docs/baseline-report.md for the real baseline
- Blockers: none
