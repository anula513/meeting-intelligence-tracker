# Meeting Intelligence Tracker
Solo student project. A RAG app: upload meeting transcripts (text), extract decisions, and answer questions across meetings with citations.

## Stack
Python, OpenAI API, Pinecone, Streamlit. LangChain optional.

## Rules
- Decisions are separate from action items and discussion.
- Each decision has: decision, status (final/provisional/unresolved), condition, owner, source_quote.
- Owner is nullable. Never invent an owner. Use null if not stated.
- Every decision needs a source quote from the transcript.
- Chunk transcripts by speaker turn.
- Store meeting name and date as Pinecone metadata. Answers must cite the meeting.
- API keys come from .env only. Never hardcode or print them.

## How to work with me
- Plan first. No code until I approve the plan.
- Work in small steps and explain in plain English. I'm a student still learning.
- Don't touch files I didn't mention.
