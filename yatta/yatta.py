#!/usr/bin/env python
import curses
import click
from pyfiglet import Figlet

CLICK_CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
)


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


def _stopwatch(stdscr, task, font):
    QUIT_KEY = ord('q')
    curses.echo()
    curses.use_default_colors()
    stdscr.timeout(1000)
    # FIXME: this errors out if text overflows terminal
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


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
@click.version_option(version='0.0.1')
def main():
    pass


@main.command()
@click.argument('task')
@click.option('-f', '--font', default='doom',
              help='Select figlet font (http://www.figlet.org/).')
def track(task, font, **kwargs):
    font = Figlet(font=font)
    count = curses.wrapper(_stopwatch, task, font)
    print(f"\nWorked on {task} for {count/3600:.2f} hrs" +
          f" ({_time_print(count)}) \u2714")
    return(count)


@main.command()
@click.option('-d', '--day', 'period', help='Print today\'s timesheet.',
              flag_value='day', default=True)
@click.option('-w', '--week', 'period', help='Print this week\'s timesheet.',
              flag_value='week')
@click.option('-m', '--month', 'period', help='Print this month\'s timesheet.',
              flag_value='month')
def report(period):
    print(f'This is your timesheet for the {period}.')


@main.command()
@click.option('-d', '--day', 'period', help='Plot today\'s timesheet.',
              flag_value='day', default=True)
@click.option('-w', '--week', 'period', help='Plot this week\'s timesheet.',
              flag_value='week')
@click.option('-m', '--month', 'period', help='Plot this month\'s timesheet.',
              flag_value='month')
def plot(period):
    print(f'Plot of your timesheet for the {period}.')


@main.command()
@click.option('-a', '--age', help="Archive data older than X days.",
              default=90)
@click.confirmation_option(prompt='Are you sure you want to archive old data?')
def archive(age):
    print(f'\nOK. Data recorded more than {age} days ago has been archived.')


if __name__ == "__main__":
    main()
