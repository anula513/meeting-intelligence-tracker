from score import (quotes_overlap, match_items, score_transcript, metrics,
                   split_totals, check_targets, build_report, write_report)

# Fake data only. These tests never call the API.

QUOTE_A = "We're going with Vendor B."
QUOTE_B = "We'll sign the one-year contract if legal approves."
QUOTE_C = "Priya will draft the summary by Wednesday."


def decision(quote, owner=None, status="final"):
    return {"decision": "x", "status": status, "condition": None,
            "owner": owner, "source_quote": quote}


def action(quote, owner=None):
    return {"task": "x", "owner": owner, "due_date": None, "source_quote": quote}


def make_output(decisions=(), actions=(), unverified=()):
    return {"decisions": list(decisions), "action_items": list(actions),
            "unverified_quotes": list(unverified)}


def make_key(decisions=(), actions=(), must_not=(), split="dev"):
    return {"split": split, "decisions": list(decisions), "action_items": list(actions),
            "must_not_extract": list(must_not)}


# ---- quotes_overlap ----

def test_overlap_when_model_quote_is_longer():
    assert quotes_overlap("Agreed. " + QUOTE_A, QUOTE_A)


def test_overlap_when_model_quote_is_shorter():
    assert quotes_overlap("going with Vendor B", QUOTE_A)


def test_overlap_ignores_extra_whitespace():
    assert quotes_overlap("We're going\n  with Vendor B.", QUOTE_A)


def test_different_quotes_do_not_overlap():
    assert not quotes_overlap(QUOTE_A, QUOTE_B)


def test_empty_quote_never_matches():
    assert not quotes_overlap("", QUOTE_A)
    assert not quotes_overlap(QUOTE_A, "")


# ---- scoring ----

def test_perfect_match():
    key = make_key([decision(QUOTE_A, status="final")], [action(QUOTE_C, owner="Priya")])
    output = make_output([decision(QUOTE_A, status="final")], [action(QUOTE_C, owner="Priya")])
    r = score_transcript(output, key)

    d = metrics(r["decisions"])
    a = metrics(r["action_items"])
    assert d["precision_correct"] == 1.0 and d["recall_correct"] == 1.0
    assert a["precision_correct"] == 1.0 and a["recall_correct"] == 1.0
    assert r["problems"] == []


def test_miss():
    key = make_key([decision(QUOTE_A), decision(QUOTE_B)])
    output = make_output([decision(QUOTE_A)])
    r = score_transcript(output, key)

    d = metrics(r["decisions"])
    assert d["precision_found"] == 1.0
    assert d["recall_found"] == 0.5
    assert any(p.startswith("MISS decision") for p in r["problems"])


def test_extra():
    key = make_key([decision(QUOTE_A)])
    output = make_output([decision(QUOTE_A), decision(QUOTE_B)])
    r = score_transcript(output, key)

    d = metrics(r["decisions"])
    assert d["precision_found"] == 0.5
    assert d["recall_found"] == 1.0
    assert any(p.startswith("EXTRA decision") for p in r["problems"])


def test_wrong_owner_is_found_but_not_fully_correct():
    key = make_key(actions=[action(QUOTE_C, owner="Priya")])
    output = make_output(actions=[action(QUOTE_C, owner="Marcus")])
    r = score_transcript(output, key)

    a = metrics(r["action_items"])
    assert a["recall_found"] == 1.0
    assert a["recall_correct"] == 0.0
    assert a["owner_accuracy"] == 0.0
    assert any(p.startswith("OWNER action item") for p in r["problems"])


def test_owner_compare_ignores_case():
    key = make_key(actions=[action(QUOTE_C, owner="Priya")])
    output = make_output(actions=[action(QUOTE_C, owner="priya")])
    r = score_transcript(output, key)
    assert r["action_items"]["fully_correct"] == 1


