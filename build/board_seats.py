"""raw/ Board composition workbook -> data/board_seats.csv

One row per year, 1871-2026: seats held by each race/ethnicity and by gender.

Fractional values are genuine - a member left mid-year and was replaced. 1883,
1884 and 1931 are "." in the source and become genuinely missing here, so
figures can render them as gaps rather than zeros.
"""
import pandas as pd

from files import BOARD_SEATS_XLSX, numeric, write

COLUMNS = ["year", "white", "black", "hisp", "aapi", "men", "women"]


def build() -> pd.DataFrame:
    b = pd.read_excel(BOARD_SEATS_XLSX)

    # The source header reads "aapi_m embers", with a space. raw/ is read-only,
    # so the spacing is corrected here. Stripping spaces from every header also
    # lets columns be read by name rather than position, so a reordered source
    # column cannot silently swap two categories.
    b.columns = [c.replace(" ", "") for c in b.columns]
    b = b.rename(columns={
        "white_members": "white",
        "black_members": "black",
        "hisp_latino_members": "hisp",
        "aapi_members": "aapi",
    })
    b = numeric(b[COLUMNS], COLUMNS)

    missing = b.loc[b["white"].isna(), "year"].tolist()
    assert missing == [1883, 1884, 1931], f"unexpected missing years: {missing}"

    # The Board is split two independent ways - by race and by gender - and
    # both must account for the same seats. Three seats through 1930, five
    # from 1932. Fractions are genuine, so compare as floats.
    reported = b.dropna(subset=["white"]).copy()
    reported["seats"] = reported["year"].apply(lambda y: 3 if y < 1932 else 5)
    by_race = reported[["white", "black", "hisp", "aapi"]].sum(axis=1)
    by_gender = reported[["men", "women"]].sum(axis=1)

    for label, totals in (("race categories", by_race), ("men + women", by_gender)):
        off = reported.loc[(totals - reported["seats"]).abs() > 1e-9, "year"]
        assert off.empty, f"{label} do not sum to the seat count in {list(off.astype(int))}"
    off = reported.loc[(by_race - by_gender).abs() > 1e-9, "year"]
    assert off.empty, f"race and gender totals disagree in {list(off.astype(int))}"
    return b


if __name__ == "__main__":
    write(build(), "board_seats")
