"""Score saved model outputs (output/) against hand-labeled keys (eval/keys/).

Two scores are printed side by side:
  strict   = quotes overlap (one contains the other)
  adjusted = strict, plus pairs whose quotes sit in ADJACENT turns
             (e.g. the model quoted the answer turn instead of the question turn)

PASS/FAIL against the charter uses strict numbers only. Adjusted is informational.

This script does NOT call the OpenAI API. Run run_eval.py first to make outputs.

Usage:
    python score.py
    python score.py --report docs/baseline-report.md
"""
import argparse
import json
from datetime import date
from pathlib import Path

from parser import parse_transcript
from verify import normalize

KEYS_DIR = Path("eval/keys")
OUTPUT_DIR = Path("output")
TRANSCRIPTS_DIR = Path("sample_transcripts")
SPLITS = ["dev", "test"]

# Charter targets (docs/01-charter.md), checked on strict "fully correct" decisions
TARGET_PRECISION = 0.80
TARGET_RECALL = 0.70
TARGET_INVENTED_OWNERS = 0

DEV_LABEL = "Dev practice numbers (inflated, the prompt was tuned on these two)"
TEST_LABEL = "Test baseline"


# ---- strict matching ----

def quotes_overlap(a, b):
    """True if one quote contains the other, ignoring extra whitespace.

    An empty quote never matches, because "" is inside every string.
    """
    a = normalize(a or "")
    b = normalize(b or "")
    if not a or not b:
        return False
    return a in b or b in a


def find_match(key_item, model_items, used):
    """Return the position of the first unused model item that overlaps key_item, or None."""
    for i, model_item in enumerate(model_items):
        if i in used:
            continue
        if quotes_overlap(model_item["source_quote"], key_item["source_quote"]):
            return i
    return None


def match_items(model_items, key_items):
    """Pair each key item with at most one model item (one-to-one).

    Returns (pairs, misses, extras):
      pairs  = list of (model_item, key_item)
      misses = key items that no model item matched
      extras = model items that matched no key item
    """
    used = set()  # positions of model items already paired
    pairs = []
    misses = []

    for key_item in key_items:
        i = find_match(key_item, model_items, used)
        if i is None:
            misses.append(key_item)
        else:
            used.add(i)
            pairs.append((model_items[i], key_item))

    extras = [m for i, m in enumerate(model_items) if i not in used]
    return pairs, misses, extras


# ---- adjusted matching (adjacent turns) ----

def clean_owner(owner):
    """Trim and lowercase an owner. None and "" both become "" (no owner)."""
    return (owner or "").strip().lower()


def load_turns(stem):
    """Return the text of each turn (or paragraph) in the transcript, or None if it is missing."""
    path = TRANSCRIPTS_DIR / (stem + ".txt")
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    return [turn["text"] for turn in parse_transcript(text)]


def find_turn(quote, turns):
    """Return the position of the first turn that contains the quote, or None if no single turn does."""
    quote = normalize(quote or "")
    if not quote:
        return None
    for i, turn_text in enumerate(turns):
        if quote in normalize(turn_text):
            return i
    return None


def can_pair_adjusted(model_item, key_item, kind):
    """Owner (and status) rules for an adjusted pair. Turns are checked separately.

    Action items: same owner, and it must not be null.
    Decisions: same owner (both null is fine) AND same status.
    One null owner and one named owner never pair, so invented owners can't be hidden.
    """
    model_owner = clean_owner(model_item.get("owner"))
    key_owner = clean_owner(key_item.get("owner"))

    if kind == "action item":
        return model_owner != "" and model_owner == key_owner

    return model_owner == key_owner and model_item.get("status") == key_item.get("status")


