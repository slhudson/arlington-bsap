"""Seats held per year, by race and by gender -> data/clean/board_seats.csv

One row per year, 1870-2026, in seat-years: a member who held a seat for the
whole year counts 1, for four months 4/12.

**The denominator is the months the Board existed that year, not the calendar
year.** For every year but its first those are the same. Virginia's 1869
constitution created county boards of supervisors and Arlington's first
election was in May 1870, so the Board existed for eight months of 1870 and the
roster's first terms all begin then. Divided by twelve, 1870 would read 2.0 -
a chart of it shows the stack starting at two and rising to three, which says
the Board grew, and it did not. Divided by the eight months it existed, 1870
reads 3.0: the Board's seats were filled the whole time it was a Board.

This does not hide a vacancy. 1873 and 1990 are years the Board existed for all
twelve months and sat a seat short for part of them, and both still fall below
the full complement.

From 1870 to 1911 and from 1932 on, the rows are computed from
board_members.csv, whose terms run to the month. A term's months are its
start month through its end month, except that a month in which a successor
begins belongs to the successor - decided by Sally, 22 September 2026,
because days are not recorded consistently and the month is the unit
(docs/board.md). The
members elected in November 1915 were seated in January 1916, inside the
years with no roster, so they contribute no seat-years at all.

From 1912 to 1931 no terms are known and the rows are an assumption, stated
below and labelled `assumed`: three seats, filled, held by white men.

The stretch begins in 1912 and not 1916 because O'Leary does not list the
November 1911 election. The three men elected in 1907 held a four-year term
that ended in January 1912, and nothing names who won the seat after them.
Running their names to the next listed election, 1915, would have covered
those four years with an inference rather than a source.

**The Board's race coding is one code per person, so it is already a set of
categories that do not overlap** - the property the census columns in
residents.csv are built to have (docs/residents.md). A member coded
Hispanic carries no separate race, so `white` here means white and not
Hispanic, which is what the census basis means there. The two are comparable.

So the two files already line up, and the figures drawn from them can be read
against each other directly. J. Walter Tejada, the one Hispanic member, sits in
the Hispanic band for 2003-2015, exactly as a Hispanic resident sits in the
Hispanic band of residents_by_race; `white` on this side means white and not
Hispanic, as `nh_white` does on that side.

That a member's race is not recorded alongside their ethnicity costs nothing
here: the census basis does not use it either. It puts every Hispanic resident
in one band whatever their race, which is the same thing one code per person
achieves.
"""
import pandas as pd

import citekeys
from board_roster import AT_LARGE_FROM, PRESENT, SEATS_AT_LARGE, SEATS_DISTRICT
from paths import CLEAN, write

COLUMNS = ["year", "white", "black", "hisp", "aapi", "men", "women"]
RACE = {"White": "white", "Black": "black", "Hispanic": "hisp", "Asian": "aapi"}
GENDER = {"man": "men", "woman": "women"}
# Party is a third split of the same seats, from 1932 only: before the County
# Manager plan no source names one, and the columns are empty rather than
# zero, so a figure shows a gap and not a Board with no parties. A member
# whose party no source records is counted in `unrecorded`, so the five still
# account for every seat. docs/board.md, Party of Board members.
PARTY = {"Democratic": "dem", "Republican": "rep", "ABC": "abc",
         "independent": "ind", "": "unrecorded"}
PARTY_COLUMNS = ["dem", "abc", "rep", "ind", "unrecorded"]
# The years with no roster: stated rather than computed, below.
NO_ROSTER_YEARS = range(1912, AT_LARGE_FROM)


