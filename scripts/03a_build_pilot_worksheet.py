#!/usr/bin/env python3
"""03a_build_pilot_worksheet.py — assemble the pilot 试标 worksheet.

Joins the pilot_draft rows of split_manifest.csv (+ the 18 purposive
distributive top-up rows) to their raw review text and the metadata fields
the codebook's irony/§5-F step needs.  Author identity is dropped (steamid,
personaname, profile_url) per the repo's privacy red line.

Output lives under data/raw/ (gitignored) because it carries full review
text; only the derived label rows (no full text) are ever publishable.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SPLITS = ROOT / "data" / "splits"
OUT = RAW / "pilot_worksheet.jsonl"

KEEP_META = ("voted_up", "votes_up", "votes_funny", "received_for_free",
             "steam_purchase", "weighted_vote_score", "written_during_early_access")


def load_raw_index():
    """review_id(str) -> raw dict, across every data/raw/{appid}_{lang}.jsonl."""
    idx = {}
    for p in sorted(RAW.glob("*.jsonl")):
        if p.name == "pilot_worksheet.jsonl":
            continue
        with p.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                idx[str(d["recommendationid"])] = d
    return idx


def main():
    idx = load_raw_index()

    # pilot_draft rows from the manifest
    rows = []  # (review_id, appid, lang, provenance, curated_tag, reason)
    with (SPLITS / "split_manifest.csv").open() as f:
        for r in csv.DictReader(f):
            if r["role"] == "pilot_draft":
                rows.append((r["review_id"], r["appid"], r["lang"],
                             "random", "", ""))

    # purposive top-ups (already part of pilot_draft): distributive + procedural
    purposive = {}  # rid -> provenance label
    for fname, prov in (("pilot_draft_purposive_distributive.csv", "purposive_distributive"),
                        ("pilot_draft_purposive_procedural.csv", "purposive_procedural"),
                        ("pilot_draft_purposive_crosslingual.csv", "purposive_crosslingual")):
        fpath = SPLITS / fname
        if not fpath.exists():
            continue
        seen = {rid for rid, *_ in rows}
        with fpath.open() as f:
            for r in csv.DictReader(f):
                purposive[r["review_id"]] = prov
                if r["review_id"] not in seen:
                    rows.append((r["review_id"], r["appid"], r["lang"],
                                 prov, r["curated_tag"], r["reason"]))
    purposive_ids = purposive

    n_written, n_missing = 0, []
    with OUT.open("w") as out:
        for rid, appid, lang, prov, tag, reason in rows:
            d = idx.get(rid)
            if d is None:
                n_missing.append(rid)
                continue
            prov_tag = purposive_ids.get(rid, prov)
            rec = {
                "review_id": rid,
                "appid": appid,
                "lang": lang,
                "provenance": prov_tag,
                "curated_tag": tag,
                "curated_reason": reason,
                "review": d.get("review", ""),
            }
            for k in KEEP_META:
                rec[k] = d.get(k)
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_written += 1

    print(f"worksheet -> {OUT}")
    print(f"written: {n_written}  purposive: {len(purposive_ids)}  missing_from_raw: {len(n_missing)}")
    if n_missing:
        print("  missing ids:", ", ".join(n_missing[:20]))
    # per lang/appid tally
    from collections import Counter
    c = Counter((r[2], r[1]) for r in rows)
    for k in sorted(c):
        print(f"  {k[0]} / {k[1]}: {c[k]}")


if __name__ == "__main__":
    main()