def adjusted_match(misses, extras, turns, kind):
    """Second pass: pair leftover misses and extras whose quotes are in adjacent turns.

    Strict pairs are never touched, so adjusted can only add pairs.
    Returns (new_pairs, misses_left, extras_left, warnings).
    """
    if not misses or not extras:
        return [], misses, extras, []  # nothing to pair up
    if turns is None:
        return [], misses, extras, []  # no transcript (warned when loading)

    # Find the turn of every leftover quote once
    key_turns = [find_turn(k["source_quote"], turns) for k in misses]
    model_turns = [find_turn(m["source_quote"], turns) for m in extras]

    warnings = []
    for item, turn in zip(misses, key_turns):
        if turn is None:
            warnings.append(f"turn unknown, no adjusted pair for key {kind}: {item['source_quote']}")
    for item, turn in zip(extras, model_turns):
        if turn is None:
            warnings.append(f"turn unknown, no adjusted pair for model {kind}: {item['source_quote']}")

    used = set()  # positions of extras already paired
    new_pairs = []
    misses_left = []

    for key_item, key_turn in zip(misses, key_turns):
        match = None
        if key_turn is not None:
            for i, (model_item, model_turn) in enumerate(zip(extras, model_turns)):
                if i in used or model_turn is None:
                    continue
                adjacent = abs(model_turn - key_turn) == 1
                if adjacent and can_pair_adjusted(model_item, key_item, kind):
                    match = i
                    break

        if match is None:
            misses_left.append(key_item)
        else:
            used.add(match)
            new_pairs.append((extras[match], key_item))

    extras_left = [m for i, m in enumerate(extras) if i not in used]
    return new_pairs, misses_left, extras_left, warnings


# ---- scoring one list (decisions or action items) ----

def is_in_must_not(item, must_not_extract):
    """True if the item's quote overlaps any must_not_extract quote."""
    return any(quotes_overlap(item["source_quote"], q) for q in must_not_extract)


def count_pairs(pairs, n_model, n_key, kind):
    """Raw counts for one set of pairs."""
    check_status = kind == "decision"
    counts = {
        "model": n_model,              # items the model returned
        "key": n_key,                  # items in the answer key
        "found": len(pairs),           # matched
        "fully_correct": 0,            # matched AND owner (and status) right
        "owner_correct": 0,
        "status_correct": 0,
        "invented_owners": 0,
    }

    for model_item, key_item in pairs:
        model_owner = clean_owner(model_item.get("owner"))
        key_owner = clean_owner(key_item.get("owner"))
        owner_ok = model_owner == key_owner
        status_ok = model_item.get("status") == key_item.get("status")

        if owner_ok:
            counts["owner_correct"] += 1
        # Invented owner: the key says nobody owns it, but the model named someone
        if key_owner == "" and model_owner != "":
            counts["invented_owners"] += 1
        if check_status and status_ok:
            counts["status_correct"] += 1
        if owner_ok and (status_ok or not check_status):
            counts["fully_correct"] += 1

    return counts


def mismatch_problems(pairs, kind):
    """Readable lines for every owner or status mismatch in matched pairs."""
    problems = []
    for model_item, key_item in pairs:
        if clean_owner(model_item.get("owner")) != clean_owner(key_item.get("owner")):
            problems.append(f"OWNER {kind}: model={model_item.get('owner')!r} "
                            f"key={key_item.get('owner')!r} | {key_item['source_quote']}")
        if kind == "decision" and model_item.get("status") != key_item.get("status"):
            problems.append(f"STATUS {kind}: model={model_item.get('status')!r} "
                            f"key={key_item.get('status')!r} | {key_item['source_quote']}")
    return problems


def score_list(model_items, key_items, must_not_extract, kind, turns=None):
    """Score one kind of item. kind is "decision" or "action item".

    Returns (strict_counts, adjusted_counts, problems, warnings).
    """
    strict_pairs, misses, extras = match_items(model_items, key_items)
    new_pairs, misses, extras, warnings = adjusted_match(misses, extras, turns, kind)

    strict = count_pairs(strict_pairs, len(model_items), len(key_items), kind)
    adjusted = count_pairs(strict_pairs + new_pairs, len(model_items), len(key_items), kind)

    # Adjusted pairs always have matching owners (and status), so only strict pairs can mismatch
    problems = mismatch_problems(strict_pairs, kind)

    for model_item, key_item in new_pairs:
        problems.append(f"ADJUSTED {kind} (adjacent turns): model={model_item['source_quote']!r} "
                        f"key={key_item['source_quote']!r}")

    # Misses and extras that are left even after the adjusted pass
    for key_item in misses:
        problems.append(f"MISS {kind}: {key_item['source_quote']}")
    for model_item in extras:
        flag = " [MUST-NOT-EXTRACT]" if is_in_must_not(model_item, must_not_extract) else ""
        problems.append(f"EXTRA {kind}{flag}: {model_item['source_quote']}")

    return strict, adjusted, problems, warnings


