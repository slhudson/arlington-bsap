"""Residents and residents per Board seat, 1870-2020 -> figures/residents_per_seat.pdf, .png

Two lines on one count axis, a marker per census, each labelled at its
last point with its 2020 value, with the 1932 rule. No legend.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.RESIDENTS)[["year", "total", "residents_per_seat"]].dropna()
    series = {label: (d[col], colour) for col, (label, colour)
              in (("total", style.POPULATION), ("residents_per_seat", style.PER_SEAT))}

    fig, ax = charts.figure(profile)
    charts.lines(ax, d["year"], series)
    charts.counts(ax, 250000, 50000)
    charts.years(ax, 1870, 2020, step=20)

    last = d.iloc[-1]
    charts.end_label(ax, 2020, last["total"],
                     f"2020 population:\n{int(last['total']):,}",
                     style.POPULATION[1], gap=0.035)
    charts.end_label(ax, 2020, last["residents_per_seat"],
                     f"2020 residents\nper Board seat:\n"
                     f"{int(round(last['residents_per_seat'])):,}",
                     style.PER_SEAT[1], where="above", gap=0.02)

    charts.rule(ax)
    paths.save(fig, "residents_per_seat", profile)
