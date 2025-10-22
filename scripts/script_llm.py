# =======================
# Auto-grader
# =======================
# - Uses SBERT + Cross-Encoder hybrid scoring
# - Aggregates across multiple reference answers (desired_answer + llm_answers)
# - Outputs JSON in the structure you asked for
#

import json
import math
import re
from typing import List, Dict, Any, Tuple
import json
import math
import re
from typing import List, Dict, Any, Set
import numpy as np
import torch
from scipy.special import expit as sigmoid
from sentence_transformers import SentenceTransformer, CrossEncoder, util
try:
    import pandas as pd
except Exception as e:
    raise RuntimeError(
        "pandas is required. Run the cell with '!pip install pandas'"
    ) from e


# -------------------------
# 0) Config
# -------------------------
ALPHA = 0.4        # hybrid weight (lower -> stricter, more cross-encoder weight)
SLOPE = 0.9        # curve slope (<1 a touch more generous near top after intercept)
INTERCEPT = 0.8    # curve intercept (adds points across the board)
ROUND_TO = 0.5     # round final mark to nearest 0.5 (change to 0.1 if you want tenths)

# If you want to read from files, set these to paths (or leave None to use in-memory lists)
QUESTIONS_JSON_PATH = "data/mohlers_question_dataset.json"
ANSWERS_JSON_PATH   = "data/mohlers_student_answers.json"

# -------------------------
# 1) Load models once
# -------------------------
print("Loading models (this may take a moment)...")
embedding_model = SentenceTransformer('all-mpnet-base-v2')
cross_encoder   = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
print("Models loaded successfully.")

# -------------------------
# 2) Provide data
# -------------------------
questions_data = []
student_answers_data = []

if QUESTIONS_JSON_PATH:
    print(f"Loading questions from {QUESTIONS_JSON_PATH}...")
    with open(QUESTIONS_JSON_PATH, "r", encoding="utf-8") as f:
        questions_data = json.load(f)
    print(f"-> Found {len(questions_data)} questions.")
else:
    print("Warning: QUESTIONS_JSON_PATH is not set. No questions loaded.")

if ANSWERS_JSON_PATH:
    print(f"Loading student answers from {ANSWERS_JSON_PATH}...")
    with open(ANSWERS_JSON_PATH, "r", encoding="utf-8") as f:
        student_answers_data = json.load(f)
    print(f"-> Found {len(student_answers_data)} student answer entries.")
else:
    print("Warning: ANSWERS_JSON_PATH is not set. No student answers loaded.")

# -------------------------
# 3) Utilities
# -------------------------
def _round_to(x: float, step: float) -> float:
    if step <= 0:
        return x
    return round(x / step) * step

def _refs_for_question(qrow: Dict[str, Any]) -> List[str]:
    """Collect reference answers for a question (desired + llm)."""
    refs = []
    for s in (qrow.get("llm_answers") or []):
        s = (s or "").strip()
        if s:
            refs.append(s)
    return refs

def _grade_one(student_answer: str,
               ref_answers: List[str],
               max_point: float,
               alpha: float = ALPHA,
               slope: float = SLOPE,
               intercept: float = INTERCEPT,
               round_to: float = ROUND_TO
              ) -> Tuple[float, Dict[str, Any]]:
    """
    Grade a single student answer against a set of reference answers.
    - We take the BEST similarity across all refs (max over refs).
    - Returns (final_mark, debug_info)
    """
    if not student_answer or not ref_answers:
        return 0.0, {"cosine": 0.0, "cross_prob": 0.0, "hybrid01": 0.0}

    # --- Embeddings: compute once for all ref + student
    sentences = ref_answers + [student_answer]
    embs = embedding_model.encode(sentences, convert_to_tensor=True)
    ref_embs = embs[:-1]
    stu_emb  = embs[-1].unsqueeze(0)  # shape [1, d]

    # cosine sim vs each ref
    cos_sims = util.cos_sim(stu_emb, ref_embs)[0]  # shape [R]
    # normalize to [0,1]
    cos_norm = ((cos_sims + 1.0) / 2.0).cpu().numpy()

    # cross-encoder logits vs each ref
    pairs = [(r, student_answer) for r in ref_answers]
    cross_logits = cross_encoder.predict(pairs)
    cross_prob = sigmoid(np.array(cross_logits))  # [R] in [0,1]

    # take best across refs
    best_cos   = float(np.max(cos_norm))
    best_cprob = float(np.max(cross_prob))

    # hybrid
    hybrid01 = alpha * best_cos + (1 - alpha) * best_cprob

    # map to 0..max_point
    raw_mark = max_point * hybrid01
    curved   = raw_mark * slope + intercept
    mark     = min(max_point, max(0.0, _round_to(curved, round_to)))

    dbg = {
        "best_cos": best_cos,
        "best_cross_prob": best_cprob,
        "hybrid01": hybrid01,
        "raw_mark": raw_mark,
        "curved": curved,
    }
    return mark, dbg

