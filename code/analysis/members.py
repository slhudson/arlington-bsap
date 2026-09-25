"""Who sits on the Board in a given year. A module, not a step: the two
age figures read it so they agree on what "sitting" means.

A member sits in a year if a term holds 1 July of it. A term's end is
exclusive, in months, as the seat-year table counts it, and the handover
month belongs to the incoming member; an unrecorded end holds to the end
of its first year. docs/figures.md says why 1 July.
"""
import pandas as pd

import paths

FIRST, LAST = 1870, 2026


def sitting(members, year):
    """The members holding a seat on 1 July of `year`, one row each."""
    start = members.start_year * 12 + members.start_month - 1
    stop = members.end_year.fillna(members.start_year) * 12 + members.end_month.fillna(12)
    starts = set(start)
    stop = pd.Series([s - 1 if (s - 1) in starts else s for s in stop], index=members.index)
    july = year * 12 + 6
    return members[(start <= july) & (july < stop)].drop_duplicates("name")


def by_year(first=FIRST, last=LAST):
    """(year, the members sitting) for every year first..last."""
    d = pd.read_csv(paths.BOARD_MEMBERS)
    return [(year, sitting(d, year)) for year in range(first, last + 1)]
