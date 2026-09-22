"""Paths for the build stage: read from raw/, write to data/.

Only the build stage may read raw/. Analysis scripts import
analysis/paths.py instead, which has no path to the source spreadsheets, so
a figure script cannot reach around the cleaning step.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / "2026-09-22-handoff"
DATA = ROOT / "data"

# The three workbooks, named exactly as received (spaces and all).
DEMOGRAPHICS_XLSX = RAW / "arlington county demographic data.xlsx"
BOARD_XLSX = RAW / "arlington board - descriptive representation (1870-2026).xlsx"
ROSTER_XLSX = RAW / "arlington county board member database (1932-2026).xlsx"

for _f in (DEMOGRAPHICS_XLSX, BOARD_XLSX, ROSTER_XLSX):
    if not _f.exists():
        raise FileNotFoundError(f"missing frozen input: {_f}")