# -------------------------
# 4) Build index of answers
# -------------------------
print("Building answer index by Question ID...")
answers_by_qid: Dict[int, List[Dict[str, Any]]] = {}
for row in student_answers_data:
    qid = int(row.get("question_id"))
    answers_by_qid.setdefault(qid, []).append(row)
print(f"-> Index built. Found answers for {len(answers_by_qid)} questions.")

# -------------------------
# 5) Grade everything
# -------------------------
print(f"\n--- Starting grading for {len(questions_data)} questions ---")
results: List[Dict[str, Any]] = []

# Use enumerate to track progress, start=1 for 1-based indexing
for q_idx, q in enumerate(questions_data, 1):
    qid = int(q.get("id"))
    question_text = q.get("question", "")
    max_point = float(q.get("max_point", 5.0))
    criteria = q.get("mark_breakdown") or []
    refs = _refs_for_question(q)
    q_answers = answers_by_qid.get(qid, [])

    print(f"[{q_idx}/{len(questions_data)}] Grading QID {qid} ({len(q_answers)} answers, {len(refs)} refs)...")

    graded_items = []
    for ans in q_answers:
        student_answer = ans.get("student_answer", "")
        # grade
        nlp_score, _dbg = _grade_one(
            student_answer=student_answer,
            ref_answers=refs,
            max_point=max_point,
        )

        # copy the original fields through, then add nlp_score (do NOT add trailing commas)
        item_out = {
            "id": ans.get("id"),
            "question_id": qid,
            "student_answer": student_answer,
        }
        # Keep any human scores if present
        if "score_me" in ans:    item_out["score_me"] = ans["score_me"]
        if "score_other" in ans: item_out["score_other"] = ans["score_other"]
        if "score_avg" in ans:   item_out["score_avg"] = ans["score_avg"]

        item_out["nlp_score"] = float(nlp_score)
        graded_items.append(item_out)

    out_obj = {
        "question_id": qid,
        "question": question_text,
        "max_point": max_point,
        "ref_count": len(refs),
        "criteria_count": len(criteria),
        "graded_count": len(graded_items),
        "items": graded_items,
    }
    results.append(out_obj)

print("--- Grading complete ---")

# -------------------------
# 6) Save results
# -------------------------
OUTPUT_JSON = "scripts/graded_results_llm.json"
print(f"\nSaving results to {OUTPUT_JSON}...")
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(results)} question bundles to {OUTPUT_JSON}")

# ==========================================================
# Graded Results - Statistical Analysis (Colab)
# ==========================================================
#
# This script reads the 'graded_results.json' (from the SBERT-grader)
# and the 'questions.json' (with reference answers) to generate
# a final 'stats_results.json' file.
#
# It calculates correlations, MAE, RMSE, and agreement %
# between the model's 'nlp_score' and human scores.
#
# ==========================================================

# ----------------------------
# 1) CONFIGURE FILE PATHS
# ----------------------------
# Point this to the *input* question file (must contain 'desired_answer', 'llm_answers')
QUESTIONS_JSON_PATH = "data/mohlers_question_dataset.json"

# Point this to the *input* file generated by the auto-grader script
GRADED_RESULTS_PATH = "scripts/graded_results_llm.json"

# This is the *output* file where stats will be saved
STATS_OUTPUT_PATH = "scripts/stats_results_llm.json"

WRITE_FAILURES_SAMPLE = True
FAILURES_SAMPLE_PATH = "scripts/stats_failures_sample_llm.json"

print(f"Input Questions: {QUESTIONS_JSON_PATH}")
print(f"Input Grades:    {GRADED_RESULTS_PATH}")
print(f"Output Stats:    {STATS_OUTPUT_PATH}")

# ----------------------------
# 2) Text similarity helpers
# ----------------------------
def _tok(s: str) -> List[str]:
    """Basic tokenizer: lowercase, alphanumeric, split."""
    return [t for t in "".join(c.lower() if c.isalnum() else " " for c in (s or "")).split() if t]

def jaccard(a: str, b: str) -> float:
    """Calculates Jaccard similarity between two strings."""
    A, B = set(_tok(a)), set(_tok(b))
    if not A and not B:
        return 1.0
    if not A or not B:
        return 0.0
    inter = len(A & B)
    union = len(A | B)
    return inter / union if union else 0.0

