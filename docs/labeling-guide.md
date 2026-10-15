# Labeling Guide

Rules for writing answer keys. The same rules are in CLAUDE.md and the prompt.

## Decision
A choice the group made, or a specific choice they tried to make and left open.
Test: "what was chosen?" Discussion that settles nothing is not a decision.
Reversed decision: if a decision is changed later in the meeting, label only the final decision.

## Action item
A task someone has to do after the meeting. Test: "who is doing what?"
A decision that already names an owner stays a decision. Do not also add it as an
action item. Only add an action item for a separate task.

## Status (decisions only)
- final: made, nothing attached
- provisional: made, with a condition or a planned revisit. Hedged wording
  ("let's probably go with") counts as provisional.
- unresolved: clearly debated, left open

## Owner
The person who takes charge or accepts the task. Announcing a decision does not
make you its owner. "Someone", "we" and "everyone" mean owner = null.
If an unlabeled transcript names a person who takes the task, that person is the owner.

## Due date
The spoken words ("by Friday", "next week"). null if none.

## Source quote
Copied word for word from ONE turn (or one paragraph). Long enough to include
the sentence that shows the owner, if it is in the same turn.

## Must NOT be extracted
For each transcript, list tempting items that are not decisions or tasks
(status updates, wishes, ideas nobody acted on).

## How a model item matches a key item (used by the scoring script)
An item matches when its source quote overlaps the key's quote. Owner and
status are checked separately.

## Eval discipline
- Never tune the prompt on the test set. Once a test meeting is used to change
  the prompt, it becomes a dev meeting, and a fresh test set is needed for any final claim.
- Label the answer key before running the model on that meeting, and commit the
  key before the run.