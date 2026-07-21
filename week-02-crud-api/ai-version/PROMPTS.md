# Stage 7 prompts

The code in this folder is AI-generated and kept separate from the hand-built `../main.py`.
`main.py` here is the round-2 output. Both prompts are recorded below.

## Round 1 (verbatim)

> write me a CRUD using the FastAPI to do it and comparing it to me working and tell me whats
> the diff. also you should use the 200, 300, or the 400 to show or specify how they work like
> 404 not fpund, 204 not content, 200 for created, and the rest as well

Result: built `/items` with `name`/`description`, no `done` field, no validation, 200 on create,
no seed data, unlabeled `/docs`.

## Round 2 (verbatim)

> Build a CRUD REST API in FastAPI for a to-do list.
>
> Resource: /tasks
>
> Fields:
>
> - id: integer, server-assigned
> - title: string, required, non-empty after stripping whitespace
> - description: string, optional, nullable
> - done: boolean, required on create (default false if omitted)
>
> Endpoints:
>
> - GET / or /health — returns {"status": "ok"}
> - GET /tasks — list all
> - GET /tasks/{id} — get one
> - POST /tasks — create
> - PATCH /tasks/{id} — partial update (merge: only overwrite fields present in the request
>   body; omitted fields stay unchanged)
> - DELETE /tasks/{id}
>
> Status codes:
>
> - 201 on successful create
> - 200 on successful read/update/delete
> - 404 on missing id, body: {"detail": "Task {id} not found"} — include the actual id
> - 400 if title is missing or empty/whitespace-only
> - 422 only for malformed JSON / wrong types (let FastAPI's default validation handle this)
>
> Seed data: start the app with 3 tasks already in the list (make up reasonable titles).
>
> ID assignment: max(existing ids) + 1 on create, so deleted ids are never reused. If the list
> is empty, start at 1.
>
> Docs: set FastAPI title, description, and version in the app constructor. Add a summary to
> every endpoint so /docs is readable, not just present.

Result: all round-1 gaps closed. Remaining problems trace to contradictions in the prompt
itself — see the "AI vs me" section of [../README.md](../README.md).

## Running it

```bash
cd ai-version
../.venv/bin/uvicorn main:app --port 8001
```

Runs on port 8001 so it never collides with the hand-built API on 8000.
