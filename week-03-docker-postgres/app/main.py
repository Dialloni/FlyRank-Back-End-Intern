"""Routes and validation — UNCHANGED from A2 in behaviour. The only difference
from A2 is the single line below that picks the repository. Same endpoints,
same status codes, same JSON shapes."""
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .repository import (
    InMemoryTaskRepository,
    PostgresTaskRepository,
    TaskNotFound,
)

load_dotenv()

# --- The swap: one line chooses storage. Routes below never mention it. -------
if os.getenv("REPO_BACKEND", "postgres") == "memory":
    repo = InMemoryTaskRepository()
else:
    repo = PostgresTaskRepository(os.environ["DATABASE_URL"])


app = FastAPI(
    title="Task API",
    description="CRUD API backed by Postgres in Docker. Week 3 assignment A3.",
    version="3.0.0",
)


class TaskCreated(BaseModel):
    title: str | None = None
    description: str = ""


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool | None = None


@app.get("/", summary="Get API information")
def read_root():
    return {"name": "Task API", "version": "3.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return repo.list()


@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    try:
        return repo.get(task_id)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(payload: TaskCreated):
    if not payload.title or not payload.title.strip():
        raise HTTPException(
            status_code=400, detail="Field 'title' is required and cannot be empty"
        )
    return repo.create(payload.title.strip(), payload.description)


@app.put("/tasks/{task_id}", summary="Update a task by ID")
def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(status_code=400, detail="Field 'title' cannot be empty")
    title = payload.title.strip() if payload.title is not None else None
    try:
        return repo.update(task_id, title, payload.description, payload.done)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task by ID")
def delete_task(task_id: int):
    try:
        repo.delete(task_id)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
