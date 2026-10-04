"""Seats held per year, by race, gender, party, birth year and place
-> data/clean/members_by_year.csv

One row per year, 1870-2026, in seat-years: a member who held a seat for
four months of a year counts 4/12, by the months members.csv says
each term held. Every year is computed from that table, and every figure
drawn on the three- and five-seat axis reads it, so a vacancy is one
decision made here. Party is from
1932 only, with a member no source records under `unrecorded`. The
denominator is the months the Board existed that year, which is twelve for
every year but 1870. docs/members.md, Seat-years.
"""
import pandas as pd

import citekeys
import members_residence
from members_terms import AT_LARGE_FROM, PRESENT, seats
from paths import read, write

COLUMNS = ["year", "white", "black", "hisp", "aapi", "men", "women"]
RACE = {"White": "white", "Black": "black", "Hispanic": "hisp", "Asian": "aapi"}
GENDER = {"man": "men", "woman": "women"}
PARTY = {"Democratic": "dem", "Republican": "rep", "ABC": "abc",
         "independent": "ind", "": "unrecorded"}
PARTY_COLUMNS = ["dem", "abc", "rep", "ind", "unrecorded"]
# Seat-years by whether the member has a birth year, and by the most exact
# place any source gives for the member (members_residence.PRECISION, most
# exact first). Each is one more split of the same seats.
BIRTH_COLUMNS = ["birth_year_known", "birth_year_unknown"]
PLACE_COLUMNS = ["address", "street", "neighborhood", "side", "district", "no_place"]
SPLIT_COLUMNS = BIRTH_COLUMNS + PLACE_COLUMNS


def best_place(residence: pd.DataFrame) -> dict:
    """Each member's most exact place, whenever it is dated: a place from
    after their service still counts (residence-after-service)."""
    order = list(members_residence.PRECISION)
    exactness = residence.precision.map(order.index)
    return exactness.groupby(residence.name).min().map(lambda r: order[int(r)]).to_dict()


def months_held(members: pd.DataFrame, places: dict) -> pd.DataFrame:
    """One row per term per calendar year: how many months of it were held,
    from held_from and held_to. A magisterial-district seat stopped existing
    as such the moment the Board reorganized to at large, whatever a term's
    own end date says, so none of it counts past the last month of 1931
    (Edward Duncan's term, ending January 1932 on the usual "ends when the
    next one starts" convention, is the first to reach that boundary).
    `places` is best_place()'s answer for each member."""
    m = members
    rows = []
    for _, t in m.iterrows():
        held_to = t.held_to if t.district == "at large" else min(t.held_to, AT_LARGE_FROM * 12)
        for year in range(t.held_from // 12, (held_to - 1) // 12 + 1):
            lo, hi = max(t.held_from, year * 12), min(held_to, year * 12 + 12)
            if hi > lo:
                rows.append({"year": year, "months": hi - lo,
                             "race": RACE[t.race], "gender": GENDER[t.gender],
                             "party": PARTY[t.party if isinstance(t.party, str) else ""],
                             "birth": BIRTH_COLUMNS[0] if pd.notna(t.birth_year) else BIRTH_COLUMNS[1],
                             "place": places.get(t["name"], "no_place")})
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    members = read("members")
    held = months_held(members, best_place(read("members_residence")))

    def split(by, columns):
        return (held.pivot_table(index="year", columns=by, values="months", aggfunc="sum", fill_value=0)
                .reindex(columns=list(columns)) / 12)

    built = pd.concat([split("race", RACE.values()), split("gender", GENDER.values()),
                       split("party", PARTY_COLUMNS), split("birth", BIRTH_COLUMNS),
                       split("place", PLACE_COLUMNS)], axis=1)
    built = built.reindex(columns=COLUMNS[1:] + PARTY_COLUMNS + SPLIT_COLUMNS).fillna(0.0).reset_index()
    built.loc[built.year < AT_LARGE_FROM, PARTY_COLUMNS] = float("nan")
    built = built[built.year <= PRESENT]
    built["source"] = citekeys.DERIVED
    d = built.sort_values("year").reset_index(drop=True)[COLUMNS + PARTY_COLUMNS + SPLIT_COLUMNS + ["source"]]

    # 1870 is scaled by the months the Board existed.
    first_month = int(members.loc[members.start_year == d.year.min(), "start_month"].min())
    months_existing = 13 - first_month
    if months_existing < 12:
        m = d.year == d.year.min()
        scaled = COLUMNS[1:] + SPLIT_COLUMNS
        d.loc[m, scaled] = d.loc[m, scaled] * 12 / months_existing
    years = list(d.year)
    assert years == list(range(1870, PRESENT + 1)), f"years are not 1870-{PRESENT} without gaps: {years[:3]}..{years[-3:]}"

    # Seats held never exceed the seats that exist, and fall short only in
    # the recorded vacancies. Four are in the district years: the Jefferson
    # seat from July to August 1870, whose elected supervisor never qualified
    # (members_roster.VACANT_1870), the Washington seat from July to November
    # 1873, the Jefferson seat from April to June 1879 after William A. Rowe
    # resigned it (members_roster.VACANT_1879), and the Washington seat from 1
    # January 1920 until Frank Upman was appointed (members_roster.VACANT_1920).
    # Seven are at large, each a seat left empty while a special election was
    # called (members_roster_roll.EMPTY): two months in 1990, one each in
    # 1997, 1999 and 2003, two in 2012, one in 2014 and two in 2020. A seat
    # nobody held counts towards nobody, which is why these years come to less
    # than five.
    exist = d.year.map(seats)
    by_race = d[["white", "black", "hisp", "aapi"]].sum(axis=1)
    over = d.loc[by_race - exist > 1e-9, "year"]
    assert over.empty, f"more seat-years than seats in {list(over)}"
    short = d.loc[(exist - by_race > 1e-9) & (d.source == citekeys.DERIVED), "year"]
    VACANT_YEARS = [1870, 1873, 1879, 1920, 1990, 1997, 1999, 2003, 2012, 2014, 2020]
    assert list(short) == VACANT_YEARS, \
        f"seats fall short in {list(short)}; expected only {VACANT_YEARS}"

    # Race, gender, party, birth year and place are splits of the same seats.
    for name, columns in (("birth year", BIRTH_COLUMNS), ("place", PLACE_COLUMNS)):
        off = d.loc[(by_race - d[columns].sum(axis=1)).abs() > 1e-9, "year"]
        assert off.empty, (f"{name} does not account for the same seats as race in "
                           f"{list(off.astype(int))}")
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
