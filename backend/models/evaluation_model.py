"""
evaluation_model.py – Evaluation scoring operations.
"""
from models import query_one, query_all, execute


def get_scores_for_submission(sub_id: int, evaluator_id: int) -> list[dict]:
    return query_all(
        """SELECT e.*, ec.name as criteria_name, ec.max_score, ec.weightage as weight
           FROM evaluations e JOIN evaluation_criteria ec ON ec.id=e.criteria_id
           WHERE e.submission_id=%s AND e.evaluator_id=%s""",
        (sub_id, evaluator_id),
    )


def get_all_scores_for_submission(sub_id: int) -> list[dict]:
    """Aggregated scores across all evaluators per criterion."""
    return query_all(
        """SELECT ec.id as criteria_id, ec.name, ec.max_score, ec.weightage as weight,
                  AVG(e.score) as avg_score,
                  GROUP_CONCAT(e.comments SEPARATOR ' | ') as comments
           FROM evaluation_criteria ec
           JOIN competition_rounds cr ON cr.id = ec.round_id
           LEFT JOIN evaluations e ON e.criteria_id=ec.id AND e.submission_id=%s
           WHERE cr.competition_id = (
               SELECT competition_id FROM submissions WHERE id=%s
           )
           GROUP BY ec.id""",
        (sub_id, sub_id),
    )


def upsert_score(sub_id: int, evaluator_id: int, criteria_id: int, score: float, comments: str | None) -> None:
    execute(
        """INSERT INTO evaluations (submission_id, evaluator_id, criteria_id, score, comments)
           VALUES (%s,%s,%s,%s,%s)
           ON DUPLICATE KEY UPDATE score=%s, comments=%s""",
        (sub_id, evaluator_id, criteria_id, score, comments, score, comments),
    )


def get_submissions_for_evaluator(evaluator_id: int, comp_id: int | None = None, round_id: int | None = None) -> list[dict]:
    """Approved submissions in competitions the evaluator is assigned to."""
    base = """
        SELECT s.*, t.name as team_name, c.title as comp_title, cr.title as round_name,
               (SELECT COUNT(DISTINCT e.criteria_id) FROM evaluations e
                WHERE e.submission_id=s.id AND e.evaluator_id=%s) as scored_criteria,
               (SELECT COUNT(*) FROM evaluation_criteria ec JOIN competition_rounds cr2 ON cr2.id=ec.round_id WHERE cr2.competition_id=s.competition_id) as total_criteria
        FROM submissions s
        JOIN teams t ON t.id=s.team_id
        JOIN competitions c ON c.id=s.competition_id
        JOIN competition_rounds cr ON cr.id=s.round_id
        WHERE s.status='approved'
          AND s.competition_id IN (
              SELECT competition_id FROM competition_evaluators WHERE evaluator_id=%s
          )
    """
    params: list = [evaluator_id, evaluator_id]
    if comp_id:
        base += " AND s.competition_id=%s"
        params.append(comp_id)
    if round_id:
        base += " AND s.round_id=%s"
        params.append(round_id)
    base += " ORDER BY s.submitted_at DESC"
    return query_all(base, tuple(params))


def get_leaderboard(comp_id: int, round_id: int | None = None) -> list[dict]:
    """Weighted total score per team for a competition/round."""
    round_filter = "AND s.round_id=%s" if round_id else ""
    params: tuple = (comp_id, round_id) if round_id else (comp_id,)
    return query_all(
        f"""SELECT t.name as team_name, sp.full_name as leader,
                   COUNT(DISTINCT e.evaluator_id) as evaluators,
                   SUM(e.score * ec.weightage) / SUM(ec.weightage) as total_score
            FROM evaluations e
            JOIN evaluation_criteria ec ON ec.id=e.criteria_id
            JOIN submissions s ON s.id=e.submission_id
            JOIN teams t ON t.id=s.team_id
            LEFT JOIN student_profiles sp ON sp.user_id=t.leader_id
            WHERE s.competition_id=%s {round_filter}
            GROUP BY s.team_id
            ORDER BY total_score DESC""",
        params,
    )
