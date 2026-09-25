"""Census population by year -> data/clean/residents.csv

One row per census, 1870-2020: the total, four race categories, the seats
the Board had, and residents per seat. `total_source` and `race_source`
name the document each came from.

    1870-1890  derived from the census volumes: Alexandria city sat inside
               the county, so the Board's territory is county minus city
    1900-1990  totals from the Bureau's county series (forstall1996)
    2000-2020  totals from the Bureau's data files, code/fetch/census.py
    1900-1970  race from POP-TWPS0076 Table 47
    1980-      race crossed with Hispanic origin: `hisp` is Hispanic of any
               race, the other three are non-Hispanic, and the five groups
               partition the county exactly

The fifth crossed group, non-Hispanic other and multiracial, is not a
column: a figure takes it as total minus the four. `hisp` is blank before
1980. docs/residents.md says what backs each year and why.
"""
import pandas as pd

import citekeys
from board_roster import seats
from paths import RAW, TRANSCRIBED, write

COLUMNS = ["year", "total", "white", "black", "hisp", "aapi", "board_seats",
           "residents_per_seat"]
CENSUSES = range(1870, 2021, 10)
# Which document each year's total comes from.
TOTAL_SOURCE = {1870: citekeys.CENSUS_1870, 1880: citekeys.CENSUS_1880, 1890: citekeys.CENSUS_1890,
                **{y: citekeys.CENSUS_COUNTY_SERIES for y in range(1900, 2000, 10)},
                **{y: citekeys.CENSUS_DATA_FILE for y in range(2000, 2021, 10)}}
# The crossed census groups, 1980 on, and the column each one fills.
CENSUS_BASIS = {"hisp": "hispanic", "white": "nh_white",
                "black": "nh_black", "aapi": "nh_aapi"}


def table(path):
    """Read a transcribed table by its path under data/transcribed/."""
    return pd.read_csv(TRANSCRIBED / path)


def twps0076() -> dict:
    """Arlington by race, 1900-1970, from POP-TWPS0076 Table 47: White, Black
    and Asian/Pacific Islander as printed, full count only. 1940 prints
    American Indian and Asian/Pacific Islander as one merged cell, so `aapi`
    is left empty that year."""
    t = table("by_claude/us_census_bureau/"
              "censusgov_pop-twps0076_p1_virginia_arlington.csv")
    t = t[(t.basis == "full count") & (t.year.between(1900, 1970))]
    parts = ["white", "black", "american_indian", "asian_pacific_islander",
             "american_indian_asian_pacific_islander", "other_race"]
    out = {}
    for _, r in t.iterrows():
        got = sum(0 if pd.isna(r[c]) else r[c] for c in parts)
        assert got == r.total, (
            f"{int(r.year)}: the race columns give {got:,.0f} against a "
            f"printed total of {r.total:,.0f}")
        out[int(r.year)] = {"white": r.white, "black": r.black,
                            "aapi": r.asian_pacific_islander,
                            "hisp": float("nan")}
    return out


def arlington(year, table):
    """Arlington's row from a Census data file, by the table's Census code."""
    hits = sorted((RAW / "us_census_bureau" / str(year)).glob(f"censusapi_*_{table}_*_virginia_counties.csv"))
    if len(hits) != 1:
        raise FileNotFoundError(f"expected one {table} file for {year}, found {len(hits)}")
    d = pd.read_csv(hits[0])
    row = d[d.NAME.str.startswith("Arlington")]
    if len(row) != 1:
        raise AssertionError(f"{hits[0].name}: expected one Arlington row, found {len(row)}")
    return row.iloc[0]


