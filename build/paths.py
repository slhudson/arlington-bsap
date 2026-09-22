"""Repo-relative paths to the frozen inputs and the generated-figure directory.

Every script imports from here rather than hard-coding a path, so there is
exactly one place to edit if the snapshot directory is ever renamed. Paths
resolve from this file's own location, which means scripts run correctly no
matter what the current working directory is.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / "2026-09-22-handoff"
FIGURES = ROOT / "figures"

# The three workbooks, named exactly as received (spaces and all).
DEMOGRAPHICS = RAW / "arlington county demographic data.xlsx"
BOARD = RAW / "arlington board - descriptive representation (1870-2026).xlsx"
ROSTER = RAW / "arlington county board member database (1932-2026).xlsx"


def out(stem: str) -> str:
    """Path prefix for a figure, e.g. out("foo") -> ".../figures/foo".

    Scripts append ".pdf" / ".png" themselves, matching how they were written.
    """
    FIGURES.mkdir(exist_ok=True)
    return str(FIGURES / stem)


# Fail loudly and immediately if an input is missing, rather than letting
# pandas raise a confusing error deep inside a read_excel call.
for _f in (DEMOGRAPHICS, BOARD, ROSTER):
    if not _f.exists():
        raise FileNotFoundError(f"missing frozen input: {_f}")
