"""Census population by year -> data/clean/residents.csv

One row per census year, 1870-2020: population totals, the four race
categories, Board seats, and the derived residents-per-seat and cube-root
columns.

The `source` column names the document each row's figures come from.

**1870-1890 are derived from the census volumes.** Before 1900 Alexandria city
sat inside the county, so no published table gives the territory the Board
governed - it has to be derived by subtracting the city. That happens in
early_years() below, from the tables transcribed under
data/extracted/by_claude/, and it replaces the delivered workbook for those
three years. See docs/questions.md Q8.

**1900-1990 totals come from the published Census county series**, transcribed
from data/raw/census/. They were checked against the workbook first and matched
every year.

**The workbook still supplies** the race and ethnicity figures for 1900-2020,
the 2000-2020 totals, and the seat columns. Each of those is a candidate for
the same treatment: find the published source, transcribe it, and stop reading
the workbook for it. The `source` column names the document behind every row,
so what is left to do is visible in the data.

Values are otherwise written as reported. The contested treatments are not
applied here while docs/questions.md Q1 and Q2 are open.
"""
import pandas as pd

from files import EXTRACTED, RESIDENTS_XLSX, numeric, write

BY_CLAUDE = EXTRACTED / "by_claude"
BY_HUMAN = EXTRACTED / "by_human"


def table(stem):
    """Read a transcribed source table, preferring a human-checked copy.

    Searches recursively, because transcriptions are filed under the census
    year they describe. Filenames are unique, so the year folder is for reading
    by people rather than for finding files.
    """
    for root in (BY_HUMAN, BY_CLAUDE):
        hits = sorted(root.rglob(f"{stem}.csv"))
        if len(hits) > 1:
            raise AssertionError(f"{stem}.csv appears more than once under {root}")
        if hits:
            return pd.read_csv(hits[0])
    raise FileNotFoundError(f"no transcription named {stem}.csv under {BY_CLAUDE}")


def early_years() -> pd.DataFrame:
    """County population for 1870-1890, derived from the published volumes.

    The hierarchy check is the point. Each transcription carries the printed
    indentation as a `level` column, and sums take level 1 only - a level-2 row
    is a detail of the line above and already inside it. Freedman village is
    printed at level 2 within Arlington district, so it cannot be added as a
    fourth district. That error is unrepresentable here rather than warned
    against; it is what produced 4,596 where the districts give 4,258.
    """
    t5_1890 = table("1890a_v1-11_p346_table5_virginia_alexandria")
    t2_1870 = table("1870a-04_p69_table2_virginia_alexandria").set_index("section")
    t3_1870 = table("1870a-09_p278_table3_virginia_alexandria")
    t5_1880 = table("1880_v1-13_p412_table5_virginia_alexandria")
    t6_1880 = table("1880_v1-13_p425_table6_virginia_alexandria")
    t22 = table("1890a_v1-14_p520_table22_virginia_alexandria").iloc[0]
    t23 = table("1890a_v1-14_p556_table23_virginia_alexandria").iloc[0]

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
    d["source"] = "workbook"
    series = table("censusgov_pop1790-1990_p177_counties_virginia_arlington").iloc[0]
    for year in range(1900, 2000, 10):
        m = d["year"] == year
        d.loc[m, "total"] = series[f"y{year}"]
        d.loc[m, "source"] = "census county series"

    # Replace 1870-1890 with the figures derived from the volumes.
    early = early_years().set_index("year")
    for year, r in early.iterrows():
        m = d["year"] == year
        for col in ("total", "white", "black"):
            d.loc[m, col] = r[col]
        d.loc[m, "source"] = "census volumes"

    # Seat-derived columns must be recomputed for any year whose total moved.
    d["residents_per_seat"] = d["total"] / d["board_seats"]
    d["cube_root_p"] = d["total"] ** (1 / 3)
    d["cube_root_resident_ratio"] = d["total"] ** (2 / 3)
    return d


if __name__ == "__main__":
    write(build(), "residents")
