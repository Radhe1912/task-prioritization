"""
Priority Scoring Formula

score = urgency+importance+effort-infeasibility_penalty
Final score is clamped to [0, 100].

URGENCY (0-40 pts) =>
  urgency = max(0, (10 - deadline_days) * 4)
  Deadline 0 days  -> 40 pts
  Deadline 10 days ->  0 pts
  Deadline > 10    ->  0 pts

IMPORTANCE (4-40 pts)
  importance_score = importance * 4   (importance: 1-10)
  Minimum 4 so every task contributes a baseline.

EFFORT (0-20 pts)
  effort_score = max(0, 20 - estimated_hours)
  Quick-win heuristic: shorter tasks score higher.
  Tasks over 20 hours contribute 0 effort points.

INFEASIBILITY PENALTY (-20 pts)
  Applied when: estimated_hours > deadline_days * 8
  Task is still returned — the penalty surfaces the problem
  without discarding the task.

DEADLINE=0 OVERRIDE
  Any task due today is forced to at least 70 (High Priority),
  regardless of importance or effort. If it's due today, it must
  be done today — deferral is not possible.

CATEGORIES
  score >= 70  -> High Priority
  score >= 40  -> Medium Priority
  score <  40  -> Low Priority

WHY THESE WEIGHTS?
  Urgency and importance are equal at their maximums (both 40).
  Neither dominates the other by default.
  Effort is half-weight (max 20) — tiebreaker and quick-win signal.
  Infeasibility penalty (20 pts) drops a borderline score by one
  category to flag the timing problem.
"""

URGENCY_MAX_DAYS = 10
URGENCY_WEIGHT = 4
IMPORTANCE_WEIGHT = 4
EFFORT_MAX_HOURS = 20
INFEASIBILITY_PENALTY = 20
WORKING_HOURS_PER_DAY = 8

HIGH_PRIORITY_THRESHOLD = 70
MEDIUM_PRIORITY_THRESHOLD = 40


def _compute_urgency(deadline_days: int) -> float:
    days = min(deadline_days, URGENCY_MAX_DAYS)
    return max(0.0, (URGENCY_MAX_DAYS - days) * URGENCY_WEIGHT)


def _compute_importance(importance: int) -> float:
    return float(importance * IMPORTANCE_WEIGHT)


def _compute_effort(estimated_hours: float) -> float:
    return max(0.0, EFFORT_MAX_HOURS - estimated_hours)


def _is_infeasible(deadline_days: int, estimated_hours: float) -> bool:
    return estimated_hours > deadline_days * WORKING_HOURS_PER_DAY


def _assign_category(score: float) -> str:
    if score >= HIGH_PRIORITY_THRESHOLD:
        return "High Priority"
    if score >= MEDIUM_PRIORITY_THRESHOLD:
        return "Medium Priority"
    return "Low Priority"


def calculate_priority(task: dict) -> tuple[float, str]:
    """
    Compute (priority_score, priority_category) for a validated task dict.
    Deterministic: same input always produces same output.

    Expected keys:
        deadline_days   (int   >= 0)
        estimated_hours (float >= 0)
        importance      (int   1-10)
    """
    deadline_days   = task["deadline_days"]
    estimated_hours = task["estimated_hours"]
    importance      = task["importance"]

    raw = (
        _compute_urgency(deadline_days)
        + _compute_importance(importance)
        + _compute_effort(estimated_hours)
    )

    if _is_infeasible(deadline_days, estimated_hours):
        raw -= INFEASIBILITY_PENALTY

    score = round(max(0.0, min(100.0, raw)), 2)

    if deadline_days == 0 and score < HIGH_PRIORITY_THRESHOLD:
        score = float(HIGH_PRIORITY_THRESHOLD)

    category = _assign_category(score)
    return score, category