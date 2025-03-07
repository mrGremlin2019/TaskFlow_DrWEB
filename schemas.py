from pydantic import BaseModel
from datetime import datetime

class TaskCreate(BaseModel):
    create_time: datetime

class TaskStatus(BaseModel):
    status: str
    create_time: datetime
    start_time: datetime | None
    time_to_execute: int | None