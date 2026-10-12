import json
from pathlib import Path

from verify import quote_is_verbatim

for key_path in sorted(Path("eval/keys").glob("*.json")):
    key = json.loads(key_path.read_text(encoding="utf-8"))
    transcript_path = Path("sample_transcripts") / (key_path.stem + ".txt")
    transcript = transcript_path.read_text(encoding="utf-8")

    items = key["decisions"] + key["action_items"]
    bad = [i["source_quote"] for i in items
           if not quote_is_verbatim(i["source_quote"], transcript)]

    print(key_path.name, "OK" if not bad else f"BAD QUOTES: {bad}")