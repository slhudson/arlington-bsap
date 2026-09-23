"""Where real paths are assigned to the short names this stage uses.

The analysis-stage counterpart to code/build/paths.py. It maps data/ and figures/;
it defines no route to raw/. A figure script asking for a source workbook gets
an ImportError, so the wall between deciding what a number IS and deciding how
it is SHOWN is a thing that is not there, rather than a rule to remember.

If a figure seems to need something raw/ has and data/ does not, the fix is a
change to code/build/, not an import added here.

The visual conventions are not here either. They live in style/, outside code/,
which has no paths.py and therefore no route to data/ - so a colour or a chart
helper cannot quietly start depending on a column. run.sh puts that folder on
the path; `import style` and `import charts` resolve to it.
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


def save(fig, stem, profile=None):
    """Save a figure for one output profile, or for both.

    The two profiles land in the two directories this repository already has.
    Print is the memo: PDF, vector, included at natural size. Screen is the
    deck: PNG, wider, with the type stepped up to match. Same figure code
    either way - only style.apply() differs.

    By convention the stem matches the script's own filename, so
    code/analysis/residents_by_race.py produces residents_by_race.pdf and .png.
    run.sh checks that after every build.
    """
    import charts
    import style
    charts.align(fig)
    profiles = [profile] if profile else list(style.PROFILES)
    for name in profiles:
        spec = style.PROFILES[name]
        kind = spec["format"]
        d = FIGURES / kind
        d.mkdir(parents=True, exist_ok=True)
        # The same numbers must produce the same bytes. Both backends stamp
        # the time of the run into the file, so without this an unchanged
        # figure is a changed file: every rebuild rewrites all of them and git
        # reports changed binaries whether or not a value has moved. figures/
        # is committed precisely so a change shows up as a reviewable diff,
        # and that only works if an unchanged figure is genuinely unchanged.
        # The two backends take different keys and neither accepts the other's.
        meta = {"CreationDate": None} if kind == "pdf" else {"Software": None}
        fig.savefig(d / f"{stem}.{kind}", dpi=spec["dpi"], metadata=meta)


def build_stage_on_path():
    """Let a figure import code/build/assumptions.py.

    Appends rather than inserts, because code/build/ also has a paths.py: putting it
    first would shadow this module and hand analysis a route to raw/.
    """
    import sys
    sys.path.append(str(ROOT / "code" / "build"))
