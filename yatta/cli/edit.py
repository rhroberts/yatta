import click
import tabulate
import yatta.db as db


@click.group()
# @click.option('-t', '--task', 'obj', flag_value='tasks', default=True)
# @click.option('-r', '--record', 'obj', flag_value='records')
def edit():
    '''
    Edit attributes of tasks and records.
    '''
    pass


# TODO: if tags, etc aren't specified, open a tmp buffer to edit, a la git
# not sure how to do that yet
@edit.command()
@click.argument('task_name')
@click.option('-t', '--tags', default='', help='Add relevant tags to task.')
@click.option(
    '-d', '--description', default='', help='Add additional task info.'
)
def task(task_name, tags=None, description=None):
    '''
    Edit task attributes.
    '''
    query = db.get_tasks(task_name)
    _task = query.first()
    if not _task:
        print(f'\nTask \'{task_name}\' does not exist!')
        return
    if tags:
        _task.tags = tags
        # TODO: is there a better way to handle this?
        db.session.commit()
        print(f'\nUpdated tags for \'{task_name}\' to \'{_task.tags}\'')
    elif description:
        _task.description = description
        print(f'\nUpdated description for \'{task_name}\' to ' +
              f'\'{_task.description}\'')
        db.session.commit()
    else:
        print(f'\nNo changes to \'{task_name}\' where specified')


@edit.command()
@click.argument('record_id')
def record(record_id):
    print(record_id)
