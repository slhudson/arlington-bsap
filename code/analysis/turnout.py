"""Who votes for the County Board, by what else is on the ballot -> figures/turnout.pdf, .png

Two panels with the same lines: (a) people, (b) shares of the adult
population. The presidential vote is one line with a marker per election;
the Board's voters are four lines, one per place in the four-year cycle.
Years the build marks incomplete are gaps. (b) starts where its
denominator does. One legend for both.
"""
import pandas as pd

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = pd.read_csv(paths.TURNOUT)
    d = d[d.year >= 1930]
    adults = d.set_index("year").voting_age_est

    board = d.dropna(subset=["board_voters"]).copy()
    board["people"] = board.board_voters.where(board.board_complete)   # incomplete: a gap
    board["share"] = board.people / adults.loc[board.year].to_numpy() * 100
    president = d.dropna(subset=["president_votes"]).copy()
    president["people"] = president.president_votes
    president["share"] = president.people / adults.loc[president.year].to_numpy() * 100

    fig, (a, b) = charts.panels(profile)
    for ax, col in ((a, "people"), (b, "share")):
        charts.lines(ax, president.year, {"voted for President":
                     (president[col], style.TURNOUT_COLORS["president"])})
        for cycle in style.CYCLE_ORDER:
            part = board[board.cycle == cycle]
            charts.lines(ax, part.year, {style.CYCLE_LABELS[cycle]:
                         (part[col], style.CYCLE_COLORS[cycle])}, marker=False)

    charts.counts(a, 150000, 50000, label="people", minor=25000)
    a.set_title("(a) people")
    charts.shares(b, label="share of adults")
    b.set_title("(b) share of adults")
    charts.years(a, 1930, 2020, step=20, label="November election", through=2028)
    charts.years(b, 1980, 2020, step=20, label="November election", through=2028)

    entries = {"voted for President": style.TURNOUT_COLORS["president"]}
    entries.update({style.CYCLE_LABELS[c]: style.CYCLE_COLORS[c] for c in style.CYCLE_ORDER})
    charts.legend(fig, entries, ncol=3)
    paths.save(fig, "turnout", profile)