def test_wrong_status_is_found_but_not_fully_correct():
    key = make_key([decision(QUOTE_B, status="provisional")])
    output = make_output([decision(QUOTE_B, status="final")])
    r = score_transcript(output, key)

    d = metrics(r["decisions"])
    assert d["recall_found"] == 1.0
    assert d["recall_correct"] == 0.0
    assert d["status_accuracy"] == 0.0


def test_invented_owner():
    key = make_key([decision(QUOTE_A, owner=None)])
    output = make_output([decision(QUOTE_A, owner="Priya")])
    r = score_transcript(output, key)
    assert r["decisions"]["invented_owners"] == 1


def test_wrong_but_named_owner_is_not_invented():
    key = make_key([decision(QUOTE_A, owner="Leo")])
    output = make_output([decision(QUOTE_A, owner="Priya")])
    r = score_transcript(output, key)
    assert r["decisions"]["invented_owners"] == 0


def test_empty_output_and_empty_key_score_one():
    r = score_transcript(make_output(), make_key())
    d = metrics(r["decisions"])
    assert d["precision_correct"] == 1.0
    assert d["recall_correct"] == 1.0
    assert d["owner_accuracy"] is None   # no matched items to judge
    assert r["problems"] == []


def test_extra_is_flagged_when_in_must_not_extract():
    flaky = "staging is still a bit flaky"
    key = make_key(must_not=["Before we start, staging is still a bit flaky. Just flagging it."])
    output = make_output([decision(flaky)])
    r = score_transcript(output, key)
    assert any("[MUST-NOT-EXTRACT]" in p for p in r["problems"])


def test_matching_is_one_to_one():
    # Two model items both overlap the single key item: 1 match, 1 extra
    key_items = [decision(QUOTE_A)]
    model_items = [decision(QUOTE_A), decision("Okay. " + QUOTE_A)]
    pairs, misses, extras = match_items(model_items, key_items)
    assert len(pairs) == 1
    assert misses == []
    assert len(extras) == 1


def test_decisions_do_not_match_action_items():
    key = make_key(actions=[action(QUOTE_A)])
    output = make_output(decisions=[decision(QUOTE_A)])
    r = score_transcript(output, key)
    assert r["decisions"]["found"] == 0
    assert r["action_items"]["found"] == 0


def test_unverified_quotes_are_counted():
    r = score_transcript(make_output(unverified=["decision: made up"]), make_key())
    assert r["unverified"] == 1


# ---- totals and targets ----

def test_totals_are_micro_averaged():
    # Transcript 1: 1 of 1 found. Transcript 2: 0 of 3 found. Micro recall = 1/4.
    r1 = score_transcript(make_output([decision(QUOTE_A)]), make_key([decision(QUOTE_A)]))
    r2 = score_transcript(make_output(),
                          make_key([decision(QUOTE_A), decision(QUOTE_B), decision(QUOTE_C)]))
    total = split_totals({"one": r1, "two": r2}, "dev")
    assert total["transcripts"] == 2
    assert metrics(total["decisions"])["recall_found"] == 0.25


def test_splits_are_kept_separate():
    r_dev = score_transcript(make_output(), make_key(split="dev"))
    r_test = score_transcript(make_output(), make_key(split="test"))
    results = {"a": r_dev, "b": r_test}
    assert split_totals(results, "dev")["transcripts"] == 1
    assert split_totals(results, "test")["transcripts"] == 1


def test_invented_owner_fails_target():
    r = score_transcript(make_output([decision(QUOTE_A, owner="Priya")]),
                         make_key([decision(QUOTE_A, owner=None)]))
    passed = check_targets(split_totals({"a": r}, "dev"))
    assert passed["invented_owners"] is False


# ---- report ----

def test_report_has_empty_failure_section():
    r = score_transcript(make_output(), make_key())
    assert "## What failed and why" in build_report({"a": r})


def test_report_never_overwrites_existing_file(tmp_path):
    path = tmp_path / "report.md"
    path.write_text("my notes", encoding="utf-8")
    r = score_transcript(make_output(), make_key())
    assert write_report({"a": r}, path) is False
    assert path.read_text(encoding="utf-8") == "my notes"
