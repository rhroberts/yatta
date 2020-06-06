#!/usr/bin/env python
import click
import logging
from appdirs import user_data_dir
from .commands import track, list, edit, delete
from importlib import metadata

APP_NAME = "yatta"
DATA_DIR = user_data_dir(APP_NAME)

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


# add cli commands and command groups to main
main.add_command(track.track)
main.add_command(list.list)
main.add_command(edit.edit)
main.add_command(delete.delete)


if __name__ == "__main__":
    main()
