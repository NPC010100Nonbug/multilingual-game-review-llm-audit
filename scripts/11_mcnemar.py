#!/usr/bin/env python3
"""Paired McNemar exact test for prompt-version A/B comparisons.

The v0.4-iso development-stage decision protocol names its primary endpoint as a
*paired* comparison ("配对 McNemar 精确检验（双侧）" plus unconditional reporting of
the discordant cell counts b/c). scripts/10_score.py reports marginal rates only.
Marginal rates cannot answer a paired question, so this script exists so that the
number the protocol actually turns on is produced by versioned, re-runnable code
rather than by an ad-hoc snippet.

It compares two or more responses.jsonl files that were produced from the SAME
input file, on a binary per-row indicator, and reports:

  b  = rows where only the FIRST condition fires the indicator
  c  = rows where only the SECOND condition fires the indicator
  two-sided exact McNemar p, computed as the exact binomial test of b out of
  (b+c) against p=0.5 -- no chi-square, no continuity correction, because
  b+c is small here and the asymptotic test is not valid at these counts.

Endpoints:
  hardneg_fp_strict  rows with arm=hardneg and human gold ABSENT; indicator =
                     model said PRESENT.  (protocol primary endpoint, n=71)
  fp_all_absent      all rows with human gold ABSENT; indicator = model PRESENT.
  {en,ja,zh}_recall_miss
                     rows of that language with human gold PRESENT; indicator =
                     model did NOT say PRESENT (a miss).  Fewer is better, so
                     this keeps "lower b/c is better" consistent across endpoints.
                     ja and zh were added 2026-08-28: an endpoint set that could
                     only test English recall is exactly the English-blindness
                     this project exists to correct.
  zh_keyword_all_fp / zh_class1_fp / zh_class24_fp
                     the erratum-D three-way Chinese report as paired tests.
                     Reporting zh_class24_fp alone is not permitted; see
                     scripts/10_score.py.  zh_keyword_all_fp is the union.
  ja_hardneg_fp      Japanese hardneg control for the above.  Japanese has no
                     class1 family, so it cannot be split the same way; the row
                     is here to stop the zh split being read as a language effect.
  Both directions are reported explicitly, so the reader never has to remember
  which way an endpoint points.

Usage:
  python3 scripts/11_mcnemar.py \
      --pred data/runs/<a>/responses.jsonl \
      --pred data/runs/<b>/responses.jsonl \
      [--answer-key data/runs/<a>/answer_key.jsonl] \
      [--endpoint hardneg_fp_strict|all]

Development-stage tool. It reads labels and review_ids only; it never reads or
prints raw review text.
"""

import argparse
import hashlib
import itertools
import json
import os
import sys
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Declared once so build_universe and indicator cannot drift apart.
#   kind "fp"   -> denominator is human-ABSENT rows;   fires on model PRESENT
#   kind "miss" -> denominator is human-PRESENT rows;  fires on anything else
#   lang/arms = None means "no filter on that field".
ZH_KEYWORD_ARMS = ("hardneg", "hardneg_class1_zh")
ENDPOINT_SPECS = {
    "hardneg_fp_strict":  {"kind": "fp",   "lang": None, "arms": ("hardneg",)},
    "fp_all_absent":      {"kind": "fp",   "lang": None, "arms": None},
    "en_recall_miss":     {"kind": "miss", "lang": "en", "arms": None},
    "ja_recall_miss":     {"kind": "miss", "lang": "ja", "arms": None},
    "zh_recall_miss":     {"kind": "miss", "lang": "zh", "arms": None},
    "zh_keyword_all_fp":  {"kind": "fp",   "lang": "zh", "arms": ZH_KEYWORD_ARMS},
    "zh_class1_fp":       {"kind": "fp",   "lang": "zh", "arms": ("hardneg_class1_zh",)},
    "zh_class24_fp":      {"kind": "fp",   "lang": "zh", "arms": ("hardneg",)},
    "ja_hardneg_fp":      {"kind": "fp",   "lang": "ja", "arms": ("hardneg",)},
}
ENDPOINTS = tuple(ENDPOINT_SPECS)
# Erratum D: these three must be reported together or not at all.
ERRATUM_D_SET = ("zh_keyword_all_fp", "zh_class1_fp", "zh_class24_fp", "ja_hardneg_fp")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                sys.exit(f"ERROR: {path}:{line_no} is not valid JSON: {exc}")
    return rows


