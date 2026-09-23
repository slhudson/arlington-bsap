"""Residents and residents per Board seat, 1870-2020 -> figures/residents_per_seat.pdf, .png

Two series on one linear axis. Both are counts of people, so the vertical
distance between them means the same thing everywhere on the page - which a
second y-axis would not give: the Board held three seats before 1932 and five
after, so no single right-hand scale is right for the whole series, and picking
one decides which era looks like the exception.

Each line is named where it runs, on one line, with its final value. Urban puts
such a label at the far right just outside the plot; a label long enough to be
readable needs enough headroom past 2020 to visibly stretch the axis, which
distorts the series to make room for its own caption.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.RESIDENTS)[["year", "total", "residents_per_seat"]].dropna()
    series = {
        "total population": (d["total"], style.SERIES_COLORS["population"]),
        "residents per Board member": (d["residents_per_seat"],
                                       style.SERIES_COLORS["per_seat"]),
    }

    fig, ax = charts.figure(style.SERIES, profile)
    charts.lines(ax, d["year"], series)
    charts.counts(ax, 250000, 50000)
    # Decades collide at this width, so labels every twenty years with an
    # unlabelled tick at each census between. No headroom: the labels sit in
    # the space between the two lines rather than past the end of the data.
    charts.years(ax, 1870, 2020, step=20)

    # Each label sits in the empty band between the series: above the per-seat
    # line and below the population line, from 1958 where both are far apart.
    last = d.iloc[-1]
    charts.label_line(ax, 1958, 128000,
                      f"total population: {int(last['total']):,}",
                      style.SERIES_COLORS["population"])
    charts.label_line(ax, 1958, 72000,
                      f"residents per Board member: {int(round(last['residents_per_seat'])):,}",
                      style.SERIES_COLORS["per_seat"])

    charts.rule(ax)
    paths.save(fig, "residents_per_seat", profile)
