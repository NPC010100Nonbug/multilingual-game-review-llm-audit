#!/usr/bin/env python3
"""05_stress_retrieve.py — mechanical keyword retrieval for the stress set (③').

Frozen keyword tables: EN/ZH now come from freeze/stress_preregistration_v1.2.md
(per-language, supersedes v1.1 §5 shared table); JA stays v1.1 §5.1.  This script
embeds them verbatim (like 03d's SEEDS) so the run is reproducible.  It is
PURELY MECHANICAL:
  - reads review text only to test frozen keywords,
  - writes ONLY review_id + match metadata (never the review text) to a
    publishable manifest,
  - opening candidate text / human labelling happens LATER, after prompt-freeze.

Firewall (stress_preregistration.md §4):
  candidates ⊂ machine_eligible_frame  MINUS  baseline = every review_id already
  in split_manifest at run time (488 pilot + 600 gold = 1088).  One review_id →
  one data role; §6 dedup (by review_id, then normalized text) runs BEFORE any
  downsampling.

Output: data/splits/stress_candidate_manifest.csv  (id-only, no text)

Usage: python3 scripts/05_stress_retrieve.py
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
FRAME = ROOT / "data" / "processed" / "machine_eligible_frame.csv"
MANIFEST = ROOT / "data" / "splits" / "split_manifest.csv"
OUT = ROOT / "data" / "splits" / "stress_candidate_manifest.csv"

SPLIT_SEED = 20260806  # frozen; kept for provenance / downstream ordering

# --- Frozen keyword tables (freeze/stress_preregistration.md §5 / §5.1) -------
# A keyword is a list of GROUPS.  A group is a regex-alternation string.
# A keyword MATCHES a review iff EVERY group is found (re.search) somewhere in
# the text (order-independent co-occurrence).  Single-token keywords are a
# one-group list.  "family" is the stable label recorded in the manifest.
# Structure: KEYWORDS[lang][bucket][tier] = list of (family, [group, ...]).

def kw(family, *groups):
    return (family, list(groups))

# v1.2 (2026-08-12, Yifan): EN and ZH split into per-language tables so each
# language's high-precision patterns run ONLY on its own Steam-language bucket
# (freeze/stress_preregistration_v1.2.md, supersedes v1.1 §5 shared EN/ZH table).
# Patterns transcribed verbatim from that addendum; `.{0,n}` windows rely on the
# re.DOTALL compile so a co-occurrence window may span newlines.

EN = {
    "distributive": {
        "high": [
            kw("pay-to-win", r"\bpay[- ]?(?:to|2)[- ]?win\b"),
            kw("paid→advantage", r"(?:paying|paid|premium).{0,40}(?:advantage|edge|stronger|win)"),
            kw("gear locked behind pay", r"(?:weapons?|guns?|vehicles?|characters?).{0,50}(?:locked|lock).{0,50}(?:pay|premium|edition|DLC)"),
            kw("f2p→disadvantage", r"(?:f2p|free[- ]?to[- ]?play|non[- ]?paying).{0,60}(?:unfair|disadvantage|cannot compete)"),
        ],
        "broad": [
            kw("premium", r"premium"), kw("paid", r"\bpaid\b"), kw("paywall", r"paywall"),
            kw("battlepass", r"battle ?pass"), kw("DLC", r"\bdlc\b"), kw("unlock", r"\bunlock"),
            kw("grind", r"\bgrind"), kw("edition", r"\bedition\b"), kw("skin", r"\bskin"),
        ],
    },
    "cheating_governance": {
        "high": [
            kw("cheaters running wild", r"(?:cheaters?|hackers?|cheating|hacks?).{0,70}(?:running wild|run rampant|not banned|never banned|ignored)"),
            kw("reports do nothing", r"(?:reports?|reporting).{0,70}(?:does nothing|no action|not actioned|ignored)"),
            kw("anticheat useless", r"(?:anti[- ]?cheat|anticheat).{0,70}(?:useless|does nothing|not working|failed)"),
            kw("devs won't ban cheaters", r"(?:devs?|developers?|EA|Valve|officials?).{0,60}(?:do not|don't|never|won't).{0,60}(?:ban|act|care|fix).{0,60}(?:cheat|hack)"),
        ],
        "broad": [
            kw("cheat", r"cheat"), kw("cheater", r"cheater"), kw("hacker", r"hacker"),
            kw("hack", r"\bhack"), kw("aimbot", r"aimbot"), kw("wallhack", r"wall ?hack"),
            kw("anti-cheat", r"anti[- ]?cheat"), kw("VAC", r"\bvac\b"), kw("report", r"\breport"),
        ],
    },
    "sanction": {
        "high": [
            kw("false ban", r"\b(?:false|wrongful(?:ly)?|unjust(?:ly)?|mistaken).{0,18}(?:perma(?:nent)?|game|VAC)? ?ban(?:ned)?\b"),
            kw("banned no reason", r"(?:banned|ban).{0,90}(?:no reason|no explanation|without.{0,25}reason)"),
            kw("appeal denied", r"(?:appeal|support).{0,90}(?:denied|ignored|no response|won't respond|copy[ -]?paste)"),
        ],
        "broad": [
            kw("ban", r"\bban\b"), kw("banned", r"\bbanned\b"), kw("game ban", r"game ban"),
            kw("VAC", r"\bvac\b"), kw("kick", r"\bkick"), kw("appeal", r"\bappeal"),
            kw("support", r"\bsupport\b"),
        ],
    },
    "competitive_balance": {
        "high": [
            kw("matchmaking unfair", r"(?:matchmaking|MMR|ranked? match(?:es)?).{0,80}(?:unfair|rigged|one[- ]sided|unbalanced)"),
            kw("newbies vs veterans", r"(?:new|low[- ]?(?:level|rank|MMR)|beginner).{0,80}(?:matched|put|placed).{0,80}(?:high[- ]?(?:level|rank|MMR)|veterans?|prestige|top)"),
            kw("matchmaking skill gap", r"matchmaking.{0,60}(?:skill gap|rank disparity|huge gap)"),
        ],
        "broad": [
            kw("matchmaking", r"match ?making"), kw("MMR", r"\bmmr\b"), kw("rank", r"\brank"),
            kw("balance", r"\bbalanc"), kw("one-sided", r"one[- ]sided"), kw("stomp", r"\bstomp"),
            kw("new player", r"new player"), kw("veteran", r"veteran"), kw("aim assist", r"aim assist"),
            kw("RNG", r"\brng\b"), kw("OP", r"\bop\b"),
        ],
    },
    "unfair_by_design": {
        "high": [
            kw("artificial difficulty", r"(?:artificial difficulty|cheap design|unfair design|unfair mechanic)"),
            kw("enemies read inputs", r"(?:enemies?|boss(?:es)?|AI).{0,70}(?:input read(?:ing)?|read(?:s)? inputs?)"),
            kw("enemies infinite stamina", r"(?:enemies?|boss(?:es)?|AI).{0,70}(?:infinite|unlimited).{0,30}(?:stamina|poise|combos?)"),
        ],
        "broad": [
            kw("difficulty", r"difficulty"), kw("hard", r"\bhard\b"), kw("boss", r"\bboss"),
            kw("enemy", r"\benemy\b"), kw("AI", r"\bai\b"), kw("artificial", r"artificial"),
            kw("cheap", r"\bcheap\b"), kw("one-shot", r"one[- ]?shot"),
        ],
    },
    "access_exclusion": {
        "high": [  # combos only, no single-token HP
            kw("secureboot required→can't play", r"(?:secure ?boot|TPM|kernel[- ]?level anti[- ]?cheat).{0,90}(?:required|require|forced).{0,90}(?:can't play|cannot play|unable to play|locked out|not supported)"),
            kw("linux/deck unsupported→locked out", r"(?:Linux|Steam Deck|Proton).{0,90}(?:unsupported|cannot play|locked out).{0,90}(?:unreasonable|no reason|pointless|does nothing|forced)?"),
        ],
        "broad": [
            kw("Secure Boot", r"secure ?boot"), kw("TPM", r"\btpm\b"), kw("Linux", r"\blinux\b"),
            kw("Steam Deck", r"steam ?deck"), kw("Proton", r"\bproton\b"), kw("kernel", r"\bkernel\b"),
            kw("BIOS", r"\bbios\b"), kw("UEFI", r"\buefi\b"), kw("motherboard", r"motherboard"),
            kw("cannot launch", r"cannot launch"),
        ],
    },
}

ZH = {
    "distributive": {
        "high": [
            kw("氪金解锁装备→不公平", r"(?:氪金|付费|充值).{0,50}(?:解锁|获得).{0,50}(?:武器|枪械|角色|载具).{0,80}(?:不公平|影响.{0,15}平衡|优势|打不过)"),
            kw("不氪打不过", r"(?:不氪|零氪|白嫖).{0,70}(?:打不过|没法玩|不公平|劣势|被虐)"),
            kw("P2W→优势", r"(?:P2W|pay[- ]?to[- ]?win|逼氪|强制氪金).{0,80}(?:优势|不公平|平衡|武器|角色|载具)"),
        ],
        "broad": [
            kw("氪金", r"氪金"), kw("付费", r"付费"), kw("充值", r"充值"), kw("P2W", r"p2w"),
            kw("通行证", r"通行证"), kw("战令", r"战令"), kw("DLC", r"\bdlc\b"),
            kw("解锁", r"解锁"), kw("抽卡", r"抽卡"), kw("皮肤", r"皮肤"), kw("价格", r"价格"),
        ],
    },
    "cheating_governance": {
        "high": [
            kw("外挂→官方不管", r"(?:外挂|挂(?:逼|壁)?|作弊).{0,80}(?:官方|蓝洞|EA|开发|运营|策划).{0,80}(?:不管|不作为|不整治|不封|放任)"),
            kw("官方不管→外挂", r"(?:官方|蓝洞|EA|开发|运营|策划).{0,80}(?:不管|不作为|不整治|不封|放任).{0,80}(?:外挂|挂(?:逼|壁)?|作弊)"),
            kw("举报无反馈", r"举报.{0,80}(?:石沉大海|没.{0,12}(?:回应|回复|反馈)|不受理|没用).{0,80}(?:外挂|挂|作弊)?"),
            kw("反作弊摆设", r"反作弊.{0,80}(?:没用|无用|摆设|形同虚设|不作为)"),
        ],
        "broad": [
            kw("外挂", r"外挂"), kw("挂", r"开挂|挂逼|挂壁|挂B|挂b"), kw("作弊", r"作弊"),
            kw("锁头", r"锁头"), kw("透视", r"透视"), kw("DMA", r"\bdma\b"),
            kw("反作弊", r"反作弊"), kw("举报", r"举报"), kw("封号", r"封号"),
        ],
    },
    "sanction": {
        "high": [
            kw("误封/无故封", r"(?:误封|误判封禁|无故封号|莫名.{0,10}封|突然.{0,10}永封)"),
            kw("申诉无门", r"(?:申诉|投诉|客服).{0,80}(?:无门|不处理|不回复|石沉大海|不受理|驳回)"),
            kw("封号无理由", r"(?:封号|封禁|永封).{0,80}(?:没.{0,15}理由|不.{0,15}说明|没有.{0,15}证据)"),
        ],
        "broad": [
            kw("封号", r"封号"), kw("封禁", r"封禁"), kw("永封", r"永封"), kw("误封", r"误封"),
            kw("申诉", r"申诉"), kw("客服", r"客服"), kw("踢出", r"踢出"),
        ],
    },
    "competitive_balance": {
        "high": [
            kw("新手匹配老玩家", r"(?:新手|萌新|低等级|低段位).{0,80}(?:匹配|分配).{0,80}(?:老玩家|大佬|高等级|高段位)"),
            kw("匹配不公平", r"(?:匹配机制|匹配).{0,80}(?:不公平|不平衡|一边倒|被碾压|虐菜|等级差|段位差)"),
            kw("新手被虐", r"(?:新手|萌新).{0,80}(?:被.{0,15}(?:虐|碾压)|完全没.{0,12}体验)"),
        ],
        "broad": [
            kw("匹配", r"匹配"), kw("匹配机制", r"匹配机制"), kw("段位", r"段位"),
            kw("等级", r"等级"), kw("平衡", r"平衡"), kw("碾压", r"碾压"), kw("虐菜", r"虐菜"),
            kw("新手", r"新手"), kw("萌新", r"萌新"), kw("大佬", r"大佬"),
            kw("RNG", r"\brng\b"), kw("运气", r"运气"), kw("OP", r"\bop\b"),
        ],
    },
    "unfair_by_design": {
        "high": [
            kw("敌人读指令", r"(?:敌人|怪物|AI|BOSS|boss).{0,70}(?:读指令|读取指令|预读.{0,15}(?:操作|指令)?)"),
            kw("读指令→敌人", r"(?:读指令|读取指令|预读.{0,15}(?:操作|指令)?).{0,70}(?:敌人|怪物|AI|BOSS|boss)"),
            kw("恶意/人工难度设计", r"(?:恶意设计|不合理设计|不公平机制|人工难度).{0,80}(?:敌人|BOSS|AI|战斗|难度)?"),
            kw("敌人无限精力", r"(?:敌人|怪物|AI|BOSS|boss).{0,70}(?:无限.{0,15}(?:精力|耐力)|不讲理.{0,15}机制)"),
        ],
        "broad": [
            kw("读指令", r"读指令"), kw("人工难度", r"人工难度"), kw("恶意设计", r"恶意设计"),
            kw("机制", r"机制"), kw("理不尽", r"理不尽"), kw("难度", r"难度"),
            kw("boss", r"\bboss\b|BOSS"), kw("AI", r"\bai\b"), kw("即死", r"即死"),
        ],
    },
    "access_exclusion": {
        "high": [  # combos only, no single-token HP
            kw("安全启动强制→玩不了", r"(?:安全启动|Secure ?Boot|TPM).{0,90}(?:强制|必须|要求).{0,90}(?:不能玩|不给进|进不去|无法进入|玩不了)"),
            kw("改主板才能进", r"(?:改(?:BIOS|主板|设置)|更换(?:主板|硬件)).{0,80}(?:才能|才可).{0,80}(?:进游戏|玩游戏)"),
        ],
        "broad": [
            kw("安全启动", r"安全启动"), kw("Secure Boot", r"secure ?boot"), kw("TPM", r"\btpm\b"),
            kw("Linux", r"\blinux\b"), kw("Steam Deck", r"steam ?deck"), kw("Proton", r"\bproton\b"),
            kw("kernel", r"\bkernel\b"), kw("BIOS", r"\bbios\b"), kw("主板", r"主板"),
            kw("进不去", r"进不去"), kw("启动失败", r"启动失败"),
        ],
    },
}

JA = {
    "distributive": {
        "high": [
            kw("P2W", r"p2w"),
            kw("課金→有利", r"課金", r"有利|強い|勝て"),
            kw("無課金→不利", r"無課金", r"不利|勝てない|厳しい"),
            kw("課金→装備→有利", r"課金", r"武器|キャラ|解放", r"有利|必須"),
            kw("おま値", r"おま値"),
        ],
        "broad": [
            kw("課金", r"課金"), kw("無課金", r"無課金"), kw("解放", r"解放"),
            kw("アンロック", r"アンロック"), kw("DLC", r"dlc"), kw("バトルパス", r"バトルパス"),
            kw("おま国", r"おま国"), kw("日本だけ", r"日本だけ"), kw("価格", r"価格"),
        ],
    },
    "cheating_governance": {
        "high": [
            kw("チーター→野放し", r"チーター|チート", r"野放し|放置"),
            kw("チート対策していない", r"チート対策", r"していない|機能していない"),
            kw("通報しても対応ない", r"通報しても", r"対応|BAN", r"ない"),
        ],
        "broad": [
            kw("チート", r"チート"), kw("チーター", r"チーター"), kw("ハッカー", r"ハッカー"),
            kw("ウォールハック", r"ウォールハック"), kw("aimbot", r"aimbot"),
            kw("コンバーター", r"コンバーター"), kw("VAC", r"vac"),
        ],
    },
    "sanction": {
        "high": [
            kw("誤BAN", r"誤ban|誤バン|冤罪ban"),
            kw("濡れ衣BAN", r"濡れ衣", r"ban"),
            kw("身に覚えBAN", r"身に覚え", r"ban"),
            kw("BAN→理由ない", r"ban", r"理由.*ない|説明.*ない|解除されない|異議申立"),
        ],
        "broad": [
            kw("BAN", r"ban"), kw("垢BAN", r"垢ban"), kw("垢バン", r"垢バン"),
            kw("アカウント停止", r"アカウント停止"), kw("永久BAN", r"永久ban"), kw("キック", r"キック"),
        ],
    },
    "competitive_balance": {
        "high": [
            kw("不公平マッチング", r"不公平", r"マッチング|mmr"),
            kw("低MMR→格上マッチ", r"低mmr|初心者|低ランク", r"高mmr|格上|上位", r"マッチ|当た"),
            kw("マッチング格差", r"マッチング", r"格差|一方的"),
        ],
        "broad": [
            kw("マッチング", r"マッチング"), kw("MMR", r"mmr"), kw("ランク", r"ランク"),
            kw("バランス", r"バランス"), kw("格差", r"格差"), kw("一方的", r"一方的"),
            kw("PAD", r"\bpad\b|パッド"), kw("エイムアシスト", r"エイムアシスト"),
            kw("RNG", r"rng"), kw("運ゲー", r"運ゲー"), kw("OP", r"\bop\b"),
        ],
    },
    "unfair_by_design": {
        "high": [
            kw("理不尽な仕様", r"理不尽な(仕様|設計|敵|ai)"),
            kw("入力読み→敵AI", r"入力読み|読んでくる", r"ボス|敵|ai|仕様"),
            kw("敵だけ無限", r"(敵|ai)だけ", r"無限|スタミナ|有利|強い"),
        ],
        "broad": [
            kw("理不尽", r"理不尽"), kw("初見殺し", r"初見殺し"), kw("簡悔", r"簡悔"),
            kw("難しい", r"難しい"), kw("死にゲー", r"死にゲー"), kw("即死", r"即死"),
            kw("ボス", r"ボス"),
        ],
    },
    "access_exclusion": {
        "high": [
            kw("SecureBoot強制→非対応", r"secure ?boot|セキュアブート|tpm", r"強制|必須", r"非対応|マザーボード|遊べない"),
        ],
        "broad": [
            kw("Secure Boot", r"secure ?boot"), kw("セキュアブート", r"セキュアブート"),
            kw("TPM", r"tpm"), kw("Linux", r"linux"), kw("Steam Deck", r"steam ?deck"),
            kw("Proton", r"proton"), kw("マザーボード", r"マザーボード"),
            kw("起動できない", r"起動できない"),
        ],
    },
}

TABLES = {"en": EN, "zh": ZH, "ja": JA}

# Windowed `.{0,n}` co-occurrence patterns (EN/ZH v1.2) may span newlines.
FLAGS = re.IGNORECASE | re.DOTALL


def compile_tables():
    """lang -> bucket -> tier -> [(family, [compiled_group, ...])]; plus a
    per-language master prefilter regex (OR of every literal group)."""
    compiled = {}
    master = {}
    for lang, table in TABLES.items():
        compiled[lang] = {}
        all_groups = []
        for bucket, tiers in table.items():
            compiled[lang][bucket] = {}
            for tier, kws in tiers.items():
                clist = []
                for family, groups in kws:
                    cg = [re.compile(g, FLAGS) for g in groups]
                    clist.append((family, cg))
                    all_groups.extend(groups)
                compiled[lang][bucket][tier] = clist
        master[lang] = re.compile("|".join(f"(?:{g})" for g in all_groups), FLAGS)
    return compiled, master


def load_baseline():
    ids = set()
    with MANIFEST.open() as f:
        for r in csv.DictReader(f):
            ids.add(str(r["review_id"]))
    return ids


def load_frame():
    ids = set()
    with FRAME.open() as f:
        for r in csv.DictReader(f):
            ids.add(str(r["review_id"]))
    return ids


def norm(text):
    return hashlib.md5(re.sub(r"\s+", "", text).lower().encode("utf-8")).hexdigest()


def main():
    compiled, master = compile_tables()
    baseline = load_baseline()
    frame = load_frame()
    eligible = frame - baseline
    print(f"frame={len(frame)}  baseline={len(baseline)}  eligible={len(eligible)}", file=sys.stderr)

    # review_id -> aggregated hit record
    hits = {}
    seen_text = {}  # normalized-text hash -> review_id kept (first wins)
    scanned = 0
    for p in sorted(RAW.glob("[0-9]*.jsonl")):  # only appid_lang review files
        lang = p.stem.split("_")[-1]
        if lang not in TABLES:
            continue
        mpat = master[lang]
        with p.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                rid = str(d["recommendationid"])
                if rid not in eligible or rid in hits:
                    continue
                txt = d.get("review", "") or ""
                if not mpat.search(txt):
                    continue
                # detailed match across buckets/tiers
                families, buckets, tiers = [], set(), set()
                for bucket, tiermap in compiled[lang].items():
                    for tier, kws in tiermap.items():
                        for family, groups in kws:
                            if all(g.search(txt) for g in groups):
                                families.append(f"{bucket}:{tier}:{family}")
                                buckets.add(bucket)
                                tiers.add(tier)
                if not families:
                    continue
                scanned += 1
                # §6 normalized-text dedup (first review_id wins)
                h = norm(txt)
                if h in seen_text:
                    continue
                seen_text[h] = rid
                hits[rid] = {
                    "review_id": rid,
                    "appid": d.get("appid", p.stem.split("_")[0]),
                    "steam_language": d.get("language", lang),
                    "lang": lang,
                    "matched_keyword_families": "|".join(families),
                    "eligible_target_buckets": "|".join(sorted(buckets)),
                    "precision_tiers": "|".join(sorted(tiers)),
                    "text_len": len(txt),
                }

    rows = sorted(hits.values(), key=lambda r: (r["lang"], r["eligible_target_buckets"], r["review_id"]))
    cols = ["review_id", "appid", "lang", "steam_language",
            "eligible_target_buckets", "precision_tiers",
            "matched_keyword_families", "text_len"]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in cols})

    # summary (counts only, no text)
    print(f"\nwrote {len(rows)} candidates -> {OUT.relative_to(ROOT)}", file=sys.stderr)
    from collections import Counter
    per_lang = Counter(r["lang"] for r in rows)
    print("per language:", dict(per_lang), file=sys.stderr)
    per_cell = Counter()
    for r in rows:
        for b in r["eligible_target_buckets"].split("|"):
            per_cell[(r["lang"], b)] += 1
    print("\nper (lang, target_bucket)  [a review can count in >1 bucket]:", file=sys.stderr)
    for lang in ("en", "zh", "ja"):
        for b in ["distributive", "cheating_governance", "sanction",
                  "competitive_balance", "unfair_by_design", "access_exclusion"]:
            print(f"  {lang:3} {b:22} {per_cell[(lang, b)]:>7}", file=sys.stderr)


if __name__ == "__main__":
    main()
