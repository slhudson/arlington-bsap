"""Tests that the build's guards still work.

    .venv/bin/python tests.py

The build already refuses bad data. What these test is that it still refuses -
so that editing build/ cannot quietly disable a check. Each test reintroduces
the specific mistake a guard exists to catch and asserts the build stops.

Only guards whose failure would be *silent* are worth this. If a figure script
saves under the wrong name the build halts with an error in your face; if the
Freedman village check stops working, a figure shows 4,596 and nobody notices.
These cover the second kind.

No framework by design: plain functions named test_*, each building its own
input, run by the loop at the bottom.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "build"))
import board_members  # noqa: E402
import board_roster  # noqa: E402
import board_seats  # noqa: E402
import citekeys  # noqa: E402
import residents  # noqa: E402


def breaks(module, attr, mangle, build=None):
    """Run a build with one input mangled; return the error it raised, or None.

    Most guards in this repository raise AssertionError. board_roster's raise
    ValueError instead - they are refusals over irreconcilable historical
    sources, not sanity checks on arithmetic - so both are caught here.
    """
    original = getattr(module, attr)
    setattr(module, attr, mangle(original))
    try:
        (build or module.build)()
        return None
    except (AssertionError, ValueError) as e:
        return str(e)
    finally:
        setattr(module, attr, original)


# --- guards on the census derivation ----------------------------------------

def test_freedman_village_cannot_become_a_district():
    """Promoting a level-2 sub-line to level 1 is what produced 4,596."""
    def mangle(orig):
        def patched(path):
            d = orig(path)
            if "p346" in path:
                d = d.copy()
                d.loc[d.label == "Freedman village", "level"] = 1
            return d
        return patched
    err = breaks(residents, "table", mangle)
    assert err and "districts sum to" in err, f"not caught: {err}"


def test_race_split_must_account_for_its_total():
    """The 1870 error: white 1,075 + black 2,010 leaves 100 unexplained."""
    def mangle(orig):
        def patched(path):
            d = orig(path)
            if "p69" in path:
                d = d.copy()
                d.loc[d.section == "white", "y1870"] = 9344
            return d
        return patched
    err = breaks(residents, "table", mangle)
    assert err and "unaccounted" in err, f"not caught: {err}"


# --- guards on the Board files ----------------------------------------------

def test_race_categories_must_sum_to_the_seat_count():
    def mangle(orig):
        def patched(*a, **k):
            d = orig(*a, **k)
            if any("aapi" in str(c) for c in d.columns):
                d = d.copy()
                d.loc[d.year == 1975, "white_members"] = 4
            return d
        return patched
    err = breaks(pd, "read_excel", mangle, build=board_seats.build)
    assert err and "1975" in err, f"not caught: {err}"


def test_a_new_duplicate_person_year_is_rejected():
    """Frisbie 1952 is known and allowed; anything else should stop the build."""
    def mangle(orig):
        def patched(*a, **k):
            d = orig(*a, **k)
            if "Last_name" in d.columns or "last_name" in d.columns:
                d = pd.concat([d, d.iloc[[0]]], ignore_index=True)
            return d
        return patched
    err = breaks(pd, "read_excel", mangle, build=board_members.build)
    assert err and "duplicate" in err, f"not caught: {err}"


def test_a_wrong_term_length_is_rejected():
    """Stretching one term by a year should throw off the five-seat count.

    check_five_seats() is what catches a wrong term boundary anywhere in the
    roster - Novack's open-ended spans, a special election's handover, a
    regular four-year cycle. This mangles one term after election_terms()
    has produced it, so the mistake looks exactly like a bad source read: an
    extra year that overlaps the next member's term.
    """
    def mangle(orig):
        def patched(earlier):
            d = orig(earlier)
            at_large = d.index[(d.district == "at large") & (d.end_year == 1997)]
            d = d.copy()
            d.loc[at_large, "end_year"] += 1
            return d
        return patched
    err = breaks(board_roster, "election_terms", mangle, build=board_roster.build)
    assert err and "at large" in err, f"not caught: {err}"


def test_prose_in_the_name_column_is_rejected():
    """O'Leary sometimes writes a sentence where a name goes - "A. D. Torreyson
    elected, but successfully contested by Frederick S. Corbett in Oct." - and
    a parser that misses the pattern would carry the whole sentence through as
    a person. check_names() refuses any name that reads as prose.
    """
    def mangle(orig):
        def patched():
            for row in orig():
                if row["name"] == "A. D. Torreyson":
                    row = dict(row, name="A. D. Torreyson elected, but contested")
                yield row
        return patched
    err = breaks(board_roster, "oleary_terms", mangle, build=board_roster.build)
    assert err and "prose" in err, f"not caught: {err}"


def test_an_attributed_name_that_misses_the_roster_is_rejected():
    """The demographics file matches people by exact name. A near-miss
    ("Bozman" for "Ellen Bozman") would fall silently into the workbook
    coding or the default - the one failure that file exists to prevent -
    so the build refuses it.
    """
    def mangle(orig):
        def patched(path, *a, **k):
            d = orig(path, *a, **k)
            if "basis" in d.columns:                        # the attributions file
                d.loc[d.name == "Ellen Bozman", "name"] = "Bozman"
            return d
        return patched
    err = breaks(board_members.pd, "read_csv", mangle, build=board_members.build)
    assert err and "not in the roster" in err, f"not caught: {err}"


def test_two_sources_disagreeing_on_race_is_a_finding():
    """Two sources naming a different race for one person is something to
    stop and look at, not something to pick between silently."""
    def mangle(orig):
        def patched(path, *a, **k):
            d = orig(path, *a, **k)
            if "basis" in d.columns:
                extra = d[d.name == "William A. Rowe"].iloc[[0]].copy()
                extra["race"] = "White"
                d = pd.concat([d, extra], ignore_index=True)
            return d
        return patched
    err = breaks(board_members.pd, "read_csv", mangle, build=board_members.build)
    assert err and "disagree" in err, f"not caught: {err}"

def test_a_citekey_with_no_bibliography_entry_is_rejected():
    """A source cell naming an entry that does not exist in sources.bib is a
    number in the report that cannot be traced to a document. That is exactly
    the silent kind: the figure still draws, and the citation points nowhere."""
    try:
        citekeys.check(["novack1994 p.4", "oleary2O10 p.6"], "board_members.csv")
        err = None
    except AssertionError as e:
        err = str(e)
    assert err and "oleary2O10" in err, f"not caught: {err}"


def test_a_placeholder_is_allowed_and_counted():
    """The placeholders are the way to say "we do not know yet" without
    stopping the build - draft work over an incomplete record needs one. They
    must pass, and must come back counted so every run reports them."""
    counts = citekeys.check(
        [citekeys.ASSUMED, citekeys.ASSUMED, citekeys.UNSOURCED], "x.csv")
    assert counts[citekeys.ASSUMED] == 2, counts
    assert counts[citekeys.UNSOURCED] == 1, counts


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ok    {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}\n        {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
