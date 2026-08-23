#!/usr/bin/env python3
"""10_score.py — grade one or two prediction files against the answer key.

WHAT IT DOES
  Joins model predictions (from 09) with the human gold labels (from 08) and
  reports the metrics this audit actually cares about:
    - JSON parse rate (did the model return valid JSON at all)
    - 3-class PRESENT/ABSENT/NA accuracy + Cohen's kappa + confusion matrix
    - PRESENT precision / recall / F1
    - *** per-language recall / false-positive rate / kappa, for EN, JA and ZH ***
      plus the cross-language kappa gap the pre-registration bounds at 0.15.
      English alone was measured until 2026-08-23; a project whose claim is a
      three-way comparison cannot report one language and call it a result.
    - *** hard-negative false-positive rate ***, strict denominator: human
      ABSENT rows only.  The hardneg arm is keyword-selected, so some of its
      rows really are PRESENT; scoring those as false positives overstated the
      rate (that is what produced the wrong 14/80 figure).
    - subtype / procedural_facet agreement on rows both sides call PRESENT
    - output-constraint legality violations (the 6 hard constraints)
  Pass two or more --pred files for a side-by-side comparison.

  Rows where the model produced no usable label are reported as NO_LABEL, never
  folded into "NA".  "NA" is a judgment; NO_LABEL is a measurement failure.

USAGE
  .venv/bin/python scripts/10_score.py --pred data/runs/<run>/responses.jsonl
  .venv/bin/python scripts/10_score.py --pred <runA>/responses.jsonl --pred <runB>/responses.jsonl
"""
import json, argparse, os, hashlib, math, random
from collections import Counter, defaultdict
from pathlib import Path

# Default to this repository's location, so the same checkout works on ASUS.
# PROJECT_ROOT is only an explicit override for a non-standard deployment.
ROOT = str(Path(os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parent.parent)).expanduser().resolve())
EVAL_IN = f"{ROOT}/data/processed/eval_input_247.jsonl"
LABELS = ["PRESENT", "ABSENT", "NA"]

# A row where the model produced no usable label at all (no response row, an
# unparseable response, or a parsed object whose unfair_label is not one of
# LABELS).  This is NOT the same as the model deliberately answering "NA":
# "NA" is a substantive judgment ("out of scope"), NO_LABEL is a measurement
# failure.  Folding the second into the first inflates NA agreement and hides
# plumbing problems inside a content metric, so they are kept apart everywhere.
NO_LABEL = "NO_LABEL"
CONFUSION_COLS = LABELS + [NO_LABEL]

REPORT_LANGS = ("en", "ja", "zh")

# 0.15 is a REFERENCE LINE, not a gate for this script.
# freeze/preregistration.md §2 sets "三语间 κ 落差 ≤ 0.15" for test #2, which is
# Yifan's own intra-rater drift (T1 vs T2, human vs human) — and that test is
# WAIVED for v1.0.  Nothing pre-registers a model-vs-human kappa gap.  Printing
# it as PASS/FAIL would import a human-drift threshold into model scoring, so
# the gap is reported with its bootstrap CI and left uninterpreted.
KAPPA_GAP_REFERENCE = 0.15
KAPPA_GAP_BOOTSTRAP = 2000
KAPPA_GAP_SEED = 20260823
MIN_PRESENT_FOR_LANGUAGE_KAPPA = 10


def load_gold():
    g = {}
    for l in open(EVAL_IN):
        if l.strip():
            r = json.loads(l)
            g[r["review_id"]] = {**r["gold"], "arm": r["arm"]}
    return g


def cohen_kappa(pairs):
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(1 for a, b in pairs if a == b) / n
    ga, gb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum((ga[c] / n) * (gb[c] / n) for c in set(ga) | set(gb))
    return (po - pe) / (1 - pe) if pe != 1 else float("nan")


