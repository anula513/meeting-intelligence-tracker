import os
from dotenv import load_dotenv
from pinecone import Pinecone

from embeddings import client, embed
from prompts import ANSWER_PROMPT
from schemas import Answer
from verify import quote_is_verbatim

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("meeting-tracker")
MODEL = os.getenv("OPENAI_MODEL")
TOP_K = 5


def retrieve(question, meeting_id=None):
    """Find the chunks closest in meaning to the question.

    If meeting_id is given, only chunks from that meeting are searched.
    """
    q = embed(question)
    scope = {"meeting_id": {"$eq": meeting_id}} if meeting_id else None
    results = index.query(
        vector=q, top_k=TOP_K, include_metadata=True, filter=scope
    )
    return results.matches


def build_context(matches):
    """Turn the chunks into numbered lines the model can read."""
    lines = []
    for number, match in enumerate(matches, start=1):
        m = match.metadata
        lines.append(
            f"[{number}] Meeting {m['meeting_name']} ({m['meeting_date']}), "
            f"{m['speaker']}: {m['text']}"
        )
    return "\n".join(lines)


def find_source(quote, matches):
    """Return the chunk that really contains the quote, or None."""
    for match in matches:
        if quote_is_verbatim(quote, match.metadata["text"]):
            return match
    return None


def ask(question, meeting_id=None):
    matches = retrieve(question, meeting_id)
    context = build_context(matches)

    response = client.responses.parse(
        model=MODEL,
        input=[
            {"role": "system", "content": ANSWER_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nChunks:\n{context}"},
        ],
        text_format=Answer,
    )
    result = response.output_parsed
    if result is None:
        raise ValueError("The model did not return a valid answer.")

    if not result.source_quote.strip():
        status = "not_found"
        source = None
    else:
        source = find_source(result.source_quote, matches)
        status = "verified" if source else "unverified"

    return {
        "status": status,
        "answer": result.answer,
        "source_quote": result.source_quote,
        # the date comes from the stored chunk, not from the model
        "meeting_date": source.metadata["meeting_date"] if source else result.meeting_date,
        "meeting_name": source.metadata["meeting_name"] if source else None,
    }


if __name__ == "__main__":
    question = input("Question: ")
    meeting = input("Meeting ID (press Enter for all): ").strip() or None
    result = ask(question, meeting)
    print()
    print("Status:  ", result["status"])
    print("Answer:  ", result["answer"])
    print("Quote:   ", result["source_quote"])
    print("Meeting: ", result["meeting_name"], result["meeting_date"])