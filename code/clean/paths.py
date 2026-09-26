"""Where real paths are assigned to the short names this stage uses.

Maps data/built/ and data/clean/. The only other files this stage can
read are the ones SOURCES names: sources no build step yet reshapes, read
here directly, each inventoried in data/contents.csv as read by a clean
step. source() refuses any other path, so a new direct read is an edit to
this file (CLAUDE.md; `built-layer-holes` in docs/questions.csv is the
plan to close them).
"""
import os
from pathlib import Path

import pandas as pd

import citekeys

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
BUILT = DATA / "built"
CLEAN = DATA / "clean"

_RAW = DATA / "raw"
_BY_CLAUDE = DATA / "transcribed" / "by_claude"

# The direct reads that remain, by the step that makes them.
OLEARY_BOARD = _BY_CLAUDE / "arlington_county" / "board_1870-1920.csv"              # board_roster, turnout
BOARD_TERMS = _BY_CLAUDE / "board_terms.csv"                                        # board_roster
NOVACK_TERMS = _BY_CLAUDE / "arlington_historical_magazine" / "novack_terms_1930-1994.csv"
OLEARY_PRESIDENT = _BY_CLAUDE / "arlington_county" / "president_1872-1920.csv"      # voters
REGISTRATION = _RAW / "va_dept_of_elections" / "registration_2010-2025.csv"        # turnout
CENSUS = _RAW / "us_census_bureau"                                                  # residents, turnout
CENSUS_BY_CLAUDE = _BY_CLAUDE / "us_census_bureau"                                  # residents

SOURCES = {
    OLEARY_BOARD, BOARD_TERMS, NOVACK_TERMS, OLEARY_PRESIDENT, REGISTRATION,
    *(CENSUS / p for p in (
        "1980/stf1a_table10_age_virginia_counties.csv",
        "1990/stf1a_age_virginia_counties.csv",
        "2000/censusapi_dec_sf1_P005_race_18_and_over_virginia_counties.csv",
        "2010/censusapi_dec_sf1_P10_race_18_and_over_virginia_counties.csv",
        "2020/censusapi_dec_pl_P3_race_18_and_over_virginia_counties.csv",
        "1980/stf1a_table7_race_virginia_counties.csv",
        "1980/stf1a_table9_race_of_spanish_origin_virginia_counties.csv",
        "1990/stf1a_hispanic_origin_by_race_virginia_counties.csv",
        "2000/censusapi_dec_sf1_P003_race_virginia_counties.csv",
        "2000/censusapi_dec_sf1_P008_hispanic_origin_by_race_virginia_counties.csv",
        "2010/censusapi_dec_sf1_P3_race_virginia_counties.csv",
        "2010/censusapi_dec_sf1_P5_hispanic_origin_by_race_virginia_counties.csv",
        "2020/censusapi_dec_pl_P1_race_virginia_counties.csv",
        "2020/censusapi_dec_pl_P2_hispanic_origin_by_race_virginia_counties.csv")),
    *(CENSUS_BY_CLAUDE / p for p in (
        "1870/1870a-04_p69_table2_virginia_alexandria.csv",
        "1870/1870a-09_p278_table3_virginia_alexandria.csv",
        "1880/1880_v1-13_p412_table5_virginia_alexandria.csv",
        "1880/1880_v1-13_p425_table6_virginia_alexandria.csv",
        "1890/1890a_v1-11_p346_table5_virginia_alexandria.csv",
        "1890/1890a_v1-14_p520_table22_virginia_alexandria.csv",
        "1890/1890a_v1-14_p556_table23_virginia_alexandria.csv",
        "censusgov_pop-twps0076_p1_virginia_arlington.csv",
        "censusgov_pop1790-1990_p177_counties_virginia_arlington.csv")),
}


def source(path, **kw):
    """Read one of the sources SOURCES names, and nothing else."""
    path = Path(path)
    if path.resolve() not in {p.resolve() for p in SOURCES}:
        raise PermissionError(
            f"code/clean/ has no route to {path}. A source enters through a "
            f"code/build/ step; the direct reads that remain are listed in "
            f"code/clean/paths.py (CLAUDE.md).")
    return pd.read_csv(path, **kw)


def _fresh(path):
    """A table written this run. run.sh exports RUN_STARTED, and a table
    older than that is refused; run by hand, with no RUN_STARTED, the
    check is skipped."""
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - a step that writes it must run first")
    started = os.environ.get("RUN_STARTED")
    if started and path.stat().st_mtime < float(started):
        raise AssertionError(
            f"{path.name} is older than this run: the step that writes it has not "
            f"run yet. Check the order of BUILD and CLEAN in run.sh.")
    return path


def built(stem):
    """Read a table the build stage wrote this run, every cell as printed
    and a blank a blank."""
    return pd.read_csv(_fresh(BUILT / f"{stem}.csv"), dtype=str, keep_default_na=False)


def read(stem):
    """Read a table another clean step wrote this run."""
    return pd.read_csv(_fresh(CLEAN / f"{stem}.csv"))


def write(frame, stem):
    """Write data/clean/<stem>.csv, after checking every source cell, and
    print the placeholder counts."""
    CLEAN.mkdir(parents=True, exist_ok=True)
    path = CLEAN / f"{stem}.csv"
    counts = citekeys.check(
        (v for c in frame.columns if c == "source" or c.endswith("_source")
           for v in frame[c].astype(str)), path.name)
    frame.to_csv(path, index=False)
    print(f"  {path.name:<22} {len(frame):>4} rows", end="")
    said = ", ".join(f"{n} {k}" for k, n in counts.items() if n)
    print(f"   [{said}]" if said else "")
