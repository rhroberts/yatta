#!/usr/bin/env python
import logging

import click

from yatta import utils as utils
from yatta.commands import config, delete, edit, list, plot, start, timesheet
from yatta.daemon import daemon_status, daemon_stop

try:
    from importlib import metadata
except ImportError:  # for Python < 3.8
    import importlib_metadata as metadata

APP_NAME = "yatta"
DATA_DIR, CONFIG_DIR, CACHE_DIR = utils.get_app_dirs()

CLICK_CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"],)


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
@click.version_option(version=metadata.version(APP_NAME))
@click.option("-l", "--log_level", default="warning")
def main(log_level):
    # setup logging
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(
        format="--> %(levelname)s in %(name)s: %(message)s", level=numeric_level
    )


@click.command()
def status():
    """
    Check status of active task.
    """
    daemon_status()


@click.command()
def stop():
    """
    Stop tracking the active task.
    """
    daemon_stop()


# add cli commands and command groups to main
main.add_command(start.start)
main.add_command(list.list)
main.add_command(edit.edit)
main.add_command(delete.delete)
main.add_command(plot.plot)
main.add_command(timesheet.timesheet)
main.add_command(config.config)
main.add_command(status)
main.add_command(stop)


if __name__ == "__main__":
    main()
