"""Residents and residents per Board seat, 1870-2020 -> figures/residents_per_seat.pdf, .png

Two lines on one count axis, a marker per census, with a legend
and the 1932 rule.
"""

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = paths.read("residents")[["year", "total", "residents_per_seat"]].dropna()
    series = {label: (d[col], colour) for col, (label, colour)
              in (("total", style.POPULATION), ("residents_per_seat", style.PER_SEAT))}

    fig, ax = charts.figure(profile)
    charts.lines(ax, d["year"], series)
    charts.counts(ax, 250000, 50000)
    charts.years(ax, 1870, 2020, step=20)

    charts.rule(ax)
    charts.legend(fig, series)
    paths.save(fig, profile)
