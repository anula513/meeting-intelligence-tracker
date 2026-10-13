import json
from pathlib import Path

from score import quotes_overlap
from verify import quote_is_verbatim


def find_trap_conflicts(key):
    """Return quotes of key items that overlap one of the same key's must_not_extract quotes.

    A key that lists something as both "extract this" and "must not extract" contradicts itself.
    Uses the same overlap rule as score.py.
    """
    must_not = key.get("must_not_extract", [])
    items = key["decisions"] + key["action_items"]
    return [i["source_quote"] for i in items
            if any(quotes_overlap(i["source_quote"], trap) for trap in must_not)]


def main():
    for key_path in sorted(Path("eval/keys").glob("*.json")):
        key = json.loads(key_path.read_text(encoding="utf-8"))
        transcript_path = Path("sample_transcripts") / (key_path.stem + ".txt")
        transcript = transcript_path.read_text(encoding="utf-8")

        items = key["decisions"] + key["action_items"]
        bad = [i["source_quote"] for i in items
               if not quote_is_verbatim(i["source_quote"], transcript)]
        conflicts = find_trap_conflicts(key)

        if not bad and not conflicts:
            print(key_path.name, "OK")
            continue
        if bad:
            print(key_path.name, f"BAD QUOTES: {bad}")
        if conflicts:
            print(key_path.name, f"TRAP CONFLICT: {conflicts}")


if __name__ == "__main__":
    main()
