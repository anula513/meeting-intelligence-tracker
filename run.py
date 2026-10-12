import json
import sys
from pathlib import Path

from extract import extract
from parser import meeting_info
from verify import find_bad_quotes


def run_one(path):
    """Extract one transcript, check its quotes, and save output/<stem>.json.

    Calls the OpenAI API. Returns (output, out_path).
    """
    date, name = meeting_info(path)
    transcript = Path(path).read_text(encoding="utf-8")

    result = extract(transcript)
    bad_quotes = find_bad_quotes(result, transcript)

    output = {
        "meeting_name": name,
        "meeting_date": date,
        "decisions": [d.model_dump() for d in result.decisions],
        "action_items": [a.model_dump() for a in result.action_items],
        "unverified_quotes": bad_quotes,
    }

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / (Path(path).stem + ".json")
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    return output, out_path


def main():
    if len(sys.argv) != 2:
        print("Usage: python run.py <path-to-transcript.txt>")
        sys.exit(1)

    output, out_path = run_one(sys.argv[1])
    bad_quotes = output["unverified_quotes"]

    print(f"Saved {out_path}")
    print(f"{len(output['decisions'])} decisions, "
          f"{len(output['action_items'])} action items, "
          f"{len(bad_quotes)} unverified quotes")
    for q in bad_quotes:
        print(f"  WARNING: {q}")


if __name__ == "__main__":
    main()
