#!/usr/bin/env python3
"""03f_extract_arm_labels.py — extract Yifan's HUMAN answer-key labels from the
three prompt-tuning annotation workbooks into tracked, publishable jsonl.

Why this exists: the human labels for the prompt-tuning set lived ONLY in local
gitignored xlsx (data/raw/*_annotation_workbook.xlsx). A week of annotation was
therefore invisible to git and would vanish on any clone/handoff. This script
turns them into id+label+facet+rationale jsonl (NO full review text), mirroring
the publishable schema of 03b_pilot_labels.py so the answer key is versioned.

Three sources (the whole prompt-tuning set = 135 + 32 + 80 = 247):
  - pilot_prompt (135): the random base. 98 ABSENT / 8 PRESENT / 29 NA. Its 8
    positives are ALL non-English -> this is the "English-blindness" hole that
    motivated the two arms below.
  - diagnostic arm (32): purposive EN positives + hard negatives. 23 PRESENT /
    9 ABSENT. Fills the EN-positive void for prompt tuning.
  - hardneg arm (80): fresh EN keyword-retrieved hard negatives. 71 ABSENT /
    9 PRESENT (unexpected true positives, kept). keyword_class joined from
    data/splits/pilot_prompt_extension_manifest.csv.

These are the HUMAN answer key for PROMPT TUNING only. They are NOT gold
measurement data and are NEVER trained on. The gold set is carved separately
with its own 后减前 firewall and these ids are reserved out of it.

Outputs (data/pilot/):
  pilot_prompt_labels_human.jsonl
  diagnostic_arm_labels_human.jsonl
  hardneg_arm_labels_human.jsonl
"""
import csv
import json
from collections import Counter
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "pilot"
EXT_MANIFEST = ROOT / "data" / "splits" / "pilot_prompt_extension_manifest.csv"
CODEBOOK_VERSION = "v1.0"
ANNOTATOR = "human (Yifan)"

FACET_COLS = {
    "facet_cheating_governance": "cheating_governance",
    "facet_sanction": "sanction",
    "facet_access_exclusion": "access_exclusion",
    "facet_competitive_balance": "competitive_balance",
    "facet_unfair_by_design": "unfair_by_design",
}

# "52" is a blank-cell sentinel Yifan used in the pilot_prompt workbook to mark
# unfilled annotation cells (facets/subtype/evidence/notes) on ABSENT/NA rows.
# It is NOT data -> treat as empty everywhere. The real facet marker is "yes".
SENTINELS = {"52"}

SOURCES = [
    ("pilot_prompt", "pilot_prompt_annotation_workbook.xlsx", "pilot_prompt_labels_human.jsonl"),
    ("diagnostic",   "diagnostic_arm_annotation_workbook.xlsx", "diagnostic_arm_labels_human.jsonl"),
    ("hardneg",      "hardneg_annotation_workbook.xlsx",        "hardneg_arm_labels_human.jsonl"),
]


def truthy_bool(v):
    """For genuine boolean cells (out_of_scope, borderline)."""
    if v is None:
        return False
    return str(v).strip().lower() not in ("", "false", "0", "no", "none")


def facet_on(v):
    """A facet is assigned only when the cell is the affirmative marker 'yes'."""
    return v is not None and str(v).strip().lower() == "yes"


def clean(v):
    """Text-field value with the '52' blank-sentinel mapped to empty string."""
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s in SENTINELS else s


def load_keyword_class():
    idx = {}
    if EXT_MANIFEST.exists():
        with EXT_MANIFEST.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                idx[str(r["review_id"])] = r.get("keyword_class")
    return idx


def extract(fn, arm, kw_idx):
    wb = openpyxl.load_workbook(RAW / fn, read_only=True, data_only=True)
    ws = wb["Annotation"]
    all_rows = list(ws.iter_rows(values_only=True))
    wb.close()
    header = all_rows[3]
    h = {name: i for i, name in enumerate(header) if name}

    def cell(row, name):
        v = row[h[name]] if name in h else None
        return v

    out = []
    for row in all_rows[4:]:
        if not row or row[h["review_id"]] in (None, ""):
            continue
        rid = str(cell(row, "review_id"))
        subtype_raw = clean(cell(row, "subtype"))
        facets = [tag for col, tag in FACET_COLS.items() if facet_on(cell(row, col))]
        # SECURITY: evidence_span in the arm workbooks can hold the FULL review
        # text (seen up to 1214 chars). Publishing that breaks the "no full
        # review text, only labels/ids" rule, so it is NOT written here — only a
        # boolean that an evidence span exists. The verbatim span stays in the
        # local gitignored xlsx, which is where prompt tuning is actually done.
        rec = {
            "review_id": rid,
            "language": cell(row, "lang"),
            "unfair_label": cell(row, "unfair_label"),
            "out_of_scope": truthy_bool(cell(row, "out_of_scope")),
            "has_evidence_span": bool(clean(cell(row, "evidence_span"))),
            "normalized_claim": clean(cell(row, "normalized_claim")),
            "subtype": [s.strip() for s in subtype_raw.split(",") if s.strip()],
            "procedural_facet": facets,
            "explicitness": clean(cell(row, "explicitness")) or None,
            "confidence": clean(cell(row, "confidence")) or None,
            "borderline": truthy_bool(cell(row, "borderline")),
            "uncertainty_reason": clean(cell(row, "uncertainty_reason")),
            "annotator_note": clean(cell(row, "annotator_note")),
            "arm": arm,
            "keyword_class": kw_idx.get(rid) if arm == "hardneg" else None,
            "codebook_version": CODEBOOK_VERSION,
            "annotator": ANNOTATOR,
        }
        out.append(rec)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    kw_idx = load_keyword_class()
    grand = 0
    for arm, fn, outname in SOURCES:
        rows = extract(fn, arm, kw_idx)
        ids = [r["review_id"] for r in rows]
        assert len(ids) == len(set(ids)), f"duplicate review_id in {arm}"
        outp = OUT_DIR / outname
        with outp.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        labs = Counter(r["unfair_label"] for r in rows)
        grand += len(rows)
        print(f"{arm:12s} n={len(rows):4d} -> {outp.relative_to(ROOT)}  labels={dict(labs)}")
    print(f"total answer-key rows: {grand}")


if __name__ == "__main__":
    main()
