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
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "sources"))
import archive  # noqa: E402
import citekeys  # noqa: E402
import clippings  # noqa: E402
import paper  # noqa: E402
import quotations  # noqa: E402

# Each data stage has its own paths.py. The build stage's modules load
# first and keep theirs; the name is then cleared so the clean stage's can
# load under it.
sys.path.insert(0, str(ROOT / "code" / "build"))
import paths as build_paths  # noqa: E402
import members_claims  # noqa: E402
import survey_satisfaction as build_survey_satisfaction  # noqa: E402
sys.path.remove(str(ROOT / "code" / "build"))
del sys.modules["paths"]
# Both stages have a step of this name, as they should: each is named for
# what it writes. The build one is kept under its own name so the clean
# one can load under the plain one.
del sys.modules["survey_satisfaction"]

sys.path.insert(0, str(ROOT / "code" / "clean"))
import candidates  # noqa: E402
import members_census  # noqa: E402
import members  # noqa: E402
import paths  # noqa: E402
import members_roster  # noqa: E402
import members_roster_arlhist  # noqa: E402
import members_roster_oleary  # noqa: E402
import members_roster_results  # noqa: E402
import members_by_year  # noqa: E402
import residents  # noqa: E402
import residents_by_district  # noqa: E402
import elections_turnout  # noqa: E402
import elections_results  # noqa: E402
import elections  # noqa: E402
import survey_satisfaction as clean_survey_satisfaction  # noqa: E402

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
    the rows of data/built/members_claims.csv from one claim file, or to
    every row when `kind` is None."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem == "members_claims":
                rows = (d.claim == kind) if kind else pd.Series(True, index=d.index)
                d = pd.concat([d[~rows], change(d[rows].copy())], ignore_index=True)
            return d
        return patched
    return mangle


def patch_built(stem, change):
    """A mangle for the clean stage's paths.built: `change` is applied to
    data/built/<stem>.csv as read."""
    def mangle(orig):
        def patched(name):
            d = orig(name)
            return change(d.copy()) if name == stem else d
        return patched
    return mangle


def candidacies_with(change):
    """The error candidates.build() raises with the built candidacy
    table changed, or None. The tests run before the clean stage, so the
    members.csv it reads is last run's: the run's start is set aside."""
    started = os.environ.pop("RUN_STARTED", None)
    try:
        return breaks(paths, "built", patch_built("candidates", change),
                      build=candidates.build)
    finally:
        if started:
            os.environ["RUN_STARTED"] = started


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


def districts_with(page, change):
    """The error residents_by_district.build() raises with one keyed-in
    table changed, or None. The tests run before the clean stage, so the
    residents.csv it checks against is last run's: the run's start is set
    aside."""
    def mangle(orig):
        def patched(path):
            d = orig(path)
            return change(d.copy()) if f"_p{page}_" in path else d
        return patched
    started = os.environ.pop("RUN_STARTED", None)
    try:
        return breaks(residents_by_district, "table", mangle)
    finally:
        if started:
            os.environ["RUN_STARTED"] = started


def test_a_misread_district_cell_is_refused():
    """The 1930 scan's 6 and 0 are hard to tell apart: Washington district
    read 5,606 for 5,666 still looks like a district."""
    def misread(d):
        d.loc[d.label == "Washington district", "pop_1930"] = 5606
        return d
    err = districts_with(1123, misread)
    assert err and "districts sum to" in err, f"not caught: {err}"


def test_a_district_race_split_that_misses_its_total_is_refused():
    """Jefferson's 1870 colored count misread, which moves its Black share
    and leaves every total tying."""
    def misread(d):
        d.loc[d.label == "Jefferson", "colored"] = 837
        return d
    err = districts_with(279, misread)
    assert err and "do not make its total" in err, f"not caught: {err}"


def test_a_wrong_enumeration_district_mapping_is_refused():
    """ED 12 read into Jefferson instead of Arlington. The county still ties,
    because the same people are counted either way, and both districts keep a
    Black share a reader would accept; only the check against the district
    totals the 1920 volume prints sees it."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem != "ipums":
                return d
            d = d.copy()
            d.loc[d.ed == "12", "district"] = "Jefferson"
            return d
        return patched
    started = os.environ.pop("RUN_STARTED", None)
    try:
        err = breaks(residents_by_district, "built", mangle)
    finally:
        if started:
            os.environ["RUN_STARTED"] = started
    assert err and "disagree about a district" in err, f"not caught: {err}"


def test_a_tolerance_too_wide_to_catch_a_move_is_refused():
    """TOO_FAR widened until an enumeration district could sit in the wrong
    magisterial district and still pass. The mapping written is still the
    right one, so every number would be correct and the check would have
    stopped doing anything, which nothing else would notice."""
    started = os.environ.pop("RUN_STARTED", None)
    try:
        err = breaks(residents_by_district, "TOO_FAR",
                     lambda orig: {y: 0.9 for y in orig})
    finally:
        if started:
            os.environ["RUN_STARTED"] = started
    assert err and "do not identify the mapping" in err, f"not caught: {err}"


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
    """residents.csv sums six bands out of the sex-by-age table; elections_turnout.csv
    reads the 18-and-over table. Different tables, same census, same figure."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem == "residents":
                d = d.copy()
                d.loc[d.year == 2020, "age65plus"] = 0
            return d
        return patched
    err = breaks(elections_turnout, "read", mangle)
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


def test_a_misread_adult_count_cannot_move_into_the_children_in_1930():
    """1930's under-18 band is the county less those 18 and over, so a
    misread count of men 21 and over moves people into the children and
    the county total still ties. The 1940 volume's own 1930 column prints
    21 and over again, and the two readings must agree."""
    def mangle(orig):
        def patched(path):
            d = orig(path)
            if "table13" in path:
                d = d.copy()
                d.loc[d.label == "Males 21 years old and over", "total"] += 100
            return d
        return patched
    err = breaks(residents, "table", mangle)
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
    err = breaks(members_by_year, "months_held", mangle)
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
    err = breaks(members_roster_results, "terms", mangle, build=members_roster.build)
    assert err and "at large" in err, f"not caught: {err}"


