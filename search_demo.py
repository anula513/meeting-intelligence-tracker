from chunker import chunk_by_turn
from embeddings import embed, similarity

text = open("sample_transcripts/2026-10-15_support-escalation.txt", encoding="utf-8").read()
chunks = chunk_by_turn(text, "support-escalation")

question = "Who is taking over the night tickets?"
q = embed(question)

scored = []
for chunk in chunks:
    score = similarity(q, embed(chunk["text"]))
    scored.append((score, chunk))

scored.sort(key=lambda pair: pair[0], reverse=True)

for score, chunk in scored[:3]:
    print(round(score, 3), "turn", chunk["turn_number"], chunk["text"][:80])