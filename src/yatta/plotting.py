import colorama as co
import numpy as np
import pandas as pd
from random import randint

import yatta.utils as utils

plot_unit = '▇'
co.init(autoreset=True)


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
    y = (y*width)/(y_max*numcols)
    y = [int(np.round(val, 0)) for val in y]
    return(y)


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
        s = ''
        for i in range(val):
            s += plot_unit
        print(f"{co.Fore.BLUE}{str(labels[n])}: " +
              f"{co.Fore.GREEN}{s} {co.Fore.MAGENTA}{str(y[n])}")


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
            s = plot_unit*val
            print(f"{legend[label]}{s}", end="")
        print(f"{co.Fore.WHITE} {utils.time_print(data.iloc[i].sum())}")

    # color legend
    print()
    print("     ", end="")
    for label, fc in legend.items():
        print(f"{fc}{plot_unit*5} {label} ", end="")
    print()


if __name__ == '__main__':
    week = ['mon', 'tue', 'wed', 'thu', 'fri']
    d = [[randint(0, 9000) for i in range(5)] for j in range(10)]
    d = np.array(d).T
    data = pd.DataFrame(d, index=week)
    hbar_stack(data, width=100)
