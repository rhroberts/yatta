import logging
import os
import time
from multiprocessing import Process

import click
from pyfiglet import Figlet

from yatta import db as db
from yatta.completion_helpers import get_matching_tasks
from yatta.config import Config
from yatta.daemon import daemon_start, dummy_stopwatch
from yatta.utils import get_app_dirs

DATA_DIR, CONFIG_DIR, CACHE_DIR = get_app_dirs()
PID_FILE = os.path.join(CACHE_DIR, "yatta.pid")

logger = logging.getLogger(__name__)


@click.command()
@click.argument("task", type=click.STRING, autocompletion=get_matching_tasks)
@click.option("-t", "--tags", default="", help="Add relevant tags to task.")
@click.option("-d", "--description", default="", help="Additional task info.")
@click.option(
    "-f", "--font", default="doom", help="Select figlet font (http://www.figlet.org/)."
)
@click.option("-b", "--background", help="Run yatta in the background.", is_flag=True)
def start(task, tags, description, font, background, **kwargs):
    """
    Start tracking a task.
    """
    # first check if there is already a task being recorded
    if not os.path.exists(PID_FILE):
        # create task if it doesn't exist
        task_name_or_id = task
        query = db.get_tasks(task_name_or_id)
        if not query.first():
            task = db.Task(name=task_name_or_id, tags=tags, description=description)
            task.total = 0
            db.validate_task(task)
            db.session.add(task)
            db.session.commit()
        else:
            task = query.first()
        font = Figlet(font=Config().get_user_value("formatting", "figlet_font"))
        if (
            background
            or Config().get_user_value("general", "run_in_background") == "true"
        ):
            daemon_start(task.name)
        else:
            Process(target=daemon_start, args=(task.name,)).start()
            # stagger processes so pidfile gets created first
            time.sleep(0.01)
            Process(target=dummy_stopwatch, args=(task.name, font)).start()
    else:
        print("You are already tracking a task. Try `yatta status` for more details.")
