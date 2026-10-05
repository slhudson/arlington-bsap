"""The electorate before 1932: who could vote, as a denominator. A module,
not a step: the two turnout figures and body_text_numbers read it, so the
rate a figure draws and the rate the prose cites are one arithmetic.

Two denominators, because the two figures answer different questions:

- ``per_100_adults`` is the county series, votes per 100 residents of voting
  age: the men aged 21 and over through 1916, and all residents 21 and over
  from 1920, when women vote (the 1920 election counts them), each interpolated
  in a straight line between the censuses either side of the year.
- ``per_100_district_men`` is a district's Board contest over the men aged 21
  and over the nearest census counted in that district, a year equally far
  from two censuses taking the earlier. The districts are counted whole at
  four censuses only, and interpolating between them would draw a line
  through years nothing records.
"""
import numpy as np

WOMEN_VOTE = 1920
CENSUSES = (1880, 1900, 1910, 1920)   # the censuses that count the districts' men


def per_100_adults(votes, adults):
    """Votes per 100 residents of voting age in the county: men through 1916,
    everyone from 1920, the count interpolated between the censuses either
    side. `votes` is a Series indexed by year; `adults` is
    residents_by_district_adults."""
    county = adults[adults.district == "county"].set_index("year")
    men, everyone = county.men_all.dropna(), county.adults_all.dropna()
    eligible = np.where(votes.index < WOMEN_VOTE,
                        np.interp(votes.index, men.index, men.to_numpy()),
                        np.interp(votes.index, everyone.index, everyone.to_numpy()))
    return votes / eligible * 100


def nearest(year):
    """The census closest to `year`, the earlier where two are as close."""
    return min(CENSUSES, key=lambda c: (abs(c - year), c))


def per_100_district_men(votes, district, adults):
    """Votes cast in `district`'s Board contests per 100 men of voting age the
    nearest census counted there. `votes` is a Series indexed by year."""
    men = adults.set_index(["district", "year"]).men_all
    return votes / np.array([men[(district, nearest(y))] for y in votes.index]) * 100
