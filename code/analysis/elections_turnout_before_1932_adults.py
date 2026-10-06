"""Votes cast per 100 residents of voting age, 1872-1928 -> figures/elections_turnout_before_1932_adults.pdf, .png

elections_turnout_before_1932 with the denominator switched from every
resident to the residents who could vote: the men aged 21 and over through
1916, and all residents 21 and over from 1920, when women vote (the 1920
election counts them). Each is the census count interpolated in a straight
line between censuses, and every census from 1870 to 1930 is a count for the
county: the schedules' at 1880, 1910 and 1920, the volumes' printed counts
at 1870, 1890, 1900 and 1930 (residents_by_district_adults). Everything else is as the all-residents figure: the same three rules, the
same Board squares. The denominator is code/analysis/elections.py's, which
body_text_numbers reads too, so the prose cites the rates this figure draws.
"""
import charts
import paths
import style
from elections import per_100_adults as per_100

FIRST, LAST = 1872, 1928


for profile in style.PROFILES:
    style.apply(profile)

    adults = paths.read("residents_by_district_adults")
    president = paths.read("elections_results")
    president = president[(president.office == "president")
                          & president.year.between(FIRST, LAST)].set_index("year")
    rate = per_100(president.total, adults)

    board = paths.read("elections_margins")
    board = board[board.contest.str.endswith("District") & board.votes_cast.notna()
                  & board.year.between(FIRST, LAST)]
    seats = board.groupby("year").contest.nunique()
    votes = board[board.year.isin(seats[seats == 3].index)].groupby("year").votes_cast.sum()
    board_rate = per_100(votes, adults)

    fig, ax = charts.figure(profile)
    label, colour = style.PRESIDENT
    charts.lines(ax, president.index.to_numpy(), {label: (rate.to_numpy(), colour)})
    label, colour = style.BOARD_VOTE_DISTRICTS
    charts.marks(ax, board_rate.index, board_rate, colour, marker="s")

    charts.counts(ax, 100, 10, label="votes per 100 residents of voting age")
    charts.years(ax, 1870, 1930, step=10, label="year", minor=5)
    for year, note, ha in style.ELECTORATE_RULES_TO_1932:
        charts.rule(ax, year, note, ha=ha)
    board_label = f"{label} ({', '.join(str(y) for y in board_rate.index)})"
    charts.legend(fig, dict([style.PRESIDENT, (board_label, colour)]))
    paths.save(fig, profile)