def check_legality(p):
    """Return list of violated hard constraints for one parsed prediction."""
    if not isinstance(p, dict):
        return ["not-an-object"]
    v = []
    lab = p.get("unfair_label")
    oos = p.get("out_of_scope")
    sub = p.get("subtype") or []
    fac = p.get("procedural_facet") or []
    conf = p.get("confidence")
    bl = p.get("borderline")
    ur = p.get("uncertainty_reason") or ""
    expl = p.get("explicitness")
    if (lab == "NA") != bool(oos):
        v.append("NA<->out_of_scope")
    if lab == "PRESENT":
        if not sub:
            v.append("PRESENT-no-subtype")
        if expl not in ("explicit", "implicit"):
            v.append("PRESENT-explicitness")
        if not (p.get("normalized_claim") or "").strip():
            v.append("PRESENT-no-claim")
    else:
        if sub:
            v.append("nonPRESENT-has-subtype")
        if expl not in (None, ""):
            v.append("nonPRESENT-explicitness-not-null")
    if fac and "procedural" not in sub:
        v.append("facet-without-procedural")
    if bool(bl) != (conf == "low"):
        v.append("borderline<->low")
    if bool(bl) and not ur:
        v.append("borderline-no-reason")
    if not bool(bl) and ur:
        v.append("reason-without-borderline")
    bad_sub = set(sub) - {"distributive", "procedural"}
    if bad_sub:
        v.append(f"bad-subtype:{','.join(bad_sub)}")
    return v


def score_one(path, gold):
    preds = {}
    for l in open(path):
        if l.strip():
            r = json.loads(l)
            preds[r["review_id"]] = r
    total = len(preds)
    parsed_ok = sum(1 for r in preds.values() if r.get("parsed"))

    pairs, present_tp = [], 0
    pred_present = gold_present = 0
    en_present_gold = en_present_hit = 0
    hardneg_total = hardneg_fp = 0
    sub_both = sub_agree = 0
    fac_both = fac_agree = 0
    legality = Counter()
    n_legal_checked = 0
    confusion = Counter()

    for rid, gr in gold.items():
        pr = preds.get(rid)
        gy = gr["unfair_label"]
        p = pr.get("parsed") if pr else None
        py = (p or {}).get("unfair_label")
        py = py if py in LABELS else "NA"        # unparseable -> treat as NA
        pairs.append((gy, py))
        confusion[(gy, py)] += 1
        if gy == "PRESENT":
            gold_present += 1
        if py == "PRESENT":
            pred_present += 1
        if gy == "PRESENT" and py == "PRESENT":
            present_tp += 1
        # English PRESENT recall
        if gr.get("language") == "en" and gy == "PRESENT":
            en_present_gold += 1
            if py == "PRESENT":
                en_present_hit += 1
        # hard-negative false positive — strict denominator.
        # The hardneg arm is keyword-selected, not label-selected: some of its
        # rows really are PRESENT by human judgment.  Calling those PRESENT is
        # a hit, not a false positive, so they must leave the denominator.
        if gr.get("arm") == "hardneg" and gy == "ABSENT":
            hardneg_total += 1
            if py == "PRESENT":
                hardneg_fp += 1
        # subtype / facet agreement (only where both call PRESENT)
        if gy == "PRESENT" and py == "PRESENT" and isinstance(p, dict):
            sub_both += 1
            if set(p.get("subtype") or []) == set(gr.get("subtype") or []):
                sub_agree += 1
            if "procedural" in (gr.get("subtype") or []):
                fac_both += 1
                if set(p.get("procedural_facet") or []) == \
                        set(gr.get("procedural_facet") or []):
                    fac_agree += 1
        # legality
        if p is not None:
            n_legal_checked += 1
            for viol in check_legality(p):
                legality[viol] += 1

    acc = sum(1 for a, b in pairs if a == b) / len(pairs)
    prec = present_tp / pred_present if pred_present else float("nan")
    rec = present_tp / gold_present if gold_present else float("nan")
    f1 = (2 * prec * rec / (prec + rec)
          if prec == prec and rec == rec and (prec + rec) else float("nan"))

    return {
        "path": os.path.basename(path), "total": total,
        "parse_rate": parsed_ok / total if total else 0,
        "acc": acc, "kappa": cohen_kappa(pairs),
        "present_p": prec, "present_r": rec, "present_f1": f1,
        "en_present": (en_present_hit, en_present_gold),
        "hardneg_fp": (hardneg_fp, hardneg_total),
        "sub_agree": (sub_agree, sub_both),
        "fac_agree": (fac_agree, fac_both),
        "legality": legality, "n_legal": n_legal_checked,
        "confusion": confusion,
    }


