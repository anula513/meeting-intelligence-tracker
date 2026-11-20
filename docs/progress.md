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

## 2026-10-17
- Done: Sprint 2 core
  - chunking by speaker turn, embeddings (text-embedding-3-small), Pinecone storage (14 meetings, 171 chunks)
  - RAG answering with a verbatim-quote check (verified / unverified / not_found) and a per-meeting filter
  - 20-question retrieval eval with a saved baseline, plus a 6-question held-out set
- Finding: practice hit@1/3/5 = 9/14/16 of 17; held-out = 2/5/5 of 6. Short decision turns lean on the turn before them, and speaker names were not in the embedded text.
- Next: try adding context to the embedded text
- Blockers: none

## 2026-10-25
- Done: two retrieval experiments. Previous turn + speaker name together: mixed (practice 8/15/16, held-out 4/4/4). Speaker name alone: practice 10/14/16, held-out 4/5/6. Kept speaker name only.
  - Both changes were made at once the first time, so I split them to see which one helped.
  - Caveat: held-out question h6 was used to design the fix, so the held-out set is no longer fully clean.
- Done: Streamlit page (answer card per status, meeting dropdown, example questions, transcript viewer)
- Next: API layer, README refresh, deploy
- Blockers: CLAUDE.md was committed by mistake; untracked it and added it to .gitignore

## 2026-11-11
- Done: FastAPI with /health, /ask and /extract; input limits; honest errors (422, 502, 503); /extract returns the quotes that failed verification
- Next: README refresh, tests for the API and chunker, deploy, fresh held-out retrieval questions
- Blockers: none

## 2026-11-20
- Done: README rewritten; .env.example now lists PINECONE_API_KEY; 18 tests added for api.py and chunker.py (114 total); removed a stray 'keys' line from .gitignore
- AI usage: the new tests and the first README draft were written by Claude; I review them before committing.
- Next: write 6 to 10 fresh held-out retrieval questions; deploy the Streamlit page with a spend limit set; Dockerfile and API deploy after finals; latency and token logging
- Blockers: none
