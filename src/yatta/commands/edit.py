import click
import logging
from datetime import datetime
import parsedatetime as pdt
from sqlalchemy.exc import IntegrityError
from .. import db

logger = logging.getLogger(__name__)


@click.group()
def edit():
    """
    Edit attributes of tasks and records.
    """
    pass


@edit.command()
@click.argument("task_name_or_id")
@click.option("-n", "--name", help="Change the name of the task.")
@click.option("-t", "--tags", default="", help="Add relevant tags to task.")
@click.option("-d", "--description", default="", help="Add additional task info.")
def tasks(task_name_or_id, name=None, tags=None, description=None):
    """
    Edit task attributes.
    """
    integrity_error_msg = (
        "Edits were not saved! It's possible you tried "
        + "to change the task name to that of an existing "
        + "task."
    )

    query = db.get_tasks(task_name_or_id)
    _task = query.first()
    if not _task:
        print(f"Task '{task_name_or_id}' does not exist.")
        return
    if name or tags or description:
        if name:
            try:
                _task.name = name
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                logger.warning(integrity_error_msg)
                return
        if tags:
            _task.tags = tags
            # TODO: is there a better way to handle this?
            db.session.commit()
        if description:
            _task.description = description
            db.session.commit()
        print(_task)
    else:
        MARKER = (
            "\n\n-----\nFORMAT: NAME,TAGS,DESCRIPTION ("
            + "Separate tags with '-')\n"
            + "EXAMPLE: fix bicycle,personal-hobbies-fitness,"
            + "fix the flat from my last ride\n-----"
        )
        task_str = f"{_task.name},{_task.tags},{_task.description}{MARKER}"
        updates = click.edit(task_str)
        if updates:
            try:
                _task.name, _task.tags, _task.description = (
                    updates.split(MARKER)[0].strip().split(",")
                )
                db.session.commit()
                print(_task)
            except IntegrityError:
                logger.warning(integrity_error_msg)
        else:
            print("No updates were specified.")


# TODO: Catch common errors from parsedatetime
# TODO: Add options for start and end
@edit.command()
@click.argument("record_id")
def records(record_id):
    query = db.get_records(record_id=record_id)
    _record = query.first()
    if not _record:
        print(f"Record with ID '{record_id}' does not exist.")

    MARKER = (
        "\n\n-----\nFORMAT: START,END\n"
        + "EXAMPLES:\n\t2020-03-21 13:01:00,2020-03-21 14:01:00\n"
        + "\tToday at noon,now\n"
        + "START and END must be interpretable by: "
        + "https://github.com/bear/parsedatetime\n-----"
    )
    record_str = f"{_record.start},{_record.end}{MARKER}"
    updates = click.edit(record_str)
    # TODO: error handling for datetime formats, ensure END is after START
    if updates:
        start, end = updates.split(MARKER)[0].strip().split(",")
        cal = pdt.Calendar()
        start = datetime(*cal.parse(start)[0][:6])
        end = datetime(*cal.parse(end)[0][:6])
        if end < start:
            logger.error("End time is before start time. No changes have been made.")
            return
        _record.start = start
        _record.end = end
        db.session.commit()
        print(_record)
    else:
        print("No updates were specified.")
