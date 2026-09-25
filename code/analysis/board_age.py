"""Ages of the sitting Board, 1932-2026 -> figures/board_age.pdf, .png

Three lines over the years: the oldest, the median and the youngest member
sitting on 1 July, in whole years from a birth year, with the 1932 rule.
A year is drawn when all but at most one of the members sitting that year
have a birth year; other years are gaps. docs/figures.md says why the
lines start in 1932.
"""
import numpy as np
import pandas as pd

import charts
import members
import paths
import style

FIRST, LAST = 1932, members.LAST
MISSING_ALLOWED = 1


def ages_by_year():
    """One row per year: youngest, median and oldest age of the members
    sitting, NaN where too few have a birth year."""
    rows = []
    for year, s in members.by_year(FIRST, LAST):
        ages = (year - s.birth_year.dropna()).to_numpy()
        drawn = len(ages) and len(s) - len(ages) <= MISSING_ALLOWED
        rows.append({"year": year,
                     "youngest": ages.min() if drawn else np.nan,
                     "median": np.median(ages) if drawn else np.nan,
                     "oldest": ages.max() if drawn else np.nan})
    out = pd.DataFrame(rows)
    if out.oldest.notna().sum() == 0:
        raise ValueError("no year has enough birth years to draw; nothing to draw")
    return out


for profile in style.PROFILES:
    style.apply(profile)
    d = ages_by_year()
    series = charts.series(d, style.AGES)

    fig, ax = charts.figure(profile)
    charts.lines(ax, d.year.to_numpy(), series, marker=False)
    charts.ages(ax, 20, 80)
    charts.years(ax, 1930, 2020, step=20, label="year", through=LAST + 1)
    charts.rule(ax)
    last = d[d.oldest.notna()].iloc[-1]
    for key, where in (("oldest", "above"), ("median", "above"), ("youngest", "below")):
        label, color = style.AGES[key]
        charts.end_label(ax, last.year, last[key], label, color, where=where)
    paths.save(fig, "board_age", profile)
