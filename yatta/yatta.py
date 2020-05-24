#!/usr/bin/env python
import os
import subprocess
import click
from appdirs import user_data_dir
import yatta.db as db
from yatta.cli import track, list, edit

APP_NAME = 'yatta'
DATA_DIR = user_data_dir(APP_NAME)

CLICK_CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
)


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
@click.version_option(version='0.0.1')
def main():
    pass


# add cli commands and command groups to main
main.add_command(track.track)
main.add_command(list.list)
main.add_command(edit.edit)


if __name__ == "__main__":
    # make sure app directory exists, create it if not
    if not os.path.isdir(DATA_DIR):
        subprocess.run(['mkdir', '-p', DATA_DIR])
    main()
    db.session.close()
