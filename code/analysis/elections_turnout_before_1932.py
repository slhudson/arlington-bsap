"""Votes cast per 100 residents, 1872-1928 -> figures/elections_turnout_before_1932.pdf, .png

The presidential vote, 1872 to 1928, as O'Leary counts it, set against the
census population interpolated in a straight line between censuses. A year
whose count is complete is joined to the next complete year, with a dotted
segment across a year that is not; a year whose count is incomplete is an
open marker, since the votes it records are fewer than were cast. The Board's
vote is the three districts' counts added together, drawn only in the years
all three seats were held and counted: 1901, 1907 and 1915.

Two rules mark the dated changes to who could vote, the Walton Act of 1894
and the constitution of 1902. The denominator is all residents, not the men
who could vote: the men of voting age are counted at four censuses only, by
district, in residents_by_district_adults.csv, and the by-district figure
uses them.
"""
import numpy as np

import charts
import paths
import style

FIRST, LAST = 1872, 1928


def per_100(votes, residents):
    """Votes per 100 residents, the residents interpolated in a straight
    line between the two censuses either side of the year."""
    census = residents.set_index("year").total
    return votes / np.interp(votes.index, census.index, census.to_numpy()) * 100


for profile in style.PROFILES:
    style.apply(profile)

    president = paths.read("elections_results")
    president = president[(president.office == "president")
                          & president.year.between(FIRST, LAST)].set_index("year")
    rate = per_100(president.total, paths.read("residents"))
    complete = president.complete.astype(bool)

    board = paths.read("elections_margins")
    board = board[board.contest.str.endswith("District") & board.votes_cast.notna()
                  & board.year.between(FIRST, LAST)]
    seats = board.groupby("year").contest.nunique()
    votes = board[board.year.isin(seats[seats == 3].index)].groupby("year").votes_cast.sum()
    board_rate = per_100(votes, paths.read("residents"))

    fig, ax = charts.figure(profile)
    label, colour = style.PRESIDENT
    charts.lines(ax, president.index.to_numpy(), {label: (rate.where(complete).to_numpy(), colour)},
                 bridge=True)
    charts.marks(ax, president.index[~complete], rate[~complete], colour, filled=False)
    label, colour = style.BOARD_VOTE_DISTRICTS
    charts.marks(ax, board_rate.index, board_rate, colour, marker="s")

    charts.counts(ax, 25, 5, label="votes per 100 residents")
    charts.years(ax, 1870, 1930, step=10, label="year", minor=5)
    for year, note, ha in style.ELECTORATE_RULES:
        charts.rule(ax, year, note, ha=ha)
    charts.legend(fig, dict([style.PRESIDENT, style.BOARD_VOTE_DISTRICTS]))
    paths.save(fig, profile)
