import os
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone

from chunker import chunk_by_turn
from embeddings import embed
from parser import meeting_info

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("meeting-tracker")


def build_embed_text(chunks, i):
    """The text we turn into a fingerprint: speaker + this turn."""
    chunk = chunks[i]
    speaker = chunk["speaker"] or "Unknown"
    return f"{speaker}: {chunk['text']}".strip()


def store_meeting(path):
    date, name = meeting_info(path)
    text = Path(path).read_text(encoding="utf-8")
    chunks = chunk_by_turn(text, Path(path).stem)

    records = []
    for i, chunk in enumerate(chunks):
        record = {
            "id": f"{chunk['meeting_id']}-{chunk['turn_number']}",
            # the fingerprint uses the longer text (with context)...
            "values": embed(build_embed_text(chunks, i)),
            "metadata": {
                "meeting_id": chunk["meeting_id"],
                "meeting_name": name,
                "meeting_date": date or "Unknown",
                "turn_number": chunk["turn_number"],
                "speaker": chunk["speaker"] or "Unknown",
                # ...but the stored text stays the ORIGINAL turn, so quotes still verify
                "text": chunk["text"],
            },
        }
        records.append(record)

    index.upsert(vectors=records)
    return len(records)


if __name__ == "__main__":
    for path in sorted(Path("sample_transcripts").glob("*.txt")):
        count = store_meeting(path)
        print(f"{path.name}: stored {count} chunks")