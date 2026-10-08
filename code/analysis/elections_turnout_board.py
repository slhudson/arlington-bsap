"""County Board votes per 100 residents of voting age against the
presidential vote, 1932 to the present -> figures/elections_turnout_board.pdf, .png

One panel. The presidential vote is one grey line throughout. The Board's
vote is one colour family, shaded by what led the November ballot
(presidential, midterm or governor's year): a line for each cycle in a
one-seat year, named in the legend by what it is rather than grouped under a
heading. A year that filled more than one seat, or that the build marks
incomplete, is a gap: its votes are not its voters, and that takes every
House of Delegates year from 1943. A dashed rule marks 1940, the first
staggered election; no Board line starts before it, and the axis reads from
1930 so that empty decade is a known fact rather than a blank. Read by
Election Method's
"Staggered Terms," whose point is that seats elected a year apart are chosen
by electorates of different size. The denominator is
code/analysis/elections.py's, which body_text_numbers reads too, so the
prose cites the rate this figure draws.
"""
import charts
import paths
import style
from elections import per_100_voting_age

FIRST_ONE_SEAT = 1935
FIRST_YEAR = 1932
AXIS_FIRST = 1930   # the data start at 1932; the axis reads from the decade before


for profile in style.PROFILES:
    style.apply(profile)

    adults = paths.read("residents_by_district_adults")
    d = paths.read("elections_turnout")
    estimate = d.set_index("year").voting_age_est

    president = d.dropna(subset=["president_votes"]).set_index("year").president_votes
    president = president[president.index >= FIRST_YEAR]
    president_rate = per_100_voting_age(president, adults, estimate)

    one_seat = d[(d.year >= FIRST_ONE_SEAT) & (d.board_seats == 1) & d.board_complete.eq(True)
                 ].set_index("year")
    board_rate = per_100_voting_age(one_seat.board_voters, adults, estimate)

    fig, ax = charts.figure(profile)
    label, colour = style.PRESIDENT
    charts.lines(ax, president_rate.index.to_numpy(), {label: (president_rate.to_numpy(), colour)})
    for name in ("president", "midterm", "governor"):
        years_of = d[d.cycle == name].year[lambda y: y >= FIRST_ONE_SEAT].to_numpy()
        rate = board_rate.reindex(years_of)       # a two-seat year is NaN: a gap
        charts.lines(ax, years_of, {name: (rate.to_numpy(), style.BOARD_FAMILY[name])}, bridge=True)

    charts.counts(ax, 100, 10, label="votes per 100 residents of voting age")
    charts.years(ax, AXIS_FIRST, 2020, step=10, label="year", minor=None, through=2028)
    charts.rule(ax, 1940, "1940: staggered terms begin", ha="left", tier=0)

    board_labels = {key: f"Board, {name}" for key, name in style.BOARD_CYCLES.items()
                    if key != "delegates"}
    entries = {style.PRESIDENT[0]: style.PRESIDENT[1]}
    entries.update({name: style.BOARD_FAMILY[key] for key, name in board_labels.items()})
    charts.legend(fig, entries, lines=list(entries))
    paths.save(fig, profile)
