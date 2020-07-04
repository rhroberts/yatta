import logging

import click

from yatta import db as db
from yatta.completion_helpers import get_matching_tasks

logger = logging.getLogger(__name__)


@click.group()
def delete():
    """
    Delete tasks or records.
    """


@delete.command()
@click.argument(
    "task_name_or_id", nargs=-1, type=click.STRING, autocompletion=get_matching_tasks
)
@click.confirmation_option(prompt="Are you sure you want to delete specified task(s)?")
def tasks(task_name_or_id):
    """
    Delete a task and all its associated records.
    """
    for name_id in task_name_or_id:
        query = db.get_tasks(name_id)
        _task = query.first()
        if not _task:
            print(f"Task '{name_id}' does not exist.")
            return
        try:
            # delete task from tasks table; cascade delete associated records
            db.delete_task(_task)
            print(f"Deleted task {name_id}!")
        except Exception as e:
            db.session.rollback()
            logger.error(e)


@delete.command()
@click.argument("record_id", nargs=-1)
@click.confirmation_option(prompt="Are you sure you want to delete specifed record(s)?")
def records(record_id):
    """
    Delete a single record by its ID.
    """
    for _id in record_id:
        query = db.get_records(record_id=_id)
        _record = query.first()
        if not _record:
            print(f"Record id '{_id}' does not exist.")
        try:
            db.delete_record(_record)
            print(f"Deleted record {_id}!")
        except Exception as e:
            db.session.rollback()
            logger.error(e)
