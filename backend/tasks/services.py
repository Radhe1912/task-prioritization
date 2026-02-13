"""
Priority Scoring Formula

score = urgency + importance + effort - infeasibility_penalty
Final score is clamped to [0, 100].

URGENCY (0-40 pts)
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


class PriorityCalculator:

    URGENCY_MAX_DAYS = 10
    URGENCY_WEIGHT = 4
    IMPORTANCE_WEIGHT = 4
    EFFORT_MAX_HOURS = 20
    INFEASIBILITY_PENALTY = 20
    WORKING_HOURS_PER_DAY = 8

    HIGH_PRIORITY_THRESHOLD = 70
    MEDIUM_PRIORITY_THRESHOLD = 40

    def _compute_urgency(self, deadline_days: int) -> float:
        days = min(deadline_days, self.URGENCY_MAX_DAYS)
        return max(0.0, (self.URGENCY_MAX_DAYS - days) * self.URGENCY_WEIGHT)

    def _compute_importance(self, importance: int) -> float:
        return float(importance * self.IMPORTANCE_WEIGHT)

    def _compute_effort(self, estimated_hours: float) -> float:
        return max(0.0, self.EFFORT_MAX_HOURS - estimated_hours)

    def _is_infeasible(self, deadline_days: int, estimated_hours: float) -> bool:
        return estimated_hours > deadline_days * self.WORKING_HOURS_PER_DAY

    def _assign_category(self, score: float) -> str:
        if score >= self.HIGH_PRIORITY_THRESHOLD:
            return "High Priority"
        if score >= self.MEDIUM_PRIORITY_THRESHOLD:
            return "Medium Priority"
        return "Low Priority"

    def calculate(self, task: dict) -> tuple[float, str]:
        deadline_days = task["deadline_days"]
        estimated_hours = task["estimated_hours"]
        importance = task["importance"]

        raw = (
            self._compute_urgency(deadline_days)
            + self._compute_importance(importance)
            + self._compute_effort(estimated_hours)
        )

        if self._is_infeasible(deadline_days, estimated_hours):
            raw -= self.INFEASIBILITY_PENALTY

        score = round(max(0.0, min(100.0, raw)), 2)

        # Tasks due today cannot be deferred — force High Priority
        if deadline_days == 0 and score < self.HIGH_PRIORITY_THRESHOLD:
            score = float(self.HIGH_PRIORITY_THRESHOLD)

        return score, self._assign_category(score)
