import click


@click.command()
@click.option(
    "-d",
    "--day",
    "period",
    help="Print today's timesheet.",
    flag_value="day",
    default=True,
)
@click.option(
    "-w", "--week", "period", help="Print this week's timesheet.", flag_value="week"
)
@click.option(
    "-m", "--month", "period", help="Print this month's timesheet.", flag_value="month"
)
def report(period):
    print(f"Your timesheet for the {period}:")
