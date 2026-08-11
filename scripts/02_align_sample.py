"""
02_align_sample.py — materialize the machine_eligible_frame and draw the gold
sampling IDs (Phase 3b).

Reads the frozen gold-sampling scheme (see data_split_spec.md §1/§3 and
~/Desktop/gold抽样与压力集_方案讨论_2026-08-10.md §7/§8, 🔒 2026-08-11):

  machine_eligible_frame  = raw dedup(recommendationid)
                          + time window (timestamp_created <= 2026-08-01 UTC,
                            no lower bound for the primary pool)
                          + light content filter (drop empty / pure-symbol; NO
                            min-length threshold)
                          + Steam-language bucket (trust the collection `lang`;
                            NO langid, NO post-hoc language_match exclusion)
                          - 后减前: subtract every review_id already in the
                            manifest (the 488 pilot rows), so pilots can never
                            leak into gold/dev/train.

  gold  = equal 200 raw per language (600 total); within each language, allocate
          across the 3 games by that game's share of the language's frame count
          via the largest-remainder method; each game×lang cell is independently
          seed-shuffled, gold takes the first n, the remainder (order preserved)
          is the NA-backfill reserve order.

  design weight (per cell) restores the *observed eligible corpus* composition
  in the frame — NOT Steam全平台/全历史/玩家人口 (the data is capped by Steam's
  `recent` depth ceiling; it is not a probability sample of all history).
      w_cell = (N_cell / N_frame) / (n_cell / n_gold)

TWO MODES (firewall):
  * default (analysis):   materialize the frame to data/processed/, recompute the
      true 9-cell counts on the REAL frame, print the allocation + exact per-cell
      design weights, then STOP. Does NOT touch the manifest. Safe/reversible.
  * --draw-gold:          actually draw the gold review_ids (ID only, no text),
      append them to split_manifest.csv, and write the reserve order. Per the
      frozen ordering firewall this may precede prompt-freeze (IDs only), but
      OPENING/LABELING gold text must wait until the prompt is frozen.

Only review_ids leave this machine. Raw texts stay local (data/raw/ gitignored).
This script draws GOLD only; dev/train are a later, separate carve.
"""
import argparse
import csv
import json
import os
import re
from datetime import datetime, timezone
from importlib import import_module
from math import floor
from random import Random

# reuse GAMES / RAW_DIR / LANGUAGES from 01_collect.py (same folder)
_mod = import_module("01_collect")
GAMES = _mod.GAMES                 # {730: {...}, 1517290: {...}, 1245620: {...}}
RAW_DIR = _mod.RAW_DIR

SPLIT_SEED = 20260806              # data_split_spec.md — NEVER change
GOLD_PER_LANG = 200               # equal-200 raw per language (frozen 2026-08-11)
LANGS = ("en", "zh", "ja")        # Steam-language buckets

# time window: timestamp_created <= 2026-08-01 00:00:00 UTC (inclusive); no lower bound
WINDOW_CUTOFF = int(datetime(2026, 8, 1, tzinfo=timezone.utc).timestamp())

SPLITS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "splits")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
MANIFEST = os.path.join(SPLITS_DIR, "split_manifest.csv")
FRAME_CSV = os.path.join(PROCESSED_DIR, "machine_eligible_frame.csv")
RESERVE_CSV = os.path.join(SPLITS_DIR, "gold_reserve_order.csv")
WEIGHTS_CSV = os.path.join(SPLITS_DIR, "gold_design_weights.csv")

MANIFEST_FIELDS = ("review_id", "appid", "lang", "role")
ROLE_ORDER = {"pilot_draft": 0, "pilot_prompt": 1, "gold": 2, "dev": 3, "train": 4}

# light content filter: keep a review iff, after stripping, it contains at least
# one "content character" = any Unicode letter or digit (CJK included). This drops
# empty / whitespace-only / pure-symbol&emoji reviews. NO min-length threshold.
_CONTENT_CHAR = re.compile(r"[^\W_]", re.UNICODE)


def is_eligible_text(text):
    return bool(text) and bool(_CONTENT_CHAR.search(text))