def test_the_seat_table_reads_the_roster_for_1912_to_1931():
    """The seat table derives 1912-1931 from the roster like every other year,
    arlhist1967officials naming all three magisterial seats for all twenty
    years. The silent failure this guards against is members_by_year.py
    stating the stretch itself again - three seats, held by white men,
    `assumed` - since a stretch no source names would then read as filled and
    nobody would see it. So every one of those years says `derived`, and a
    seat the roster stops naming stops the build."""
    stated = members_by_year.build()
    era = stated[stated.year.between(members_roster_arlhist.FIRST_YEAR,
                                     members_roster_arlhist.LAST_YEAR)]
    assert len(era) == 20 and (era.source == citekeys.DERIVED).all(), \
        f"1912-1931 is not derived from the roster: {sorted(set(era.source))}"

    def mangle(orig):        # the Arlington seat loses its 1928-31 holder, so
        # Ingram's term ends in January 1928 and February names nobody
        def patched():
            return [r for r in orig()
                    if not (r["district"] == "Arlington" and r["start_year"] == 1928)]
        return patched
    err = breaks(members_roster_arlhist, "rows", mangle, build=members_roster.build)
    assert err and "1928-02 Arlington" in err, f"not caught: {err}"


def test_a_term_that_does_not_say_how_it_began_is_rejected():
    """A seated_by value outside the four the roster defines."""
    def mangle(orig):
        def patched(earlier):
            d = orig(earlier).copy()
            d.loc[d.index[(d.district == "at large") & (d.start_year == 1997)][0],
                  "seated_by"] = "Elected"
            return d
        return patched
    err = breaks(members_roster_results, "terms", mangle, build=members_roster.build)
    assert err and "seated_by must be one of" in err, f"not caught: {err}"


def test_prose_in_the_name_column_is_rejected():
    """A sentence carried through the name column as a person. The member
    mangled is one no reading in members_roster_arlhist.py is keyed to, so
    what this catches is check_names and not a reading looking for a term
    that has moved."""
    def mangle(orig):
        def patched():
            for row in orig():
                if row["name"] == "Horatio Ball":
                    row = dict(row, name="Horatio Ball elected, but contested")
                yield row
        return patched
    err = breaks(members_roster_oleary, "terms", mangle, build=members_roster.build)
    assert err and "prose" in err, f"not caught: {err}"


def test_an_attributed_name_that_misses_the_roster_is_rejected():
    """An attributed name that is a near-miss for a roster name."""
    def rename(d):
        d.loc[d.name == "Ellen Bozman", "name"] = "Bozman"
        return d
    err = breaks(paths, "built", patch_claims("demographics", rename), build=members.build)
    assert err and "not in the roster" in err, f"not caught: {err}"


def test_words_with_no_category_are_refused():
    """A race, gender or party as a source words it that clean has no
    category for: the transcribed files keep the words, so a new phrasing has
    to be decided in code/clean/members.py before it counts."""
    def novel(d):
        d.loc[d.name == "William A. Rowe", "race_words"] = "a man of color"
        return d
    err = breaks(paths, "built", patch_claims("demographics", novel), build=members.build)
    assert err and "no single category" in err, f"not caught: {err}"


