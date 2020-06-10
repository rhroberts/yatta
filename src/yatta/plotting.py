import logging
from datetime import datetime, timedelta
from random import randint

import colorama as co
import numpy as np
import pandas as pd
import yatta.utils as utils

logger = logging.getLogger(__name__)

plot_unit = "▇"
co.init(autoreset=True)

days = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}


def _weekday_to_label(weekday):
    """
    Convert weekday index to string weekday

    Args:
        weekday (int): Day of the week [0-6]

    Returns:
        (string): Weekday as "mon", "tue", etc.
    """
    return days[weekday]


def _prep_hbar_stack(data, period, start_date):
    """
    Take dataframe returned from yatta.db.query_to_df() and format for
    plotting in hbar_stack()

    Args:
        data (pd.DataFrame): Dataframe from yatta.db.query_to_df()

    Returns:
        data (pd.DataFrame): Dataframe with string index labels and unique tasks as columns
    """
    if period == "day":
        pass
    elif period == "week":
        df = data[
            (data["start"] >= start_date)
            & (data["start"] <= start_date + timedelta(days=7))
        ]
        if df.empty:
            return df
        # break up into days, format df
        group = df.groupby(["start", "task_name"])
        df = group.sum().reset_index()
        df["weekday"] = df["start"].dt.weekday.apply(_weekday_to_label)
        # build properly formatted dataframe
        data_fmt = pd.DataFrame(index=days.values(), columns=df["task_name"].unique())
        for col in data_fmt.columns:
            task_df = df.loc[df["task_name"] == col]
            data_fmt.loc[task_df["weekday"], col] = task_df["duration"].values
        data_fmt = data_fmt.dropna(axis=0, how="all").fillna(0)
    elif period == "month":
        pass
    else:
        logger.error("Invalid plot period!")

    return data_fmt


def _normalize_data(y, width=50, norm_factor=1):
    """
    Normalize dependent variable to screen width.

    Args:
        y (np.array): Numpy array of ints or floats.
        width (int): Maximum screen columns.

    Returns:
        y (np.array): Normalized list of ints.
    """
    y = (y / norm_factor) * width
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
    norm_factor = data.T.sum().max()
    data_norm = data.apply(_normalize_data, args=([width, norm_factor]))
    fcolors = [
        co.Fore.LIGHTGREEN_EX,
        co.Fore.LIGHTBLUE_EX,
        co.Fore.LIGHTMAGENTA_EX,
        co.Fore.LIGHTYELLOW_EX,
        co.Fore.LIGHTRED_EX,
    ]
    legend = {}
    print()
    for i in range(len(data_norm.index)):
        print(f"{co.Fore.BLUE}{str(labels[i])}: ", end="")
        for n, val in enumerate(data_norm.iloc[i]):
            fc = fcolors[n % len(data_norm.columns)]
            label = data_norm.columns[n]
            if label not in legend:
                legend[label] = fc
            s = plot_unit * val
            print(f"{legend[label]}{s}", end="")
        print(f" {utils.time_print(data.iloc[i].sum())}")

    # color legend
    print()
    print("     ", end="")
    for label, fc in legend.items():
        print(f"{fc}{plot_unit*3} {label} ", end="")
    print()


if __name__ == "__main__":
    week = ["mon", "tue", "wed", "thu", "fri"]
    d = [[randint(0, 9000) for i in range(5)] for j in range(10)]
    d = np.array(d).T
    data = pd.DataFrame(d, index=week)
    hbar_stack(data, width=100)
    print(data)