def frac(t):
    a, b = t
    return f"{a}/{b}" + (f" ({a/b:.0%})" if b else "")


def print_report(s):
    print(f"\n=== {s['path']} ===")
    print(f"rows scored          : {s['total']}")
    print(f"JSON parse rate      : {s['parse_rate']:.1%}")
    print(f"3-class accuracy     : {s['acc']:.1%}")
    print(f"Cohen's kappa        : {s['kappa']:.3f}")
    print(f"PRESENT P / R / F1   : {s['present_p']:.1%} / "
          f"{s['present_r']:.1%} / {s['present_f1']:.1%}")
    print(f"** English PRESENT recall : {frac(s['en_present'])}")
    print(f"** hardneg FP (strict)    : {frac(s['hardneg_fp'])}")
    print(f"subtype agreement    : {frac(s['sub_agree'])}")
    print(f"facet agreement      : {frac(s['fac_agree'])}")
    print(f"legality violations  : "
          f"{sum(s['legality'].values())} across {s['n_legal']} parsed rows")
    for k, v in s["legality"].most_common():
        print(f"    - {k}: {v}")
    print("confusion (gold->pred):")
    for g in LABELS:
        row = "  ".join(f"{p}:{s['confusion'].get((g, p), 0):>3}" for p in LABELS)
        print(f"    gold {g:<8} | {row}")


# v2 separated-answer-key scorer --------------------------------------------
# The legacy scorer above is retained for provenance.  This entry point never
# reads the raw-text input package; it joins responses only to answer_key.jsonl.

V2_OUTPUT_FIELDS = {"unfair_label", "out_of_scope", "subtype", "procedural_facet",
                    "evidence_span", "normalized_claim", "explicitness", "confidence",
                    "borderline", "uncertainty_reason", "annotator_note"}
V2_SUBTYPES = {"distributive", "procedural"}
V2_FACETS = {"cheating_governance", "sanction", "access_exclusion",
             "competitive_balance", "unfair_by_design"}
V2_REASONS = {"attribution_unclear", "irony_undecidable", "price_boundary",
              "technical_access_boundary", "toxicity_attribution", "language_cue",
              "facet_boundary"}


