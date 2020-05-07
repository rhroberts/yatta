#!/usr/bin/env python
import time
import sys

def _time_print(h, m, s):
    if h == 1:
        htext = f"{h} hour "
    elif h != 0:
        htext = f"{h} hours "
    else:
        htext = ""
    if m == 1:
        mtext = f"{m} minute "
    elif m != 0:
        mtext = f"{m} minutes "
    else:
        mtext = ""
    if s == 1:
        stext = f"{s} second"
    else:
        stext = f"{s} seconds"
    return(f"\u23F0 {htext}{mtext}{stext} have elapsed \u23F0")
try:
    n = 0
    while True:
        m, s = divmod(n, 60)
        h, m = divmod(m, 60)
        sys.stdout.write("\r")
        sys.stdout.write(_time_print(h, m, s))
        sys.stdout.flush()
        time.sleep(1)
        n += 1
except KeyboardInterrupt:
    pass

print(f"\nTotal: {n} seconds")
