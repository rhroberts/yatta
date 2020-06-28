"""
Functions to generate custom tab completions for click.
"""
import tabulate
import yatta.db as db
from pyfiglet import Figlet
from yatta.config import Config


def get_matching_tasks(ctx, args, incomplete):
    task_names = [task.name for task in db.get_tasks().all()]
    return [task_name for task_name in task_names if incomplete in task_name]


def get_figlet_fonts(ctx, args, incomplete):
    f = Figlet(Config().get_user_value("formatting", "figlet_font"))
    fonts = sorted(f.getFonts())
    return [font for font in fonts if incomplete in font]


def get_table_formats(ctx, args, incomplete):
    return [fmt for fmt in tabulate.tabulate_formats if incomplete in fmt]
