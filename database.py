from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import threading
import time
import random
from datetime import datetime
from models import Task, Base

class DatabaseClient:
    def __init__(self):
        # Указываем путь к базе данных
        db_dpath = Path(".")  # Текущая директория
        if not db_dpath.exists():
            db_dpath.mkdir(parents=True)

        # Создаем переменную с путем до файла БД
        self.db_path = db_dpath / "tasks.db"

        # Создаем объект движка SQLAlchemy
        self.engine = create_engine(f"sqlite:///{self.db_path}", connect_args={"check_same_thread": False})

        # Создаем объект сессии
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Создаем таблицы, если они еще не существуют
        Base.metadata.create_all(self.engine)

        # Очередь задач и синхронизация
        self.task_queue = []
        self.task_lock = threading.Lock()
        self.task_semaphore = threading.Semaphore(2)  # Ограничение одновременно выполняемых задач

    def get_db(self):
        """Генератор сессий для работы с базой данных."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def task_worker(self):
        """Функция для выполнения задач в фоновом режиме."""
        while True:
            self.task_semaphore.acquire()
            with self.task_lock:
                if self.task_queue:
                    task_id = self.task_queue.pop(0)
                    with self.SessionLocal() as db:  # Контекстный менеджер для сессии
                        task = db.query(Task).filter(Task.id == task_id).first()
                        if task:
                            task.start_time = datetime.now()
                            db.commit()
                            time.sleep(random.randint(0, 10))
                            task.exec_time = random.randint(0, 10)
                            db.commit()
            self.task_semaphore.release()

    def start_task_worker(self):
        """Запуск фонового потока для обработки задач."""
        threading.Thread(target=self.task_worker, daemon=True).start()

    def add_task_to_queue(self, task_id: int):
        """Добавление задачи в очередь."""
        with self.task_lock:
            self.task_queue.append(task_id)