from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

tasks = [ 
         {"id": 1, "title": "Learn FastAPI", "description": "This is task 1", "done": False},
         {"id": 2, "title": "Build CRUD API", "description": "This is task 2", "done": True},
         {"id": 3, "title": "Push Code to GitHub", "description": "This is task 3", "done": False}
        ]

class TaskCreated(BaseModel):
    title: str | None = None
    description: str = ""



@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreated):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Field 'title' is required and cannot be empty")
    title = payload.title.strip()

    
    new_id = max((task["id"] for task in tasks), default=0) + 1
    task = {"id": new_id, "title": title, "description": payload.description, "done": False}
    tasks.append(task)
    return task

