from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import func
import logging
from appdirs import user_data_dir
from tabulate import tabulate
import pandas as pd
import os

APP_NAME = "yatta"
DATA_DIR = user_data_dir(APP_NAME)
DB_PATH = os.path.join(DATA_DIR, "yatta.db")

logger = logging.getLogger(__name__)

# make sure app directory exists, create it if not
if not os.path.isdir(DATA_DIR):
    try:
        os.mkdir(DATA_DIR)
        # FIXME: this isn't showing up in logs
        logger.debug(f"Created data directory: {DATA_DIR}")
    except OSError:
        logger.error(f"Failed to create directory: {DATA_DIR}")

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Sessionmkr = sessionmaker(bind=engine)
session = Sessionmkr()
Base = declarative_base()


# define tables / db objects
class Task(Base):
    __tablename__ = "tasks"
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    tags = Column(String)
    description = Column(String)
    records = relationship("Record", back_populates="task")
    total = Column(Integer)

    def __repr__(self):
        return (
            f"<Task(name={self.name}, tags={self.tags}, "
            + f"description={self.description}, total={self.total})>"
        )

    def __str__(self):
        s = [
            ["ID", "Task", "Tags", "Description", "Total"],
            [self.id, self.name, self.tags, self.description, self.total],
        ]
        return tabulate(s, tablefmt="fancy_grid")


class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True)
    task_name = Column(String, nullable=False, unique=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)

    task = relationship("Task", back_populates="records")

    def __repr__(self):
        return (
            f"<Record(task_name={self.task_name}, start={self.start} "
            + f"end={self.start}, duration={self.duration.seconds})>"
        )

    def __str__(self):
        s = [
            ["Record ID", "Task ID", "Task", "Start", "End", "Duration"],
            [
                self.id,
                self.task_id,
                self.task_name,
                self.start,
                self.end,
                self.duration,
            ],
        ]
        return tabulate(s, tablefmt="fancy_grid")


# add the above mappings to database, if they don't already exist
Base.metadata.create_all(engine)


def add_record(task, record):
    try:
        session.add(task)
        session.commit()
        print(f"Created new task: [{task.name}]")
    except IntegrityError:
        print(f"Task [{task.name}] exists; It's record will be updated.")
        session.rollback()
    task.records.append(record)
    session.add(record)
    session.commit()


def get_records(record_id=None, task_name_or_id=None):
    if record_id:
        try:
            record_id = int(record_id)
            query = session.query(Record).filter(Record.id == record_id)
        except ValueError:
            logger.warning("Record ID must be an integer!")
            # query all records instead
            query = session.query(Record)
    elif task_name_or_id:
        # check if it's a name or an id
        try:
            task_name_or_id = int(task_name_or_id)
            query = session.query(Record).filter(Record.task_id == task_name_or_id)
        except ValueError:
            query = session.query(Record).filter(Record.task_name == task_name_or_id)
    else:
        query = session.query(Record)  # return all records
    return query


def get_tasks(task_name_or_id=None):
    if task_name_or_id:
        # check if it's a name or an id
        try:
            assert int(task_name_or_id)
            query = session.query(Task).filter(Task.id == task_name_or_id)
        except ValueError:
            query = session.query(Task).filter(Task.name == task_name_or_id)
    else:
        query = session.query(Task)  # return all tasks
    return query


def query_to_df(query):
    df = pd.read_sql(query.statement, query.session.bind, index_col="id")
    return df


def validate_task(task):
    """
    Make sure task object meets certain requirements.
    """
    # Ensure that task name cannot be converted to int (conflicts w/ task id)
    try:
        assert int(task.name)
        logger.warning("Cannot use integers as task names!")
        return False
    except ValueError:
        return True


def delete_task(task):
    session.delete(task)
    session.commit()


def delete_record(record):
    session.delete(record)
    session.commit()


def update_task_total(task):
    total = (
        session.query(func.sum(Record.duration))
        .filter(Task.name == task.name)
        .first()[0]
    )
    task.total = total
    session.commit()
