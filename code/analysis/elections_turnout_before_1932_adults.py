"""Votes cast per 100 residents of voting age, 1880-1928 -> figures/elections_turnout_before_1932_adults.pdf, .png

elections_turnout_before_1932 with the denominator switched from every
resident to the residents who could vote: the men aged 21 and over through
1916, and all residents 21 and over from 1920, when women vote (the 1920
election counts them). Each is the census count interpolated in a straight
line between censuses (1880, 1910, 1920 and 1930 for the county; 1900 is not
counted whole). The elections before 1880 are not drawn: no census before 1880
counts adults, and holding 1880's count back would invent the denominator.
Everything else is as the all-residents figure: the same three rules, the
same open marker for 1920's count, which is O'Leary's, the same Board squares.
"""
import numpy as np

import charts
import paths
import style

FIRST, LAST = 1880, 1928
WOMEN_VOTE = 1920


def per_100(votes, adults):
    """Votes per 100 residents of voting age: men through 1916, everyone from
    1920, the count interpolated between the censuses either side."""
    county = adults[adults.district == "county"].set_index("year")
    men, everyone = county.men_all.dropna(), county.adults_all.dropna()
    eligible = np.where(votes.index < WOMEN_VOTE,
                        np.interp(votes.index, men.index, men.to_numpy()),
                        np.interp(votes.index, everyone.index, everyone.to_numpy()))
    return votes / eligible * 100


for profile in style.PROFILES:
    style.apply(profile)

    adults = paths.read("residents_by_district_adults")
    president = paths.read("elections_results")
    president = president[(president.office == "president")
                          & president.year.between(FIRST, LAST)].set_index("year")
    rate = per_100(president.total, adults)
    oleary = president.source.str.startswith("oleary")

    board = paths.read("elections_margins")
    board = board[board.contest.str.endswith("District") & board.votes_cast.notna()
                  & board.year.between(FIRST, LAST)]
    seats = board.groupby("year").contest.nunique()
    votes = board[board.year.isin(seats[seats == 3].index)].groupby("year").votes_cast.sum()
    board_rate = per_100(votes, adults)

    fig, ax = charts.figure(profile)
    label, colour = style.PRESIDENT
    charts.lines(ax, president.index.to_numpy(), {label: (rate.to_numpy(), colour)})
    olabel, _ = style.PRESIDENT_OLEARY
    charts.marks(ax, rate.index[oleary], rate[oleary], colour, filled=False)
    label, colour = style.BOARD_VOTE_DISTRICTS
    charts.marks(ax, board_rate.index, board_rate, colour, marker="s")

    charts.counts(ax, 80, 10, label="votes per 100 residents of voting age")
    charts.years(ax, 1870, 1930, step=10, label="year", minor=5)
    for year, note, ha in style.ELECTORATE_RULES_TO_1932:
        charts.rule(ax, year, note, ha=ha)
    charts.legend(fig, dict([style.PRESIDENT, style.PRESIDENT_OLEARY, style.BOARD_VOTE_DISTRICTS]),
                  hollow=[olabel])
    paths.save(fig, profile)
