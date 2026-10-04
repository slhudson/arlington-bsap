"""Votes cast for each district's Board seat per 100 men of voting age, 1893-1919 -> figures/elections_turnout_by_district.pdf, .png

One line per magisterial district: the votes cast in its contest for the
Board, over the men aged 21 and over the nearest census counted in that
district (residents_by_district_adults.csv), a year equally far from two
censuses taking the earlier. The Board is elected in odd years, so the
x axis is every odd year from 1893 and a year with no count recovered for a
district breaks its line, a dotted segment crossing the gap.

Two things a reader of the figure needs, and the caption carries:

- 1893 to 1901 rest on the Alexandria Gazette's OCR text, whose digits
  misread elsewhere on the same pages (tracker row margins-gazette-ocr), so
  those points are provisional. Arlington District's denominator through
  1905 is the 1900 count, which is short of the district by one resident in
  six, so its 1893 to 1901 rates are upper bounds.
- The denominators are the nearest census, not the year's own population.
  Washington District's 1915 point reads near 100 because the district
  doubled between the 1910 count it is divided by and the 1920 one.

The two rules are the Walton Act of 1894 and the constitution of 1902.
"""
import numpy as np
import pandas as pd

import charts
import paths
import style

CENSUSES = (1880, 1900, 1910, 1920)
ELECTIONS = range(1893, 1920, 2)


def nearest(year):
    """The census closest to `year`, the earlier where two are as close."""
    return min(CENSUSES, key=lambda c: (abs(c - year), c))


for profile in style.PROFILES:
    style.apply(profile)

    adults = paths.read("residents_by_district_adults").set_index(["district", "year"]).men_all
    contests = paths.read("elections_margins")
    contests = contests[contests.contest.str.endswith("District") & contests.votes_cast.notna()
                        & contests.year.between(1893, 1919)]

    fig, ax = charts.figure(profile)
    for district, (label, colour) in style.DISTRICTS.items():
        votes = contests[contests.contest == f"{district} District"].set_index("year").votes_cast
        rate = pd.Series({y: votes.get(y, np.nan) / adults[(district, nearest(y))] * 100
                          for y in ELECTIONS})
        charts.lines(ax, rate.index.to_numpy(), {label: (rate.to_numpy(), colour)}, bridge=True)

    charts.counts(ax, 120, 20, label="votes per 100 men of voting age")
    charts.years(ax, 1890, 1920, step=10, label="year", minor=5)
    for year, note, ha in style.ELECTORATE_RULES:
        charts.rule(ax, year, note, ha=ha)
    charts.legend(fig, {label: colour for label, colour in style.DISTRICTS.values()})
    paths.save(fig, profile)
