#!/usr/bin/env python3
"""09_annotate.py — run ONE prompt version over the 247-row eval set.

WHAT IT DOES
  Reads data/processed/eval_input_247.jsonl (built by 08). For each row it
  sends the model:
     system message = the model-facing block of the prompt file
     user message   = json.dumps(row["input"])   # 10 parity fields ONLY
  and stores the model's JSON answer. row["gold"] is NEVER sent.

  The prompt files carry a trailing "不给模型 / 不喂给模型" section (run notes for
  Yifan). This script strips it and sends only the "喂给标注模型" block, so the
  answer key / validation notes never reach the model.

SAFETY GATE (iron rule: estimate cost + confirm before any paid call)
  Default = DRY RUN: prints row count + token/cost estimate, calls NOTHING.
  Add --run to actually hit the API. --limit N runs a tiny smoke test first.

  Same model must be used to tune==freeze==deploy. Record --model exactly.

USAGE
  # 1) estimate only (no network, no cost):
  .venv/bin/python scripts/09_annotate.py --prompt configs/prompts/annotation_prompt_v0.2_draft.md
  # 2) 5-row smoke test after you approve cost:
  .venv/bin/python scripts/09_annotate.py --prompt ... --run --limit 5
  # 3) full run:
  .venv/bin/python scripts/09_annotate.py --prompt ... --run

  Needs DEEPSEEK_API_KEY in .env (gitignored). Override provider with
  --base-url / --env-key for any OpenAI-compatible endpoint.
"""
import json, os, re, sys, time, argparse, urllib.request, urllib.error, hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests

# Default to this repository's location, so the same checkout works on ASUS.
# PROJECT_ROOT is only an explicit override for a non-standard deployment.
ROOT = str(Path(os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parent.parent)).expanduser().resolve())
EVAL_IN = f"{ROOT}/data/processed/eval_input_247.jsonl"


def load_env(path=f"{ROOT}/.env"):
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def extract_system_prompt(md_text):
    """Keep only the block meant for the model: from the '喂给标注模型' heading
    up to (but not including) the trailing '不给模型/不喂给模型' heading."""
    start = re.search(r"^#+.*喂给标注模型.*$", md_text, re.M)
    body = md_text[start.end():] if start else md_text
    end = re.search(r"^#+.*(不给模型|不喂给模型).*$", body, re.M)
    if end:
        body = body[:end.start()]
    return body.strip()


def est_tokens(s):
    """Rough token estimate for mixed CJK/EN text (~3.5 chars/token)."""
    return max(1, int(len(s) / 3.5))


def call_api(base_url, api_key, model, system, user, json_mode, temperature,
             timeout=90, retries=3):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    data = json.dumps(payload).encode()
    url = base_url.rstrip("/") + "/chat/completions"
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, data=data,
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {api_key}"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode())
            content = body["choices"][0]["message"]["content"]
            usage = body.get("usage", {})
            return content, usage
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode()[:300]}"
        except Exception as e:                        # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"API failed after {retries} tries: {last}")


