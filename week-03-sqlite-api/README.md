# Week 3 — Task API (SQLite)

The Week 2 CRUD API with storage moved from an in-memory list to a real **SQLite** database
(`tasks.db`). Same endpoints, same responses — but the data now survives a restart.

## Example SQL (Stage 4, run by hand in DB Browser)

```sql
SELECT * FROM tasks WHERE done = 1;   -- only completed tasks
```

Returned the one seeded task whose `done` is `1` ("Build CRUD API"). Running it in DB Browser
and then calling `GET /tasks` shows the same data — the API and DB Browser read the one same
file, `tasks.db`. There is no syncing; there is one source of truth.
