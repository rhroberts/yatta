import click
import pandas

df = pandas.DataFrame([])


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
def timesheet(period):
    print(f"Your timesheet for the {period}:")
