"""Residents by age band, 1930-2020 -> figures/residents_by_age.pdf, .png

One panel: every resident, as stacked bars in style.RESIDENT_AGES with the
youngest band at the base. Shares rather than counts, and children included
though they cannot vote.
"""

import charts
import paths
import style

FIRST = 1930         # from 1930, the earliest county age table we hold
BARS = 7             # years per bar, as on the other census figures

for profile in style.PROFILES:
    style.apply(profile)

    bands = list(style.RESIDENT_AGES)
    c = paths.read("residents")
    c = c[c["year"] >= FIRST].reset_index(drop=True)
    shares = c[bands].astype(float).div(c["total"], axis=0) * 100

    fig, ax = charts.figure(profile, of_width=style.NARROW)
    stacked = charts.series(shares, style.RESIDENT_AGES)
    charts.stacked_bars(ax, c["year"], stacked, width=BARS)
    charts.shares(ax)
    charts.years(ax, FIRST, 2020, step=10, bars=BARS, dense=True)

    charts.legend(fig, stacked, ncol=4)
    paths.save(fig, profile)
