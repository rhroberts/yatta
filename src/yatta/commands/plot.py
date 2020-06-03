import click


@click.command()
@click.option(
    "-d",
    "--day",
    "period",
    help="Plot today's timesheet.",
    flag_value="day",
    default=True,
)
@click.option(
    "-w", "--week", "period", help="Plot this week's timesheet.", flag_value="week"
)
@click.option(
    "-m", "--month", "period", help="Plot this month's timesheet.", flag_value="month"
)
def plot(period):
    print(f"Plot of your timesheet for the {period}.")
