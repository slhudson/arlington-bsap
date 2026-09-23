"""Census population by year -> data/clean/residents.csv

One row per census year, 1870-2020: population totals, the four race
categories, Board seats, and the derived residents-per-seat and cube-root
columns.

The `source` column names the document each row's figures come from.

**1870-1890 are derived from the census volumes.** Before 1900 Alexandria city
sat inside the county, so no published table gives the territory the Board
governed - it has to be derived by subtracting the city. That happens in
early_years() below, from the tables transcribed under
data/transcribed/by_claude/, and it replaces the delivered workbook for those
three years. See docs/questions.md.

**1900-1990 totals come from the published Census county series**, transcribed
from data/raw/us_census_bureau/. They were checked against the workbook first and matched
every year.

**2000-2020 totals come from the Bureau's own data files**, fetched by
code/fetch/census.py into data/raw/us_census_bureau/. No transcription step, so no
reading error to make.

**The workbook still supplies** the race and ethnicity figures for 1900-2020
and the seat columns. Each of those is a candidate for
the same treatment: find the published source, transcribe it, and stop reading
the workbook for it.

Which is why there are two source columns rather than one. `total_source`
names the document the year's total came from; `race_source` names where its
race and ethnicity figures came from, which before 1900 is the same volume and
after it is Alex's workbook, whose own source is not recorded. One column
saying `forstall1996` beside race figures that document never supplied would
be a false citation - so what is left to do stays visible in the data.

**From 1980 the race columns come from the crossed census table.** Race and
Hispanic origin are two census questions, not one, so a person answers both and
lands in two of the four columns at once - which is why the workbook's figures
sum to more than the county in 1970 and 1990 (Q1 in docs/questions.md). The
Bureau also publishes the two answers crossed, and those categories partition
the county exactly:

    hisp + white + black + aapi + the remainder == total

where `hisp` is Hispanic of any race and the other three are non-Hispanic. The
remainder - non-Hispanic other and multiracial - is not a column: it is what a
figure has left after subtracting these four from the total, which is how the
figures already draw it.

1980 is the first census to ask Hispanic origin of everyone rather than of a 5
percent sample. 1970's is not comparable and is left on the workbook's figures;
before 1970 the question does not exist and `white` means white.

`race_source` says which of the two each year's figures came from, so a row
carries its own provenance rather than the reader having to know where the
switch falls.

Values are otherwise written as reported. The contested treatments are not
applied here; see docs/questions.md.
"""
import pandas as pd

import citekeys
from paths import RAW, RESIDENTS_XLSX, TRANSCRIBED, numeric, write

# Which document each year's population total comes from. Named here rather
# than decided by a rule, so it can be read off rather than inferred, and so a
# change of source is a visible edit.
TOTAL_SOURCE = {
    1870: citekeys.CENSUS_1870,
    1880: citekeys.CENSUS_1880,
    1890: citekeys.CENSUS_1890,
    1900: citekeys.CENSUS_COUNTY_SERIES, 1910: citekeys.CENSUS_COUNTY_SERIES,
    1920: citekeys.CENSUS_COUNTY_SERIES, 1930: citekeys.CENSUS_COUNTY_SERIES,
    1940: citekeys.CENSUS_COUNTY_SERIES, 1950: citekeys.CENSUS_COUNTY_SERIES,
    1960: citekeys.CENSUS_COUNTY_SERIES, 1970: citekeys.CENSUS_COUNTY_SERIES,
    1980: citekeys.CENSUS_COUNTY_SERIES, 1990: citekeys.CENSUS_COUNTY_SERIES,
    2000: citekeys.CENSUS_DATA_FILE, 2010: citekeys.CENSUS_DATA_FILE,
    2020: citekeys.CENSUS_DATA_FILE,
}


def table(path):
    """Read a transcribed table by its path under data/transcribed/."""
    return pd.read_csv(TRANSCRIBED / path)


