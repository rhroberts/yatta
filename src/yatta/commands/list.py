import click
from tabulate import tabulate
from .. import db
from .. import utils


@click.group()
def list():
    """
    List information about tasks and records.
    """
    pass


@list.command()
@click.argument("task_name", required=False)
def tasks(task_name=None):
    """
    List all tasks or show info for a particular task.
    """
    query = db.get_tasks(task_name)
    _tasks = db.query_to_df(query)
    _tasks['total'] = _tasks['total'].apply(utils.time_print)
    print(tabulate(_tasks, headers=_tasks.columns, tablefmt="fancy_grid"))


@list.command()
@click.argument("record_id", required=False)
@click.option("-t", "--task", help="Task name or ID to get records from.")
@click.option(
    "-m",
    "--max-entries",
    default=10,
    help="Number of recent records to return. (Default: 10)",
)
@click.option("-a", "--all", is_flag=True, help="List all records.")
def records(all, max_entries, record_id=None, task=None):
    """
    List recent records from all tasks or a particular task.
    """
    query = db.get_records(record_id=record_id, task_name_or_id=task)
    _records = db.query_to_df(query)
    if not all:
        _records = _records.tail(max_entries)
    _records['duration'] = _records['duration'].apply(utils.time_print)
    print(tabulate(_records, headers=_records.columns, tablefmt="fancy_grid"))
