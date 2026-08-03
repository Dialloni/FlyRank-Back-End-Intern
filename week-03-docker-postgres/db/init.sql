-- Runs once, automatically, the first time the Postgres volume is created
-- (Docker mounts this into /docker-entrypoint-initdb.d/). Creates the table
-- and seeds three example tasks. The app also ensures this idempotently at
-- startup, so a fresh DB is always ready either way.
CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    done        BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tasks (title, description, done) VALUES
    ('Learn FastAPI', 'This is task 1', FALSE),
    ('Build CRUD API', 'This is task 2', TRUE),
    ('Push Code to GitHub', 'This is task 3', FALSE);