def arlington(year, table):
    """Arlington's row from a Census data file, which holds every Virginia county.

    The table is named by its Census code - P003, P3, P1 - because the codes
    differ by census and a name like "race" also matches
    "hispanic_origin_by_race".
    """
    hits = sorted((RAW / "us_census_bureau" / str(year)).glob(f"censusapi_*_{table}_*_virginia_counties.csv"))
    if len(hits) != 1:
        raise FileNotFoundError(f"expected one {table} file for {year}, found {len(hits)}")
    d = pd.read_csv(hits[0])
    row = d[d.NAME.str.startswith("Arlington")]
    if len(row) != 1:
        raise AssertionError(f"{hits[0].name}: expected one Arlington row, found {len(row)}")
    return row.iloc[0]


def early_years() -> pd.DataFrame:
    """County population for 1870-1890, derived from the published volumes.

    The hierarchy check is the point. Each transcription carries the printed
    indentation as a `level` column, and sums take level 1 only - a level-2 row
    is a detail of the line above and already inside it. Freedman village is
    printed at level 2 within Arlington district, so it cannot be added as a
    fourth district. That error is unrepresentable here rather than warned
    against; it is what produced 4,596 where the districts give 4,258.
    """
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

    # A race split must account for its own total. This is the check the
    # delivered workbook fails for 1870 (by 100) and 1890 (by 278).
    for _, r in d.iterrows():
        gap = r.total - r.white - r.black
        if abs(gap) > 5:
            raise AssertionError(
                f"{int(r.year)}: white {r.white:,.0f} + black {r.black:,.0f} leaves "
                f"{gap:,.0f} of a total of {r.total:,.0f} unaccounted.")
    return d

COLUMNS = ["year", "total", "white", "black", "hisp", "aapi", "board_seats",
           "at_large", "residents_per_seat", "cube_root_p", "cube_root_resident_ratio"]

# Categories that do not overlap, 1980 on. Written in stacking order.
# The crossed census groups, and which delivered column each one replaces.
# "nh_other" has no column: it is the remainder, and the figures compute it.
CENSUS_BASIS = {"hisp": "hispanic", "white": "nh_white",
                "black": "nh_black", "aapi": "nh_aapi"}


def stf1a(year, table):
    """A row of one archived Summary Tape File extract, for Arlington."""
    path = RAW / "us_census_bureau" / str(year) / f"stf1a_{table}_virginia_counties.csv"
    d = pd.read_csv(path)
    row = d[d.name.str.strip().str.upper().str.startswith("ARLINGTON COUNTY")]
    if len(row) != 1:
        raise AssertionError(f"{path.name}: expected one Arlington row, found {len(row)}")
    return row.iloc[0]


