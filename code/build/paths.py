"""Where real paths are assigned to the short names this stage uses.

The only module with a path to data/raw/ and data/transcribed/ (CLAUDE.md).
Every source a build step reads comes through source(), which remembers
it, and write() then refuses an output that lost a value: this stage
reshapes and never decides.
"""
from pathlib import Path

import pandas as pd

import citekeys

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
TRANSCRIBED = DATA / "transcribed"
BY_CLAUDE = TRANSCRIBED / "by_claude"
BUILT = DATA / "built"

# Every table read this run, as printed: (path, frame with every cell a string).
_INPUTS = []


def _reader(path):
    """The pandas reader for a source, by extension. A workbook the County
    publishes is read where it sits, like any other raw file."""
    return pd.read_excel if str(path).endswith((".xlsx", ".xls")) else pd.read_csv


def source(path, **kw):
    """Read a raw or transcribed table, and remember it for write()'s check.
    Keyword arguments go to pandas; the remembered copy is read as printed."""
    read = _reader(path)
    _INPUTS.append((path, read(path, dtype=str, keep_default_na=False)))
    return read(path, **kw)


def _parsed(values: pd.Series) -> bool:
    """Whether every non-blank value is a number or a true/false, which the
    output holds as a number or a boolean: a parse, not a decision."""
    return (pd.to_numeric(values.str.replace(",", ""), errors="coerce").notna().all()
            or values.str.lower().isin(["true", "false"]).all())


def lost(frame, inputs=None) -> list:
    """What `frame` dropped from the tables read this run: (path, column,
    values) for every column an input shares with it, by name, whose
    distinct printed values are not all in the output's. Numbers and
    booleans are not compared, since parsing "1,234" or "true" is not a
    decision. A column the output does not carry is not compared either: a
    dropped column is visible, a merged category is not."""
    out = frame.astype(object).where(frame.notna(), "").astype(str)
    problems = []
    for path, inp in (inputs if inputs is not None else _INPUTS):
        for col in inp.columns.intersection(out.columns):
            had = inp[col][inp[col] != ""]
            if had.empty or _parsed(had):
                continue
            gone = sorted(set(had) - set(out[col]))
            if gone:
                problems.append((path, col, gone))
    return problems


def write(frame, stem):
    """Write data/built/<stem>.csv, after checking that every value read
    this run is still there and every source cell names a citekey, and
    print the placeholder counts."""
    problems = lost(frame)
    if problems:
        raise AssertionError(
            f"{stem}.csv drops values its inputs carry. code/build/ reshapes and "
            f"never decides: a category merged or a value dropped belongs in "
            f"code/clean/, where the decision is reviewable (CLAUDE.md).\n"
            + "\n".join(f"  {Path(p).relative_to(ROOT)} column {c!r}: "
                        + ", ".join(repr(v) for v in gone[:5])
                        + (f" and {len(gone) - 5} more" if len(gone) > 5 else "")
                        for p, c, gone in problems))
    BUILT.mkdir(parents=True, exist_ok=True)
    path = BUILT / f"{stem}.csv"
    said = citekeys.checked(frame, path)
    frame.to_csv(path, index=False)
    print(said)
