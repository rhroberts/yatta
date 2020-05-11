from tabulate import tabulate
from yatta.db import AppDB


class Task():
    '''
    Class to model tasks in yatta.
    '''
    # TODO: type checking
    # TODO: add a total time attribute
    def __init__(self, name: str, db: AppDB, tags='', description=''):
        self.name = name.lower()
        self.db = db
        # if task exists, default to existing tags and description
        if db.check_existing(self):
            _, _, self.tags, self.description, self.total = db.get_task_info(self)
        else:
            self.tags = tags
            self.description = description
        self.start = None
        self.end = None
        self.duration = 0

    def __str__(self):
        s = [['Task', 'Tags', 'Description', 'Total'],
             [self.name, self.tags, self.description, self.total]]
        return(tabulate(s, tablefmt='fancy_grid'))