def test_a_candidate_party_word_with_no_category_is_refused():
    """A press or campaign source's own words for a County Board candidate's
    party since 2023 that CANDIDATE_PARTY_WORDS has no category for: the
    transcribed file keeps the words, so a new phrasing has to be decided in
    code/clean/elections_results.py before it counts."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem == "candidates_party":
                d = d.copy()
                d.loc[d.name == "Bob Cambridge", "party_words"] = "Libertarian"
            return d
        return patched
    err = breaks(paths, "built", mangle, build=elections_results.build)
    assert err and "no category here" in err, f"not caught: {err}"


def test_a_candidacy_on_two_source_pages_collapses_to_one_row():
    """The county's candidate history can print a County Board candidacy
    twice: a narrative of holdovers and incumbents, with no vote count, and
    a results table, with one - 1935's Chew, McShea, Yeatman and Ames are
    all printed both ways, and the two pages even disagree on the contest's
    exact date. Reintroducing that shape on a contest with no such
    duplicate today must still read as one candidacy, with the table's
    vote count, not two."""
    def duplicate(d):
        base = d[(d.year == "1989") & d.candidate.str.contains("Bozman")].iloc[0].to_dict()
        narrative = dict(base, page="999", election_date="November 6",
                         votes="", candidate="*Ellen Bozman (holdover)")
        return pd.concat([d, pd.DataFrame([narrative])], ignore_index=True)
    original = paths.built
    paths.built = patch_built("elections", duplicate)(original)
    try:
        c = elections.contests()
    finally:
        paths.built = original
    rows = c[(c.year == 1989) & (c.surname == "bozman")]
    assert len(rows) == 1, f"one candidacy on two pages became {len(rows)} rows: {list(rows.candidate)}"
    assert rows.votes.iloc[0] == 31780, f"the table's vote count was not kept: {rows.votes.iloc[0]}"
    assert "holdover" in rows.status.iloc[0], "the narrative page's own words were dropped"


def test_two_pages_disagreeing_on_a_candidacys_votes_is_refused():
    """Two pages naming the same candidate in the same contest with two
    different vote counts is not the same candidacy printed twice; it is a
    real disagreement, and nothing here should guess which page is right."""
    def contradict(d):
        base = d[(d.year == "1989") & d.candidate.str.contains("Bozman")].iloc[0].to_dict()
        second = dict(base, page="999", votes="1")
        return pd.concat([d, pd.DataFrame([second])], ignore_index=True)
    err = breaks(paths, "built", patch_built("elections", contradict), build=elections.contests)
    assert err and "different vote counts" in err, f"not caught: {err}"


def test_two_sources_disagreeing_on_race_is_a_finding():
    """Two sources naming a different race for one person."""
    def contradict(d):
        extra = d[d.name == "William A. Rowe"].iloc[[0]].copy()
        extra["race_words"] = "former confederate soldier"
        return pd.concat([d, extra], ignore_index=True)
    err = breaks(paths, "built", patch_claims("demographics", contradict), build=members.build)
    assert err and "disagree" in err, f"not caught: {err}"


def test_an_age_that_makes_a_child_a_member_is_rejected():
    """A misread age (39 read as 10) that makes a member a child when first
    seated. The birth year is worked out in the clean stage, from the age
    and the date it was stated, so the check has to see it there."""
    def misread(d):
        d.loc[(d.name == "Harold J. Casto") & (d.age != ""), "age"] = "10"
        return d
    err = breaks(paths, "built", patch_claims("demographics", misread), build=members.build)
    assert err and "age when first seated" in err, f"not caught: {err}"


def test_an_age_without_the_date_it_was_stated_is_rejected():
    """An age is only a birth year with a date beside it; the transcribed
    file gives both and this stage does the subtraction."""
    def undated(d):
        d.loc[d.name == "Harold J. Casto", "age_date"] = ""
        return d
    err = breaks(paths, "built", patch_claims("demographics", undated), build=members.build)
    assert err and "no year in its date" in err, f"not caught: {err}"


def test_a_birth_year_written_beside_an_age_is_rejected():
    """The transcribed file records what was printed. A birth year worked
    out by the reader and keyed beside the age it came from is refused."""
    def worked_out(d):
        d.loc[d.name == "Harold J. Casto", "birth_year"] = "1924"
        return d
    err = breaks(paths, "built", patch_claims("demographics", worked_out), build=members.build)
    assert err and "both a birth year and an age" in err, f"not caught: {err}"


def test_a_census_row_that_does_not_name_what_was_checked_is_refused():
    """A census record read off an image that does not say whether the
    sheet or only the index was read."""
    def unchecked(d):
        d.loc[d.source == "census1950tillema", "checked"] = ""
        return d
    err = breaks(members_claims, "source",
                 patch_source(lambda d: "checked" in d.columns, unchecked),
                 build=members_claims.build)
    assert err and "what was checked" in err, f"not caught: {err}"


def test_a_place_read_only_from_the_index_is_refused():
    """A street taken from Ancestry's index with the sheet never read. The
    index misreads a street where it reads a race or a sex correctly, so a
    place it alone carries would put a member on a street that is not his."""
    def index_only(d):
        d.loc[d.source == "census1950kaul", "checked"] = "the index only"
        d.loc[d.source == "census1950kaul", "place"] = "N Nash St, house number 1101"
        return d
    err = breaks(members_claims, "source",
                 patch_source(lambda d: "checked" in d.columns, index_only),
                 build=members_claims.build)
    assert err and "without the sheet read" in err, f"not caught: {err}"


def test_a_census_record_keyed_into_a_claim_file_is_refused():
    """A demographics row citing a census record. The record belongs in
    members_census.csv as one row, and left in the claim file it would count
    beside the record's own row as a second source."""
    def stray(d):
        extra = d.iloc[[0]].copy()
        extra["source"] = "census1950tillema"
        return pd.concat([d, extra], ignore_index=True)
    err = breaks(members_claims, "source",
                 patch_source(lambda d: "birth_year" in d.columns and "checked" not in d.columns, stray),
                 build=members_claims.build)
    assert err and "belongs in members_census.csv" in err, f"not caught: {err}"


def test_a_census_race_with_no_category_is_refused():
    """A race the index prints that the build has no category for, which
    would otherwise drop the claim and leave the member to the default."""
    def uncoded(d):
        d.loc[d.source == "census1880allen", "race"] = "Negro"
        return d
    err = breaks(paths, "built", patch_claims("census", uncoded), build=members.build)
    assert err and "no category" in err, f"not caught: {err}"


def test_a_census_record_matched_on_the_name_alone_feeds_nothing():
    """A census row whose match is `none` stays in the table but gives the
    member no birth year, race, gender or place; without this a doubtful
    match would put a stroke on members_age."""
    def weak(d):
        d.loc[d.source == "census1950tillema", "match"] = "none"
        return d
    original = paths.built
    paths.built = patch_claims("census", weak)(original)
    try:
        m = members.build()
        places = members_census.residences()
    finally:
        paths.built = original
    t = m[m.name == "John A. Tillema"].iloc[0]
    assert t.birth_year_source != "census1950tillema" and "census1950tillema" not in t.race_source, t
    assert not (places.source == "census1950tillema").any()


def test_a_census_match_with_no_category_is_refused():
    """A `match` value the clean stage does not list."""
    def novel(d):
        d.loc[d.source == "census1950tillema", "match"] = "same street"
        return d
    err = breaks(paths, "built", patch_claims("census", novel), build=members.build)
    assert err and "match with no category" in err, f"not caught: {err}"


def test_a_misreported_age_no_census_row_uses_is_refused():
    """A citekey in members_census.AGE_MISREPORTED that no census row cites.
    The list stops a misreported age from becoming a birth year, and a key
    that matches nothing would drop nothing and say nothing."""
    kept = members_census.AGE_MISREPORTED
    members_census.AGE_MISREPORTED = kept + ("census1910nobody",)
    try:
        err = breaks(paths, "built", lambda orig: orig, build=members.build)
    finally:
        members_census.AGE_MISREPORTED = kept
    assert err and "AGE_MISREPORTED names a record" in err, f"not caught: {err}"


def test_a_category_merged_in_the_build_stage_is_refused():
    """Two census race categories collapsed into one by a build step. That
    is a decision, and the stage refuses it; the same collapse in
    code/clean/members_census.py is where it belongs. Written to a scratch
    folder, so a broken guard cannot leave a collapsed table in data/built/."""
    build_paths._INPUTS.clear()
    honest = members_claims.build()
    assert not build_paths.lost(honest), build_paths.lost(honest)
    collapsed = honest.copy()
    collapsed.loc[collapsed.race == "Mulatto", "race"] = "Black"
    kept, build_paths.BUILT = build_paths.BUILT, Path(tempfile.mkdtemp())
    try:
        build_paths.write(collapsed, "members_claims")
        err = None
    except AssertionError as e:
        err = str(e)
    finally:
        build_paths.BUILT = kept
    assert err and "'race'" in err and "Mulatto" in err, f"not caught: {err}"


