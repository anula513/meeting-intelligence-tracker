# Project Proposal and Charter: Meeting Intelligence Tracker

**Author:** Anula Dinesh
**Type:** Solo capstone-style personal project
**Status:** Sprint 0 (planning)

> Targets and dates in this document are proposals. After the Sprint 1 baseline, revise anything unrealistic and record why.

## Problem
Teams make decisions in meetings and then lose track of them. Notes are messy, decisions are buried in discussion, and weeks later nobody remembers what was agreed, who owns the follow-up, or whether the decision was final. Existing summarizers produce a wall of text. They don't separate decisions from discussion and action items, and they can't answer questions across many past meetings.

## Solution
A RAG-based web app. The user uploads meeting transcripts as text. The system:
1. Extracts decisions as structured records (decision, status, condition, owner, source quote), kept separate from action items and discussion.
2. Generates a short summary of each meeting.
3. Stores transcripts as embeddings so the user can ask questions across meetings ("What did we decide about pricing?") and get an answer that cites the source meeting.

## In scope
- Text transcript input (paste or file), with or without speaker labels
- Decision extraction with status (final / provisional / unresolved), condition, nullable owner, source quote
- Separate action item extraction
- Meeting summary
- Speaker-turn chunking, embeddings, Pinecone storage with meeting name and date metadata
- Cross-meeting Q&A with citations
- Evaluation of the extractor and the retrieval layer on a hand-labeled set
- Streamlit UI, deployed demo, README, final report

## Out of scope (v1)
- Audio transcription or live capture
- User accounts, authentication, permissions
- Calendar, Slack, or Teams integrations
- Fine-tuning a model

## Stretch (only after all Must stories are done)
Cross-meeting reversal detection: flag decisions contradicted or dropped in a later meeting.

## Success metrics
| # | Metric | Target | How measured |
|---|--------|--------|--------------|
| 1 | Decision precision | >= 80% | Share of extracted decisions that match my hand labels (15 transcripts) |
| 2 | Decision recall | >= 70% | Share of true decisions the system catches |
| 3 | Retrieval accuracy | >= 80% | Of 20 test questions, share answered from the right meeting with the right citation |
| 4 | Invented owners | 0 | Count of owners returned that never appear in the transcript |
| 5 | Delivery | Demo + final report by end of Sprint 3 | Live link and report in the repo |

## Timeline
| Sprint | Dates | Goal |
|--------|-------|------|
| 0 | Sep 30 - Oct 2 | Plan and document |
| 1 | Oct 3 - Oct 9 | Core extractor, eval set, baseline |
| 2 | Oct 10 - Oct 16 | RAG layer and retrieval evaluation |
| 3 | Oct 17 - Oct 23 | Polish, deploy, report, demo |
| Buffer | Oct 24 - Oct 30 | Slip room, stretch goal, resume bullets |

Planned pace: about 3 hours per day.

## Tech stack
- **Python:** main language
- **OpenAI API (structured outputs) and embeddings:** extraction, summaries, vectors
- **Pinecone:** vector store with metadata filtering
- **Streamlit:** UI
- **pydantic and pytest:** validate model output and test my own code
- **Claude Code in VS Code:** coding assistant, used in small reviewed steps
- **LangChain:** optional; plain API calls first
