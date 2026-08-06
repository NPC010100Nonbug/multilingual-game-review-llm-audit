"""
02a_make_pilot.py — carve the two PILOT sets (pilot_draft, pilot_prompt) from the
raw pool and record them in data/splits/split_manifest.csv (Phase 3a).

See data_split_spec.md for the full rules. Invariants enforced HERE:
  - one review_id  ->  exactly one role
  - "后减前": each draw subtracts review_ids already assigned in the manifest
  - fixed SPLIT_SEED so the split is reproducible on any machine
  - pilot_draft and pilot_prompt are DISJOINT (Tier-2 hygiene: the LLM prompt
    examples must not be the same reviews baked into the codebook).

Pilots are drawn from data/raw/ (BEFORE alignment) on purpose: the unfairness
construct is window-independent, so codebook drafting need not wait for
02_align_sample.py. gold/dev/train are carved LATER, from the aligned pool, by
02_align_sample.py — always subtracting the ids already in the manifest.

Drawn from all three games (CS2 / BF2042 / Elden Ring) so the codebook generalises
across different unfairness contexts (P2W & matchmaking, monetisation, "hard != unfair").

Idempotent: if pilots are already in the manifest this is a no-op unless --force.

Raw texts stay local (data/raw/ gitignored); only review_ids leave this machine.
"""
import argparse
import csv
import json
import os
import random
from importlib import import_module

# reuse GAMES / LANGUAGES / RAW_DIR from 01_collect.py (same folder)
_mod = import_module("01_collect")
GAMES = _mod.GAMES                 # {730: {...}, 1517290: {...}, 1245620: {...}}
RAW_DIR = _mod.RAW_DIR

SPLIT_SEED = 20260806              # data_split_spec.md — NEVER change
PER_GAME_DRAFT = 15               # per (game, lang) -> ~45/lang across 3 games
PER_GAME_PROMPT = 15              # per (game, lang) -> ~45/lang across 3 games
SHORT_LANGS = ("en", "zh", "ja")

SPLITS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "splits")
MANIFEST = os.path.join(SPLITS_DIR, "split_manifest.csv")
FIELDS = ("review_id", "appid", "lang", "role")
ROLE_ORDER = {"pilot_draft": 0, "pilot_prompt": 1, "gold": 2, "dev": 3, "train": 4}


def load_manifest():
    """Existing manifest rows (empty list if only the header / no file)."""
    if not os.path.exists(MANIFEST):
        return []
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def raw_ids(appid, lang):
    """All review_ids in data/raw/<appid>_<lang>.jsonl as strings, sorted by
    numeric value so sampling is independent of file line order."""
    path = os.path.join(RAW_DIR, f"{appid}_{lang}.jsonl")
    ids = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            ids.add(str(json.loads(line)["recommendationid"]))
    return sorted(ids, key=int)


def write_manifest(rows):
    """Rewrite the whole manifest in a stable, diff-friendly order."""
    os.makedirs(SPLITS_DIR, exist_ok=True)
    rows = sorted(rows, key=lambda r: (ROLE_ORDER.get(r["role"], 9),
                                       int(r["appid"]), r["lang"], int(r["review_id"])))
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="re-carve even if pilots already exist in the manifest")
    args = ap.parse_args()

    rows = load_manifest()
    assigned = {r["review_id"] for r in rows}
    existing_pilot = [r for r in rows if r["role"] in ("pilot_draft", "pilot_prompt")]
    if existing_pilot and not args.force:
        print(f"Pilots already in manifest ({len(existing_pilot)} rows) — nothing to do. "
              f"Use --force to re-carve.")
        return

    new_rows, summary = [], []
    for appid in GAMES:
        for lang in SHORT_LANGS:
            pool = [rid for rid in raw_ids(appid, lang) if rid not in assigned]  # 后减前
            rng = random.Random(f"{SPLIT_SEED}-{appid}-{lang}")  # reproducible, per-cell
            rng.shuffle(pool)
            need = PER_GAME_DRAFT + PER_GAME_PROMPT
            if len(pool) < need:
                raise SystemExit(f"[{appid}/{lang}] pool={len(pool)} < needed={need}; "
                                 f"lower PER_GAME_* or check raw data.")
            draft = pool[:PER_GAME_DRAFT]
            prompt = pool[PER_GAME_DRAFT:need]
            for rid in draft:
                new_rows.append({"review_id": rid, "appid": appid, "lang": lang, "role": "pilot_draft"})
                assigned.add(rid)
            for rid in prompt:
                new_rows.append({"review_id": rid, "appid": appid, "lang": lang, "role": "pilot_prompt"})
                assigned.add(rid)
            summary.append((appid, lang, len(draft), len(prompt)))

    write_manifest(rows + new_rows)

    print(f"\nWrote {len(new_rows)} pilot rows -> {os.path.relpath(MANIFEST)}")
    print(f"{'game':<11}{'lang':<5}{'draft':>7}{'prompt':>8}")
    for appid, lang, nd, npr in summary:
        print(f"{GAMES[appid]['name']:<11}{lang:<5}{nd:>7}{npr:>8}")
    print(f"{'TOTAL':<16}{sum(s[2] for s in summary):>7}{sum(s[3] for s in summary):>8}")


if __name__ == "__main__":
    main()
