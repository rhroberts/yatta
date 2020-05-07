#!/usr/bin/env python

import curses
from datetime import datetime

SPACE_KEY = ord(' ')

def run(win):
    curses.echo()
    win.timeout(1000) # Wait at most one second for a key.

    start = datetime.now()
    while True:
        now = datetime.now()
        minutes, seconds = divmod((now - start).total_seconds(), 60)
        win.addstr(0, 0, "%02d:%02d" % (minutes, round(seconds)))

        c = win.getch()
        if c == SPACE_KEY:
            break

curses.wrapper(run)