def pairwise_jaccard_mean(strings: List[str]) -> float | None:
    """Calculates the mean pairwise Jaccard similarity for a list of strings."""
    toks: List[Set[str]] = [set(_tok(x)) for x in (strings or []) if x]
    n = len(toks)
    if n < 2:
        return None
    sims = []
    for i in range(n):
        for j in range(i + 1, n):
            A, B = toks[i], toks[j]
            if not A and not B:
                sims.append(1.0)
            elif not A or not B:
                sims.append(0.0)
            else:
                sims.append(len(A & B) / len(A | B))
    return sum(sims) / len(sims) if sims else None

# ----------------------------
# 3) Core stats functions
# ----------------------------
def _to_numeric(series):
    """Helper to convert series to numeric, coercing errors."""
    return pd.to_numeric(series, errors="coerce")

def per_question_stats(df_q: pd.DataFrame) -> Dict[str, Any]:
    """Calculate statistics for a single question's dataframe."""
    out = {}
    out["n"] = int(len(df_q))

    # Calculate means for all available score columns
    for col in ["score_me", "score_other", "score_avg", "nlp_score"]:
        if col in df_q.columns:
            out[f"mean_{col}"] = float(_to_numeric(df_q[col]).mean())

    # Calculate correlations, errors, and agreement vs. 'nlp_score'
    for col in ["score_me", "score_other", "score_avg"]:
        if col in df_q.columns and "nlp_score" in df_q.columns:
            s1 = _to_numeric(df_q[col])
            s2 = _to_numeric(df_q["nlp_score"])
            
            # Check for sufficient valid data pairs
            mask = s1.notna() & s2.notna()
            if mask.sum() > 2:
                out[f"pearson_nlp_vs_{col}"] = float(s1[mask].corr(s2[mask]))
            else:
                out[f"pearson_nlp_vs_{col}"] = None

            diff = (s2 - s1)[mask]
            out[f"mae_nlp_vs_{col}"] = float(diff.abs().mean()) if not diff.empty else None
            out[f"rmse_nlp_vs_{col}"] = float((diff.pow(2).mean()) ** 0.5) if not diff.empty else None

            # Calculate agreement within thresholds
            for thr in [0.25, 0.5, 1.0]:
                out[f"agree_{col}_within_{thr}"] = float((diff.abs() <= thr).mean()) if not diff.empty else None

    # Calculate quantiles for the model's score
    if "nlp_score" in df_q.columns:
        s = _to_numeric(df_q["nlp_score"]).dropna()
        if not s.empty:
            qs = s.quantile([0.1, 0.25, 0.5, 0.75, 0.9]).to_dict()
            out["nlp_score_quantiles"] = {str(k): float(v) for k, v in qs.items()}
            out["nlp_score_min"] = float(s.min())
            out["nlp_score_max"] = float(s.max())
        else:
            out["nlp_score_quantiles"] = {}
            out["nlp_score_min"] = None
            out["nlp_score_max"] = None

    return out

def reference_similarity_stats(desired_answer: str, llm_answers: List[str]) -> Dict[str, Any]:
    """Calculate Jaccard stats for reference answers."""
    desired = desired_answer or ""
    llm_ans = list(llm_answers or [])

    sims = [jaccard(desired, a) for a in llm_ans] if llm_ans else []
    avg_sim = float(sum(sims) / len(sims)) if sims else None
    max_sim = float(max(sims)) if sims else None

    div = pairwise_jaccard_mean(llm_ans)
    diversity = float(div) if div is not None else None

    len_desired = len(_tok(desired))
    len_llm = [len(_tok(x)) for x in llm_ans] if llm_ans else []
    len_llm_avg = float(sum(len_llm) / len(len_llm)) if len_llm else None

    return {
        "desired_vs_llm_avg_jaccard": avg_sim,
        "desired_vs_llm_max_jaccard": max_sim,
        "llm_answer_pairwise_avg_jaccard": diversity,
        "desired_len_tokens": int(len_desired),
        "llm_len_tokens_avg": len_llm_avg,
        "llm_count": len(llm_ans)
    }

# ----------------------------
# 4) Main execution
# ----------------------------
print("\n--- Starting Statistical Analysis ---")

