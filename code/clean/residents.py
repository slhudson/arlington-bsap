"""Census population by year -> data/clean/residents.csv

One row per census, 1870-2020: the total, four race categories, the county
in seven age bands from 1930, the seats the Board had, and residents per
seat. `total_source`, `race_source` and `age_source` name the document each
came from.

    1870-1890  derived from the census volumes: Alexandria city sat inside
               the county, so the Board's territory is county minus city
    1900-1990  totals from the Bureau's county series (forstall1996)
    2000-2020  totals from the Bureau's data files, code/fetch/census.py
    1900-1970  race from POP-TWPS0076 Table 47
    1980-      race crossed with Hispanic origin: `hisp` is Hispanic of any
               race, the other three are non-Hispanic, and the five groups
               partition the county exactly

    1930-1970  seven age bands, from the census volume's county age table,
               keyed in by hand
    1980-      seven age bands, from each census's own age table

The fifth crossed group, non-Hispanic other and multiracial, is not a
column: a figure takes it as total minus the four. `hisp` is blank before 1980
and the age bands before 1930. The seven bands sum to `total`, and the adult
population is the six of them above `ageunder18`; neither has a column of
its own. docs/residents.md says what backs each year and why.
"""
import pandas as pd

import census
import citekeys
from board_terms import seats
from paths import write

# The county in seven age bands. Every cut is one all five censuses from
# 1980 share: 1980 prints 35 to 44, 45 to 54, 65 to 74 and 75 to 84 as
# single groups, so no cut at 40, 50, 70 or 80 exists to take.
# docs/residents.md has the reasoning.
AGE_BANDS = ("ageunder18", "age18to24", "age25to34", "age35to44", "age45to54",
             "age55to64", "age65plus")
ADULT_BANDS = AGE_BANDS[1:]
COLUMNS = ["year", "total", "white", "black", "hisp", "aapi", *AGE_BANDS,
           "board_seats", "residents_per_seat"]
CENSUSES = range(1870, 2021, 10)
# Which document each year's total comes from.
TOTAL_SOURCE = {1870: citekeys.CENSUS_1870, 1880: citekeys.CENSUS_1880, 1890: citekeys.CENSUS_1890,
                **{y: citekeys.CENSUS_COUNTY_SERIES for y in range(1900, 2000, 10)},
                **{y: citekeys.CENSUS_DATA_FILE for y in range(2000, 2021, 10)}}
# The crossed census groups, 1980 on, and the column each one fills.
CENSUS_BASIS = {"hisp": "hispanic", "white": "nh_white",
                "black": "nh_black", "aapi": "nh_aapi"}

# Which of an age table's groups each band is summed from. The Summary Tape
# Files name their groups; the API's sex-by-age table numbers them, and the
# numbers below are the male cells, with the female cell 24 further on.
STF_AGE_GROUPS = {
    1980: {"ageunder18": ["under_1", "1_2", "3_4", "5", "6", "7_9", "10_13",
                          "14", "15", "16", "17"],
           "age18to24": ["18", "19", "20", "21", "22_24"],
           "age25to34": ["25_29", "30_34"],
           "age35to44": ["35_44"],
           "age45to54": ["45_54"],
           "age55to64": ["55_59", "60_61", "62_64"],
           "age65plus": ["65_74", "75_84", "85_over"]},
    1990: {"ageunder18": ["under_1", "1_2", "3_4", "5", "6", "7_9", "10_11",
                          "12_13", "14", "15", "16", "17"],
           "age18to24": ["18", "19", "20", "21", "22_24"],
           "age25to34": ["25_29", "30_34"],
           "age35to44": ["35_39", "40_44"],
           "age45to54": ["45_49", "50_54"],
           "age55to64": ["55_59", "60_61", "62_64"],
           "age65plus": ["65_69", "70_74", "75_79", "80_84", "85_over"]},
}
API_AGE_CELLS = {"ageunder18": [3, 4, 5, 6],
                 "age18to24": [7, 8, 9, 10], "age25to34": [11, 12],
                 "age35to44": [13, 14], "age45to54": [15, 16],
                 "age55to64": [17, 18, 19],
                 "age65plus": [20, 21, 22, 23, 24, 25]}
FEMALE_OFFSET = 24
# (age table, its total cell, how a cell number is written) per census.
API_AGE_TABLE = {2000: ("P012", "P012001", "P012{:03d}".format),
                 2010: ("P12", "P012001", "P012{:03d}".format),
                 2020: ("P12", "P12_001N", "P12_{:03d}N".format)}


