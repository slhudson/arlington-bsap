"""Population by magisterial district, 1870-1930 -> data/clean/residents_by_district.csv

One row per census per district, Arlington, Jefferson and Washington, each
as that census drew it: the total, the race split where there is one, and
the source of each. Race below the county is published for 1870 alone. 1920
is counted instead from the full-count schedules, so its race split and its
total come from different documents and the table names both.

The districts are the level-1 lines of each census's table of the county's
minor civil divisions, less Alexandria city, which sits among them through
1890, as in residents.early_years(). Each census's three must sum to the
county total in residents.csv. docs/residents.md has the boundary changes
the series crosses, and the 1920 mapping and its checks.
"""
import re

import pandas as pd

import census
import citekeys
from paths import built, read, typed, write

DISTRICTS = ("Arlington", "Jefferson", "Washington")
# (volume, table file, the column holding that census's own count) per census.
TABLES = {
    1870: (citekeys.CENSUS_1870, "1870/1870a-09_p279_table3_virginia_alexandria.csv", "total"),
    1880: (citekeys.CENSUS_1880, "1880/1880_v1-12_p356_table3_virginia_alexandria.csv", "pop_1880"),
    1890: (citekeys.CENSUS_1890, "1890/1890a_v1-11_p346_table5_virginia_alexandria.csv", "pop_1890"),
    1900: (citekeys.CENSUS_1900, "1900/volume-1-p8_p396_table5_virginia_alexandria.csv", "pop_1900"),
    1910: (citekeys.CENSUS_1910, "1910/volume-3-p8_p920_table1_virginia_alexandria.csv", "pop_1910"),
    1920: (citekeys.CENSUS_1920, "1920/41084484v1ch5_p647_table53_virginia_arlington.csv", "pop_1920"),
    1930: (citekeys.CENSUS_1930, "1930/03815512v1ch10_p1123_table4_virginia_arlington.csv", "pop_1930"),
}

# --- the race split counted from the full-count schedules ---------------------

# The censuses whose race split is counted from the schedules rather than
# printed in the volume.
FROM_THE_SCHEDULES = (1920,)

# The enumeration district descriptions name a magisterial district for five
# of the county's six districts. The sixth, ED 11, is the Fort Myer Military
# Reservation, and its description names none: the reservation is what the two
# Arlington district descriptions say they exclude, so it is the part of
# Arlington district they were carved around, and its people are Arlington's.
# docs/residents.md has the checks this rests on.
ED_WITHOUT_A_DISTRICT = {"11": "Arlington"}

# IPUMS race codes, as the codebook in data/raw/ipums/1920/ lists them, read
# into the columns this table carries. Code 3 is American Indian.
RACE_CODES = {"1": "white", "2": "black", "3": "other"}

# The extract and the volume are two counts of the same population: 16,043
# people against the 16,040 the volume prints for the county. A district whose
# extract total is further than this from the published one is refused, since
# it means an enumeration district is in the wrong district. The smallest
# enumeration district holds 1,148 people, so no misplacement can pass.
PEOPLE_APART = 25


def table(path):
    """One keyed-in census table, as data/built/census.csv holds it."""
    return census.table("transcribed/by_claude/us_census_bureau/" + path)


def enumeration_districts(year) -> pd.DataFrame:
    """The year's extract as counts per magisterial district per race column,
    every enumeration district placed in a district and every code named."""
    d = typed(built("ipums"))
    d = d[d.year == year]
    if d.empty:
        raise AssertionError(f"data/built/ipums.csv holds no {year}")

    ed = d.ed.astype(str)
    named = d.district.where(d.district.notna(), ed.map(ED_WITHOUT_A_DISTRICT))
    if named.isna().any():
        raise AssertionError(
            f"{year}: enumeration district(s) {sorted(set(ed[named.isna()]))} have no "
            f"magisterial district. The description names none, so the reading belongs "
            f"in ED_WITHOUT_A_DISTRICT with its reason in docs/residents.md.")
    if not set(named) <= set(DISTRICTS):
        raise AssertionError(f"{year}: {sorted(set(named) - set(DISTRICTS))} is no district")

    code = d.race.astype(str)
    if not set(code) <= set(RACE_CODES):
        raise AssertionError(
            f"{year}: race code(s) {sorted(set(code) - set(RACE_CODES))} are not in "
            f"RACE_CODES, so their people would be counted in no column")

    wide = (pd.DataFrame({"district": named, "column": code.map(RACE_CODES),
                          "people": d.people})
            .pivot_table(index="district", columns="column", values="people",
                         aggfunc="sum", fill_value=0))
    return wide.reindex(index=list(DISTRICTS), columns=list(RACE_CODES.values()),
                        fill_value=0)


