def parse_labeled(text):
    turns = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("["):
            end = line.index("]")
            timestamp = line[1:end]
            colon = line.index(":", end)
            speaker = line[end + 1:colon].strip()
            spoken = line[colon + 1:].strip()
            turns.append({"timestamp": timestamp, "speaker": speaker, "text": spoken})
        elif turns:
            turns[-1]["text"] += " " + line
    return turns