def score_transcript(output, key, turns=None):
    """Score one transcript's output against its key.

    turns is the list of turn texts. Without it, no adjusted pairs are made.
    """
    must_not = key.get("must_not_extract", [])
    dec_strict, dec_adjusted, dec_problems, dec_warnings = score_list(
        output.get("decisions", []), key.get("decisions", []), must_not, "decision", turns)
    act_strict, act_adjusted, act_problems, act_warnings = score_list(
        output.get("action_items", []), key.get("action_items", []), must_not, "action item", turns)

    return {
        "split": key.get("split"),
        "decisions": dec_strict,
        "action_items": act_strict,
        "adjusted": {"decisions": dec_adjusted, "action_items": act_adjusted},
        "unverified": len(output.get("unverified_quotes", [])),
        "problems": dec_problems + act_problems,
        "warnings": dec_warnings + act_warnings,
    }


# ---- turning counts into numbers ----

def ratio(part, whole, empty_value=None):
    """part / whole, or empty_value when whole is 0."""
    if whole == 0:
        return empty_value
    return part / whole


def metrics(counts):
    """Precision, recall and accuracies from raw counts.

    0 model items -> precision 1.0 (it said nothing wrong).
    0 key items   -> recall 1.0 (there was nothing to find).
    Accuracies are over matched items only; None means no matches.
    """
    return {
        "precision_found": ratio(counts["found"], counts["model"], 1.0),
        "recall_found": ratio(counts["found"], counts["key"], 1.0),
        "precision_correct": ratio(counts["fully_correct"], counts["model"], 1.0),
        "recall_correct": ratio(counts["fully_correct"], counts["key"], 1.0),
        "owner_accuracy": ratio(counts["owner_correct"], counts["found"]),
        "status_accuracy": ratio(counts["status_correct"], counts["found"]),
    }


def add_counts(total, counts):
    """Add one transcript's counts into a running total (micro-averaging)."""
    for name, value in counts.items():
        total[name] = total.get(name, 0) + value


def split_totals(results, split):
    """Add up every transcript in one split, strict and adjusted."""
    total = {
        "transcripts": 0,
        "decisions": {},
        "action_items": {},
        "adjusted": {"decisions": {}, "action_items": {}},
        "unverified": 0,
    }
    for r in results.values():
        if r["split"] != split:
            continue
        total["transcripts"] += 1
        add_counts(total["decisions"], r["decisions"])
        add_counts(total["action_items"], r["action_items"])
        add_counts(total["adjusted"]["decisions"], r["adjusted"]["decisions"])
        add_counts(total["adjusted"]["action_items"], r["adjusted"]["action_items"])
        total["unverified"] += r["unverified"]
    return total


def invented_owners(scores):
    """Invented owners across decisions and action items (strict pairs)."""
    return scores["decisions"]["invented_owners"] + scores["action_items"]["invented_owners"]


def check_targets(total):
    """PASS/FAIL against the charter, using strict fully correct decisions."""
    m = metrics(total["decisions"])
    return {
        "precision": m["precision_correct"] >= TARGET_PRECISION,
        "recall": m["recall_correct"] >= TARGET_RECALL,
        "invented_owners": invented_owners(total) <= TARGET_INVENTED_OWNERS,
    }


# ---- loading files ----

def load_results():
    """Score every key that has a saved output. Returns {stem: result}."""
    results = {}
    for key_path in sorted(KEYS_DIR.glob("*.json")):
        stem = key_path.stem
        key = json.loads(key_path.read_text(encoding="utf-8"))
        out_path = OUTPUT_DIR / key_path.name

        if key.get("split") not in SPLITS:
            print(f"SKIP {stem}: split must be one of {SPLITS}")
            continue
        if not out_path.exists():
            print(f"SKIP {stem}: no output, run run_eval.py")
            continue

        turns = load_turns(stem)
        output = json.loads(out_path.read_text(encoding="utf-8"))
        result = score_transcript(output, key, turns)
        if turns is None:
            result["warnings"].insert(0, "no transcript found, no adjusted pairs for this transcript")
        results[stem] = result
    return results


