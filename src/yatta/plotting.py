import logging
from datetime import datetime, timedelta

import colorama as co
import numpy as np
import pandas as pd

from yatta import utils as utils

logger = logging.getLogger(__name__)

plot_unit = "▇"
co.init(autoreset=True)

days = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}

fcolors = [
    co.Fore.LIGHTGREEN_EX,
    co.Fore.LIGHTBLUE_EX,
    co.Fore.LIGHTMAGENTA_EX,
    co.Fore.LIGHTYELLOW_EX,
    co.Fore.LIGHTRED_EX,
    co.Fore.LIGHTCYAN_EX,
    co.Fore.LIGHTBLACK_EX,
    co.Fore.GREEN,
    co.Fore.BLUE,
    co.Fore.MAGENTA,
    co.Fore.YELLOW,
    co.Fore.RED,
    co.Fore.CYAN,
]


def _weekday_to_label(weekday):
    """
    Convert weekday index to string weekday

    Args:
        weekday (int): Day of the week [0-6]

    Returns:
        (string): Weekday as "mon", "tue", etc.
    """
    return days[weekday]


def _month_split(year, month):
    """
    Split month into calendar weeks.

    Args:
        year (int)
        month (int)

    Returns:
        weeks (dict): Dict of tuples with start/end datetime for each calendar week.
    """
    _date = datetime(year, month, 1)
    dow = _date.weekday()
    weeks = {}
    i = 0
    while _date.month == month:
        year, month, day = _date.timetuple()[:3]
        try:
            weeks[i] = (
                datetime(year, month, day),
                datetime(year, month, day + (6 - dow)),
            )
        except ValueError:
            # adjust end datetime if it would end in a new month
            weeks[i] = (
                datetime(year, month, day),
                datetime(year, month + 1, 1) - timedelta(days=1),
            )
        try:
            _date += timedelta(days=7)
        except ValueError:
            # adjust end datetime if it would end in a new month
            _date = datetime(year, month + 1, 1) - timedelta(days=1)
        i += 1

    return weeks


def _preproc_data(data, period, start_date):
    """
    Take dataframe returned from yatta.db.query_to_df() and format for
    timesheet or plotting in hbar_stack()

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
            & (data["start"] < start_date + timedelta(days=7))
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
            data_fmt.loc[task_df["weekday"], col] = task_df.groupby(["weekday"]).sum()[
                "duration"
            ]
        data_fmt = data_fmt.dropna(axis=0, how="all").fillna(0)
    elif period == "month":
        year, month, day = start_date.timetuple()[:3]
        df = data[
            (data["start"] >= start_date)
            & (data["start"] < datetime(year, month + 1, day))
        ].sort_values(["start"])
        if df.empty:
            return df
        # Split data into calendar weeks...
        df["week"] = 0
        weeks = _month_split(year, month)
        for week, week_range in weeks.items():
            df.loc[
                (df["start"] >= week_range[0]) & (df["start"] < week_range[1]), "week"
            ] = week
        df = df.groupby(["week", "task_name"]).sum()
        tmp = pd.DataFrame(
            columns=df.index.get_level_values(1).unique().values,
            index=df.index.get_level_values(0).unique().values,
        )
        data_fmt = df.loc[df.index.get_level_values(0) == 0].T
        for col in tmp.columns:
            for week in tmp.index:
                val = df.loc[
                    (df.index.get_level_values(1) == col)
                    & (df.index.get_level_values(0) == week),
                    "duration",
                ].values
                try:
                    tmp.loc[week, col] = val[0]
                except IndexError:
                    tmp.loc[week, col] = 0
        # convert from week index to date range
        if year == datetime.now().year:
            tmp.index = [
                f"{weeks[i][0].strftime('%d')}-{weeks[i][1].strftime('%d %b')}"
                for i in tmp.index
            ]
        else:
            tmp.index = [
                f"{weeks[i][0].strftime('%d')}-{weeks[i][1].strftime('%d %b %Y')}"
                for i in tmp.index
            ]

        data_fmt = tmp
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
    data_norm = data_norm.T.sort_values("duration", ascending=False).T
    print()
    for n, col in enumerate(data_norm.columns):
        val = data_norm[col].values[0]
        s = plot_unit * val
        print(
            f"{co.Fore.RESET}{utils.time_print(data[col].values[0])} "
            + f"{fcolors[(n % len(fcolors))]}{s} {col}"
        )


def hbar_stack(data, columns=50, show_legend=True):
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
    legend = {}
    print()
    for i in range(len(data_norm.index)):
        print(f"{co.Fore.BLUE}{str(labels[i])}: ", end="")
        sorted_row = data_norm.iloc[i].sort_values(ascending=False)
        for n, val in enumerate(sorted_row):
            fc = fcolors[n % len(fcolors)]
            label = sorted_row.index[n]
            if label not in legend:
                legend[label] = fc
            s = plot_unit * val
            print(f"{legend[label]}{s}", end="")
        print(f" {utils.time_print(data.iloc[i].sum())}")

    # color legend
    # pad legend to same column as actual plotted data
    # eg: "mon: " --> legend_pad = 5, "01-08 Jun: " --> legend_pad = 11
    if show_legend:
        legend_pad = len(data_norm.index.values[0]) + 2
        pad = " " * legend_pad
        print()
        print(pad, end="")
        i = 1
        rows = int(columns / 10)
        for label, fc in legend.items():
            if i % rows != 0:
                print(f"{fc}{plot_unit*3} {label} ", end="  ")
            else:
                print(f"\n{pad}{fc}{plot_unit*3} {label} ", end="  ")
            i += 1
        print()
