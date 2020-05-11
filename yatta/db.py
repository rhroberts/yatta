import sqlite3
import pandas as pd


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
        self._init_database()

    def _init_database(self):
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
                description TEXT NOT NULL DEFAULT '',
                total INTEGER NOT NULL
            )
        '''
        self.execute(create_tasklist_table)

    def record_task(self, task):
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

    def add_to_task_list(self, task):
        if not self.check_existing(task):
            query = '''
                INSERT INTO task_list
                (task, tags, description, total)
                VALUES (?, ?, ?, ?)
            '''
            self.execute(
                query, (task.name, task.tags, task.description, 0)
            )
        else:
            query = '''UPDATE task_list SET total = ? WHERE task = ?'''
            self.execute(query, (self.get_total_time(task), task.name))

    def check_existing(self, task):
        # check if a task exists in task_list table
        task_list = self.get_task_list()
        if task_list.empty:
            return(False)
        return(task.name in task_list['task'].to_numpy())

    def get_task_list(self):
        # get the contents of a task_list table and convert to DataFrame
        query = '''SELECT * FROM task_list'''
        self.execute(query)
        task_list = to_dataframe(self.result)
        query = '''PRAGMA table_info(task_list)'''
        self.execute(query)
        if not task_list.empty:
            task_list.columns = [res[1] for res in self.result[1:]]
        return(task_list)

    def get_task_info(self, task):
        query = '''SELECT * FROM task_list WHERE task = ?'''
        self.execute(query, (task.name,))
        id, name, tags, description, total = self.result[0]
        return(id, name, tags, description, total)

    # FIXME: only updates after task is tracked a second time
    # FIXME: this all got way too convoluted...
    def get_total_time(self, task):
        query = '''SELECT * FROM tasks WHERE task = ?'''
        self.execute(query, (task.name,))
        task_history = to_dataframe(self.result)
        if task_history.empty:
            return(0)
        # TODO: store table cols somewhere?
        query = '''PRAGMA table_info(tasks)'''
        self.execute(query)
        task_history.columns = [res[1] for res in self.result[1:]]
        return(task_history['duration'].sum())


def to_dataframe(result):
    if not result:
        return(pd.DataFrame())
    # convert query results to dataframe
    df = pd.DataFrame.from_records(result)
    df = df.set_index(0, drop=True)
    return(df)
