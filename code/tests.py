"""Tests that the build's guards still work.

    .venv/bin/python code/tests.py

Each test reintroduces the specific mistake a guard exists to catch and
asserts the build stops. Only guards whose failure would be silent are
tested. No framework: plain functions named test_*, each building its own
input, run by the loop at the bottom.
"""
import csv
import hashlib
import os
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code" / "build"))
import board_members  # noqa: E402
import paths  # noqa: E402
import board_roster  # noqa: E402
import board_seats  # noqa: E402
import citekeys  # noqa: E402
import residents  # noqa: E402
import turnout  # noqa: E402

sys.path.insert(0, str(ROOT / "code" / "fetch"))
import registration  # noqa: E402


def breaks(module, attr, mangle, build=None):
    """Run a build with one input mangled; return the error it raised, or None."""
    original = getattr(module, attr)
    setattr(module, attr, mangle(original))
    try:
        (build or module.build)()
        return None
    except (AssertionError, ValueError) as e:
        return str(e)
    finally:
        setattr(module, attr, original)


def patch_csv(module, when, change):
    """A mangle for a module's pd.read_csv: `change` is applied to any frame
    for which `when(frame)` holds."""
    def mangle(orig):
        def patched(path, *a, **k):
            d = orig(path, *a, **k)
            return change(d) if when(d) else d
        return patched
    return mangle


def bib_entries():
    """(key, body) for every entry in paper/sources.bib."""
    bib = (ROOT / "paper" / "sources.bib").read_text()
    return re.findall(r"^@\w+\{([^,\s]+)\s*,(.*?)^\}", bib, re.M | re.S)


def questions():
    return (ROOT / "docs" / "questions.csv").read_text()


# --- guards on the census derivation ----------------------------------------

def test_freedman_village_cannot_become_a_district():
    """A level-2 sub-line promoted to level 1."""
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
    """A race column that leaves part of the total unexplained."""
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

def test_race_and_gender_must_account_for_the_same_seats():
    """One term with a gender the seat table has no column for."""
    def mangle(orig):
        def patched(members):
            d = orig(members).copy()
            d.loc[d.index[d.year == 1975][0], "gender"] = "unrecorded"
            return d
        return patched
    err = breaks(board_seats, "months_held", mangle)
    assert err and "same seats" in err, f"not caught: {err}"


def test_a_wrong_term_length_is_rejected():
    """One term stretched by a year, so it overlaps the next member's."""
    def mangle(orig):
        def patched(earlier):
            d = orig(earlier).copy()
            at_large = d.index[(d.district == "at large") & (d.end_year == 1997)]
            d.loc[at_large, "end_year"] += 1
            return d
        return patched
    err = breaks(board_roster, "election_terms", mangle, build=board_roster.build)
    assert err and "at large" in err, f"not caught: {err}"


def test_a_term_that_does_not_say_how_it_began_is_rejected():
    """A seated_by value outside the four the roster defines."""
    def mangle(orig):
        def patched(earlier):
            d = orig(earlier).copy()
            d.loc[d.index[(d.district == "at large") & (d.start_year == 1997)][0],
                  "seated_by"] = "Elected"
            return d
        return patched
    err = breaks(board_roster, "election_terms", mangle, build=board_roster.build)
    assert err and "seated_by must be one of" in err, f"not caught: {err}"


def test_prose_in_the_name_column_is_rejected():
    """A sentence carried through the name column as a person."""
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
    """An attributed name that is a near-miss for a roster name."""
    def rename(d):
        d.loc[d.name == "Ellen Bozman", "name"] = "Bozman"
        return d
    err = breaks(board_members.pd, "read_csv",
                 patch_csv(board_members, lambda d: "basis" in d.columns, rename),
                 build=board_members.build)
    assert err and "not in the roster" in err, f"not caught: {err}"


def test_two_sources_disagreeing_on_race_is_a_finding():
    """Two sources naming a different race for one person."""
    def contradict(d):
        extra = d[d.name == "William A. Rowe"].iloc[[0]].copy()
        extra["race"] = "White"
        return pd.concat([d, extra], ignore_index=True)
    err = breaks(board_members.pd, "read_csv",
                 patch_csv(board_members, lambda d: "basis" in d.columns, contradict),
                 build=board_members.build)
    assert err and "disagree" in err, f"not caught: {err}"


def test_party_must_account_for_the_same_seats():
    """One term with a party the seat table has no column for."""
    def mangle(orig):
        def patched(members):
            d = orig(members).copy()
            d.loc[d.index[d.year == 1975][0], "party"] = "whig"
            return d
        return patched
    err = breaks(board_seats, "months_held", mangle)
    assert err and "party does not account" in err, f"not caught: {err}"


