"""Residents by age band, 1980-2020 -> figures/residents_by_age.pdf, .png

One panel: every resident, as stacked bars in style.RESIDENT_AGES with the
youngest band at the base. Shares rather than counts, and children included
though they cannot vote.
"""
import pandas as pd

import charts
import paths
import style

FIRST = 1980         # the first census that reports age this way

for profile in style.PROFILES:
    style.apply(profile)

    bands = list(style.RESIDENT_AGES)
    c = pd.read_csv(paths.RESIDENTS)
    c = c[c["year"] >= FIRST].reset_index(drop=True)
    shares = c[bands].astype(float).div(c["total"], axis=0) * 100

    fig, ax = charts.figure(profile)
    stacked = charts.series(shares, style.RESIDENT_AGES)
    charts.stacked_bars(ax, c["year"], stacked)
    charts.shares(ax)
    charts.years(ax, FIRST, 2020)

    charts.legend(fig, stacked)
    paths.save(fig, "residents_by_age", profile)
