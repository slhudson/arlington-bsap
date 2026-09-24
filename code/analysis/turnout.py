"""Who votes for the County Board, by what else is on the ballot -> figures/turnout.pdf, .png

Two panels, the same lines in each: (a) people, (b) the same as shares of
the county's adults, from 1980, the first census whose count of those 18
and over the build holds.

The Board's voters are split into four series by the year's place in the
four-year cycle - what else the November ballot carried: the President,
the governor, Congress alone, or the House of Delegates alone. Drawn as one
annual line the series is a sawtooth, and the teeth are the ballot, not the
Board; drawn as four, each every fourth year, the teeth become four levels
and the trend in each is visible. The presidential vote itself is the grey
reference: the gap between it and the presidential-year Board line is the
roll-off within one ballot.

The Board lines are votes per seat filled, from data/clean/turnout.csv,
which says why: exact for one seat, a lower bound for two or more. Since
1951 every two-seat year has been a House of Delegates year, so the
understatement lives in that one line, and the caption says so.

Years the build marks incomplete are gaps, not zeros: 1931 (others ran who
are not listed), 1942 and 1949 (no counts), 1947 (8 of 11 precincts). The
whole Board was elected at once in 1931, 1935 and 1939, all House of
Delegates years, so that line starts in 1935 and has nothing between. The
two district-era counts, 1907 and 1915, are in the table and not drawn.

Registered voters are in the table from 2010 and not drawn: a fifteen-year
line above everything else, for a denominator the prose can state in a
sentence. The denominator drawn is adults, carried between censuses on the
build's straight line (voting_age_est).
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
    # An incomplete year is a break in the line, which is what a gap should
    # look like; a zero would draw the drop the source does not report.
    board["people"] = board.board_voters.where(board.board_complete)
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

    # Twenty-year labels anchored on 2020, with an unlabelled tick each
    # decade between; both axes run to 2025 for the last Board election.
    # (b) starts where its denominator does, so its frame is not half empty.
    charts.years(a, 1930, 2020, step=20, label="November election")
    a.set_xlim(1927, 2028)
    charts.years(b, 1980, 2020, step=20, label="November election")
    b.set_xlim(1977, 2028)

    # One legend below both panels, in the order the lines stack: the
    # presidential vote on top, then the Board's voters from the top of the
    # ticket down. Five lines in two frames would be named ten times.
    entries = {"voted for President": style.TURNOUT_COLORS["president"]}
    entries.update({style.CYCLE_LABELS[c]: style.CYCLE_COLORS[c] for c in style.CYCLE_ORDER})
    charts.legend(fig, entries, ncol=3)

    paths.save(fig, "turnout", profile)
