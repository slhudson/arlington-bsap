"""Residents by race/ethnicity, 1870-2020 -> figures/residents_by_race.pdf, .png

Two panels. (a) Counts, one line per group with a marker per census; White
is clipped at TOP and marked where it leaves the axis. (b) Shares, as
stacked bars, the residual between the counted groups and White. One
legend for both. Both draw from style.RESIDENTS_CROSSED, so Black and White
read "not Hispanic"; that is true only from style.CROSSED_YEAR, before which
the census asked no Hispanic-origin question, so a dashed rule marks the year
the definition changes.
"""
import numpy as np

import charts
import paths
import style

TOP = 50000          # top of the counts axis; White is clipped above it

for profile in style.PROFILES:
    style.apply(profile)

    c = paths.read("residents")
    groups = list(style.RACE)

    # A blank stays blank, so a line begins where the column does.
    counts = c[groups].astype(float)
    counts["other"] = (c["total"] - c[groups].sum(axis=1)).clip(lower=0).replace(0, np.nan)

    shares = counts[groups].div(c["total"], axis=0) * 100
    shares["other"] = (100 - shares.fillna(0).sum(axis=1)).clip(lower=0)
    shares = shares.fillna(0)

    fig, (a, b) = charts.panels(profile)

    # (a) White is drawn last, in the darker stroke, clipped at TOP.
    lines = charts.series(counts, style.RESIDENTS_CROSSED)
    lines[style.RESIDENTS_CROSSED["white"][0]] = (counts["white"], style.SAND_LINE)
    charts.lines(a, c["year"], lines)
    charts.counts(a, TOP, 5000)
    charts.years(a, 1870, 2020, step=40)
    charts.off_scale(a, c["year"], counts["white"], style.SAND_LINE, TOP)
    charts.rule(a, style.CROSSED_YEAR, note=None)
    a.set_title("(a) number of residents")

    stacked = charts.series(shares, style.RESIDENTS_CROSSED)
    charts.stacked_bars(b, c["year"], stacked)
    charts.shares(b)
    charts.years(b, 1870, 2020, step=40)
    charts.rule(b, style.CROSSED_YEAR, note=None)
    b.set_title("(b) share of residents")

    charts.legend(fig, stacked, ncol=3)
    paths.save(fig, profile)
