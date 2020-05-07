#!/usr/bin/env python
import curses
from pyfiglet import Figlet


def _time_div(count):
    min, sec = divmod(count, 60)
    hour, min = divmod(min, 60)
    return(hour, min, sec)


def _time_print(font, count, figlet=True):
    hour, min, sec = _time_div(count)
    if figlet:
        time_str = font.renderText(f"{hour:02}:{min:02}:{sec:02}")
    else:
        time_str = f"{hour:02}:{min:02}:{sec:02}"
    return(time_str)


def _stopwatch(stdscr, task, font, figlet=True):
    QUIT = ord('q')
    h, w = stdscr.getmaxyx()
    curses.echo()
    stdscr.timeout(1000)
    count = 0
    if figlet:
        stdscr.addstr(font.renderText(task))
    else:
        stdscr.addstr(task)

    while True:
        stdscr.insstr(_time_print(font, count, figlet))
        count += 1
        ch = stdscr.getch()
        stdscr.refresh()
        if ch == QUIT:
            break
    return(count)


def main(stdscr, task, font, figlet=True):
    curses.use_default_colors()
    count = _stopwatch(stdscr, task, font, figlet)
    return(count)


if __name__ == "__main__":
    task = "Temporary Task"
    font = Figlet(font='larry3d')
    count = curses.wrapper(main, task, font, figlet=False)
    # TODO: make it optional to pass font
    print(f"\nTotal {_time_print(font, count, figlet=False)}")
