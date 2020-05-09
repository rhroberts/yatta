import os
import sqlite3
from appdirs import user_data_dir

db_file = os.path.join(user_data_dir('yatta'), 'yatta.db')


def Task(object):
    """
    Class to model tasks in yatta. Individual task data stored as table in
    sqlite database. So, when a task is initialized, it should create a table
    for itself.
    """
    def __init__(self, name: str, tags=[], description=''):
        self.name = name.lower()
        self.tags = tags
        self.description = description
