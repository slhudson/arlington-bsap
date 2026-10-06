"""Who could vote, as a denominator. A module, not a step: the turnout figure
and body_text_numbers read it, so the rate a figure draws and the rate the
prose cites are one arithmetic.

Three denominators, for three questions:

- ``per_100_voting_age`` is the whole series the turnout figure draws, 1872 to
  the present: ``per_100_adults`` to 1930 and the clean table's estimate after.

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
import pandas as pd

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


def per_100_voting_age(votes, adults, estimate):
    """Votes per 100 residents of voting age, 1872 to the present: through
    the census of 1930 as per_100_adults, and from 1930 the clean table's
    own estimate (men 21 and over, then everyone 21 and over, then 18 and over
    from 1971, a count at every census and a straight line between).
    `estimate` is elections_turnout's voting_age_est, a Series by year."""
    early = votes[votes.index < 1930]
    late = votes[votes.index >= 1930]
    return pd.concat([per_100_adults(early, adults),
                      late / estimate.loc[late.index] * 100])


CYCLE = {0: "president", 1: "governor", 2: "midterm", 3: "delegates"}


def cycle(year):
    """What led the November ballot: the four-year cycle that
    code/clean/elections_turnout.py gives each row from 1931, worked out the
    same way for the years before."""
    return CYCLE[year % 4]


def nearest(year):
    """The census closest to `year`, the earlier where two are as close."""
    return min(CENSUSES, key=lambda c: (abs(c - year), c))


def per_100_district_men(votes, district, adults):
    """Votes cast in `district`'s Board contests per 100 men of voting age the
    nearest census counted there. `votes` is a Series indexed by year."""
    men = adults.set_index(["district", "year"]).men_all
    return votes / np.array([men[(district, nearest(y))] for y in votes.index]) * 100
