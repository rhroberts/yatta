#!/usr/bin/env python
import curses
from pyfiglet import Figlet


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


def stopwatch(stdscr, task, font):
    QUIT_KEY = ord('q')
    curses.echo()
    curses.use_default_colors()
    stdscr.timeout(1000)
    stdscr.addstr(font.renderText(task))
    count = 0
    while True:
        stdscr.insstr(_time_figlet_print(font, count))
        count += 1
        ch = stdscr.getch()
        stdscr.refresh()
        if ch == QUIT_KEY:
            break
    return(count)


if __name__ == "__main__":
    # FIXME: this errors out if text overflows terminal
    task = "Test"
    font = Figlet(font='larry3d')
    count = curses.wrapper(stopwatch, task, font)
    print(f"\nTotal {_time_print(count)}")