def model_label(row):
    """PRESENT / ABSENT / NA, or None when the row produced no usable label.

    Matches scripts/10_score.py exactly: a label is unusable only when the row is
    missing, failed to parse, or carries a label outside the schema.  It is NOT
    silently recoded as ABSENT -- that would let a measurement failure
    masquerade as a substantive negative judgment.

    `validation_errors` is deliberately NOT a reason to void the label.  In these
    runs it holds only evidence_span violations (not verbatim / over 200 chars),
    which say nothing about whether unfair_label itself is usable.  Voiding on
    them would also bias this test: an ABSENT row has an empty evidence_span and
    so can never violate, meaning the dropped rows are almost all PRESENT ones.
    """
    if row.get("parse_error"):
        return None
    parsed = row.get("parsed")
    if not isinstance(parsed, dict):
        return None
    label = parsed.get("unfair_label")
    if label not in ("PRESENT", "ABSENT", "NA"):
        return None
    return label


def exact_mcnemar_two_sided(b, c):
    """Exact two-sided McNemar p: binomial(b; b+c, 0.5), two-sided.

    Returns 1.0 when there are no discordant pairs -- with b+c=0 the paired
    design carries no information about a difference, which is a p of 1, not a
    small p.
    """
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / (2.0 ** n)
    return min(1.0, 2.0 * tail)


def min_attainable_p(n):
    """Smallest two-sided exact p reachable with n discordant pairs.

    Reported alongside every comparison so a null result is never mistaken for
    evidence of no difference when the design simply could not reach 0.05.
    """
    return exact_mcnemar_two_sided(0, n) if n > 0 else 1.0


def build_universe(key_rows, endpoint):
    """Return {review_id: True} for the rows this endpoint scores."""
    spec = ENDPOINT_SPECS[endpoint]
    wanted = "ABSENT" if spec["kind"] == "fp" else "PRESENT"
    stray = sorted({(row.get("arm") or (row.get("gold") or {}).get("arm")) for row in key_rows
                    if (row.get("gold") or {}).get("language") == "zh"
                    and str(row.get("arm") or "").startswith("hardneg")
                    and (row.get("arm") or "") not in ZH_KEYWORD_ARMS})
    if stray and endpoint in ERRATUM_D_SET:
        sys.exit("ERROR: zh_keyword_all_fp must cover ALL Chinese keyword arms, but "
                 f"{stray} are not declared in ZH_KEYWORD_ARMS. Declare them there first.")
    universe = {}
    for row in key_rows:
        gold = row.get("gold") or {}
        if gold.get("unfair_label") != wanted:
            continue
        if spec["lang"] is not None and gold.get("language") != spec["lang"]:
            continue
        if spec["arms"] is not None and (row.get("arm") or gold.get("arm")) not in spec["arms"]:
            continue
        universe[row["review_id"]] = True
    return universe


def indicator(endpoint, label):
    """1 = the bad outcome fired on this row; None = no usable model label."""
    if label is None:
        return None
    if ENDPOINT_SPECS[endpoint]["kind"] == "fp":
        return 1 if label == "PRESENT" else 0
    return 0 if label == "PRESENT" else 1


ENDPOINT_BLURB = {
    "hardneg_fp_strict": "hardneg rows with human ABSENT; fires when the model says PRESENT (false positive -- lower is better)",
    "fp_all_absent": "every row with human ABSENT; fires when the model says PRESENT (false positive -- lower is better)",
    "en_recall_miss": "English rows with human PRESENT; fires when the model does NOT say PRESENT (miss -- lower is better)",
    "ja_recall_miss": "Japanese rows with human PRESENT; fires when the model does NOT say PRESENT (miss -- lower is better)",
    "zh_recall_miss": "Chinese rows with human PRESENT; fires when the model does NOT say PRESENT (miss -- lower is better)",
    "zh_keyword_all_fp": "erratum-D view (1): ALL Chinese keyword-selected rows with human ABSENT; fires on model PRESENT",
    "zh_class1_fp": "erratum-D view (2): Chinese class1_anticheat rows with human ABSENT; fires on model PRESENT",
    "zh_class24_fp": "erratum-D view (3): Chinese class2-4 remainder with human ABSENT; fires on model PRESENT -- never report alone",
    "ja_hardneg_fp": "control: Japanese hardneg rows with human ABSENT; Japanese has no class1 family, so it cannot be split like zh",
}


