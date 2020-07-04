import logging
from calendar import monthrange
from datetime import datetime

import click
import parsedatetime as pdt
from tabulate import tabulate

from yatta import db as db
from yatta.config import Config
from yatta.plotting import _preproc_data, _weekday_to_label
from yatta.utils import time_print

logger = logging.getLogger(__name__)
cal = pdt.Calendar()


@click.command()
@click.option(
    "-d", "--day", "period", help="Print today's timesheet.", flag_value="day",
)
@click.option(
    "-w",
    "--week",
    "period",
    help="Print this week's timesheet.",
    flag_value="week",
    default=True,
)
@click.option(
    "-s", "--start-date", help="Report data from this date onward.", default="now"
)
def timesheet(period, start_date):
    """
    View daily and weekly timesheet summary.
    """
    start_date = datetime(*cal.parse(start_date)[0][:6])
    day_of_week = start_date.weekday()
    year, month, day = start_date.timetuple()[:3]
    if period == "day":
        start_date = datetime(year, month, day)
    elif period == "week":
        # week straddles two months
        if day_of_week > day:
            diff = day_of_week - day
            month = month - 1
            # week straddles two years
            if month == 0:
                month = 12
                year = year - 1
            day = monthrange(year, month)[1] - diff
            start_date = datetime(year, month, day)
        else:
            start_date = datetime(year, month, day - day_of_week)
    elif period == "month":
        start_date = datetime(year, month, 1)
    else:
        logger.error("Invalid timesheet period!")

    query = db.get_records()
    data = _preproc_data(db.query_to_df(query), period, start_date)
    if not data.empty:
        if period == "day":
            data.index = [_weekday_to_label(day_of_week)]
            data["TOTAL"] = data.sum(axis=1)
            for col in data:
                data[col] = data[col].apply(time_print)
            print(
                "\n"
                + tabulate(
                    data,
                    headers=data.columns,
                    tablefmt=Config().get_user_value("formatting", "table_style"),
                )
            )
        elif period == "week":
            data["TOTAL"] = data.sum(axis=1)
            data.loc["TOTAL"] = data.sum()
            for col in data:
                data[col] = data[col].apply(time_print)
            print(
                "\n"
                + tabulate(
                    data,
                    headers=data.columns,
                    tablefmt=Config().get_user_value("formatting", "table_style"),
                )
            )
        else:
            logger.error("Invalid timesheet period!")
    else:
        print("No data for this period!")
