"""Transcribed census tables -> data/clean/early_census.csv, 1870-1890.

Before 1900 Alexandria city was part of the county, so no published table gives
the territory the Board actually governed. That figure has to be derived, and
the derivation lives here rather than in anyone's spreadsheet.

Sources are read table-by-table into data/extracted/by_claude/, laid out as
printed. A value confirmed by a person is copied into by_human/ and takes
precedence, so checking something changes what gets built.

The hierarchy check is the point. Each transcription carries the printed
indentation as a `level` column, and summing a level-1 group never touches
level 2. Freedman village is printed at level 2 inside Arlington district, so
it cannot be added as a fourth district - the error that produced 4,596 is
unrepresentable here rather than merely warned against.
"""
import pandas as pd

from files import EXTRACTED, write

BY_CLAUDE = EXTRACTED / "by_claude"
BY_HUMAN = EXTRACTED / "by_human"


def table(stem):
    """Read a transcribed table, preferring a human-checked copy if one exists."""
    human = BY_HUMAN / f"{stem}.csv"
    path = human if human.exists() else BY_CLAUDE / f"{stem}.csv"
    d = pd.read_csv(path)
    d.attrs["checked_by_person"] = human.exists()
    return d


def parts_of(d, column):
    """Sum the level-1 rows of a table - its immediate parts, never their details.

    A level-2 row is a detail of the line above it and is already counted in
    that line. Summing level 1 only is what makes double counting impossible.
    """
    return d.loc[d.level == 1, column].sum()


def build() -> pd.DataFrame:
    t5_1890 = table("1890a_v1-11_p346_table5_virginia_alexandria")
    t2_1870 = table("1870a-04_p69_table2_virginia_alexandria")
    t3_1870 = table("1870a-09_p278_table3_virginia_alexandria")
    t5_1880 = table("1880_v1-13_p412_table5_virginia_alexandria")
    t6_1880 = table("1880_v1-13_p425_table6_virginia_alexandria")
    t22_1890 = table("1890a_v1-14_p520_table22_virginia_alexandria")
    t23_1890 = table("1890a_v1-14_p556_table23_virginia_alexandria")

    def county_minus_city(county, city):
        return county - city

    rows = []

    # --- totals -------------------------------------------------------------
    for year, col in ((1890, "pop_1890"), (1880, "pop_1880")):
        county = t5_1890.loc[t5_1890.level == 0, col].iloc[0]
        city = t5_1890.loc[t5_1890.label == "Alexandria city", col].iloc[0]
        # Route 1: county minus city. Route 2: the districts, which are the
        # level-1 rows other than the city.
        districts = parts_of(t5_1890, col) - city
        if districts != county - city:
            raise AssertionError(
                f"{year}: county minus city is {county-city:,} but the districts "
                f"sum to {districts:,}")
        rows.append({"year": year, "total": county - city})

    city_1870 = t3_1870.loc[t3_1870.label == "Alexandria", "total"].iloc[0]
    rows.append({"year": 1870, "total": 16755 - city_1870})   # county total: census.gov 1790-1990

    d = pd.DataFrame(rows).set_index("year").sort_index()

    # --- race ---------------------------------------------------------------
    w = t2_1870.set_index("section")
    d.loc[1870, "white"] = w.loc["white", "y1870"] - t3_1870.loc[t3_1870.label == "Alexandria", "white"].iloc[0]
    d.loc[1870, "black"] = w.loc["free_colored", "y1870"] - t3_1870.loc[t3_1870.label == "Alexandria", "colored"].iloc[0]

    d.loc[1880, "white"] = t5_1880.white_1880.iloc[0] - t6_1880.white_1880.iloc[0]
    d.loc[1880, "black"] = t5_1880.colored_1880.iloc[0] - t6_1880.colored_1880.iloc[0]

    def white_of(t):
        r = t.iloc[0]
        return (r.total_native_white_m + r.total_native_white_f
                + r.foreign_white_m + r.foreign_white_f)

    def colored_of(t):
        r = t.iloc[0]
        return r.total_colored_m + r.total_colored_f

    d.loc[1890, "white"] = white_of(t22_1890) - white_of(t23_1890)
    d.loc[1890, "black"] = colored_of(t22_1890) - colored_of(t23_1890)

    # --- the check the delivered workbook fails ------------------------------
    for year, r in d.iterrows():
        gap = r.total - r.white - r.black
        if abs(gap) > 5:
            raise AssertionError(
                f"{year}: white {r.white:,.0f} + black {r.black:,.0f} leaves "
                f"{gap:,.0f} of a total of {r.total:,.0f} unaccounted.")
        d.loc[year, "unaccounted"] = gap

    return d.reset_index().astype(int)


if __name__ == "__main__":
    d = build()
    print(d.to_string(index=False))
    write(d, "early_census")
