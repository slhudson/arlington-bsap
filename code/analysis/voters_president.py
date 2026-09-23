"""Share of Arlington's vote for President, by party, 1872-2024 -> figures/voters_president.pdf, .png

The county's partisanship as its whole electorate expresses it, every fourth
year. voters_board is its counterpart, the same axis and colours, for the
smaller November electorate that chooses the Board; the two are kept as
separate figures, as board_race and board_gender are, because they are not
the same voters and should not be read as one series.

Stacked bars because a presidential election is a point in time; a step
would claim the share held for four years. Three elections are missing by
the build's decision - 1896, 1904 and 1908, whose returns are incomplete on
O'Leary's page - and a gap says so where a short bar would not.

"Share of voters" rather than of residents: Virginia has no party
registration, so the vote is the proxy, and before 1966 the electorate was
the one the poll tax allowed. Q30 in docs/questions.md.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.VOTERS)
    d = d[(d.office == "president") & d.complete]
    share = d[style.VOTERS_ORDER].div(d.total, axis=0) * 100
    series = {style.VOTERS_LABELS[g]: (share[g].to_numpy(), style.VOTERS_COLORS[g])
              for g in style.VOTERS_ORDER}

    fig, ax = charts.figure(style.SERIES, profile)
    charts.stacked_bars(ax, d["year"].to_numpy(), series, width=3)
    charts.shares(ax, label="share of the vote for President")
    charts.years(ax, 1870, 2020, step=20, label="presidential election")
    ax.set_xlim(1866, 2027)
    charts.legend(fig, {style.VOTERS_LABELS[g]: style.VOTERS_COLORS[g] for g in style.VOTERS_ORDER})
    paths.save(fig, "voters_president", profile)