# ---- printing ----

def pct(value):
    """Format a ratio as a percent, or n/a."""
    return "n/a" if value is None else f"{value:.0%}"


METRIC_LABELS = [
    ("precision_found", "precision (found)"),
    ("recall_found", "recall (found)"),
    ("precision_correct", "precision (fully correct)"),
    ("recall_correct", "recall (fully correct)"),
    ("owner_accuracy", "owner accuracy (matched)"),
    ("status_accuracy", "status accuracy (matched)"),
]


def comparison_rows(strict, adjusted):
    """Rows of (label, strict %, adjusted %).

    strict and adjusted are dicts with "decisions" and "action_items" counts.
    """
    rows = []
    for kind_label, kind_key in [("Decision", "decisions"), ("Action item", "action_items")]:
        s = metrics(strict[kind_key])
        a = metrics(adjusted[kind_key])
        for metric_name, metric_label in METRIC_LABELS:
            if kind_key == "action_items" and metric_name == "status_accuracy":
                continue  # action items have no status
            rows.append((f"{kind_label} {metric_label}", pct(s[metric_name]), pct(a[metric_name])))
    return rows


def print_block(title, strict, adjusted, unverified):
    """Print strict and adjusted numbers side by side."""
    print(title)
    print(f"  {'':38} {'strict':>8} {'adjusted':>9}")
    for label, s, a in comparison_rows(strict, adjusted):
        print(f"  {label:38} {s:>8} {a:>9}")
    for kind_label, kind_key in [("decisions", "decisions"), ("action items", "action_items")]:
        print(f"  {kind_label} matched: {strict[kind_key]['found']} strict, "
              f"{adjusted[kind_key]['found']} adjusted, of {strict[kind_key]['key']} in key "
              f"({strict[kind_key]['model']} returned)")
    print(f"  invented owners {invented_owners(strict)} | unverified quotes {unverified}")


def print_targets(total):
    """Print PASS/FAIL lines for one split (strict numbers only)."""
    d = metrics(total["decisions"])
    a = metrics(total["action_items"])
    passed = check_targets(total)

    def word(ok):
        return "PASS" if ok else "FAIL"

    print(f"  decision precision (fully correct) {pct(d['precision_correct'])} "
          f"target >= {TARGET_PRECISION:.0%}  {word(passed['precision'])}")
    print(f"  decision recall    (fully correct) {pct(d['recall_correct'])} "
          f"target >= {TARGET_RECALL:.0%}  {word(passed['recall'])}")
    print(f"  invented owners {invented_owners(total)} target = {TARGET_INVENTED_OWNERS}  "
          f"{word(passed['invented_owners'])}")
    print(f"  action item precision {pct(a['precision_correct'])}, "
          f"recall {pct(a['recall_correct'])} (fully correct, no target)")


def print_results(results):
    print("=== Per transcript ===")
    for stem, r in results.items():
        print_block(f"{stem} ({r['split']})", r, r["adjusted"], r["unverified"])

    for split in SPLITS:
        total = split_totals(results, split)
        label = DEV_LABEL if split == "dev" else TEST_LABEL
        print(f"\n=== {label} ===")
        if total["transcripts"] == 0:
            print("  no transcripts scored yet")
            continue
        print_block(f"{total['transcripts']} transcripts (micro-averaged)",
                    total, total["adjusted"], total["unverified"])
        print("Targets (strict only):")
        print_targets(total)

    print("\n=== Problems to read ===")
    any_problems = False
    for stem, r in results.items():
        for line in r["problems"]:
            print(f"{stem}: {line}")
            any_problems = True
    if not any_problems:
        print("none")

    print("\n=== Warnings ===")
    any_warnings = False
    for stem, r in results.items():
        for line in r["warnings"]:
            print(f"{stem}: WARNING {line}")
            any_warnings = True
    if not any_warnings:
        print("none")


