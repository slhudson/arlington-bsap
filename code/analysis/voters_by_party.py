"""Share of Arlington's presidential vote by party, 1872-2024 -> figures/voters_by_party.pdf, .png

The counterpart to board_party: the same colours, the same three bands from
the axis upward - Democratic, other, Republican - so the two read against
each other. Stacked bars rather than steps because an election is a point in
time; a step would claim the share held for four years.

"Share of voters" and not of residents: Virginia has no party registration,
the presidential vote is the proxy, and it counts the people who voted, in
an electorate that before 1966 was narrowed by the poll tax. Q30 in
docs/questions.md.

Three elections are missing from the figure by the build's decision: 1896,
1904 and 1908, whose returns are incomplete on the page. A gap says so;
a bar would not.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.VOTERS)
    d = d[d.complete]
    share = d[["dem", "other", "rep"]].div(d.total, axis=0) * 100
    series = {style.VOTERS_LABELS[g]: (share[g].to_numpy(), style.VOTERS_COLORS[g])
              for g in style.VOTERS_ORDER}

    fig, ax = charts.figure(style.SERIES, profile)
    charts.stacked_bars(ax, d["year"].to_numpy(), series, width=3)
    charts.shares(ax, label="share of voters")
    charts.years(ax, 1870, 2020, step=20, label="presidential election")
    ax.set_xlim(1866, 2027)
    charts.legend(fig, {style.VOTERS_LABELS[g]: style.VOTERS_COLORS[g] for g in style.VOTERS_ORDER})
    paths.save(fig, "voters_by_party", profile)
