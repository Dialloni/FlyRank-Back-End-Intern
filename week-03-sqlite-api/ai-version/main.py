# AI-generated version (Stage 6 rematch) — kept in quarantine, NOT the submission.
# This is round-1 output from the prompt in PROMPTS.md, left intact so it can be
# diffed against the hand-built ../main.py.
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# AI decision: one module-level connection shared across all requests.
conn = sqlite3.connect("tasks.db", check_same_thread=False)
conn.row_factory = sqlite3.Row

# AI decision: dropped the `description` column — the prompt didn't mention it.
conn.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0
    )
    """
)

# AI decision: three separate inserts, no explicit transaction wrapper.
if conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
    conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Learn FastAPI", 0))
    conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Build CRUD API", 1))
    conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Push Code to GitHub", 0))
    conn.commit()

app = FastAPI(title="Task API (AI version)")


class TaskIn(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


def to_dict(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.get("/tasks")
def list_tasks():
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    return [to_dict(r) for r in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return to_dict(row)


@app.post("/tasks", status_code=201)
def create_task(payload: TaskIn):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    cur = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)", (payload.title.strip(), 0)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    return to_dict(row)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task = to_dict(row)
    if payload.title is not None:
        task["title"] = payload.title.strip()
    if payload.done is not None:
        task["done"] = payload.done
    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (task["title"], int(task["done"]), task_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return to_dict(row)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return
