"""
01b_deep_collect.py — resumable DEEP collection of EN/ZH back to each game's
Japanese floor (Phase 2, experimental).

Why a separate script from 01_collect.py:
  CS2 English/Chinese are so dense that reaching the 2023 Japanese floor may
  require paging through hundreds of thousands of reviews — potentially hours of
  requests. A run that long WILL be interrupted (network blip, laptop sleep,
  rate-limit). So this collector is built to survive that:

  1. WRITE AS IT GOES  — every page is appended to data/raw/<appid>_<lang>.jsonl
     immediately, so a crash never loses already-collected reviews.
  2. RESUME            — a checkpoint file remembers the last cursor per
     (game, lang); re-running continues instead of restarting from newest.
  3. SURVIVE ERRORS    — 429 / 5xx / timeouts retry with exponential backoff.
  4. TELL THE TRUTH    — if Steam's cursor stalls before reaching the floor (a
     real, UNVERIFIED possibility for very dense titles), it STOPS and reports
     the oldest date it actually reached. It never pretends to have data it
     doesn't have. This honest stop is the whole point of the experiment.

Floor per game = the oldest Japanese review already collected (the alignment
target from 01_collect.py). Run 01_collect.py (which pulls Japanese) FIRST.

NOTE: for a fresh (game, lang) with no checkpoint, any existing raw file from
the earlier capped v3 run is deleted and re-pulled from newest, so pagination
starts clean at cursor="*". Japanese files are never touched.

data/raw/ is gitignored: raw texts stay on this machine only.
"""

import json
import os
import time
from datetime import datetime, timezone
from importlib import import_module

# reuse fetch_page / GAMES / LANGUAGES / RAW_DIR from 01_collect.py (same folder)
_mod = import_module("01_collect")
fetch_page = _mod.fetch_page
GAMES = _mod.GAMES
LANGUAGES = _mod.LANGUAGES
RAW_DIR = _mod.RAW_DIR

LANGS_TO_DEEPEN = ("english", "schinese")   # Japanese is already collected in full

PAGE_PAUSE = 0.8            # seconds between successful pages (be polite)
MAX_PAGES = 20000          # ~4.4h/cell at 0.8s/page; just re-run to go further
PROGRESS_EVERY = 25        # print a progress line every N pages
MAX_RETRIES = 6            # per-page retry attempts on transient errors
STALL_LIMIT = 5            # consecutive "no new reviews" pages => cursor exhausted

CHECKPOINT_PATH = os.path.join(RAW_DIR, "_deep_checkpoint.json")


def as_date(ts):
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_checkpoint(ckpt):
    # write to a temp file then atomically replace, so a crash mid-write can't
    # leave a half-written (corrupt) checkpoint.
    tmp = CHECKPOINT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ckpt, f)
    os.replace(tmp, CHECKPOINT_PATH)


def game_floor(appid):
    """Oldest already-collected Japanese review = the alignment floor for EN/ZH."""
    ja_path = os.path.join(RAW_DIR, f"{appid}_ja.jsonl")
    floor = GAMES[appid]["min_timestamp"]          # fallback: construct floor / None
    if os.path.exists(ja_path):
        stamps = []
        with open(ja_path, encoding="utf-8") as f:
            for line in f:
                stamps.append(json.loads(line)["timestamp_created"])
        if stamps:
            floor = min(stamps)
    return floor


def load_existing(path):
    """Return (seen_ids, count, oldest_ts) from an existing jsonl, for resume."""
    seen = set()
    oldest = None
    if not os.path.exists(path):
        return seen, 0, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            seen.add(r["recommendationid"])
            ts = r["timestamp_created"]
            oldest = ts if oldest is None else min(oldest, ts)
    return seen, len(seen), oldest


def fetch_with_retry(appid, language, cursor):
    """fetch_page with exponential backoff on transient network / HTTP / JSON errors."""
    delay = 2
    for attempt in range(MAX_RETRIES):
        try:
            return fetch_page(appid=appid, language=language, cursor=cursor,
                              purchase_type="all")
        except Exception as exc:              # transient: retry, else re-raise
            if attempt == MAX_RETRIES - 1:
                raise
            print(f"    ! {exc.__class__.__name__}: {exc} — retry in {delay}s")
            time.sleep(delay)
            delay = min(delay * 2, 60)


def deep_collect(appid, language, floor, ckpt):
    short = LANGUAGES[language]
    name = GAMES[appid]["name"]
    key = f"{appid}_{short}"
    path = os.path.join(RAW_DIR, f"{appid}_{short}.jsonl")

    if ckpt.get(key, {}).get("done"):
        s = ckpt[key]
        print(f"{name:<12} {short}: already done "
              f"(kept {s['kept']}, oldest {s['oldest_date']}) — skip")
        return

    fresh = key not in ckpt
    if fresh and os.path.exists(path):
        os.remove(path)   # earlier capped file: re-pull from newest for a clean cursor walk

    seen, kept, oldest = load_existing(path)
    cursor = ckpt.get(key, {}).get("cursor", "*")
    stall = 0

    def record(done, reason):
        ckpt[key] = {
            "done": done, "reason": reason, "cursor": cursor, "kept": kept,
            "oldest_ts": oldest, "oldest_date": as_date(oldest),
        }
        save_checkpoint(ckpt)

    os.makedirs(RAW_DIR, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fout:
        for page in range(MAX_PAGES):
            reviews, next_cursor, _summary = fetch_with_retry(appid, language, cursor)

            if not reviews:                       # empty page: true end of the feed
                record(True, "reached_end")
                break

            new_this_page = 0
            hit_floor = False
            for r in reviews:
                if floor is not None and r["timestamp_created"] < floor:
                    hit_floor = True              # newest-first: rest are older too
                    break
                rid = r["recommendationid"]
                if rid in seen:
                    continue
                seen.add(rid)
                rec = dict(r)
                rec["appid"] = appid
                rec["lang"] = short
                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                kept += 1
                new_this_page += 1
                ts = r["timestamp_created"]
                oldest = ts if oldest is None else min(oldest, ts)
            fout.flush()                          # persist this page's reviews to disk

            if hit_floor:
                record(True, "reached_floor")
                break

            # cursor exhausted? no advance, or a page that added nothing new.
            if next_cursor in (None, cursor) or new_this_page == 0:
                stall += 1
            else:
                stall = 0
            cursor = next_cursor or cursor
            record(False, "in_progress")

            if stall >= STALL_LIMIT:
                record(True, "cursor_stalled")    # honest: could not go deeper
                break
            if (page + 1) % PROGRESS_EVERY == 0:
                print(f"{name:<12} {short}: page {page + 1:>5}  kept {kept:>7}  "
                      f"oldest {as_date(oldest) or '-'}")
            time.sleep(PAGE_PAUSE)
        else:
            record(False, "hit_max_pages")        # ran out of page budget; re-run to continue

    s = ckpt[key]
    reached = floor is not None and oldest is not None and oldest <= floor
    print(f"{name:<12} {short}: STOP [{s['reason']}]  kept {kept}  "
          f"oldest {s['oldest_date']}  reached_floor={reached}")


if __name__ == "__main__":
    ckpt = load_checkpoint()
    for appid in GAMES:
        floor = game_floor(appid)
        print(f"\n=== {GAMES[appid]['name']}  (floor = {as_date(floor) or 'none'}) ===")
        for language in LANGS_TO_DEEPEN:
            deep_collect(appid, language, floor, ckpt)
