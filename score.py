"""Score saved model outputs (output/) against hand-labeled keys (eval/keys/).

This script does NOT call the OpenAI API. Run run_eval.py first to make outputs.

Usage:
    python score.py
    python score.py --report docs/baseline-report.md
"""
import argparse
import json
from datetime import date
from pathlib import Path

from verify import normalize

KEYS_DIR = Path("eval/keys")
OUTPUT_DIR = Path("output")
SPLITS = ["dev", "test"]

# Charter targets (docs/01-charter.md), checked on "fully correct" decisions
TARGET_PRECISION = 0.80
TARGET_RECALL = 0.70
TARGET_INVENTED_OWNERS = 0

DEV_LABEL = "Dev practice numbers (inflated, the prompt was tuned on these two)"
TEST_LABEL = "Test baseline"


# ---- matching ----

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


# ---- scoring one list (decisions or action items) ----

def clean_owner(owner):
    """Trim and lowercase an owner. None and "" both become "" (no owner)."""
    return (owner or "").strip().lower()


def is_in_must_not(item, must_not_extract):
    """True if the item's quote overlaps any must_not_extract quote."""
    return any(quotes_overlap(item["source_quote"], q) for q in must_not_extract)


def score_list(model_items, key_items, must_not_extract, kind):
    """Score one kind of item. kind is "decision" or "action item".

    Returns (counts, problems). counts are raw numbers; problems are
    readable lines describing every miss, extra and mismatch.
    """
    check_status = kind == "decision"
    pairs, misses, extras = match_items(model_items, key_items)

    counts = {
        "model": len(model_items),     # items the model returned
        "key": len(key_items),         # items in the answer key
        "found": len(pairs),           # quote matched
        "fully_correct": 0,            # quote matched AND owner (and status) right
        "owner_correct": 0,
        "status_correct": 0,
        "invented_owners": 0,
    }
    problems = []

    for model_item, key_item in pairs:
        model_owner = clean_owner(model_item.get("owner"))
        key_owner = clean_owner(key_item.get("owner"))
        owner_ok = model_owner == key_owner
        status_ok = model_item.get("status") == key_item.get("status")

        if owner_ok:
            counts["owner_correct"] += 1
        else:
            problems.append(f"OWNER {kind}: model={model_item.get('owner')!r} "
                            f"key={key_item.get('owner')!r} | {key_item['source_quote']}")

        # Invented owner: the key says nobody owns it, but the model named someone
        if key_owner == "" and model_owner != "":
            counts["invented_owners"] += 1

        if check_status:
            if status_ok:
                counts["status_correct"] += 1
            else:
                problems.append(f"STATUS {kind}: model={model_item.get('status')!r} "
                                f"key={key_item.get('status')!r} | {key_item['source_quote']}")

        if owner_ok and (status_ok or not check_status):
            counts["fully_correct"] += 1

    for key_item in misses:
        problems.append(f"MISS {kind}: {key_item['source_quote']}")

    for model_item in extras:
        flag = " [MUST-NOT-EXTRACT]" if is_in_must_not(model_item, must_not_extract) else ""
        problems.append(f"EXTRA {kind}{flag}: {model_item['source_quote']}")

    return counts, problems


