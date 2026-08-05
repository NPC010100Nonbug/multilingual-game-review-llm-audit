"""
00_probe_counts.py — a diagnostic probe, run BEFORE the real collector.

Question we're answering: the store page shows one number of reviews per
language, but the API (with its default purchase_type="steam") returned a
smaller one (e.g. Japanese CS2: store 11,262 vs API 6,767). Is `purchase_type`
the lever? This probe holds everything else constant and varies ONLY
purchase_type ("steam" vs "all"), then prints total_reviews side by side so we
can SEE the difference instead of guessing.

It does NOT save any reviews — it only reads query_summary totals. Cheap.
"""

import time

from importlib import import_module

# reuse fetch_page from 01_collect.py (same folder)
fetch_page = import_module("01_collect").fetch_page

GAMES = {
    "CS2 (730)": 730,
    "BF2042 (1517290)": 1517290,
    "Elden Ring (1245620)": 1245620,
}
LANGUAGES = ["schinese", "english", "japanese"]
PURCHASE_TYPES = ["steam", "all"]

SLEEP_SECONDS = 1.0  # be polite: pause between API calls


def total_reviews(appid, language, purchase_type):
    """Read just the query_summary total for one game/language/purchase_type."""
    # num_per_page=1: we only want the summary, not the reviews themselves.
    _reviews, _cursor, summary = fetch_page(
        appid=appid,
        language=language,
        num_per_page=1,
        purchase_type=purchase_type,
    )
    return summary.get("total_reviews")


if __name__ == "__main__":
    # header
    print(f"{'game':<22}{'lang':<10}{'steam':>10}{'all':>10}{'all/steam':>12}")
    print("-" * 64)

    for game_name, appid in GAMES.items():
        for language in LANGUAGES:
            counts = {}
            for ptype in PURCHASE_TYPES:
                counts[ptype] = total_reviews(appid, language, ptype)
                time.sleep(SLEEP_SECONDS)
            steam_n = counts["steam"] or 0
            all_n = counts["all"] or 0
            ratio = f"{all_n / steam_n:.2f}x" if steam_n else "-"
            print(f"{game_name:<22}{language:<10}{steam_n:>10}{all_n:>10}{ratio:>12}")
