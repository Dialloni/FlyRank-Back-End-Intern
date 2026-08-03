"""Storage layer. The routes depend only on the TaskRepository interface,
so switching from in-memory to Postgres changes one line in main.py and
nothing else. That is the whole point of A3."""
from abc import ABC, abstractmethod

import psycopg
from psycopg.rows import dict_row


class TaskNotFound(Exception):
    """Raised when an id doesn't exist. Routes turn this into a 404."""


class TaskRepository(ABC):
    """The contract every storage backend must satisfy. Identical shape to
    the in-memory version from A1/A2 — that's why the swap is invisible."""

    @abstractmethod
    def list(self) -> list[dict]: ...

    @abstractmethod
    def get(self, task_id: int) -> dict: ...

    @abstractmethod
    def create(self, title: str, description: str) -> dict: ...

    @abstractmethod
    def update(self, task_id: int, title, description, done) -> dict: ...

    @abstractmethod
    def delete(self, task_id: int) -> None: ...


# --- In-memory (kept from A1/A2 to prove the interface is real) ---------------
class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._tasks: list[dict] = []
        self._next_id = 1

    def list(self) -> list[dict]:
        return list(self._tasks)

    def get(self, task_id: int) -> dict:
        for t in self._tasks:
            if t["id"] == task_id:
                return t
        raise TaskNotFound

    def create(self, title: str, description: str) -> dict:
        task = {"id": self._next_id, "title": title, "description": description, "done": False}
        self._next_id += 1
        self._tasks.append(task)
        return task

    def update(self, task_id, title, description, done) -> dict:
        task = self.get(task_id)
        if title is not None:
            task["title"] = title
        if description is not None:
            task["description"] = description
        if done is not None:
            task["done"] = done
        return task

    def delete(self, task_id: int) -> None:
        for i, t in enumerate(self._tasks):
            if t["id"] == task_id:
                del self._tasks[i]
                return
        raise TaskNotFound


# --- Postgres (the A3 swap-in) ------------------------------------------------
class PostgresTaskRepository(TaskRepository):
    """Same interface, backed by Postgres. All queries parameterized."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._init_schema()

    def _conn(self) -> psycopg.Connection:
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def _init_schema(self) -> None:
        """Idempotent: create the table if missing and seed 3 tasks only when
        empty. Safe alongside db/init.sql — whichever runs first, no dupes."""
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id          SERIAL PRIMARY KEY,
                    title       TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    done        BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )
            count = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
            if count == 0:
                conn.executemany(
                    "INSERT INTO tasks (title, description, done) VALUES (%s, %s, %s)",
                    [
                        ("Learn FastAPI", "This is task 1", False),
                        ("Build CRUD API", "This is task 2", True),
                        ("Push Code to GitHub", "This is task 3", False),
                    ],
                )

    def list(self) -> list[dict]:
        with self._conn() as conn:
            return conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()

    def get(self, task_id: int) -> dict:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = %s", (task_id,)
            ).fetchone()
        if row is None:
            raise TaskNotFound
        return row

    def create(self, title: str, description: str) -> dict:
        with self._conn() as conn:
            return conn.execute(
                "INSERT INTO tasks (title, description, done) "
                "VALUES (%s, %s, FALSE) RETURNING *",
                (title, description),
            ).fetchone()

    def update(self, task_id, title, description, done) -> dict:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = %s", (task_id,)
            ).fetchone()
            if row is None:
                raise TaskNotFound
            new_title = title if title is not None else row["title"]
            new_desc = description if description is not None else row["description"]
            new_done = done if done is not None else row["done"]
            return conn.execute(
                "UPDATE tasks SET title = %s, description = %s, done = %s "
                "WHERE id = %s RETURNING *",
                (new_title, new_desc, new_done, task_id),
            ).fetchone()

    def delete(self, task_id: int) -> None:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            if cur.rowcount == 0:
                raise TaskNotFound
