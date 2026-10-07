EXTRACTION_PROMPT = """
The following prompt is used to take a meeting transcript and pull the decisions
and action items out of it. The transcript could be a labeled transcript with the
speaker's name, timestamp and text, or an unlabeled transcript with just text, no
speaker names and no timestamps. Every turn or paragraph of the transcript is
numbered so that you can tell where things were said.

Your job is only to find the decisions and the action items in the transcript.
Do not summarize the meeting and do not answer any questions about it.

FIELDS:

Decision: Something the group agreed on or settled during the meeting, basically
a choice that was made. A good way to check is to ask "what was chosen?"
In the following example "[00:01:47] Priya: Agreed. We're dropping dark mode from
the beta. It can come back after launch." the decision is "We're dropping dark
mode from the beta." The source quote is "Agreed. We're dropping dark mode from
the beta. It can come back after launch." A decision is not the same thing as an
action item.

Action item: A task that someone has to do after the meeting. A good way to check
is to ask "who is doing what?" For example, "Sam: I'll email the vendor." Here the
action item is "email the vendor". In the dark mode example above there is no
action item, because nobody is being asked to do anything, the group is only
choosing what goes into the beta.

Status: How final the decision is. Status only applies to decisions, not to action
items. It can be final, provisional or unresolved.
Final is for when the decision was made and there is nothing attached to it, no
"ifs" or "buts". For example, "Let's go with Vendor B."
Provisional is for when the decision was made but it has some "ifs" or "buts"
attached to it, basically it has a condition or a planned revisit. For example,
"Let's go with Vendor B, but only if legal signs off."
Unresolved is for when the group clearly talked about a specific choice but did
not make the decision and left it open. For example, "We still haven't decided
between Vendor A and Vendor B." Only use unresolved when the group was clearly
trying to decide something. Do not make one up out of general discussion.

Condition: The "ifs" and "buts" attached to a decision. For example, "We will go
with Vendor B after we speak to Vendor A." Here the decision is "go with Vendor B"
and the condition is "after we speak to Vendor A". Use the words from the
transcript. If the decision has no condition, leave the condition empty.

Owner: The person who is responsible for an action item. For example, "Priya will
email the vendor." Here the owner is "Priya" for the action item "email the
vendor". It's not just the speaking person who is the owner, an owner of an action
item could be someone who was assigned to do it by someone else. For example,
"Priya: Sam, can you email the vendor?" followed by "Sam: Sure." Here the owner is
"Sam", because Sam is the one who accepted the task. If nobody was assigned the
task and nobody accepted it, for example "Someone should email the vendor."
followed by "Yeah, true.", leave the owner empty. Never guess an owner. An empty
owner is always better than a wrong one.

Due date: When an action item needs to be done, written as the words that were
spoken. For example, "by Friday" or "next week". If no deadline was mentioned,
leave the due date empty. Do not turn it into a calendar date.

Source quote: The exact words from the transcript that show the decision or the
action item. Copy them word for word, do not paraphrase them and do not fix the
grammar. Every decision and every action item needs a source quote. If you cannot
quote it from the transcript, do not include it.

WHAT TO SKIP:
Discussion that doesn't settle anything, for example "We should probably look into
caching." Small talk and background information. Notes that look like a speaker
label but are not decisions, for example "Note: the budget figures below are
estimates."

UNLABELED TRANSCRIPTS:
If the transcript has no speaker names, you do not know who is speaking. In that
case only give an owner if the text itself names a person, for example "Priya will
own the launch date." Otherwise leave the owner empty.

IF THERE IS NOTHING TO EXTRACT:
If the transcript has no decisions, or no action items, return an empty list for
that kind. Do not invent items to fill the list.
"""