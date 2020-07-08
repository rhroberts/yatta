import logging
import os
import time
from datetime import datetime

from appdirs import user_cache_dir, user_config_dir, user_data_dir

APP_NAME = "yatta"
CACHE_DIR = user_cache_dir(APP_NAME)
TMP_FILE = os.path.join(CACHE_DIR, "active_task")
PID_FILE = os.path.join(CACHE_DIR, "yatta.pid")

logger = logging.getLogger(__name__)


def get_app_dirs(app_name, dir_type):
    """
    Make sure common app directories exists, create them if not

    Args:
        app_name (string): name of application
        dir_type (string): which user directory to return
                           options: "data", "cache", "config"
    """
    if dir_type == "data":
        DIR = user_data_dir(app_name)
    elif dir_type == "cache":
        DIR = user_cache_dir(app_name)
    elif dir_type == "config":
        DIR = user_config_dir(app_name)
    else:
        logger.error(
            "Incorrect dir_type argument supplied. "
            + "Please choose one of 'data', 'cache', or 'config'."
        )

    if not os.path.isdir(DIR):
        try:
            os.makedirs(DIR)
            logger.debug(f"Created data directory: {DIR}")
        except OSError:
            logger.error(f"Failed to create directory: {DIR}")

    return DIR


def time_div(count):
    min, sec = divmod(count, 60)
    hour, min = divmod(min, 60)
    return (hour, min, sec)


def time_format(hour, min, sec):
    return f"{hour:02}:{min:02}:{sec:02}"


def time_print(count):
    hour, min, sec = time_div(count)
    return time_format(hour, min, sec)


def time_figlet_print(font, count):
    """
    Print time as ASCII art.

    Args:
        font (pyfiglet.Figlet): A Figlet "font" object.
        count (int): Number of seconds.

    Returns:
        Figlet string
    """
    hour, min, sec = time_div(count)
    return font.renderText(time_format(hour, min, sec))


def stopwatch(taskname):
    start_time = datetime.now()
    while True:
        end_time = datetime.now()
        duration = (end_time - start_time).seconds
        _write_tmp_info(taskname, start_time, end_time, duration)
        time.sleep(1)


def _write_tmp_info(taskname, start, end, duration):
    with open(TMP_FILE, "w") as f:
        f.write(f"{start}\n{end}\n{duration}\n{taskname}\n{time_print(duration)}")


def _read_tmp_info():
    with open(TMP_FILE, "r") as f:
        # ignoring the formatting duration, this is intended for external
        # tools accessing the tmp file
        start, end, duration, taskname, _ = f.read().split("\n")
        start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")
        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f")
        duration = int(duration)
    return (start, end, duration, taskname)


def _last_day_of_month(any_day):
    next_month = any_day.replace(28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)
