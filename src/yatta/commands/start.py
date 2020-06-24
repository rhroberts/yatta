import logging
import os
import time
from multiprocessing import Process

import click
import yatta.db as db
from appdirs import user_cache_dir
from pyfiglet import Figlet
from yatta.utils import daemon_start, dummy_stopwatch

APP_NAME = "yatta"
CACHE_DIR = user_cache_dir(APP_NAME)
PID_FILE = os.path.join(CACHE_DIR, "yatta.pid")

logger = logging.getLogger(__name__)


@click.command()
@click.argument("task")
@click.option("-t", "--tags", default="", help="Add relevant tags to task.")
@click.option("-d", "--description", default="", help="Additional task info.")
@click.option(
    "-f", "--font", default="doom", help="Select figlet font (http://www.figlet.org/)."
)
@click.option("-b", "--background", help="Run yatta in the background.", is_flag=True)
def start(task, tags, description, font, background, **kwargs):
    """
    Track time spent on a task using a stopwatch.
    """
    # first check if there is already a task being recorded
    if not os.path.exists(PID_FILE):
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
            if background:
                daemon_start(taskname)
            else:
                Process(target=daemon_start, args=(taskname,)).start()
                # stagger processes so pidfile gets created first
                time.sleep(0.001)
                Process(target=dummy_stopwatch, args=(taskname, font)).start()
    else:
        print("You are already tracking a task. Try `yatta status` for more details.")
