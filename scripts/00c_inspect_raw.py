"""
00c_inspect_raw.py — sanity-check the collected raw files (no API calls).

For every data/raw/*.jsonl it prints: number of reviews, and the oldest /
newest review-creation date. We use it here to explain why CS2 japanese
stopped at ~1943: if the oldest kept date is close to the CS2 launch
(2023-09-27) the date filter is the reason; if it's much later, Steam's
recent-pagination cap is.
"""

import glob
import json
import os
from datetime import datetime, timezone

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def as_date(unix_seconds):
    return datetime.fromtimestamp(unix_seconds, tz=timezone.utc).strftime("%Y-%m-%d")


if __name__ == "__main__":
    print(f"{'file':<24}{'n':>7}{'oldest':>14}{'newest':>14}")
    print("-" * 59)
    for path in sorted(glob.glob(os.path.join(RAW_DIR, "*.jsonl"))):
        timestamps = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                timestamps.append(r["timestamp_created"])
        name = os.path.basename(path)
        if timestamps:
            print(f"{name:<24}{len(timestamps):>7}{as_date(min(timestamps)):>14}{as_date(max(timestamps)):>14}")
        else:
            print(f"{name:<24}{0:>7}{'-':>14}{'-':>14}")
