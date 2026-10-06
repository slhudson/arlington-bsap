"""Votes cast per 100 residents of voting age, 1872 to the present -> figures/elections_turnout.pdf, .png

One panel. The presidential vote is one grey line throughout. The Board's
vote is one colour family, shaded by what led the November ballot
(presidential, midterm, governor's or House of Delegates year): a square for
each district-era election in which every district's count survives, and from
1935 a line for each cycle in a one-seat year. A year that filled more than
one seat, or that the build marks incomplete, is a gap: its votes are not its
voters, and that takes every House of Delegates year from 1943, so the
delegates shade appears only among the squares. The denominator is
code/analysis/elections.py's, which body_text_numbers reads too, so the prose
cites the rates this figure draws.
"""
import charts
import paths
import style
from elections import cycle, per_100_voting_age

FIRST_ONE_SEAT = 1935
LAST_DISTRICT_ERA = 1928


for profile in style.PROFILES:
    style.apply(profile)

    adults = paths.read("residents_by_district_adults")
    d = paths.read("elections_turnout")
    estimate = d.set_index("year").voting_age_est

    president = d.dropna(subset=["president_votes"]).set_index("year").president_votes
    president_rate = per_100_voting_age(president, adults, estimate)

    districts = paths.read("elections_margins")
    districts = districts[districts.contest.str.endswith("District") & districts.votes_cast.notna()
                          & (districts.year <= LAST_DISTRICT_ERA)]
    seats = districts.groupby("year").contest.nunique()
    votes = districts[districts.year.isin(seats[seats == 3].index)].groupby("year").votes_cast.sum()
    district_rate = per_100_voting_age(votes, adults, estimate)

    one_seat = d[(d.year >= FIRST_ONE_SEAT) & (d.board_seats == 1) & d.board_complete.eq(True)
                 ].set_index("year")
    board_rate = per_100_voting_age(one_seat.board_voters, adults, estimate)

    fig, ax = charts.figure(profile)
    label, colour = style.PRESIDENT
    charts.lines(ax, president_rate.index.to_numpy(), {label: (president_rate.to_numpy(), colour)})
    for year, rate in district_rate.items():
        charts.marks(ax, [year], [rate], style.BOARD_FAMILY[cycle(year)], marker="s")
    for name in ("president", "midterm", "governor"):
        years_of = d[d.cycle == name].year[lambda y: y >= FIRST_ONE_SEAT].to_numpy()
        rate = board_rate.reindex(years_of)       # a two-seat year is NaN: a gap
        charts.lines(ax, years_of, {name: (rate.to_numpy(), style.BOARD_FAMILY[name])})

    charts.counts(ax, 100, 10, label="votes per 100 residents of voting age")
    charts.years(ax, 1870, 2020, step=20, label="year", minor=10, through=2028)
    for year, note, ha, tier in style.ELECTORATE_RULES:
        charts.rule(ax, year, note, ha=ha, tier=tier)

    family = {name: (style.BOARD_FAMILY[key], "s" if key == "delegates" else "o", key != "delegates")
              for key, name in style.BOARD_CYCLES.items()}
    charts.legend_family(fig, {style.PRESIDENT[0]: (style.PRESIDENT[1], "o")},
                         style.BOARD_VOTES, family)
    paths.save(fig, profile)
