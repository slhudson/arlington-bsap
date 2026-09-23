"""Residents by race/ethnicity, log-scale lines, 1870-2020 -> figures/residents_by_race_log.pdf, .png

The one figure here that uses a log axis, and it earns it: the crossover is
only visible on one. Black residents outnumbered White residents in 1870 and
1880, the two were close in 1890, and White residents pulled ahead by 1900. On
a linear axis at 2020's scale those decades are a flat line on the floor.

A log axis shows proportional change, not absolute change - worth a caption
note wherever it appears.

No assumption from code/build/assumptions.py is applied: blanks stay missing,
so each line begins the year its category is first reported. That is the
opposite of the stacked figures - see docs/questions.md.
"""
import pandas as pd
from matplotlib.ticker import FixedLocator, NullLocator

import charts
import files
import style

for profile in style.PROFILES:
    style.apply(profile)
    p = style.palette()

    c = pd.read_csv(files.RESIDENTS)
    series = {"total population": (c["total"], p["spacegrey"])}
    for g in style.GROUP_ORDER:
        series[style.GROUP_LABELS[g]] = (c[g], p[style.GROUP_HUES[g]])

    fig, ax = charts.figure(0.62, profile)
    charts.lines(ax, c["year"], series)

    ax.set_yscale("log")
    ax.set_ylim(30, 400000)
    ax.yaxis.set_major_locator(FixedLocator([100, 1000, 10000, 100000]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(charts.THOUSANDS)
    ax.set_ylabel("residents (log scale)")
    charts.years(ax, 1870, 2020, step=20)

    # White is the pale neutral, which is close to invisible as a line on white
    # paper. Legend rather than end labels here: five lines converge at the
    # right-hand edge, which is the case Urban's guide sends to a legend.
    ax.lines[style.GROUP_ORDER.index("white") + 1].set_color(p["spacegrey"])
    ax.lines[style.GROUP_ORDER.index("white") + 1].set_linestyle((0, (5, 2)))
    ax.lines[0].set_linestyle((0, (1, 1.6)))
    charts.legend(fig, {k: v[1] for k, v in series.items()})

    files.save(fig, "residents_by_race_log", profile)
