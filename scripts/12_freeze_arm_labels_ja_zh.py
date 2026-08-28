#!/usr/bin/env python3
"""12_freeze_arm_labels_ja_zh.py — FREEZE the 301 zh/ja human answer-key labels.

Why this exists: after 07c built the two merged blind workbooks, Yifan annotated
all 301 rows (zh 157 + ja 144) on 2026-08-27. Those labels existed ONLY inside
editable, gitignored .xlsx. The project rule is 「标注在看到模型结果之前冻结,
之后不改」 — so they must be exported to immutable id+label jsonl WITH a sha256
BEFORE any DeepSeek output for these rows exists. Otherwise the 301 rows lose
their evidentiary standing permanently (nobody can prove the labels predate the
model's answers).

This mirrors scripts/03f_extract_arm_labels.py (the EN-side equivalent, 247 rows)
in schema and in its security rule: NO full review text is written out, only a
boolean that an evidence span exists. Full text stays in the gitignored xlsx.

ARM ASSIGNMENT — registered decision (2026-08-27, Yifan):
  zh `hardneg` rows whose keyword_class == class1_anticheat are emitted as a
  SEPARATE arm `hardneg_class1_zh`, not merged into `hardneg`. Reason: human
  labels came back 18/28 = 64% PRESENT, i.e. that class is a high-precision
  POSITIVE retriever, not a hard negative. Leaving it inside `hardneg` would
  (a) inflate the zh hard-negative PRESENT base rate to 21% vs ja 7%, making any
  raw cross-language FP comparison a base-rate artifact, and (b) put true
  positives in the false-positive denominator — the exact class of error already
  logged three times in decision_log. This split is registered BEFORE the model
  is run on these rows, so it is a design decision, not p-hacking.

Outputs (data/pilot/):
  merged_arm_zh_labels_human.jsonl      157 rows
  merged_arm_ja_labels_human.jsonl      144 rows
  merged_arm_ja_zh_labels_human.sha256  checksums of both (the freeze receipt)
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "pilot"
CODEBOOK_VERSION = "v1.0"
ANNOTATOR = "human (Yifan)"
FREEZE_DATE = "2026-08-27"

SOURCES = [
    ("zh", "annotation_workbook_zh.xlsx", "merged_arm_zh_labels_human.jsonl", 157),
    ("ja", "annotation_workbook_ja.xlsx", "merged_arm_ja_labels_human.jsonl", 144),
]

FACET_COLS = {
    "facet_cheating_governance": "cheating_governance",
    "facet_sanction": "sanction",
    "facet_access_exclusion": "access_exclusion",
    "facet_competitive_balance": "competitive_balance",
    "facet_unfair_by_design": "unfair_by_design",
}

# The four columns that MUST be filled for a row to count as annotated.
REQUIRED = ["out_of_scope", "unfair_label", "confidence", "borderline"]

# Registered 2026-08-27: zh class1 leaves the hardneg arm.
SPLIT_ARM = {("zh", "hardneg", "class1_anticheat"): "hardneg_class1_zh"}


def truthy_bool(v):
    if v is None:
        return False
    return str(v).strip().lower() not in ("", "false", "0", "no", "none")


def facet_on(v):
    return v is not None and str(v).strip().lower() == "yes"


def clean(v):
    return "" if v is None else str(v).strip()


def read_sheet(wb, name, header_row):
    """Return (header_index_map, data_rows). header_row is 0-based."""
    rows = list(wb[name].iter_rows(values_only=True))
    hdr = rows[header_row]
    return {n: i for i, n in enumerate(hdr) if n}, rows[header_row + 1:]


def extract(lang, fn):
    wb = openpyxl.load_workbook(RAW / fn, read_only=True, data_only=True)
    # Annotation: title/subtitle/blank/header -> header on row 4 (0-based 3).
    ah, arows = read_sheet(wb, "Annotation", 3)
    # Key (SEALED): warning banner/blank/header -> header on row 3 (0-based 2).
    kh, krows = read_sheet(wb, "Key (SEALED)", 2)
    wb.close()

    key = {}
    for r in krows:
        if not r or r[kh["review_id"]] in (None, ""):
            continue
        key[str(r[kh["review_id"]])] = (
            clean(r[kh["arm"]]),
            clean(r[kh["keyword_class"]]) or None,
            clean(r[kh["prior_label_untrusted"]]) or None,
        )

    out, unfilled = [], []
    for row in arows:
        if not row or row[ah["review_id"]] in (None, ""):
            continue
        rid = str(row[ah["review_id"]])

        def c(name):
            return row[ah[name]] if name in ah else None

        missing = [k for k in REQUIRED if c(k) is None or str(c(k)).strip() == ""]
        # out_of_scope / borderline are real booleans: False is filled, not blank.
        missing = [k for k in missing if not isinstance(c(k), bool)]
        if missing:
            unfilled.append((rid, missing))

        arm, kw, prior = key.get(rid, ("UNKNOWN", None, None))
        arm = SPLIT_ARM.get((lang, arm, kw), arm)

        subtype_raw = clean(c("subtype"))
        out.append({
            "review_id": rid,
            "language": c("lang") or lang,
            "unfair_label": clean(c("unfair_label")) or None,
            "out_of_scope": truthy_bool(c("out_of_scope")),
            # SECURITY: evidence_span can hold the full review text. Only a
            # boolean leaves this script; the verbatim span stays in the xlsx.
            "has_evidence_span": bool(clean(c("evidence_span"))),
            "normalized_claim": clean(c("normalized_claim")),
            "subtype": [s.strip() for s in subtype_raw.replace(";", ",").split(",") if s.strip()],
            "procedural_facet": [t for col, t in FACET_COLS.items() if facet_on(c(col))],
            "explicitness": clean(c("explicitness")) or None,
            "confidence": clean(c("confidence")) or None,
            "borderline": truthy_bool(c("borderline")),
            "uncertainty_reason": clean(c("uncertainty_reason")),
            "annotator_note": clean(c("annotator_note")),
            "arm": arm,
            "keyword_class": kw,
            # Claude v1-draft-rev6's old label, kept for the agreement analysis.
            # NEVER an input to anything: it is the thing being audited.
            "prior_label_untrusted": prior,
            "codebook_version": CODEBOOK_VERSION,
            "annotator": ANNOTATOR,
            "frozen_on": FREEZE_DATE,
        })
    return out, unfilled


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    receipt, total, failed = [], 0, False

    for lang, fn, outname, expect_n in SOURCES:
        rows, unfilled = extract(lang, fn)

        # --- refuse to freeze anything incomplete or ambiguous ---
        if len(rows) != expect_n:
            print(f"ABORT {lang}: got {len(rows)} rows, expected {expect_n}")
            failed = True
        ids = [r["review_id"] for r in rows]
        if len(ids) != len(set(ids)):
            print(f"ABORT {lang}: duplicate review_id")
            failed = True
        if unfilled:
            print(f"ABORT {lang}: {len(unfilled)} unannotated rows, e.g. {unfilled[:3]}")
            failed = True
        unknown = [r["review_id"] for r in rows if r["arm"] == "UNKNOWN"]
        if unknown:
            print(f"ABORT {lang}: {len(unknown)} rows absent from Key (SEALED)")
            failed = True
        if failed:
            continue

        outp = OUT_DIR / outname
        with outp.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        digest = hashlib.sha256(outp.read_bytes()).hexdigest()
        receipt.append((outname, len(rows), digest))
        total += len(rows)

        by_arm = defaultdict(Counter)
        for r in rows:
            by_arm[r["arm"]][r["unfair_label"]] += 1
        print(f"\n{lang}  n={len(rows)}  -> {outp.relative_to(ROOT)}")
        print(f"     sha256 {digest}")
        for arm in sorted(by_arm):
            c = by_arm[arm]
            n = sum(c.values())
            pres = c.get("PRESENT", 0)
            print(f"     {arm:20s} n={n:4d}  PRESENT {pres:3d} ({pres/n:5.1%})  {dict(c)}")

    if failed:
        print("\nNOTHING FROZEN — fix the workbook and re-run.")
        sys.exit(1)

    rec = OUT_DIR / "merged_arm_ja_zh_labels_human.sha256"
    with rec.open("w", encoding="utf-8") as f:
        f.write(f"# frozen {FREEZE_DATE} by {ANNOTATOR}; codebook {CODEBOOK_VERSION}\n")
        f.write("# 301 zh/ja prompt-tuning answer-key rows. Frozen BEFORE any\n")
        f.write("# DeepSeek run on these ids. Do not edit after this point.\n")
        for name, n, digest in receipt:
            f.write(f"{digest}  {name}  # n={n}\n")
    print(f"\ntotal frozen: {total} rows -> {rec.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
