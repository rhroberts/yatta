import click
from tabulate import tabulate
from .. import db


@click.group()
def list():
    '''
    List information about tasks and records.
    '''
    pass


@list.command()
@click.argument('task_name', required=False)
def task(task_name=None):
    '''
    List all tasks or show info for a particular task.
    '''
    query = db.get_tasks(task_name)
    records = db.query_to_df(query)
    print(
        tabulate(records, headers=records.columns, tablefmt='fancy_grid')
    )


@list.command()
@click.argument('record_id', required=False)
@click.option('-t', '--task', help='Task name or ID to get records from.')
@click.option(
    '-m', '--max-entries', default=10,
    help='Number of recent records to return. (Default: 10)'
)
@click.option('-a', '--all', is_flag=True, help='List all records.')
def record(all, max_entries, record_id=None, task=None):
    '''
    List recent records from all tasks or a particular task.
    '''
    query = db.get_records(record_id=record_id, task_name_or_id=task)
    records = db.query_to_df(query)
    if not all:
        records = records.tail(max_entries)
    print(
        tabulate(records, headers=records.columns, tablefmt='fancy_grid')
    )
