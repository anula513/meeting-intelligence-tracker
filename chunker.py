from parser import parse_transcript


def chunk_by_turn(transcript_text, meeting_id):
    turns = parse_transcript(transcript_text)

    chunks = []
    for number, turn in enumerate(turns, start=1):
        chunk = {
            "meeting_id": meeting_id,
            "turn_number": number,
            "speaker": turn["speaker"],
            "text": turn["text"]
        }
        chunks.append(chunk)

    return chunks

if __name__ == "__main__":
    text = open("sample_transcripts/2026-10-15_support-escalation.txt", encoding="utf-8").read()
    chunks = chunk_by_turn(text, "support-escalation")
    print(len(chunks))
    print(chunks[2])