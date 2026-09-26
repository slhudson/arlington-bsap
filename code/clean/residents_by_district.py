"""Population by magisterial district, 1870-1930 -> data/clean/residents_by_district.csv

One row per census per district, Arlington, Jefferson and Washington, each
as that census drew it: the total, white and black where the table prints
race (1870 only, blank otherwise), and `source`, the volume and page.

The districts are the level-1 lines of each census's table of the county's
minor civil divisions, less Alexandria city, which sits among them through
1890, as in residents.early_years(). Each census's three must sum to the
county total in residents.csv. docs/residents.md has the boundary changes
the series crosses.
"""
import re

import pandas as pd

import census
import citekeys
from paths import read, write

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


def table(path):
    """One keyed-in census table, as data/built/census.csv holds it."""
    return census.table("transcribed/by_claude/us_census_bureau/" + path)


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
    if "colored" in t.columns:
        d["white"], d["black"] = lines.white, lines.colored
    d["source"] = f"{key} p.{re.search(r'_p(\d+)_', path).group(1)}"
    return d


def build() -> pd.DataFrame:
    d = pd.concat([districts(y) for y in TABLES], ignore_index=True)
    d = d[["year", "district", "total", "white", "black", "source"]]

    # A misread district cell shows here: the county total is printed, or
    # derived from the city's line, independently of the district lines.
    county = read("residents").set_index("year")["total"]
    for year, g in d.groupby("year"):
        if g.total.sum() != county[year]:
            raise AssertionError(
                f"{year}: the districts sum to {g.total.sum():,.0f} but residents.csv's "
                f"county total is {county[year]:,.0f}; a district cell is misread")
    raced = d.white.notna()
    off = d[raced & (d.white + d.black != d.total)]
    if not off.empty:
        r = off.iloc[0]
        raise AssertionError(f"{r.year} {r.district}: white {r.white:,.0f} and black "
                             f"{r.black:,.0f} do not make its total {r.total:,.0f}")

    for col in ("total", "white", "black"):
        d[col] = d[col].astype("Int64")
    return d


if __name__ == "__main__":
    write(build(), "residents_by_district")
