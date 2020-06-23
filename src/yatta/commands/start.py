import curses
import logging

import click
import yatta.db as db
from pyfiglet import Figlet
from yatta.utils import daemon_start, stopwatch, time_print

logger = logging.getLogger(__name__)


@click.command()
@click.argument("task")
@click.option("-t", "--tags", default="", help="Add relevant tags to task.")
@click.option("-d", "--description", default="", help="Additional task info.")
@click.option(
    "-f", "--font", default="doom", help="Select figlet font (http://www.figlet.org/)."
)
@click.option("--daemonize", help="Run yatta in the background.", is_flag=True)
def start(task, tags, description, font, daemonize, **kwargs):
    """
    Track time spent on a task using a stopwatch.
    """
    # create task if it doesn't exist
    taskname = task
    query = db.get_tasks(taskname)
    if not query.first():
        task = db.Task(name=taskname, tags=tags, description=description)
        task.total = 0
    else:
        task = query.first()
    if db.validate_task(task):
        db.session.add(task)
        db.session.commit()
        font = Figlet(font=font)
        if daemonize:
            daemon_start(taskname)
        else:
            start, end, duration = curses.wrapper(stopwatch, task.name, font)
            if not duration:
                logger.info("Could not acquire lock. A task is already being tracked.")
                print(
                    "\nYou are already tracking a task. "
                    + "Please complete the running task to begin a new one."
                )
            else:
                record = db.Record(
                    task_name=task.name, start=start, end=end, duration=duration
                )
                db.add_record(task, record)
                db.update_task_total(task)
                print(
                    f"\nWorked on {task.name} for {record.duration/3600:.2f}"
                    + f"hrs ({time_print(record.duration)}) \u2714"
                )
