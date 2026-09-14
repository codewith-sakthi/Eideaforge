"""
evaluation_service.py – Evaluation scoring business logic.
"""
from models import evaluation_model, competition_model


def submit_scores(sub_id: int, evaluator_id: int, scores: dict) -> dict:
    """
    scores = { criteria_id: { score: float, comments: str } }
    """
    if not scores:
        return {"success": False, "error": "No scores provided."}
    for criteria_id, val in scores.items():
        score = float(val.get("score", 0))
        comments = val.get("comments")
        evaluation_model.upsert_score(sub_id, evaluator_id, int(criteria_id), score, comments)
    return {"success": True}


def get_result_for_submission(sub_id: int, evaluator_id: int) -> dict:
    return {
        "scores": evaluation_model.get_scores_for_submission(sub_id, evaluator_id),
        "aggregated": evaluation_model.get_all_scores_for_submission(sub_id),
    }


def get_leaderboard(comp_id: int, round_id: int | None = None) -> list:
    return evaluation_model.get_leaderboard(comp_id, round_id)


def get_student_results(user_id: int) -> list:
    from models.submission_model import get_for_user
    subs = get_for_user(user_id)
    result = []
    for sub in subs:
        breakdown = evaluation_model.get_all_scores_for_submission(sub["id"])
        total = sum(
            (row["avg_score"] or 0) * row["weight"] for row in breakdown
        )
        result.append({**sub, "breakdown": breakdown, "total_score": total})
    return result
