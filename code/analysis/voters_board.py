"""Share of Arlington's vote for County Board, by party, 1931-2025 -> figures/voters_board.pdf, .png

What the November electorate did with the candidates it was offered. The
counterpart to voters_president, on the same axis and in the same colours,
and to board_party, whose bands these are: reading the three together is the
point. A separate figure rather than a panel because these are not the same
voters as the presidential ones, and a shared frame would say they were.

A candidate is counted under the label the county's record prints after
their name, not under the party reporting later attached to the winners in
board_party. So 1967-83 is mostly grey here and Republican there,
deliberately: this figure is about the choice on the ballot, that one about
who sat. Candidates the county prints no label for are "not recorded".

A step area, because it is annual, with each year's value spanning the year.
Years the build marks incomplete - a winner with no vote count - are gaps.
Shares are of votes cast: in a two-seat year each ballot carries two, which
matters only where a party ran a short slate (Q30 in docs/questions.md).
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.VOTERS)
    d = d[d.office == "county board"].sort_values("year")
    held = [g for g in style.BOARD_VOTE_ORDER if d[g].sum() > 0]
    assert held, "no County Board vote is attributed to any band - check the build"
    share = d[held].where(d.complete).div(d.total, axis=0) * 100
    spans = charts.runs(d.complete.to_numpy())
    series = {style.BOARD_VOTE_LABELS[g]: (share[g].fillna(0).to_numpy(), style.BOARD_VOTE_COLORS[g])
              for g in held}

    fig, ax = charts.figure(profile)
    charts.stacked_steps(ax, d["year"].to_numpy(), series, spans)
    charts.shares(ax, label="share of the vote for County Board")
    charts.years(ax, 1870, 2020, step=20, label="year")
    ax.set_xlim(1866, 2027)
    charts.legend(fig, {style.BOARD_VOTE_LABELS[g]: style.BOARD_VOTE_COLORS[g] for g in held})
    paths.save(fig, "voters_board", profile)
