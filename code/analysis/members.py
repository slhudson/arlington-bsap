"""Who sits on the Board, and how a year's seats are counted. A module, not a
step: the coverage figures read it so they agree on what "sitting" means.

A seat-year is the average, over the months the Board existed in a year, of
the members seated that month, so a vacancy is a dip below the seats that
exist and a member who served part of a year counts that part. A 1 July
count would draw a full Board through both. docs/figures.md says why.

FIRST and LAST are the years the build covers, read from the seat table,
which ends in the year the roster was checked to. A figure's year axis
runs through LAST + 1, so every figure ends where the build does.
"""

import pandas as pd

import paths

_by_year = paths.read("members_by_year")
FIRST, LAST = int(_by_year.year.min()), int(_by_year.year.max())
AGE_FIRST = 1900    # the age figures begin with the censuses' ages (docs/members.md, "Birth years")


def seat_years(label):
    """One row per year, one column per label: the seat-years held by members
    whose `label` (a function of the member's name) is that column.

    The terms are read the way members_by_year reads them: a district seat
    ends when the Board went at large. Each year's total is asserted equal to
    the seats members_by_year counts, men + women, so the two cannot drift.
    """
    terms = paths.read("members")
    end = (LAST + 1) * 12                     # terms run past the year the roster was checked to
    at_large_from = terms.loc[terms.district == "at large", "held_from"].min()
    terms = terms.assign(held_to=terms.held_to.where(terms.district == "at large",
                                                     terms.held_to.clip(upper=at_large_from)))
    terms["held_to"] = terms.held_to.clip(upper=end)
    terms = terms[terms.held_to > terms.held_from]

    per_month = []
    for month in range(int(terms.held_from.min()), int(terms.held_to.max())):
        sitting = terms[(terms.held_from <= month) & (month < terms.held_to)].drop_duplicates("name")
        per_month.append({"year": month // 12, **sitting.name.map(label).value_counts().to_dict()})
    monthly = pd.DataFrame(per_month).fillna(0)
    # The first year is averaged over the months the Board existed, every other over twelve.
    months_existing = monthly.groupby("year").size().clip(upper=12)
    graded = monthly.groupby("year").sum().div(months_existing, axis=0)

    seats_held = _by_year.set_index("year")[["men", "women"]].sum(axis=1)
    off = (graded.sum(axis=1) - seats_held.reindex(graded.index)).abs() > 1e-9
    if off.any() or set(graded.index) != set(seats_held.index):
        raise AssertionError(
            "seat-years here and in members_by_year differ in "
            f"{list(graded.index[off])}; the years differ by {set(graded.index) ^ set(seats_held.index)}")
    return graded.reset_index()
