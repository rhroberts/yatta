import logging
from datetime import datetime

import click
import parsedatetime as pdt
import yatta.db as db
import yatta.plotting as plt
from yatta.config import Config

logger = logging.getLogger(__name__)

cal = pdt.Calendar()


@click.command()
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
    "-s", "--start-date", help="Plot data from this date onward.", default="now"
)
@click.option(
    "-c",
    "--columns",
    type=click.INT,
    help="Maximum columns on screen for plot to occupy.",
    default=Config().get_user_value("plotting", "columns"),
)
def plot(period, start_date, columns):
    """
    Visualize summary data.
    """
    start_date = datetime(*cal.parse(start_date)[0][:6])
    day_of_week = start_date.weekday()
    year, month, day = start_date.timetuple()[:3]
    if period == "day":
        start_date = datetime(year, month, day)
    elif period == "week":
        start_date = datetime(year, month, day - day_of_week)
    elif period == "month":
        start_date = datetime(year, month, 1)
    else:
        logger.error("Invalid plot period!")

    query = db.get_records()
    data = plt._preproc_data(db.query_to_df(query), period, start_date)
    if not data.empty:
        if period == "day":
            plt.hbar(data, columns)
        elif period == "week":
            plt.hbar_stack(data, columns)
        elif period == "month":
            plt.hbar_stack(data, columns)
        else:
            logger.error("Invalid plot period!")
    else:
        print("No data for this period!")