def early_years() -> pd.DataFrame:
    """County population 1870-1890: the county minus Alexandria city, from
    the published volumes. Sums take `level` 1 rows only; a level-2 row is
    already inside the line above it."""
    t5_1890 = table("by_claude/us_census_bureau/1890/1890a_v1-11_p346_table5_virginia_alexandria.csv")
    t2_1870 = table("by_claude/us_census_bureau/1870/1870a-04_p69_table2_virginia_alexandria.csv").set_index("section")
    t3_1870 = table("by_claude/us_census_bureau/1870/1870a-09_p278_table3_virginia_alexandria.csv")
    t5_1880 = table("by_claude/us_census_bureau/1880/1880_v1-13_p412_table5_virginia_alexandria.csv")
    t6_1880 = table("by_claude/us_census_bureau/1880/1880_v1-13_p425_table6_virginia_alexandria.csv")
    t22 = table("by_claude/us_census_bureau/1890/1890a_v1-14_p520_table22_virginia_alexandria.csv").iloc[0]
    t23 = table("by_claude/us_census_bureau/1890/1890a_v1-14_p556_table23_virginia_alexandria.csv").iloc[0]

    rows = {}
    for year, col in ((1890, "pop_1890"), (1880, "pop_1880")):
        county = t5_1890.loc[t5_1890.level == 0, col].iloc[0]
        city = t5_1890.loc[t5_1890.label == "Alexandria city", col].iloc[0]
        districts = t5_1890.loc[t5_1890.level == 1, col].sum() - city
        if districts != county - city:
            raise AssertionError(
                f"{year}: county minus city is {county-city:,.0f} but the districts "
                f"sum to {districts:,.0f}")
        rows[year] = {"total": county - city}

    city70 = t3_1870.loc[t3_1870.label == "Alexandria"].iloc[0]
    rows[1870] = {"total": 16755 - city70.total}   # county total: census.gov 1790-1990
    rows[1870]["white"] = t2_1870.loc["white", "y1870"] - city70.white
    rows[1870]["black"] = t2_1870.loc["free_colored", "y1870"] - city70.colored
    rows[1880]["white"] = t5_1880.white_1880.iloc[0] - t6_1880.white_1880.iloc[0]
    rows[1880]["black"] = t5_1880.colored_1880.iloc[0] - t6_1880.colored_1880.iloc[0]

    def white(r):
        return r.total_native_white_m + r.total_native_white_f + r.foreign_white_m + r.foreign_white_f

    def colored(r):
        return r.total_colored_m + r.total_colored_f

    rows[1890]["white"] = white(t22) - white(t23)
    rows[1890]["black"] = colored(t22) - colored(t23)

    d = pd.DataFrame(rows).T.rename_axis("year").reset_index()
    # A race split must account for its own total.
    for _, r in d.iterrows():
        gap = r.total - r.white - r.black
        if abs(gap) > 5:
            raise AssertionError(
                f"{int(r.year)}: white {r.white:,.0f} + black {r.black:,.0f} leaves "
                f"{gap:,.0f} of a total of {r.total:,.0f} unaccounted.")
    return d


def stf1a(year, table):
    """A row of one archived Summary Tape File extract, for Arlington."""
    path = RAW / "us_census_bureau" / str(year) / f"stf1a_{table}_virginia_counties.csv"
    d = pd.read_csv(path)
    row = d[d.name.str.strip().str.upper().str.startswith("ARLINGTON COUNTY")]
    if len(row) != 1:
        raise AssertionError(f"{path.name}: expected one Arlington row, found {len(row)}")
    return row.iloc[0]


