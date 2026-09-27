"""Where real paths are assigned to the short names this stage uses.

Maps data/clean/, figures/ and the one file of numbers the prose cites,
paper/body_text_numbers.tex, and defines no route to data/raw/,
data/transcribed/ or data/built/ (CLAUDE.md).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "clean"
FIGURES = ROOT / "figures"
BODY_TEXT_NUMBERS = ROOT / "paper" / "body_text_numbers.tex"

RESIDENTS = CLEAN / "residents.csv"
RESIDENTS_BY_DISTRICT = CLEAN / "residents_by_district.csv"
MEMBERS = CLEAN / "members.csv"
MEMBERS_BY_YEAR = CLEAN / "members_by_year.csv"
BOARD_RESIDENCE = CLEAN / "members_residence.csv"
ELECTIONS_RESULTS = CLEAN / "elections_results.csv"
ELECTIONS_TURNOUT = CLEAN / "elections_turnout.csv"
BOARD_PEERS = CLEAN / "localities.csv"
BOARD_CANDIDACIES = CLEAN / "candidates.csv"

for _f in (RESIDENTS, RESIDENTS_BY_DISTRICT, MEMBERS, MEMBERS_BY_YEAR, BOARD_RESIDENCE,
           ELECTIONS_RESULTS, ELECTIONS_TURNOUT, BOARD_PEERS, BOARD_CANDIDACIES):
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
