URGENCY_MAX_DAYS = 10       # Days beyond which urgency contribution = 0
URGENCY_WEIGHT = 4          # Points per day remaining inside the window
IMPORTANCE_WEIGHT = 4       # Points per importance unit
EFFORT_MAX_HOURS = 20       # Hours beyond which effort contribution = 0
INFEASIBILITY_PENALTY = 20  # Score penalty for tasks that can't fit before deadline
WORKING_HOURS_PER_DAY = 8

HIGH_PRIORITY_THRESHOLD = 70
MEDIUM_PRIORITY_THRESHOLD = 40


def _compute_urgency(deadline_days: int) -> float:
    """Return urgency contribution (0–40). Maxes out when deadline is 0 days."""
    days_remaining = min(deadline_days, URGENCY_MAX_DAYS)
    return max(0, (URGENCY_MAX_DAYS - days_remaining) * URGENCY_WEIGHT)


def _compute_importance(importance: int) -> float:
    """Return importance contribution (4–40)."""
    return importance * IMPORTANCE_WEIGHT


def _compute_effort(estimated_hours: float) -> float:
    """Return effort contribution (0–20). Quick tasks score higher (quick-win heuristic)."""
    return max(0.0, EFFORT_MAX_HOURS - estimated_hours)


def _is_infeasible(deadline_days: int, estimated_hours: float) -> bool:
    """True if the task cannot realistically fit within the available time."""
    available_hours = deadline_days * WORKING_HOURS_PER_DAY
    return estimated_hours > available_hours


def _assign_category(score: float) -> str:
    if score >= HIGH_PRIORITY_THRESHOLD:
        return "High Priority"
    if score >= MEDIUM_PRIORITY_THRESHOLD:
        return "Medium Priority"
    return "Low Priority"


def calculate_priority(task: dict) -> tuple[float, str]:
    """
    Compute (priority_score, priority_category) for a validated task dict.

    Expected keys: deadline_days (int >= 0), estimated_hours (float >= 0),
                   importance (int 1–10).
    Returns a (score, category) tuple. Score is deterministic for the same input.
    """
    deadline_days = task["deadline_days"]
    estimated_hours = task["estimated_hours"]
    importance = task["importance"]

    urgency = _compute_urgency(deadline_days)
    importance_score = _compute_importance(importance)
    effort_score = _compute_effort(estimated_hours)

    raw_score = urgency + importance_score + effort_score

    if _is_infeasible(deadline_days, estimated_hours):
        raw_score -= INFEASIBILITY_PENALTY

    score = round(max(0.0, min(100.0, raw_score)), 2)
    category = _assign_category(score)

    return score, category