"""Tests for chunk_by_turn: one chunk per speaker turn, with numbering and metadata."""
from chunker import chunk_by_turn

LABELED = (
    "[00:00:04] Priya: Okay, let's get started.\n"
    "[00:00:09] Sam: I'll own the launch date.\n"
    "That date is final.\n"
    "[00:00:15] Priya: Great, thanks.\n"
)


def test_one_chunk_per_turn_numbered_from_one():
    chunks = chunk_by_turn(LABELED, "demo-meeting")
    assert [c["turn_number"] for c in chunks] == [1, 2, 3]


def test_chunk_carries_meeting_id_speaker_and_text():
    first = chunk_by_turn(LABELED, "demo-meeting")[0]
    assert first == {
        "meeting_id": "demo-meeting",
        "turn_number": 1,
        "speaker": "Priya",
        "text": "Okay, let's get started.",
    }


def test_wrapped_line_stays_in_the_same_chunk():
    second = chunk_by_turn(LABELED, "demo-meeting")[1]
    assert second["speaker"] == "Sam"
    assert second["text"] == "I'll own the launch date. That date is final."


def test_unlabeled_transcript_gets_chunks_with_no_speaker():
    chunks = chunk_by_turn("First paragraph.\n\nSecond paragraph.\n", "demo")
    assert [c["speaker"] for c in chunks] == [None, None]
    assert [c["turn_number"] for c in chunks] == [1, 2]


def test_empty_transcript_gives_no_chunks():
    assert chunk_by_turn("", "demo") == []


def test_record_ids_are_unique_within_a_meeting():
    # store_all.py builds each Pinecone id as "<meeting_id>-<turn_number>".
    chunks = chunk_by_turn(LABELED, "demo-meeting")
    ids = [f"{c['meeting_id']}-{c['turn_number']}" for c in chunks]
    assert len(ids) == len(set(ids))
