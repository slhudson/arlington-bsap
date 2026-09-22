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
import board_seats  # noqa: E402
import residents  # noqa: E402


def breaks(module, attr, mangle, build=None):
    """Run a build with one input mangled; return the error it raised, or None."""
    original = getattr(module, attr)
    setattr(module, attr, mangle(original))
    try:
        (build or module.build)()
        return None
    except AssertionError as e:
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