def test_the_clean_stage_has_no_route_above_built():
    """A name in code/clean/paths.py that points under data/raw/ or
    data/transcribed/. A source reaches the clean stage through a build step
    or not at all."""
    above = (ROOT / "data" / "raw", ROOT / "data" / "transcribed")
    routes = [n for n, v in vars(paths).items()
              if isinstance(v, Path) and any(v == a or a in v.parents for a in above)]
    assert not routes, f"code/clean/paths.py maps a path above data/built/: {routes}"


def test_party_must_account_for_the_same_seats():
    """One term with a party the seat table has no column for."""
    def mangle(orig):
        def patched(members):
            d = orig(members).copy()
            d.loc[d.index[d.year == 1975][0], "party"] = "whig"
            return d
        return patched
    err = breaks(members_by_year, "months_held", mangle)
    assert err and "party does not account" in err, f"not caught: {err}"


def test_an_unknown_party_label_stops_the_build():
    """A county party label the build has never seen."""
    def mangle(orig):
        def patched():
            labels = orig()
            labels[("bozman", 1993)]["labels"] = {"X"}
            return labels
        return patched
    err = breaks(members, "county_labels", mangle, build=members.build)
    assert err and "label (X)" in err, f"not caught: {err}"


def test_reporting_cannot_overrule_a_party_the_county_prints():
    """Reporting that contradicts a party the county prints."""
    def contradict(d):
        extra = d.iloc[[0]].copy()
        extra["name"], extra["start_year"], extra["party_words"] = "Mary Margaret Whipple", "1983", "Republicans"
        return pd.concat([d, extra], ignore_index=True)
    err = breaks(paths, "built", patch_claims("party", contradict), build=members.build)
    assert err and "county lists (D)" in err, f"not caught: {err}"


def test_a_citekey_with_no_bibliography_entry_is_rejected():
    """A source cell naming no entry in sources.bib."""
    try:
        citekeys.check(["novack1994 p.4", "oleary2O10 p.6"], "members.csv")
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
    err = breaks(elections_turnout, "registration", mangle)
    assert err and "registered" in err and "2020" in err, f"not caught: {err}"


def test_more_board_voters_than_presidential_voters_is_rejected():
    """A year's Board vote larger than its presidential vote."""
    def mangle(orig):
        def patched(roster):
            b = orig(roster)
            b.loc[b.year == 1972, "board_votes"] *= 2
            return b
        return patched
    err = breaks(elections_turnout, "board_votes", mangle)
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


# --- guards on Black candidacies ----------------------------------------------

def test_a_candidacy_that_matches_no_election_is_refused():
    """Monroe's special election keyed a year early. With no guard the
    figure would draw a loss in 1998, a year no record has him standing."""
    def move(d):
        d.loc[(d.name == "Charles P. Monroe") & (d.election == "special"), "year"] = "1998"
        return d
    err = candidacies_with(move)
    assert err and "matches no election record" in err, f"not caught: {err}"


def test_a_black_members_election_with_no_candidacy_is_refused():
    """Pendleton's 1883 row left out: his seat would still count in
    members_by_race, and this figure would show 1883 as a year nobody ran."""
    err = candidacies_with(lambda d: d[d.name != "John W. Pendleton"])
    assert err and "a term, no candidacy" in err, f"not caught: {err}"


def test_a_candidacy_inside_a_period_a_source_says_none_ran_is_refused():
    """Hjerpe's period keyed from 1880: it would then contain five
    elections Black members won, and the two claims cannot both stand."""
    def widen(d):
        d.loc[(d.name == "") & (d.source == "hjerpe2021"), "year"] = "1880"
        return d
    err = candidacies_with(widen)
    assert err and "says no Black candidate ran" in err, f"not caught: {err}"


def test_a_candidate_the_1931_list_marks_is_not_left_out():
    """Moseley's rows left out, which no count would notice: the list still
    marks him "(Col)", so the build stops."""
    err = candidacies_with(lambda d: d[~((d.claim == "candidacy") & (d.name == "Moseley, C. H."))])
    assert err and "the 1931 list marks" in err, f"not caught: {err}"


# --- the numbers the prose cites ------------------------------------------------

def body_text_numbers():
    """(name, value, the rest of the line) for each command
    paper/body_text_numbers.tex defines."""
    tex = (ROOT / "paper" / "body_text_numbers.tex").read_text()
    return re.findall(r"^\\newcommand\{\\(\w+)\}\{([^}]*)\}(.*)$", tex, re.M)


