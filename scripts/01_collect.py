"""
01_collect.py — fetch Steam public reviews (Phase 2).

v3 (this version): time-window-aware collector.
  - For each game, collect ALL Japanese reviews first (Japanese is the sparse,
    binding language). Its oldest kept review defines the game's time `floor`.
  - Then collect English / Chinese back to that same `floor` (early-stop as soon
    as a review older than the floor appears, since filter=recent is newest-first),
    capped at CAP_PER_LANG so the densest cell (CS2/en) can't page forever.
  - This makes the three languages share a comparable time window, so later
    cross-lingual comparisons aren't confounded by time. (Residual limit: CS2/en
    is so dense it still can't reach the JA 2023 floor within the cap.)
  - Uses purchase_type="all" (decision_log 2026-08-05); CS2 also drops pre-launch
    CS:GO reviews via the game-level min_timestamp.

data/raw/ is gitignored: raw texts stay on this machine only.
Downstream (Phase 3+) does the stratified monthly down-sampling toward the JA count.
"""

import json
import os
import time

import requests

BASE_URL = "https://store.steampowered.com/appreviews/{appid}"

# Steam's language codes -> our short codes (used later when we build reviews.csv)
LANGUAGES = {"schinese": "zh", "english": "en", "japanese": "ja"}

# Games to collect. min_timestamp (unix seconds) is a hard construct floor applied
# to ALL languages; None means no floor. CS2 (730) drops pre-CS2 CS:GO reviews.
GAMES = {
    730: {"name": "CS2", "min_timestamp": 1695772800},      # 2023-09-27 CS2 launch
    1517290: {"name": "BF2042", "min_timestamp": None},
    1245620: {"name": "Elden Ring", "min_timestamp": None},
}

JA_TARGET = 10000          # big enough to pull ALL Japanese for each game
CAP_PER_LANG = 15000       # safety cap for EN/ZH so CS2/en can't page forever
PAGE_PAUSE = 0.8           # seconds between API calls (be polite)
MAX_PAGES = 400            # hard safety cap on pages per (game, language)

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def fetch_page(appid, language, cursor="*", num_per_page=100, purchase_type="steam"):
    """Fetch ONE page of reviews from the Steam public reviews API.

    purchase_type: "steam" (default; only Steam-store purchases),
      "non_steam_purchase" (keys / retail), or "all" (both). Steam's own
      default is "steam", so leaving this alone keeps the earlier behavior.

    Returns a tuple (reviews, next_cursor, summary):
      reviews     : list of review dicts (can be empty on the last page)
      next_cursor : cursor string to send as `cursor` for the NEXT page
      summary     : the query_summary dict (per-language totals)
    """
    url = BASE_URL.format(appid=appid)
    params = {
        "json": 1,
        "language": language,
        "filter": "recent",
        "num_per_page": num_per_page,
        "cursor": cursor,           # "*" for the first page; requests URL-encodes it
        "purchase_type": purchase_type,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()          # raise on HTTP errors (e.g. 429 rate-limit, 500)
    data = resp.json()
    if data.get("success") != 1:
        raise RuntimeError(f"API did not return success=1: {data}")
    return data["reviews"], data.get("cursor"), data.get("query_summary", {})


def collect_language(appid, language, target, min_keep_ts):
    """Paginate one game+language, newest-first, returning up to `target` reviews.

    min_keep_ts: keep only reviews with timestamp_created >= this. Because the
    feed is newest-first, the FIRST review older than it means we've passed the
    window's edge, so we stop the whole loop (no point paging into older reviews).

    Stops when: target reached, a review older than min_keep_ts appears, the API
    returns an empty page, or the cursor stops advancing.
    """
    kept = []
    seen_ids = set()          # dedup guard: recommendationid should be unique
    cursor = "*"

    for _page in range(MAX_PAGES):
        reviews, next_cursor, _summary = fetch_page(
            appid=appid,
            language=language,
            cursor=cursor,
            purchase_type="all",
        )
        if not reviews:                       # empty page -> reached the end
            break

        for r in reviews:
            if min_keep_ts is not None and r["timestamp_created"] < min_keep_ts:
                return kept                   # newest-first: rest are older, done
            rid = r["recommendationid"]
            if rid in seen_ids:
                continue
            seen_ids.add(rid)
            kept.append(r)
            if len(kept) >= target:
                return kept

        if next_cursor is None or next_cursor == cursor:   # cursor didn't advance
            break
        cursor = next_cursor
        time.sleep(PAGE_PAUSE)

    return kept


def save_jsonl(appid, lang_short, reviews):
    """Write reviews to data/raw/{appid}_{lang}.jsonl, one JSON object per line."""
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, f"{appid}_{lang_short}.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in reviews:
            record = dict(r)                  # copy so we don't mutate the original
            record["appid"] = appid
            record["lang"] = lang_short
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


if __name__ == "__main__":
    for appid, meta in GAMES.items():
        construct_floor = meta["min_timestamp"]   # None or a hard floor (CS2)

        # 1) Japanese first, in full — it defines this game's time window.
        ja = collect_language(appid, "japanese", target=JA_TARGET,
                              min_keep_ts=construct_floor)
        save_jsonl(appid, "ja", ja)
        ja_floor = min((r["timestamp_created"] for r in ja), default=construct_floor)
        print(f"{meta['name']:<12} ja: kept {len(ja):>5}  (floor set from Japanese)")

        # 2) English + Chinese, back to the Japanese floor (capped).
        for steam_lang in ("english", "schinese"):
            short = LANGUAGES[steam_lang]
            revs = collect_language(appid, steam_lang, target=CAP_PER_LANG,
                                   min_keep_ts=ja_floor)
            save_jsonl(appid, short, revs)
            print(f"{meta['name']:<12} {short}: kept {len(revs):>5}")
