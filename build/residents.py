"""raw/ census workbook -> data/residents.csv

One row per census year, 1870-2020: population totals, the four race
categories, Board seats, and the derived residents-per-seat and cube-root
columns.

Values are written as reported. The contested treatments are not applied here
while docs/questions.md Q1 and Q2 are open.
"""
import pandas as pd

from files import RESIDENTS_XLSX, numeric, write

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
    return d


if __name__ == "__main__":
    write(build(), "residents")
