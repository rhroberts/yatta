import logging
import os

import pandas as pd
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    event,
    func,
)
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from tabulate import tabulate

from yatta import utils as utils
from yatta.config import Config
from yatta.utils import get_app_dirs


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


DATA_DIR, CONFIG_DIR, CACHE_DIR = get_app_dirs()
DB_PATH = os.path.join(DATA_DIR, "yatta.db")

logger = logging.getLogger(__name__)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Sessionmkr = sessionmaker(bind=engine)
session = Sessionmkr()
Base = declarative_base()


# define tables / db objects
class Task(Base):
    __tablename__ = "tasks"
    # __table_args__ = {'extend_existing': True}
    name = Column(String, unique=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
    tags = Column(String)
    description = Column(String)
    total = Column(Integer)

    records = relationship(
        "Record",
        primaryjoin="and_(Task.id == Record.task_id, Task.name == Record.task_name)",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Task(name={self.name}, tags={self.tags}, "
            + f"description={self.description}, total={utils.time_print(self.total)})>"
        )

    def __str__(self):
        headers = ["ID", "Task", "Tags", "Description", "Total"]
        data = [
            [
                self.id,
                self.name,
                self.tags,
                self.description,
                utils.time_print(self.total),
            ],
        ]
        return "\n" + tabulate(
            data,
            headers=headers,
            tablefmt=Config().get_user_value("formatting", "table_style"),
        )


class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(
        String, ForeignKey("tasks.id", onupdate="cascade", ondelete="cascade")
    )
    task_name = Column(
        String, ForeignKey("tasks.name", onupdate="cascade", ondelete="cascade")
    )
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)

    def __repr__(self):
        return (
            f"<Record(task_name={self.task_name}, start={self.start} "
            + f"end={self.start}, duration={utils.time_print(self.duration)})>"
        )

    def __str__(self):
        h = ["record_id", "task_id", "task", "start", "end", "duration"]
        s = [
            [
                self.id,
                self.task_id,
                self.task_name,
                self.start,
                self.end,
                utils.time_print(self.duration),
            ],
        ]
        return "\n" + tabulate(
            s, headers=h, tablefmt=Config().get_user_value("formatting", "table_style"),
        )


# add the above mappings to database, if they don't already exist
Base.metadata.create_all(engine)


def add_record(task, record):
    session.add(task)
    session.commit()
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
        .filter(Record.task_id == task.id)
        .first()[0]
    )
    task.total = total
    session.commit()
