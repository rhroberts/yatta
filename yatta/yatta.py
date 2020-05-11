#!/usr/bin/env python
import os
import subprocess
import curses
import click
from pyfiglet import Figlet
from datetime import datetime
from appdirs import user_data_dir
from tabulate import tabulate
from yatta.db import AppDB
from yatta.task import Task


APP_NAME = 'yatta'
DATA_DIR = user_data_dir(APP_NAME)
APP_DB = AppDB(os.path.join(DATA_DIR, 'yatta.db'))

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
    return(start_time, end_time, count)


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
    task = Task(task, APP_DB, tags=tags, description=description)
    font = Figlet(font=font)
    task.start, task.end, task.duration = curses.wrapper(
        _stopwatch, task.name, font
    )
    APP_DB.record_task(task)
    APP_DB.update_task_list(task)
    print(f"\nWorked on {task.name} for {task.duration/3600:.2f} hrs" +
          f" ({_time_print(task.duration)}) \u2714")


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
def ls(task_name=None):
    if task_name:
        print(Task(task_name, APP_DB))
    else:
        tl = APP_DB.get_task_list()
        print(tabulate(tl, headers=tl.columns, tablefmt='fancy_grid'))


if __name__ == "__main__":
    # make sure app directory exists, create it if not
    if not os.path.isdir(DATA_DIR):
        subprocess.run(['mkdir', '-p', DATA_DIR])
    main()
    APP_DB._close()
