"""Where real paths are assigned to the short names this stage uses.

data/ has four layers, sorted by how the numbers were produced:

    raw/          published sources, as they exist in the world
    transcribed/  someone read a source and wrote the numbers down:
                    by_ocr/     an OCR engine
                    by_claude/  a vision model reading a page image
    clean/        computed by code/build/, and the only layer code/analysis/ reads

Nothing reads by_ocr/. OCR misreads digits, so it locates a table and never
supplies a number.

No folder outranks another. code/build/residents.py names the source it uses for
each year, in one place, so which document a figure came from is something you
read rather than infer.

Fix the mapping here once and every script that imports it follows. Without
this, each script carries its own copy of a filename - which is how five
scripts ended up with five hardcoded paths to the same spreadsheet, free to
drift apart.

It also fails fast: a missing input raises here, with the path, before any work
starts, rather than surfacing as a confusing error from inside pandas.

This is the only module in the repository that knows where raw/ is.
code/analysis/paths.py does the same job for data/ and figures/, and deliberately
defines no route to raw/ - so a figure script asking for a source table gets
an ImportError. The wall between the stages is a thing that is not there,
rather than a rule someone has to remember.
"""
import os
from pathlib import Path

import pandas as pd

import citekeys

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"          # published sources, self-citing
TRANSCRIBED = DATA / "transcribed"   # by_ocr / by_claude
CLEAN = DATA / "clean"      # built here, read by code/analysis/



def read(stem):
    """Read a table another build step wrote this run.

    board_seats, voters and turnout read tables the steps before them wrote,
    so the order of the BUILD list in run.sh is a dependency and nothing else
    would say so: a step moved above its input would read the previous run's
    file and carry on. run.sh exports RUN_STARTED, and a table older than
    that is refused. Run by hand, with no RUN_STARTED, the check is skipped.
    """
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
    """Write a built dataset to data/clean/<stem>.csv, matching this script's name."""
    CLEAN.mkdir(parents=True, exist_ok=True)
    path = CLEAN / f"{stem}.csv"
    counts = citekeys.check(
        (v for c in frame.columns if c == "source" or c.endswith("_source")
           for v in frame[c].astype(str)), path.name)
    frame.to_csv(path, index=False)
    print(f"  {path.name:<22} {len(frame):>4} rows", end="")
    # Printed on every build rather than left to be discovered: these are the
    # rows whose basis is still a research errand, and they should fall.
    said = ", ".join(f"{n} {k}" for k, n in counts.items() if n)
    print(f"   [{said}]" if said else "")

