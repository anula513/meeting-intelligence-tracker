import json
from pathlib import Path

from answer import ask, retrieve

# The 20 questions we wrote down BEFORE running anything.
# Each answerable question has: meeting_id and turns (the chunks that hold the answer).
# The no-answer questions have turns = [] and should come back as "not_found".
QUESTIONS = json.loads(Path("eval/questions.json").read_text(encoding="utf-8"))


def find_rank(q, matches):
    """Where did the right chunk land in the search results?

    matches is the list Pinecone returned, best match first.
    Returns 1 if the right chunk was first, 2 if second, and so on.
    Returns None if none of the results was the right chunk (a "miss").
    """
    for rank, match in enumerate(matches, start=1):
        right_meeting = match.metadata["meeting_id"] == q["meeting_id"]
        right_turn = match.metadata["turn_number"] in q["turns"]
        if right_meeting and right_turn:
            return rank
    return None


def hit_at(ranks, k):
    """Count the questions whose right chunk was in the top k results.

    A rank of None means a miss, so it never counts.
    """
    return sum(1 for r in ranks if r is not None and r <= k)


def main():
    ranks = []

    print("RETRIEVAL (no meeting filter, top 5)")
    for q in QUESTIONS:
        if not q["turns"]:
            continue  # no-answer questions are tested below
        matches = retrieve(q["question"])
        rank = find_rank(q, matches)
        ranks.append(rank)
        print(f'{q["id"]}  rank={rank or "miss"}  {q["question"]}')

    total = len(ranks)
    print()
    print(f"hit@1: {hit_at(ranks, 1)}/{total}  (right chunk was the very first result)")
    print(f"hit@3: {hit_at(ranks, 3)}/{total}  (right chunk was in the top 3)")
    print(f"hit@5: {hit_at(ranks, 5)}/{total}  (right chunk was anywhere in the 5 the model reads)")

    print("\nNO-ANSWER QUESTIONS (should be not_found)")
    for q in QUESTIONS:
        if q["turns"]:
            continue
        result = ask(q["question"])
        print(f'{q["id"]}  status={result["status"]}  {q["question"]}')


if __name__ == "__main__":
    main()