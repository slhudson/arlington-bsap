"""Board seats by race/ethnicity, 1870-2026 -> figures/board_race.pdf, .png

A stacked step area of seat-years in style.GROUP_ORDER, on the same frame
as board_gender, with the 1932 rule. Blank years are gaps. A category with
no seat in any year gets no band and no legend entry.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.BOARD_SEATS)
    spans = charts.runs(d["white"].notna().to_numpy())
    held = [g for g in style.GROUP_ORDER if d[g].fillna(0).sum() > 0]
    assert held, "no seat is attributed to any race category - check the build"
    series = {style.GROUP_LABELS[g]: (d[g].fillna(0).to_numpy(), style.RACE_COLORS[g])
              for g in held}

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, 1870, 2020, step=20, label="year", through=2027)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS)
    charts.legend(fig, series)
    paths.save(fig, "board_race", profile)
