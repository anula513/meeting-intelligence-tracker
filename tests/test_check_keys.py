from check_keys import find_trap_conflicts

# Fake keys only. These tests never read eval/keys/ or call the API.

TRAP = "We should probably look into caching at some point."


def make_key(decision_quotes=(), action_quotes=(), must_not=None):
    key = {
        "split": "dev",
        "decisions": [{"source_quote": q} for q in decision_quotes],
        "action_items": [{"source_quote": q} for q in action_quotes],
    }
    if must_not is not None:
        key["must_not_extract"] = list(must_not)
    return key


def test_decision_that_overlaps_a_trap_is_flagged():
    key = make_key(decision_quotes=["look into caching"], must_not=[TRAP])
    assert find_trap_conflicts(key) == ["look into caching"]


def test_action_item_that_overlaps_a_trap_is_flagged():
    key = make_key(action_quotes=[TRAP], must_not=[TRAP])
    assert find_trap_conflicts(key) == [TRAP]


def test_clean_key_has_no_conflicts():
    key = make_key(decision_quotes=["We're going with Vendor B."], must_not=[TRAP])
    assert find_trap_conflicts(key) == []


def test_key_without_must_not_extract_has_no_conflicts():
    key = make_key(decision_quotes=["We're going with Vendor B."])
    assert find_trap_conflicts(key) == []