def load_manifest():
    if not os.path.exists(MANIFEST):
        return []
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_frame(assigned):
    """Stream every raw cell, apply window + content filter + dedup, subtract
    `assigned` (后减前). Returns (frame_rows, counts) where
      frame_rows = list of dicts {review_id, appid, lang, timestamp_created}
      counts     = {(appid, lang): n_eligible}
    """
    frame_rows, counts = [], {}
    for appid in GAMES:
        for lang in LANGS:
            path = os.path.join(RAW_DIR, f"{appid}_{lang}.jsonl")
            seen, kept = set(), 0
            with open(path, encoding="utf-8") as f:
                for line in f:
                    d = json.loads(line)
                    rid = str(d["recommendationid"])
                    if rid in seen:                 # dedup within cell
                        continue
                    seen.add(rid)
                    ts = int(d["timestamp_created"])
                    if ts > WINDOW_CUTOFF:          # time window (upper bound)
                        continue
                    if not is_eligible_text(d.get("review", "")):
                        continue                    # light content filter
                    if rid in assigned:             # 后减前 (drop the 488 pilots)
                        continue
                    frame_rows.append({"review_id": rid, "appid": appid,
                                       "lang": lang, "timestamp_created": ts})
                    kept += 1
            counts[(appid, lang)] = kept
    return frame_rows, counts


def largest_remainder(total, weights_by_key):
    """Allocate `total` integer units across keys proportional to weights, via the
    largest-remainder (Hamilton) method. weights_by_key: {key: nonneg count}."""
    keys = list(weights_by_key)
    wsum = sum(weights_by_key.values())
    if wsum == 0:
        return {k: 0 for k in keys}
    exact = {k: total * weights_by_key[k] / wsum for k in keys}
    alloc = {k: int(floor(exact[k])) for k in keys}
    remainder = total - sum(alloc.values())
    # hand out the leftover to the largest fractional parts (ties: larger cell first)
    order = sorted(keys, key=lambda k: (exact[k] - alloc[k], weights_by_key[k]), reverse=True)
    for k in order[:remainder]:
        alloc[k] += 1
    return alloc


def compute_plan(counts):
    """Return per-cell allocation + weights given frame counts.
    plan[(appid,lang)] = dict(N, n, w) ; also returns N_frame total."""
    N_frame = sum(counts.values())
    plan = {}
    for lang in LANGS:
        by_game = {appid: counts[(appid, lang)] for appid in GAMES}
        alloc = largest_remainder(GOLD_PER_LANG, by_game)
        for appid in GAMES:
            N, n = counts[(appid, lang)], alloc[appid]
            # normalized design weight: (N/N_frame) / (n/n_gold), n_gold = 3*200 = 600
            w = ((N / N_frame) / (n / (GOLD_PER_LANG * len(LANGS)))) if n else float("nan")
            plan[(appid, lang)] = {"N": N, "n": n, "w": w}
    return plan, N_frame


def write_frame(frame_rows):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    frame_rows = sorted(frame_rows, key=lambda r: (int(r["appid"]), r["lang"], int(r["review_id"])))
    with open(FRAME_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=("review_id", "appid", "lang", "timestamp_created"))
        w.writeheader()
        w.writerows(frame_rows)


def print_report(counts, plan, N_frame, wrote_frame):
    lang_tot = {lang: sum(counts[(a, lang)] for a in GAMES) for lang in LANGS}
    print(f"\nmachine_eligible_frame  (window: timestamp_created <= "
          f"{datetime.fromtimestamp(WINDOW_CUTOFF, timezone.utc):%Y-%m-%d} UTC, after 后减前)")
    print(f"  total eligible reviews N_frame = {N_frame:,}")
    print(f"  language shares: " + "  ".join(
        f"{lang.upper()} {lang_tot[lang]:,} ({lang_tot[lang]/N_frame:6.2%})" for lang in LANGS))
    print(f"\n{'game':<12}{'lang':<5}{'N_cell':>10}{'lang%':>9}{'gold n':>8}{'weight':>10}")
    print("-" * 54)
    for lang in LANGS:
        for appid in GAMES:
            c = plan[(appid, lang)]
            share = c["N"] / lang_tot[lang] if lang_tot[lang] else 0
            print(f"{GAMES[appid]['name']:<12}{lang:<5}{c['N']:>10,}{share:>9.2%}"
                  f"{c['n']:>8}{c['w']:>10.3f}")
    print("-" * 54)
    print(f"{'gold total':<17}{sum(p['n'] for p in plan.values()):>26}")
    if wrote_frame:
        print(f"\nframe materialized -> {os.path.relpath(FRAME_CSV)} "
              f"({N_frame:,} rows, review_id only, no text)")
    print("\n[analysis mode] manifest NOT touched, gold NOT drawn.")
    print("Re-run with --draw-gold to commit the gold IDs (one-way door: only do "
          "this once the scheme is signed off).")


