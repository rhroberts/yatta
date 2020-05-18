#!/usr/bin/env python
import os
import subprocess
import curses
import click
from pyfiglet import Figlet
from datetime import datetime
from appdirs import user_data_dir
from tabulate import tabulate
import yatta.db as db

APP_NAME = 'yatta'
DATA_DIR = user_data_dir(APP_NAME)

CLICK_CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
)


def _time_div(count):
    min, sec = divmod(count, 60)
    hour, min = divmod(min, 60)
    return(hour, min, sec)


def _time_format(hour, min, sec):
    return(f"{hour:02}:{min:02}:{sec:02}")


def _time_print(count):
    hour, min, sec = _time_div(count)
    return(_time_format(hour, min, sec))


def _time_figlet_print(font, count):
    hour, min, sec = _time_div(count)
    return(font.renderText(_time_format(hour, min, sec)))


def _stopwatch(stdscr, taskname, font):
    QUIT_KEY = ord('q')
    curses.echo()
    curses.use_default_colors()
    # FIXME: timeout gets reset when resizing terminal
    stdscr.timeout(1000)
    # FIXME: this errors out if text overflows terminal
    print(f'Taskname: {taskname}')
    stdscr.addstr(font.renderText(taskname))
    count = 0
    start_time = datetime.now()
    while True:
        stdscr.insstr(_time_figlet_print(font, count))
        count += 1
        ch = stdscr.getch()
        stdscr.refresh()
        if ch == QUIT_KEY:
            end_time = datetime.now()
            break
    duration = end_time - start_time
    return(start_time, end_time, duration)


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
@click.version_option(version='0.0.1')
def main():
    pass


@main.command()
@click.argument('task')
@click.option('-t', '--tags', default='', help='Add relevant tags to task.')
@click.option('-d', '--description', default='', help='Additional task info.')
@click.option('-f', '--font', default='doom',
              help='Select figlet font (http://www.figlet.org/).')
def track(task, tags, description, font, **kwargs):
    # create task if it doesn't exist
    taskname = task
    query = db.get_tasks(taskname)
    if not query.first():
        task = db.Task(name=task, tags=tags, description=description)
    else:
        task = query.first()
    font = Figlet(font=font)
    start, end, duration = curses.wrapper(
        _stopwatch, task.name, font
    )
    record = db.Record(
        task_name=task.name, start=start, end=end, duration=duration
    )
    db.add_record(task, record)
    print(
        f"\nWorked on {task.name} for {record.duration.seconds/3600:.2f} hrs" +
        f" ({_time_print(record.duration.seconds)}) \u2714"
    )


@main.command()
@click.option('-d', '--day', 'period', help='Print today\'s timesheet.',
              flag_value='day', default=True)
@click.option('-w', '--week', 'period', help='Print this week\'s timesheet.',
              flag_value='week')
@click.option('-m', '--month', 'period', help='Print this month\'s timesheet.',
              flag_value='month')
def report(period):
    print(f'Your timesheet for the {period}:')


@main.command()
@click.option('-d', '--day', 'period', help='Plot today\'s timesheet.',
              flag_value='day', default=True)
@click.option('-w', '--week', 'period', help='Plot this week\'s timesheet.',
              flag_value='week')
@click.option('-m', '--month', 'period', help='Plot this month\'s timesheet.',
              flag_value='month')
def plot(period):
    print(f'Plot of your timesheet for the {period}.')


@main.command()
def config():
    pass


@main.command()
@click.argument('task_name', required=False)
def history(task_name=None):
    query = db.get_records(task_name)
    records = db.query_to_df(query)
    print(tabulate(records, headers=records.columns, tablefmt='fancy_grid'))


@main.command()
@click.argument('task_name', required=False)
def tasks(task_name=None):
    query = db.get_tasks(task_name)
    records = db.query_to_df(query)
    print(tabulate(records, headers=records.columns, tablefmt='fancy_grid'))


def delete():
    pass


# TODO: consider changing structure from "yatta edit task" to "yatta task edit"
# similar for records. Then have "yatta task __" give task details for ___?
# OR maybe it's better if every command is a verb though, conceptually?
# yatta list tasks/records
# yatta edit tasks/records (and allow for editing multiple? ooh..)
@main.group()
def edit():
    '''
    Edit attributes of tasks and records
    '''
    pass


@edit.command()
@click.argument('task_name')
@click.option('-t', '--tags', default='', help='Add relevant tags to task.')
@click.option('-d', '--description', default='', help='Additional task info.')
def task(task_name, tags=None, description=None):
    '''
    Edit task attributes
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
@click.argument('id')
def record():
    '''
    Edit record attributes
    '''
    pass


if __name__ == "__main__":
    # make sure app directory exists, create it if not
    if not os.path.isdir(DATA_DIR):
        subprocess.run(['mkdir', '-p', DATA_DIR])
    main()
    db.session.close()
