"""
02a4_purposive_procedural.py — append a PURPOSIVE (keyword-seeded, read-and-verified)
top-up of `procedural` facet examples to pilot_draft, so the §4.2.1 facet >=15
test has a fair chance (the 288-row pilot yielded every facet < 15; see
scripts/03c_facet_counts.py).

Same rationale/firewall as 02a3 (distributive top-up): pilot_draft is NOT
measurement, so purposive oversampling of a sparse construct is legitimate for
codebook drafting and MUST be disclosed as non-random. Candidates were surfaced
by scripts/03d over data/raw MINUS the manifest, then EACH WAS READ and checked
against the §4.0 positive-example gate before being curated here (不能猜). gold is
carved later from the aligned pool with its own 后减前, so these ids are simply
unavailable to it.

Cross-lingual note (disclose in codebook): the surviving facets are not evenly
spread across languages — `unfair_by_design`(理不尽) is JA/Elden-dominant,
`sanction`/`access_exclusion`(EA account bans / secure-boot lockout) are
ZH/EN-BF-dominant. `competitive_balance` is intentionally topped up only lightly
(3): genuine PvP-unearned-edge instances are sparse — most "balance" hits are
design-quality gripes (ABSENT) or collapse into cheating_governance — so it is
expected to stay < 15 and fold into plain `procedural` (codebook already flagged
it 证据最弱).

Provenance -> data/splits/pilot_draft_purposive_procedural.csv
"""
import csv
import os
from importlib import import_module

_p = import_module("02a_make_pilot")
load_manifest = _p.load_manifest
write_manifest = _p.write_manifest
SPLITS_DIR = os.path.dirname(_p.MANIFEST)

