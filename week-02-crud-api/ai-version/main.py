"""
CRUD REST API for a to-do list — FastAPI.

Generated from the Stage 7 round-2 prompt, implemented literally as specified.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    description="A CRUD REST API for a to-do list, stored in memory.",
    version="1.0.0",
)

tasks: list[dict] = [
    {"id": 1, "title": "Read the FastAPI docs", "description": None, "done": True},
    {"id": 2, "title": "Write the task API", "description": None, "done": False},
    {"id": 3, "title": "Ship it", "description": None, "done": False},
]


class TaskCreate(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool = False


class TaskPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool | None = None


def find_task(task_id: int) -> dict:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task by id")
def get_task(task_id: int):
    return find_task(task_id)


@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(payload: TaskCreate):
    if payload.title is None or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Field 'title' is required and cannot be empty")

    new_id = max((task["id"] for task in tasks), default=0) + 1
    task = {
        "id": new_id,
        "title": payload.title.strip(),
        "description": payload.description,
        "done": payload.done,
    }
    tasks.append(task)
    return task


@app.patch("/tasks/{task_id}", summary="Partially update a task")
def patch_task(task_id: int, payload: TaskPatch):
    task = find_task(task_id)

    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(status_code=400, detail="Field 'title' cannot be empty")
        task["title"] = payload.title.strip()
    if payload.description is not None:
        task["description"] = payload.description
    if payload.done is not None:
        task["done"] = payload.done

    return task


@app.delete("/tasks/{task_id}", summary="Delete a task")
def delete_task(task_id: int):
    task = find_task(task_id)
    tasks.remove(task)
    return {"detail": f"Task {task_id} deleted"}
