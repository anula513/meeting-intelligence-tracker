from schemas import Decision, ActionItem, Extraction
from verify import normalize, quote_is_verbatim, find_bad_quotes

TRANSCRIPT = "Priya will draft a short summary of the contract terms for legal by Wednesday."


# ---- normalize ----

def test_normalize_collapses_extra_spaces():
    assert normalize("the   contract    terms") == "the contract terms"


def test_normalize_turns_line_breaks_into_spaces():
    assert normalize("the contract\nterms") == "the contract terms"


# ---- quote_is_verbatim ----

def test_exact_quote_is_found():
    assert quote_is_verbatim("summary of the contract terms", TRANSCRIPT)


def test_quote_still_found_when_transcript_has_a_line_break():
    transcript = "Priya will draft a short summary of the contract\nterms for legal by Wednesday."
    assert quote_is_verbatim("summary of the contract terms", transcript)


def test_squashed_words_are_not_found():
    assert not quote_is_verbatim("summary of the contractterms", TRANSCRIPT)


def test_changed_word_is_not_found():
    assert not quote_is_verbatim("summary of the contract conditions", TRANSCRIPT)


def test_empty_quote_is_not_found():
    assert not quote_is_verbatim("", TRANSCRIPT)

FINDER_TRANSCRIPT = "We are going with Vendor B. Priya will email the vendor by Friday."


def make_result(decision_quote, action_quote):
    """Build a small fake Extraction so tests don't need the API."""
    return Extraction(
        decisions=[Decision(decision="Go with Vendor B", status="final",
                            source_quote=decision_quote)],
        action_items=[ActionItem(task="Email the vendor",
                                 source_quote=action_quote)],
    )


def test_find_bad_quotes_returns_empty_list_when_all_quotes_are_real():
    result = make_result("going with Vendor B", "Priya will email the vendor")
    assert find_bad_quotes(result, FINDER_TRANSCRIPT) == []


def test_find_bad_quotes_flags_a_bad_decision_quote():
    result = make_result("going with Vendor C", "Priya will email the vendor")
    bad = find_bad_quotes(result, FINDER_TRANSCRIPT)
    assert len(bad) == 1
    assert bad[0].startswith("decision:")


def test_find_bad_quotes_flags_a_bad_action_item_quote():
    result = make_result("going with Vendor B", "Priya will emailthe vendor")
    bad = find_bad_quotes(result, FINDER_TRANSCRIPT)
    assert len(bad) == 1
    assert bad[0].startswith("action item:")