def parse_json_answer(text):
    """Model must return one JSON object; tolerate stray code fences / prose."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?|```$", "", t).strip()
    try:
        return json.loads(t), None
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", t, re.S)
        if m:
            try:
                return json.loads(m.group()), None
            except json.JSONDecodeError as e:
                return None, str(e)
        return None, "no JSON object found"


# v2 condition runner --------------------------------------------------------
# The legacy functions and ``main`` below are retained for provenance.  This
# entry point makes the JSON condition executable and physically never opens an
# answer-key file.
C_ROOT = Path(ROOT)
C_RUNS_ROOT = (C_ROOT / "data/runs").resolve()
C_INPUT_FIELDS = ["review", "voted_up", "votes_funny", "votes_up",
                  "received_for_free", "steam_purchase", "weighted_vote_score",
                  "written_during_early_access", "appid", "lang"]
C_OUTPUT_FIELDS = {"unfair_label", "out_of_scope", "subtype", "procedural_facet",
                   "evidence_span", "normalized_claim", "explicitness", "confidence",
                   "borderline", "uncertainty_reason", "annotator_note"}
C_SUBTYPES = {"distributive", "procedural"}
C_FACETS = {"cheating_governance", "sanction", "access_exclusion",
            "competitive_balance", "unfair_by_design"}
C_REASONS = {"attribution_unclear", "irony_undecidable", "price_boundary",
             "technical_access_boundary", "toxicity_attribution", "language_cue",
             "facet_boundary"}
C_PARSER_VERSION = "strict-json-schema-v1"


def c_now():
    return datetime.now(timezone.utc).isoformat()


def c_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def c_load_json(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read JSON file {path}: {exc}") from exc


def c_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON at {path}:{line_number}: {exc}") from exc


def c_prompt(markdown):
    start = re.search(r"^#+.*喂给标注模型.*$", markdown, re.M)
    if not start:
        raise ValueError("Prompt needs a heading containing '喂给标注模型'.")
    body = markdown[start.end():]
    end = re.search(r"^#+.*(不给模型|不喂给模型).*$", body, re.M)
    if not end:
        raise ValueError("Prompt needs a trailing heading containing '不给模型' or '不喂给模型'.")
    system = body[:end.start()].strip()
    if len(system) < 400 or "JSON" not in system.upper():
        raise ValueError("Extracted system prompt is implausibly short or lacks a JSON instruction.")
    return system


def c_validate_config(config):
    required = {"condition_id", "provider", "model", "generation", "transport",
                "prompt", "io", "scope_guard", "run_record", "pricing"}
    missing = required - set(config)
    if missing or config.get("schema_version") != "1.1":
        raise ValueError(f"Unsupported condition JSON (missing={sorted(missing)}, schema={config.get('schema_version')!r})")
    generation = config["generation"]
    if generation.get("stream") is not False or generation.get("response_format", {}).get("type") != "json_object":
        raise ValueError("Condition must set stream=false and response_format.type=json_object.")
    if config["provider"].get("api_compatibility") != "openai_chat_completions":
        raise ValueError("Only an OpenAI-compatible chat-completions condition is supported.")
    if config["transport"].get("retry", {}).get("max_attempts", 0) < 1:
        raise ValueError("transport.retry.max_attempts must be at least 1.")
    expected_models = config["model"].get("accepted_returned_model_ids")
    if not isinstance(expected_models, list) or not expected_models or not all(isinstance(item, str) for item in expected_models):
        raise ValueError("model.accepted_returned_model_ids must be a non-empty list of strings.")


def c_validate_rows(rows, guard):
    allowed, forbidden, seen = set(guard["allowed_sources"]), set(guard["forbidden_sources"]), set()
    for index, row in enumerate(rows, 1):
        if set(row) != {"review_id", "arm", "source_arm", "input"}:
            raise ValueError(f"Row {index} has an unsafe structure: answer key or provenance fields are not allowed.")
        review_id = str(row["review_id"])
        if review_id in seen:
            raise ValueError(f"Duplicate review_id in input package: {review_id}")
        seen.add(review_id)
        if row["source_arm"] in forbidden or row["source_arm"] not in allowed:
            raise ValueError(f"Blocked source_arm for {review_id}: {row['source_arm']!r}")
        if not isinstance(row["input"], dict) or list(row["input"]) != C_INPUT_FIELDS:
            raise ValueError(f"Input schema mismatch for {review_id}; only the 10 frozen fields may be sent.")
    if not rows:
        raise ValueError("Input package is empty.")


def c_validate_answer(answer, review):
    """Validate controlled fields, including the review-text-only span rule."""
    if not isinstance(answer, dict):
        return ["not_json_object"]
    if set(answer) != C_OUTPUT_FIELDS:
        return ["output_keys_mismatch"]
    violations = []
    label, oos = answer["unfair_label"], answer["out_of_scope"]
    subtype, facet = answer["subtype"], answer["procedural_facet"]
    evidence, claim = answer["evidence_span"], answer["normalized_claim"]
    explicitness, confidence = answer["explicitness"], answer["confidence"]
    borderline, reason = answer["borderline"], answer["uncertainty_reason"]
    if label not in {"PRESENT", "ABSENT", "NA"}:
        violations.append("invalid_unfair_label")
    if not isinstance(oos, bool) or (label == "NA") != oos:
        violations.append("NA_out_of_scope_mismatch")
    if not isinstance(subtype, list) or len(subtype) != len(set(subtype)) or set(subtype) - C_SUBTYPES:
        violations.append("invalid_subtype")
    if not isinstance(facet, list) or len(facet) != len(set(facet)) or set(facet) - C_FACETS:
        violations.append("invalid_procedural_facet")
    if explicitness not in {"explicit", "implicit", None}:
        violations.append("invalid_explicitness")
    if confidence not in {"high", "medium", "low"}:
        violations.append("invalid_confidence")
    if not isinstance(borderline, bool) or borderline != (confidence == "low"):
        violations.append("borderline_confidence_mismatch")
    if not all(isinstance(value, str) for value in (evidence, claim, reason, answer["annotator_note"])):
        violations.append("nonstring_text_field")
    reasons = reason.split(";") if isinstance(reason, str) and reason else []
    if (not isinstance(reason, str) or (not borderline and reason) or
            (borderline and (not reasons or set(reasons) - C_REASONS))):
        violations.append("invalid_uncertainty_reason")
    if label == "PRESENT":
        if not subtype:
            violations.append("PRESENT_missing_subtype")
        if not evidence or not claim:
            violations.append("PRESENT_missing_evidence_or_claim")
        if explicitness not in {"explicit", "implicit"}:
            violations.append("PRESENT_invalid_explicitness")
        if "procedural" in subtype and not facet:
            violations.append("procedural_missing_facet")
        if "procedural" not in subtype and facet:
            violations.append("facet_without_procedural")
        if isinstance(evidence, str):
            if len(evidence) > 200:
                violations.append("evidence_span_over_200_chars")
            if not evidence or any(piece not in review for piece in evidence.split(" […] ")):
                violations.append("evidence_span_not_verbatim_review_text")
    elif label in {"ABSENT", "NA"}:
        if subtype or facet or evidence or explicitness is not None:
            violations.append("nonPRESENT_fields_not_empty")
        if label == "NA" and claim:
            violations.append("NA_claim_not_empty")
        if label == "ABSENT" and ((borderline and not claim) or (not borderline and claim)):
            violations.append("ABSENT_claim_rule")
    return violations


def c_call(config, api_key, system, user_message, review_id, raw_out):
    generation, transport = config["generation"], config["transport"]
    retry = transport["retry"]
    payload = {
        "model": config["model"]["id"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_message}],
        "temperature": generation["temperature"], "top_p": generation["top_p"],
        "max_tokens": generation["max_tokens"], "stream": False,
        "response_format": generation["response_format"],
    }
    if generation.get("thinking") is not None:
        payload["thinking"] = generation["thinking"]
    connect = float(transport["connect_timeout_seconds"])
    read = min(float(transport["read_timeout_seconds"]), float(transport["overall_timeout_seconds"]) - connect)
    if read <= 0:
        raise ValueError("overall_timeout_seconds must exceed connect_timeout_seconds")
    url = config["provider"]["base_url"].rstrip("/") + config["provider"]["chat_completions_path"]
    transient_status = {429, 500, 502, 503, 504}
    backoff = retry.get("backoff_seconds", [])
    for attempt in range(1, int(retry["max_attempts"]) + 1):
        started = time.monotonic()
        try:
            response = requests.post(url, json=payload, headers={
                "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                timeout=(connect, read))
            try:
                body = response.json()
            except ValueError:
                body = {"_non_json_body": response.text[:4000]}
            raw_out.write(json.dumps({"review_id": review_id, "attempt": attempt,
                "event": "http_response", "received_at": c_now(),
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "status_code": response.status_code, "body": body}, ensure_ascii=False) + "\n")
            raw_out.flush()
            if response.status_code >= 400:
                if response.status_code not in transient_status or attempt == int(retry["max_attempts"]):
                    return {"ok": False, "attempts": attempt, "error": f"HTTP_{response.status_code}"}
            elif not isinstance(body, dict) or not body.get("choices"):
                return {"ok": False, "attempts": attempt, "error": "invalid_provider_envelope"}
            else:
                content = body["choices"][0].get("message", {}).get("content")
                # Empty/invalid JSON are recorded failures, not retried: retrying them would hide a model defect.
                if not isinstance(content, str) or not content.strip():
                    return {"ok": False, "attempts": attempt, "error": "empty_content", "body": body}
                return {"ok": True, "attempts": attempt, "body": body, "content": content}
        except (requests.ConnectionError, requests.Timeout) as exc:
            raw_out.write(json.dumps({"review_id": review_id, "attempt": attempt,
                "event": "transport_error", "received_at": c_now(),
                "error_type": type(exc).__name__, "detail": str(exc)[:500]}, ensure_ascii=False) + "\n")
            raw_out.flush()
            if attempt == int(retry["max_attempts"]):
                return {"ok": False, "attempts": attempt, "error": f"{type(exc).__name__}:{exc}"}
        if attempt < int(retry["max_attempts"]):
            time.sleep(float(backoff[min(attempt - 1, len(backoff) - 1)]) if backoff else 0)
    raise AssertionError("unreachable retry exit")


def c_write_manifest(path, manifest):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def condition_main():
    parser = argparse.ArgumentParser(description="Run one auditable DeepSeek development condition.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-dir", required=True, help="existing data/runs/<run-id> directory")
    parser.add_argument("--run", action="store_true", help="make paid API calls; default is dry-run")
    parser.add_argument("--limit", type=int, default=0, help="first N rows only; zero means all")
    parser.add_argument("--resume", action="store_true", help="only resume a manifest-identical interrupted run")
    args = parser.parse_args()
    config_path = Path(args.config).expanduser().resolve()
    config = c_load_json(config_path)
    c_validate_config(config)
    run_dir = Path(args.run_dir).expanduser().resolve()
    if run_dir.parent != C_RUNS_ROOT:
        sys.exit("ERROR: --run-dir must be one direct child of data/runs/")
    input_path = run_dir / "input.jsonl"
    if not input_path.exists():
        sys.exit("ERROR: input.jsonl is missing. Build this development package with 08 first.")
    rows = list(c_jsonl(input_path))
    c_validate_rows(rows, config["scope_guard"])
    if args.limit < 0:
        sys.exit("ERROR: --limit must be zero or positive")
    if args.limit:
        rows = rows[:args.limit]
    prompt_path = (C_ROOT / config["prompt"]["path"]).resolve()
    if C_ROOT not in prompt_path.parents or not prompt_path.exists():
        sys.exit("ERROR: configured prompt is missing or outside the repository.")
    prompt_sha, system = c_sha256(prompt_path), c_prompt(prompt_path.read_text(encoding="utf-8"))
    pinned_sha = config["prompt"].get("sha256", "")
    if pinned_sha not in {"", "TO_BE_FILLED_WHEN_FROZEN", prompt_sha}:
        sys.exit("ERROR: prompt SHA differs from the condition JSON; make a new condition or deliberately freeze it.")
    input_sha = c_sha256(input_path)
    ids_sha = hashlib.sha256("\n".join(str(row["review_id"]) for row in rows).encode()).hexdigest()
    in_tokens = sum(max(1, int(len(system) / 3.5)) + max(1, int(len(json.dumps(row["input"], ensure_ascii=False)) / 3.5)) for row in rows)
    out_tokens = int(config["pricing"]["estimate_output_tokens_per_review"]) * len(rows)
    prices = config["pricing"]["usd_per_million_tokens"]
    cost = in_tokens / 1e6 * prices["input_cache_miss_peak"] + out_tokens / 1e6 * prices["output_peak"]
    print(f"condition: {config['condition_id']}\nmodel: {config['model']['id']}\nrows: {len(rows)} development-only")
    print(f"prompt SHA: {prompt_sha}\nestimate: ~{in_tokens:,} input + ~{out_tokens:,} output tokens; ceiling ~${cost:.4f}")
    if not args.run:
        print("DRY RUN — no API key read, no network request, and no file written.")
        return

    env = load_env()
    key_name = config["provider"]["api_key_env"]
    api_key = os.environ.get(key_name) or env.get(key_name)
    if not api_key:
        sys.exit(f"ERROR: {key_name} is missing from .env or environment.")
    manifest_path, raw_path, response_path = run_dir / "manifest.json", run_dir / "raw_responses.jsonl", run_dir / "responses.jsonl"
    static = {"condition_id": config["condition_id"], "config_sha256": c_sha256(config_path),
              "prompt_file_sha256": prompt_sha, "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
              "model_requested": config["model"]["id"], "base_url": config["provider"]["base_url"],
              "generation": config["generation"], "input_schema_version": "freeze/input_schema.md §2",
              "parser_version": C_PARSER_VERSION, "input_sha256": input_sha,
              "selected_ids_sha256": ids_sha, "rows_selected": len(rows)}
    if manifest_path.exists():
        if not args.resume:
            sys.exit("ERROR: manifest exists. Use a new run directory, or --resume only for the same interrupted condition.")
        manifest = c_load_json(manifest_path)
        if any(manifest.get(key) != value for key, value in static.items()):
            sys.exit("ERROR: cannot resume because config/prompt/input/selection differs from the existing manifest.")
        done = {str(row["review_id"]) for row in c_jsonl(response_path)} if response_path.exists() else set()
    else:
        if args.resume:
            sys.exit("ERROR: --resume supplied but manifest does not exist.")
        done = set()
        manifest = {**static, "started_at": c_now(), "status": "running", "development_only": True,
                    "model_returned_values": [], "system_fingerprint_values": [], "completed_rows": 0,
                    "api_error_rows": 0, "parse_error_rows": 0, "schema_invalid_rows": 0}
        c_write_manifest(manifest_path, manifest)
    models, fingerprints, drift = set(manifest["model_returned_values"]), set(manifest["system_fingerprint_values"]), False
    accepted_returned_models = set(config["model"]["accepted_returned_model_ids"])
    with open(raw_path, "a", encoding="utf-8") as raw_out, open(response_path, "a", encoding="utf-8") as response_out:
        for index, row in enumerate(rows, 1):
            review_id = str(row["review_id"])
            if review_id in done:
                continue
            result = c_call(config, api_key, system, json.dumps(row["input"], ensure_ascii=False), review_id, raw_out)
            record = {"review_id": review_id, "arm": row["arm"], "source_arm": row["source_arm"],
                      "condition_id": config["condition_id"], "model_requested": config["model"]["id"],
                      "attempt_count": result["attempts"], "completed_at": c_now(), "parsed": None,
                      "parse_error": None, "validation_errors": [], "usage": {}, "model_returned": None,
                      "system_fingerprint": None, "finish_reason": None}
            if not result["ok"]:
                record["parse_error"] = f"api_error:{result['error']}"; manifest["api_error_rows"] += 1
            else:
                body = result["body"]
                record.update({"model_returned": body.get("model"), "system_fingerprint": body.get("system_fingerprint"),
                               "usage": body.get("usage", {}), "finish_reason": body["choices"][0].get("finish_reason")})
                if not record["model_returned"]:
                    record["parse_error"] = "condition_drift:provider_response_missing_model"; manifest["api_error_rows"] += 1; drift = True
                elif record["model_returned"] not in accepted_returned_models:
                    record["parse_error"] = "condition_drift:returned_model_does_not_match_condition"; manifest["api_error_rows"] += 1; drift = True
                else:
                    models.add(record["model_returned"])
                if record["system_fingerprint"]: fingerprints.add(record["system_fingerprint"])
                if drift or len(models) > 1 or len(fingerprints) > 1:
                    record["parse_error"] = "condition_drift:returned_model_or_system_fingerprint_changed"; manifest["api_error_rows"] += 1; drift = True
                else:
                    try:
                        record["parsed"] = json.loads(result["content"])
                    except json.JSONDecodeError as exc:
                        record["parse_error"] = f"invalid_json:{exc.msg} at char {exc.pos}"; manifest["parse_error_rows"] += 1
                    if record["parse_error"] is None:
                        record["validation_errors"] = c_validate_answer(record["parsed"], row["input"]["review"])
                        manifest["schema_invalid_rows"] += bool(record["validation_errors"])
            response_out.write(json.dumps(record, ensure_ascii=False) + "\n"); response_out.flush()
            manifest["completed_rows"] += 1
            manifest["model_returned_values"], manifest["system_fingerprint_values"] = sorted(models), sorted(fingerprints)
            c_write_manifest(manifest_path, manifest)
            if drift:
                print("ERROR: provider condition drift detected; no further reviews will be sent.", file=sys.stderr); break
            if index % 20 == 0:
                print(f"  {index}/{len(rows)} requests recorded")
    manifest["finished_at"], manifest["status"] = c_now(), "halted_condition_drift" if drift else "completed"
    c_write_manifest(manifest_path, manifest)
    print(f"run status: {manifest['status']} -> {response_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="prompt .md file")
    ap.add_argument("--run", action="store_true", help="actually call the API")
    ap.add_argument("--limit", type=int, default=0, help="only first N rows")
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--base-url", default="https://api.deepseek.com")
    ap.add_argument("--env-key", default="DEEPSEEK_API_KEY")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--no-json-mode", action="store_true")
    # DeepSeek list price (USD / 1M tok). VERIFY current pricing before trusting.
    ap.add_argument("--price-in", type=float, default=0.27)
    ap.add_argument("--price-out", type=float, default=1.10)
    ap.add_argument("--est-out-tokens", type=int, default=180,
                    help="assumed output tokens/row for the estimate")
    args = ap.parse_args()

    system = extract_system_prompt(open(args.prompt).read())
    if len(system) < 400:
        sys.exit(f"ERROR: extracted system prompt too short ({len(system)} "
                 f"chars) — check the '喂给标注模型' heading in {args.prompt}")

    rows = [json.loads(l) for l in open(EVAL_IN) if l.strip()]
    if args.limit:
        rows = rows[:args.limit]

    sys_tok = est_tokens(system)
    in_tok = sum(sys_tok + est_tokens(json.dumps(r["input"], ensure_ascii=False))
                 for r in rows)
    out_tok = args.est_out_tokens * len(rows)
    cost = in_tok / 1e6 * args.price_in + out_tok / 1e6 * args.price_out

    ver = re.search(r"v\d+\.\d+", os.path.basename(args.prompt))
    ver = ver.group() if ver else "vX"
    tag = f"{ver}_{args.model}".replace("/", "-")
    out_path = f"{ROOT}/data/processed/pred_{tag}.jsonl"

    print(f"prompt      : {args.prompt}  ({ver})")
    print(f"system chars: {len(system)}  (~{sys_tok} tok)")
    print(f"rows        : {len(rows)}")
    print(f"model       : {args.model} @ {args.base_url}")
    print(f"est tokens  : in ~{in_tok:,}  out ~{out_tok:,}")
    print(f"est cost    : ~${cost:.4f}  "
          f"(@ ${args.price_in}/${args.price_out} per 1M in/out — VERIFY price)")
    print(f"output file : {out_path}")

    if not args.run:
        print("\nDRY RUN — no API call made. Re-run with --run to execute.")
        return

    env = load_env()
    api_key = env.get(args.env_key) or os.environ.get(args.env_key)
    if not api_key:
        sys.exit(f"ERROR: {args.env_key} not found in .env or environment.")

    done = set()
    if os.path.exists(out_path):
        for l in open(out_path):
            if l.strip():
                done.add(json.loads(l)["review_id"])
        print(f"resuming: {len(done)} rows already done, skipping them.")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ok = err = 0
    with open(out_path, "a") as out:
        for i, r in enumerate(rows, 1):
            rid = r["review_id"]
            if rid in done:
                continue
            user = json.dumps(r["input"], ensure_ascii=False)
            try:
                content, usage = call_api(
                    args.base_url, api_key, args.model, system, user,
                    json_mode=not args.no_json_mode,
                    temperature=args.temperature)
            except RuntimeError as e:
                print(f"[{i}/{len(rows)}] {rid} FAILED: {e}", file=sys.stderr)
                err += 1
                continue
            parsed, perr = parse_json_answer(content)
            out.write(json.dumps({
                "review_id": rid, "arm": r["arm"], "model": args.model,
                "prompt_version": ver, "parsed": parsed,
                "parse_error": perr, "raw_response": content,
                "usage": usage}, ensure_ascii=False) + "\n")
            out.flush()
            ok += 1
            if perr:
                err += 1
            if i % 20 == 0:
                print(f"  {i}/{len(rows)} done (ok={ok}, parse_err={err})")
    print(f"\nDONE. wrote {ok} predictions ({err} parse errors) -> {out_path}")


if __name__ == "__main__":
    condition_main()
