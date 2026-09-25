"""Where real paths are assigned to the short names this stage uses.

The only module with a path to data/raw/ and data/transcribed/ (CLAUDE.md).
"""
import os
from pathlib import Path

import pandas as pd

import citekeys

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
TRANSCRIBED = DATA / "transcribed"
CLEAN = DATA / "clean"


def read(stem):
    """Read a table another build step wrote this run. run.sh exports
    RUN_STARTED, and a table older than that is refused; run by hand, with
    no RUN_STARTED, the check is skipped."""
    path = CLEAN / f"{stem}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - a step that writes it must run first")
    started = os.environ.get("RUN_STARTED")
    if started and path.stat().st_mtime < float(started):
        raise AssertionError(
            f"{path.name} is older than this run: the step that writes it has not "
            f"run yet. Check the order of BUILD in run.sh.")
    return pd.read_csv(path)


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
