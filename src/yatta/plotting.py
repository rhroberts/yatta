"""
Origin gnuplot script:

    set terminal dumb aspect 2 size 79, 24
    set datafile separator ","
    set key autotitle columnhead
    set style data histograms
    set style histogram cluster
    # set boxwidth 1 relative
    set style fill solid 1.0 border -1
    # plot '~/ownCloud/yatta_data/timesheet.csv' using 0:5
    # plot for [COL=2:-1:1] 'scratch.csv' using COL:xticlabels(1)
    plot 'scratch.csv' using 1:6

"""
# TODO: switch to termplotlib: https://github.com/nschloe/termplotlib
from appdirs import user_data_dir
import PyGnuplot as gp
import os

import yatta.db as db


APP_NAME = "yatta"
DATA_DIR = user_data_dir(APP_NAME)

tmp_file = os.path.join(DATA_DIR, 'tmp.dat')
df = db.query_to_df(db.get_records())
x = df.index.values
y = df['duration'].values

gp.c("set terminal dumb")
gp.s([x, y], filename=tmp_file)
gp.c(f'plot "{tmp_file}" w p')
