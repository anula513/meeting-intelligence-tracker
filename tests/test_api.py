"""Tests for the FastAPI layer (api.py).

No network and no API keys: ask() and extract() are replaced by fakes, so these
tests check only the API's own job: validation, response shape, and turning
outside-service failures into honest HTTP errors.
"""
import importlib
import sys
import types

import httpx
import openai
import pytest
from fastapi.testclient import TestClient

from schemas import ActionItem, Decision, Extraction

TRANSCRIPT = "Priya: We ship Friday.\nSam: I will update the docs."


@pytest.fixture
def api_module(monkeypatch):
    """Import api.py with fake answer/extract modules (the real ones need API keys)."""
    fake_answer = types.ModuleType("answer")
    fake_answer.ask = lambda question, meeting_id=None: {}
    fake_extract = types.ModuleType("extract")
    fake_extract.extract = lambda text: Extraction(decisions=[], action_items=[])

    monkeypatch.setitem(sys.modules, "answer", fake_answer)
    monkeypatch.setitem(sys.modules, "extract", fake_extract)
    monkeypatch.delitem(sys.modules, "api", raising=False)

    module = importlib.import_module("api")
    yield module
    sys.modules.pop("api", None)


@pytest.fixture
def client(api_module):
    return TestClient(api_module.app)


def _request():
    return httpx.Request("POST", "https://api.openai.com/v1/responses")


# ---------- /health ----------

def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------- /ask ----------

def test_ask_returns_the_answer_shape(api_module, client, monkeypatch):
    def fake_ask(question, meeting_id=None):
        return {
            "status": "verified",
            "answer": "Priya owns the launch date.",
            "source_quote": "I'll own the launch date.",
            "meeting_date": "2026-09-15",
            "meeting_name": "beta-launch-planning",
        }

    monkeypatch.setattr(api_module, "ask", fake_ask)
    response = client.post("/ask", json={"question": "Who owns the launch date?"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "verified"
    assert body["source_quote"] == "I'll own the launch date."
    assert body["meeting_name"] == "beta-launch-planning"


def test_ask_passes_the_meeting_filter_through(api_module, client, monkeypatch):
    seen = {}

    def fake_ask(question, meeting_id=None):
        seen["meeting_id"] = meeting_id
        return {"status": "not_found", "answer": "I could not find this in the meetings.", "source_quote": ""}

    monkeypatch.setattr(api_module, "ask", fake_ask)
    client.post("/ask", json={"question": "Anything?", "meeting_id": "2026-10-15_support-escalation"})
    assert seen["meeting_id"] == "2026-10-15_support-escalation"


def test_ask_rejects_an_empty_question(client):
    assert client.post("/ask", json={"question": ""}).status_code == 422


def test_ask_rejects_a_question_over_500_characters(client):
    assert client.post("/ask", json={"question": "x" * 501}).status_code == 422


def test_ask_turns_a_bad_model_response_into_502(api_module, client, monkeypatch):
    def broken(question, meeting_id=None):
        raise ValueError("The model did not return a valid answer.")

    monkeypatch.setattr(api_module, "ask", broken)
    response = client.post("/ask", json={"question": "Who owns it?"})
    assert response.status_code == 502
    assert "invalid response" in response.json()["detail"]


def test_ask_turns_a_rate_limit_into_503(api_module, client, monkeypatch):
    def limited(question, meeting_id=None):
        raise openai.RateLimitError(
            "slow down", response=httpx.Response(429, request=_request()), body=None
        )

    monkeypatch.setattr(api_module, "ask", limited)
    response = client.post("/ask", json={"question": "Who owns it?"})
    assert response.status_code == 503
    assert "busy" in response.json()["detail"]


def test_ask_turns_a_connection_error_into_502(api_module, client, monkeypatch):
    def offline(question, meeting_id=None):
        raise openai.APIConnectionError(request=_request())

    monkeypatch.setattr(api_module, "ask", offline)
    response = client.post("/ask", json={"question": "Who owns it?"})
    assert response.status_code == 502
    assert "Could not reach" in response.json()["detail"]


# ---------- /extract ----------

def test_extract_flags_a_quote_that_is_not_in_the_transcript(api_module, client, monkeypatch):
    fake_result = Extraction(
        decisions=[
            Decision(decision="Ship on Friday", status="final", source_quote="We ship Friday."),
        ],
        action_items=[
            ActionItem(task="Update the docs", owner="Sam", source_quote="Sam will rewrite everything."),
        ],
    )
    monkeypatch.setattr(api_module, "extract", lambda text: fake_result)

    response = client.post("/extract", json={"transcript_text": TRANSCRIPT})

    assert response.status_code == 200
    body = response.json()
    assert len(body["decisions"]) == 1
    assert len(body["action_items"]) == 1
    # Only the made-up quote is flagged; the real one passes.
    assert body["unverified_quotes"] == ["action item: Sam will rewrite everything."]


def test_extract_reports_no_bad_quotes_when_all_are_verbatim(api_module, client, monkeypatch):
    fake_result = Extraction(
        decisions=[Decision(decision="Ship on Friday", status="final", source_quote="We ship Friday.")],
        action_items=[],
    )
    monkeypatch.setattr(api_module, "extract", lambda text: fake_result)

    response = client.post("/extract", json={"transcript_text": TRANSCRIPT})
    assert response.status_code == 200
    assert response.json()["unverified_quotes"] == []


def test_extract_rejects_an_empty_transcript(client):
    assert client.post("/extract", json={"transcript_text": ""}).status_code == 422


def test_extract_rejects_a_transcript_over_50000_characters(client):
    assert client.post("/extract", json={"transcript_text": "x" * 50_001}).status_code == 422
