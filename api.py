from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from answer import ask

app = FastAPI(title="Meeting Intelligence Tracker API")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    meeting_id: str | None = None


class AskResponse(BaseModel):
    status: Literal["verified", "unverified", "not_found"]
    answer: str
    source_quote: str
    meeting_date: str | None = None
    meeting_name: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest):
    result = ask(req.question, req.meeting_id)
    return result