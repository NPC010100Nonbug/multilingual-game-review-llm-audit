#!/usr/bin/env python3
"""03e_build_anchor_catalog.py — assemble the standalone anchor_catalog (rev7 + freeze-prep).

Codebook §4.2.1 lists each facet's anchor examples as ID pointers only.  The
external review (round 3) asked for the full 三件套 per anchor — complete
original text + minimal evidence_span (with the norm cue) + normalized_claim —
plus a per-example ruling, kept OUT of the codebook body so it doesn't bloat.

Freeze-prep extension (codebook §9.3 row "anchor+字段完整"): each facet must carry
not only POSITIVE anchors but also a HARD NEGATIVE (looks-PRESENT, ruled ABSENT —
teaches the exclusion boundary) and a BORDERLINE (genuinely on the edge).  The
hard-neg / borderline ids are drawn ONLY from rows Claude already labelled AND
Yifan already adjudicated (their rulings live in annotator_note), so no new
labelling is invented here — the human ruling is the authority; this script just
assembles them.  Cells the current pilot has no clean adjudicated candidate for
are recorded as GAPS for Yifan to fill or waive (printed at the end).

This script is the reproducible artifact: it joins the hard-coded anchor list
(mirroring the codebook §4.2.1 anchor block) to
  - the local worksheet  (data/raw/pilot_worksheet.jsonl)  -> full text + metadata
  - the pilot labels      (data/pilot/pilot_labels_claude.jsonl) -> span/claim/ruling
and emits THREE files:
  - data/raw/anchor_catalog.jsonl   (WITH full text; gitignored, local only)
  - data/pilot/anchor_catalog.jsonl (span/claim/facet/ruling ONLY, no raw text;
                                     publishable, same privacy rule as the labels)
  - freeze/anchor_review_sheet.md   (human-readable, for Yifan to ratify keep/cut)

Anchors that violate their role's expectation (a positive that isn't PRESENT, a
hard-neg that isn't ABSENT, a borderline whose borderline flag is false) are
reported as data-quality warnings.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKSHEET = ROOT / "data" / "raw" / "pilot_worksheet.jsonl"          # local, full text
LABELS = ROOT / "data" / "pilot" / "pilot_labels_claude.jsonl"       # publishable
OUT_FULL = ROOT / "data" / "raw" / "anchor_catalog.jsonl"            # gitignored
OUT_PUB = ROOT / "data" / "pilot" / "anchor_catalog.jsonl"          # publishable
OUT_SHEET = ROOT / "freeze" / "anchor_review_sheet.md"              # human review

# facet -> {role -> [review_id, ...]}  (mirrors codebook §4.2.1; keep in sync).
# positive = clear PRESENT for the facet; hard_negative = looks-PRESENT but ruled
# ABSENT (exclusion boundary); borderline = genuinely on the edge (borderline=true).
# hard_neg / borderline ids are all Yifan-adjudicated rows (rulings in annotator_note).
# rev7 freeze-prep (2026-08-10, Yifan-adjudicated): 2 borderline-ABSENT rows promoted
# to PRESENT positives (228759578, 226675676); 228424527 flipped to PRESENT but kept as
# a BORDERLINE anchor (Yifan final call — genuinely on the edge, not a clean positive);
# 153192679 kept as hard_neg (pure prevalence, no (B) attribution); backfills drawn from
# already-adjudicated rows.
ANCHORS = {
    "cheating_governance": {
        "positive": ["232062443", "229414199", "160753326", "222115139", "228759578"],
        "hard_negative": ["153192679"],   # ZH: pure prevalence, no authority attribution -> ABSENT
        "borderline": ["103037208"],      # EN "Kernel-level anticheat malware": intrusion/privacy edge
    },
    "sanction": {
        "positive": ["200120577", "156768786", "217797587", "194187711", "226675676"],
        "hard_negative": [],              # WAIVED: no clean ABSENT ban-topical row in pilot
                                          # (sanction-topical rows nearly all ruled PRESENT)
        "borderline": ["226232348"],      # ZH: player toxicity §5-E, no official-tolerance -> edge
    },
    "access_exclusion": {
        "positive": ["114083525", "202460812", "201569269"],
        "hard_negative": ["162971869"],   # ZH: states secure-boot requirement, no norm cue §5-C -> ABSENT
        "borderline": ["175291341", "228424527"],  # 228424527: Yifan 定 borderline(非满配正例);"我不是程序员"排除语气 PRESENT-borderline,与 162971869 无语气 ABSENT 成锐对
    },
    "competitive_balance": {
        "positive": ["225680958", "150436907", "162341785"],
        "hard_negative": ["164972778"],   # EN: paywall present but cosmetic-only, no P2W edge -> ABSENT
        "borderline": ["150172993"],      # ZH: competitive_balance candidate, PRESENT-borderline
    },
    "unfair_by_design": {
        "positive": ["111593981", "156643716", "221548261", "230587480"],
        "hard_negative": ["110932128"],   # JA: names 理不尽 but terse positive -> topic≠construct ABSENT
        "borderline": ["165149867"],      # ZH: battlepass-unlock grind = monetization/distributive edge, not design-unfair -> ABSENT-borderline
    },
}

# per-role expectation used to sanity-check the rulings
ROLE_EXPECT = {
    "positive": ("PRESENT", True),        # (expected unfair_label, must be facet-consistent)
    "hard_negative": ("ABSENT", False),
    "borderline": (None, False),          # any label, but borderline flag must be true
}

# label fields carried into the PUBLISHABLE catalog (no raw text)
PUB_FIELDS = ("language", "unfair_label", "subtype", "procedural_facet",
              "evidence_span", "normalized_claim", "explicitness", "confidence",
              "borderline", "uncertainty_reason", "adjudicated_label",
              "adjudication_reason", "annotator_note")
# extra metadata (non-identity) carried ONLY into the full-text local catalog
META_FIELDS = ("voted_up", "votes_funny", "votes_up", "received_for_free",
               "steam_purchase", "weighted_vote_score", "written_during_early_access")


def load_jsonl_index(path, key="review_id"):
    idx = {}
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            idx[str(d[key])] = d
    return idx


def main():
    labels = load_jsonl_index(LABELS)
    work = load_jsonl_index(WORKSHEET) if WORKSHEET.exists() else {}
    if not work:
        print(f"WARN: {WORKSHEET} not found — full-text catalog will be skipped.")

    pub_rows, full_rows, warnings, gaps = [], [], [], []
    sheet_by_facet = {}
    for facet, by_role in ANCHORS.items():
        sheet_by_facet[facet] = {"positive": [], "hard_negative": [], "borderline": []}
        for role in ("positive", "hard_negative", "borderline"):
            ids = by_role.get(role, [])
            if not ids:
                gaps.append(f"{facet}/{role}: no anchor (pilot has no clean adjudicated candidate)")
                continue
            exp_label, must_match_facet = ROLE_EXPECT[role]
            for rid in ids:
                lab = labels.get(rid)
                if lab is None:
                    warnings.append(f"{facet}/{role}/{rid}: NOT in labels")
                    continue
                got = lab.get("unfair_label")
                if exp_label is not None and got != exp_label:
                    warnings.append(f"{facet}/{role}/{rid}: label={got} (expected {exp_label})")
                if role == "borderline" and not lab.get("borderline"):
                    warnings.append(f"{facet}/{role}/{rid}: borderline flag is false")
                if must_match_facet and facet not in (lab.get("procedural_facet") or []):
                    warnings.append(f"{facet}/{role}/{rid}: labelled facet={lab.get('procedural_facet')}")

                base = {"review_id": rid, "catalog_facet": facet, "role": role}
                base.update({k: lab.get(k) for k in PUB_FIELDS})
                pub_rows.append(base)
                sheet_by_facet[facet][role].append((rid, lab, work.get(rid)))

                w = work.get(rid)
                if w is not None:
                    full = dict(base)
                    full["appid"] = w.get("appid")
                    full["provenance"] = w.get("provenance")
                    full["review"] = w.get("review", "")
                    full.update({k: w.get(k) for k in META_FIELDS})
                    full_rows.append(full)
                elif work:
                    warnings.append(f"{facet}/{role}/{rid}: NOT in worksheet (no full text)")

    with OUT_PUB.open("w") as f:
        for r in pub_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"publishable anchor_catalog -> {OUT_PUB}  ({len(pub_rows)} anchors, no raw text)")

    if full_rows:
        with OUT_FULL.open("w") as f:
            for r in full_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"full-text anchor_catalog -> {OUT_FULL}  ({len(full_rows)} anchors, LOCAL/gitignored)")

    # human review sheet (uses full text if available, else the publishable span/claim)
    OUT_SHEET.parent.mkdir(exist_ok=True)
    with OUT_SHEET.open("w") as f:
        f.write("# anchor_catalog 审阅表(冻结前请逐条裁定 ✅留 / ✏️改理由 / ❌换)\n\n")
        f.write("> 由 `scripts/03e_build_anchor_catalog.py` 生成。hard_negative / borderline 均取自"
                "你已裁定过的行(理由即 annotator_note)。**这是冻结 codebook 的前置——请本人过一遍。**\n\n")
        role_zh = {"positive": "正例", "hard_negative": "hard negative(像却不算)",
                   "borderline": "borderline(卡边)"}
        for facet, roles in sheet_by_facet.items():
            f.write(f"## {facet}\n\n")
            for role in ("positive", "hard_negative", "borderline"):
                items = roles[role]
                f.write(f"### {role_zh[role]}\n\n")
                if not items:
                    f.write("- ⚠️ **缺**:pilot 里没有干净的已裁定候选。请人工指定一条,或接受本 facet 无此角色。\n\n")
                    continue
                for rid, lab, w in items:
                    txt = (w or {}).get("review", "") if w else ""
                    txt = (txt[:220] + "…") if len(txt) > 220 else txt
                    f.write(f"- **[{lab.get('language')}/{rid}] {lab.get('unfair_label')}**"
                            f"{' ·facet=' + ','.join(lab.get('procedural_facet') or []) if lab.get('procedural_facet') else ''}\n")
                    if txt:
                        f.write(f"  - 原文:{txt}\n")
                    if lab.get("evidence_span"):
                        f.write(f"  - span:{lab.get('evidence_span')}\n")
                    if lab.get("normalized_claim"):
                        f.write(f"  - claim:{lab.get('normalized_claim')}\n")
                    f.write(f"  - 裁定理由:{lab.get('annotator_note') or '(无)'}\n")
                    f.write("  - [ ] ✅留  [ ] ✏️改  [ ] ❌换\n\n")
    print(f"human review sheet -> {OUT_SHEET}")

    if warnings:
        print(f"\nDATA-QUALITY WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    if gaps:
        print(f"\nCOVERAGE GAPS ({len(gaps)}) — Yifan to fill a candidate or waive the role:")
        for g in gaps:
            print(f"  - {g}")
    if not warnings and not gaps:
        print("\nall anchors present, role-consistent, and complete.")


if __name__ == "__main__":
    main()
