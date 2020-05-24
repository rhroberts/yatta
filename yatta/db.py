from sqlalchemy import (create_engine, Column, Integer, String, ForeignKey,
                        DateTime, Interval)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, relationship
from appdirs import user_data_dir
from tabulate import tabulate
import pandas as pd
import os

APP_NAME = 'yatta'
DATA_DIR = user_data_dir(APP_NAME)
DB_PATH = os.path.join(DATA_DIR, 'yatta.db')

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Sessionmkr = sessionmaker(bind=engine)
session = Sessionmkr()
Base = declarative_base()


# define tables / db objects
class Task(Base):
    __tablename__ = 'tasks'
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    tags = Column(String)
    description = Column(String)
    records = relationship('Record', back_populates='task')
    total = Column(Integer)

    def __repr__(self):
        return(f'<Task(name={self.name}, tags={self.tags}, ' +
               f'description={self.description}, total={self.total})>')

    def __str__(self):
        s = [['ID', 'Task', 'Tags', 'Description', 'Total'],
             [self.id, self.name, self.tags, self.description, self.total]]
        return(tabulate(s, tablefmt='fancy_grid'))


class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    task_name = Column(String, nullable=False, unique=False)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    duration = Column(Interval, nullable=False)

    task = relationship('Task', back_populates='records')

    def __repr__(self):
        return(f'<Record(task_name={self.task_name}, start={self.start} ' +
               f'end={self.start}, duration={self.duration.seconds})>')

    def __str__(self):
        s = [
                ['Record ID', 'Task ID', 'Task', 'Start', 'End', 'Duration'],
                [
                    self.id, self.task_id, self.task_name,
                    self.start, self.end, self.duration.seconds
                ]
            ]
        return(tabulate(s, tablefmt='fancy_grid'))


# add the above mappings to database, if they don't already exist
Base.metadata.create_all(engine)


def add_record(task, record):
    try:
        session.add(task)
        session.commit()
        print(f'Created new task: [{task.name}]')
    except IntegrityError:
        print(f'Task [{task.name}] exists; It\'s record will be updated.')
        session.rollback()

    task.records.append(record)
    session.add(record)
    session.commit()


def get_records(taskname=None):
    if taskname:
        query = session.query(Record).filter(Record.task_name == taskname)
    else:
        query = session.query(Record)
    return(query)


def get_tasks(taskname=None):
    if taskname:
        query = session.query(Task).filter(Task.name == taskname)
    else:
        query = session.query(Task)
    return(query)


def query_to_df(query):
    df = pd.read_sql(
        query.statement, query.session.bind, index_col='id'
    )
    return(df)
