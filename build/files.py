"""Where real filenames are assigned to the short names the code uses.

Fix the mapping here once and every script that imports it follows. Without
this, each script carries its own copy of a filename - which is how five
scripts ended up with five hardcoded paths to the same spreadsheet, free to
drift apart.

It also fails fast: a missing input raises here, with the path, before any work
starts, rather than surfacing as a confusing error from inside pandas.

This is the only module in the repository that knows where raw/ is.
analysis/files.py does the same job for data/ and figures/, and deliberately
defines no route to raw/ - so a figure script asking for a source workbook gets
an ImportError. The wall between the stages is a thing that is not there,
rather than a rule someone has to remember.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / "2026-09-22-handoff"
DATA = ROOT / "data"

# The three workbooks, named exactly as received (spaces and all).
RESIDENTS_XLSX = RAW / "arlington county demographic data.xlsx"
BOARD_SEATS_XLSX = RAW / "arlington board - descriptive representation (1870-2026).xlsx"
BOARD_MEMBERS_XLSX = RAW / "arlington county board member database (1932-2026).xlsx"

for _f in (RESIDENTS_XLSX, BOARD_SEATS_XLSX, BOARD_MEMBERS_XLSX):
    if not _f.exists():
        raise FileNotFoundError(f"missing frozen input: {_f}")


def write(frame, stem):
    """Write a built dataset to data/<stem>.csv, matching this script's name."""
    DATA.mkdir(exist_ok=True)
    path = DATA / f"{stem}.csv"
    frame.to_csv(path, index=False)
    print(f"  {path.name:<22} {len(frame):>4} rows")


def numeric(df, cols):
    """Coerce to numbers, turning "." and blanks into genuinely missing values."""
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df
