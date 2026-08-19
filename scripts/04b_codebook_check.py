#!/usr/bin/env python3
"""04b_codebook_check.py — independent blind-check set for the codebook (§9.3 #1).

Tests whether the FROZEN-CANDIDATE codebook is clear enough that a reader who did
NOT draft it can reproduce the labels.  The check set is drawn from pilot rows
that the codebook body does NOT cite as anchors/examples (so it isn't testing on
the very rows the rules were written around).

Two modes:

  build   Carve `codebook_check` from non-cited pilot rows, stratified by
          language x main-label, emit a blank labelling sheet (raw text,
          gitignored) + an id manifest (no text, tracked).  The intended blind
          labeller is a FRESH Claude instance given ONLY the codebook + these
          rows (no drafting memory) — an "independent stranger" proxy; Yifan
          adjudicates disagreements.

  score   Given the blind labels, compare to the reference pilot labels
          (NOT ground truth — the reference face against which disagreements
          localise ambiguous codebook rules), report Cohen's kappa + PRESENT-
          vs-rest specific agreement vs the pre-registered floor.

Firewall: pilot-only, never gold.  Privacy: sheet under data/raw/ (gitignored).
Usage:
  python3 scripts/04b_codebook_check.py build
  python3 scripts/04b_codebook_check.py score data/raw/codebook_check_filled.jsonl
"""
import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = ROOT / "data" / "pilot" / "pilot_labels_claude.jsonl"
WORKSHEET = ROOT / "data" / "raw" / "pilot_worksheet.jsonl"
CODEBOOK = ROOT / "codebook" / "codebook_claude_v1.md"
ANCHOR_CATALOG = ROOT / "data" / "pilot" / "anchor_catalog.jsonl"     # exclude anchors too
MANIFEST = ROOT / "data" / "splits" / "codebook_check_manifest.csv"   # tracked, no text
SHEET = ROOT / "data" / "raw" / "codebook_check_sheet.jsonl"          # gitignored, has text

# ---- PRE-REGISTERED (freeze/preregistration.md §1); change => decision_log ----
CHECK_SEED = 20260810
PER_LANG = 20
KAPPA_FLOOR = 0.65          # Yifan chose the stricter tier (2026-08-10)
PRESENT_SPECIFIC_FLOOR = 0.70
FILL_FIELDS = ["unfair_label", "subtype", "procedural_facet", "borderline"]
SHOW_META = ("voted_up", "votes_funny", "votes_up", "received_for_free",
             "steam_purchase", "weighted_vote_score", "written_during_early_access")


def load_jsonl(path, key="review_id"):
    idx = {}
    for line in path.open():
        line = line.strip()
        if line:
            d = json.loads(line)
            idx[str(d[key])] = d
    return idx


def cited_ids():
    """review_ids used in drafting = codebook body citations UNION anchor_catalog ids.
    Anchors promoted to the catalog may not yet appear in the codebook .md, but they
    ARE now teaching examples, so they must be excluded from the blind-check set too."""
    ids = set(re.findall(r"\b\d{9}\b", CODEBOOK.read_text()))
    if ANCHOR_CATALOG.exists():
        for line in ANCHOR_CATALOG.open():
            line = line.strip()
            if line:
                ids.add(str(json.loads(line)["review_id"]))
    return ids


def build():
    labels = load_jsonl(LABELS)
    work = load_jsonl(WORKSHEET) if WORKSHEET.exists() else {}
    cited = cited_ids()
    eligible = {rid: d for rid, d in labels.items() if rid not in cited}
    print(f"pilot rows: {len(labels)}   codebook-cited: {len(cited & set(labels))}   "
          f"eligible (not cited): {len(eligible)}")

    by_lang_class = defaultdict(lambda: defaultdict(list))
    for rid, d in eligible.items():
        by_lang_class[d["language"]][d["unfair_label"]].append(rid)

    rng = random.Random(CHECK_SEED)
    chosen = []
    for lang in ("en", "zh", "ja"):
        classes = by_lang_class[lang]
        total = sum(len(v) for v in classes.values())
        picked = []
        # proportional allocation by main-label, floor 1 per present class
        for cls, ids in classes.items():
            share = max(1, round(PER_LANG * len(ids) / total)) if total else 0
            pool = sorted(ids); rng.shuffle(pool)
            picked += pool[:share]
        rng.shuffle(picked)
        chosen += [(lang, r) for r in picked[:PER_LANG]]

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["review_id", "lang", "role"])
        for lang, rid in chosen:
            w.writerow([rid, lang, "codebook_check"])

    sheet_rows = []
    for lang, rid in chosen:
        w = work.get(rid, {})
        row = {"review_id": rid, "lang": lang,
               "review": w.get("review", "(text only in local worksheet)")}
        row.update({k: w.get(k) for k in SHOW_META})
        row.update({f: None for f in FILL_FIELDS})
        sheet_rows.append(row)
    rng.shuffle(sheet_rows)
    with SHEET.open("w") as f:
        for r in sheet_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"codebook_check manifest -> {MANIFEST}  ({len(chosen)} ids, tracked)")
    print(f"blind sheet             -> {SHEET}  ({len(sheet_rows)} rows, gitignored)")
    for lang in ("en", "zh", "ja"):
        c = Counter(labels[r]["unfair_label"] for l, r in chosen if l == lang)
        print(f"  {lang}: {dict(c)}")
    print("\nNEXT: a FRESH Claude (codebook + this sheet only) fills the blank "
          "fields -> data/raw/codebook_check_filled.jsonl. Then: score.")


def cohen_kappa(a, b):
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[k] / n) * (cb[k] / n) for k in set(ca) | set(cb))
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def score(blind_path):
    ref = load_jsonl(LABELS)
    blind = load_jsonl(Path(blind_path))
    ids = sorted(set(ref) & set(blind))
    a = [ref[i]["unfair_label"] for i in ids]
    b = [blind[i]["unfair_label"] for i in ids]
    k = cohen_kappa(a, b)
    raw = sum(x == y for x, y in zip(a, b)) / len(a)
    pa = ["P" if x == "PRESENT" else "O" for x in a]
    pb = ["P" if x == "PRESENT" else "O" for x in b]
    spa = cohen_kappa(pa, pb)
    print(f"n={len(ids)} raw={raw:.2f} kappa={k:.2f} "
          f"({'PASS' if k >= KAPPA_FLOOR else 'FAIL'} vs {KAPPA_FLOOR})")
    print(f"PRESENT-vs-rest kappa={spa:.2f} "
          f"({'PASS' if spa >= PRESENT_SPECIFIC_FLOOR else 'FAIL'} vs {PRESENT_SPECIFIC_FLOOR})")
    conf = Counter((x, y) for x, y in zip(a, b) if x != y)
    if conf:
        print("disagreements (ref -> blind):", dict(conf))
        print("-> each disagreement localises a codebook rule to sharpen (fix rules, NOT thresholds).")
    print("\ncompare against freeze/preregistration.md §1 before freezing.")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "build":
        build()
    elif len(sys.argv) == 3 and sys.argv[1] == "score":
        score(sys.argv[2])
    else:
        sys.exit(__doc__)
