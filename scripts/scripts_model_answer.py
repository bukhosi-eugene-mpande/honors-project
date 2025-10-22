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

import numpy as np
import torch
from scipy.special import expit as sigmoid
from sentence_transformers import SentenceTransformer, CrossEncoder, util

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
