import logging
from datetime import datetime
from random import randint

import colorama as co
import numpy as np
import pandas as pd
import yatta.utils as utils

logger = logging.getLogger(__name__)

plot_unit = "▇"
co.init(autoreset=True)

days = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}


def _prep_hbar_stack(data, period, start_date):
    """
    Take dataframe returned from yatta.db.query_to_df() and format for
    plotting in hbar_stack()

    Args:
        data (pd.DataFrame): Dataframe from yatta.db.query_to_df()

    Returns:
        data (pd.DataFrame): Dataframe with string labels and normalized columns
    """
    if period == "day":
        pass
    elif period == "week":
        week_df = data[
            (data["start"] >= start_date) & (data["start"] <= datetime.now())
        ]
        print(week_df)
    elif period == "month":
        pass
    else:
        logger.error("Invalid plot period!")


def _normalize_data(y, width=50, numcols=1):
    """
    Normalize dependent variable to screen width.

    Args:
        y (np.array): Numpy array of ints or floats.
        width (int): Maximum screen columns.

    Returns:
        y (np.array): Normalized list of ints.
    """
    y_max = np.max(y)
    y = (y * width) / (y_max * numcols)
    y = [int(np.round(val, 0)) for val in y]
    return y


def hbar(data, width=50):
    """
    Print horizontal bar chart to stdout.

    Args:
        data (pd.Series): Data to plot.
        width (int): Maximum screen columns.

    Returns:
        None
    """
    labels = data.index
    y = data.values
    y_norm = _normalize_data(y=y, width=width)
    print()
    for n, val in enumerate(y_norm):
        s = ""
        for i in range(val):
            s += plot_unit
        print(
            f"{co.Fore.BLUE}{str(labels[n])}: "
            + f"{co.Fore.GREEN}{s} {co.Fore.MAGENTA}{str(y[n])}"
        )


def hbar_stack(data, width=50):
    """
    Print horizontal bar chart to stdout.

    Args:
        data (pd.DataFrame): Data to plot.
        width (int): Maximum screen columns.

    Returns:
        None
    """
    labels = data.index
    data_norm = data.apply(_normalize_data, args=([width, len(data.columns)]))
    fcolors = [
        co.Fore.LIGHTGREEN_EX,
        co.Fore.LIGHTBLUE_EX,
        co.Fore.LIGHTMAGENTA_EX,
        co.Fore.LIGHTYELLOW_EX,
        co.Fore.LIGHTRED_EX,
    ]
    legend = {}
    print()
    # TODO: colors need to stick w/ tasks across days
    for i in range(len(data_norm.index)):
        print(f"{co.Fore.BLUE}{str(labels[i])}: ", end="")
        for n, val in enumerate(data_norm.iloc[i]):
            fc = fcolors[n % len(data_norm.index)]
            label = data_norm.columns[n]
            if label not in legend:
                legend[label] = fc
            s = plot_unit * val
            print(f"{legend[label]}{s}", end="")
        print(f"{co.Fore.WHITE} {utils.time_print(data.iloc[i].sum())}")

    # color legend
    print()
    print("     ", end="")
    for label, fc in legend.items():
        print(f"{fc}{plot_unit*5} {label} ", end="")
    print()


if __name__ == "__main__":
    # week = ['mon', 'tue', 'wed', 'thu', 'fri']
    # d = [[randint(0, 9000) for i in range(5)] for j in range(10)]
    # d = np.array(d).T
    # data = pd.DataFrame(d, index=week)
    # hbar_stack(data, width=100)
    pass
