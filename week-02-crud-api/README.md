# Week 2 — Task API (CRUD)

A small REST API for managing a to-do list, built with **Python + FastAPI**.
Supports the four CRUD operations over an **in-memory** list — no database, no files.

Interactive docs (Swagger UI) are served at `/docs`.

## Install & run

```bash
cd week-02-crud-api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn main:app --reload
```

Server starts at <http://localhost:8000>. Swagger UI: <http://localhost:8000/docs>.

## Endpoints

| Method | Path | Purpose | Success | Errors |
|--------|------|---------|---------|--------|
| GET | `/` | API info | 200 | — |
| GET | `/health` | Health check | 200 | — |
| GET | `/tasks` | List all tasks | 200 | — |
| GET | `/tasks/{task_id}` | Get one task | 200 | 404 unknown id |
| POST | `/tasks` | Create a task | 201 | 400 missing/empty title |
| PUT | `/tasks/{task_id}` | Update a task | 200 | 400 empty title · 404 unknown id |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 | 404 unknown id |

### Task shape

```json
{ "id": 1, "title": "Learn FastAPI", "description": "This is task 1", "done": false }
```

`id` and `done` are set by the server — the client never sends them on create.

### Validation rules

- `POST /tasks` requires a non-empty `title`. Missing field, `""`, or `"   "` all return **400**.
- `PUT /tasks/{id}` accepts any subset of `title`, `description`, `done`. Omitted fields are left
  unchanged; a `title` that is present but blank returns **400**.

## Example request

```
$ curl -i -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d '{"title":"Buy milk"}'
HTTP/1.1 201 Created
date: Tue, 21 Jul 2026 08:11:15 GMT
server: uvicorn
content-length: 57
content-type: application/json

{"id":4,"title":"Buy milk","description":"","done":false}
```

## Swagger UI

![Swagger UI showing all seven endpoints](docs/swagger.png)

Every endpoint can be exercised from this page with "Try it out" — the full
create → read → update → delete cycle works without touching a terminal.

## The mortality experiment

Create a few tasks, restart the server, then `GET /tasks`: the new tasks are gone and the
original three are back. The task list is a plain Python list living in the process's memory,
so it dies with the process and is rebuilt from the literal in `main.py` on every start.

That is exactly the problem a database solves — storage that outlives the program that wrote it.

## AI vs me (Stage 7)

After building Stages 0–6 by hand, I asked an AI to build the same API from a prompt I wrote
from memory. Its code lives in [`ai-version/`](ai-version/) and is never mixed with mine.

### My prompt (round 1, exactly as written)

> write me a CRUD using the FastAPI to do it and comparing it to me working and tell me whats
> the diff. also you should use the 200, 300, or the 400 to show or specify how they work like
> 404 not fpund, 204 not content, 200 for created, and the rest as well

The AI's version started on the first try. But every one of my Stage 4 checkpoint curls returned
**404** against it, because it built `/items`, not `/tasks` — I never said what the resource was.

`git diff --no-index main.py ai-version/main.py` → 52 insertions, 69 deletions.

### 1. What the AI did better

It tracks ids with a `global next_id` counter that only ever increments. I used
`max(ids) + 1`, which reuses an id after a delete: delete task 3, create a new one, and it
becomes task 3 again — a different task wearing a dead task's id. The AI's version is safer.

### 2. What the AI got wrong

- **`200` on create instead of `201`.** My prompt literally said "200 for created", and it
  obeyed. The AI implemented my mistake faithfully — it did not correct me.
- **No validation at all.** `{"name":"   "}` returns 200 and stores a blank item; `{}` returns
  422 rather than 400. My version returns 400 for both. I never stated a validation rule, so
  the AI wrote none.
- **PUT is destructive.** Sending `{"name":"x"}` wipes `description` to `null`, because its PUT
  replaces the whole object. Mine merges, leaving unsent fields untouched.
- **Unhelpful 404 body.** `"Item not found"` with no id, versus my `"Task 999 not found"`.

### 3. What my prompt forgot to specify

My prompt was vague, so the AI decided these for me without asking:

| It chose | I built | What my prompt left out |
|----------|---------|--------------------------|
| `/items` | `/tasks` | The resource was never named — "CRUD" doesn't say *of what*. |
| `name`, `description` | `title`, `description`, `done` | No fields specified. It produced a to-do API with **no way to mark a task done**. |
| no `/` or `/health` | both | Never mentioned. |
| empty list at boot | 3 seeded tasks | Never mentioned. |
| `global next_id` | `max(ids) + 1` | Never mentioned — and here its guess beat mine. |
| bare `FastAPI()` | title, version, 7 endpoint summaries | I never said "Swagger", so `/docs` exists but is unlabeled. |

I also mixed an instruction to the assistant ("tell me whats the diff") into a spec that should
only describe the software.

### The rematch (round 2)

I rewrote the prompt naming the resource, every field, each status code, the validation rules,
the seed data, the id strategy and the Swagger requirements — and switched `PUT` to `PATCH`
since I wanted merge semantics.

**One sentence on what changed:** every gap from round 1 closed — create returns 201, both bad
bodies return 400, the 404 body names the id, the data is seeded and `/docs` is labeled — but
being precise exposed a different failure mode: contradictions *inside* the spec.

Three of them survived into the code:

- **My id rule contradicts itself.** I wrote "`max(existing ids) + 1` … so deleted ids are never
  reused". Those clauses fight: deleting the highest id and creating a new task reproduces it.
  I tested it — deleted task 3, created one, got id 3 back. Round 1's `global next_id` is what
  actually delivers that guarantee, and I had already identified it as the better approach.
- **I specified away my own 204.** "200 on successful read/update/delete" means DELETE now
  returns 200 with a body, instead of the 204 No Content my hand-built version returns.
- **"GET `/` or `/health`"** isn't a specification. The AI built `/health` only, so `/` 404s.

Also `done: boolean, required on create (default false if omitted)` — required and defaulted are
opposites — and `PATCH` means `PUT /tasks/{id}` now returns 405, so this version would fail the
assignment's own endpoint list even though PATCH is the better verb for a merge.

### What I learned

The AI's output was exactly as good as my specification. Everything I stated, it built;
everything I left out, it invented; and the things I stated *wrongly* it implemented wrongly,
without argument. Round 2 taught me the harder half: a vague prompt produces obvious gaps you
notice immediately, but a precise prompt produces confident code built on whatever contradiction
you didn't catch. I could only see any of it because I had built the thing myself first.
