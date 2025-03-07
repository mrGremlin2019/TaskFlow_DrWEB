from fastapi import FastAPI, HTTPException
from datetime import datetime
import time
import random
import sqlite3
import threading

app = FastAPI()

DATABASE = "tasks.db"

# Подключение к БД
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Очередь задач и синхронизация
task_queue = []
task_lock = threading.Lock()
task_semaphore = threading.Semaphore(2)

# Функция для выполнения задач
def task_worker():
    while True:
        task_semaphore.acquire()
        with task_lock:
            if task_queue:
                task_id = task_queue.pop(0)
                conn = get_db_connection()
                cursor = conn.cursor()
                start_time = datetime.now().isoformat()
                cursor.execute("UPDATE tasks SET start_time = ? WHERE id = ?",
                               (start_time, task_id))
                conn.commit()
                conn.close()
                time.sleep(random.randint(0, 10))
                exec_time = random.randint(0, 10)
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET exec_time = ? WHERE id = ?",
                               (exec_time, task_id))
                conn.commit()
                conn.close()
        task_semaphore.release()

# Запуск фонового потока для обработки задач
threading.Thread(target=task_worker, daemon=True).start()

# Ручка для создания задачи
@app.post("/task/")
async def create_task():
    conn = get_db_connection()
    cursor = conn.cursor()
    create_time = datetime.now().isoformat()
    cursor.execute("INSERT INTO tasks (create_time) VALUES (?)", (create_time,))
    task_id = cursor.lastrowid
    task_queue.append(task_id)  # Добавляем задачу в очередь
    conn.commit()
    conn.close()
    return {"task_id": task_id}

# Ручка для получения статуса задачи
@app.get("/task/{task_id}")
async def get_task_status(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "In Queue", "create_time": task['create_time'],
            "start_time": task['start_time'], "time_to_execute": task['exec_time']}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)