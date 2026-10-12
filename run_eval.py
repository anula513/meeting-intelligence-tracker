"""Run the extractor on every transcript that has an answer key in eval/keys/.

This CALLS THE OPENAI API (costs money), so it asks before running.
Transcripts that already have output/<stem>.json are skipped unless --force.

Usage:
    python run_eval.py
    python run_eval.py --force
"""
import argparse
from pathlib import Path

KEYS_DIR = Path("eval/keys")
TRANSCRIPTS_DIR = Path("sample_transcripts")
OUTPUT_DIR = Path("output")


def find_transcripts_to_run(force):
    """Return the transcripts that have a key and still need an output."""
    to_run = []
    for key_path in sorted(KEYS_DIR.glob("*.json")):
        transcript = TRANSCRIPTS_DIR / (key_path.stem + ".txt")
        output = OUTPUT_DIR / (key_path.stem + ".json")

        if not transcript.exists():
            print(f"WARNING: key {key_path.name} has no transcript {transcript}")
        elif output.exists() and not force:
            print(f"Skip {key_path.stem}: output exists (use --force to redo)")
        else:
            to_run.append(transcript)
    return to_run


def main():
    arg_parser = argparse.ArgumentParser(description="Run the extractor on all keyed transcripts.")
    arg_parser.add_argument("--force", action="store_true", help="redo transcripts that already have output")
    args = arg_parser.parse_args()

    to_run = find_transcripts_to_run(args.force)
    if not to_run:
        print("Nothing to run.")
        return

    answer = input(f"Will call the OpenAI API for {len(to_run)} transcript(s). Continue? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return

    # Imported here so the API client is only created after you say yes
    from run import run_one

    for transcript in to_run:
        print(f"Running {transcript.name} ...")
        output, out_path = run_one(transcript)
        print(f"  Saved {out_path}: {len(output['decisions'])} decisions, "
              f"{len(output['action_items'])} action items, "
              f"{len(output['unverified_quotes'])} unverified quotes")


if __name__ == "__main__":
    main()
