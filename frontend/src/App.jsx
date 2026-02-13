import { useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

const emptyTask = () => ({
  title: "", deadline_days: "", estimated_hours: "", importance: "",
});

const toPayload = (t) => ({
  title: t.title,
  deadline_days: t.deadline_days === "" ? undefined : Number(t.deadline_days),
  estimated_hours: t.estimated_hours === "" ? undefined : Number(t.estimated_hours),
  importance: t.importance === "" ? undefined : Number(t.importance),
});

const FIELDS = [
  ["title", "Title", "text"],
  ["deadline_days", "Deadline (days)", "number"],
  ["estimated_hours", "Estimated Hours", "number"],
  ["importance", "Importance (1–10)", "number"],
];

export default function App() {
  const [tasks, setTasks] = useState([emptyTask()]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const update = (i, field, val) =>
    setTasks((prev) => prev.map((t, idx) => idx === i ? { ...t, [field]: val } : t));

  const submit = async () => {
    setError(null); setResult(null);
    try {
      const res = await fetch(`${API_BASE}/tasks/prioritize/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tasks.map(toPayload)),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.error ?? `Error ${res.status}`); return; }
      setResult(data);
    } catch (e) { setError(e.message); }
  };

  return (
    <div className="container">
      <h2>Task Prioritization</h2>

      {tasks.map((t, i) => (
        <div key={t.task_id} className="card">
          <div className="card-head">
            <span>Task {i + 1}</span>
            <button onClick={() => setTasks((p) => p.filter((_, j) => j !== i))}>Remove</button>
          </div>
          <div className="grid">
            {FIELDS.map(([field, label, type]) => (
              <label key={field}>{label}
                <input type={type} value={t[field]}
                  onChange={(e) => update(i, field, e.target.value)} />
              </label>
            ))}
          </div>
        </div>
      ))}

      <div className="actions">
        <button onClick={() => setTasks((p) => [...p, emptyTask()])}>+ Add Task</button>
        <button className="primary" onClick={submit}>Prioritize</button>
      </div>

      {error && <p className="error">{error}</p>}

      {result?.prioritized?.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Score</th>
              <th>Category</th>
              <th>Days</th>
              <th>Hours</th>
              <th>Imp.</th>
            </tr>
          </thead>
          <tbody>
            {result.prioritized.map((r) => (
              <tr key={r.task_id}>
                <td>{r.title}</td>
                <td>{r.priority_score}</td>
                <td><span className={`badge ${r.priority_category.split(" ")[0].toLowerCase()}`}>{r.priority_category}</span></td>
                <td>{r.deadline_days}</td>
                <td>{r.estimated_hours}</td>
                <td>{r.importance}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {result?.invalid?.length > 0 && (
        <div className="invalid">
          <strong>Invalid ({result.invalid.length})</strong>
          {result.invalid.map((item, i) => (
            <p key={i}>{item.task?.title || "—"} — {JSON.stringify(item.errors)}</p>
          ))}
        </div>
      )}
    </div>
  );
}