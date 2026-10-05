from pathlib import Path

from parser import parse_labeled


# ---- Normal cases -------------------------------------------------------

def test_one_line():
    turns = parse_labeled("[00:00:04] Priya: Okay, let's get started.")
    assert len(turns) == 1
    assert turns[0]["speaker"] == "Priya"
    assert turns[0]["timestamp"] == "00:00:04"
    assert turns[0]["text"] == "Okay, let's get started."


def test_two_speakers_in_order():
    text = "[00:00:04] Priya: Hi.\n[00:00:09] Sam: Hello."
    turns = parse_labeled(text)
    assert len(turns) == 2
    assert turns[0]["speaker"] == "Priya"
    assert turns[1]["speaker"] == "Sam"
    assert turns[1]["timestamp"] == "00:00:09"
    assert turns[1]["text"] == "Hello."


# ---- Special-character cases --------------------------------------------

def test_colon_in_text():
    turns = parse_labeled(
        "[00:00:04] Priya: Okay, let's get started. Three things today: "
        "the beta launch date, dark mode, and pricing for the beta."
    )
    assert len(turns) == 1
    assert turns[0]["timestamp"] == "00:00:04"
    assert turns[0]["speaker"] == "Priya"
    assert turns[0]["text"] == (
        "Okay, let's get started. Three things today: "
        "the beta launch date, dark mode, and pricing for the beta."
    )


# ---- Line-break cases ---------------------------------------------------

def test_wrapped_line():
    turns = parse_labeled(
        "[00:00:31] Dana: I'm fine with that, but the security review\nisn't done yet."
    )
    assert len(turns) == 1
    assert turns[0]["timestamp"] == "00:00:31"
    assert turns[0]["speaker"] == "Dana"
    assert turns[0]["text"] == "I'm fine with that, but the security review isn't done yet."


def test_multiple_wrapped_lines():
    text = "[00:00:31] Dana: I'm fine with that,\nbut the security review\nisn't done yet."
    turns = parse_labeled(text)
    assert len(turns) == 1
    assert turns[0]["text"] == "I'm fine with that, but the security review isn't done yet."


# ---- Whitespace and empty-input cases -----------------------------------

def test_blank_lines_ignored():
    text = "[00:00:04] Priya: Hi.\n\n\n[00:00:09] Sam: Hello."
    turns = parse_labeled(text)
    assert len(turns) == 2


def test_extra_spaces_are_trimmed():
    turns = parse_labeled("   [00:00:04]   Priya  :   Okay.   ")
    assert len(turns) == 1
    assert turns[0]["speaker"] == "Priya"
    assert turns[0]["text"] == "Okay."


def test_empty_input_gives_no_turns():
    assert parse_labeled("") == []


# ---- Gap test: expected to FAIL until parser.py is updated ---------------
# Text that appears before the first "[timestamp] Name:" line has no turn
# to attach to. Decision: ignore it.

def test_text_before_first_turn_is_ignored():
    text = "Meeting notes header\n[00:00:04] Priya: Hi."
    turns = parse_labeled(text)
    assert len(turns) == 1
    assert turns[0]["speaker"] == "Priya"


# ---- Real data ----------------------------------------------------------
# Run pytest from the project root so this relative path works.

def test_real_sample_has_25_turns():
    path = Path("sample_transcripts/2026-09-15_beta-launch-planning.txt")
    turns = parse_labeled(path.read_text(encoding="utf-8"))
    assert len(turns) == 25