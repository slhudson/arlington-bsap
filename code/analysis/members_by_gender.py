"""Board seats by gender, 1870-2026 -> figures/members_by_gender.pdf, .png

A stacked step area of seat-years, women then men, with the 1932 rule.
Blank years are gaps.
"""
import pandas as pd

import charts
import members
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.MEMBERS_BY_YEAR)
    spans = charts.runs(d["women"].notna().to_numpy())
    series = charts.series(d.fillna(0), style.GENDER)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, 1870, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax)
    charts.legend(fig, series)
    paths.save(fig, "members_by_gender", profile)
