# A transcript counts as "labeled" if at least this share of its
# non-blank lines start with "[" (a timestamp). Tune this later on real data.
from pathlib import Path


LABELED_THRESHOLD = 0.3


def parse_labeled(text):
    """Split a transcript with '[timestamp] Name: text' lines into turns."""
    turns = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue  # skip blank lines
        if line.startswith("["):
            # a new turn: [00:00:04] Priya: Okay, let's get started.
            end = line.index("]")
            timestamp = line[1:end]
            colon = line.index(":", end)  # first colon AFTER the timestamp
            speaker = line[end + 1:colon].strip()
            spoken = line[colon + 1:].strip()
            turns.append({"timestamp": timestamp, "speaker": speaker, "text": spoken})
        elif turns:
            # a wrapped line: add it to the previous turn
            turns[-1]["text"] += " " + line
        # if there is no previous turn yet, the line is ignored
    return turns


def parse_unlabeled(text):
    """Split a transcript with no speaker labels into paragraphs."""
    paragraphs = []
    current = []  # the lines of the paragraph we're building right now

    for line in text.splitlines():
        line = line.strip()
        if line:
            current.append(line)
        elif current:
            # a blank line ends the current paragraph
            paragraphs.append({
                "paragraph": len(paragraphs) + 1,
                "speaker": None,
                "text": " ".join(current),
            })
            current = []

    # save the last paragraph (the file may not end with a blank line)
    if current:
        paragraphs.append({
            "paragraph": len(paragraphs) + 1,
            "speaker": None,
            "text": " ".join(current),
        })

    return paragraphs


def is_labeled(text):
    """Return True if the transcript looks like it has [timestamp] labels."""
    total = 0    # non-blank lines
    labeled = 0  # non-blank lines that start with "["

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        total += 1
        if line.startswith("["):
            labeled += 1

    if total == 0:
        return False  # empty transcript: nothing to parse, treat as unlabeled
    return labeled / total >= LABELED_THRESHOLD


def parse_transcript(text):
    """Pick the right parser for this transcript."""
    if is_labeled(text):
        return parse_labeled(text)
    return parse_unlabeled(text)

def meeting_info(path):
    """Get (date, name) from a filename like 2026-09-22_vendor-sync.txt."""
    stem = Path(path).stem
    if "_" not in stem:
        return None, stem  # no date in the filename
    date, name = stem.split("_", 1)
    return date, name