# 1930-1970: the census volumes' county tables, keyed in under
# data/transcribed/by_claude/us_census_bureau/, one file per printed table.
# A year may stack two tables; a label then names one printed line of the
# year, and no label may repeat.
VOLUME_AGE_TABLES = {
    1970: ["1970/00496492v1p48ch03_p48-122_table35_virginia_arlington.csv"],
}
# The line that prints the county's total.
VOLUME_TOTAL_LINE = {1970: "All ages"}
_SINGLE_1970 = ["Under 1 year", "1 year", *[f"{a} years" for a in range(2, 21)]]
_FIVE_1970 = ["Under 5 years", *[f"{a} to {a + 4} years" for a in range(5, 85, 5)],
              "85 years and over"]
# Runs of printed lines that must sum to the same number: a distribution the
# table prints in full against the county total, or two tables' counts of
# the same ages. A misread digit breaks one of them.
VOLUME_AGE_RUNS = {
    1970: [(_SINGLE_1970 + ["21 years and over"], ["All ages"]),
           (_FIVE_1970, ["All ages"])],
}
# Which printed lines each band is summed from.
VOLUME_AGE_LINES = {
    1970: {"ageunder18": ["Under 5 years", "5 to 9 years", "10 to 14 years",
                          "15 years", "16 years", "17 years"],
           "age18to24": ["18 years", "19 years", "20 to 24 years"],
           "age25to34": ["25 to 29 years", "30 to 34 years"],
           "age35to44": ["35 to 39 years", "40 to 44 years"],
           "age45to54": ["45 to 49 years", "50 to 54 years"],
           "age55to64": ["55 to 59 years", "60 to 64 years"],
           "age65plus": ["65 to 69 years", "70 to 74 years", "75 to 79 years",
                         "80 to 84 years", "85 years and over"]},
}


def table(path):
    """A transcribed census table by its path under
    data/transcribed/by_claude/us_census_bureau/."""
    return census.table("transcribed/by_claude/us_census_bureau/" + path)


def twps0076() -> dict:
    """Arlington by race, 1900-1970, from POP-TWPS0076 Table 47: White, Black
    and Asian/Pacific Islander as printed, full count only. 1940 prints
    American Indian and Asian/Pacific Islander as one merged cell, so `aapi`
    is left empty that year."""
    t = table("censusgov_pop-twps0076_p1_virginia_arlington.csv")
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
    return census.row(f"raw/us_census_bureau/{year}/censusapi_*_{table}_*_virginia_counties.csv")


def early_years() -> pd.DataFrame:
    """County population 1870-1890: the county minus Alexandria city, from
    the published volumes. Sums take `level` 1 rows only; a level-2 row is
    already inside the line above it."""
    t5_1890 = table("1890/1890a_v1-11_p346_table5_virginia_alexandria.csv")
    t2_1870 = table("1870/1870a-04_p69_table2_virginia_alexandria.csv").set_index("section")
    t3_1870 = table("1870/1870a-09_p278_table3_virginia_alexandria.csv")
    t5_1880 = table("1880/1880_v1-13_p412_table5_virginia_alexandria.csv")
    t6_1880 = table("1880/1880_v1-13_p425_table6_virginia_alexandria.csv")
    t22 = table("1890/1890a_v1-14_p520_table22_virginia_alexandria.csv").iloc[0]
    t23 = table("1890/1890a_v1-14_p556_table23_virginia_alexandria.csv").iloc[0]

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


def volume_table(year) -> pd.DataFrame:
    """The year's keyed-in age tables stacked, one row per printed line,
    indexed by its label; `cite` is the source cell with the page. Where a
    line prints male and female, the two must make its total: a digit
    misread in one column shows there."""
    parts = []
    for path in VOLUME_AGE_TABLES[year]:
        t = table(path)
        page = t["page"].map(lambda p: f"{p:.0f}" if isinstance(p, float) else p)
        t["cite"] = t["source"] + " p." + page
        parts.append(t)
    t = pd.concat(parts, ignore_index=True)
    twice = sorted(t.label[t.label.duplicated()])
    assert not twice, f"{year}: a label names two printed lines: {twice}"
    counts = t[~t.label.str.lower().str.startswith("median")]
    both = counts.dropna(subset=["male", "female"])
    off = both[both.male + both.female != both.total]
    assert off.empty, (
        f"{year}: male and female do not make the printed total on "
        f"{list(off.label)}; a line is misread")
    return t.set_index("label")


