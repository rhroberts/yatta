import subprocess
import os


DATA_DIR = os.path.join(os.getenv('HOME'), '.local/share/yatta')
DATA_FILE = os.path.join(DATA_DIR, 'timesheet.csv')


def _check_for_datafile():
    if not os.path.isfile(DATA_FILE):
        _init_datafile()
        

def _init_datafile():
    subprocess.run(['mkdir', '-p', DATA_DIR])
    with open(DATA_FILE, 'w') as f:
        header = "start,end,task,duration\n"
        f.write(header)


def record_task(task, start, end, duration):
    with open(DATA_FILE, 'a') as f:
        f.write(f'{start},{end},{task},{duration}\n')


def print_timesheet():
    _check_for_datafile()
    with open(DATA_FILE, 'r') as f:
        timesheet = f.read()
    print(timesheet)