def census_basis() -> dict:
    """Five groups that partition the county, one row per census from 1980.

    Each census names its cells differently and 1980 words it as Spanish
    origin, so the arithmetic is written out per year rather than driven from a
    table of variable codes. Reading it should not require the code books.
    """
    out = {}

    # 1980: Table 7 is race for everyone, Table 9 the race of persons of
    # Spanish origin. Non-Hispanic is the first minus the second.
    r7, r9 = stf1a(1980, "table7_race"), stf1a(1980, "table9_race_of_spanish_origin")
    asian = ["japanese", "chinese", "filipino", "korean", "asian_indian",
             "vietnamese", "hawaiian", "guamanian", "samoan"]
    native = ["american_indian", "eskimo", "aleut"]
    out[1980] = {
        "hispanic": r9["total"],
        "nh_white": r7["white"] - r9["white"],
        "nh_black": r7["black"] - r9["black"],
        # 1980 does not split American Indian from Asian among Spanish-origin
        # persons, so the two are subtracted together and the remainder is
        # carried in nh_aapi rather than split on an assumption.
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

    # 2000-2020, from the API files. Variable numbers differ by census and
    # 2020 nests the races a level deeper, so each is named from the file's own
    # data dictionary rather than assumed to follow the previous one.
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
    d = pd.read_excel(RESIDENTS_XLSX).rename(columns={
        "census": "year",
        "population_total": "total",
        "white_population": "white",
        "black_population": "black",
        "hisp-latino_population": "hisp",
        "aapi_population": "aapi",
    })
    d = numeric(d[COLUMNS], COLUMNS)

    # The sheet carries source URLs in rows below the data. Those rows have no
    # year, so filtering on year drops them - rather than slicing a row count,
    # which would silently truncate if a third URL were added.
    d = d[d["year"].notna()].reset_index(drop=True)

    # Structural checks: these columns are derived from others in the same
    # sheet and must still agree. A silent disagreement would propagate into
    # the residents-per-seat figure.
    assert (d["residents_per_seat"] - d["total"] / d["board_seats"]).abs().max() < 1e-6, \
        "residents_per_seat no longer equals population / seats"
    assert (d["cube_root_resident_ratio"] - d["total"] ** (2 / 3)).abs().max() < 1e-6, \
        "cube_root_resident_ratio no longer equals population^(2/3)"

    # Take 1900-1990 totals from the published Census county series rather than
    # from the workbook. They were checked against it and matched every year,
    # so there is no reason to go on reading them second-hand.
    d["total_source"] = d["year"].map(TOTAL_SOURCE)
    series = table("by_claude/us_census_bureau/censusgov_pop1790-1990_p177_counties_virginia_arlington.csv").iloc[0]
    for year in range(1900, 2000, 10):
        m = d["year"] == year
        published = series[f"y{year}"]

        # The published figure is what gets used. The workbook's own value is
        # still compared against it: a disagreement would mean that row was
        # keyed from something else, which puts its race figures in doubt too -
        # and those have no traced source - see docs/questions.md.
        delivered = d.loc[m, "total"]
        if not delivered.empty and int(delivered.iloc[0]) != int(published):
            raise AssertionError(
                f"{year}: the workbook total is {delivered.iloc[0]:,.0f} but the "
                f"Census county series gives {published:,.0f}")

        d.loc[m, "total"] = published

    # 2000-2020 come from the Bureau's own data files, fetched by
    # code/fetch/census.py. No transcription step, so no reading error.
    # (year, race table, its total variable) - all three differ by census.
    for year, race_table, total in ((2000, "P003", "P003001"),
                                    (2010, "P3", "P003001"),
                                    (2020, "P1", "P1_001N")):
        d.loc[d["year"] == year, "total"] = arlington(year, race_table)[total]

    # Replace 1870-1890 with the figures derived from the volumes.
    early = early_years().set_index("year")
    for year, r in early.iterrows():
        m = d["year"] == year
        for col in ("total", "white", "black"):
            d.loc[m, col] = r[col]
        d.loc[m, "total_source"] = TOTAL_SOURCE[year]

    # Seat-derived columns must be recomputed for any year whose total moved.
    # The race and ethnicity figures have their own provenance: derived from
    # the volumes before 1900, and taken from the workbook after it.
    d["race_source"] = [TOTAL_SOURCE[y] if y < 1900 else citekeys.KEENA
                        for y in d["year"]]

    # From 1980, the crossed census table replaces the workbook's four columns.
    # The guard is the point of the exercise: if the five groups do not account
    # for the county exactly, they are not a partition and must not be drawn as
    # one. Only four are written - the fifth is the remainder a figure is left
    # with, and writing it as well would be the same number twice.
    basis = census_basis()
    for year, groups in basis.items():
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

    d["residents_per_seat"] = d["total"] / d["board_seats"]
    d["cube_root_p"] = d["total"] ** (1 / 3)
    d["cube_root_resident_ratio"] = d["total"] ** (2 / 3)
    return d


if __name__ == "__main__":
    write(build(), "residents")
