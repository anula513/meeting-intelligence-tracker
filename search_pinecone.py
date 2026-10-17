import os
from dotenv import load_dotenv
from pinecone import Pinecone

from embeddings import embed

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("meeting-tracker")

question = "Who is taking over the night tickets?"
q = embed(question)

results = index.query(vector=q, top_k=3, include_metadata=True)

for match in results.matches:
    print(round(match.score, 3), match.id, match.metadata["text"][:80])