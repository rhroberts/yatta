import curses
from datetime import datetime


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
    QUIT_KEY = ord("q")
    curses.echo()
    curses.use_default_colors()
    # FIXME: timeout gets reset when resizing terminal
    stdscr.timeout(1000)
    # FIXME: this errors out if text overflows terminal
    print(f"Taskname: {taskname}")
    stdscr.addstr(font.renderText(taskname))
    count = 0
    start_time = datetime.now()
    while True:
        stdscr.insstr(time_figlet_print(font, count))
        count += 1
        ch = stdscr.getch()
        stdscr.refresh()
        if ch == QUIT_KEY:
            end_time = datetime.now()
            break
    duration = (end_time - start_time).seconds
    return (start_time, end_time, duration)
