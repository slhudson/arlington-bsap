"""Where real filenames are assigned to the short names the code uses.

The analysis-stage counterpart to code/build/files.py. It maps data/ and figures/;
it defines no route to raw/. A figure script asking for a source workbook gets
an ImportError, so the wall between deciding what a number IS and deciding how
it is SHOWN is a thing that is not there, rather than a rule to remember.

If a figure seems to need something raw/ has and data/ does not, the fix is a
change to code/build/, not an import added here.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "clean"
FIGURES = ROOT / "figures"

RESIDENTS = CLEAN / "residents.csv"
BOARD_SEATS = CLEAN / "board_seats.csv"
BOARD_MEMBERS = CLEAN / "board_members.csv"

for _f in (RESIDENTS, BOARD_SEATS):
    if not _f.exists():
        raise FileNotFoundError(f"{_f} missing - run the build stage first (bash run.sh)")


def save(fig, stem):
    """Save a figure as both formats, PDF and PNG in their own directories.

    PDF is what the paper includes - vector, so it stays sharp at any size.
    PNG is for slides, email and anywhere that cannot take a PDF.

    By convention the stem matches the script's own filename, so
    code/analysis/residents_by_race.py produces residents_by_race.pdf and .png.
    run.sh checks that after every build.
    """
    import style                      # imported here: this is the only visual choice files.py makes
    for kind, kwargs in (("pdf", {}), ("png", {"dpi": 200})):
        d = FIGURES / kind
        d.mkdir(parents=True, exist_ok=True)
        # A tight box crops to the legend and the rotated ticks exactly, which
        # reads as cramped on the page. style.PAD is the margin every figure keeps.
        fig.savefig(d / f"{stem}.{kind}", bbox_inches="tight",
                    pad_inches=style.PAD, **kwargs)


def build_stage_on_path():
    """Let a figure import code/build/open_questions.py.

    Appends rather than inserts, because code/build/ also has a files.py: putting it
    first would shadow this module and hand analysis a route to raw/.
    """
    import sys
    sys.path.append(str(ROOT / "code" / "build"))
