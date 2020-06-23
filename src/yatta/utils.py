import curses
import logging
import os
import time
from datetime import datetime

from appdirs import user_data_dir
from filelock import FileLock, Timeout
from yatta.daemon import Daemon

APP_NAME = "yatta"
DATA_DIR = user_data_dir(APP_NAME)
TMP_FILE = os.path.join(DATA_DIR, "active_task")

logger = logging.getLogger(__name__)


class StopwatchDaemon(Daemon):
    def run(self):
        stopwatch_daemon()


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


def stopwatch(stdscr, taskname, font):
    # FIXME: This is redundant if implementing pid
    # Set lockfile to prevent recording multiple tasks at once
    lock = FileLock(f"{TMP_FILE}.lock")
    try:
        lock.acquire(timeout=0)
    except Timeout:
        return (None, None, None)

    QUIT_KEY = ord("q")
    curses.echo()
    curses.use_default_colors()
    stdscr.timeout(0)
    # FIXME: #7 this errors out if text overflows terminal
    stdscr.addstr(font.renderText(taskname))
    start_time = datetime.now()
    while True:
        count = int(time.time() - start_time.timestamp())
        stdscr.insstr(time_figlet_print(font, count))
        ch = stdscr.getch()
        stdscr.refresh()
        # _write_tmp_info(taskname, count)
        if ch == QUIT_KEY:
            end_time = datetime.now()
            lock.release()
            os.remove(TMP_FILE)
            break
    duration = (end_time - start_time).seconds
    return (start_time, end_time, duration)


def stopwatch_daemon(taskname):
    # # Set lockfile to prevent recording multiple tasks at once
    # lock = FileLock(f"{TMP_FILE}.lock")
    # try:
    #     lock.acquire(timeout=0)
    # except Timeout:
    #     return (None, None, None)

    start_time = datetime.now()
    while True:
        end_time = datetime.now()
        duration = (end_time - start_time).seconds
        _write_tmp_info(taskname, start_time, end_time, duration)

    # lock.release()
    # os.remove(TMP_FILE)


def _write_tmp_info(taskname, start, end, duration):
    with open(TMP_FILE, "w") as f:
        f.write(f"{taskname}\n{start}\n{end}\n{time_print(duration)}\n")