def v2_rows(path):
    with open(path, encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON at {path}:{line_number}: {exc}") from exc


def v2_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def v2_load_gold(path):
    result = {}
    for row in v2_rows(path):
        if set(row) != {"review_id", "arm", "source_arm", "gold"}:
            raise ValueError("Answer key must contain review_id, arms, and gold only; it must not contain review text.")
        review_id = str(row["review_id"])
        if review_id in result:
            raise ValueError(f"Duplicate review_id in answer key: {review_id}")
        result[review_id] = {**row["gold"], "arm": row["arm"], "source_arm": row["source_arm"]}
    if not result:
        raise ValueError("Answer key is empty.")
    return result


def v2_schema_violations(answer):
    """Re-check relations possible without raw text; 09 checks literal spans."""
    if not isinstance(answer, dict):
        return ["not_json_object"]
    if set(answer) != V2_OUTPUT_FIELDS:
        return ["output_keys_mismatch"]
    violations = []
    label, oos = answer["unfair_label"], answer["out_of_scope"]
    subtype, facet = answer["subtype"], answer["procedural_facet"]
    evidence, claim = answer["evidence_span"], answer["normalized_claim"]
    explicitness, confidence = answer["explicitness"], answer["confidence"]
    borderline, reason = answer["borderline"], answer["uncertainty_reason"]
    if label not in LABELS: violations.append("invalid_unfair_label")
    if not isinstance(oos, bool) or (label == "NA") != oos: violations.append("NA_out_of_scope_mismatch")
    if not isinstance(subtype, list) or len(subtype) != len(set(subtype)) or set(subtype) - V2_SUBTYPES: violations.append("invalid_subtype")
    if not isinstance(facet, list) or len(facet) != len(set(facet)) or set(facet) - V2_FACETS: violations.append("invalid_procedural_facet")
    if explicitness not in {"explicit", "implicit", None}: violations.append("invalid_explicitness")
    if confidence not in {"high", "medium", "low"}: violations.append("invalid_confidence")
    if not isinstance(borderline, bool) or borderline != (confidence == "low"): violations.append("borderline_confidence_mismatch")
    if not all(isinstance(value, str) for value in (evidence, claim, reason, answer["annotator_note"])): violations.append("nonstring_text_field")
    reasons = reason.split(";") if isinstance(reason, str) and reason else []
    if (not isinstance(reason, str) or (not borderline and reason) or
            (borderline and (not reasons or set(reasons) - V2_REASONS))): violations.append("invalid_uncertainty_reason")
    if label == "PRESENT":
        if not subtype: violations.append("PRESENT_missing_subtype")
        if not evidence or not claim: violations.append("PRESENT_missing_evidence_or_claim")
        if explicitness not in {"explicit", "implicit"}: violations.append("PRESENT_invalid_explicitness")
        if "procedural" in subtype and not facet: violations.append("procedural_missing_facet")
        if "procedural" not in subtype and facet: violations.append("facet_without_procedural")
    elif label in {"ABSENT", "NA"}:
        if subtype or facet or evidence or explicitness is not None: violations.append("nonPRESENT_fields_not_empty")
        if label == "NA" and claim: violations.append("NA_claim_not_empty")
        if label == "ABSENT" and ((borderline and not claim) or (not borderline and claim)): violations.append("ABSENT_claim_rule")
    return violations


def v2_fraction(pair):
    left, right = pair
    return f"{left}/{right}" + (f" ({left/right:.0%})" if right else "")


def v2_percent(value):
    return "n/a" if isinstance(value, float) and math.isnan(value) else f"{value:.1%}"


def v2_cell():
    """One accumulator.  The same shape is used overall, per language, per arm,
    so every slice is computed by identical code and the numbers are comparable
    by construction rather than by my remembering to keep two formulas in sync."""
    return {"n": 0, "no_label": 0, "all3_pairs": [], "codable_pairs": [],
            "human_present": 0, "human_absent": 0, "human_na": 0,
            "model_present": 0, "tp": 0, "fp": 0}


def v2_tally(cell, human_label, model_label):
    cell["n"] += 1
    if model_label == NO_LABEL:
        # A measurement failure contributes to no agreement statistic; it is
        # counted, reported, and left out of accuracy/kappa rather than being
        # quietly scored as if the model had said "NA".
        cell["no_label"] += 1
    else:
        cell["all3_pairs"].append((human_label, model_label))
        if human_label in {"PRESENT", "ABSENT"}:
            cell["codable_pairs"].append((human_label, model_label))
    cell["human_present"] += human_label == "PRESENT"
    cell["human_absent"] += human_label == "ABSENT"
    cell["human_na"] += human_label == "NA"
    cell["model_present"] += model_label == "PRESENT"
    cell["tp"] += human_label == model_label == "PRESENT"
    cell["fp"] += human_label == "ABSENT" and model_label == "PRESENT"


def v2_rates(cell):
    """Derive rates from one accumulator.

    Denominator conventions, fixed here once so no caller can drift:
      precision  = tp / (rows the model called PRESENT)
      recall     = tp / (rows a human called PRESENT)   <- NO_LABEL rows stay in
                   this denominator: a row the model failed to label is a real
                   miss.  The no_label count is printed beside it so the reader
                   can always see how much of a recall shortfall is judgment
                   and how much is plumbing.
      fp_rate    = (human ABSENT & model PRESENT) / (human ABSENT)
                   <- human-PRESENT rows are never in a false-positive
                   denominator, whatever arm they sit in.
    """
    nan = float("nan")
    precision = cell["tp"] / cell["model_present"] if cell["model_present"] else nan
    recall = cell["tp"] / cell["human_present"] if cell["human_present"] else nan
    f1 = (2 * precision * recall / (precision + recall)
          if precision == precision and recall == recall and precision + recall else nan)
    return {
        "n": cell["n"], "no_label": cell["no_label"], "scored": len(cell["all3_pairs"]),
        "human_present": cell["human_present"], "human_absent": cell["human_absent"],
        "human_na": cell["human_na"], "model_present": cell["model_present"],
        "tp": cell["tp"], "fp": cell["fp"],
        "all_accuracy": (sum(a == b for a, b in cell["all3_pairs"]) / len(cell["all3_pairs"])
                         if cell["all3_pairs"] else nan),
        "all_kappa": cohen_kappa(cell["all3_pairs"]),
        "codable_accuracy": (sum(a == b for a, b in cell["codable_pairs"]) / len(cell["codable_pairs"])
                             if cell["codable_pairs"] else nan),
        "codable_kappa": cohen_kappa(cell["codable_pairs"]),
        "p": precision, "r": recall, "f1": f1,
        "recall_pair": (cell["tp"], cell["human_present"]),
        "fp_pair": (cell["fp"], cell["human_absent"]),
    }


def v2_kappa_gap_ci(cells):
    """Bootstrap CI for the max-min per-language codable kappa.

    Reported because the point estimate on its own invites over-reading: with
    3 Japanese and 5 Chinese human-PRESENT rows, a single flipped row moves a
    language's kappa by more than the whole gap.  Seeded, so reruns agree.
    """
    pools = {lang: cell["codable_pairs"] for lang, cell in cells.items()
             if lang in REPORT_LANGS and cell["codable_pairs"]}
    if len(pools) < 2:
        return float("nan"), float("nan"), float("nan")
    rng = random.Random(KAPPA_GAP_SEED)
    gaps = []
    for _ in range(KAPPA_GAP_BOOTSTRAP):
        values = []
        for pairs in pools.values():
            sample = [pairs[rng.randrange(len(pairs))] for _ in pairs]
            k = cohen_kappa(sample)
            if k == k:
                values.append(k)
        if len(values) > 1:
            gaps.append(max(values) - min(values))
    if not gaps:
        return float("nan"), float("nan"), float("nan")
    gaps.sort()
    return (gaps[int(0.025 * len(gaps))], gaps[int(0.975 * len(gaps))],
            sum(g <= KAPPA_GAP_REFERENCE for g in gaps) / len(gaps))


def v2_score(prediction_path, gold):
    predictions = {}
    for row in v2_rows(prediction_path):
        review_id = str(row["review_id"])
        if review_id in predictions:
            raise ValueError(f"Duplicate review_id in responses: {review_id}")
        predictions[review_id] = row
    unknown = set(predictions) - set(gold)
    if unknown:
        raise ValueError(f"Responses include IDs outside this answer key: {sorted(unknown)[:10]}")
    confusion, legality, raw_text_checks = Counter(), Counter(), Counter()
    no_label_reasons = Counter()
    parsed_ok = schema_ok = missing = 0
    subtype_total = subtype_agree = facet_total = facet_agree = 0
    hardneg_loose_fp = hardneg_rows = 0
    overall = v2_cell()
    by_language = defaultdict(v2_cell)
    by_arm = defaultdict(v2_cell)
    # Which arms supply each language's human-PRESENT rows.  If the mixes
    # differ, a per-language comparison is confounded with sampling design:
    # a language whose positives come from the purposive diagnostic/hardneg
    # arms is being asked harder questions than one sampled at random.
    present_arm_mix = defaultdict(Counter)
    for review_id, human in gold.items():
        if human["unfair_label"] == "PRESENT":
            present_arm_mix[human.get("language") or "unknown"][human["arm"]] += 1
    for review_id, human in gold.items():
        response = predictions.get(review_id)
        parsed = response.get("parsed") if response else None
        if response is None: missing += 1
        if isinstance(parsed, dict):
            parsed_ok += 1
            violations = v2_schema_violations(parsed)
            for violation in violations: legality[violation] += 1
            schema_ok += not violations
        if response:
            for violation in response.get("validation_errors", []): raw_text_checks[violation] += 1
        # --- model label, with measurement failures kept separate from "NA" ---
        if response is None:
            model_label = NO_LABEL; no_label_reasons["missing_response_row"] += 1
        elif not isinstance(parsed, dict):
            model_label = NO_LABEL; no_label_reasons["unparsed_response"] += 1
        elif parsed.get("unfair_label") not in LABELS:
            model_label = NO_LABEL; no_label_reasons["label_not_in_schema"] += 1
        else:
            model_label = parsed["unfair_label"]
        human_label = human["unfair_label"]
        confusion[(human_label, model_label)] += 1
        v2_tally(overall, human_label, model_label)
        v2_tally(by_language[human.get("language") or "unknown"], human_label, model_label)
        v2_tally(by_arm[human["arm"]], human_label, model_label)
        if human["arm"] == "hardneg":
            hardneg_rows += 1
            hardneg_loose_fp += model_label == "PRESENT"
        if human_label == model_label == "PRESENT" and isinstance(parsed, dict):
            subtype_total += 1; subtype_agree += set(parsed.get("subtype", [])) == set(human.get("subtype", []))
            if "procedural" in human.get("subtype", []):
                facet_total += 1; facet_agree += set(parsed.get("procedural_facet", [])) == set(human.get("procedural_facet", []))
    language_rates = {lang: v2_rates(cell) for lang, cell in by_language.items()}
    arm_rates = {arm: v2_rates(cell) for arm, cell in by_arm.items()}
    hardneg = arm_rates.get("hardneg", v2_rates(v2_cell()))
    # Cross-language kappa gap: descriptive only.  See KAPPA_GAP_REFERENCE.
    comparable = {lang: language_rates[lang]["codable_kappa"] for lang in REPORT_LANGS
                  if lang in language_rates and language_rates[lang]["codable_kappa"] == language_rates[lang]["codable_kappa"]}
    kappa_gap = max(comparable.values()) - min(comparable.values()) if len(comparable) > 1 else float("nan")
    gap_low, gap_high, gap_p = v2_kappa_gap_ci(by_language)
    return {"name": str(prediction_path), "expected": len(gold), "responded": len(predictions), "missing": missing,
            "kappa_gap_ci": (gap_low, gap_high), "kappa_gap_p_under_ref": gap_p,
            "present_arm_mix": present_arm_mix,
            "parse_rate": parsed_ok / len(gold), "schema_rate": schema_ok / len(gold),
            "no_label_reasons": no_label_reasons, "no_label": overall["no_label"],
            "overall": v2_rates(overall), "by_language": language_rates, "by_arm": arm_rates,
            "hardneg_strict": hardneg["fp_pair"],
            "hardneg_loose": (hardneg_loose_fp, hardneg_rows),
            "absent_fp": v2_rates(overall)["fp_pair"],
            "en": language_rates.get("en", v2_rates(v2_cell()))["recall_pair"],
            "kappa_gap": kappa_gap, "kappa_by_language": comparable,
            "subtype": (subtype_agree, subtype_total), "facet": (facet_agree, facet_total),
            "legality": legality, "raw_text_checks": raw_text_checks, "confusion": confusion}


def v2_print(result):
    overall = result["overall"]
    print(f"\n=== {result['name']} ===")
    print(f"responses / expected   : {result['responded']}/{result['expected']} (missing={result['missing']})")
    print(f"strict JSON parse rate : {v2_percent(result['parse_rate'])}")
    print(f"schema-valid rate      : {v2_percent(result['schema_rate'])}")
    print(f"rows with no model label: {result['no_label']}"
          + (f"  ({', '.join(f'{k}={v}' for k, v in result['no_label_reasons'].most_common())})"
             if result["no_label"] else "   <- excluded from accuracy/kappa, kept in recall denominator"))
    print(f"3-class accuracy/kappa : {v2_percent(overall['all_accuracy'])} / {overall['all_kappa']:.3f}"
          f"   (on {overall['scored']} labeled rows)")
    print(f"codable P/A acc/kappa  : {v2_percent(overall['codable_accuracy'])} / {overall['codable_kappa']:.3f}")
    print(f"PRESENT P / R / F1     : {v2_percent(overall['p'])} / {v2_percent(overall['r'])} / {v2_percent(overall['f1'])}")
    print(f"subtype / facet agree  : {v2_fraction(result['subtype'])} / {v2_fraction(result['facet'])}")
    print("\nper language (the three-way comparison this project exists to make):")
    print(f"  {'lang':<6}{'n':>5}{'noLbl':>6}{'PRESENT recall':>17}{'FP on ABSENT':>15}"
          f"{'prec':>8}{'F1':>8}{'codable kappa':>15}")
    for lang in list(REPORT_LANGS) + sorted(set(result["by_language"]) - set(REPORT_LANGS)):
        rates = result["by_language"].get(lang)
        if not rates: continue
        print(f"  {lang:<6}{rates['n']:>5}{rates['no_label']:>6}{v2_fraction(rates['recall_pair']):>17}"
              f"{v2_fraction(rates['fp_pair']):>15}{v2_percent(rates['p']):>8}{v2_percent(rates['f1']):>8}"
              f"{rates['codable_kappa']:>15.3f}")
    gap = result["kappa_gap"]
    if gap == gap:
        low, high = result["kappa_gap_ci"]
        print(f"  cross-language codable-kappa gap: {gap:.3f}  95% CI [{low:.2f}, {high:.2f}]  "
              f"P(gap <= {KAPPA_GAP_REFERENCE:.2f}) = {result['kappa_gap_p_under_ref']:.2f}")
        print(f"  NOTE: {KAPPA_GAP_REFERENCE:.2f} is a reference line borrowed from the WAIVED "
              f"human test-retest check (preregistration.md §2), not a gate on model scores.")
    thin = [f"{lang}={result['by_language'][lang]['human_present']}" for lang in REPORT_LANGS
            if lang in result["by_language"]
            and result["by_language"][lang]["human_present"] < MIN_PRESENT_FOR_LANGUAGE_KAPPA]
    if thin:
        print(f"  CAUTION: thin PRESENT support ({', '.join(thin)}; floor is "
              f"{MIN_PRESENT_FOR_LANGUAGE_KAPPA}); these per-language figures are directional.")
    mixes = {lang: dict(mix) for lang, mix in result["present_arm_mix"].items() if lang in REPORT_LANGS}
    if len({tuple(sorted(mix)) for mix in mixes.values()}) > 1:
        print("  CONFOUNDED: languages draw their human-PRESENT rows from different arms, so a "
              "cross-language comparison also compares sampling designs, not just languages:")
        for lang in REPORT_LANGS:
            if lang in mixes:
                print(f"    {lang}: " + ", ".join(f"{arm}={n}" for arm, n in sorted(mixes[lang].items())))
    print("\nper arm (the arms are purposive samples; rates are QC, not ability estimates):")
    print(f"  {'arm':<12}{'n':>5}{'noLbl':>6}{'PRESENT recall':>17}{'FP on ABSENT':>15}")
    for arm in sorted(result["by_arm"]):
        rates = result["by_arm"][arm]
        print(f"  {arm:<12}{rates['n']:>5}{rates['no_label']:>6}{v2_fraction(rates['recall_pair']):>17}"
              f"{v2_fraction(rates['fp_pair']):>15}")
    print(f"hardneg FP (strict, human-ABSENT denominator) : {v2_fraction(result['hardneg_strict'])}")
    print(f"hardneg FP (loose, all hardneg rows; legacy)  : {v2_fraction(result['hardneg_loose'])}")
    print(f"FP on every human-ABSENT row (all 3 arms)     : {v2_fraction(result['absent_fp'])}")
    print(f"\ncontrolled-field violations: {sum(result['legality'].values())}")
    for name, count in result["legality"].most_common(): print(f"  - {name}: {count}")
    if result["raw_text_checks"]:
        print("raw-text-only checks performed by 09:")
        for name, count in result["raw_text_checks"].most_common(): print(f"  - {name}: {count}")
    print("confusion (human -> model):")
    for human_label in LABELS:
        values = "  ".join(f"{model_label}:{result['confusion'].get((human_label, model_label), 0):>3}"
                           for model_label in CONFUSION_COLS)
        print(f"  {human_label:<7} | {values}")


def separated_score_main():
    parser = argparse.ArgumentParser(description="Score responses against a text-free development answer key.")
    parser.add_argument("--pred", action="append", required=True, help="one or more responses.jsonl files")
    parser.add_argument("--answer-key", help="answer_key.jsonl; defaults to beside the first --pred")
    args = parser.parse_args()
    paths = [Path(path).expanduser().resolve() for path in args.pred]
    answer_key = Path(args.answer_key).expanduser().resolve() if args.answer_key else paths[0].parent / "answer_key.jsonl"
    gold = v2_load_gold(answer_key)
    print(f"answer key: {answer_key} ({len(gold)} rows; sha256={v2_sha256(answer_key)})")
    results = [v2_score(path, gold) for path in paths]
    for result in results: v2_print(result)
    if len(results) >= 2:
        width = max(16, min(28, max(len(Path(r["name"]).parent.name) for r in results) + 2))
        print("\n=== A/B summary (higher is better except false-positive rows) ===")
        print(f"{'metric':<26}" + "".join(f"{Path(r['name']).parent.name[-width + 2:]:>{width}}" for r in results))

        def row(label, values):
            print(f"{label:<26}" + "".join(f"{value:>{width}}" for value in values))

        row("schema-valid rate", [v2_percent(r["schema_rate"]) for r in results])
        row("rows with no model label", [str(r["no_label"]) for r in results])
        row("codable P/A kappa", [f"{r['overall']['codable_kappa']:.3f}" for r in results])
        row("PRESENT F1", [v2_percent(r["overall"]["f1"]) for r in results])
        for lang in REPORT_LANGS:
            if any(lang in r["by_language"] for r in results):
                row(f"{lang.upper()} PRESENT recall",
                    [v2_fraction(r["by_language"][lang]["recall_pair"]) if lang in r["by_language"] else "-"
                     for r in results])
        for lang in REPORT_LANGS:
            if any(lang in r["by_language"] for r in results):
                row(f"{lang.upper()} FP on ABSENT",
                    [v2_fraction(r["by_language"][lang]["fp_pair"]) if lang in r["by_language"] else "-"
                     for r in results])
        row("cross-lang kappa gap",
            [f"{r['kappa_gap']:.3f}" if r["kappa_gap"] == r["kappa_gap"] else "n/a" for r in results])
        row("hardneg FP (strict)", [v2_fraction(r["hardneg_strict"]) for r in results])
        row("FP on all human-ABSENT", [v2_fraction(r["absent_fp"]) for r in results])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", action="append", required=True,
                    help="prediction jsonl (repeat for A/B comparison)")
    args = ap.parse_args()
    gold = load_gold()
    print(f"answer key rows: {len(gold)}")
    results = [score_one(p, gold) for p in args.pred]
    for s in results:
        print_report(s)
    if len(results) == 2:
        a, b = results
        print("\n=== A/B summary (higher = better, except hardneg FP) ===")
        print(f"{'metric':<24}{a['path'][:22]:>24}{b['path'][:22]:>24}")
        def line(name, va, vb):
            print(f"{name:<24}{va:>24}{vb:>24}")
        line("parse rate", f"{a['parse_rate']:.1%}", f"{b['parse_rate']:.1%}")
        line("accuracy", f"{a['acc']:.1%}", f"{b['acc']:.1%}")
        line("kappa", f"{a['kappa']:.3f}", f"{b['kappa']:.3f}")
        line("PRESENT F1", f"{a['present_f1']:.1%}", f"{b['present_f1']:.1%}")
        line("EN PRESENT recall", frac(a['en_present']), frac(b['en_present']))
        line("hardneg FP", frac(a['hardneg_fp']), frac(b['hardneg_fp']))
        line("legality viol.", str(sum(a['legality'].values())),
             str(sum(b['legality'].values())))


if __name__ == "__main__":
    separated_score_main()
