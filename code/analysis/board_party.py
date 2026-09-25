"""Board seats by party, 1932-2026 -> figures/board_party.pdf, .png

A stacked step area of seat-years in style.PARTY, on the same frame
as board_race and board_gender, with the 1932 rule. Blank years are gaps.
A category with no seat in any year gets no band and no legend entry.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.BOARD_SEATS)
    spans = charts.runs(d["dem"].notna().to_numpy())
    held = [g for g in style.PARTY if d[g].fillna(0).sum() > 0]
    assert held, "no seat is attributed to any party category - check the build"
    series = charts.series(d.fillna(0), style.PARTY, held)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.seats(ax)
    charts.years(ax, 1870, 2020, step=20, label="year", through=2027)
    charts.rule(ax, note=style.EXPANSION_NOTE_SEATS)
    charts.legend(fig, series)
    paths.save(fig, "board_party", profile)
