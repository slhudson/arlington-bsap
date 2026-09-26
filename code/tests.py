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
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import citekeys  # noqa: E402

# Each data stage has its own paths.py. The build stage's modules load
# first and keep theirs; the name is then cleared so the clean stage's can
# load under it.
sys.path.insert(0, str(ROOT / "code" / "build"))
import paths as build_paths  # noqa: E402
import board_claims  # noqa: E402
sys.path.remove(str(ROOT / "code" / "build"))
del sys.modules["paths"]

sys.path.insert(0, str(ROOT / "code" / "clean"))
import board_members  # noqa: E402
import paths  # noqa: E402
import board_roster  # noqa: E402
import board_roster_oleary  # noqa: E402
import board_roster_results  # noqa: E402
import board_terms  # noqa: E402
import board_seats  # noqa: E402
import residence_district  # noqa: E402
import residents  # noqa: E402
import turnout  # noqa: E402
import voters  # noqa: E402

# The fetch stage has a paths.py of its own too.
del sys.modules["paths"]
sys.path.insert(0, str(ROOT / "code" / "fetch"))
import registration  # noqa: E402
sys.path.remove(str(ROOT / "code" / "fetch"))
sys.modules["paths"] = paths


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


def patch_source(when, change):
    """A mangle for a build step's paths.source: `change` is applied to any
    frame for which `when(frame)` holds."""
    def mangle(orig):
        def patched(path, *a, **k):
            d = orig(path, *a, **k)
            return change(d) if when(d) else d
        return patched
    return mangle


def patch_claims(kind, change):
    """A mangle for the clean stage's paths.built: `change` is applied to
    the rows of data/built/board_claims.csv from one claim file, or to
    every row when `kind` is None."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem == "board_claims":
                rows = (d.claim == kind) if kind else pd.Series(True, index=d.index)
                d = pd.concat([d[~rows], change(d[rows].copy())], ignore_index=True)
            return d
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


def test_an_age_group_left_out_of_every_band_is_refused():
    """A Summary Tape File group that no band claims. The county total would
    still tie, because the missing people are simply never counted, so only
    the partition check sees it."""
    err = breaks(residents, "STF_AGE_GROUPS",
                 lambda orig: {**orig, 1980: {**orig[1980], "age25to34": ["25_29"]}})
    assert err and "do not cover the age groups exactly" in err, f"not caught: {err}"


def test_an_age_group_claimed_by_two_bands_is_refused():
    """The same group summed into two bands, which would inflate the adults."""
    err = breaks(residents, "STF_AGE_GROUPS",
                 lambda orig: {**orig, 1990: {**orig[1990],
                                              "age35to44": ["35_39", "40_44", "45_49"]}})
    assert err and "named in more than one band" in err, f"not caught: {err}"


def test_a_wrong_sex_by_age_cell_number_is_refused():
    """A cell dropped from the API's sex-by-age table. The bands must name
    every age cell the table has, 3 to 25; the tie to the table's own total
    stands behind that and would catch a cell counted as the wrong sex."""
    err = breaks(residents, "API_AGE_CELLS",
                 lambda orig: {**orig, "age25to34": [12]})
    assert err and "the table's age cells are 3 to 25" in err, f"not caught: {err}"


def test_the_two_counts_of_the_adult_population_must_agree():
    """residents.csv sums six bands out of the sex-by-age table; turnout.csv
    reads the 18-and-over table. Different tables, same census, same figure."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem == "residents":
                d = d.copy()
                d.loc[d.year == 2020, "age65plus"] = 0
            return d
        return patched
    err = breaks(turnout, "read", mangle)
    assert err and "the age bands in residents.csv give" in err, f"not caught: {err}"



def misread(line, by, columns):
    """A mangle for residents.table: one printed line of the 1970 age table
    read `by` too high in each of `columns`."""
    def mangle(orig):
        def patched(path):
            d = orig(path)
            if "table35" in path:
                d = d.copy()
                for c in columns:
                    d.loc[d.label == line, c] += by
            return d
        return patched
    return mangle


