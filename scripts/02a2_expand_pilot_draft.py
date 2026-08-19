"""
02a2_expand_pilot_draft.py — draw a SECOND batch of pilot_draft reviews,
doubling the codebook-drafting set from 15 -> 30 per (game, lang) cell
(45 -> 90 per language; 135 -> 270 total pilot_draft rows).

Why a separate additive script instead of bumping PER_GAME_DRAFT in
02a_make_pilot.py: the first 135 rows are already carved and (soon) acted on;
re-running 02a with a larger N would reshuffle and could move existing rows.
Keeping the expansion additive preserves the original 135 verbatim and only
appends new review_ids.

Invariants (same as 02a, see data_split_spec.md):
  - 后减前: the new draw subtracts EVERY review_id already in the manifest
    (both pilot_draft batch-1 and pilot_prompt), so a review keeps exactly one role.
  - reproducible: fixed per-cell seed, distinct suffix ("-draft2") so batch-2
    is a fresh draw, not a re-run of batch-1.
  - Tier-1 firewall intact: gold/dev/train are carved LATER from the aligned pool
    with their own 后减前, so these new pilot ids are simply unavailable to them.

Idempotent: if pilot_draft already has the target count this is a no-op unless --force.
Raw texts stay local; only review_ids enter the manifest.
"""
import argparse
import random
from importlib import import_module

# reuse everything from the first pilot script (which itself pulls 01_collect)
_p = import_module("02a_make_pilot")
GAMES = _p.GAMES
SHORT_LANGS = _p.SHORT_LANGS
SPLIT_SEED = _p.SPLIT_SEED
raw_ids = _p.raw_ids
load_manifest = _p.load_manifest
write_manifest = _p.write_manifest
MANIFEST = _p.MANIFEST

PER_GAME_DRAFT2 = 15   # add this many per (game, lang) -> doubles pilot_draft
TARGET_PER_CELL = 30   # 15 (batch-1) + 15 (batch-2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="re-carve batch-2 even if the target count already exists")
    args = ap.parse_args()

    rows = load_manifest()
    assigned = {r["review_id"] for r in rows} | _p.load_reserved_ids()
    draft_per_cell = {}
    for r in rows:
        if r["role"] == "pilot_draft":
            draft_per_cell[(r["appid"], r["lang"])] = draft_per_cell.get((r["appid"], r["lang"]), 0) + 1

    # GAMES keys are ints (730); manifest appid is a string ("730") -> compare as str
    already_full = draft_per_cell and all(
        draft_per_cell.get((str(appid), lang), 0) >= TARGET_PER_CELL
        for appid in GAMES for lang in SHORT_LANGS
    )
    if already_full and not args.force:
        print(f"pilot_draft already at {TARGET_PER_CELL}/cell — nothing to do. Use --force.")
        return

    new_rows, summary = [], []
    for appid_int in GAMES:
        appid = str(appid_int)
        for lang in SHORT_LANGS:
            have = draft_per_cell.get((appid, lang), 0)
            need = max(0, TARGET_PER_CELL - have)
            pool = [rid for rid in raw_ids(appid, lang) if rid not in assigned]  # 后减前
            rng = random.Random(f"{SPLIT_SEED}-{appid}-{lang}-draft2")           # fresh draw
            rng.shuffle(pool)
            if len(pool) < need:
                raise SystemExit(f"[{appid}/{lang}] pool={len(pool)} < need={need}")
            take = pool[:need]
            for rid in take:
                new_rows.append({"review_id": rid, "appid": appid, "lang": lang, "role": "pilot_draft"})
                assigned.add(rid)
            summary.append((appid, lang, have, len(take)))

    write_manifest(rows + new_rows)

    print(f"\nAppended {len(new_rows)} pilot_draft rows -> {MANIFEST}")
    print(f"{'game':<11}{'lang':<5}{'had':>5}{'added':>7}")
    for appid, lang, had, added in summary:
        print(f"{GAMES[int(appid)]['name']:<11}{lang:<5}{had:>5}{added:>7}")

    # emit the NEW review_ids so a caller can dump/inspect just batch-2
    print("\nNEW_IDS " + ",".join(f"{r['appid']}/{r['lang']}/{r['review_id']}" for r in new_rows))


if __name__ == "__main__":
    main()
