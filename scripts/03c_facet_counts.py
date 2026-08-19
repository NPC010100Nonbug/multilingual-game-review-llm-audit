#!/usr/bin/env python3
"""03c_facet_counts.py — tally the pilot 试标 on descriptive facet dimensions.

Counts subtype and procedural_facet across the three languages on
pilot_draft ONLY (that is all pilot_labels_claude.jsonl contains).  Facets are
counted on pilot, never gold (holdout firewall, codebook §9.2).

rev7 framing (codebook §4.2.1): the dimensions below are DESCRIPTIVE ONLY — they
report what the evidence looks like; they do NOT decide a facet's fate.  The
disposition is `taxonomy_status ∈ {core, exploratory, folded}`, a human call set
in the codebook (concept independence + rater stability), printed here so the
script and codebook never disagree (the old "FOLD/thin" verdict contradicted the
codebook's KEEP rulings — removed).

  (1) support_volume — aggregated over EN+ZH+JA, does it meet the dev-sample
      coverage floor (SUPPORT_THRESHOLD=15)?  This is DEV-SAMPLE COVERAGE, NOT
      natural frequency (pilot_draft is purposively topped-up); real frequency is
      reported only from random gold.
  (2) language_coverage — how many languages have >= PER_LANG_FLOOR (3)
      *independent* PRESENT instances (an EXISTENCE threshold, not measurement
      equivalence; aggregate >=15 does NOT prove per-language coverage).
  (+) title_coverage / game locus — coverage is confounded with game (Elden≈JA,
      BF≈ZH/EN in this design), so we also print the game spread.  A facet in >=2
      games can at most be "observed in two titles"; one in a single game is
      title-specific.  (Needs the local worksheet for appid; skipped if absent.)
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "data" / "pilot" / "pilot_labels_claude.jsonl"
WORKSHEET = ROOT / "data" / "raw" / "pilot_worksheet.jsonl"  # local only; for appid/game locus
SUPPORT_THRESHOLD = 15   # support_volume: dev-sample coverage floor (NOT natural frequency)
PER_LANG_FLOOR = 3       # language_coverage: per-language existence floor
APPID_GAME = {"730": "CS2", "1517290": "BF2042", "1245620": "Elden"}
FACETS = ["cheating_governance", "sanction", "access_exclusion",
          "competitive_balance", "unfair_by_design"]
# taxonomy_status is a HUMAN disposition set in codebook §4.2.1, NOT a threshold
# verdict — printed here so script output never contradicts the codebook.
TAXONOMY_STATUS = {
    "cheating_governance": "core",         # support 15, cross-lingual & cross-game
    "sanction": "core",                    # support 21, cross-lingual (BF-dominant)
    "unfair_by_design": "core",            # support 24, cross-lingual (Elden-only)
    "competitive_balance": "exploratory",  # support 9 (<floor), 3/3/3, BF-only
    "access_exclusion": "exploratory",     # support 11 (<floor), EN·ZH, JA under-attested
}


def load_appid():
    """review_id -> game name, from the local worksheet; {} if unavailable."""
    if not WORKSHEET.exists():
        return {}
    idx = {}
    with WORKSHEET.open() as f:
        for line in f:
            d = json.loads(line)
            idx[d["review_id"]] = APPID_GAME.get(str(d.get("appid")), str(d.get("appid")))
    return idx


def main():
    rows = [json.loads(l) for l in LAB.open()]
    present = [r for r in rows if r["unfair_label"] == "PRESENT"]

    print(f"pilot rows: {len(rows)}   PRESENT: {len(present)}\n")

    # main-label distribution
    lab_by_lang = defaultdict(Counter)
    for r in rows:
        lab_by_lang[r["language"]][r["unfair_label"]] += 1
    print("main label × language")
    print(f"  {'lang':4} {'PRESENT':>8} {'ABSENT':>7} {'NA':>4} {'total':>6}")
    for lang in ("en", "zh", "ja"):
        c = lab_by_lang[lang]
        tot = sum(c.values())
        print(f"  {lang:4} {c['PRESENT']:>8} {c['ABSENT']:>7} {c['NA']:>4} {tot:>6}")
    print()

    # subtype × language (PRESENT only; multi-select so counts can exceed PRESENT)
    sub_lang = defaultdict(Counter)
    for r in present:
        for s in r["subtype"]:
            sub_lang[s][r["language"]] += 1
    print("subtype × language (PRESENT, multi-select)")
    print(f"  {'subtype':14} {'en':>3} {'zh':>3} {'ja':>3} {'ALL':>4}")
    for s in ("distributive", "procedural"):  # rev5: `other` removed from domain
        c = sub_lang[s]
        allc = c["en"] + c["zh"] + c["ja"]
        print(f"  {s:14} {c['en']:>3} {c['zh']:>3} {c['ja']:>3} {allc:>4}")
    print()

    # facet × language  (+ game locus)
    appid = load_appid()
    fac_lang = defaultdict(Counter)
    fac_game = defaultdict(Counter)
    fac_border = Counter()
    for r in present:
        for f in r["procedural_facet"]:
            fac_lang[f][r["language"]] += 1
            if appid.get(r["review_id"]):
                fac_game[f][appid[r["review_id"]]] += 1
            if r["borderline"]:
                fac_border[f] += 1

    # dim (1): support_volume  (dev-sample coverage; NOT natural frequency)
    print(f"support_volume — dev-sample coverage floor = {SUPPORT_THRESHOLD} "
          f"(NOT natural frequency; random gold reports frequency)")
    print(f"  {'facet':22} {'en':>3} {'zh':>3} {'ja':>3} {'ALL':>4} {'(bl)':>5}  {'meets_floor':>11}  taxonomy_status")
    for f in FACETS:
        c = fac_lang[f]
        allc = c["en"] + c["zh"] + c["ja"]
        meets = "yes" if allc >= SUPPORT_THRESHOLD else "no"
        status = TAXONOMY_STATUS.get(f, "?")
        print(f"  {f:22} {c['en']:>3} {c['zh']:>3} {c['ja']:>3} {allc:>4} {fac_border[f]:>5}  {meets:>11}  {status}")
    print()

    # dim (2): language_coverage  (per-language >= PER_LANG_FLOOR) + title_coverage/game locus
    print(f"language_coverage — EXISTENCE floor >= {PER_LANG_FLOOR} in EACH language "
          f"(not measurement equivalence; aggregate does NOT count)")
    print(f"  {'facet':22} langs>=floor        games        coverage")
    for f in FACETS:
        c = fac_lang[f]
        ok = [lg for lg in ("en", "zh", "ja") if c[lg] >= PER_LANG_FLOOR]
        games = fac_game.get(f, {})
        game_str = ",".join(f"{g}:{n}" for g, n in sorted(games.items(), key=lambda x: -x[1])) or "n/a"
        n_lang, n_game = len(ok), len(games)
        if n_lang == 3:
            claim = "3langs-attested" + (" & 2+ games" if n_game >= 2 else " (single-game→title-specific)")
        elif n_lang == 2:
            claim = f"bilingual ({'+'.join(ok)})"
        elif n_lang == 1:
            claim = f"single-lang ({ok[0]})"
        else:
            claim = "sub-floor in all"
        print(f"  {f:22} {'+'.join(ok) or '-':18} {game_str:12} {claim}")
    print()

    # borderline / confidence health
    bl = sum(1 for r in rows if r["borderline"])
    print(f"borderline rows: {bl}  ({bl/len(rows)*100:.0f}%)")
    conf = Counter(r["confidence"] for r in present)
    print("PRESENT confidence:", dict(conf))

    # FLAG notes surfaced during labeling
    flags = [r for r in rows if "FLAG" in (r.get("annotator_note") or "")]
    print(f"\nFLAGGED for Yifan ({len(flags)}):")
    for r in flags:
        print(f"  [{r['language']}/{r['review_id']}] {r['unfair_label']}: {r['annotator_note'][:100]}")


if __name__ == "__main__":
    main()
