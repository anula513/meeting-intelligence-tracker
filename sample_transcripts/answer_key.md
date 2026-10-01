# Answer key: sample transcripts

The correct extraction for each sample transcript. This is the start of the eval set (step 11). How to match the model's output against it gets decided in step 11.

Rules applied (from CLAUDE.md):
- Decisions, action items and discussion are separate. Discussion is not extracted.
- `owner` is the person who accepts or is assigned the decision or task, not just whoever spoke. If no one is named, it is `null`.
- `source_quote` is copied word for word from the transcript.

---

## 2026-09-15_beta-launch-planning.txt (speaker labels)

### Decisions (4)

| # | Decision | Status | Condition | Owner | Source quote | Location |
|---|---|---|---|---|---|---|
| D1 | Launch the beta on October 1st | provisional | Security review passes | Priya | "Let's go with October 1st, assuming security signs off. I'll own the launch date." | 00:00:44, Priya |
| D2 | Drop dark mode from the beta | final | null | null | "We're dropping dark mode from the beta. It can come back after launch." | 00:01:47, Priya |
| D3 | Switch to the new onboarding flow instead of the old one | final | null | Leo | "we also agreed to switch to the new onboarding flow instead of the old one. Leo, this one's yours." | 00:02:04, Priya |
| D4 | Whether the beta is free or paid | unresolved | null | null | "Okay, we're not going to settle this today. Let's come back to pricing next week." | 00:03:05, Priya |

Traps:
- D2: Priya announces it, but nobody takes ownership. The owner must be `null`, not Priya.
- D3: Priya speaks, but Leo is assigned it and accepts at 00:02:12 ("Sure, I'll take it."). The owner is Leo.

### Action items (3)

| # | Task | Owner | Due date | Source quote | Location |
|---|---|---|---|---|---|
| A1 | Run the pen test | Dana | next week | "I'll run the pen test next week so we know in time." | 00:01:03, Dana |
| A2 | Get the staging environment stable | Marcus | by the 25th | "Marcus, can you get the staging environment stable by the 25th?" | 00:01:10, Priya (Marcus accepts at 00:01:16) |
| A3 | Send the security checklist to the vendor | null | by Friday | "Someone needs to send the security checklist to the vendor by Friday." | 00:03:14, Dana |

Traps:
- A2: Priya speaks, but Marcus is the owner.
- A3: "Someone" is not an owner. Dana raised it but did not take it on.

### Must NOT be extracted

- "Before we start, staging is still a bit flaky. Just flagging it." (00:00:15): a status update.
- "We should probably look into caching at some point too." (00:02:20): a suggestion that wasn't acted on.
- The individual pricing opinions (00:02:41 to 00:02:58): part of D4, not separate decisions.

### Parser check

- 25 speaker turns.
- Leo's turn at 00:01:29 runs over two lines. Both lines belong to one turn.

---

## 2026-09-22_vendor-sync.txt (no speaker labels)

Location is given as a paragraph number (paragraphs are separated by blank lines, counting from 1). The speaker is always `null`.

### Decisions (3)

| # | Decision | Status | Condition | Owner | Source quote | Location |
|---|---|---|---|---|---|---|
| D1 | Go with Vendor B as the analytics vendor | final | null | null | "So we're going with Vendor B. Everyone okay with that? Good, that's decided." | Paragraph 5 |
| D2 | Sign the one-year contract with Vendor B | provisional | Legal approves the data retention terms | null | "We'll sign the one-year contract if legal approves the data retention terms." | Paragraph 6 |
| D3 | Whether to move the old analytics data over | unresolved | null | null | "We didn't reach a conclusion on that one, so let's leave it open for now." | Paragraph 8 |

### Action items (2)

| # | Task | Owner | Due date | Source quote | Location |
|---|---|---|---|---|---|
| A1 | Draft a short summary of the contract terms for legal | Priya | by Wednesday | "Priya will draft a short summary of the contract terms for legal by Wednesday." | Paragraph 7 |
| A2 | Ask finance about the invoice schedule | null | null (acceptable: "before we sign anything") | "Someone should ask finance about the invoice schedule before we sign anything." | Paragraph 9 |

Traps:
- A1: no speaker labels, but the text names Priya, so she is a valid owner.
- D2: "If legal pushes back, we go month to month" is part of the same decision, not a separate one.

### Must NOT be extracted

- "It would be nice to get a demo of their new alerting feature at some point." (paragraph 10): a wish, not an action item.
- The vendor price comparison (paragraphs 3 to 4): reasoning for D1, not separate decisions.

### Parser check

- 11 paragraphs.
- Must be detected as **unlabeled**. Paragraph 2 ("Note: the budget figures...") looks like a `Name:` label, but it is only 1 of 11 paragraphs.
