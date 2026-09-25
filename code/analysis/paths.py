"""Where real paths are assigned to the short names this stage uses.

Maps data/clean/ and figures/, and defines no route to data/raw/ or
data/transcribed/ (CLAUDE.md).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "clean"
FIGURES = ROOT / "figures"

RESIDENTS = CLEAN / "residents.csv"
BOARD_SEATS = CLEAN / "board_seats.csv"
VOTERS = CLEAN / "voters.csv"
TURNOUT = CLEAN / "turnout.csv"

for _f in (RESIDENTS, BOARD_SEATS, VOTERS, TURNOUT):
    if not _f.exists():
        raise FileNotFoundError(f"{_f} missing - run the build stage first (bash run.sh)")


def save(fig, stem, profile=None):
    """Save a figure for one output profile, or for both, under the script's
    own name."""
    import charts
    import style
    charts.fit(fig)
    for name in [profile] if profile else list(style.PROFILES):
        spec = style.PROFILES[name]
        kind = spec["format"]
        d = FIGURES / kind
        d.mkdir(parents=True, exist_ok=True)
        # No timestamp, so an unchanged figure is an unchanged file.
        meta = {"CreationDate": None} if kind == "pdf" else {"Software": None}
        fig.savefig(d / f"{stem}.{kind}", dpi=spec["dpi"], metadata=meta)
