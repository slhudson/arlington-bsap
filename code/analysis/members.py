"""Who sits on the Board in a given year. A module, not a step: the age
figures read it so they agree on what "sitting" means.

A member sits in a year if a term holds 1 July of it, by the months
board_members.csv says the term held. docs/figures.md says why 1 July.
"""
import pandas as pd

import paths

FIRST, LAST = 1870, 2026


def sitting(members, year):
    """The members holding a seat on 1 July of `year`, one row each."""
    july = year * 12 + 6
    return members[(members.held_from <= july) & (july < members.held_to)].drop_duplicates("name")


def by_year(first=FIRST, last=LAST):
    """(year, the members sitting) for every year first..last."""
    d = pd.read_csv(paths.BOARD_MEMBERS)
    return [(year, sitting(d, year)) for year in range(first, last + 1)]