def test_a_transcribed_age_table_that_does_not_sum_to_its_total_is_refused():
    """A digit misread the same way in the total and male columns, so the
    line still cross-foots and the county total is untouched: only the
    printed lines summing to "All ages" can see it."""
    err = breaks(residents, "table", misread("35 to 39 years", 10, ["total", "male"]))
    assert err and "The transcription misreads a number" in err, f"not caught: {err}"


def test_an_age_line_whose_sexes_do_not_make_its_total_is_refused():
    """A digit misread in the total column alone."""
    err = breaks(residents, "table", misread("19 years", 100, ["total"]))
    assert err and "male and female do not make the printed total" in err, f"not caught: {err}"

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
    err = breaks(board_roster_results, "terms", mangle, build=board_roster.build)
    assert err and "at large" in err, f"not caught: {err}"


def test_the_seat_table_before_1932_does_not_depend_on_the_roster():
    """A member with a term in the middle of the years no source names.
    board_seats states those years itself, so adding people to the roster
    for them (board_terms.csv) must not move a seat-year. If the stated
    years were read from the roster instead, the surrounding years would
    read as unfilled and this member would appear in the race, gender
    and party columns."""
    stated = list(board_seats.NO_ROSTER_YEARS)
    assert stated == list(range(1912, board_terms.AT_LARGE_FROM)), f"stated years are {stated[0]}-{stated[-1]}"
    real = board_seats.build()
    read = board_seats.read

    def with_a_member(name):
        members = read(name)
        if name != "board_members":
            return members
        extra = members.iloc[[0]].copy()
        extra["held_from"], extra["held_to"] = 1925 * 12, 1926 * 12
        extra["race"], extra["gender"], extra["party"] = "Black", "woman", "Democratic"
        return pd.concat([members, extra], ignore_index=True)

    board_seats.read = with_a_member
    try:
        changed = board_seats.build()
    finally:
        board_seats.read = read
    before, after = (t[t.year.isin(stated)].reset_index(drop=True) for t in (real, changed))
    pd.testing.assert_frame_equal(before, after)


def test_a_term_that_does_not_say_how_it_began_is_rejected():
    """A seated_by value outside the four the roster defines."""
    def mangle(orig):
        def patched(earlier):
            d = orig(earlier).copy()
            d.loc[d.index[(d.district == "at large") & (d.start_year == 1997)][0],
                  "seated_by"] = "Elected"
            return d
        return patched
    err = breaks(board_roster_results, "terms", mangle, build=board_roster.build)
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
    err = breaks(board_roster_oleary, "terms", mangle, build=board_roster.build)
    assert err and "prose" in err, f"not caught: {err}"


def test_an_attributed_name_that_misses_the_roster_is_rejected():
    """An attributed name that is a near-miss for a roster name."""
    def rename(d):
        d.loc[d.name == "Ellen Bozman", "name"] = "Bozman"
        return d
    err = breaks(paths, "built", patch_claims("demographics", rename), build=board_members.build)
    assert err and "not in the roster" in err, f"not caught: {err}"


def test_words_with_no_category_are_refused():
    """A race, gender or party as a source words it that clean has no
    category for: the transcribed files keep the words, so a new phrasing has
    to be decided in code/clean/board_members.py before it counts."""
    def novel(d):
        d.loc[d.name == "William A. Rowe", "race_words"] = "a man of color"
        return d
    err = breaks(paths, "built", patch_claims("demographics", novel), build=board_members.build)
    assert err and "no single category" in err, f"not caught: {err}"


