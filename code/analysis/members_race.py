"""Board seats by race/ethnicity, 1870-2026 -> figures/members_race.pdf, .png

A stacked step area of seat-years in style.RACE, on the same frame
as members_gender, with the 1932 rule. Blank years are gaps. A category with
no seat in any year gets no band and no legend entry.
"""
import pandas as pd

import charts
import members
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.MEMBERS_BY_YEAR)
    spans = charts.runs(d["white"].notna().to_numpy())
    held = [g for g in style.RACE if d[g].fillna(0).sum() > 0]
    assert held, "no seat is attributed to any race category - check the build"
    series = charts.series(d.fillna(0), style.RACE, held)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, 1870, 2020, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax)
    charts.legend(fig, series)
    paths.save(fig, "members_race", profile)
