import os
from dotenv import load_dotenv
from pinecone import Pinecone

from chunker import chunk_by_turn
from embeddings import embed

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("meeting-tracker")

MEETING_ID = "support-escalation"
text = open("sample_transcripts/2026-10-15_support-escalation.txt", encoding="utf-8").read()
chunks = chunk_by_turn(text, MEETING_ID)

records = []
for chunk in chunks:
        record = {
        "id": f"{chunk['meeting_id']}-{chunk['turn_number']}",
        "values": embed(chunk["text"]),
        "metadata": {
            "meeting_id": chunk["meeting_id"],
            "turn_number": chunk["turn_number"],
            "speaker": chunk["speaker"] or "Unknown",
            "text": chunk["text"],
        },
        }
        records.append(record)

index.upsert(vectors=records)
print("Stored", len(records), "chunks")