def test_a_body_text_number_is_the_clean_tables_number():
    """A value in paper/body_text_numbers.tex that is not the share its clean
    table gives, worked out here separately: a hand edit, a rounding change,
    or a file left from before the table moved."""
    words = {1870: "EighteenSeventy", 1880: "EighteenEighty", 1890: "EighteenNinety",
             1900: "NineteenHundred", 1910: "NineteenTen", 1920: "NineteenTwenty",
             1930: "NineteenThirty"}

    def rounded(part, whole):          # a whole per cent, halves up
        return str((200 * int(part) + int(whole)) // (2 * int(whole)))

    d = pd.read_csv(ROOT / "data" / "clean" / "residents_by_district.csv")
    expected = {}
    for r in d.itertuples():
        county = d.loc[d.year == r.year, "total"].sum()
        expected[f"share{r.district}{words[r.year]}"] = rounded(r.total, county)
        if pd.notna(r.black):
            expected[f"blackShare{r.district}{words[r.year]}"] = rounded(r.black, r.total)

    m = pd.read_csv(ROOT / "data" / "clean" / "members.csv").drop_duplicates(subset="name")
    expected["genderCensusShareMembers"] = rounded(m.gender_source.str.contains("census").sum(), len(m))
    expected["raceAssumedShareMembers"] = rounded((m.race_source == "assumed").sum(), len(m))

    wrong = [f"\\{name} is {value}, the table gives {expected.get(name, 'nothing')}"
             for name, value, _ in body_text_numbers() if expected.get(name) != value]
    assert not wrong, "paper/body_text_numbers.tex:\n  " + "\n  ".join(wrong)


# --- the documentation names real files ---------------------------------------

def test_a_source_we_cannot_fully_cite_is_logged_as_a_question():
    """A bib entry marked provisional that docs/questions.csv does not name."""
    unlogged = [key for key, body in bib_entries()
                if re.search(r"PROVISIONAL|INCOMPLETE", body) and key not in questions()]
    assert not unlogged, (
        f"{', '.join(unlogged)}: the annotation says the entry is provisional, "
        f"but docs/questions.csv never names it. Log it as a question with an "
        f"owner, or finish the entry and drop the word.")


def tracker_rows():
    """docs/questions.csv as dictionaries, one per open question."""
    return list(csv.DictReader((ROOT / "docs" / "questions.csv").open(newline="")))


def slug_references():
    """Every place outside the tracker that names a row, as (slug, file).

    A write-up names one in backticks. Code names one in a parenthesis or
    ahead of "in docs/questions.csv", and that narrower shape is what keeps
    the census's own sex-by-age and race-by-18-and-over tables from reading
    as slugs."""
    slug = r"[a-z][a-z0-9]*(?:-[a-z0-9]+){2,}"
    found = []
    for path in sorted((ROOT / "docs").glob("*.md")):
        found += [(t, f"docs/{path.name}")
                  for t in re.findall(rf"`({slug})`", path.read_text())]
    for path in sorted((ROOT / "code").rglob("*.py")):
        found += [(t, f"code/{path.name}") for t in re.findall(
            rf"({slug})(?=\)| in docs/questions\.csv)", path.read_text())]
    return found


def test_a_row_that_closes_takes_its_references_with_it():
    """A slug named in docs/ or code/ that no row answers to.

    Closing a row deletes it, and the prose pointing at it sits in another
    file. docs/members.md went on calling two spellings unsettled for a day
    after the row tracking them had been rewritten to settle one, because
    the commit that rewrote the row never opened the write-up."""
    rows = {r["id"] for r in tracker_rows()}
    dangling = sorted({f"{slug} in {where}" for slug, where in slug_references()
                       if slug not in rows})
    assert not dangling, (
        "no row in docs/questions.csv answers to:\n  " + "\n  ".join(dangling) +
        "\nA row that closes leaves its prose behind. Say in the write-up what "
        "settled the question, or put the row back.")


def test_a_row_does_not_describe_work_in_flight():
    """A row reporting a search under way rather than what would settle it.

    A thread ends and the row outlives it. roster-walker-end-date said the
    Alexandria Gazette was "being searched for in another thread" for a day
    after that search had finished and filed two citekeys, so the next
    session read finished work as still running."""
    flight = re.compile(r"being searched|in another thread|in progress|under ?way",
                        re.I)
    stale = []
    for row in tracker_rows():
        hit = flight.search(" ".join(v for v in row.values() if v))
        if hit:
            stale.append(f'{row["id"]}: "{hit.group(0)}"')
    assert not stale, (
        "docs/questions.csv describes work in flight:\n  " + "\n  ".join(stale) +
        "\nA row says what would settle the question and what has already been "
        "searched and come back empty. Who is doing it now belongs nowhere: "
        "the thread ends and the row stays.")


def residence_coverage():
    """The coverage table docs/members.md prints: for the members first seated
    from 1932 on, the most exact kind of place any source gives each, and how
    close to his service the best-dated row of that kind is. The rule is the
    one the write-up states beside the table."""
    members = list(csv.DictReader((ROOT / "data/clean/members.csv").open(newline="")))
    places = list(csv.DictReader((ROOT / "data/clean/members_residence.csv").open(newline="")))
    terms, first = {}, {}
    for m in members:
        start, end = int(m["start_year"]), int(m["end_year"] or m["start_year"])
        terms.setdefault(m["name"], []).append((start, end))
        first[m["name"]] = min(first.get(m["name"], start), start)
    rows = {}
    for r in places:
        rows.setdefault(r["name"], []).append(r)

    order = ("address", "street", "neighborhood", "side", "district")
    when = ("Dated during service", "Within 5 years of it",
            "6 or more years from it", "Undated")

    def dating(name, row):
        if not row["year"]:
            return when[3]
        y = int(row["year"])
        if any(a <= y <= b for a, b in terms[name]):
            return when[0]
        off = min(min(abs(y - a), abs(y - b)) for a, b in terms[name])
        return when[1] if off <= 5 else when[2]

    table, nothing = {k: dict.fromkeys(when, 0) for k in order}, 0
    for name, start in first.items():
        if start < 1932:
            continue
        mine = rows.get(name, [])
        if not mine:
            nothing += 1
            continue
        kind = order[min(order.index(r["precision"]) for r in mine)]
        best = min((dating(name, r) for r in mine if r["precision"] == kind),
                   key=when.index)
        table[kind][best] += 1
    return {k: [v[w] for w in when] for k, v in table.items() if any(v.values())}, nothing


def district_shares():
    """The table docs/residents.md prints: each magisterial district's Black
    share at every census that gives race below the county, and the county's
    own from residents.csv. A district with no race split that year has no
    cell."""
    def share(row):
        return round(int(row["black"]) / int(row["total"]) * 100) if row["black"] else None
    out = {}
    for r in csv.DictReader((ROOT / "data/clean/residents_by_district.csv").open(newline="")):
        out[(r["district"], int(r["year"]))] = share(r)
    for r in csv.DictReader((ROOT / "data/clean/residents.csv").open(newline="")):
        out[("The county", int(r["year"]))] = share(r)
    return out


def test_the_district_share_table_in_the_write_up_is_current():
    """The table in docs/residents.md, "Race by district", read by hand off
    the clean tables. Two of its cells once disagreed with them, which nothing
    announced: a share in prose reads as current however old it is. So the
    build recomputes it, here, the way it does the residence coverage table."""
    text = (ROOT / "docs" / "residents.md").read_text()
    body = text.split("| District | 1870 |", 1)[1].split("\n\n", 1)[0]
    years = [int(y) for y in body.splitlines()[0].strip().strip("|").split("|") if y.strip()]
    years = [1870, *years]
    counted, printed, wrong = district_shares(), {}, []
    for line in body.splitlines()[2:]:
        cells = [c.strip(" *") for c in line.strip().strip("|").split("|")]
        for year, cell in zip(years, cells[1:]):
            printed[(cells[0], year)] = None if cell == "—" else int(cell.rstrip("%"))
    for key, value in printed.items():
        if counted.get(key) != value:
            wrong.append(f"{key[0]} {key[1]}: table {value}, clean {counted.get(key)}")
    assert printed and not wrong, ("docs/residents.md, \"Race by district\", does not "
                                  "match the clean tables:\n  " + "\n  ".join(wrong))


def test_the_residence_coverage_table_in_the_write_up_is_current():
    """The table in docs/members.md, "Where members lived", counted by hand.
    Every census read moves it, and a stale table is the kind of wrongness
    nothing else would announce: the numbers read as current and no build
    step touches them. So the count lives here and the build does it."""
    labels = {"Street address": "address", "Street name": "street",
              "Neighborhood": "neighborhood", "Side of the County": "side",
              "Magisterial district": "district"}
    text = (ROOT / "docs" / "members.md").read_text()
    body = text.split("| Most exact place held |", 1)[1].split("\n\n", 1)[0]
    printed, printed_nothing = {}, None
    for line in body.splitlines()[2:]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "Nothing":
            printed_nothing = int(cells[-1])
        elif cells[0] in labels:
            printed[labels[cells[0]]] = [int(c) for c in cells[1:5]]
    counted, nothing = residence_coverage()
    assert printed == counted and printed_nothing == nothing, (
        "docs/members.md, \"Where members lived\", does not count what the clean "
        f"tables hold.\n  table says: {printed}, nothing {printed_nothing}\n"
        f"  clean says: {counted}, nothing {nothing}")


def test_every_bib_entry_closes_before_the_next():
    """An entry whose closing brace is missing swallows the entry after it.
    bib_entries() still finds every key, so the other bib tests pass on a file
    code/sources/archive.py refuses to parse; this is the check that would have
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
        # Whitespace-tolerant: biblatex wraps an annotation anywhere, so a
        # literal match would fail an entry that names its copy across a line.
        held = re.search(r"Filed\s+in\s+Drive\s+as", body) or "data/raw/" in body
        # A page cited only for a count keeps no copy, on purpose: what it said
        # is keyed into data/transcribed/ with the date it was read, and that
        # file is the source a reviewer reads. The keyed file must be named, so
        # "no copy is kept" cannot stand on its own.
        if re.search(r"no\s+copy\s+is\s+kept", body) and "data/transcribed/" in body:
            held = True
        if has_url and not held and key not in questions():
            problems.append(f"{key}: has a url but names no copy - add 'Filed in Drive as \"...\"' "
                            f"or the path under data/raw/, or log a question naming the key")
    assert not problems, "sources with no copy on file:\n  " + "\n  ".join(problems)


def test_a_census_record_is_filed_as_one_whoever_indexed_it():
    """The FamilySearch record, reintroduced: the rule looked for Ancestry by
    name, so the one census page indexed elsewhere fell through to reports/
    and would have been filed as though a number were not read off it."""
    for who in ("Ancestry", "FamilySearch"):
        e = {"type": "online", "key": "planted", "title": "United States, Census, 1900",
             "organization": who}
        assert archive.kind(e) == "census", f"a {who} census record filed as {archive.kind(e)}"
        base = f"{who} 1900 - United States, Census, 1900.pdf"
        assert archive.subfolder("census", base) == f"census/{who}/1900", \
            f"{base} does not file by maker and year"



def a_legal_entry(key, annotation):
    """A one-entry bib naming a copy that is really on file, so a test can
    put words in its mouth. @jurisdiction is what archive.kind() files under
    legal/, which is the only kind this check reads."""
    return ("@jurisdiction{" + key + ",\n"
            "  title       = {Bennett v. Garrett},\n"
            "  annotation  = {" + annotation + "},\n}\n")


BENNETT = 'Filed in Drive as "legal/Supreme Court of Appeals of Virginia 1922 - Bennett v. Garrett.pdf"'


def test_a_quotation_the_document_does_not_contain_is_refused():
    """The Bennett misattribution, reintroduced: Rose's phrase written as
    the court's own. Nothing caught it for months because the opinion was
    filed in Drive all along and no one compared the two."""
    bib = a_legal_entry("planted", 'The court held that Arlington was "a continuous, '
                                   'contiguous, and homogeneous community". ' + BENNETT)
    missing, read = quotations.unsupported(bib)
    assert [q for _, q in missing] == ["a continuous, contiguous, and homogeneous community"], \
        f"a quotation that is not in the opinion was accepted: {missing}, {read} read"


def test_a_quotation_the_document_does_contain_passes():
    """The other half: the court's own words are not flagged, so the check
    is not simply refusing everything."""
    bib = a_legal_entry("planted", 'The court called Clarendon "a part only of a '
                                   'thickly settled community". ' + BENNETT)
    missing, read = quotations.unsupported(bib)
    assert not missing and read == 1, f"{missing}, {read} read"


def test_every_quotation_in_a_legal_source_is_in_the_copy_we_hold():
    """Every legal entry in the real bib, against the real copies."""
    missing, read = quotations.unsupported(archive.BIB.read_text())
    assert not missing, "quotations not in the document they are attributed to:\n  " + \
        "\n  ".join(f'{k}: "{q}"' for k, q in missing)
    assert read >= quotations.FEWEST, (
        f"only {read} quotations were read, fewer than the {quotations.FEWEST} this "
        f"check is known to cover: the copies or the annotations are not being found")



# --- where a web print stops --------------------------------------------------

# Pages of a press copy printed from a web page, as code/sources/clippings.py reads
# them: the article, then the site's own furniture.
ARTICLE = ("Zimmerman is the second-longest serving member of the board in the county's "
           "history, behind only Ellen Bozman, who served for 23 years.")
FOOTER_HEAD = ("ARLINGTON, VA Advertise Contact Us Email Newsletter Event Calendar "
               "Privacy & Other Policies Public Notices on ARLnow Readers' Choice")
FOOTER_TAIL = ("ALXnow (Alexandria) FFXnow (Fairfax Co.) MoCoShow (Montgomery Co., Md.) "
               "PoPville (Washington, D.C.) Potomac Local (Pr. Wm. & Stafford) RunWashington")


def test_a_footers_list_of_sister_sites_is_not_the_article():
    """The footer's own pages, reintroduced: its list of sister papers is as
    many words as a paragraph, so counting words alone keeps a page of links
    and the copy ends on the publisher's navigation."""
    assert clippings.article_pages([ARTICLE, FOOTER_HEAD, FOOTER_TAIL]) == 1


def test_an_article_that_shares_its_last_page_with_the_footer_is_kept():
    """The other half: the Connection prints its footer under the end of the
    article, and that page is the article's."""
    assert clippings.article_pages([ARTICLE, ARTICLE + " " + FOOTER_HEAD]) == 2


def test_a_signature_overleaf_stays_with_its_letter():
    """Tejada's resignation letter, reintroduced: "Sincerely," ends a page and
    the name is overleaf, three words on a page the word count would drop."""
    pages = [ARTICLE + " Please feel free to share this message as appropriate. Sincerely,",
             "J. Walter Tejada #Walter Tejada", FOOTER_HEAD]
    assert clippings.article_pages(pages) == 2


def test_an_event_promotion_is_not_the_article():
    """A page of nothing but the site's event promotion and the writer's
    biography, which read as prose until each block is removed."""
    page = ("Featured Event Shop the Boulevard Manor Neighborhood Yard Sale! 30+ Homes "
            "Participating! October 3, 2026 9:00 am-1:00 pm Read More About the Author "
            "ARLnow.com Launched in January 2010, ARLnow.com is the place for the latest "
            "news, views and things to do around Arlington, Virginia.")
    assert clippings.article_pages([ARTICLE, page, FOOTER_HEAD]) == 1



# --- how many other sessions are live in this checkout ------------------------

def a_checkout_and_sockets(tmp):
    """A throwaway repo carrying .claude/sessions.sh, and a directory to put
    session sockets in. Not a worktree: the counter answers only for a
    primary checkout, which is the only shared one."""
    root, socks = Path(tmp) / "repo", Path(tmp) / "socks"
    (root / ".claude").mkdir(parents=True)
    socks.mkdir()
    subprocess.run(["git", "init", "-q", "."], cwd=root, check=True)
    shutil.copy(ROOT / ".claude" / "sessions.sh", root / ".claude" / "sessions.sh")
    return root, socks


def a_session(socks, cwd, keep):
    """A process standing in for a Claude session working in cwd, with the
    socket the app opens for it. Returns its pid."""
    proc = subprocess.Popen(["sleep", "60"], cwd=cwd)
    s = socket.socket(socket.AF_UNIX)
    s.bind(str(Path(socks) / f"{proc.pid}.sock"))
    keep.append((proc, s))
    return proc.pid


def a_dead_session(socks, keep):
    """A socket left behind by a session that has gone."""
    proc = subprocess.Popen(["true"])
    proc.wait()
    s = socket.socket(socket.AF_UNIX)
    s.bind(str(Path(socks) / f"{proc.pid}.sock"))
    keep.append((None, s))
    return proc.pid


def others_here(root, socks, cwd=None):
    r = subprocess.run(["bash", ".claude/sessions.sh", "others"], cwd=cwd or root,
                       capture_output=True, text=True,
                       env={**os.environ, "CC_SOCKS": str(socks)})
    return r.returncode, r.stdout.split(), r.stderr


def close_all(keep):
    for proc, s in keep:
        s.close()
        if proc is not None:
            proc.kill()


def test_only_live_sessions_in_this_checkout_are_counted():
    """Both ways this counter has been wrong. It once reported nobody while
    three sessions worked here, and then reported six where four were live,
    because it read transcripts that outlast their session. A socket is held
    by a process or it is not: here one session has gone, one is working in
    another directory, and two are working in this checkout."""
    keep = []
    with tempfile.TemporaryDirectory() as tmp:
        root, socks = a_checkout_and_sockets(tmp)
        try:
            here = sorted(str(a_session(socks, root, keep)) for _ in range(2))
            a_session(socks, tmp, keep)          # live, working somewhere else
            a_dead_session(socks, keep)          # gone, socket left behind
            code, out, err = others_here(root, socks)
            assert code == 0 and sorted(out) == here, (code, out, err, here)
        finally:
            close_all(keep)


def test_the_session_that_asks_is_not_one_of_the_others():
    """The hooks run as children of the session asking, which must not be
    told about itself: SessionStart would warn about an empty checkout and
    pre-commit would refuse every commit."""
    keep = []
    with tempfile.TemporaryDirectory() as tmp:
        root, socks = a_checkout_and_sockets(tmp)
        here = os.getcwd()
        try:
            # This test process stands in for the session: it owns a socket
            # and, while chdir'd, is working in the checkout being asked about.
            os.chdir(root)
            s = socket.socket(socket.AF_UNIX)
            s.bind(str(socks / f"{os.getpid()}.sock"))
            keep.append((None, s))
            other = str(a_session(socks, root, keep))
            code, out, err = others_here(root, socks)
            assert code == 0 and out == [other], (code, out, err, other)
        finally:
            os.chdir(here)
            close_all(keep)


def test_sockets_that_cannot_be_found_stop_the_counter():
    """An empty answer and no answer must not look alike: that is how the
    first design hid for a month."""
    with tempfile.TemporaryDirectory() as tmp:
        root, _ = a_checkout_and_sockets(tmp)
        code, out, err = others_here(root, Path(tmp) / "gone")
        assert code != 0 and "cannot be answered" in err, (code, out, err)


def test_docs_name_only_paths_that_exist():
    """A path named in the docs, the skill, sources.bib or the paper that
    does not exist. Markdown names paths in backticks; the bib and the
    .tex as bare words. Globs and placeholders are skipped.

    So are paths git ignores. The docs name generated files on purpose -
    paper/arlington-bsap.pdf, the latexmk record beside it - and none of them
    exists in a fresh clone until something builds it. What this test is for is
    a path typed wrong or left behind by a rename, and those are tracked."""
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
    # Drop the ones git ignores, in one call rather than one per path.
    if missing:
        names = [m.split(": ", 1)[1].strip("`") for m in missing]
        ignored = subprocess.run(
            ["git", "check-ignore", "--stdin"], cwd=ROOT, text=True,
            input="\n".join(names), capture_output=True).stdout.split()
        missing = [m for m in missing
                   if m.split(": ", 1)[1].strip("`") not in set(ignored)]
    assert not missing, "documentation names paths that do not exist:\n  " + "\n  ".join(missing)


def test_a_stale_input_table_is_refused():
    """A clean table older than the run's start."""
    os.environ["RUN_STARTED"] = str(2e10)
    try:
        paths.read("members")
        err = None
    except AssertionError as e:
        err = str(e)
    finally:
        del os.environ["RUN_STARTED"]
    assert err and "older than this run" in err, f"not caught: {err}"


def test_every_data_file_is_inventoried():
    """A file under data/ with no row in data/contents.csv, a row with no
    file (unless fetched on demand), a file with two rows, or a raw file
    whose checksum has moved."""
    data = ROOT / "data"
    listed = [r["path"] for r in csv.DictReader((data / "contents.csv").open())]
    twice = sorted({p for p in listed if listed.count(p) > 1})
    assert not twice, "files with two rows in data/contents.csv:\n  " + "\n  ".join(twice)
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


def test_a_paper_build_that_lost_something_is_refused():
    """Each symptom latexmk reports while still exiting 0.

    All three leave a PDF that reads as finished: the citation case strips
    every footnote when bibtex runs where biber was needed, the reference case
    points the prose at no figure, and the font case sets the report's case
    names in a substituted face, which is what shipped once. One test, because
    they are one guard - a table of patterns - and three tests of three regexes
    would say nothing the first does not.
    """
    for log, expected in [
        ("LaTeX Warning: Citation 'samuel2026' on page 3 undefined on "
         "input line 154.", "samuel2026"),
        ("LaTeX Warning: Reference `fig:board-gender' on page 6 undefined "
         "on input line 286.", "fig:board-gender"),
        ("LaTeX Font Warning: Font shape `TU/Lato(0)/m/it' undefined",
         "style/fonts/"),
    ]:
        found = paper.problems(log)
        assert found, f"a good build, said the log: {log!r}"
        assert expected in found[0], (expected, found)


def test_a_clean_paper_log_passes():
    """A guard that fires on a good build gets ignored, so check it is quiet."""
    log = ("This is LuaHBTeX, Version 1.18.0\nOutput written on "
           "arlington-bsap.pdf (14 pages).\n")
    assert paper.problems(log) == [], paper.problems(log)


def test_a_second_empty_row_among_the_survey_responses_is_refused():
    """A blank row below the heading is a spacer; a second one is a
    respondent whose answers went missing, and dropping both silently
    would shorten the file by one with nothing to show for it."""
    mangle = patch_source(lambda d: "language" in d.columns,
                          lambda d: pd.concat([d, d.iloc[[0]]], ignore_index=True))
    err = breaks(build_survey_satisfaction, "source", mangle)
    assert err and "expected one empty row" in err, f"not caught: {err}"


def test_a_survey_file_of_the_wrong_length_is_refused():
    """A response file that is not the one zilo2026 counts. Every topline
    here is checked against the published report, so reading a different
    extract would move every number with nothing to say it had."""
    mangle = patch_source(lambda d: "language" in d.columns, lambda d: d.iloc[:-1])
    err = breaks(build_survey_satisfaction, "source", mangle)
    assert err and "not the one the report describes" in err, f"not caught: {err}"


def test_a_survey_item_matching_two_headings_is_refused():
    """The instrument heads the race write-in and its comment field almost
    alike, and six other questions repeat a stem. Matching an item on a
    phrase that reaches two of them would read the wrong column and say
    nothing."""
    stem = "Which of the following best describes your race or ethnicity? "
    frame = pd.DataFrame({stem + "8. Other (please specify)": [""],
                          stem + "8. Other (please specify) Comments": [""]})
    try:
        clean_survey_satisfaction.column(frame, "8. Other (please specify)")
    except AssertionError as e:
        assert "matches 2 headings" in str(e), e
    else:
        raise AssertionError("not caught: a phrase matching two headings was accepted")


def test_a_hispanic_respondent_naming_another_race_stays_hispanic():
    """The census publishes race and Hispanic origin crossed, Hispanic of
    any race first, and data/clean/residents.csv carries that crossing
    (docs/residents.md). Reading the boxes in instrument order instead
    would put 42 of the survey's Hispanic respondents under another race
    and leave the two tables uncomparable, with both still summing."""
    stem = "Which of the following best describes your race or ethnicity? "
    boxes = {stem + "1. Asian": "", stem + "2. Black or African American": "",
             stem + "3. Hispanic or Latino": "", stem + "4. Native American or Alaska Native": "",
             stem + "5. White": "", stem + "6. Native Hawaiian or Pacific Islander": "",
             stem + "7. Prefer not to respond": "",
             stem + "8. Other (please specify)": ""}
    def respondent(**checked):
        row = dict(boxes)
        for k, v in checked.items():
            row[[c for c in row if k in c][0]] = v
        return row
    frame = pd.DataFrame([
        respondent(**{"3. Hispanic": "x", "5. White": "x"}),
        respondent(**{"5. White": "x"}),
        respondent(**{"2. Black": "x", "5. White": "x"}),
        respondent(**{"7. Prefer not": "x"}),
        respondent(),
    ])
    got = list(clean_survey_satisfaction.race(frame))
    assert got == ["hispanic", "white", "other_or_multiracial", "declined", ""], got


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