def run_endpoint(endpoint, key_rows, key_path, pred_paths):
        universe = build_universe(key_rows, endpoint)
        if not universe:
            sys.exit(f"ERROR: endpoint {endpoint} selected zero rows from {key_path}.")

        print(f"answer key : {key_path} ({len(key_rows)} rows; sha256={sha256_file(key_path)})")
        print(f"endpoint   : {endpoint} -- {ENDPOINT_BLURB[endpoint]}")
        print(f"denominator: {len(universe)} rows")
        print()

        # Every condition must cover the same denominator, or the pairing is a lie.
        conditions = []
        for path in pred_paths:
            rows = read_jsonl(path)
            by_id = {r["review_id"]: r for r in rows}
            missing = [rid for rid in universe if rid not in by_id]
            if missing:
                sys.exit(f"ERROR: {path} is missing {len(missing)} of the {len(universe)} endpoint rows "
                         f"(first: {missing[0]}). The runs are not paired; refusing to test.")
            vals, unusable = {}, []
            for rid in universe:
                ind = indicator(endpoint, model_label(by_id[rid]))
                if ind is None:
                    unusable.append(rid)
                else:
                    vals[rid] = ind
            conditions.append({
                "path": path,
                "name": os.path.basename(os.path.dirname(os.path.abspath(path))),
                "vals": vals,
                "unusable": unusable,
            })
            fired = sum(vals.values())
            note = f"; {len(unusable)} row(s) had no usable model label and are dropped from the paired test" if unusable else ""
            print(f"  {conditions[-1]['name']:<44} fires {fired}/{len(vals)}{note}")
        print()

        for a, b_cond in itertools.combinations(conditions, 2):
            shared = sorted(set(a["vals"]) & set(b_cond["vals"]))
            dropped = len(universe) - len(shared)
            both = sum(1 for r in shared if a["vals"][r] and b_cond["vals"][r])
            only_a = sum(1 for r in shared if a["vals"][r] and not b_cond["vals"][r])
            only_b = sum(1 for r in shared if not a["vals"][r] and b_cond["vals"][r])
            neither = len(shared) - both - only_a - only_b
            n_disc = only_a + only_b
            p = exact_mcnemar_two_sided(only_a, only_b)

            print(f"=== {a['name']}  vs  {b_cond['name']} ===")
            if dropped:
                print(f"  paired on {len(shared)}/{len(universe)} rows ({dropped} dropped: no usable label in at least one run)")
            print(f"  both fire            : {both}")
            print(f"  only {a['name'][-24:]:<24}: b = {only_a}")
            print(f"  only {b_cond['name'][-24:]:<24}: c = {only_b}")
            print(f"  neither fires        : {neither}")
            print(f"  discordant b+c       : {n_disc}")
            print(f"  exact two-sided p    : {p:.4f}")
            print(f"  smallest p reachable at b+c={n_disc}: {min_attainable_p(n_disc):.4f}"
                  f"{'  <- cannot reach 0.05 at this discordant count' if min_attainable_p(n_disc) > 0.05 else ''}")
            if only_a > only_b:
                print(f"  direction            : fewer on {b_cond['name']} ({only_b} vs {only_a} discordant)")
            elif only_b > only_a:
                print(f"  direction            : fewer on {a['name']} ({only_a} vs {only_b} discordant)")
            else:
                print("  direction            : tied -- the paired data show no directional preference")
            print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred", action="append", required=True,
                    help="responses.jsonl to compare; pass two or more (all pairs are tested)")
    ap.add_argument("--answer-key", default=None,
                    help="answer_key.jsonl; defaults to the one beside the first --pred")
    ap.add_argument("--endpoint", default="hardneg_fp_strict", choices=tuple(ENDPOINTS) + ("all",),
                    help="binary per-row indicator to test (default: the protocol's primary endpoint)")
    args = ap.parse_args()

    if len(args.pred) < 2:
        sys.exit("ERROR: a paired test needs at least two --pred files.")

    key_path = args.answer_key or os.path.join(os.path.dirname(os.path.abspath(args.pred[0])), "answer_key.jsonl")
    if not os.path.exists(key_path):
        sys.exit(f"ERROR: answer key not found: {key_path}")
    key_rows = read_jsonl(key_path)

    # Erratum D is enforced structurally: asking for any one of the three Chinese
    # views runs all three plus the Japanese control, so no caller can report the
    # class2-4 remainder on its own the way the 2026-08-23 write-up did.
    if args.endpoint == "all":
        endpoints = list(ENDPOINTS)
    elif args.endpoint in ERRATUM_D_SET:
        endpoints = list(ERRATUM_D_SET)
        print("NOTE: erratum D -- the three Chinese views and the Japanese control are "
              "reported together; requesting one runs all four.\n")
    else:
        endpoints = [args.endpoint]

    ran = 0
    for endpoint in endpoints:
        if not build_universe(key_rows, endpoint):
            print(f"(skipped {endpoint}: this answer key has no rows for it)\n")
            continue
        run_endpoint(endpoint, key_rows, key_path, args.pred)
        ran += 1
    if not ran:
        sys.exit(f"ERROR: no requested endpoint selected any row from {key_path}.")

    print("Reminder: this is a development-stage comparison on purposive arms. A p value here")
    print("describes the paired discordance in this sample; it is not an ability estimate, and")
    print("the endpoint was chosen after seeing earlier results on these same rows.")


if __name__ == "__main__":
    main()