def test_a_candidate_party_word_with_no_category_is_refused():
    """A press or campaign source's own words for a County Board candidate's
    party since 2023 that CANDIDATE_PARTY_WORDS has no category for: the
    transcribed file keeps the words, so a new phrasing has to be decided in
    code/clean/voters.py before it counts."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem == "voters_party":
                d = d.copy()
                d.loc[d.name == "Bob Cambridge", "party_words"] = "Libertarian"
            return d
        return patched
    err = breaks(paths, "built", mangle, build=voters.build)
    assert err and "no category here" in err, f"not caught: {err}"


def test_two_sources_disagreeing_on_race_is_a_finding():
    """Two sources naming a different race for one person."""
    def contradict(d):
        extra = d[d.name == "William A. Rowe"].iloc[[0]].copy()
        extra["race_words"] = "former confederate soldier"
        return pd.concat([d, extra], ignore_index=True)
    err = breaks(paths, "built", patch_claims("demographics", contradict), build=board_members.build)
    assert err and "disagree" in err, f"not caught: {err}"


def test_an_age_that_makes_a_child_a_member_is_rejected():
    """A misread age (39 read as 10) that makes a member a child when first
    seated. The birth year is worked out in the clean stage, from the age
    and the date it was stated, so the check has to see it there."""
    def misread(d):
        d.loc[(d.name == "Harold J. Casto") & (d.age != ""), "age"] = "10"
        return d
    err = breaks(paths, "built", patch_claims("demographics", misread), build=board_members.build)
    assert err and "age when first seated" in err, f"not caught: {err}"


def test_an_age_without_the_date_it_was_stated_is_rejected():
    """An age is only a birth year with a date beside it; the transcribed
    file gives both and this stage does the subtraction."""
    def undated(d):
        d.loc[d.name == "Harold J. Casto", "age_date"] = ""
        return d
    err = breaks(paths, "built", patch_claims("demographics", undated), build=board_members.build)
    assert err and "no year in its date" in err, f"not caught: {err}"


def test_a_birth_year_written_beside_an_age_is_rejected():
    """The transcribed file records what was printed. A birth year worked
    out by the reader and keyed beside the age it came from is refused."""
    def worked_out(d):
        d.loc[d.name == "Harold J. Casto", "birth_year"] = "1924"
        return d
    err = breaks(paths, "built", patch_claims("demographics", worked_out), build=board_members.build)
    assert err and "both a birth year and an age" in err, f"not caught: {err}"


def test_a_census_row_that_does_not_name_what_was_checked_is_refused():
    """A census record read off an image that does not say whether the
    sheet or only the index was read."""
    def unchecked(d):
        d.loc[d.source == "census1950tillema", "checked"] = ""
        return d
    err = breaks(board_claims, "source",
                 patch_source(lambda d: "checked" in d.columns, unchecked),
                 build=board_claims.build)
    assert err and "what was checked" in err, f"not caught: {err}"


def test_a_place_read_only_from_the_index_is_refused():
    """A street taken from Ancestry's index with the sheet never read. The
    index misreads a street where it reads a race or a sex correctly, so a
    place it alone carries would put a member on a street that is not his."""
    def index_only(d):
        d.loc[d.source == "census1950kaul", "checked"] = "the index only"
        d.loc[d.source == "census1950kaul", "place"] = "N Nash St, house number 1101"
        return d
    err = breaks(board_claims, "source",
                 patch_source(lambda d: "checked" in d.columns, index_only),
                 build=board_claims.build)
    assert err and "without the sheet read" in err, f"not caught: {err}"


def test_a_census_record_keyed_into_a_claim_file_is_refused():
    """A demographics row citing a census record. The record belongs in
    board_census.csv as one row, and left in the claim file it would count
    beside the record's own row as a second source."""
    def stray(d):
        extra = d.iloc[[0]].copy()
        extra["source"] = "census1950tillema"
        return pd.concat([d, extra], ignore_index=True)
    err = breaks(board_claims, "source",
                 patch_source(lambda d: "birth_year" in d.columns and "checked" not in d.columns, stray),
                 build=board_claims.build)
    assert err and "belongs in board_census.csv" in err, f"not caught: {err}"


