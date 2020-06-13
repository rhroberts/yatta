import logging
from datetime import timedelta

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


def _prep_data_for_plot(data, period, start_date):
    """
    Take dataframe returned from yatta.db.query_to_df() and format for
    plotting in hbar_stack()

    Args:
        data (pd.DataFrame): Dataframe from yatta.db.query_to_df()

    Returns:
        data (pd.DataFrame): Dataframe with string index labels and unique tasks as
                             columns
    """
    if period == "day":
        df = data[
            (data["start"] >= start_date)
            & (data["start"] < start_date + timedelta(days=1))
        ]
        if df.empty:
            return df
        df = df.groupby(["task_name", "task_id"]).sum().droplevel("task_id").T
        df.columns = df.columns.values
        data_fmt = df
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


def _normalize_data(y, columns=50, norm_factor=1):
    """
    Normalize dependent variable to screen width.

    Args:
        y (np.array): Numpy array of ints or floats.
        columns (int): Maximum screen columns.

    Returns:
        y (np.array): Normalized list of ints.
    """
    y = (y / norm_factor) * columns
    y = [int(np.round(val, 0)) for val in y]
    return y


def hbar(data, columns=50):
    """
    Print horizontal bar chart to stdout.

    Args:
        data (pd.Series): Data to plot.
        columns (int): Maximum screen columns.

    Returns:
        None
    """
    norm_factor = data.values.max()
    data_norm = data.apply(_normalize_data, args=([columns, norm_factor]))
    fcolors = [
        co.Fore.LIGHTGREEN_EX,
        co.Fore.LIGHTBLUE_EX,
        co.Fore.LIGHTMAGENTA_EX,
        co.Fore.LIGHTYELLOW_EX,
        co.Fore.LIGHTRED_EX,
    ]
    print()
    for n, col in enumerate(data_norm.columns):
        val = data_norm[col].values[0]
        s = plot_unit * val
        print(
            f"{co.Fore.RESET}{utils.time_print(data[col].values[0])} "
            + f"{fcolors[(n % len(fcolors))]}{s} {col}"
        )


def hbar_stack(data, columns=50):
    """
    Print horizontal bar chart to stdout.

    Args:
        data (pd.DataFrame): Data to plot.
        columns (int): Maximum screen columns.

    Returns:
        None
    """
    labels = data.index
    norm_factor = data.T.sum().max()
    data_norm = data.apply(_normalize_data, args=([columns, norm_factor]))
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
            fc = fcolors[n % len(fcolors)]
            label = data_norm.columns[n]
            if label not in legend:
                legend[label] = fc
            s = plot_unit * val
            print(f"{legend[label]}{s}", end="")
        print(f" {utils.time_print(data.iloc[i].sum())}")

    # color legend
    print()
    print("     ", end="")
    i = 1
    for label, fc in legend.items():
        if i % 4 != 0:
            print(f"{fc}{plot_unit*3} {label} ", end="  ")
        else:
            print(f"\n     {fc}{plot_unit*3} {label} ", end="  ")
        i += 1
    print()
