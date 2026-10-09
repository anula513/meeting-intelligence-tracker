import pytest
from pydantic import ValidationError

from schemas import Decision, ActionItem
# ---- Decision -----------------------------------------------------------

def test_valid_decision_works():
    d = Decision(
        decision="Go with vendor B",
        status="provisional",
        source_quote="Let's go with B.",
    )
    assert d.condition is None
    assert d.owner is None


def test_decision_without_quote_is_rejected():
    with pytest.raises(ValidationError):
        Decision(decision="Go with vendor B", status="provisional")


def test_decision_with_bad_status_is_rejected():
    with pytest.raises(ValidationError):
        Decision(
            decision="Go with vendor B",
            status="done",
            source_quote="Let's go with B.",
        )


# ---- ActionItem ---------------------------------------------------------

def test_valid_action_item_works():
    item = ActionItem(
        task="Email the vendor",
        source_quote="I'll email the vendor.",
    )
    assert item.owner is None
    assert item.due_date is None


def test_action_item_without_task_is_rejected():
    with pytest.raises(ValidationError):
        ActionItem(source_quote="I'll email the vendor.")


def test_action_item_without_quote_is_rejected():
    with pytest.raises(ValidationError):
        ActionItem(task="Email the vendor")