def census_basis() -> dict:
    """Five groups that partition the county, one row per census from 1980,
    with the arithmetic written out per census."""
    out = {}

    # 1980: Table 7 is race for everyone, Table 9 the race of persons of
    # Spanish origin; non-Hispanic is the first minus the second. Table 9
    # does not split American Indian from Asian, so nh_aapi carries both.
    r7, r9 = stf1a(1980, "table7_race"), stf1a(1980, "table9_race_of_spanish_origin")
    asian = ["japanese", "chinese", "filipino", "korean", "asian_indian",
             "vietnamese", "hawaiian", "guamanian", "samoan"]
    native = ["american_indian", "eskimo", "aleut"]
    out[1980] = {
        "hispanic": r9["total"],
        "nh_white": r7["white"] - r9["white"],
        "nh_black": r7["black"] - r9["black"],
        "nh_aapi": sum(r7[c] for c in asian + native)
                   - r9["american_indian_eskimo_aleut_asian_pacific_islander"],
        "nh_other": r7["other"] - r9["other"],
    }

    # 1990: the crossed table gives non-Hispanic directly.
    r = stf1a(1990, "hispanic_origin_by_race")
    hispanic = sum(r[c] for c in r.index if c.startswith("hispanic_"))
    out[1990] = {
        "hispanic": hispanic,
        "nh_white": r["not_hispanic_white"],
        "nh_black": r["not_hispanic_black"],
        "nh_aapi": r["not_hispanic_asian_pacific_islander"],
        "nh_other": r["not_hispanic_other"] + r["not_hispanic_american_indian_eskimo_aleut"],
    }

    # 2000-2020, from the API files, each named from its own data dictionary:
    #     hisp   Hispanic or Latino, all races
    #     w b a  non-Hispanic White, Black, Asian alone
    #     nh     non-Hispanic Native Hawaiian and other Pacific Islander alone
    #     ai o   non-Hispanic American Indian and Alaska Native, some other race
    #     two    non-Hispanic two or more races
    for year, table, keys in (
        (2000, "P008", {"hisp": "P008010", "w": "P008003", "b": "P008004",
                        "ai": "P008005", "a": "P008006", "nh": "P008007",
                        "o": "P008008", "two": "P008009"}),
        (2010, "P5", {"hisp": "P005010", "w": "P005003", "b": "P005004",
                      "ai": "P005005", "a": "P005006", "nh": "P005007",
                      "o": "P005008", "two": "P005009"}),
        (2020, "P2", {"hisp": "P2_002N", "w": "P2_005N", "b": "P2_006N",
                      "ai": "P2_007N", "a": "P2_008N", "nh": "P2_009N",
                      "o": "P2_010N", "two": "P2_011N"}),
    ):
        row = arlington(year, table)
        out[year] = {
            "hispanic": int(row[keys["hisp"]]),
            "nh_white": int(row[keys["w"]]),
            "nh_black": int(row[keys["b"]]),
            "nh_aapi": int(row[keys["a"]]) + int(row[keys["nh"]]),
            "nh_other": int(row[keys["ai"]]) + int(row[keys["o"]]) + int(row[keys["two"]]),
        }
    return out


def build() -> pd.DataFrame:
    d = pd.DataFrame({"year": list(CENSUSES)}, dtype=float).reindex(columns=COLUMNS)
    d["board_seats"] = d["year"].map(seats)
    d["total_source"] = d["year"].map(TOTAL_SOURCE)

    series = table("by_claude/us_census_bureau/censusgov_pop1790-1990_p177_counties_virginia_arlington.csv").iloc[0]
    for year in range(1900, 2000, 10):
        d.loc[d["year"] == year, "total"] = series[f"y{year}"]
    # (year, race table, its total variable) - all three differ by census.
    for year, race_table, total in ((2000, "P003", "P003001"),
                                    (2010, "P3", "P003001"),
                                    (2020, "P1", "P1_001N")):
        d.loc[d["year"] == year, "total"] = arlington(year, race_table)[total]
    for year, r in early_years().set_index("year").iterrows():
        m = d["year"] == year
        for col in ("total", "white", "black"):
            d.loc[m, col] = r[col]

    d["race_source"] = [TOTAL_SOURCE[y] if y < 1900 else "" for y in d["year"]]
    for year, r in twps0076().items():
        m = d["year"] == year
        for col in ("white", "black", "aapi", "hisp"):
            d.loc[m, col] = r[col]
        d.loc[m, "race_source"] = citekeys.CENSUS_TWPS0076
    # From 1980 the five groups must account for the county exactly.
    for year, groups in census_basis().items():
        m = d["year"] == year
        total = int(d.loc[m, "total"].iloc[0])
        got = sum(int(v) for v in groups.values())
        if got != total:
            raise AssertionError(
                f"{year}: the census categories sum to {got:,} but the county "
                f"total is {total:,}; they are not a partition")
        for col, key in CENSUS_BASIS.items():
            d.loc[m, col] = int(groups[key])
        d.loc[m, "race_source"] = (
            {1980: citekeys.CENSUS_1980_STF1A,
             1990: citekeys.CENSUS_1990_STF1A}.get(year, citekeys.CENSUS_DATA_FILE))
    assert (d["race_source"] != "").all(), (
        "no race source for "
        f"{[int(y) for y in d.loc[d.race_source == '', 'year']]}")

    d["residents_per_seat"] = d["total"] / d["board_seats"]
    # Int64 keeps a blank blank.
    d["year"] = d["year"].astype(int)
    for col in ("total", "white", "black", "hisp", "aapi", "board_seats"):
        d[col] = d[col].astype("Int64")
    return d


if __name__ == "__main__":
    write(build(), "residents")
