# Week 3 · A3 (BE-04) — Containerize the stack

The A2 Task API, now backed by **Postgres running in Docker**, with app + database
started by **one command**. Storage moved from SQLite to a Postgres repository — and
the routes and service did **not** change. That is the architecture proving itself.

## Run the whole stack

```bash
cd week-03-docker-postgres
cp .env.example .env      # then edit the password if you like
docker compose up --build
```

That starts two containers — `db` (Postgres 18) and `app` (FastAPI) — and the app waits
for the database to be healthy before booting. API at <http://localhost:8000>, Swagger at
<http://localhost:8000/docs>.

## Configuration — `.env`

The connection string lives in `.env`, which is **git-ignored**. A committed
[`.env.example`](.env.example) documents every variable. Nothing secret is in the repo.

```
DATABASE_URL=postgresql://taskuser:...@db:5432/tasks
```

Host `db` is the compose service name. Use `localhost` if you run the app outside Docker.

## The table

Created + seeded by one SQL file, [`db/init.sql`](db/init.sql), which Docker runs once on
first volume init (mounted into `/docker-entrypoint-initdb.d/`). The app also ensures the
same schema idempotently at startup, so a fresh database is ready either way — and the seed
never duplicates (three tasks are inserted only when the table is empty).

## "Only the storage changed" — honestly

The routes in [`app/main.py`](app/main.py) call a `TaskRepository` interface and never
mention SQL, Postgres, or connections. Swapping storage is **one line**:

```python
repo = PostgresTaskRepository(os.environ["DATABASE_URL"])   # or InMemoryTaskRepository()
```

Both implementations live in [`app/repository.py`](app/repository.py) and satisfy the same
five-method interface carried over from A1/A2. Set `REPO_BACKEND=memory` in `.env` to flip
back to the in-memory store with zero code changes — the endpoints behave identically. All
Postgres queries use parameterized placeholders (`%s`), never string interpolation.

## Persistence proven

Data survives an **app + container** restart. How it was checked:

1. `docker compose up --build` → `GET /tasks` shows the 3 seeded tasks.
2. `POST /tasks` a 4th task ("Survive Docker restart") → `id: 4`.
3. `docker compose down` — **containers removed, the named volume kept** (no `-v`).
4. `docker compose up -d` again → `GET /tasks` still returns all **four** tasks.

Because the data lives in a Docker **named volume** (`pgdata`), destroying and recreating the
containers does not lose it. Only `docker compose down -v` wipes the volume.

## Endpoints (unchanged from A2)

| Method | Path | Success | Errors |
|--------|------|---------|--------|
| GET | `/tasks` | 200 | — |
| GET | `/tasks/{id}` | 200 | 404 |
| POST | `/tasks` | 201 | 400 empty title |
| PUT | `/tasks/{id}` | 200 | 400 · 404 |
| DELETE | `/tasks/{id}` | 204 | 404 |

## Stop the stack

```bash
docker compose down       # keeps your data
docker compose down -v    # also deletes the volume (fresh start next time)
```