def districts(year) -> pd.DataFrame:
    """The year's three districts, named by the first word of the printed
    line: "Jefferson district, including Potomac town" is Jefferson."""
    key, path, column = TABLES[year]
    t = table(path)
    lines = t[(t.level == 1) & (t.label != "Alexandria city")]
    d = pd.DataFrame({"year": year,
                      "district": lines.label.str.split().str[0].str.rstrip(","),
                      "total": lines[column]})
    if sorted(d.district) != sorted(DISTRICTS):
        raise AssertionError(f"{year}: the level-1 lines less Alexandria city are "
                             f"{list(lines.label)}, not the three districts")
    d["total_source"] = f"{key} p.{re.search(r'_p(\d+)_', path).group(1)}"
    d["race_source"] = ""            # no race below the county in this volume

    if "colored" in t.columns:
        d["white"], d["black"] = lines.white, lines.colored
        d["race_source"] = d.total_source
    elif year in FROM_THE_SCHEDULES:
        counted = enumeration_districts(year).reindex(d.district.to_numpy())
        for column, values in counted.items():
            d[column] = values.to_numpy()
        d["race_source"] = f"{citekeys.IPUMS_1920}; {citekeys.NARA_1920_EDS}"
        published = d.set_index("district").total
        apart = (d.set_index("district")[list(RACE_CODES.values())].sum(axis=1)
                 - published).abs()
        if (apart > PEOPLE_APART).any():
            raise AssertionError(
                f"{year}: the schedules and the volume disagree about a district by more "
                f"than {PEOPLE_APART} people - "
                + ", ".join(f"{k} {v:,.0f}" for k, v in apart.items()) +
                ". An enumeration district is in the wrong magisterial district: check "
                "ED_WITHOUT_A_DISTRICT and the `district` column of the transcribed "
                "descriptions against the totals the volume prints.")
    return d


def build() -> pd.DataFrame:
    d = pd.concat([districts(y) for y in TABLES], ignore_index=True)
    d = d[["year", "district", "total", "white", "black", "other",
           "total_source", "race_source"]]

    # A misread district cell shows here: the county total is printed, or
    # derived from the city's line, independently of the district lines.
    county = read("residents").set_index("year")["total"]
    for year, g in d.groupby("year"):
        if g.total.sum() != county[year]:
            raise AssertionError(
                f"{year}: the districts sum to {g.total.sum():,.0f} but residents.csv's "
                f"county total is {county[year]:,.0f}; a district cell is misread")
    # A race split printed in the volume accounts for the district exactly. One
    # counted from the schedules is checked against the volume in districts(),
    # to the people the two counts differ by, and cannot be checked twice.
    printed = d.white.notna() & ~d.year.isin(FROM_THE_SCHEDULES)
    counted = d[["white", "black", "other"]].sum(axis=1, min_count=1)
    off = d[printed & (counted != d.total)]
    if not off.empty:
        r = off.iloc[0]
        raise AssertionError(f"{r.year} {r.district}: white {r.white:,.0f} and black "
                             f"{r.black:,.0f} do not make its total {r.total:,.0f}")

    for col in ("total", "white", "black", "other"):
        d[col] = d[col].astype("Int64")
    return d


if __name__ == "__main__":
    write(build(), "residents_by_district")