def months_held(members: pd.DataFrame) -> pd.DataFrame:
    """One row per term per calendar year: how many months of it were held."""
    m = members.copy()
    m["end_year"] = m.end_year.fillna(m.start_year)      # end unrecorded: this year only
    m["end_month"] = m.end_month.fillna(12)
    m["start"] = m.start_year * 12 + m.start_month - 1   # months since year 0, inclusive
    m["stop"] = m.end_year * 12 + m.end_month             # exclusive

    # The handover month belongs to the incoming member: where a successor in
    # the same district begins in a term's last month, that month is dropped
    # from the outgoing term. A term ending in December has no successor
    # beginning in December, so it keeps all twelve months.
    starts = m.groupby("district").start.apply(set)
    m["stop"] = [stop - 1 if (stop - 1) in starts[d] else stop
                 for d, stop in zip(m.district, m.stop)]

    rows = []
    for _, t in m.iterrows():
        for year in range(int(t.start_year), int(t.end_year) + 1):
            lo, hi = max(t.start, year * 12), min(t.stop, year * 12 + 12)
            if hi > lo:
                rows.append({"year": year, "months": hi - lo,
                             "race": RACE[t.race], "gender": GENDER[t.gender],
                             "party": PARTY[t.party if isinstance(t.party, str) else ""]})
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    members = pd.read_csv(CLEAN / "board_members.csv")
    held = months_held(members)
    by_race = held.pivot_table(index="year", columns="race", values="months", aggfunc="sum", fill_value=0) / 12
    by_gender = held.pivot_table(index="year", columns="gender", values="months", aggfunc="sum", fill_value=0) / 12
    by_party = held.pivot_table(index="year", columns="party", values="months", aggfunc="sum", fill_value=0) / 12
    # Each split keeps only its own columns before they are joined, so a
    # value that belongs to no category drops out here and is caught below
    # as seats unaccounted for, rather than surfacing as a column collision.
    built = pd.concat([by_race.reindex(columns=list(RACE.values())),
                       by_gender.reindex(columns=list(GENDER.values())),
                       by_party.reindex(columns=PARTY_COLUMNS)], axis=1)
    built = built.reindex(columns=COLUMNS[1:] + PARTY_COLUMNS).fillna(0.0).reset_index()
    built.loc[built.year < AT_LARGE_FROM, PARTY_COLUMNS] = float("nan")
    built = built[built.year <= PRESENT]
    built["source"] = citekeys.DERIVED

    # 1912-1931: no terms are known, so the rows are stated here rather than
    # computed. Three seats, all filled, all held by white men. That is an
    # assumption and reads as one; the seat count is structural (three
    # magisterial districts) but the occupancy and the coding are not.
    # docs/board.md.
    fill = pd.DataFrame({"year": list(NO_ROSTER_YEARS)})
    fill["white"] = SEATS_DISTRICT
    fill["men"] = SEATS_DISTRICT
    for c in ("black", "hisp", "aapi", "women"):
        fill[c] = 0.0
    for c in PARTY_COLUMNS:
        fill[c] = float("nan")
    fill["source"] = citekeys.ASSUMED

    d = pd.concat([built[~built.year.isin(NO_ROSTER_YEARS)], fill]).sort_values("year").reset_index(drop=True)
    d = d[COLUMNS + PARTY_COLUMNS + ["source"]]

    # The Board's first year is short because the Board was, not because a seat
    # was empty: it came into existence at the May 1870 election. Scale that year
    # by the months it existed, taken from the roster rather than written in, so
    # the figure is a measure of seats filled while there was a Board to fill.
    first_month = int(members.loc[members.start_year == d.year.min(), "start_month"].min())
    months_existing = 13 - first_month
    if months_existing < 12:
        m = d.year == d.year.min()
        d.loc[m, COLUMNS[1:]] = d.loc[m, COLUMNS[1:]] * 12 / months_existing
    years = list(d.year)
    assert years == list(range(1870, PRESENT + 1)), f"years are not 1870-2026 without gaps: {years[:3]}..{years[-3:]}"

    # The seats held never exceed the seats that exist, and fall short only
    # where the roster records a vacancy or the year the Board began.
    seats = d.year.apply(
        lambda y: SEATS_DISTRICT if y < AT_LARGE_FROM else SEATS_AT_LARGE)
    total = d[["white", "black", "hisp", "aapi"]].sum(axis=1)
    over = d.loc[total - seats > 1e-9, "year"]
    assert over.empty, f"more seat-years than seats in {list(over)}"
    short = d.loc[(seats - total > 1e-9) & (d.source == citekeys.DERIVED), "year"]
    # 1873: Washington district vacant from the May election to December. 1990:
    # Milliken resigned in February and the special election was in May. 1870 is
    # not here: it is scaled by the months the Board existed, above.
    assert list(short) == [1873, 1990], f"seats fall short in {list(short)}; expected only 1873, 1990"

    # Race and gender split the same seats two independent ways, so they must
    # account for the same total in every year. That is where a term wrongly
    # attributed in one split and not the other would otherwise pass through
    # silently and move one figure without moving its pair.
    by_race = d[["white", "black", "hisp", "aapi"]].sum(axis=1)
    by_gender = d[["men", "women"]].sum(axis=1)
    off = d.loc[(by_race - by_gender).abs() > 1e-9, "year"]
    assert off.empty, (
        "race and gender do not account for the same seats in "
        f"{list(off.astype(int))}")
    # Party is the third split, and from 1932 it must account for the same
    # seats too. A term whose party fell into no column - a value PARTY does
    # not map - would otherwise thin one figure and leave its pair intact.
    by_party = d[PARTY_COLUMNS].sum(axis=1)
    off = d.loc[(d.year >= AT_LARGE_FROM) & ((by_race - by_party).abs() > 1e-9), "year"]
    assert off.empty, (
        "party does not account for the same seats as race in "
        f"{list(off.astype(int))}")
    blank = d.loc[(d.year < AT_LARGE_FROM) & d[PARTY_COLUMNS].notna().any(axis=1), "year"]
    assert blank.empty, f"party is recorded before {AT_LARGE_FROM} in {list(blank.astype(int))}"
    return d


if __name__ == "__main__":
    write(build(), "board_seats")
