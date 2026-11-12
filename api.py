from typing import Literal

import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from answer import ask
from extract import extract
from schemas import ActionItem, Decision
from verify import find_bad_quotes

app = FastAPI(title="Meeting Intelligence Tracker API")


# ---------- Request / response models ----------

class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    meeting_id: str | None = None


class AskResponse(BaseModel):
    status: Literal["verified", "unverified", "not_found"]
    answer: str
    source_quote: str
    meeting_date: str | None = None
    meeting_name: str | None = None


class ExtractRequest(BaseModel):
    transcript_text: str = Field(min_length=1, max_length=50_000)


class ExtractResponse(BaseModel):
    decisions: list[Decision]
    action_items: list[ActionItem]
    unverified_quotes: list[str]


# ---------- Error handling ----------

def run_model_call(func, *args):
    """Call ask()/extract() and turn outside-service failures into honest errors."""
    try:
        return func(*args)
    except ValueError:
        # The model answered, but not in the shape we asked for.
        raise HTTPException(status_code=502, detail="The AI model returned an invalid response. Try again.")
    except openai.RateLimitError:
        raise HTTPException(status_code=503, detail="AI service is busy (rate limit). Try again shortly.")
    except openai.APIError:
        raise HTTPException(status_code=502, detail="Could not reach the AI service.")


# ---------- Routes ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest):
    return run_model_call(ask, req.question, req.meeting_id)


@app.post("/extract", response_model=ExtractResponse)
def extract_items(req: ExtractRequest):
    result = run_model_call(extract, req.transcript_text)
    bad_quotes = find_bad_quotes(result, req.transcript_text)
    return ExtractResponse(
        decisions=result.decisions,
        action_items=result.action_items,
        unverified_quotes=bad_quotes,
    )