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
FROM_THE_SCHEDULES = (1880, 1900, 1910, 1920)

# Where an enumeration district's own description does not place it, or where
# the census's descriptions cannot be matched to the extract at all. The
# numbering is each census's own, so this is keyed by census. None means the
# district is outside the county the Board governed and its people are not
# counted: in 1880 Alexandria city is still inside the census county.
# docs/residents.md has the evidence for each reading.
#
#   1880  the transcribed descriptions carry no text, so the three
#         magisterial districts are the three enumeration districts whose
#         head counts are the three the volume prints, and the other five are
#         the city's four wards
#   1900  IPUMS numbers the districts differently from the descriptions,
#         which run 1, 2, 3 and 99, so none of them can be joined by number
#   1910  Fort Myer, which the Arlington descriptions say they exclude
#   1920  the same, under a different number
ED_READ_BY_HAND = {
    1880: {"1": None, "2": None, "3": None, "4": None, "5": None,
           "6": "Arlington", "7": "Jefferson", "8": "Washington"},
    1900: {"1": "Arlington", "15": "Arlington", "16": "Arlington",
           "2": "Jefferson", "3": "Washington"},
    1910: {"10": "Arlington"},
    1920: {"11": "Arlington"},
}

# A district whose head count in the extract is known to be short of the
# volume's, so no race split is written for it and the figure's line breaks
# there. 1900's database is missing 499 of Arlington district's 3,200 people.
INCOMPLETE = {1900: ("Arlington",)}

# IPUMS race codes, as the codebooks in data/raw/ipums/ list them, read into
# the columns this table carries. Code 3 is American Indian.
RACE_CODES = {"1": "white", "2": "black", "3": "other"}

# How far a district's head count in the schedules may be from the total the
# volume prints for it. The schedules and the volume are two counts of the
# same population and the gap between them is a property of each census's
# database, not a single allowance: 1880, 1900 and 1920 tie to within a
# handful of people, and 1910's database is up to seventy-five short of a
# district. A tolerance is only worth having if it is still tight enough to
# catch an enumeration district in the wrong magisterial district, and
# identified() checks each of these against that directly.
TOO_FAR = {1880: 0.01, 1900: 0.01, 1910: 0.05, 1920: 0.01}


def table(path):
    """One keyed-in census table, as data/built/census.csv holds it."""
    return census.table("transcribed/by_claude/us_census_bureau/" + path)


def placed(year):
    """The year's extract with every enumeration district placed in a
    magisterial district: the rows, and the district each row belongs to."""
    d = typed(built("ipums"))
    d = d[d.year == year]
    if d.empty:
        raise AssertionError(f"data/built/ipums.csv holds no {year}")

    ed = d.ed.astype(str)
    by_hand = ED_READ_BY_HAND.get(year, {})
    named = d.district.where(d.district.notna(), ed.map(by_hand))
    unplaced = sorted(set(ed[named.isna() & ~ed.isin(by_hand)]))
    if unplaced:
        raise AssertionError(
            f"{year}: enumeration district(s) {unplaced} have no magisterial district. "
            f"Nothing places them, so the reading belongs in ED_READ_BY_HAND with its "
            f"evidence in docs/residents.md.")
    # An enumeration district read as outside the county is dropped here.
    keep = ~(named.isna() & ed.isin([e for e, v in by_hand.items() if v is None]))
    d, named = d[keep], named[keep]
    if not set(named) <= set(DISTRICTS):
        raise AssertionError(f"{year}: {sorted(set(named) - set(DISTRICTS))} is no district")
    return d, named


def enumeration_districts(year) -> pd.DataFrame:
    """The year's extract as counts per magisterial district per race column,
    every race code named."""
    d, named = placed(year)
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


def far(counted: pd.Series, published: pd.Series) -> pd.Series:
    """How far each district's count is from the total the volume prints for
    it, as a share of that total."""
    return ((counted.reindex(published.index).fillna(0) - published) / published).abs()


def identified(year, published: pd.Series):
    """Refuse unless the mapping is both close to the published district
    totals and the only mapping that is.

    The first check catches a wrong reading. The second keeps TOO_FAR
    honest: a tolerance wide enough to let an enumeration district sit in
    the wrong magisterial district would make the first check decorative,
    and nothing else would notice. Moving one district at a time is enough,
    because a mapping wrong in more than one place is wrong in one place
    first."""
    d, named = placed(year)
    apart = far(d.groupby(named).people.sum(), published)
    if (apart > TOO_FAR[year]).any():
        raise AssertionError(
            f"{year}: the schedules and the volume disagree about a district by more "
            f"than {TOO_FAR[year]:.0%} - " + ", ".join(f"{k} {v:.1%}" for k, v in apart.items())
            + ". An enumeration district is in the wrong magisterial district: check "
            "ED_READ_BY_HAND and the `district` column of the transcribed "
            "descriptions against the totals the volume prints.")

    ed = d.ed.astype(str)
    for one in sorted(set(ed)):
        moved = ed == one
        for elsewhere in DISTRICTS:
            if (named[moved] == elsewhere).all():
                continue
            other = named.mask(moved, elsewhere)
            if (far(d.groupby(other).people.sum(), published) <= TOO_FAR[year]).all():
                raise AssertionError(
                    f"{year}: enumeration district {one} would pass the check in "
                    f"{elsewhere} as well as where its description puts it, so the "
                    f"published district totals do not identify the mapping. TOO_FAR "
                    f"of {TOO_FAR[year]:.0%} is too wide for this census to police itself.")


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
        # A district the database is short of is left blank rather than given
        # a share of a population that is missing people of unknown race.
        short = INCOMPLETE.get(year, ())
        whole = ~d.district.isin(short)
        counted = enumeration_districts(year).reindex(d.district.to_numpy())
        for column, values in counted.items():
            d[column] = values.to_numpy()
            d.loc[~whole, column] = pd.NA
        d.loc[whole, "race_source"] = citekeys.race_source(year)
        identified(year, d[whole].set_index("district").total)
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
