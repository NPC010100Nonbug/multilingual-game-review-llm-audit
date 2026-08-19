#!/usr/bin/env python3
"""04a_retest.py — single-annotator cross-lingual test-retest harness (codebook §9.3 #2).

Two modes:

  build   Carve a fixed retest subset from the ALREADY-LABELLED pilot, blank the
          labels, randomise row order, and emit a labelling sheet for Yifan to
          fill as T1 (today) and, after a 10-14 day gap, T2.  Fully reproducible
          from RETEST_SEED, so anyone can reconstruct the exact subset.

  score   Given the two filled sheets (t1, t2), compute raw agreement, Cohen's
          kappa, the confusion matrix, and PRESENT-vs-rest specific agreement,
          per language.  Compare against the PRE-REGISTERED thresholds in
          freeze/preregistration.md (kappa >= 0.60 per language; cross-language
          kappa spread <= 0.15).

Firewall: draws ONLY from pilot_draft (never gold); gold is carved later with
后减前, so these ids being seen twice by the annotator cannot touch it.
Privacy: the labelling sheet carries raw text -> written under data/raw/ (gitignored).
The id manifest (no text) -> data/splits/ (tracked).

Usage:
  python3 scripts/04a_retest.py build
  python3 scripts/04a_retest.py score data/raw/retest_t1_filled.jsonl data/raw/retest_t2_filled.jsonl
"""
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = ROOT / "data" / "pilot" / "pilot_labels_claude.jsonl"
WORKSHEET = ROOT / "data" / "raw" / "pilot_worksheet.jsonl"
MANIFEST = ROOT / "data" / "splits" / "retest_manifest.csv"          # tracked, no text
SHEET = ROOT / "data" / "raw" / "retest_t1_sheet.jsonl"             # gitignored, has text

# ---- PRE-REGISTERED (freeze/preregistration.md §2); change => decision_log ----
RETEST_SEED = 20260810
PER_LANG = 18                       # subset size per language
CLASS_TARGET = {"PRESENT": 7, "ABSENT": 8, "NA": 3}   # per-lang class mix
KAPPA_FLOOR = 0.60
KAPPA_SPREAD_MAX = 0.15
# fields the annotator fills at T1/T2 (mirror codebook §7 core decision fields)
FILL_FIELDS = ["unfair_label", "subtype", "procedural_facet", "borderline"]
# non-identity metadata shown to the annotator (input_schema.md §2)
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


def build():
    labels = load_jsonl(LABELS)
    work = load_jsonl(WORKSHEET) if WORKSHEET.exists() else {}
    by_lang_class = defaultdict(lambda: defaultdict(list))
    for rid, d in labels.items():
        by_lang_class[d["language"]][d["unfair_label"]].append(rid)

    rng = random.Random(RETEST_SEED)
    chosen = []
    for lang in ("en", "zh", "ja"):
        picked = []
        for cls, tgt in CLASS_TARGET.items():
            pool = sorted(by_lang_class[lang].get(cls, []))
            rng.shuffle(pool)
            picked += pool[:tgt]
        # top up to PER_LANG from any remaining, prefer borderline rows for coverage
        remaining = sorted(set().union(*[set(v) for v in by_lang_class[lang].values()]) - set(picked))
        remaining.sort(key=lambda r: (not labels[r].get("borderline"), r))  # borderline first
        i = 0
        while len(picked) < PER_LANG and i < len(remaining):
            picked.append(remaining[i]); i += 1
        chosen += [(lang, r) for r in picked[:PER_LANG]]

    # emit id manifest (tracked, no text)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["review_id", "lang", "role"])
        for lang, rid in chosen:
            w.writerow([rid, lang, "retest"])

    # emit blank labelling sheet (gitignored, WITH text), rows shuffled so T1 order
    # differs from the original pilot order; language order rotated across the sheet
    sheet_rows = []
    for lang, rid in chosen:
        w = work.get(rid, {})
        row = {"review_id": rid, "lang": lang,
               "review": w.get("review", "(text only in local worksheet)")}
        row.update({k: w.get(k) for k in SHOW_META})
        row.update({f: None for f in FILL_FIELDS})   # blanks for the annotator
        sheet_rows.append(row)
    rng.shuffle(sheet_rows)                            # break original order
    with SHEET.open("w") as f:
        for r in sheet_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"retest manifest -> {MANIFEST}  ({len(chosen)} ids, no text, tracked)")
    print(f"T1 blank sheet  -> {SHEET}  ({len(sheet_rows)} rows, WITH text, gitignored)")
    print("by lang x class (from existing labels):")
    for lang in ("en", "zh", "ja"):
        c = Counter(labels[r]["unfair_label"] for l, r in chosen if l == lang)
        print(f"  {lang}: {dict(c)}")
    print("\nNEXT: copy the sheet to data/raw/retest_t1_filled.jsonl, fill the blank "
          "fields = T1. Wait 10-14 days, re-shuffle & fill again = T2. Then: score.")


def cohen_kappa(a, b):
    """multiclass Cohen's kappa for two equal-length label lists."""
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[k] / n) * (cb[k] / n) for k in set(ca) | set(cb))
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def score(t1_path, t2_path):
    t1 = load_jsonl(Path(t1_path)); t2 = load_jsonl(Path(t2_path))
    ids = sorted(set(t1) & set(t2))
    if not ids:
        sys.exit("no shared review_ids between t1 and t2 — check the files")
    per_lang_kappa = {}
    for lang in ("en", "zh", "ja"):
        la = [t1[i]["unfair_label"] for i in ids if t1[i].get("lang") == lang]
        lb = [t2[i]["unfair_label"] for i in ids if t1[i].get("lang") == lang]
        if not la:
            continue
        k = cohen_kappa(la, lb)
        raw = sum(x == y for x, y in zip(la, lb)) / len(la)
        # PRESENT-vs-rest specific agreement
        pa = ["P" if x == "PRESENT" else "O" for x in la]
        pb = ["P" if x == "PRESENT" else "O" for x in lb]
        spa = cohen_kappa(pa, pb)
        per_lang_kappa[lang] = k
        mark = "PASS" if k >= KAPPA_FLOOR else "FAIL"
        print(f"[{lang}] n={len(la)} raw={raw:.2f} kappa={k:.2f} ({mark} vs {KAPPA_FLOOR}) "
              f"PRESENT-vs-rest kappa={spa:.2f}")
        conf = Counter((x, y) for x, y in zip(la, lb) if x != y)
        if conf:
            print("     disagreements:", dict(conf))
    if len(per_lang_kappa) > 1:
        spread = max(per_lang_kappa.values()) - min(per_lang_kappa.values())
        mark = "PASS" if spread <= KAPPA_SPREAD_MAX else "FAIL"
        print(f"cross-language kappa spread = {spread:.2f} ({mark} vs {KAPPA_SPREAD_MAX})")
    print("\ncompare against freeze/preregistration.md §2 before freezing.")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        build()
    elif len(sys.argv) == 4 and sys.argv[1] == "score":
        score(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
