"""
02a5_purposive_crosslingual.py — a THIRD purposive top-up to pilot_draft, this
time targeted at the *missing-language cells* of each surviving facet, so we can
empirically test whether a facet's language skew is a real property of the world
or merely an artifact of which language's seed words I searched (02a3/02a4 only
seeded a subset).

Rationale (Yifan, 2026-08-10): "语言和游戏绑死会不会是因为你没去有意找某种语言对应
该 facet 的评论?" — right. This pass consciously searches the SAME game where a
facet lives, in the languages that were empty, and hand-verifies every hit
against the §4.0 positive-example gate (norm-violation cue required, not a bare
keyword). Floor set by Yifan = each facet should reach >=3 standalone PRESENT
per language before "cross-lingual" may be claimed for that language.

FINDINGS (disclose in codebook §9):
  - unfair_by_design EN/ZH were a SAMPLING HOLE, not a real gap: Elden Ring has
    abundant EN "artificial difficulty / input reading" and ZH "读指令/作弊AI/理不尽"
    reviews. Filled to en>=3, zh>=3.
  - sanction EN/JA: genuine unjust-ban instances exist in both. Filled.
  - competitive_balance JA was a small-pilot artifact: the full BF dump is full
    of structural one-sided-balance complaints (一方的/陣営有利/兵器過強+対抗手段なし).
    Reached en3/zh3/ja3.
  - access_exclusion JA is UNDER-ATTESTED in the current pilot (rev7 wording):
    after multiple seed sets (secure boot / TPM / kernel / 課金アンロック / Linux)
    only ONE genuine JA instance (201569269, secure-boot lockout) surfaced; the
    rest are cosmetic battle-pass or §5-C technical. We CANNOT yet tell whether
    this is real sparsity, a game-mechanic difference, or insufficient seed-word
    recall — so ja stays 1 (NOT force-inflated) and the facet is kept as a full,
    potentially tri-lingual construct with JA marked under-attested, NOT
    downgraded to bilingual. Current locus: EN·ZH attested, JA under-attested,
    BF-only. taxonomy_status = exploratory (codebook §4.2.1).

Same firewall as 02a3/02a4: pilot_draft is NOT measurement; gold is carved later
from the aligned pool with 后减前, so these ids are simply unavailable to it.

Provenance -> data/splits/pilot_draft_purposive_crosslingual.csv
"""
import csv
import os
from importlib import import_module

_p = import_module("02a_make_pilot")
load_manifest = _p.load_manifest
write_manifest = _p.write_manifest
SPLITS_DIR = os.path.dirname(_p.MANIFEST)

# (appid, lang, review_id, facet, one-line reason) — ALL read in full & verified
CURATED = [
    # ---- unfair_by_design: fill EN + ZH (Elden 1245620) ----
    ("1245620", "en", "230265639", "unfair_by_design", "artificial difficulty inflation of buffered inputs / enemies phasing through attacks"),
    ("1245620", "en", "224450185", "unfair_by_design", "nonsense troll design, input reading fake difficulty; gave it many 'fair shakes'"),
    ("1245620", "en", "221548261", "unfair_by_design", "bosses have unfair advantages a normal player can't counter; clears overworld fine (not skill)"),
    ("1245620", "en", "230299621", "unfair_by_design", "up=1 review: 'instead of fair fights' one-shot gimmicks / input reading; hard for wrong reasons"),
    ("1245620", "zh", "230587480", "unfair_by_design", "精英怪读指令+无限精力=作弊AI,理不尽设计(详尽)"),
    ("1245620", "zh", "231333698", "unfair_by_design", "神经刀/预输入/读指令等不正当机制"),
    ("1245620", "zh", "227213259", "unfair_by_design", "招式不可躲+数值畸高+超长连段,恶意理不尽难度"),
    # ---- sanction: fill EN + JA (BF 1517290) ----
    ("1517290", "en", "217797587", "sanction", "accused of cheating then banned, 'unlawfully' stripped paid access; never cheated"),
    ("1517290", "en", "202942525", "sanction", "perma-banned for unknown TOS violation; appealed, pointless"),
    ("1517290", "en", "202880727", "sanction", "account hacked then perma-banned; appealed 3 times, denied"),
    ("1517290", "ja", "194187711", "sanction", "ソロでAI相手に誤BAN,処罰不公"),
    ("1517290", "ja", "129681583", "sanction", "無チートでBAN、問い合わせ返信なし(申訴無門)"),
    ("1517290", "ja", "109029583", "sanction", "未使用でオートエイム扱い垢ban、申訴無効、返金要求"),
    # ---- access_exclusion: only ONE genuine JA instance exists (see FINDINGS) ----
    ("1517290", "ja", "201569269", "access_exclusion", "secure boot 強制;非対応マザボは締め出し(JAで唯一の実例、up=1)"),
    # ---- competitive_balance: fill EN + JA (BF 1517290) ----
    ("1517290", "en", "225680958", "competitive_balance", "pay-to-win gun (MK-4) with no balancing"),
    ("1517290", "en", "203001509", "competitive_balance", "OP guns locked behind a paywall (paid PvP edge)"),
    ("1517290", "en", "202937972", "competitive_balance", "matchmaking lopsided: opposing team special forces vs your team clueless"),
    ("1517290", "ja", "162341785", "competitive_balance", "プレイヤーバランス無く常にどちらかの陣営有利、一方的な試合"),
    ("1517290", "ja", "159465541", "competitive_balance", "競技バランスが前作から退化、一方的な撃ち合い"),
    ("1517290", "ja", "178770151", "competitive_balance", "up=1: spawn設計+兵器過強で歩兵に対抗手段なく一方的に摺り潰される(構造的)"),
]

PROV = os.path.join(SPLITS_DIR, "pilot_draft_purposive_crosslingual.csv")


def main():
    rows = load_manifest()
    assigned = {r["review_id"] for r in rows} | _p.load_reserved_ids()

    new_rows, prov_rows, skipped = [], [], []
    for appid, lang, rid, facet, reason in CURATED:
        prov_rows.append({"review_id": rid, "appid": appid, "lang": lang,
                          "curated_tag": facet, "reason": reason})
        if rid in assigned:
            skipped.append(rid)
            continue
        new_rows.append({"review_id": rid, "appid": appid, "lang": lang, "role": "pilot_draft"})
        assigned.add(rid)

    write_manifest(rows + new_rows)
    with open(PROV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["review_id", "appid", "lang", "curated_tag", "reason"])
        w.writeheader()
        w.writerows(prov_rows)

    print(f"Appended {len(new_rows)} purposive-crosslingual pilot_draft rows -> {_p.MANIFEST}")
    print(f"Provenance -> {PROV}")
    if skipped:
        print(f"skipped (already assigned): {skipped}")
    from collections import Counter
    print("by lang:", dict(Counter(r["lang"] for r in new_rows)))
    print("by facet x lang:",
          dict(Counter((p["curated_tag"], p["lang"]) for p in prov_rows)))


if __name__ == "__main__":
    main()
