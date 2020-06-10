import logging
from datetime import datetime

import click
import parsedatetime as pdt
import yatta.db as db
import yatta.plotting as plt

logger = logging.getLogger(__name__)


@click.group()
def plot():
    pass


@plot.command()
@click.option("-d", "--day", "period", help="Plot today's timesheet.", flag_value="day")
@click.option(
    "-w",
    "--week",
    "period",
    help="Plot this week's timesheet.",
    flag_value="week",
    default=True,
)
@click.option(
    "-m", "--month", "period", help="Plot this month's timesheet.", flag_value="month"
)
@click.option(
    "-d", "--start-date", help="Plot data from this date onward.", default="today"
)
def records(period, start_date):
    day_of_week = datetime.now().weekday()
    year, month, day = datetime.now().timetuple()[:3]
    if period == "day":
        start_date = datetime(year, month, day)
    elif period == "week":
        start_date = datetime(year, month, day - day_of_week)
    elif period == "month":
        start_date = datetime(year, month, 1)
    else:
        logger.error("Invalid plot period!")

    query = db.get_records()
    df = db.query_to_df(query)
    plt._prep_hbar_stack(df, period, start_date)
