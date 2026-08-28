#!/usr/bin/env python3
"""08_build_eval_input.py — join the 247-row answer key to local raw text.

WHAT IT DOES
  The answer key (data/pilot/{pilot_prompt,diagnostic_arm,hardneg_arm}_labels_
  human.jsonl) holds ONLY review_id + human labels, no review text. The full
  text + metadata live in data/raw/{appid}_{lang}.jsonl (gitignored, local
  only). This script joins them into ONE eval file the harness can run on.

  Each output row = {review_id, arm, input{10 parity fields}, gold{...}}.
    - `input`  = EXACTLY the input_schema §2 fields fed to the model.
    - `gold`   = the human label, kept in a SEPARATE key. 09_annotate.py only
                 ever serializes `input` into the model message, so the model
                 never sees `gold`. 10_score.py reads `gold` to grade.

  Output has FULL review text -> written to data/processed/ (gitignored). It is
  NEVER committed and NEVER fed to the model as an example (zero leakage: the
  answer key is the exam, not teaching material).

USAGE
  .venv/bin/python scripts/08_build_eval_input.py
"""
import argparse, glob, hashlib, json, os, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Default to this repository's location, so the same checkout works on ASUS.
# PROJECT_ROOT is only an explicit override for a non-standard deployment.
ROOT = str(Path(os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parent.parent)).expanduser().resolve())
# --keyset selects which frozen human answer keys go into a run package.
#   en247   the original English-side prompt-tuning set (135 + 32 + 80)
#   jazh301 the zh/ja merged arms frozen 2026-08-27 (157 + 144)
#   all548  both, for a single combined package
# They are kept as separate keysets because the 247 rows already have four
# completed DeepSeek runs; re-running them costs money and buys nothing unless
# a drift probe says the model moved.
KEYSETS = {
    "en247": [
        f"{ROOT}/data/pilot/pilot_prompt_labels_human.jsonl",
        f"{ROOT}/data/pilot/diagnostic_arm_labels_human.jsonl",
        f"{ROOT}/data/pilot/hardneg_arm_labels_human.jsonl",
    ],
    "jazh301": [
        f"{ROOT}/data/pilot/merged_arm_zh_labels_human.jsonl",
        f"{ROOT}/data/pilot/merged_arm_ja_labels_human.jsonl",
    ],
}
KEYSETS["all548"] = KEYSETS["en247"] + KEYSETS["jazh301"]
KEY_FILES = KEYSETS["en247"]   # legacy ``main`` default
RAW_GLOB = f"{ROOT}/data/raw/*_[a-z][a-z].jsonl"   # {appid}_{lang}.jsonl only
OUT = f"{ROOT}/data/processed/eval_input_247.jsonl"

# input_schema §2 — the ONLY fields given to human annotators and the model.
PARITY_FIELDS = ["review", "voted_up", "votes_funny", "votes_up",
                 "received_for_free", "steam_purchase", "weighted_vote_score",
                 "written_during_early_access", "appid", "lang"]
GOLD_FIELDS = ["unfair_label", "out_of_scope", "subtype", "procedural_facet",
               "explicitness", "confidence", "borderline", "uncertainty_reason",
               "language", "arm", "keyword_class"]


def load_answer_key(key_files=None):
    rows = {}
    for path in (key_files or KEY_FILES):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                rows[str(r["review_id"])] = r
    return rows


def fast_id(line):
    """Pull recommendationid without a full JSON parse (raw files are huge)."""
    try:
        return line.split('"recommendationid": "', 1)[1].split('"', 1)[0]
    except IndexError:
        return None


# v2 development-run package -------------------------------------------------
# The legacy ``main`` below is intentionally retained for provenance.  New
# calls use this entry point so the model input and answer key are never stored
# in the same file.
RUNS_ROOT = (Path(ROOT) / "data/runs").resolve()
SOURCE_ARM = {
    "pilot_prompt": "pilot_prompt",
    "diagnostic": "diagnostic_arm",
    "hardneg": "hardneg_arm",
}
# zh/ja merged-arm rows get their own `merged_arm_*` provenance names, because
# `hardneg`/`diagnostic` alone would silently collide with the English arms of
# the same name and make per-arm slices unreadable. `hardneg_class1_zh` is a
# registered SEPARATE arm: 64% of its rows are true positives, so folding it
# back into `hardneg` would poison the false-positive denominator
# (decision_log 2026-08-27). `control` is the zh/ja negative-control arm.
MERGED_ARM_LANGS = {"zh", "ja"}
MERGED_ARMS = ["hardneg", "hardneg_class1_zh", "diagnostic", "control"]


def resolve_source_arm(arm, language):
    """Provenance tag for the scope guard: English arms keep their historical
    names so the four 2026-08-2x dev247 runs stay comparable; zh/ja rows are
    namespaced."""
    if language in MERGED_ARM_LANGS:
        return f"merged_arm_{arm}"
    return SOURCE_ARM[arm]


ALL_SOURCE_ARMS = sorted(
    set(SOURCE_ARM.values()) | {f"merged_arm_{a}" for a in MERGED_ARMS})


def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run_dir(run_id):
    directory = (RUNS_ROOT / run_id).resolve()
    if not run_id or Path(run_id).name != run_id or directory.parent != RUNS_ROOT:
        raise ValueError("--run-id must be one simple directory name under data/runs/")
    return directory


