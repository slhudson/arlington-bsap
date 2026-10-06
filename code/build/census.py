"""Every census table the build holds, Arlington's rows only -> data/built/census.csv

One row per cell, as printed: which table, which row of it, which column,
what value. From the Bureau's county-level files under data/raw/, the one
row naming Arlington; from the tables keyed in under
data/transcribed/by_claude/us_census_bureau/, every row, since each is
already the county's. Nothing is summed or chosen; code/clean/census.py
gives a table back in its own shape.

    table    the source file's path under data/, without the .gz the raw
             files are stored under
    row      its position in the source, from 0
    column   the source's column heading
    value    the cell as printed
"""
import pandas as pd

from paths import BY_CLAUDE, DATA, RAW, source, write

COUNTY_FILES = sorted((RAW / "us_census_bureau").glob("*/*_virginia_counties.csv.gz"))
COUNTY_TABLES = sorted((BY_CLAUDE / "us_census_bureau").rglob("*.csv"))


def arlington(frame: pd.DataFrame, path) -> pd.DataFrame:
    """The one row of a county-level file that names Arlington."""
    name = next(c for c in frame.columns if c.lower() == "name")
    rows = frame[frame[name].str.strip().str.upper().str.startswith("ARLINGTON")]
    if len(rows) != 1:
        raise AssertionError(f"{path.name}: expected one Arlington row, found {len(rows)}")
    return rows


def cells(frame: pd.DataFrame, path) -> pd.DataFrame:
    """A table as one row per cell, in row-major order."""
    long = frame.reset_index(drop=True).rename_axis("row").reset_index().melt(
        id_vars="row", var_name="column", value_name="value")
    long = long.sort_values(["row"], kind="stable")
    long.insert(0, "table", str(path.relative_to(DATA)).removesuffix(".gz"))
    return long


def build() -> pd.DataFrame:
    parts = [cells(arlington(source(p, dtype=str, keep_default_na=False), p), p) for p in COUNTY_FILES]
    parts += [cells(source(p, dtype=str, keep_default_na=False), p) for p in COUNTY_TABLES]
    return pd.concat(parts, ignore_index=True)


if __name__ == "__main__":
    write(build(), "census")
