# DeepSeek model configuration

`deepseek_v4_pro.json` is the reusable **draft calibration condition** for the official DeepSeek API. It is intentionally separate from Codex's own model settings: it is read by a future annotation runner, not by the Codex desktop app itself.

## 1. Keep the key out of the repository

Copy the example file once, then place the real key only in the ignored `.env` file:

```sh
cd ~/Documents/multilingual-game-review-llm-audit
cp .env.example .env
# Edit .env locally and set DEEPSEEK_API_KEY to the key from DeepSeek Platform.
```

For the current terminal session, load it without printing it:

```sh
set -a
source .env
set +a
test -n "$DEEPSEEK_API_KEY" && echo "DEEPSEEK_API_KEY is set"
```

Alternatively, set it only for one session (it disappears when that terminal closes):

```sh
export DEEPSEEK_API_KEY='paste-your-key-here'
```

Never commit `.env`, paste a live key into a prompt, or put it in this JSON file. The repository's `.gitignore` already excludes `.env`.

## 2. What the condition fixes

- Official OpenAI-compatible API base URL: `https://api.deepseek.com`
- Requested model: `deepseek-v4-pro`
- Prompt: `configs/prompts/annotation_prompt_v0.2_draft.md`
- Deterministic decoding baseline: `temperature: 0.0`, `top_p: 1.0`, `max_tokens: 1200`, with DeepSeek thinking explicitly disabled. This is a supported DeepSeek OpenAI-format request field, not an Anthropic-only field.
- Structured output: `response_format: {"type": "json_object"}`; the prompt itself also requires one JSON object.

The model name returned in each response must be written to `manifest.json` and must equal one of `model.accepted_returned_model_ids` in the condition. Otherwise the runner stops before sending another review. A change in returned model version, thinking mode, prompt hash, decoding settings, preprocessing, or parser is a new measurement condition—not a continuation of a comparable run.

## 3. Safe run contract for the future runner

Before any paid call, estimate cost and obtain Yifan's confirmation. Build a de-identified input JSONL containing only the fields permitted by `freeze/input_schema.md`, one review per line. Do not include author data, human labels, `provenance`, curated/seed fields, or any gold/stress text.

Use a fresh run directory such as:

```text
data/runs/2026-08-19_deepseek-v4-pro_v0.2-dev/
  input.jsonl
  raw_responses.jsonl
  responses.jsonl
  manifest.json
```

The guard in the configuration permits only `pilot_prompt`, `diagnostic_arm`, and `hardneg_arm`. It explicitly blocks `gold`, `stress`, `dev`, and `train`; do not weaken this guard while the prompt is still a draft.

## 4. Minimal preflight for an eventual runner

```sh
cd ~/Documents/multilingual-game-review-llm-audit
set -a; source .env; set +a
test -n "$DEEPSEEK_API_KEY" || { echo "DEEPSEEK_API_KEY is missing"; exit 1; }
python -m json.tool configs/models/deepseek_v4_pro.json >/dev/null
# Next: run the project's dedicated annotation runner with this config and an approved development-only input JSONL.
```

This document deliberately contains no generic API call. Use this configuration only through a reviewed annotation runner, and obtain cost approval before a paid or batch request. The runner should accept `--config configs/models/deepseek_v4_pro.json`, reject forbidden inputs before sending data, log raw responses, and validate JSON before producing labels.