def build_development_package():
    parser = argparse.ArgumentParser(
        description="Build separated local input/answer-key files for one development-only run.")
    parser.add_argument("--run-id", required=True,
                        help="new directory name below data/runs/")
    parser.add_argument("--overwrite", action="store_true",
                        help="deliberately replace an existing local package")
    parser.add_argument("--keyset", default="en247", choices=sorted(KEYSETS),
                        help="which frozen human answer keys to package (default en247)")
    args = parser.parse_args()
    run_dir = _run_dir(args.run_id)
    input_path = run_dir / "input.jsonl"
    answer_path = run_dir / "answer_key.jsonl"
    manifest_path = run_dir / "input_build_manifest.json"
    if any(path.exists() for path in (input_path, answer_path, manifest_path)) and not args.overwrite:
        sys.exit("ERROR: run package already exists. Use a new --run-id, or --overwrite only "
                 "after confirming replacement is intended.")

    key = load_answer_key(KEYSETS[args.keyset])
    if not key:
        sys.exit("ERROR: no development answer-key rows were found.")
    unknown_arms = {row.get("arm") for row in key.values()} - set(SOURCE_ARM) - set(MERGED_ARMS)
    if unknown_arms:
        sys.exit(f"ERROR: answer key contains a non-development arm: {sorted(unknown_arms)}")
    print(f"development answer-key rows: {len(key)}  (keyset={args.keyset})")

    found = {}
    for raw_path in sorted(glob.glob(RAW_GLOB)):
        if not os.path.basename(raw_path)[:1].isdigit():
            continue
        with open(raw_path, encoding="utf-8") as handle:
            for line in handle:
                review_id = fast_id(line)
                if review_id in key and review_id not in found:
                    found[review_id] = json.loads(line)
        if len(found) == len(key):
            break
    missing = sorted(set(key) - set(found))
    if missing:
        sys.exit("ERROR: aborting without output because raw text is missing for "
                 f"{len(missing)} development IDs: {missing[:10]}")

    run_dir.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    with open(input_path, "w", encoding="utf-8") as input_out, \
            open(answer_path, "w", encoding="utf-8") as answer_out:
        for review_id in sorted(key, key=int):
            human, raw = key[review_id], found[review_id]
            arm = human["arm"]
            source_arm = resolve_source_arm(arm, human.get("language"))
            model_input = {}
            for field in PARITY_FIELDS:
                value = raw.get(field)
                model_input[field] = str(value) if field == "appid" and value is not None else value
            if list(model_input) != PARITY_FIELDS:
                raise AssertionError("frozen input schema changed unexpectedly")
            input_out.write(json.dumps({
                "review_id": review_id, "arm": arm, "source_arm": source_arm,
                "input": model_input,
            }, ensure_ascii=False) + "\n")
            answer_out.write(json.dumps({
                "review_id": review_id, "arm": arm, "source_arm": source_arm,
                "gold": {field: human.get(field) for field in GOLD_FIELDS},
            }, ensure_ascii=False) + "\n")
            counts[source_arm] += 1

    manifest = {
        "artifact_type": "development_input_package",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": args.run_id,
        "development_only": True,
        "allowed_sources": ALL_SOURCE_ARMS,
        "forbidden_sources": ["gold", "stress", "dev", "train"],
        "input_schema_version": "freeze/input_schema.md §2",
        "input_fields": PARITY_FIELDS,
        "row_count": sum(counts.values()),
        "source_counts": dict(sorted(counts.items())),
        "input_sha256": _sha256_file(input_path),
        "answer_key_sha256": _sha256_file(answer_path),
        "input_contains_human_labels": False,
        "answer_key_contains_review_text": False,
    }
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"wrote {manifest['row_count']} model inputs -> {input_path}")
    print(f"wrote separate text-free answer key -> {answer_path}")
    print("local-only build complete; data/runs/ is gitignored and no API call was made")


def main():
    key = load_answer_key()
    need = set(key)
    print(f"answer key rows: {len(need)}")

    found = {}
    raw_files = sorted(glob.glob(RAW_GLOB))
    # skip lock/temp files like .~foo.xlsx that the glob won't match anyway
    raw_files = [p for p in raw_files if os.path.basename(p)[0].isdigit()]
    for path in raw_files:
        with open(path) as f:
            for line in f:
                rid = fast_id(line)
                if rid is None or rid not in need or rid in found:
                    continue
                found[rid] = json.loads(line)
        if len(found) == len(need):
            break

    missing = need - set(found)
    if missing:
        print(f"WARNING: {len(missing)} ids not found in raw: "
              f"{sorted(missing)[:10]}{'...' if len(missing) > 10 else ''}",
              file=sys.stderr)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    n = 0
    with open(OUT, "w") as out:
        for rid, kr in key.items():
            raw = found.get(rid)
            if raw is None:
                continue
            inp = {}
            for fld in PARITY_FIELDS:
                v = raw.get(fld)
                if fld == "appid" and v is not None:
                    v = str(v)          # prompt example shows appid as string
                inp[fld] = v
            gold = {g: kr.get(g) for g in GOLD_FIELDS}
            out.write(json.dumps(
                {"review_id": rid, "arm": kr.get("arm"),
                 "input": inp, "gold": gold}, ensure_ascii=False) + "\n")
            n += 1
    print(f"wrote {n} rows -> {OUT}")
    print("(gitignored: contains full review text, never committed)")


if __name__ == "__main__":
    build_development_package()
