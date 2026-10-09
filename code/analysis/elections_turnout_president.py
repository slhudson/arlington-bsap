"""Votes for President per 100 residents of voting age, 1872 to the present
-> figures/elections_turnout_president.pdf, .png

One grey line, with a line for the district-era Board elections whose
three districts were all contested, with the Walton Act of 1894, the constitution of 1902 and
women voting in 1920 ruled off. Read by Race's "A Shrinking Electorate,"
whose point is the collapse after 1894 and 1902 and the long recovery. The
denominator is code/analysis/elections.py's, which body_text_numbers reads
too, so the prose cites the rate this figure draws.
"""
import charts
import paths
import style
from elections import per_100_voting_age

for profile in style.PROFILES:
    style.apply(profile)

    adults = paths.read("residents_by_district_adults")
    d = paths.read("elections_turnout")
    estimate = d.set_index("year").voting_age_est

    president = d.dropna(subset=["president_votes"]).set_index("year").president_votes
    president_rate = per_100_voting_age(president, adults, estimate)

    fig, ax = charts.figure(profile)
    label, colour = style.PRESIDENT
    charts.lines(ax, president_rate.index.to_numpy(), {label: (president_rate.to_numpy(), colour)})

    # Every district-era election the roster names, so a line is solid between
    # consecutive elections both drawn and dotted across one that is not.
    roster = paths.read("members")
    held = roster[(roster.district != "at large") & (roster.start_year < style.EXPANSION_YEAR)]
    elections_held = sorted(held.election_year.dropna().astype(int).unique())
    district_era = d[d.year < 1931].dropna(subset=["board_voters"]).set_index("year").board_voters
    board_rate = per_100_voting_age(district_era, adults, estimate).reindex(elections_held)
    board_label, board_colour = style.BOARD_DISTRICTS
    charts.lines(ax, board_rate.index.to_numpy(), {board_label: (board_rate.to_numpy(), board_colour)},
                 bridge=True)

    charts.counts(ax, 100, 10, label="votes per 100 residents of voting age")
    charts.years(ax, 1870, 2020, step=20, label="year", minor=10, through=2028)
    for year, note, ha, tier in style.ELECTORATE_RULES:
        charts.rule(ax, year, note, ha=ha, tier=tier)

    charts.legend(fig, {label: colour, board_label: board_colour},
                  lines=[label, board_label])
    paths.save(fig, profile)