# Load questions (with desired_answer + llm_answers)
try:
    with open(QUESTIONS_JSON_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
    q_df = pd.DataFrame(questions)
    q_df = q_df[["id", "question", "desired_answer", "llm_answers", "max_point"]].copy()
    print(f"Loaded {len(q_df)} questions from {QUESTIONS_JSON_PATH}")
except FileNotFoundError:
    print(f"ERROR: Questions file not found at {QUESTIONS_JSON_PATH}")
    # Stop execution by raising the error
    raise
except Exception as e:
    print(f"ERROR: Could not read or parse questions file: {e}")
    raise

# 2) Read all graded items from the single JSON file
try:
    with open(GRADED_RESULTS_PATH, "r", encoding="utf-8") as f:
        graded_bundles = json.load(f)

    rows = []
    for bundle in graded_bundles:
        qid = bundle.get("question_id")
        for item in bundle.get("items", []):
            r = dict(item)
            # Ensure question_id is present and numeric
            r["question_id"] = int(r.get("question_id", qid))
            rows.append(r)
    
    if not rows:
        raise RuntimeError(f"No graded 'items' found inside {GRADED_RESULTS_PATH}")

    df = pd.DataFrame(rows)
    print(f"Loaded {len(df)} graded answers from {GRADED_RESULTS_PATH}")

except FileNotFoundError:
    print(f"ERROR: Graded results file not found at {GRADED_RESULTS_PATH}")
    raise
except Exception as e:
    print(f"ERROR: Could not read or parse graded results file: {e}")
    raise


# 3) Filter out failed gradings
nlp_score_series = pd.to_numeric(df.get("nlp_score"), errors="coerce")
df["__nlp_failed"] = nlp_score_series.isna()

dropped_total = int(df["__nlp_failed"].sum())
print(f"Found {dropped_total} answers with failed/NaN NLP scores.")

if dropped_total > 0:
    failures_df = df.loc[df["__nlp_failed"]].copy()
    dropped_per_q = (
        failures_df[["question_id"]]
        .groupby("question_id", dropna=False)
        .size()
        .to_dict()
    )
    if WRITE_FAILURES_SAMPLE and not failures_df.empty:
        try:
            sample_json = failures_df.head(200).to_json(orient="records", indent=2)
            with open(FAILURES_SAMPLE_PATH, "w", encoding="utf-8") as f:
                f.write(sample_json)
            print(f"-> Wrote failure sample to {FAILURES_SAMPLE_PATH}")
        except Exception as e:
            print(f"-> Warning: Could not write failure sample: {e}")
else:
    dropped_per_q = {}

# Drop failed rows
df = df.loc[~df["__nlp_failed"]].drop(columns=["__nlp_failed"])
print(f"-> Proceeding with {len(df)} validly graded answers.")

# 4) Per-question stats
print("Calculating per-question statistics...")
per_q = []
grouped = df.groupby("question_id", dropna=False)

for qid, df_q in grouped:
    # Find the matching question row from the questions file
    q_match = q_df[q_df["id"] == qid]
    qrow = q_match.iloc[0] if not q_match.empty else None

    # Calculate all stats for this question's answers
    pq = per_question_stats(df_q)

    # Get reference answer stats
    if qrow is not None:
        ref_stats = reference_similarity_stats(
            qrow.get("desired_answer"),
            qrow.get("llm_answers") or []
        )
        question_text = qrow.get("question")
        max_point = qrow.get("max_point", None)
    else:
        ref_stats = reference_similarity_stats("", [])
        question_text = None
        max_point = None # Will try to get from graded bundle later

    # Get max_point from graded bundle if missing from question file
    if max_point is None:
        try:
            bundle = next(b for b in graded_bundles if b.get("question_id") == qid)
            max_point = bundle.get("max_point", 5.0) # default 5.0
        except StopIteration:
            max_point = 5.0 # default 5.0

    # Assemble the final stats object for this question
    entry = {
        "question_id": int(qid),
        "question": question_text,
        "max_point": float(max_point) if max_point is not None else None,
        "counts": {
            "answers_n": pq.pop("n", 0),
            "dropped_failures": int(dropped_per_q.get(int(qid), 0))
        },
        "scores": {
            "means": {
                "score_me": pq.pop("mean_score_me", None),
                "score_other": pq.pop("mean_score_other", None),
                "score_avg": pq.pop("mean_score_avg", None),
                "nlp_score": pq.pop("mean_nlp_score", None),
            },
            "nlp_quantiles": pq.pop("nlp_score_quantiles", {}),
            "nlp_min": pq.pop("nlp_score_min", None),
            "nlp_max": pq.pop("nlp_score_max", None),
            "agreement_and_errors": {
                "pearson_nlp_vs_score_me": pq.pop("pearson_nlp_vs_score_me", None),
                "pearson_nlp_vs_score_other": pq.pop("pearson_nlp_vs_score_other", None),
                "pearson_nlp_vs_score_avg": pq.pop("pearson_nlp_vs_score_avg", None),
                "mae_nlp_vs_score_me": pq.pop("mae_nlp_vs_score_me", None),
                "mae_nlp_vs_score_other": pq.pop("mae_nlp_vs_score_other", None),
                "mae_nlp_vs_score_avg": pq.pop("mae_nlp_vs_score_avg", None),
                "rmse_nlp_vs_score_me": pq.pop("rmse_nlp_vs_score_me", None),
                "rmse_nlp_vs_score_other": pq.pop("rmse_nlp_vs_score_other", None),
                "rmse_nlp_vs_score_avg": pq.pop("rmse_nlp_vs_score_avg", None),
                "agree_score_me_within": {
                    "0.25": pq.pop("agree_score_me_within_0.25", None),
                    "0.5":  pq.pop("agree_score_me_within_0.5", None),
                    "1.0":  pq.pop("agree_score_me_within_1.0", None),
                },
                "agree_score_other_within": {
                    "0.25": pq.pop("agree_score_other_within_0.25", None),
                    "0.5":  pq.pop("agree_score_other_within_0.5", None),
                    "1.0":  pq.pop("agree_score_other_within_1.0", None),
                },
                "agree_score_avg_within": {
                    "0.25": pq.pop("agree_score_avg_within_0.25", None),
                    "0.5":  pq.pop("agree_score_avg_within_0.5", None),
                    "1.0":  pq.pop("agree_score_avg_within_1.0", None),
                }
            }
        },
        "reference_similarity": ref_stats
    }
    per_q.append(entry)

print(f"-> Calculated stats for {len(per_q)} questions.")

# 5) Overall aggregates
print("Calculating overall statistics...")
overall = {}

def _safe_mean(s: pd.Series) -> float | None:
    s = pd.to_numeric(s, errors="coerce")
    return float(s.mean()) if s is not None and s.notna().any() else None

overall["counts"] = {
    "total_answers": int(len(df)),
    "total_questions": int(len(grouped)),
    "dropped_failures_total": dropped_total
}
overall["means"] = {
    "score_me": _safe_mean(df.get("score_me")),
    "score_other": _safe_mean(df.get("score_other")),
    "score_avg": _safe_mean(df.get("score_avg")),
    "nlp_score": _safe_mean(df.get("nlp_score")),
}

# Overall correlations and errors
for human in ["score_me", "score_other", "score_avg"]:
    if human in df.columns and "nlp_score" in df.columns:
        s1 = pd.to_numeric(df[human], errors="coerce")
        s2 = pd.to_numeric(df["nlp_score"], errors="coerce")
        mask = s1.notna() & s2.notna()
        if mask.sum() > 2:
            overall[f"pearson_nlp_vs_{human}"] = float(s1[mask].corr(s2[mask]))
        else:
            overall[f"pearson_nlp_vs_{human}"] = None
        d = (s2 - s1)[mask]
        overall[f"mae_nlp_vs_{human}"]  = float(d.abs().mean()) if not d.empty else None
        overall[f"rmse_nlp_vs_{human}"] = float((d.pow(2).mean()) ** 0.5) if not d.empty else None

# Overall reference similarity stats
ref_rows = []
for _, r in q_df.iterrows():
    ref_rows.append(reference_similarity_stats(r.get("desired_answer"), r.get("llm_answers") or []))
if ref_rows:
    ref_df = pd.DataFrame(ref_rows)
    overall["reference_similarity"] = {
        "desired_vs_llm_avg_jaccard_mean": _safe_mean(ref_df["desired_vs_llm_avg_jaccard"]),
        "desired_vs_llm_max_jaccard_mean": _safe_mean(ref_df["desired_vs_llm_max_jaccard"]),
        "llm_answer_pairwise_avg_jaccard_mean": _safe_mean(ref_df["llm_answer_pairwise_avg_jaccard"]),
        "desired_len_tokens_mean": _safe_mean(ref_df["desired_len_tokens"]),
        "llm_len_tokens_avg_mean": _safe_mean(ref_df["llm_len_tokens_avg"]),
    }
else:
    overall["reference_similarity"] = {}

# 6) Write result
print(f"Saving final stats to {STATS_OUTPUT_PATH}...")
result = {
    "inputs": {
        "questions_file": QUESTIONS_JSON_PATH,
        "graded_file": GRADED_RESULTS_PATH,
    },
    "overall": overall,
    "per_question": per_q
}

try:
    with open(STATS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ --- Analysis Complete! Stats saved. ---")
except Exception as e:
    print(f"❌ ERROR: Failed to write final stats file: {e}")

# Optional: Print a small summary of overall results
print("\n--- Overall Results Summary ---")
print(json.dumps(result.get("overall"), indent=2))