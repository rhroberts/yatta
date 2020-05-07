#!/usr/bin/env python
import time
import curses
from pyfiglet import Figlet


def _time_print(font, hour, min, sec):
    if hour != 0:
        htext = f"{hour}h "
    else:
        htext = ""
    if min != 0:
        mtext = f"{min}m "
    else:
        mtext = ""
    stext = f"{sec}s"

    time_str = font.renderText(f"{htext}{mtext}{stext}")
    return(time_str)


def _stopwatch(stdscr, font):
    try:
        count = 0
        while True:
            min, sec = divmod(count, 60)
            hour, min = divmod(min, 60)
            stdscr.insstr(_time_print(font, hour, min, sec))
            time.sleep(1)
            count += 1
            stdscr.refresh()
    except KeyboardInterrupt:
        pass
    return(count)


if __name__ == "__main__":
    stdscr = curses.initscr()
    font = Figlet(font='larry3d')
    count = _stopwatch(stdscr, font)
    stdscr.clear()
    # stdscr.insstr(font.renderText(f"\nTotal: {count} seconds"))
    print(f"\nTotal: {count} seconds")