def test_an_unknown_party_label_stops_the_build():
    """A county party label the build has never seen."""
    def mangle(orig):
        def patched():
            labels = orig()
            labels[("bozman", 1993)]["labels"] = {"X"}
            return labels
        return patched
    err = breaks(board_members, "county_labels", mangle, build=board_members.build)
    assert err and "label (X)" in err, f"not caught: {err}"


def test_reporting_cannot_overrule_a_party_the_county_prints():
    """Reporting that contradicts a party the county prints."""
    def contradict(d):
        extra = d.iloc[[0]].copy()
        extra["name"], extra["start_year"], extra["party"] = "Mary Margaret Whipple", 1983, "Republican"
        return pd.concat([d, extra], ignore_index=True)
    err = breaks(board_members.pd, "read_csv",
                 patch_csv(board_members, lambda d: {"quote", "party"} <= set(d.columns), contradict),
                 build=board_members.build)
    assert err and "county lists (D)" in err, f"not caught: {err}"


def test_a_citekey_with_no_bibliography_entry_is_rejected():
    """A source cell naming no entry in sources.bib."""
    try:
        citekeys.check(["novack1994 p.4", "oleary2O10 p.6"], "board_members.csv")
        err = None
    except AssertionError as e:
        err = str(e)
    assert err and "oleary2O10" in err, f"not caught: {err}"


def test_a_placeholder_is_allowed_and_counted():
    """The placeholders pass, and come back counted."""
    counts = citekeys.check(
        [citekeys.ASSUMED, citekeys.ASSUMED, citekeys.UNSOURCED], "x.csv")
    assert counts[citekeys.ASSUMED] == 2, counts
    assert counts[citekeys.UNSOURCED] == 1, counts


# --- guards on the turnout series ---------------------------------------------

def test_more_board_voters_than_registered_voters_is_rejected():
    """A year's registration smaller than its Board vote."""
    def mangle(orig):
        def patched():
            r = orig()
            r.loc[r.year == 2020, "registered"] = 100000
            return r
        return patched
    err = breaks(turnout, "registration", mangle)
    assert err and "registered" in err and "2020" in err, f"not caught: {err}"


def test_more_board_voters_than_presidential_voters_is_rejected():
    """A year's Board vote larger than its presidential vote."""
    def mangle(orig):
        def patched(roster):
            b = orig(roster)
            b.loc[b.year == 1972, "board_votes"] *= 2
            return b
        return patched
    err = breaks(turnout, "board_county", mangle)
    assert err and "presidential" in err and "1972" in err, f"not caught: {err}"


def test_registration_refuses_a_locality_total_that_is_not_its_precincts():
    """A locality total that is not the sum of the locality's precincts."""
    head = ("Locality,PrecinctCode,PrecinctName,ActiveVoters,InactiveVoters,AllVoters,"
            "TotalPrecinctsInLocality,TotalActiveVotersPrecinctLocality,"
            "TotalInActiveVotersPrecinctLocality,TotalAllVotersPrecinctLocality,"
            "TotalActiveVotersLocality,TotalInActiveVotersLocality,TotalAllVotersLocality\n")
    good = head + ("Locality: 013 ARLINGTON COUNTY,0001,001 - A,100,10,110,2,250,25,275,5000,500,5500\n"
                   "Locality: 013 ARLINGTON COUNTY,0002,002 - B,150,15,165,2,250,25,275,5000,500,5500\n")
    row = registration.from_csv(good.encode(), "x.csv")
    assert row["all"] == 275, row
    bad = good.replace(",250,25,275,", ",5000,500,5500,")
    try:
        registration.from_csv(bad.encode(), "x.csv")
        err = None
    except SystemExit as e:
        err = str(e)
    assert err and "sum of Arlington's precincts" in err, f"not caught: {err}"


# --- the documentation names real files ---------------------------------------

def test_a_source_we_cannot_fully_cite_is_logged_as_a_question():
    """A bib entry marked provisional that docs/questions.csv does not name."""
    unlogged = [key for key, body in bib_entries()
                if re.search(r"PROVISIONAL|INCOMPLETE", body) and key not in questions()]
    assert not unlogged, (
        f"{', '.join(unlogged)}: the annotation says the entry is provisional, "
        f"but docs/questions.csv never names it. Log it as a question with an "
        f"owner, or finish the entry and drop the word.")