def test_a_census_race_with_no_category_is_refused():
    """A race the index prints that the build has no category for, which
    would otherwise drop the claim and leave the member to the default."""
    def uncoded(d):
        d.loc[d.source == "census1880allen", "race"] = "Negro"
        return d
    err = breaks(paths, "built", patch_claims("census", uncoded), build=board_members.build)
    assert err and "no category" in err, f"not caught: {err}"


def test_an_at_large_seat_gets_no_derived_district():
    """The residence-district assumption is for a magisterial district. An
    at-large seat names no place, so a district claim for it would be invented."""
    m = pd.DataFrame({"name": ["A", "B"], "district": ["Jefferson", "at large"],
                      "start_year": [1900, 1950], "start_month": [5, 1]})
    got = residence_district.district_claims(m)
    assert list(got.name) == ["A"] and list(got.place) == ["Jefferson District"], got
    assert (got.source == "derived").all() and (got.precision == "district").all()


# --- the build stage reshapes and never decides -------------------------------

def test_a_category_merged_in_the_build_stage_is_refused():
    """Two census race categories collapsed into one by a build step. That
    is a decision, and the stage refuses it; the same collapse in
    code/clean/board_census.py is where it belongs. Written to a scratch
    folder, so a broken guard cannot leave a collapsed table in data/built/."""
    build_paths._INPUTS.clear()
    honest = board_claims.build()
    assert not build_paths.lost(honest), build_paths.lost(honest)
    collapsed = honest.copy()
    collapsed.loc[collapsed.race == "Mulatto", "race"] = "Black"
    kept, build_paths.BUILT = build_paths.BUILT, Path(tempfile.mkdtemp())
    try:
        build_paths.write(collapsed, "board_claims")
        err = None
    except AssertionError as e:
        err = str(e)
    finally:
        build_paths.BUILT = kept
    assert err and "'race'" in err and "Mulatto" in err, f"not caught: {err}"


def test_the_clean_stage_has_no_route_above_built():
    """A name in code/clean/paths.py that points under data/raw/ or
    data/transcribed/, or an inventory row saying a clean step reads a file
    there. A source reaches the clean stage through a build step or not at all."""
    above = (ROOT / "data" / "raw", ROOT / "data" / "transcribed")
    routes = [n for n, v in vars(paths).items()
              if isinstance(v, Path) and any(v == a or a in v.parents for a in above)]
    assert not routes, f"code/clean/paths.py maps a path above data/built/: {routes}"
    direct = [r["path"] for r in csv.DictReader((ROOT / "data" / "contents.csv").open())
              if r["layer"] not in ("built", "clean") and "code/clean/" in r["read_by"]]
    assert not direct, ("data/contents.csv says a clean step reads these directly; give each a "
                        "build step:\n  " + "\n  ".join(direct))


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
        extra["name"], extra["start_year"], extra["party_words"] = "Mary Margaret Whipple", "1983", "Republicans"
        return pd.concat([d, extra], ignore_index=True)
    err = breaks(paths, "built", patch_claims("party", contradict), build=board_members.build)
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
    err = breaks(turnout, "board_votes", mangle)
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


def test_every_bib_entry_closes_before_the_next():
    """An entry whose closing brace is missing swallows the entry after it.
    bib_entries() still finds every key, so the other bib tests pass on a file
    code/archive.py refuses to parse; this is the check that would have
    caught the merge that dropped one."""
    swallowed = [key for key, body in bib_entries() if re.search(r"^@\w+\{", body, re.M)]
    assert not swallowed, f"no closing brace before the next entry: {swallowed}"


def test_every_source_with_a_url_is_filed():
    """A bib entry with a url that names no copy on file ("Filed in Drive
    as", or a path under data/raw/); or one that says it is not filed.
    Either is allowed only while docs/questions.csv names the key, so an
    entry that admits to holding no copy is tracked rather than rewritten
    into a claim that it is filed."""
    problems = []
    for key, body in bib_entries():
        if re.search(r"not\s+(?:yet\s+)?filed", body, re.I) and key not in questions():
            problems.append(f"{key}: says it is not filed - file it in Drive and say so, "
                            f"or log a question naming the key")
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
        for m in re.finditer(r"(?<![\w/.-])(?:code|data|docs|figures|paper|style)/[\w./-]+", doc.read_text()):
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


