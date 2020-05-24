import click
from tabulate import tabulate
import yatta.db as db


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
def record(record_id=None):
    '''
    List all records or list records for a particular task.
    '''
    query = db.get_records(record_id)
    records = db.query_to_df(query)
    print(
        tabulate(records, headers=records.columns, tablefmt='fancy_grid')
    )
