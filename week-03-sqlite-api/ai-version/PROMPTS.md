# Stage 6 — the AI rematch

## My prompt (written from memory)

> I have a FastAPI to-do CRUD API that stores tasks in an in-memory Python list.
> Move the storage to SQLite using the standard-library `sqlite3` module, in a file
> called `tasks.db`. Keep all five endpoints and their behaviour identical:
> `GET /tasks`, `GET /tasks/{id}`, `POST /tasks`, `PUT /tasks/{id}`, `DELETE /tasks/{id}`.
> Create a `tasks` table if it doesn't exist with columns id (integer primary key),
> title (text), done (boolean 0/1). Seed three example tasks, but only when the table
> is empty. Use parameterized queries everywhere (no f-strings in SQL). Keep the same
> status codes: 400 on missing/empty title, 404 on unknown id, 201 on create, 204 on delete.

## Rematch (round 2)

Improved prompt added one sentence:

> The task JSON shape must stay exactly `{id, title, description, done}` — do not drop the
> `description` field — and seed the three tasks in a single transaction.

Result: round 2 kept the `description` column and wrapped the seed in one commit, matching
my hand-built version.

See the "AI vs me" section in the main README for the concrete differences.
