import sqlite3
from yatta.task import Task


class DB(object):
    '''
    Object representing sqlite database.
    '''
    def __init__(self, db_path):
        self.path = db_path
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        self.result = None
        self._close()

    def _open(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()

    def _close(self):
        self.connection.close()

    def _commit(self):
        self.connection.commit()

    def _fetch(self):
        return(self.cursor.fetchall())

    def execute(self, query, *args):
        self._open()
        self.cursor.execute(query, *args)
        self.result = self._fetch()
        self._commit()
        self._close()


class AppDB(DB):
    '''
    Subclass of DB specific to this application.
    '''
    def __init__(self, db_path):
        super().__init__(db_path)
        self.init_database()

    def init_database(self):
        create_tasks_table = '''
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
        self.execute(create_tasks_table)
        create_tasklist_table = '''
            CREATE TABLE if not exists task_list (
                id INTEGER PRIMARY KEY,
                task TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT ''
            )
        '''
        self.execute(create_tasklist_table)

    def record_task(self, task: Task):
        query = '''
            INSERT INTO tasks
            (task, tags, description, start, stop, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.execute(
            query,
            (
                task.name, task.tags, task.description,
                task.start, task.end, task.duration
            )
        )

    def check_existing(self, task: Task):
        # check if a task exists in DB
        query_task = ''''''
        self.execute(query_task)

    def add_to_tasklist(self):
        # add a new task to the tasklist table
        pass
