# Meeting Intelligence Tracker

Ask questions about your meetings and get an answer with a quote you can check. It also pulls decisions and action items out of a transcript. Every quote must appear word for word in the transcript, and the code checks that. If a quote can't be verified, the app says so instead of guessing.

**Status:** runs locally (Streamlit page and FastAPI). Not deployed yet.

## Why build this when Fathom exists?
Fathom is a strong product. I built this from scratch to learn how a trustworthy AI extraction pipeline is built and tested. Every extracted item must carry a verbatim quote from the transcript, and the code checks that the quote really appears there. Items that fail the check are flagged, not deleted. I also measured it against hand-labeled answer keys instead of just trusting a demo.

## What it does
- **Q&A over many meetings.** Type a question ("Who owns the beta launch date?"). The app finds the most relevant moments across all meetings (or one meeting you pick), asks the model to answer using only those, and shows the answer with its source quote, meeting name and date.
- **Extraction.** Give it one transcript and it returns the decisions (final, provisional or unresolved) and action items (task, owner, due date), each with a source quote.
- **A trust check on every answer.** The model must quote its source. The code then looks for that quote, word for word, in the text it was given:

| Status | Meaning |
|---|---|
| `verified` | The quote was found word for word in a real transcript chunk. |
| `unverified` | The model gave a quote, but it is not in the text. Treat the answer with caution. |
| `not_found` | The meetings don't contain the answer, and the model said so instead of guessing. |

## How it works
**Q&A**

```
question -> embed -> Pinecone top 5 (optional: one meeting only)
         -> model answers from those chunks and must give a quote
         -> verify.py looks for the quote in the chunks -> verified / unverified / not_found
```

Each speaker turn is one chunk. Before embedding, the speaker's name is added to the chunk ("Sam: ...") so a question like "What is Sam updating?" can match. The text stored in Pinecone is the original turn, so quotes are always checked against the real words.

**Extraction**

```
transcript -> parser.py (speaker turns) -> model with a strict schema (schemas.py)
           -> verify.py checks every quote -> decisions, action items, unverified quotes
```

## Tech stack
Python, OpenAI API (structured outputs, `text-embedding-3-small`), Pinecone (index `meeting-tracker`, 1536 dimensions, cosine), Pydantic, FastAPI, Streamlit, pytest.

## Run it locally (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env      # then open .env and fill in your own keys
```
(macOS/Linux: `source .venv/bin/activate` and `cp .env.example .env`.)

Create a Pinecone index named `meeting-tracker` with 1536 dimensions, the cosine metric, and no integrated embedding model. Then store the sample meetings once (this spends a few cents of OpenAI embedding credit):

```powershell
python store_all.py
```

Then run whichever part you want:

```powershell
streamlit run app.py              # the web page
uvicorn api:app --reload          # the API; docs at http://127.0.0.1:8000/docs
python -m pytest                  # tests; no API keys needed
```

## API
| Endpoint | Input | Output |
|---|---|---|
| `GET /health` | none | `{"status": "ok"}` |
| `POST /ask` | `question` (1 to 500 characters), optional `meeting_id` | `status`, `answer`, `source_quote`, `meeting_date`, `meeting_name` |
| `POST /extract` | `transcript_text` (1 to 50,000 characters) | `decisions`, `action_items`, `unverified_quotes` |

Bad input returns 422. If the model returns something unusable or can't be reached, the API returns 502; if OpenAI is rate limiting, it returns 503. The API has no login or rate limit yet, so don't expose it publicly.

## Results
**Retrieval** (does the right transcript chunk come back?). "hit@3" means the right chunk was among the top 3 results. The raw outputs are in `docs/retrieval-*.txt`.

| Question set | hit@1 | hit@3 | hit@5 |
|---|---|---|---|
| Practice, 17 questions: baseline | 9 | 14 | 16 |
| Practice, 17 questions: final | 10 | 14 | 16 |
| Held-out, 6 questions: baseline | 2 | 5 | 5 |
| Held-out, 6 questions: final | 4 | 5 | 6 |

- **What I tried:** adding the previous turn plus the speaker name to each chunk before embedding gave mixed results (it helped one question and lost two held-out ones). Adding the speaker name alone did better, so that is what the code does.
- **Questions with no answer** (3 in the practice set): the latest run returned `not_found` for all 3. In an earlier run one of them returned `verified`, because the model quoted a real sentence that did not actually answer the question. The quote check proves a quote exists, not that it answers the question.

**Extraction** results, using hand-labeled answer keys: `docs/baseline-report.md`, `docs/post-fix-dev-report.md` and `docs/fresh-test-report.md`. The official held-out result is a FAIL (1 invented owner), explained below.

## How I used AI
- I used Claude as a coach and tutor, and Claude Code for parts of the scorer and tests.
- The 14 sample transcripts are fictional and AI-drafted. The answer keys were half drafted with AI and half drafted and reviewed by me. The model under test never saw the keys.
- The retrieval questions in `eval/` were written with Claude's help.
- I wrote the labeling rules (decision versus action item, owner rules) and made the design decisions. I tuned the extraction prompt only on dev meetings.
- `tests/test_api.py`, `tests/test_chunker.py` and the first draft of this README were drafted by Claude, and I reviewed them.

## Limitations
- Small evaluation sets: 14 meetings for extraction, and 17 plus 6 questions for retrieval, so one error moves the numbers visibly. Treat them as signals, not proof.
- One run per meeting in the main scores. The model is not deterministic; I measured 5 runs on one meeting, which is not a statistical result.
- Meetings used to tune the prompt are dev data. Post-fix scores on them are not held-out. The official held-out result is in `docs/fresh-test-report.md` and it is a FAIL (1 invented owner).
- One held-out retrieval question (h6) was used to design the speaker-name fix, so the held-out retrieval set is no longer fully clean. A fresh question set is still to do.
- "Invented owner" is defined strictly: the key's owner is null but the model gave one.
- The scorer originally penalized valid answers. I report strict and adjusted scores, and pass/fail uses strict.
- A verified quote shows the words exist in a meeting. It does not guarantee the answer is right.
- The transcripts are text, not audio, and they are synthetic, so real meetings will be messier.
- The API has no authentication or rate limiting, and the app is not deployed.

## Project layout
- `parser.py`, `chunker.py`: split transcripts into speaker turns and chunks.
- `embeddings.py`, `store_all.py`: turn chunks into vectors and store them in Pinecone.
- `answer.py`: retrieve, answer and verify (Q&A). `extract.py`, `run.py`: extraction.
- `verify.py`, `schemas.py`, `prompts.py`: the quote check, data shapes and prompts.
- `api.py`: FastAPI. `app.py`: Streamlit page.
- `score.py`, `run_eval.py`, `check_keys.py`: extraction evaluation. `eval_retrieval.py`, `eval/`: retrieval evaluation.
- `docs/`: plans, reports and progress log. `tests/`: pytest suite. `sample_transcripts/`: the 14 AI-drafted meetings.