def test_every_source_with_a_url_is_filed():
    """A bib entry with a url that names no copy on file ("Filed in Drive
    as", or a path under data/raw/) and is not a logged question; or one
    that says it is not filed."""
    problems = []
    for key, body in bib_entries():
        if re.search(r"not\s+(?:yet\s+)?filed", body, re.I):
            problems.append(f"{key}: says it is not filed - file it in Drive and say so")
        has_url = re.search(r"^\s*url\s*=", body, re.M)
        held = "Filed in Drive as" in body or "data/raw/" in body
        if has_url and not held and key not in questions():
            problems.append(f"{key}: has a url but names no copy - add 'Filed in Drive as \"...\"' "
                            f"or the path under data/raw/, or log a question naming the key")
    assert not problems, "sources with no copy on file:\n  " + "\n  ".join(problems)


def test_docs_name_only_paths_that_exist():
    """A path named in the docs, the skill, sources.bib or the paper that
    does not exist. Markdown names paths in backticks; the bib and the
    .tex as bare words. Globs and placeholders are skipped."""
    tops = ("code/", "data/", "docs/", "figures/", "paper/", "style/")
    missing = []
    for doc in [*ROOT.glob("*.md"), *ROOT.glob("docs/*.md"), *ROOT.glob(".claude/skills/*/SKILL.md")]:
        for m in re.finditer(r"`([^`\n]+)`", doc.read_text()):
            token = m.group(1).strip().rstrip("/")
            if not token.startswith(tops) or any(c in token for c in "*<>{}"):
                continue
            if not (ROOT / token).exists():
                missing.append(f"{doc.relative_to(ROOT)}: `{token}`")
    for doc in [ROOT / "paper" / "sources.bib", ROOT / "paper" / "arlington-bsap.tex"]:
        for m in re.finditer(r"\b(?:code|data|docs|figures|paper|style)/[\w./-]+", doc.read_text()):
            token = m.group(0).rstrip(".,;)}")
            if any(c in token for c in "*<>{}"):
                continue
            if not (ROOT / token).exists():
                missing.append(f"{doc.relative_to(ROOT)}: {token}")
    assert not missing, "documentation names paths that do not exist:\n  " + "\n  ".join(missing)


def test_a_stale_input_table_is_refused():
    """A clean table older than the run's start."""
    os.environ["RUN_STARTED"] = str(2e10)
    try:
        paths.read("board_members")
        err = None
    except AssertionError as e:
        err = str(e)
    finally:
        del os.environ["RUN_STARTED"]
    assert err and "older than this run" in err, f"not caught: {err}"


def test_every_data_file_is_inventoried():
    """A file under data/ with no row in data/contents.csv, a row with no
    file (unless fetched on demand), or a raw file whose checksum has moved."""
    data = ROOT / "data"
    rows = {r["path"]: r for r in csv.DictReader((data / "contents.csv").open())}
    on_disk = {str(p.relative_to(ROOT)) for p in data.rglob("*")
               if p.is_file() and not p.name.startswith(".") and p.name != "contents.csv"}
    missing = sorted(on_disk - set(rows))
    gone = sorted(p for p in set(rows) - on_disk if rows[p]["in_git"] == "yes")
    assert not missing, "files under data/ with no row in data/contents.csv:\n  " + "\n  ".join(missing)
    assert not gone, "rows in data/contents.csv for files that do not exist:\n  " + "\n  ".join(gone)
    moved = [p for p, r in rows.items() if r["layer"] == "raw" and (ROOT / p).exists()
             and hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:16] != r["sha256"]]
    assert not moved, ("raw files whose checksum does not match data/contents.csv - data/raw/ "
                       "is never edited:\n  " + "\n  ".join(moved))


def test_docs_agree_with_run_sh():
    """A `pip install` line or an "N figures" in the docs that differs from
    run.sh."""
    run = (ROOT / "run.sh").read_text()
    install = re.search(r"pip install ([a-z0-9 ]+)", run).group(1).split()
    figures = re.search(r"FIGURES=\(([^)]*)\)", run, re.S).group(1).split()
    words = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}
    problems = []
    for doc in [ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / "docs" / "setup.md"]:
        text = doc.read_text()
        for m in re.finditer(r"pip install ([a-z0-9 ]+)", text):
            if m.group(1).split() != install:
                problems.append(f"{doc.name}: install line says {m.group(1).split()}, run.sh says {install}")
        for m in re.finditer(r"\b(\w+) figures\b", text):
            n = m.group(1).lower()
            if n in words.values() and n != words[len(figures)]:
                problems.append(f"{doc.name}: says '{n} figures', run.sh builds {len(figures)}")
    assert not problems, "docs disagree with run.sh:\n  " + "\n  ".join(problems)


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
