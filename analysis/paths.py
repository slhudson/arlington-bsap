"""Paths for the analysis stage: read from data/, write to figures/.

There is deliberately no path to raw/ here. By the time analysis runs, the
subjective decisions about what the numbers *are* have been made in build/.
Analysis may choose how to show a number; it may not change one.

If a figure seems to need something raw/ has and data/ does not, the fix is a
change to build/, not an import added here.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"

DEMOGRAPHICS = DATA / "demographics.csv"
BOARD_COUNTS = DATA / "board_counts.csv"
ROSTER = DATA / "roster.csv"


def out(stem: str) -> str:
    """Path prefix for a figure; scripts append ".pdf" / ".png" themselves."""
    FIGURES.mkdir(exist_ok=True)
    return str(FIGURES / stem)


for _f in (DEMOGRAPHICS, BOARD_COUNTS):
    if not _f.exists():
        raise FileNotFoundError(f"{_f} missing - run the build stage first (bash run.sh)")