def write_manifest(rows):
    os.makedirs(SPLITS_DIR, exist_ok=True)
    rows = sorted(rows, key=lambda r: (ROLE_ORDER.get(r["role"], 9),
                                       int(r["appid"]), r["lang"], int(r["review_id"])))
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        w.writeheader()
        w.writerows(rows)


def draw_gold(frame_rows, plan, rows, assigned, force):
    """Draw gold IDs per cell (seed-shuffle, take first n), record reserve order,
    append gold rows to the manifest, write reserve + weights side files."""
    existing_gold = [r for r in rows if r["role"] == "gold"]
    if existing_gold and not force:
        raise SystemExit(f"Gold already in manifest ({len(existing_gold)} rows) — "
                         f"refusing to redraw. Use --force to overwrite (DANGEROUS: "
                         f"changes which reviews are gold).")

    # index frame ids by cell, sorted by int id so the shuffle is order-independent
    by_cell = {(a, l): [] for a in GAMES for l in LANGS}
    for r in frame_rows:
        by_cell[(int(r["appid"]), r["lang"])].append(r["review_id"])
    for k in by_cell:
        by_cell[k] = sorted(by_cell[k], key=int)

    gold_rows, reserve_rows = [], []
    for lang in LANGS:
        for appid in GAMES:
            pool = [rid for rid in by_cell[(appid, lang)] if rid not in assigned]
            rng = Random(f"{SPLIT_SEED}-{appid}-{lang}")   # per-cell, reproducible
            rng.shuffle(pool)
            n = plan[(appid, lang)]["n"]
            gold_ids, reserve_ids = pool[:n], pool[n:]
            for rid in gold_ids:
                gold_rows.append({"review_id": rid, "appid": appid, "lang": lang, "role": "gold"})
                assigned.add(rid)
            for order, rid in enumerate(reserve_ids):
                reserve_rows.append({"review_id": rid, "appid": appid, "lang": lang, "reserve_order": order})

    # keep non-gold manifest rows if --force redrew (drop old gold)
    kept = [r for r in rows if r["role"] != "gold"]
    write_manifest(kept + gold_rows)

    with open(RESERVE_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=("review_id", "appid", "lang", "reserve_order"))
        w.writeheader()
        w.writerows(reserve_rows)

    with open(WEIGHTS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("appid", "lang", "N_cell", "n_gold", "weight"))
        for lang in LANGS:
            for appid in GAMES:
                c = plan[(appid, lang)]
                w.writerow((appid, lang, c["N"], c["n"], f"{c['w']:.6f}"))

    print(f"\n[--draw-gold] wrote {len(gold_rows)} gold rows -> {os.path.relpath(MANIFEST)}")
    print(f"              wrote reserve order ({len(reserve_rows)} rows) -> {os.path.relpath(RESERVE_CSV)}")
    print(f"              wrote per-cell design weights -> {os.path.relpath(WEIGHTS_CSV)}")
    print("\nGold IDs are drawn (text NOT read). FIREWALL: do not open/label gold "
          "text until the annotation prompt is frozen.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draw-gold", action="store_true",
                    help="commit the gold IDs to the manifest (one-way door)")
    ap.add_argument("--force", action="store_true",
                    help="allow redrawing gold even if it already exists (DANGEROUS)")
    args = ap.parse_args()

    rows = load_manifest()
    assigned = {r["review_id"] for r in rows}
    print(f"manifest: {len(rows)} rows already assigned "
          f"({sum(r['role']=='pilot_draft' for r in rows)} pilot_draft, "
          f"{sum(r['role']=='pilot_prompt' for r in rows)} pilot_prompt)")

    frame_rows, counts = build_frame(assigned)
    plan, N_frame = compute_plan(counts)

    if args.draw_gold:
        # still materialize the frame so it's on disk alongside the draw
        write_frame(frame_rows)
        print_report(counts, plan, N_frame, wrote_frame=True)
        draw_gold(frame_rows, plan, rows, assigned, args.force)
    else:
        write_frame(frame_rows)
        print_report(counts, plan, N_frame, wrote_frame=True)


if __name__ == "__main__":
    main()
