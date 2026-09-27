"""Share of Arlington's vote for President, by party, 1872-2024 -> figures/elections_president.pdf, .png

Stacked bars of each band's share of the vote, one per election, in
style.ELECTIONS_RESULTS. Years the build marks incomplete are left out.
"""
import pandas as pd

import charts
import members
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.ELECTIONS_RESULTS)
    d = d[(d.office == "president") & d.complete]
    share = d[list(style.ELECTIONS_RESULTS)].div(d.total, axis=0) * 100
    series = charts.series(share, style.ELECTIONS_RESULTS)

    fig, ax = charts.figure(profile)
    charts.stacked_bars(ax, d["year"].to_numpy(), series, width=3)
    charts.shares(ax, label="share of the vote for President")
    charts.years(ax, 1870, 2020, step=20, label="presidential election", through=members.LAST + 1)
    charts.legend(fig, series)
    paths.save(fig, "elections_president", profile)
