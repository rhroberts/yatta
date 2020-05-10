import sqlite3
from .task import Task


class DB(object):
    '''
    Object representing sqlite database.
    '''
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.init_database()

    def init_database(self):
        c = self.connection.cursor()
        query = '''
            CREATE TABLE if not exists tasks (
                id INTEGER PRIMARY KEY,
                task TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                start DATETIME NOT NULL,
                stop DATETIME NOT NULL,
                duration REAL NOT NULL
            )
        '''
        c.execute(query)
        self.connection.commit()

    def record_task(self, task: Task):
        c = self.connection.cursor()
        query = '''
            INSERT INTO tasks
            (task, tags, description, start, stop, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        c.execute(
            query,
            (
                task.name, task.tags, task.description,
                task.start, task.end, task.duration
            )
        )
        self.connection.commit()

    def close(self):
        self.connection.close()