def test_the_inventory_names_what_reads_each_table():
    """A built or clean table whose read_by in data/contents.csv is not the
    scripts that read it: a clean step's built("x") or read("x"), or an
    analysis script's paths.NAME where code/analysis/paths.py maps NAME to
    x.csv. The inventory is the only place a reader is written down, and
    nothing else notices when one is added or dropped."""
    mapped = {m.group(2): m.group(1) for m in re.finditer(
        r'^(\w+) = CLEAN / "(\w+)\.csv"', (ROOT / "code" / "analysis" / "paths.py").read_text(), re.M)}

    def readers(layer, stem):
        found = []
        for script in sorted((ROOT / "code" / "clean").glob("*.py")):
            text = script.read_text()
            if (layer == "built" and f'built("{stem}")' in text) or (layer == "clean" and f'read("{stem}")' in text):
                found.append(str(script.relative_to(ROOT)))
        if layer == "clean":
            for script in sorted((ROOT / "code" / "analysis").glob("*.py")):
                if f"paths.{mapped[stem]}" in script.read_text():
                    found.append(str(script.relative_to(ROOT)))
        return "; ".join(found)

    problems = []
    for r in csv.DictReader((ROOT / "data" / "contents.csv").open()):
        if r["layer"] not in ("built", "clean"):
            continue
        got = readers(r["layer"], Path(r["path"]).stem)
        if got != r["read_by"]:
            problems.append(f"{r['path']}: read_by says {r['read_by']!r}; the scripts that read it: {got!r}")
    assert not problems, "data/contents.csv is out of date:\n  " + "\n  ".join(problems)


def test_docs_agree_with_run_sh():
    """A `pip install` line in the docs that differs from run.sh."""
    run = (ROOT / "run.sh").read_text()
    install = re.search(r"pip install ([a-z0-9 ]+)", run).group(1).split()
    problems = []
    for doc in [ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / "docs" / "setup.md"]:
        text = doc.read_text()
        for m in re.finditer(r"pip install ([a-z0-9 ]+)", text):
            if m.group(1).split() != install:
                problems.append(f"{doc.name}: install line says {m.group(1).split()}, run.sh says {install}")
    assert not problems, "docs disagree with run.sh:\n  " + "\n  ".join(problems)


def test_a_timeline_citation_reaches_the_footnote():
    """A \\autocite inside \\timeline while the preamble does not make tabular
    footnote-safe. LaTeX drops a footnote raised inside a tabular: the
    superscript prints and the note never appears, with no warning and a
    compile that succeeds. Six citations were lost that way before
    \\makesavenoteenv{tabular} was added, so the pairing is checked rather
    than trusted."""
    tex = (ROOT / "paper" / "arlington-bsap.tex").read_text()
    live = "\n".join(re.sub(r"(?<!\\\\)%.*", "", line) for line in tex.split("\n"))
    cited = len([m for m in re.finditer(r"\\timeline\{(.*?)\n\}", live, re.S)
                 if "autocite" in m.group(1)])
    tabular = re.search(r"\\newcommand\{\\timeline\}.*?\\end\{tabular\}", live, re.S)
    safe = re.search(r"\\makesavenoteenv\{tabular\}", live)
    assert not (cited and tabular and not safe), (
        f"{cited} timeline(s) cite a source inside a tabular, but the preamble "
        f"has no \\makesavenoteenv{{tabular}}: those footnotes are dropped "
        f"silently. Add \\usepackage{{footnote}} and \\makesavenoteenv{{tabular}}, "
        f"or move the citations into the prose.")


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
