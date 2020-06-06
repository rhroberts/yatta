import click
import curses
from pyfiglet import Figlet
import yatta.db as db
from yatta.utils import stopwatch, time_print


@click.command()
@click.argument("task")
@click.option("-t", "--tags", default="", help="Add relevant tags to task.")
@click.option("-d", "--description", default="", help="Additional task info.")
@click.option(
    "-f", "--font", default="doom", help="Select figlet font (http://www.figlet.org/)."
)
def track(task, tags, description, font, **kwargs):
    """
    Track time spent on a task using a stopwatch.
    """
    # create task if it doesn't exist
    taskname = task
    query = db.get_tasks(taskname)
    if not query.first():
        task = db.Task(name=task, tags=tags, description=description)
    else:
        task = query.first()
    if db.validate_task(task):
        font = Figlet(font=font)
        start, end, duration = curses.wrapper(stopwatch, task.name, font)
        record = db.Record(task_name=task.name, start=start, end=end, duration=duration)
        db.add_record(task, record)
        db.update_task_total(task)
        print(
            f"\nWorked on {task.name} for {record.duration/3600:.2f}"
            + f"hrs ({time_print(record.duration)}) \u2714"
        )
