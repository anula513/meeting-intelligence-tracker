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


def store_meeting(path):
    date, name = meeting_info(path)
    text = Path(path).read_text(encoding="utf-8")
    chunks = chunk_by_turn(text, Path(path).stem)

    records = []
    for chunk in chunks:
        record = {
            "id": f"{chunk['meeting_id']}-{chunk['turn_number']}",
            "values": embed(chunk["text"]),
            "metadata": {
                "meeting_id": chunk["meeting_id"],
                "meeting_name": name,
                "meeting_date": date or "Unknown",
                "turn_number": chunk["turn_number"],
                "speaker": chunk["speaker"] or "Unknown",
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