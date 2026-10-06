from pathlib import Path

from parser import parse_labeled, parse_unlabeled, is_labeled, parse_transcript 


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


def test_two_paragraphs_unlabeled():
    turns = parse_unlabeled(
        "Thanks everyone for joining. The main goal today is to pick an analytics "
        "vendor for the beta. We looked at Vendor A and Vendor B over the last "
        "two weeks.\n\nNote: the budget figures below are estimates from last quarter.\n"
    )
    assert len(turns) == 2
    assert turns[0]["paragraph"] == 1
    assert turns[0]["speaker"] is None
    assert turns[0]["text"] == "Thanks everyone for joining. The main goal today is to pick an analytics vendor for the beta. We looked at Vendor A and Vendor B over the last two weeks."
    assert turns[1]["paragraph"] == 2
    assert turns[1]["speaker"] is None
    assert turns[1]["text"] == "Note: the budget figures below are estimates from last quarter."

# ---- Blank-line cases ---------------------------------------------------

def test_several_blank_lines_between_paragraphs():
    text = "First thing.\n\n\n\nSecond thing."
    turns = parse_unlabeled(text)
    assert len(turns) == 2
    assert turns[0]["paragraph"] == 1
    assert turns[0]["text"] == "First thing."
    assert turns[1]["paragraph"] == 2
    assert turns[1]["text"] == "Second thing."
 
 
# ---- Line-break cases ---------------------------------------------------
 
def test_wrapped_paragraph_is_joined():
    text = "This paragraph\nwraps over\nthree lines.\n\nSecond paragraph."
    turns = parse_unlabeled(text)
    assert len(turns) == 2
    assert turns[0]["speaker"] is None
    assert turns[0]["text"] == "This paragraph wraps over three lines."
    assert turns[1]["text"] == "Second paragraph."
 
 
# ---- Empty and whitespace cases -----------------------------------------
 
def test_empty_input_gives_no_paragraphs():
    assert parse_unlabeled("") == []
 
 
def test_extra_spaces_are_trimmed_unlabeled():
    # includes a "blank" line that actually contains spaces
    text = "   First thing.   \n   \n   Second thing.   "
    turns = parse_unlabeled(text)
    assert len(turns) == 2
    assert turns[0]["text"] == "First thing."
    assert turns[1]["text"] == "Second thing."
 
 
# ---- Real data ----------------------------------------------------------
# Run pytest from the project root so this relative path works.
 
def test_real_unlabeled_sample_has_11_paragraphs():
    path = Path("sample_transcripts/2026-09-22_vendor-sync.txt")
    turns = parse_unlabeled(path.read_text(encoding="utf-8"))
    assert len(turns) == 11

def test_is_labeled_true_for_labeled_text():
    text = "[00:00:04] Priya: Hi.\n[00:00:09] Sam: Hello."
    assert is_labeled(text) is True
 
 
def test_is_labeled_false_for_unlabeled_text():
    text = "First thing.\n\nSecond thing."
    assert is_labeled(text) is False
 
 
# ---- is_labeled: empty and edge cases -----------------------------------
 
def test_is_labeled_empty_input():
    assert is_labeled("") is False
 
 
def test_is_labeled_wrapped_lines_still_count_as_labeled():
    # 5 non-blank lines, only 2 start with "[" (40%), the rest are wrapped text.
    # This is why the cutoff is 30% and not 100%.
    text = (
        "[00:00:04] Priya: A long sentence\n"
        "that wraps\n"
        "across lines.\n"
        "[00:00:09] Sam: Okay.\n"
        "Yes."
    )
    assert is_labeled(text) is True
 
 
def test_is_labeled_one_bracket_line_in_unlabeled_text():
    # 10 non-blank lines, 1 starts with "[" (10%), so it is still unlabeled.
    text = "[Note: estimates]\n\n" + "\n\n".join(["Some paragraph."] * 9)
    assert is_labeled(text) is False
 
 
def test_is_labeled_exactly_at_threshold():
    # 10 non-blank lines, exactly 3 start with "[" (30%): "at least 30%" counts.
    lines = ["[00:00:01] A: x"] * 3 + ["more text"] * 7
    assert is_labeled("\n".join(lines)) is True
 
 
# ---- parse_transcript: picks the right parser ---------------------------
 
def test_parse_transcript_uses_labeled_parser():
    turns = parse_transcript("[00:00:04] Priya: Hi.")
    assert len(turns) == 1
    assert turns[0]["speaker"] == "Priya"
    assert turns[0]["timestamp"] == "00:00:04"
 
 
def test_parse_transcript_uses_unlabeled_parser():
    paragraphs = parse_transcript("First thing.\n\nSecond thing.")
    assert len(paragraphs) == 2
    assert paragraphs[0]["paragraph"] == 1
    assert paragraphs[0]["speaker"] is None
 
 
def test_parse_transcript_empty_input():
    assert parse_transcript("") == []
 
 
# ---- Real data ----------------------------------------------------------
# Run pytest from the project root so these relative paths work.
 
def test_is_labeled_on_real_samples():
    labeled = Path("sample_transcripts/2026-09-15_beta-launch-planning.txt")
    unlabeled = Path("sample_transcripts/2026-09-22_vendor-sync.txt")
    assert is_labeled(labeled.read_text(encoding="utf-8")) is True
    assert is_labeled(unlabeled.read_text(encoding="utf-8")) is False
 
 
def test_parse_transcript_on_real_samples():
    labeled = Path("sample_transcripts/2026-09-15_beta-launch-planning.txt")
    unlabeled = Path("sample_transcripts/2026-09-22_vendor-sync.txt")
    assert len(parse_transcript(labeled.read_text(encoding="utf-8"))) == 25
    assert len(parse_transcript(unlabeled.read_text(encoding="utf-8"))) == 11