# (appid, lang, review_id, facet, one-line reason) — all read & verified
CURATED = [
    # ---- cheating_governance (cheaters + official inaction / useless anti-cheat) ----
    ("1517290", "zh", "150161145", "cheating_governance", "外挂锁头几百小时都没封号，官方吃屎"),
    ("1517290", "zh", "150165754", "cheating_governance", "开挂每局都有，EA反外挂比腾讯还差"),
    ("1517290", "zh", "150206371", "cheating_governance", "只能匹配遇挂只能忍，举报没用"),
    ("1517290", "zh", "150211153", "cheating_governance", "反作弊反了个寂寞，把把锁头"),
    ("1517290", "zh", "150213777", "cheating_governance", "亚服挂壁巨多，反作弊系统毫无卵用"),
    ("1517290", "zh", "150258942", "cheating_governance", "举报是摆设，10级开到100多没封，反作弊是托"),
    ("1517290", "zh", "150268645", "cheating_governance", "举报无用官方不受理，怀疑没人在运营"),
    ("1517290", "ja", "103066720", "cheating_governance", "チーターだらけ、取り締まってもアカ作り直しで放置状態"),
    ("1517290", "ja", "103119670", "cheating_governance", "長年BFのチート放置、開発運営が無能"),
    ("1517290", "ja", "103208564", "cheating_governance", "怪しいチャットは即アカ停止なのにチーターはLv100超でも放置"),
    # ---- unfair_by_design (PvE '理不尽', not 難しさ; illegitimate design) ----
    ("1245620", "ja", "110935440", "unfair_by_design", "ワンパン即死、あえて言うがこれは理不尽"),
    ("1245620", "ja", "110980549", "unfair_by_design", "ボス圧倒的に理不尽、敵の射程異常、遠距離のメリット潰す"),
    ("1245620", "ja", "111006379", "unfair_by_design", "ボスの理不尽さ際立つ、チェイン即死、徒労感"),
    ("1245620", "ja", "111171900", "unfair_by_design", "高難易度は間違い、要するに理不尽なだけ"),
    ("1245620", "ja", "111210060", "unfair_by_design", "敵は常時3~4行動、こちら1行動の間に即死技連打"),
    ("1245620", "ja", "111245287", "unfair_by_design", "チャリオット触れただけ即死は納得いかない、敵だけ射程届く"),
    ("1245620", "ja", "111269280", "unfair_by_design", "高難易度と理不尽をはき違えたボス、雑な複数戦"),
    ("1245620", "ja", "111335816", "unfair_by_design", "クソカメラ地形、2匹ボスの理不尽難易度、性格の悪いゲーム"),
    ("1245620", "ja", "111364629", "unfair_by_design", "達成感なくただただ理不尽なゲーム"),
    ("1245620", "ja", "111373012", "unfair_by_design", "終盤は難しいより理不尽が目立つ、後半の雑な調整"),
    ("1245620", "ja", "111376155", "unfair_by_design", "バランス酷すぎ、理不尽な攻撃にストレス"),
    ("1245620", "ja", "111412231", "unfair_by_design", "自機はダクソ動作なのに敵はSEKIRO並、ひたすら理不尽"),
    # ---- sanction (unjust/arbitrary ban, appeal useless) ----
    ("1517290", "zh", "150223003", "sanction", "买没几天连不上，再过两周直接封号"),
    ("1517290", "zh", "150224641", "sanction", "玩五小时无缘无故被封号，申诉没用退款无门"),
    ("1517290", "zh", "150257085", "sanction", "大陆玩家别买，EA账户很容易被封禁"),
    ("1517290", "zh", "150327632", "sanction", "举报作弊无回信，举报言论隔天邮件称不采取行动"),
    ("1517290", "zh", "150974310", "sanction", "号被乱封，正经外挂不封、我却被封"),
    ("1517290", "zh", "150989951", "sanction", "付完款库里没戏，申诉一天没解决没退款"),
    ("1517290", "zh", "151030953", "sanction", "傻逼EA不当人乱封号"),
    ("1517290", "zh", "151032914", "sanction", "被封号至今未解除，申诉2小时也没用"),
    ("1517290", "zh", "151358849", "sanction", "打折期间购买玩几天，打折一到就被封号"),
    ("1517290", "zh", "151394650", "sanction", "EA账号永久封禁，无缘无故没开过挂，申诉不一定通过"),
    ("1517290", "zh", "151615816", "sanction", "刚玩一天账号就被永久封禁"),
    ("1517290", "en", "103041746", "sanction", "banned 3 days for username, stripped of right to play a $90 game"),
    ("1517290", "zh", "151039367", "sanction", "APEX没开过挂突然永封，2042全是挂一个不封"),
    # ---- access_exclusion (platform/hardware exclusion WITH normative cue; strict §4.0 gate) ----
    ("1517290", "en", "103042299", "access_exclusion", "secure boot does nothing vs cheaters so the anti-cheat excuse is bollocks"),
    ("1517290", "en", "103062450", "access_exclusion", "Unplayable on Linux systems. Get with the times, Dice/EA!"),
    ("1517290", "en", "103037208", "access_exclusion", "kernel-level anticheat = malware (intrusive gatekeeping)"),
    ("1517290", "en", "103070453", "access_exclusion", "f u dice for update requiring ALL players to enable secure boot"),
    ("1517290", "zh", "157114225", "access_exclusion", "自己没技术防外挂却要玩家开Secure boot，刚氪金完游戏不给进"),
    ("1517290", "zh", "163631825", "access_exclusion", "举报外挂没用，现在要开Secure boot才能进，开了就死机"),
    ("1517290", "zh", "167554716", "access_exclusion", "单机玩家却被逼改bios开安全模式，否则玩不了"),
    # ---- competitive_balance (PvP unearned edge / matchmaking unfairness) — expected to stay THIN ----
    ("1517290", "zh", "150436907", "competitive_balance", "匹配机制局局被碾压，这边最高10杀对面人均20"),
    ("1517290", "zh", "151023360", "competitive_balance", "匹配烂，自家打点掉一百个都进不去载具，对面分分钟平推"),
    ("1517290", "zh", "150172993", "competitive_balance", "匹配机制烂，对面开载具框框揍、队友载具不出门"),
]

PROV = os.path.join(SPLITS_DIR, "pilot_draft_purposive_procedural.csv")


def main():
    rows = load_manifest()
    assigned = {r["review_id"] for r in rows} | _p.load_reserved_ids()

    # provenance is written for EVERY curated row (idempotent across re-runs);
    # the manifest only gains rows not already assigned.
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

    print(f"Appended {len(new_rows)} purposive-procedural pilot_draft rows -> {_p.MANIFEST}")
    print(f"Provenance -> {PROV}")
    if skipped:
        print(f"skipped (already assigned): {skipped}")
    from collections import Counter
    print("by lang:", dict(Counter(r["lang"] for r in new_rows)))
    print("by facet:", dict(Counter(p["curated_tag"] for p in prov_rows)))


if __name__ == "__main__":
    main()
