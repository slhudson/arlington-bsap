"""Where real paths are assigned to the short names this stage uses.

Maps data/clean/, figures/ and the files the paper inputs,
paper/body_text_numbers.tex, paper/tables/members_roster.tex and
paper/tables/members_subsets.tex, and defines no route to sources/,
data/transcribed/ or data/built/ (CLAUDE.md).

A figure is saved under the name of the script that draws it, which save()
reads from the running program rather than taking as an argument: a script
cannot name another's figure.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "clean"
FIGURES = ROOT / "figures"
BODY_TEXT_NUMBERS = ROOT / "paper" / "body_text_numbers.tex"
MEMBERS_ROSTER = ROOT / "paper" / "tables" / "members_roster.tex"
MEMBERS_ROSTER_SUBSETS = ROOT / "paper" / "tables" / "members_subsets.tex"


def read(stem, **kw):
    """Read data/clean/<stem>.csv, under the short name the clean stage
    wrote it. Keyword arguments go to pandas."""
    path = CLEAN / f"{stem}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - run the build stage first (bash run.sh)")
    return pd.read_csv(path, **kw)


def stem():
    """The running script's name, which is the name of what it writes."""
    script = Path(sys.argv[0])
    if script.suffix != ".py":
        raise RuntimeError(
            f"a figure is named after the script that draws it, and the running "
            f"program is {script.name!r}, not a script in code/analysis/.")
    return script.stem


def save(fig, profile=None):
    """Save a figure for one output profile, or for both, under the
    script's own name."""
    import charts
    import style
    charts.fit(fig, profile or style.DEFAULT_PROFILE)
    name = stem()
    for p in [profile] if profile else list(style.PROFILES):
        spec = style.PROFILES[p]
        kind = spec["format"]
        d = FIGURES / kind
        d.mkdir(parents=True, exist_ok=True)
        # No timestamp, so an unchanged figure is an unchanged file.
        meta = {"CreationDate": None} if kind == "pdf" else {"Software": None}
        fig.savefig(d / f"{name}.{kind}", dpi=spec["dpi"], metadata=meta)
