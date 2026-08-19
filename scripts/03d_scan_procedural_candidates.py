#!/usr/bin/env python3
"""03d_scan_procedural_candidates.py — surface purposive top-up candidates.

For each thin procedural facet, keyword-scan data/raw MINUS the manifest (so we
never touch anything already assigned, and the future gold draw's 后减前 keeps
these out of gold) and print candidate reviews with enough text to curate by
hand.  Keyword hits are ONLY a net — every candidate must still be read and
pass the §4.0 positive-example gate before being curated in (不能猜).

Usage: python3 scripts/03d_scan_procedural_candidates.py <facet> [lang]
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "splits" / "split_manifest.csv"

SEEDS = {
    "cheating_governance": [
        r"cheat", r"hacker", r"aimbot", r"wall ?hack", r"anti-?cheat", r"vac\b",
        r"外挂", r"作弊", r"挂", r"反作弊", r"放置", r"官匹",
        r"チート", r"チーター", r"ハッカー", r"不正",
    ],
    "sanction": [
        r"\bban\b", r"banned", r"\bkick", r"appeal", r"suspend",
        r"封号", r"封禁", r"误封", r"申诉", r"踢", r"红信", r"红信",
        r"垢ban", r"アカ.?ban", r"処罰", r"キック", r"バン\b", r"理由もなく",
    ],
    "access_exclusion": [
        r"secure ?boot", r"\blinux\b", r"steam ?deck", r"kernel", r"tpm",
        r"not supported", r"proton", r"主板", r"bios", r"筛选", r"不给进", r"排除",
        r"セキュアブート", r"対応してない", r"非対応", r"はじかれ", r"締め出",
    ],
    "competitive_balance": [
        r"pay ?to ?win", r"\bp2w\b", r"match ?making", r"\bsbmm\b", r"\brng\b",
        r"balanc", r"\bnerf", r"overpowered", r"\bop\b", r"rank",
        r"匹配", r"平衡", r"数值", r"氪金碾压", r"课金", r"ランク", r"マッチング",
        r"バランス", r"ナーフ", r"ぶっ壊れ", r"格差",
    ],
    "unfair_by_design": [
        r"理不尽", r"りふじん", r"ズル", r"セコ", r"簡悔", r"初見殺", r"即死",
        r"unfair", r"cheap ?shot", r"bullshit", r"artificial difficulty",
        r"数值用脚", r"神经刀", r"读指令", r"逆天",
    ],
}


def load_assigned():
    ids = set()
    with MANIFEST.open() as f:
        for r in csv.DictReader(f):
            ids.add(r["review_id"])
    return ids


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SEEDS:
        print("facets:", ", ".join(SEEDS))
        return
    facet = sys.argv[1]
    only_lang = sys.argv[2] if len(sys.argv) > 2 else None
    pat = re.compile("|".join(SEEDS[facet]), re.IGNORECASE)
    assigned = load_assigned()

    hits = []
    for p in sorted(RAW.glob("*.jsonl")):
        if p.name == "pilot_worksheet.jsonl":
            continue
        lang = p.stem.split("_")[-1]
        if only_lang and lang != only_lang:
            continue
        with p.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                rid = str(d["recommendationid"])
                if rid in assigned:
                    continue
                txt = d.get("review", "") or ""
                if pat.search(txt):
                    hits.append((lang, d["appid"], rid, len(txt),
                                 int(bool(d.get("voted_up"))), d.get("votes_funny", 0),
                                 txt.replace("\n", " ⏎ ")))

    # readable band: substantive but not a wall of text; skip noise & essays
    lo, hi = 20, 420
    band = [h for h in hits if lo <= h[3] <= hi]
    band.sort(key=lambda h: (h[0], h[2]))
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 45
    print(f"facet={facet} lang={only_lang or 'ALL'}  hits={len(hits)}  "
          f"in-band[{lo},{hi}]={len(band)}  showing<= {cap}\n")
    for lang, appid, rid, ln, up, funny, txt in band[:cap]:
        print(f"[{appid}/{lang}/{rid}] len={ln} up={up} funny={funny}")
        print(f"  {txt[:300]}")


if __name__ == "__main__":
    main()
