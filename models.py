from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Базовый класс для моделей
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    create_time = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=True)
    exec_time = Column(Integer, nullable=True)