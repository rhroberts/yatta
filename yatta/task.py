class Task():
    '''
    Class to model tasks in yatta. Individual task data stored as table in
    sqlite database. So, when a task is initialized, it should create a table
    for itself.
    '''
    # TODO: "enforce" type
    def __init__(self, name: str, tags='', description=''):
        self.name = name.lower()
        self.tags = tags
        self.description = description
        self.start = None
        self.end = None
        self.duration = 0