def score_transcript(output, key):
    """Score one transcript's output against its key."""
    must_not = key.get("must_not_extract", [])
    dec_counts, dec_problems = score_list(
        output.get("decisions", []), key.get("decisions", []), must_not, "decision")
    act_counts, act_problems = score_list(
        output.get("action_items", []), key.get("action_items", []), must_not, "action item")

    return {
        "split": key.get("split"),
        "decisions": dec_counts,
        "action_items": act_counts,
        "unverified": len(output.get("unverified_quotes", [])),
        "problems": dec_problems + act_problems,
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
    """Add up every transcript in one split."""
    total = {"transcripts": 0, "decisions": {}, "action_items": {}, "unverified": 0}
    for r in results.values():
        if r["split"] != split:
            continue
        total["transcripts"] += 1
        add_counts(total["decisions"], r["decisions"])
        add_counts(total["action_items"], r["action_items"])
        total["unverified"] += r["unverified"]
    return total


def check_targets(total):
    """PASS/FAIL against the charter, using fully correct decisions."""
    m = metrics(total["decisions"])
    invented = total["decisions"]["invented_owners"] + total["action_items"]["invented_owners"]
    return {
        "precision": m["precision_correct"] >= TARGET_PRECISION,
        "recall": m["recall_correct"] >= TARGET_RECALL,
        "invented_owners": invented <= TARGET_INVENTED_OWNERS,
    }


# ---- loading files ----

def load_results():
    """Score every key that has a saved output. Returns {stem: result}."""
    results = {}
    for key_path in sorted(KEYS_DIR.glob("*.json")):
        key = json.loads(key_path.read_text(encoding="utf-8"))
        out_path = OUTPUT_DIR / key_path.name

        if key.get("split") not in SPLITS:
            print(f"SKIP {key_path.stem}: split must be one of {SPLITS}")
            continue
        if not out_path.exists():
            print(f"SKIP {key_path.stem}: no output, run run_eval.py")
            continue

        output = json.loads(out_path.read_text(encoding="utf-8"))
        results[key_path.stem] = score_transcript(output, key)
    return results


# ---- printing ----

def pct(value):
    """Format a ratio as a percent, or n/a."""
    return "n/a" if value is None else f"{value:.0%}"


def print_block(title, decisions, action_items, unverified):
    """Print the numbers for one transcript or one split total."""
    d = metrics(decisions)
    a = metrics(action_items)
    invented = decisions["invented_owners"] + action_items["invented_owners"]
    print(title)
    print(f"  decisions     found P {pct(d['precision_found'])} R {pct(d['recall_found'])}"
          f" | fully correct P {pct(d['precision_correct'])} R {pct(d['recall_correct'])}"
          f" | owner {pct(d['owner_accuracy'])} | status {pct(d['status_accuracy'])}"
          f" | {decisions['found']}/{decisions['key']} found, {decisions['model']} returned")
    print(f"  action items  found P {pct(a['precision_found'])} R {pct(a['recall_found'])}"
          f" | fully correct P {pct(a['precision_correct'])} R {pct(a['recall_correct'])}"
          f" | owner {pct(a['owner_accuracy'])}"
          f" | {action_items['found']}/{action_items['key']} found, {action_items['model']} returned")
    print(f"  invented owners {invented} | unverified quotes {unverified}")


def print_targets(total):
    """Print PASS/FAIL lines for one split."""
    d = metrics(total["decisions"])
    a = metrics(total["action_items"])
    passed = check_targets(total)
    invented = total["decisions"]["invented_owners"] + total["action_items"]["invented_owners"]

    def word(ok):
        return "PASS" if ok else "FAIL"

    print(f"  decision precision (fully correct) {pct(d['precision_correct'])} "
          f"target >= {TARGET_PRECISION:.0%}  {word(passed['precision'])}")
    print(f"  decision recall    (fully correct) {pct(d['recall_correct'])} "
          f"target >= {TARGET_RECALL:.0%}  {word(passed['recall'])}")
    print(f"  invented owners {invented} target = {TARGET_INVENTED_OWNERS}  "
          f"{word(passed['invented_owners'])}")
    print(f"  action item precision {pct(a['precision_correct'])}, "
          f"recall {pct(a['recall_correct'])} (fully correct, no target)")


def print_results(results):
    print("=== Per transcript ===")
    for stem, r in results.items():
        print_block(f"{stem} ({r['split']})", r["decisions"], r["action_items"], r["unverified"])

    for split in SPLITS:
        total = split_totals(results, split)
        label = DEV_LABEL if split == "dev" else TEST_LABEL
        print(f"\n=== {label} ===")
        if total["transcripts"] == 0:
            print("  no transcripts scored yet")
            continue
        print_block(f"{total['transcripts']} transcripts (micro-averaged)",
                    total["decisions"], total["action_items"], total["unverified"])
        print("Targets:")
        print_targets(total)

    print("\n=== Problems to read ===")
    any_problems = False
    for stem, r in results.items():
        for line in r["problems"]:
            print(f"{stem}: {line}")
            any_problems = True
    if not any_problems:
        print("none")


# ---- markdown report ----

def report_section(label, total):
    """Markdown table of one split's totals."""
    lines = [f"## {label}", ""]
    if total["transcripts"] == 0:
        return lines + ["No transcripts scored yet.", ""]

    d = metrics(total["decisions"])
    a = metrics(total["action_items"])
    passed = check_targets(total)
    invented = total["decisions"]["invented_owners"] + total["action_items"]["invented_owners"]

    def word(ok):
        return "PASS" if ok else "FAIL"

    lines += [
        f"Transcripts: {total['transcripts']} (micro-averaged)",
        "",
        "| Metric | Found | Fully correct | Target | Result |",
        "|---|---|---|---|---|",
        f"| Decision precision | {pct(d['precision_found'])} | {pct(d['precision_correct'])} "
        f"| >= {TARGET_PRECISION:.0%} | {word(passed['precision'])} |",
        f"| Decision recall | {pct(d['recall_found'])} | {pct(d['recall_correct'])} "
        f"| >= {TARGET_RECALL:.0%} | {word(passed['recall'])} |",
        f"| Action item precision | {pct(a['precision_found'])} | {pct(a['precision_correct'])} | - | - |",
        f"| Action item recall | {pct(a['recall_found'])} | {pct(a['recall_correct'])} | - | - |",
        f"| Decision owner accuracy (matched) | {pct(d['owner_accuracy'])} | | | |",
        f"| Decision status accuracy (matched) | {pct(d['status_accuracy'])} | | | |",
        f"| Action item owner accuracy (matched) | {pct(a['owner_accuracy'])} | | | |",
        f"| Invented owners | {invented} | | = {TARGET_INVENTED_OWNERS} "
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
        "Made by `python score.py --report`. A model item matches a key item when their "
        "source quotes overlap (one contains the other). \"Fully correct\" means matched "
        "AND owner equal AND, for decisions, status equal. PASS/FAIL uses fully correct decisions.",
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
        "## Per transcript (fully correct)",
        "",
        "| Transcript | Split | Dec P | Dec R | Action P | Action R | Invented owners | Unverified |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for stem, r in results.items():
        d = metrics(r["decisions"])
        a = metrics(r["action_items"])
        invented = r["decisions"]["invented_owners"] + r["action_items"]["invented_owners"]
        lines.append(f"| {stem} | {r['split']} | {pct(d['precision_correct'])} "
                     f"| {pct(d['recall_correct'])} | {pct(a['precision_correct'])} "
                     f"| {pct(a['recall_correct'])} | {invented} | {r['unverified']} |")

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
