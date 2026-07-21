from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    description="A simple in-memory CRUD API for managing tasks. Week 2 assignment.",
    version="1.0.0",
)

tasks = [ 
         {"id": 1, "title": "Learn FastAPI", "description": "This is task 1", "done": False},
         {"id": 2, "title": "Build CRUD API", "description": "This is task 2", "done": True},
         {"id": 3, "title": "Push Code to GitHub", "description": "This is task 3", "done": False}
        ]

class TaskCreated(BaseModel):
    title: str | None = None
    description: str = ""


# Read the root endpoint
@app.get("/", summary="Get API information")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# Create a new task
@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(payload: TaskCreated):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Field 'title' is required and cannot be empty")
    title = payload.title.strip()

    
    new_id = max((task["id"] for task in tasks), default=0) + 1
    task = {"id": new_id, "title": title, "description": payload.description, "done": False}
    tasks.append(task)
    return task

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool | None = None
    

# Update an existing task
@app.put("/tasks/{task_id}", summary="Update a task by ID")
def update_task(task_id: int, payload: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if payload.title is not None:
                if not payload.title.strip():
                    raise HTTPException(status_code=400, detail="Field 'title' cannot be empty")
                task["title"] = payload.title.strip()
            if payload.description is not None:
                task["description"] = payload.description
            if payload.done is not None:
                task["done"] = payload.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# Delete a task
@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task by ID")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            del tasks[index]
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")