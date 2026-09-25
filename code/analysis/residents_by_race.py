"""Residents by race/ethnicity, 1870-2020 -> figures/residents_by_race.pdf, .png

Two panels. (a) Counts, one line per group with a marker per census; White
is clipped at TOP and marked where it leaves the axis. (b) Shares, as
stacked bars in style.GROUP_ORDER with the residual between the counted
groups and White. One legend for both.
"""
import numpy as np
import pandas as pd

import charts
import paths
import style

TOP = 50000          # top of the counts axis; White is clipped above it

for profile in style.PROFILES:
    style.apply(profile)

    c = pd.read_csv(paths.RESIDENTS)
    groups = style.GROUP_ORDER                                 # black, hisp, aapi, white

    # A blank stays blank, so a line begins where the column does.
    counts = c[groups].astype(float)
    residual = (c["total"] - c[groups].sum(axis=1)).clip(lower=0)

    shares = counts.div(c["total"], axis=0) * 100
    residual_share = (100 - shares.fillna(0).sum(axis=1)).clip(lower=0)
    shares = shares.fillna(0)

    def bands(frame, resid):
        out = {style.GROUP_LABELS[g]: (frame[g].to_numpy(), style.RACE_COLORS[g])
               for g in ("black", "hisp", "aapi")}
        out[style.OTHER_LABEL] = (np.asarray(resid), style.RESIDUAL_COLOR)
        out[style.GROUP_LABELS["white"]] = (frame["white"].to_numpy(),
                                            style.RACE_COLORS["white"])
        return out

    fig, (a, b) = charts.panels(profile)

    # (a) White is drawn last, in the darker stroke, clipped at TOP.
    lines = {style.GROUP_LABELS[g]: (counts[g], style.RACE_COLORS[g])
             for g in ("black", "hisp", "aapi")}
    lines[style.OTHER_LABEL] = (residual.replace(0, np.nan), style.RESIDUAL_COLOR)
    lines[style.GROUP_LABELS["white"]] = (counts["white"], style.SAND_LINE)
    charts.lines(a, c["year"], lines)
    charts.counts(a, TOP, 5000)
    charts.years(a, 1870, 2020, step=20)
    charts.off_scale(a, c["year"], counts["white"], style.SAND_LINE, TOP)
    a.set_title("(a) number of residents")

    stacked = bands(shares, residual_share)
    charts.stacked_bars(b, c["year"], stacked)
    charts.shares(b)
    charts.years(b, 1870, 2020, step=20)
    b.set_title("(b) share of residents")

    charts.legend(fig, stacked, ncol=3)
    paths.save(fig, "residents_by_race", profile)