def volume_ages(year):
    """The seven bands from a census volume's printed age lines, and the
    citation for them. Every run the table prints in full must sum to what
    it is printed against, and the bands must account for the county's
    printed total: a misread digit, or a line put in two bands or none,
    stops the build."""
    t = volume_table(year)
    for lines, against in VOLUME_AGE_RUNS[year]:
        got, want = t.loc[lines, "total"].sum(), t.loc[against, "total"].sum()
        if got != want:
            raise AssertionError(
                f"{year}: the printed lines {lines[0]!r} to {lines[-1]!r} sum to "
                f"{got:,.0f}, but {' + '.join(against)} prints {want:,.0f}. The "
                f"transcription misreads a number; read the page again.")
    bands = VOLUME_AGE_LINES[year]
    named = [line for lines in bands.values() for line in lines]
    twice = sorted({line for line in named if named.count(line) > 1})
    assert not twice, f"{year}: printed lines named in more than one band: {twice}"
    out = {band: int(t.loc[lines, "total"].sum()) for band, lines in bands.items()}
    printed = int(t.loc[VOLUME_TOTAL_LINE[year], "total"])
    if sum(out.values()) != printed:
        raise AssertionError(
            f"{year}: the bands account for {sum(out.values()):,} of a printed "
            f"total of {printed:,}; a line is missing or counted twice")
    return out, printed, "; ".join(t.cite.unique())


def stf1a(year, table):
    """Arlington's row of one archived Summary Tape File extract."""
    return census.row(f"raw/us_census_bureau/{year}/stf1a_{table}_virginia_counties.csv")


def partition(bands, groups, year):
    """Every group of an age table belongs to exactly one band. A group named
    twice, or left out, is a mis-mapping the county total would not catch on
    its own: left out, the people are simply never counted."""
    named = [g for named_ in bands.values() for g in named_]
    twice = sorted({g for g in named if named.count(g) > 1})
    assert not twice, f"{year}: age groups named in more than one band: {twice}"
    assert set(named) == set(groups), (
        f"{year}: the bands do not cover the age groups exactly - "
        f"missing {sorted(set(groups) - set(named))}, "
        f"unknown {sorted(set(named) - set(groups))}")


def stf1a_ages(year, table):
    """The seven bands from an archived Summary Tape File's age table, and
    everyone the table counts."""
    row = stf1a(year, table)
    groups = [c for c in row.index if c not in ("name", "state", "county")]
    partition(STF_AGE_GROUPS[year], groups, year)
    out = {band: int(sum(row[g] for g in named))
           for band, named in STF_AGE_GROUPS[year].items()}
    return out, sum(out.values())


def api_ages(year) -> dict:
    """The seven bands from a census's sex-by-age table, men and women
    summed, checked against the table's own total."""
    table, total_cell, cell = API_AGE_TABLE[year]
    row = arlington(year, table)
    cells_ = [n for named in API_AGE_CELLS.values() for n in named]
    partition(API_AGE_CELLS, cells_, year)
    assert sorted(cells_) == list(range(3, 26)), (
        f"{year}: the bands name cells {sorted(cells_)}; the table's age cells "
        f"are 3 to 25")
    out = {band: int(sum(int(row[cell(n)]) + int(row[cell(n + FEMALE_OFFSET)])
                         for n in named))
           for band, named in API_AGE_CELLS.items()}
    got, want = sum(out.values()), int(row[total_cell])
    if got != want:
        raise AssertionError(
            f"{year}: the age cells account for {got:,} but {total_cell} states "
            f"{want:,} - check the cell numbers in API_AGE_CELLS")
    return out


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

    series = table("censusgov_pop1790-1990_p177_counties_virginia_arlington.csv").iloc[0]
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

    # The county in seven age bands, from 1930. Each census's age table must
    # account for the same county the total column does.
    d["age_source"] = ""
    ages, age_source = {}, {}
    for year in VOLUME_AGE_TABLES:
        ages[year], printed, age_source[year] = volume_ages(year)
        total = int(d.loc[d["year"] == year, "total"].iloc[0])
        if printed != total:
            raise AssertionError(
                f"{year}: the age table prints a county of {printed:,}; the total "
                f"column holds {total:,}")
    for year, age_table in ((1980, "table10_age"), (1990, "age")):
        ages[year], counted = stf1a_ages(year, age_table)
        total = int(d.loc[d["year"] == year, "total"].iloc[0])
        if counted != total:
            raise AssertionError(
                f"{year}: the age bands account for {counted:,} but the county "
                f"total is {total:,}; a group is missing or counted twice")
    for year in (2000, 2010, 2020):
        ages[year] = api_ages(year)
    for year, bands in ages.items():
        m = d["year"] == year
        for col, value in bands.items():
            d.loc[m, col] = value
        d.loc[m, "age_source"] = age_source.get(year) or (
            {1980: citekeys.CENSUS_1980_STF1A,
             1990: citekeys.CENSUS_1990_STF1A}.get(year, citekeys.CENSUS_DATA_FILE))

    d["residents_per_seat"] = d["total"] / d["board_seats"]
    # Int64 keeps a blank blank.
    d["year"] = d["year"].astype(int)
    for col in ("total", "white", "black", "hisp", "aapi", "board_seats",
                *AGE_BANDS):
        d[col] = d[col].astype("Int64")
    return d


if __name__ == "__main__":
    write(build(), "residents")
