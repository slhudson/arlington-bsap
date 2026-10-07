"""Votes for President per 100 residents of voting age, 1872 to the present
-> figures/elections_turnout_president.pdf, .png

One grey line, with the Walton Act of 1894, the constitution of 1902 and
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

    charts.counts(ax, 100, 10, label="votes per 100 residents of voting age")
    charts.years(ax, 1870, 2020, step=20, label="year", minor=10, through=2028)
    for year, note, ha, tier in style.ELECTORATE_RULES:
        charts.rule(ax, year, note, ha=ha, tier=tier)

    paths.save(fig, profile)
