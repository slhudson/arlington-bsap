"""Where real paths are assigned to the short names this stage uses.

Maps data/built/ and data/clean/, and defines no route to data/raw/ or
data/transcribed/ (CLAUDE.md). A source reaches this stage through a
code/build/ step or not at all.
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd

import citekeys

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
BUILT = DATA / "built"
CLEAN = DATA / "clean"


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


def typed(frame: pd.DataFrame) -> pd.DataFrame:
    """A printed table with the types a plain read would give it: a column
    whose every non-blank value is a number becomes numeric, and a blank
    becomes missing."""
    out = {}
    for c in frame.columns:
        col = frame[c]
        numbers = pd.to_numeric(col.where(col != "", np.nan), errors="coerce")
        out[c] = numbers if numbers.notna().eq(col != "").all() else col.where(col != "", np.nan)
    return pd.DataFrame(out, index=frame.index)


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
