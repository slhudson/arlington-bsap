"""Seats held per year, by race, gender and party -> data/clean/members_by_year.csv

One row per year, 1870-2026, in seat-years: a member who held a seat for
four months of a year counts 4/12, by the months members.csv says
each term held. Computed from that table, except 1912-1931, which
have no roster and are stated: three seats, held by white men, labelled
`assumed`. Party is from 1932 only, with a member no source records under
`unrecorded`. The denominator is the months the Board existed that year,
which is twelve for every year but 1870. docs/members.md, Seat-years.
"""
import pandas as pd

import citekeys
from members_terms import AT_LARGE_FROM, PRESENT, SEATS_DISTRICT, seats
from paths import read, write

COLUMNS = ["year", "white", "black", "hisp", "aapi", "men", "women"]
RACE = {"White": "white", "Black": "black", "Hispanic": "hisp", "Asian": "aapi"}
GENDER = {"man": "men", "woman": "women"}
PARTY = {"Democratic": "dem", "Republican": "rep", "ABC": "abc",
         "independent": "ind", "": "unrecorded"}
PARTY_COLUMNS = ["dem", "abc", "rep", "ind", "unrecorded"]
NO_ROSTER_YEARS = range(1912, AT_LARGE_FROM)


def months_held(members: pd.DataFrame) -> pd.DataFrame:
    """One row per term per calendar year: how many months of it were held,
    from held_from and held_to. A magisterial-district seat stopped existing
    as such the moment the Board reorganized to at large, whatever a term's
    own end date says, so none of it counts past the last month of 1931
    (Edward Duncan's term, ending January 1932 on the usual "ends when the
    next one starts" convention, is the first to reach that boundary)."""
    m = members
    rows = []
    for _, t in m.iterrows():
        held_to = t.held_to if t.district == "at large" else min(t.held_to, AT_LARGE_FROM * 12)
        for year in range(t.held_from // 12, (held_to - 1) // 12 + 1):
            lo, hi = max(t.held_from, year * 12), min(held_to, year * 12 + 12)
            if hi > lo:
                rows.append({"year": year, "months": hi - lo,
                             "race": RACE[t.race], "gender": GENDER[t.gender],
                             "party": PARTY[t.party if isinstance(t.party, str) else ""]})
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    members = read("members")
    held = months_held(members)

    def split(by, columns):
        return (held.pivot_table(index="year", columns=by, values="months", aggfunc="sum", fill_value=0)
                .reindex(columns=list(columns)) / 12)

    built = pd.concat([split("race", RACE.values()), split("gender", GENDER.values()),
                       split("party", PARTY_COLUMNS)], axis=1)
    built = built.reindex(columns=COLUMNS[1:] + PARTY_COLUMNS).fillna(0.0).reset_index()
    built.loc[built.year < AT_LARGE_FROM, PARTY_COLUMNS] = float("nan")
    built = built[built.year <= PRESENT]
    built["source"] = citekeys.DERIVED

    fill = pd.DataFrame({"year": list(NO_ROSTER_YEARS),
                         "white": SEATS_DISTRICT, "men": SEATS_DISTRICT,
                         **{c: 0.0 for c in ("black", "hisp", "aapi", "women")},
                         **{c: float("nan") for c in PARTY_COLUMNS},
                         "source": citekeys.ASSUMED})
    d = pd.concat([built[~built.year.isin(NO_ROSTER_YEARS)], fill]).sort_values("year").reset_index(drop=True)
    d = d[COLUMNS + PARTY_COLUMNS + ["source"]]

    # 1870 is scaled by the months the Board existed.
    first_month = int(members.loc[members.start_year == d.year.min(), "start_month"].min())
    months_existing = 13 - first_month
    if months_existing < 12:
        m = d.year == d.year.min()
        d.loc[m, COLUMNS[1:]] = d.loc[m, COLUMNS[1:]] * 12 / months_existing
    years = list(d.year)
    assert years == list(range(1870, PRESENT + 1)), f"years are not 1870-{PRESENT} without gaps: {years[:3]}..{years[-3:]}"

    # Seats held never exceed the seats that exist, and fall short only in
    # the two recorded vacancies.
    exist = d.year.map(seats)
    by_race = d[["white", "black", "hisp", "aapi"]].sum(axis=1)
    over = d.loc[by_race - exist > 1e-9, "year"]
    assert over.empty, f"more seat-years than seats in {list(over)}"
    short = d.loc[(exist - by_race > 1e-9) & (d.source == citekeys.DERIVED), "year"]
    assert list(short) == [1873, 1990], f"seats fall short in {list(short)}; expected only 1873, 1990"

    # Race, gender and party are three splits of the same seats.
    by_gender = d[["men", "women"]].sum(axis=1)
    off = d.loc[(by_race - by_gender).abs() > 1e-9, "year"]
    assert off.empty, (
        "race and gender do not account for the same seats in "
        f"{list(off.astype(int))}")
    by_party = d[PARTY_COLUMNS].sum(axis=1)
    off = d.loc[(d.year >= AT_LARGE_FROM) & ((by_race - by_party).abs() > 1e-9), "year"]
    assert off.empty, (
        "party does not account for the same seats as race in "
        f"{list(off.astype(int))}")
    blank = d.loc[(d.year < AT_LARGE_FROM) & d[PARTY_COLUMNS].notna().any(axis=1), "year"]
    assert blank.empty, f"party is recorded before {AT_LARGE_FROM} in {list(blank.astype(int))}"
    return d


if __name__ == "__main__":
    write(build(), "members_by_year")
