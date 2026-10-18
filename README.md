# meeting-intelligence-tracker

## Why build this when Fathom exists?
Fathom is a strong product. I built this from scratch to learn how a trustworthy AI extraction pipeline is built and tested. Every extracted item must carry a verbatim quote from the transcript, and the code checks that the quote really appears there. Items that fail the check are flagged, not deleted. I also measured it against hand-labeled answer keys instead of just trusting a demo.

## How I used AI
- I used Claude as a coach, and Claude Code for parts of the scorer and tests.
- The 14 sample transcripts are fictional and AI-drafted. The answer keys were half drafted with AI and half drafted and reviewed by me. The model under test never saw the keys.
- I wrote the labeling rules (decision versus action item, owner rules) and made the design decisions. I tuned the prompt only on dev meetings.

## Limitations
- Small evaluation set: 14 meetings, so one error moves the percentages visibly.
- One run per meeting in the main scores. The model is not deterministic; I measured 5 runs on one meeting, which is not a statistical result.
- Meetings used to tune the prompt are dev data. Post-fix scores on them are not held-out. The official held-out result is in docs/fresh-test-report.md and it is a FAIL (1 invented owner).
- "Invented owner" is defined strictly: the key's owner is null but the model gave one.
- The scorer originally penalized valid answers. I report strict and adjusted scores, and pass/fail uses strict.
- The transcripts are text, not audio, and they are synthetic, so real meetings will be messier.
