"""Residents and residents per Board seat, 1870-2020 -> figures/residents_per_seat.pdf, .png

Two series on one linear axis. Both are counts of people, so the vertical
distance between them means the same thing everywhere on the page - which a
second y-axis would not give: the Board held three seats before 1932 and five
after, so no single right-hand scale is right for the whole series, and picking
one decides which era looks like the exception.

Each line is named at its own end with its final value, which is Urban's
preference over a legend where the lines allow it.
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
        "residents per\nBoard seat": (d["residents_per_seat"], style.SERIES_COLORS["per_seat"]),
    }

    fig, ax = charts.figure(0.62, profile)
    charts.lines(ax, d["year"], series)
    charts.counts(ax, 250000, 50000)
    # Decades collide at this width; headroom is for the end labels, which sit
    # inside the axes so constrained layout accounts for them.
    charts.years(ax, 1870, 2020, step=20, headroom=0.30)
    charts.end_labels(ax, d["year"], series)
    charts.rule(ax)
    paths.save(fig, "residents_per_seat", profile)
