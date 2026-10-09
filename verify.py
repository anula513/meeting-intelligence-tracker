def normalize(text):
    """Collapse all whitespace into single spaces."""
    return " ".join(text.split())


def quote_is_verbatim(quote, text):
    """Return True if the quote appears word for word in the text."""
    quote = normalize(quote)
    if not quote:          # an empty quote proves nothing
        return False
    return quote in normalize(text)

def find_bad_quotes(result, transcript_text):
    """Return a list of quotes that are NOT word for word in the transcript."""
    bad = []

    for d in result.decisions:
        if not quote_is_verbatim(d.source_quote, transcript_text):
            bad.append(f"decision: {d.source_quote}")

    for a in result.action_items:
        if not quote_is_verbatim(a.source_quote, transcript_text):
            bad.append(f"action item: {a.source_quote}")

    return bad
