# Sprint 1 Plan: Core Extractor and Baseline

**Dates:** Oct 3 - Oct 9
**Goal:** run `python extract.py 2026-09-15_pricing-sync.txt` and get a JSON file of decisions and action items following every rule in CLAUDE.md, with a measured baseline.

**Stories:** US-01, US-02, US-03, US-04, US-05, US-06, US-07

## Steps (each small enough to review)
1. Setup files: .gitignore addition, .env.example, requirements.txt (done)
2. Two fake sample transcripts, one labeled and one unlabeled, with tricky cases
3. Parser for labeled transcripts, plus tests
4. Parser for unlabeled transcripts and labeled/unlabeled detection, plus tests
5. Schemas (Decision and ActionItem) with pydantic
6. Prompt, including the owner rule: the owner is the person who accepts or is assigned the task, never a guess
7. API call with structured outputs (check current OpenAI docs first)
8. Code check that every source quote appears in the transcript
9. Command line: meeting name and date from the filename (YYYY-MM-DD_name.txt), optional override; save to output/
10. Run on both samples and review the JSON together
11. Labeling guide and eval set of 15 transcripts, labeled by hand
12. Script for precision, recall, and invented-owner count; write the baseline report

## Working rules
- Plan first, then one step at a time; read every change before accepting
- Parser tests never call the API
- Keys only in .env; never pasted into chat
- Commit after each working step

## Sprint 1 risks
Invented owners (risk 1), low recall (risk 2), eval set too small (risk 3).

## Required documents this sprint
Requirements summary, architecture and schema doc, labeling guide, baseline evaluation report, sprint review, retrospective, Sprint 2 plan.
