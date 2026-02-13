# Task Prioritization System

A REST API that scores and ranks tasks by urgency, importance, and effort. Built with Django REST Framework + React.

---

## Project Overview

Users submit tasks with a deadline, estimated hours, and importance level. The system assigns each task a priority score (0–100) and categorizes it as High, Medium, or Low priority. Results are saved to PostgreSQL and returned sorted by score.

---

## Architecture

```
└── 📁backend
    └── 📁backend
        ├── __init__.py
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        ├── wsgi.py
    └── 📁tasks
        └── 📁migrations
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── models.py
        ├── serializers.py
        ├── services.py
        ├── tests.py
        ├── urls.py
        ├── views.py
    └── manage.py

└── 📁frontend
    └── 📁src
        ├── App.css
        ├── App.jsx
        ├── main.jsx
    ├── eslint.config.js
    ├── index.html
    ├── package-lock.json
    ├── package.json
    └── vite.config.js
```

**Key design decisions:**

- `services.py` has zero Django imports — scoring logic is completely isolated and independently testable.
- Two serializers: `TaskInputSerializer` for validation (no DB fields required), `TaskOutputSerializer` for responses. This prevents computed fields from being required on input.
- `update_or_create` on `task_id` makes the prioritize endpoint idempotent — resubmitting the same task updates rather than duplicates.
- Business logic never lives in views; views only handle HTTP and DB calls.

**Database — PostgreSQL**

Chosen for strong data integrity, reliable concurrent writes, and long-term scalability. Tasks are persisted so scoring history is retrievable via `GET /tasks` without resubmitting.

---

## Prioritization Logic

```
score = urgency + importance + effort − infeasibility_penalty
score = clamp(score, 0, 100)
```

| Component | Range | Formula |
|---|---|---|
| Urgency | 0–40 pts | `max(0, (10 − deadline_days) × 4)` |
| Importance | 4–40 pts | `importance × 4` |
| Effort | 0–20 pts | `max(0, 20 − estimated_hours)` |
| Infeasibility penalty | −20 pts | applied when `hours > deadline_days × 8` |

**Urgency** decays linearly over 10 days. Deadlines beyond 10 days contribute 0 urgency — the window is intentional to keep urgency meaningful.

**Importance** scales 1–10. Minimum contribution is 4 (not 0) so even low-importance tasks register a baseline.

**Effort** rewards quick tasks (quick-win heuristic). A 1-hour task fits in any gap; a 20-hour task needs dedicated blocks. Tasks over 20 hours contribute 0.

**Infeasibility penalty** flags tasks that cannot physically fit before the deadline (assuming 8 working hours/day). The task is not rejected — the reduced score surfaces the problem.

**Categories:**

| Score | Category |
|---|---|
| ≥ 70 | High Priority |
| ≥ 40 | Medium Priority |
| < 40 | Low Priority |

---

## Edge Case Handling

| Case | Behavior |
|---|---|
| `deadline_days = 0` | Urgency maxes at 40. Any task with `hours > 0` triggers infeasibility penalty. Score forced to minimum 70 (High) — a today task cannot be deferred. |
| Task cannot fit before deadline | Infeasibility penalty (−20) applied. Task still returned with reduced score. |
| Equal scores | Stable sort preserves submission order. DB tiebreaker uses `created_at`. |
| Invalid/missing fields | Task rejected, returned in `invalid` list with per-field error. Not saved to DB. |
| `importance` outside 1–10 | Validation error with reason. |
| Malformed body (not a list) | Returns `400 {"error": "Request body must be a JSON array"}` |
| Mixed valid/invalid in one request | Valid tasks scored and saved. Invalid collected separately. Request does not abort. |
| Re-submitting same `task_id` | `update_or_create` overwrites existing record. No duplicates. |

---

## API Endpoints

### `GET /health`
Confirms the service is running.

**Response 200**
```json
{ "status": "ok" }
```

---

### `GET /tasks`
Returns all previously scored tasks, sorted by priority score descending.

**Response 200**
```json
{
  "count": 2,
  "tasks": [
    {
      "task_id": "1",
      "title": "Fix critical bug",
      "deadline_days": 1,
      "estimated_hours": 3,
      "importance": 10,
      "priority_score": 83.0,
      "priority_category": "High Priority"
    }
  ]
}
```

---

### `POST /tasks/validate`
Validates tasks without scoring. Use to check input before submitting.

**Request body**
```json
[
  { "task_id": "1", "title": "Write report", "deadline_days": 3, "estimated_hours": 4, "importance": 8 }
]
```

**Response 200**
```json
{ "valid_count": 1, "invalid_count": 0, "valid": [...], "invalid": [] }
```

---

### `POST /tasks/prioritize`
Scores, categorizes, and saves tasks. Returns results sorted by score descending.

**Request body** — same shape as `/tasks/validate`

**Response 200**
```json
{
  "prioritized_count": 1,
  "invalid_count": 0,
  "prioritized": [
    {
      "task_id": "1",
      "title": "Write report",
      "deadline_days": 3,
      "estimated_hours": 4,
      "importance": 8,
      "priority_score": 76.0,
      "priority_category": "High Priority"
    }
  ],
  "invalid": []
}
```

**Response 400** — malformed body
```json
{ "error": "Request body must be a JSON array of task objects." }
```

---

## Setup & Run

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend

```bash
git clone <repo-url>
cd backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Create the database
psql -U postgres -c "CREATE DATABASE task_db;"

# Set environment variables
export DJANGO_SECRET_KEY="your-secret-key"
export DJANGO_DEBUG="True"
export DB_PASSWORD="your-db-password"

python manage.py migrate
python manage.py runserver
```

API available at `http://127.0.0.1:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI available at `http://localhost:5173`

### Quick Test (curl)

```bash
curl -X POST http://127.0.0.1:8000/tasks/prioritize/ \
  -H "Content-Type: application/json" \
  -d '[
    {"task_id":"1","title":"Fix bug","deadline_days":1,"estimated_hours":3,"importance":10},
    {"task_id":"2","title":"Update docs","deadline_days":14,"estimated_hours":2,"importance":4}
  ]'
```