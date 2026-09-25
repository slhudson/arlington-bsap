"""Board seats by gender, 1870-2026 -> figures/board_gender.pdf, .png

A stacked step area of seat-years, women then men, with the 1932 rule.
Blank years are gaps.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.BOARD_SEATS)
    spans = charts.runs(d["women"].notna().to_numpy())
    series = {style.GENDER_LABELS[g]: (d[g].fillna(0).to_numpy(), style.GENDER_COLORS[g])
              for g in style.GENDER_ORDER}

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, 1870, 2020, step=20, label="year", through=2027)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS)
    charts.legend(fig, series)
    paths.save(fig, "board_gender", profile)
