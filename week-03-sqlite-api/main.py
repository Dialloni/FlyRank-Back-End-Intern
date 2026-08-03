import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- Database setup (Stage 0) -------------------------------------------------
# The DB file lives next to this script, so it works no matter where you run from.
DB_PATH = Path(__file__).parent / "tasks.db"


def get_conn() -> sqlite3.Connection:
    """Open a connection. row_factory lets us read columns by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_task(row: sqlite3.Row) -> dict:
    """Convert a DB row into the same JSON shape the A1 API returned.
    done is stored as 0/1 in SQLite; expose it as a real boolean."""
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "done": bool(row["done"]),
    }


def init_db() -> None:
    """Create the table if missing and seed 3 tasks only when empty.
    Runs once at startup. Restarting never duplicates the seeds."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                done        INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, description, done) VALUES (?, ?, ?)",
                [
                    ("Learn FastAPI", "This is task 1", 0),
                    ("Build CRUD API", "This is task 2", 1),
                    ("Push Code to GitHub", "This is task 3", 0),
                ],
            )
        # `with get_conn()` commits automatically on a clean exit.


app = FastAPI(
    title="Task API",
    description="A CRUD API for managing tasks, now backed by SQLite. Week 3 assignment.",
    version="2.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


class TaskCreated(BaseModel):
    title: str | None = None
    description: str = ""


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool | None = None


@app.get("/", summary="Get API information")
def read_root():
    return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok"}


# --- Read (Stage 1) -----------------------------------------------------------
@app.get("/tasks", summary="List all tasks")
def list_tasks():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    return [row_to_task(r) for r in rows]


@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return row_to_task(row)


# --- Create (Stage 2) ---------------------------------------------------------
@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(payload: TaskCreated):
    if not payload.title or not payload.title.strip():
        raise HTTPException(
            status_code=400, detail="Field 'title' is required and cannot be empty"
        )
    title = payload.title.strip()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, description, done) VALUES (?, ?, ?)",
            (title, payload.description, 0),
        )
        new_id = cur.lastrowid
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    return row_to_task(row)


# --- Update (Stage 3) ---------------------------------------------------------
@app.put("/tasks/{task_id}", summary="Update a task by ID")
def update_task(task_id: int, payload: TaskUpdate):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        task = row_to_task(row)
        if payload.title is not None:
            if not payload.title.strip():
                raise HTTPException(
                    status_code=400, detail="Field 'title' cannot be empty"
                )
            task["title"] = payload.title.strip()
        if payload.description is not None:
            task["description"] = payload.description
        if payload.done is not None:
            task["done"] = payload.done

        conn.execute(
            "UPDATE tasks SET title = ?, description = ?, done = ? WHERE id = ?",
            (task["title"], task["description"], int(task["done"]), task_id),
        )
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return row_to_task(row)


# --- Delete (Stage 3) ---------------------------------------------------------
@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task by ID")
def delete_task(task_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return
