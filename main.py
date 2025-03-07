from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.orm import Session
from database import DatabaseClient
from models import Task
from schemas import TaskCreate, TaskStatus

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация клиента базы данных
db_client = DatabaseClient()

# Запуск фонового потока для обработки задач
db_client.start_task_worker()

# Ручка для создания задачи
@app.post("/task/", response_model=TaskStatus)
async def create_task(db: Session = Depends(db_client.get_db)):
    create_time = datetime.now()
    task = Task(create_time=create_time)
    db.add(task)
    db.commit()
    db.refresh(task)
    db_client.add_task_to_queue(task.id)  # Добавляем задачу в очередь
    return {
        "status": "In Queue",
        "create_time": task.create_time,
        "start_time": None,
        "time_to_execute": None,
    }

# Ручка для получения статуса задачи
@app.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: int, db: Session = Depends(db_client.get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    status = "In Queue"
    if task.start_time:
        status = "Run"
    if task.exec_time is not None:
        status = "Completed"
    return {
        "status": status,
        "create_time": task.create_time,
        "start_time": task.start_time,
        "time_to_execute": task.exec_time,
    }

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)