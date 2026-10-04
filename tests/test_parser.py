from parser import parse_labeled

def test_one_line():
    turns = parse_labeled("[00:00:04] Priya: Okay, let's get started.")
    assert len(turns) == 1
    assert turns[0]["speaker"] == "Priya"
    assert turns[0]["timestamp"] == "00:00:04"
    assert turns[0]["text"] == "Okay, let's get started."