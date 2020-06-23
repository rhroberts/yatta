import atexit
import curses
import logging
import os
import signal
import sys
import time
from datetime import datetime

import yatta.db as db
from appdirs import user_cache_dir
from filelock import FileLock, Timeout

APP_NAME = "yatta"
CACHE_DIR = user_cache_dir(APP_NAME)
TMP_FILE = os.path.join(CACHE_DIR, "active_task")
PID_FILE = os.path.join(CACHE_DIR, "yatta.pid")

logger = logging.getLogger(__name__)

# make sure cache directory exists, create it if not
if not os.path.isdir(CACHE_DIR):
    try:
        os.mkdir(CACHE_DIR)
        logger.debug(f"Created data directory: {CACHE_DIR}")
    except OSError:
        logger.error(f"Failed to create directory: {CACHE_DIR}")


# TODO: using logging, not durect stdout stderr
class Daemon:
    """
    A generic daemon class.
    Credit: https://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

    Usage: subclass the daemon class and override the run() method.
    """

    def __init__(self, pidfile):
        self.pidfile = pidfile

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write("fork #1 failed: {0}\n".format(err))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:

                # exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write("fork #2 failed: {0}\n".format(err))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, "r")
        so = open(os.devnull, "a+")
        se = open(os.devnull, "a+")

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile, "w+") as f:
            f.write(pid + "\n")

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon."""

        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, "r") as pf:

                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            message = "pidfile {0} already exist. " + "Daemon already running?\n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon."""

        # Get the pid from the pidfile
        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile {0} does not exist. " + "Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    def run(self):
        """You should override this method when you subclass Daemon.

        It will be called after the process has been daemonized by
        start() or restart()."""


class StopwatchDaemon(Daemon):
    def __init__(self, pidfile, taskname=None):
        Daemon.__init__(self, pidfile)
        self.taskname = taskname

    def run(self):
        stopwatch_daemon(self.taskname)


def daemon_start(taskname):
    daemon = StopwatchDaemon(PID_FILE, taskname)
    # start() will execute the hijacked run() func
    daemon.start()


def daemon_stop():
    daemon = StopwatchDaemon(PID_FILE)
    daemon.stop()
    try:
        start, end, duration, taskname = _read_tmp_info()
    except FileNotFoundError:
        print("No tasks are being tracked right now.")
        return
    # FIXME: Fetching task/record info from a 555 file in user space seems risky
    # create record
    record = db.Record(task_name=taskname, start=start, end=end, duration=duration)
    # at this point, the task has already been added to db in track(),
    # just need to fetch it
    task = db.get_tasks(taskname).first()
    db.add_record(task, record)
    db.update_task_total(task)
    print(
        f"\nWorked on {task.name} for {record.duration/3600:.2f}"
        + f"hrs ({time_print(record.duration)}) \u2714"
    )
    os.remove(TMP_FILE)


def daemon_status():
    if os.path.exists(PID_FILE):
        start, end, duration, taskname = _read_tmp_info()
        print(f"{taskname},{start},{end},{time_print(int(duration))}")
    else:
        print("No tasks are being tracked right now.")


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
