"""Where real paths are assigned to the short names this stage uses.

Maps data/clean/, figures/ and the one file of numbers the prose cites,
paper/body_text_numbers.tex, and defines no route to data/raw/,
data/transcribed/ or data/built/ (CLAUDE.md).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "clean"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper" / "arlington-bsap.tex"
BODY_TEXT_NUMBERS = ROOT / "paper" / "body_text_numbers.tex"

RESIDENTS = CLEAN / "residents.csv"
RESIDENTS_BY_DISTRICT = CLEAN / "residents_by_district.csv"
BOARD_MEMBERS = CLEAN / "board_members.csv"
BOARD_SEATS = CLEAN / "board_seats.csv"
BOARD_RESIDENCE = CLEAN / "board_residence.csv"
VOTERS = CLEAN / "voters.csv"
TURNOUT = CLEAN / "turnout.csv"
BOARD_PEERS = CLEAN / "board_peers.csv"
BOARD_CANDIDACIES = CLEAN / "board_candidacies.csv"

for _f in (RESIDENTS, RESIDENTS_BY_DISTRICT, BOARD_MEMBERS, BOARD_SEATS, BOARD_RESIDENCE,
           VOTERS, TURNOUT, BOARD_PEERS, BOARD_CANDIDACIES):
    if not _f.exists():
        raise FileNotFoundError(f"{_f} missing - run the build stage first (bash run.sh)")


def save(fig, stem, profile=None):
    """Save a figure for one output profile, or for both, under the script's
    own name."""
    import charts
    import style
    charts.fit(fig, profile or style.DEFAULT_PROFILE)
    for name in [profile] if profile else list(style.PROFILES):
        spec = style.PROFILES[name]
        kind = spec["format"]
        d = FIGURES / kind
        d.mkdir(parents=True, exist_ok=True)
        # No timestamp, so an unchanged figure is an unchanged file.
        meta = {"CreationDate": None} if kind == "pdf" else {"Software": None}
        fig.savefig(d / f"{stem}.{kind}", dpi=spec["dpi"], metadata=meta)
