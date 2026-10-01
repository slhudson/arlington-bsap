"""Who votes for the County Board, by what else is on the ballot -> figures/elections_turnout.pdf, .png

Two panels with the same lines: (a) people, (b) shares of the adult
population. The presidential vote is one line with a marker per election;
the Board's voters are four lines, one per place in the four-year cycle.
Years the build marks incomplete are gaps. (b) starts where its
denominator does. One legend for both.
"""

import charts
import paths
import style

for profile in style.PROFILES:
    style.apply(profile)

    d = paths.read("elections_turnout")
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
        label, colour = style.PRESIDENT
        charts.lines(ax, president.year, {label: (president[col], colour)})
        for cycle, (label, colour) in style.CYCLE.items():
            part = board[board.cycle == cycle]
            charts.lines(ax, part.year, {label: (part[col], colour)})

    charts.counts(a, 150000, 50000, label="people", minor=25000)
    a.set_title("(a) people")
    charts.shares(b, label="share of adults")
    b.set_title("(b) share of adults")
    charts.years(a, 1930, 2020, step=20, label="November election", through=2028)
    charts.years(b, 1930, 2020, step=20, label="November election", through=2028)

    charts.legend(fig, dict([style.PRESIDENT, *style.CYCLE.values()]), ncol=3)
    paths.save(fig, profile)