# ---- markdown report ----

def report_section(label, total):
    """Markdown table of one split's totals, strict and adjusted side by side."""
    lines = [f"## {label}", ""]
    if total["transcripts"] == 0:
        return lines + ["No transcripts scored yet.", ""]

    passed = check_targets(total)

    def word(ok):
        return "PASS" if ok else "FAIL"

    # Only these rows have a charter target (checked on strict numbers)
    targets = {
        "Decision precision (fully correct)": (f">= {TARGET_PRECISION:.0%}", word(passed["precision"])),
        "Decision recall (fully correct)": (f">= {TARGET_RECALL:.0%}", word(passed["recall"])),
    }

    lines += [
        f"Transcripts: {total['transcripts']} (micro-averaged)",
        "",
        "| Metric | Strict | Adjusted | Target | Result (strict) |",
        "|---|---|---|---|---|",
    ]
    for row_label, s, a in comparison_rows(total, total["adjusted"]):
        target, result = targets.get(row_label, ("-", "-"))
        lines.append(f"| {row_label} | {s} | {a} | {target} | {result} |")

    lines += [
        f"| Invented owners | {invented_owners(total)} | | = {TARGET_INVENTED_OWNERS} "
        f"| {word(passed['invented_owners'])} |",
        f"| Unverified quotes | {total['unverified']} | | | |",
        "",
    ]
    return lines


def build_report(results):
    """Build the whole markdown report as one string."""
    lines = [
        "# Evaluation Report",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "Made by `python score.py --report`.",
        "",
        "- **Strict:** a model item matches a key item when their source quotes overlap "
        "(one contains the other). \"Fully correct\" means matched AND owner equal AND, "
        "for decisions, status equal. PASS/FAIL uses strict fully correct decisions.",
        "- **Adjusted (informational only):** strict, plus leftover items whose quotes are "
        "in adjacent turns. Action items also need the same non-null owner. Decisions also "
        "need the same owner (both null is allowed) and the same status.",
        "",
        "Invented owner = the key's owner is null but the model gave one. This is stricter "
        "than the charter's definition (an owner that never appears in the transcript).",
        "",
        "Eval set: 10 planned (charter says 15, to revisit).",
        "",
    ]
    for split in SPLITS:
        label = DEV_LABEL if split == "dev" else TEST_LABEL
        lines += report_section(label, split_totals(results, split))

    lines += [
        "## Per transcript (strict, fully correct)",
        "",
        "| Transcript | Split | Dec P | Dec R | Action P | Action R | Invented owners "
        "| Unverified | Adjusted pairs |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for stem, r in results.items():
        d = metrics(r["decisions"])
        a = metrics(r["action_items"])
        added = (r["adjusted"]["decisions"]["found"] - r["decisions"]["found"]
                 + r["adjusted"]["action_items"]["found"] - r["action_items"]["found"])
        lines.append(f"| {stem} | {r['split']} | {pct(d['precision_correct'])} "
                     f"| {pct(d['recall_correct'])} | {pct(a['precision_correct'])} "
                     f"| {pct(a['recall_correct'])} | {invented_owners(r)} | {r['unverified']} "
                     f"| {added} |")

    lines += ["", "## What failed and why", "", "<!-- Fill this in by hand. -->", ""]
    return "\n".join(lines)


def write_report(results, path):
    """Write the report, but never overwrite an existing file (it may hold your notes)."""
    path = Path(path)
    if path.exists():
        print(f"\nNOT writing {path}: it already exists. Delete or rename it first.")
        return False
    path.write_text(build_report(results), encoding="utf-8")
    print(f"\nWrote {path}")
    return True


def main():
    arg_parser = argparse.ArgumentParser(description="Score outputs against answer keys.")
    arg_parser.add_argument("--report", help="write a markdown report to this path")
    args = arg_parser.parse_args()

    results = load_results()
    if not results:
        print("Nothing to score. Add keys to eval/keys/ and run run_eval.py.")
        return

    print_results(results)
    if args.report:
        write_report(results, args.report)


if __name__ == "__main__":
    main()
