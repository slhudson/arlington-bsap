"""Share of Arlington's vote for County Board, by party, 1931-2025 -> figures/voters_board.pdf, .png

A stacked step area of each band's share of the year's vote, in
style.BOARD_VOTE, on the same axis and in the same colours as
voters_president. Years the build marks incomplete are gaps. A band with
no votes in any year gets no band and no legend entry.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.VOTERS)
    d = d[d.office == "county board"].sort_values("year")
    held = [g for g in style.BOARD_VOTE if d[g].sum() > 0]
    assert held, "no County Board vote is attributed to any band - check the build"
    share = d[held].where(d.complete).div(d.total, axis=0) * 100
    spans = charts.runs(d.complete.to_numpy())
    series = charts.series(share.fillna(0), style.BOARD_VOTE, held)

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.shares(ax, label="share of the vote for County Board")
    charts.years(ax, 1870, 2020, step=20, label="year", through=2027)
    charts.legend(fig, series)
    paths.save(fig, "voters_board", profile)
