"""
Functions to generate custom tab completions for click.
"""
import yatta.db as db
from yatta.utils import time_print


def get_matching_tasks(ctx, args, incomplete):
    task_names = [task.name for task in db.get_tasks().all()]
    return [task_name for task_name in task_names if incomplete in task_name]


def get_matching_records(ctx, args, incomplete):
    record_info = [
        "ID="
        + str(record.id)
        + ","
        + "Task="
        + str(db.get_tasks(record.task_id).first().name)
        + "Duration="
        + str(time_print(record.duration))
        for record in db.get_records().all()
    ]
    return [record for record in record_info if incomplete in record]
