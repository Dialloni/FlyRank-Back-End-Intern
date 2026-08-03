import sqlite3
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

# --- Database setup (Stage 0) -------------------------------------------------
# The DB file lives next to this script, so it works no matter where you run from.
DB_PATH = Path(__file__).parent / "tasks.db"


def get_conn() -> sqlite3.Connection:
    """Open a connection. row_factory lets us read columns by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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


@app.get("/", summary="Get API information")
def read_root():
    return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok"}
