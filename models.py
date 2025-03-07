from datetime import datetime

class Task:
    def __init__(self, id, create_time, start_time=None, exec_time=None):
        self.id = id
        self.create_time = create_time
        self.start_time = start_time
        self.exec_time = exec_time