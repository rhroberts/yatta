"""
Functions to generate custom tab completions for click.
"""
import yatta.db as db


def get_matching_tasks(ctx, args, incomplete):
    task_names = [task.name for task in db.get_tasks().all()]
    return [task_name for task_name in task_names if incomplete in task_name]
