"""
02a3_purposive_distributive.py — append a PURPOSIVE (keyword-seeded, human-curated)
top-up of `distributive` examples to pilot_draft, in all three languages.

Why purposive, not random: the two earlier random pilot_draft batches (270 rows)
yielded almost no `distributive` signal in Chinese and none of it in a balanced
way across languages, because the construct is sparse and the games differ
(CS2 = cosmetic skins, Elden = single-player). Random sampling a sparse
construct is inefficient. pilot_draft is NOT used for measurement, so purposive
oversampling of likely-PRESENT reviews is methodologically legitimate for
codebook drafting — it MUST be disclosed as non-random in the codebook.

Firewall unchanged: gold/dev/train are carved LATER from the aligned pool with
their own 后减前, so these ids are simply unavailable to them. These reviews were
found by a keyword scan over data/raw MINUS the manifest, then read and curated
by hand; the curated ids are hard-coded HERE (the curation is human judgement,
so the id list *is* the reproducible artifact).

Provenance is written to data/splits/pilot_draft_purposive_distributive.csv so it
stays machine-readable which pilot_draft rows are purposive vs random.
"""
import csv
import os
from importlib import import_module

_p = import_module("02a_make_pilot")
load_manifest = _p.load_manifest
write_manifest = _p.write_manifest
SPLITS_DIR = os.path.dirname(_p.MANIFEST)

# (appid, lang, review_id, curated_tag, one-line reason)
CURATED = [
    ("1517290", "en", "138975097", "distributive",        "HAVE TO BUY THE ELITE for basic content (pay-to-unlock)"),
    ("1517290", "en", "207539435", "distributive",        "weapons/vehicles locked behind Elite edition + premium currency"),
    ("1517290", "en", "141902653", "distributive",        "everything locked behind a paywall"),
    ("1517290", "en", "148928031", "distributive",        "pay-to-win store framing"),
    ("1517290", "en", "140004357", "distributive_border", "$120 Ultimate edition but must still buy Premium battle pass"),
    ("1517290", "en", "164972778", "hard_negative",       "battle pass is cosmetic, no gameplay impact (cosmetic != advantage)"),
    ("1517290", "zh", "202517276", "distributive",        "elite edition unlocks only 10 guns; store blurb of 35 is misleading"),
    ("1517290", "zh", "165149867", "distributive",        "guns locked behind battle-pass level"),
    ("1517290", "zh", "202254837", "distributive",        "buy elite edition to skip grinding for guns (pay-to-skip-grind)"),
    ("730",     "zh", "225992615", "distributive_claim",  "accusation: don't pay -> dealt bad hands every match"),
    ("730",     "zh", "227223824", "hard_negative",       "no pay-to-win crush, skill wins (fairness norm stated positively)"),
    ("730",     "zh", "229241969", "hard_negative",       "no forced spending breaks match balance"),
    ("1245620", "ja", "111128390", "distributive",        "Japanese pay the world's highest price (regional pricing)"),
    ("1245620", "ja", "111096605", "distributive",        "Namco おま国 exploitation, 9240 yen highest of all regions"),
    ("1245620", "ja", "121372217", "distributive",        "region-locked and domestic-only price very high"),
    ("1245620", "ja", "111214517", "distributive",        "おま値: forced to pay $20+ more than other countries"),
    ("1245620", "ja", "113317778", "distributive",        "Japan-only high price"),
    ("1245620", "ja", "115896598", "distributive",        "no explanation for domestic price premium vs overseas"),
]

PROV = os.path.join(SPLITS_DIR, "pilot_draft_purposive_distributive.csv")


def main():
    rows = load_manifest()
    assigned = {r["review_id"] for r in rows} | _p.load_reserved_ids()

    new_rows, prov_rows, skipped = [], [], []
    for appid, lang, rid, tag, reason in CURATED:
        if rid in assigned:
            skipped.append(rid)
            continue
        new_rows.append({"review_id": rid, "appid": appid, "lang": lang, "role": "pilot_draft"})
        prov_rows.append({"review_id": rid, "appid": appid, "lang": lang,
                          "curated_tag": tag, "reason": reason})
        assigned.add(rid)

    if not new_rows:
        print(f"nothing to add (all {len(CURATED)} already in manifest).")
        return

    write_manifest(rows + new_rows)
    with open(PROV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["review_id", "appid", "lang", "curated_tag", "reason"])
        w.writeheader()
        w.writerows(prov_rows)

    print(f"Appended {len(new_rows)} purposive pilot_draft rows -> {_p.MANIFEST}")
    print(f"Provenance -> {PROV}")
    if skipped:
        print(f"skipped (already assigned): {skipped}")
    from collections import Counter
    print("by lang:", dict(Counter(r["lang"] for r in new_rows)))
    print("by tag :", dict(Counter(p["curated_tag"] for p in prov_rows)))


if __name__ == "__main__":
    main()
