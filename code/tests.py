"""Tests that the build's guards still work.

    .venv/bin/python code/tests.py [word ...]    # words: only tests named with one

Each test reintroduces the specific mistake a guard exists to catch and
asserts the build stops. Only guards whose failure would be silent are
tested. No framework: plain functions named test_*, each building its own
input, run by the loop at the bottom.
"""
import contextlib
import csv
import hashlib
import importlib
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "sources"))
import archive  # noqa: E402
import cache  # noqa: E402
import citekeys  # noqa: E402
import cite  # noqa: E402
import clippings  # noqa: E402
import merge_questions  # noqa: E402
import paper  # noqa: E402
import publish  # noqa: E402
import quotations  # noqa: E402
import revisions  # noqa: E402


def stage(folder, *names):
    """The named modules of one stage, in the order asked.

    Each stage has a paths.py of its own and they cannot be merged
    (CLAUDE.md), so only one stage's folder is on the path at a time: it
    goes on, the modules load and bind the paths they see, and it comes off
    again. Every module loaded out of that folder is then dropped from the
    import cache, so a step of the same name in another stage - both stages
    have a survey_satisfaction, as they should, each named for what it
    writes - loads as its own module and not as this one's. The objects
    returned stay live, and a test that mangles one mangles the module the
    stage itself is holding.
    """
    here = str(ROOT / "code" / folder)
    sys.path.insert(0, here)
    try:
        return tuple(importlib.import_module(n) for n in names)
    finally:
        sys.path.remove(here)
        for name, module in list(sys.modules.items()):
            file = getattr(module, "__file__", None)
            if file and str(Path(file).parent) == here:
                del sys.modules[name]


(fetch_paths,) = stage("fetch", "paths")

(build_paths, members_claims, build_survey_satisfaction, build_census,
 build_localities) = stage(
    "build", "paths", "members_claims", "survey_satisfaction", "census",
    "localities")

(paths, candidates, census, members, members_census, members_chairs, members_by_year,
 members_roster, members_roster_arlhist, members_roster_oleary,
 members_roster_results, residents, residents_by_district, elections,
 elections_results, elections_turnout, clean_survey_satisfaction,
 clean_survey_rcv, localities, members_residence, localities_southeastern,
 elections_nominations, elections_margins, residents_by_district_adults,
 residents_by_district_boundaries) = stage(
    "clean", "paths", "candidates", "census", "members", "members_census", "members_chairs",
    "members_by_year", "members_roster", "members_roster_arlhist",
    "members_roster_oleary", "members_roster_results", "residents",
    "residents_by_district", "elections", "elections_results",
    "elections_turnout", "survey_satisfaction", "survey_rcv", "localities",
    "members_residence", "localities_southeastern", "elections_nominations",
    "elections_margins", "residents_by_district_adults",
    "residents_by_district_boundaries")

registration, = stage("fetch", "registration")


class NothingMangled(Exception):
    """A test's mangle left every input it was handed as it found it. Not an
    AssertionError or ValueError, so breaks() does not catch it as the build's
    refusal: it fails the test with this message instead of reading as
    "not caught"."""


def same(a, b):
    return a.equals(b) if hasattr(a, "equals") else a == b


def breaks(module, attr, mangle, build=None):
    """Run a build with one input mangled; return the error it raised, or None.

    The mangle must change something. A guard test that mangles nothing (its
    anchor row is missing from stale data, a filter matches no rows) would
    see the build pass and read as a guard that failed to fire; so a
    constant is compared with its mangled value, and for a function every
    value it hands the build is compared with what the original hands it. A
    run in which nothing differed raises NothingMangled."""
    original = getattr(module, attr)
    mangled = mangle(original)
    differed = []
    if callable(original):
        def watched(*a, **k):
            got = mangled(*a, **k)
            differed.append(not same(got, original(*a, **k)))
            return got
        planted = watched
    else:
        differed.append(not same(mangled, original))
        planted = mangled

    setattr(module, attr, planted)
    try:
        (build or module.build)()
        error = None
    except (AssertionError, ValueError) as e:
        error = str(e)
    finally:
        setattr(module, attr, original)
    if not any(differed):
        raise NothingMangled(
            f"{module.__name__}.{attr} was never handed anything the mangle changed "
            f"(error: {error}): stale data/built/, or the test's filter matches nothing")
    return error


def refusal(build):
    """The error a build raises as it stands, or None: for a test that has
    planted its mistake some other way and has nothing for breaks() to mangle."""
    try:
        build()
        return None
    except (AssertionError, ValueError) as e:
        return str(e)


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


def residents_reads(mangle):
    """The error code/clean/residents.py raises with one keyed-in census
    table mangled as it reads it, or None. The tables reach that step
    through census.keyed(), so that is where a misreading is planted."""
    return breaks(census, "keyed", mangle, build=residents.build)


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


def breaks_aside(module, attr, mangle, build=None):
    """breaks(), for a build step that reads a table the clean stage
    writes. The tests run before that stage, so the table it reads is last
    run's: the run's start is set aside."""
    started = os.environ.pop("RUN_STARTED", None)
    try:
        return breaks(module, attr, mangle, build=build or module.build)
    finally:
        if started:
            os.environ["RUN_STARTED"] = started


def bib_entries():
    """(key, body) for every entry in paper/bib/sources.bib."""
    bib = (ROOT / "paper" / "bib" / "sources.bib").read_text()
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
    err = residents_reads(mangle)
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
    err = residents_reads(mangle)
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
        return breaks(census, "keyed", mangle, build=residents_by_district.build)
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


def test_a_district_line_too_short_to_cross_the_county_is_refused():
    """A line in district_lines.csv edited (or misread) short enough that it
    no longer reaches the county's edge on both sides: the split then
    returns fewer than three pieces, since the county polygon is not cut
    all the way through."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem != "district_lines":
                return d
            d = d.copy()
            keep = d[(d.boundary != "washington_arlington") | (d.seq.astype(int).between(4, 8))]
            return keep.reset_index(drop=True)
        return patched
    err = breaks(residents_by_district_boundaries, "built", mangle,
                 build=residents_by_district_boundaries.areas)
    assert err and "not 3" in err, f"not caught: {err}"


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


def test_men_of_voting_age_cannot_be_everyone():
    """The age filter lost, so every man, woman and child is counted as a
    voter. The county still ties and the shares between races still look
    like a district's; only the share of the district that is men of voting
    age, a little under a third, is wrong, and the step checks it."""
    err = breaks_aside(residents_by_district_adults, "ADULT", lambda orig: 0)
    assert err and "not a plausible share" in err, f"not caught: {err}"


def test_adult_men_cannot_be_placed_differently_from_the_race_table():
    """ED 12 read into Jefferson for the adults and not for the race table.
    Each table would tie to itself; only the head count the two share sees
    that they no longer place the same people in the same district."""
    err = breaks_aside(residents_by_district_adults.rbd, "ED_READ_BY_HAND",
                       lambda orig: {**orig, 1920: {**orig[1920], "11": "Jefferson"}},
                       build=residents_by_district_adults.build)
    assert err and "place enumeration districts differently" in err, f"not caught: {err}"


def test_the_adults_county_is_only_written_where_every_district_is_whole():
    """1900's Arlington is short, so the county is not its three districts
    added up and the schedules write none; the volume's printed count stands
    for it, as it does for 1870, 1890 and 1930. A county the schedules do
    write is its three districts added, race by race."""
    started = os.environ.pop("RUN_STARTED", None)   # reads last run's race table
    try:
        d = residents_by_district_adults.build()
    finally:
        if started:
            os.environ["RUN_STARTED"] = started
    published = residents_by_district_adults.PUBLISHED
    for year, g in d.groupby("year"):
        county = g[g.district == "county"]
        if not county.empty:
            if year in published or year == 1930:   # the volume prints the county only
                continue
            parts = g[g.district != "county"][["men_white", "men_black", "men_other", "men_all",
                                               "women_white", "women_black", "women_other",
                                               "women_all"]].sum()
            assert (county.iloc[0][parts.index] == parts).all(), f"{year}: county is not its districts"


def test_the_adults_county_is_counted_at_every_census_from_1870_to_1930():
    """The turnout figure divides by this table's county men and, between
    two censuses, draws a straight line. A census with no count in it is a
    line across a decade nothing recorded: the figure was interpolating
    across 1880-1910 until 1870, 1890 and 1900 were keyed in from the
    volumes, and one of the three going missing again would still draw a
    plausible line. Every census from 1870 to 1930 must have a county row
    with a counted number of men."""
    started = os.environ.pop("RUN_STARTED", None)
    try:
        d = residents_by_district_adults.build()
    finally:
        if started:
            os.environ["RUN_STARTED"] = started
    county = d[d.district == "county"].set_index("year").men_all
    missing = [y for y in range(1870, 1931, 10) if y not in county.index or pd.isna(county[y])]
    assert not missing, f"no counted men in the county at the census of {missing}"


def test_the_adults_women_and_men_make_the_adults():
    """The women columns added beside the men. Each sex's races must sum to
    its total, and men plus women must make `adults_all`, in every row the
    schedules count and in the county rows the volumes print, where only the
    men's total (1930: the women's too) is there."""
    started = os.environ.pop("RUN_STARTED", None)
    try:
        d = residents_by_district_adults.build()
    finally:
        if started:
            os.environ["RUN_STARTED"] = started
    counted = d[d.source.str.startswith(citekeys.IPUMS_FULL_COUNT)]
    assert (counted[["women_white", "women_black", "women_other"]].sum(axis=1) == counted.women_all).all()
    assert (counted[["men_white", "men_black", "men_other"]].sum(axis=1) == counted.men_all).all()
    both = d[d.women_all.notna()]
    assert (both.adults_all == both.men_all + both.women_all).all()
    assert d[d.women_all.isna()].adults_all.isna().all(), "adults counted where the women are not"
    assert d[(d.year == 1930) & (d.district == "county")].shape[0] == 1, "1930 has no county row"


def test_a_sex_code_other_than_one_or_two_is_refused():
    """A third sex code in the schedules: its adults would be counted in
    neither the men's columns nor the women's, and every total would still
    tie to itself."""
    err = breaks_aside(residents_by_district_adults, "SEXES", lambda orig: {"1": "men"},
                       build=residents_by_district_adults.build)
    assert err and "counted in neither column" in err, f"not caught: {err}"


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
    """A mangle for census.keyed, which is how code/clean/residents.py reads
    a keyed-in volume table: one printed line of the 1970 age table read
    `by` too high in each of `columns`."""
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
    err = residents_reads(misread("35 to 39 years", 10, ["total", "male"]))
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
    err = residents_reads(mangle)
    assert err and "The transcription misreads a number" in err, f"not caught: {err}"

def test_an_age_line_whose_sexes_do_not_make_its_total_is_refused():
    """A digit misread in the total column alone."""
    err = residents_reads(misread("19 years", 100, ["total"]))
    assert err and "male and female do not make the printed total" in err, f"not caught: {err}"

def test_a_county_table_with_a_second_row_is_refused_when_it_is_read():
    """A county-level table built with another county's row ahead of
    Arlington's. census.row() would take the first row, and every figure
    reading that volume would show a neighbouring county's population."""
    table = census.names("us_census_bureau/*/stf1a_*_virginia_counties.csv")[0]

    def mangle(orig):
        def patched():
            c = orig()
            one = c[c.table == table]
            shifted = one.assign(row=one.row.astype(int) + 1)
            stray = one.assign(value="1")
            return pd.concat([c[c.table != table], stray, shifted], ignore_index=True)
        return patched
    err = breaks(census, "cells", mangle, build=lambda: census.row(table))
    assert err and "expected Arlington's one row" in err, f"not caught: {err}"


def test_a_county_file_naming_arlington_twice_is_refused_when_it_is_built():
    """A Bureau county file in which a second row begins with Arlington, as
    a repeated page would. Both rows would reach census.csv, and the census
    read in code/clean/ would take whichever came first."""
    def has_arlington(d):
        names = [c for c in d.columns if c.lower() == "name"]
        return bool(names) and d[names[0]].str.strip().str.upper().str.startswith("ARLINGTON").any()

    def repeat(d):
        name = next(c for c in d.columns if c.lower() == "name")
        arlington = d[d[name].str.strip().str.upper().str.startswith("ARLINGTON")]
        return pd.concat([d, arlington], ignore_index=True)
    err = breaks(build_census, "source", patch_source(has_arlington, repeat),
                 build=build_census.build)
    assert err and "expected one Arlington row" in err, f"not caught: {err}"


# --- guards on the Board files ----------------------------------------------

def test_race_and_gender_must_account_for_the_same_seats():
    """One term with a gender the seat table has no column for."""
    def mangle(orig):
        def patched(members, places):
            d = orig(members, places).copy()
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


def test_a_ruling_keyed_to_a_term_that_is_not_in_the_roster_is_refused():
    """A rename in members_roster_arlhist.py keyed to a district the member
    never sat in. With no guard it renames nothing, and the roster keeps
    O'Leary's spelling while the table says the article's was applied. The
    notes, seated dates and vacated dates match their rows the same way,
    so this one mangle stands for all of them."""
    def mangle(orig):
        return {**orig, ("Roach", "Washington"): orig[("Roach", "Jefferson")]}
    err = breaks(members_roster_arlhist, "NAMES", mangle, build=members_roster.build)
    assert err and "NAMES has no roster row to rename" in err, f"not caught: {err}"


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


def test_the_two_records_naming_different_2021_winners_are_refused():
    """The state's 2021 County Board winner renamed. With no guard the build
    keeps the county's winner for 2021 and the state's for every year after,
    so the roster joins two records that do not agree on who sat in 2022."""
    def mangle(orig):
        def patched(*a, **k):
            d = orig(*a, **k).copy()
            state = d[(d.record == "state") & (d.year == 2021) & d.person & ~d.primary & ~d.special]
            d.loc[state.votes.idxmax(), "name"] = "Nobody Else"
            return d
        return patched
    err = breaks(elections, "contests", mangle, build=members_roster_results.outcomes)
    assert err and "county and state sources disagree" in err, f"not caught: {err}"


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


def test_a_county_candidate_printed_with_two_labels_is_refused():
    """Magruder's 1939 line printed "(D) (R)". With no guard the sorted
    first label wins, and her 5,815 votes go to one party's column in
    elections_results with nothing to say the county printed two."""
    def mangle(orig):
        def patched(*a, **k):
            d = orig(*a, **k).copy()
            hit = d.candidate == "*Elizabeth B. Magruder (D)"
            d.loc[hit, "candidate"] = "*Elizabeth B. Magruder (D) (R)"
            return d
        return patched
    err = breaks(elections, "contests", mangle, build=elections_results.county_board)
    assert err and "more than one label" in err, f"not caught: {err}"


def test_a_presidential_year_with_neither_nominee_is_refused():
    """O'Leary's 1920 returns with the nominees' names changed. With no
    guard both nominees are zero and the whole vote lands in `other`, so
    the figure draws 1920 as a year nobody voted for either party."""
    def mangle(orig):
        def patched(kind, *a, **k):
            d = orig(kind, *a, **k)
            if kind == elections.PRESIDENT:
                d = d.assign(entry=d.entry.where(d.year != 1920,
                                                 d.entry.str.replace(r"Cox|Harding", "Nobody", regex=True)))
            return d
        return patched
    err = breaks(elections, "oleary", mangle, build=elections_results.oleary)
    assert err and "no line matched either nominee" in err, f"not caught: {err}"


def test_a_year_with_a_state_return_cannot_fall_back_to_oleary():
    """The state's return for 1888 dropped from the keyed rows. O'Leary
    prints 1888 too (407 Democratic, 314 Republican, against the state's 255
    and 462, which reverse the county's winner), so a build that took
    whatever source had the year would draw his count with nothing to say
    the return was missing. Only the years in OLEARY_ONLY take his."""
    def mangle(orig):
        def patched(*a, **k):
            d = orig(*a, **k)
            return d[d.year != 1888].reset_index(drop=True)
        return patched
    err = breaks_aside(elections, "state_return", mangle,
                       build=elections_results.presidential)
    assert err and "no state return keyed" in err, f"not caught: {err}"


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


def test_a_press_count_that_fills_no_blank_is_refused():
    """The Evening Star's 1949 counts fill the blanks the county's history
    leaves for Cox, DeLashmutt and Bechtel. A count whose candidate matches
    no blank of that election - a misspelt name, a wrong year - would sit
    unused while the year still read incomplete (or, worse, complete on the
    wrong man's votes), so the fill must stop instead of skipping it."""
    def misspell(d):
        d = d.copy()
        press = d.record == "press_return"
        # A stale data/built/ has no press rows; mangling none would read as
        # "not caught", so say what is wrong instead.
        assert press.any(), "data/built/elections.csv has no press_return rows: run the build"
        d.loc[press, "candidate"] = "Nobody Atall"
        return d
    def fill():
        c = elections.contests()
        return elections.filled_from_press(c[c.year == 1949])
    err = breaks(paths, "built", patch_built("elections", misspell), build=fill)
    assert err and "fills 0 blank county rows" in err, f"not caught: {err}"


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


def test_a_place_no_precision_rule_reads_is_refused():
    """A residence keyed as a place none of the rules in members_residence.py
    reads. With no guard the place is kept with no precision, and the
    coverage figure shades it as no kind of place at all."""
    def novel(d):
        d.loc[d.index[0], "place"] = "the old mill"
        return d
    err = breaks(paths, "built", patch_claims("residence", novel), build=members_residence.build)
    assert err and "no precision rule reads this place" in err, f"not caught: {err}"


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
        err = refusal(members.build)
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
    """A name in code/clean/paths.py that points under sources/ or
    data/transcribed/. A source reaches the clean stage through a build step
    or not at all."""
    above = (ROOT / "sources", ROOT / "data" / "transcribed")
    routes = [n for n, v in vars(paths).items()
              if isinstance(v, Path) and any(v == a or a in v.parents for a in above)]
    assert not routes, f"code/clean/paths.py maps a path above data/built/: {routes}"


def test_party_must_account_for_the_same_seats():
    """One term with a party the seat table has no column for."""
    def mangle(orig):
        def patched(members, places):
            d = orig(members, places).copy()
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


def test_two_sources_naming_different_parties_for_one_term_are_refused():
    """Massey's 1971 term given to the Republicans by a second source. With
    no guard the sorted first value wins, and the term is counted for
    whichever party sorts earlier in members_by_party."""
    def contradict(d):
        extra = d[d.name == "Howard R. Massey"].iloc[[0]].copy()
        extra["party_words"] = "Republicans"
        return pd.concat([d, extra], ignore_index=True)
    err = breaks(paths, "built", patch_claims("party", contradict), build=members.build)
    assert err and "sources disagree on party" in err, f"not caught: {err}"


def test_a_county_printing_two_labels_for_one_term_is_refused():
    """Bozman's 1993 election printed under both D and R. With no guard the
    alphabetically first label wins, and the term is counted for that party
    with no sign that the county printed two."""
    def mangle(orig):
        def patched():
            labels = orig()
            labels[("bozman", 1993)]["labels"] = {"D", "R"}
            return labels
        return patched
    err = breaks(members, "county_labels", mangle, build=members.build)
    assert err and "more than one label" in err, f"not caught: {err}"


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


def test_a_november_election_that_seats_more_than_five_is_refused():
    """The roster given six terms beginning after one November election.
    With no guard the year's seat count is six, and every per-seat figure
    for it is computed against a Board larger than five."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem == "members":
                crowd = d[(d.seated_by == "election") & (d.start_year == 1993)
                          & (d.start_month == 1)]
                d = pd.concat([d] + [crowd] * 5, ignore_index=True)
            return d
        return patched
    err = breaks_aside(elections_turnout, "read", mangle, build=elections_turnout.build)
    assert err and "a Board of five cannot fill that many" in err, f"not caught: {err}"


def test_no_district_election_with_a_count_in_every_district_is_refused():
    """The Gazette's supervisor counts stripped. With no guard 1870-1915 has
    no board_votes at all, and the turnout figure starts in 1931 with nothing
    to say the earlier series is missing."""
    def strip_gazette(orig):
        def patched(stem, *a, **k):
            d = orig(stem, *a, **k)
            return d.assign(votes="") if stem == "candidates_gazette" else d
        return patched

    err = breaks(elections_turnout.paths, "built", strip_gazette,
                 build=elections_turnout.board_districts)
    assert err and "no district election with a count in every district" in err, \
        f"not caught: {err}"


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


def test_a_term_counted_twice_in_the_roster_is_refused():
    """A pre-1931 term repeated in members.csv. A candidacy matching two
    terms would take the first, and its election would carry whichever
    source that row happens to name."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem == "members":
                rowe = d[(d["name"] == "William A. Rowe") & (d.start_year == 1872)]
                d = pd.concat([d, rowe], ignore_index=True)
            return d
        return patched
    err = breaks_aside(paths, "read", mangle, build=candidates.build)
    assert err and "terms in members.csv" in err, f"not caught: {err}"


def test_a_nomination_method_with_no_category_is_refused():
    """A press-keyed nomination whose method is a phrasing the clean step has
    no category for. The transcribed file keeps the source's words, so a new
    method has to be decided in code/clean/elections_nominations.py before
    it is counted in the by-year table."""
    def mangle(orig):
        def patched(stem):
            d = orig(stem)
            if stem == "elections_nominations":
                d = d.copy()
                d.loc[d.name == "Leo Lloyd", "method"] = "Whig caucus"
            return d
        return patched
    err = breaks(elections_nominations.paths, "built", mangle, build=elections_nominations.keyed)
    assert err and "not one the clean step knows" in err, f"not caught: {err}"


def test_a_wrong_seat_count_for_a_general_election_is_refused():
    """1939 filled five seats and the county prints "Vote for 1". Counting six
    puts the top Republican among the winners, and the margin shrinks to the
    gap between the Republicans with no sign; the roster did not seat him."""
    orig = dict(elections_margins.SEATS)
    elections_margins.SEATS["1939 November 7 County Board"] = 6
    started = os.environ.pop("RUN_STARTED", None)
    try:
        elections_margins.build()
        err = None
    except (AssertionError, ValueError) as e:
        err = str(e)
    finally:
        elections_margins.SEATS.clear()
        elections_margins.SEATS.update(orig)
        if started:
            os.environ["RUN_STARTED"] = started
    assert err and "did not seat" in err, f"not caught: {err}"


def test_a_candidate_standing_in_two_contests_of_a_year_is_refused():
    """Spain's 2024 primary row repeated under a second contest. With no
    guard the candidacy takes the first contest's votes and seat count, and
    which contest that is depends on the order the records list them."""
    def mangle(orig):
        def patched():
            d = orig()
            spain = d[(d.surname == "spain") & (d.year == 2024) & (d.election == "primary")]
            return pd.concat([d, spain.assign(contest="a second contest")], ignore_index=True)
        return patched
    err = breaks_aside(candidates, "records", mangle, build=candidates.build)
    assert err and "stood in 2 contests" in err, f"not caught: {err}"


def test_a_jefferson_win_count_that_is_not_hjerpes_is_refused():
    """Hjerpe's count of Jefferson District wins moved by one. The recorded
    candidacies would no longer say what the source says, and the figure's
    Jefferson row would be drawn from a count that does not tie out."""
    err = breaks_aside(candidates, "JEFFERSON_WINS", lambda orig: orig - 1,
                       build=candidates.build)
    assert err and "Hjerpe counts" in err, f"not caught: {err}"


# --- guards on the peer localities --------------------------------------------

def drop_body(name):
    """A mangle for localities_southeastern_bodies: the table without `name`,
    as if nobody had keyed that body's seats."""
    return lambda d: d[d["body"] != name]


def test_a_southeastern_city_nothing_keys_is_refused():
    """Cary, North Carolina (174,721 residents) dropped from the keyed bodies.
    With no guard the figure is captioned as every city of Arlington's size
    in the region and silently omits one."""
    err = breaks(paths, "built", patch_built("localities_southeastern_bodies",
                                             drop_body("Cary, NC")),
                 build=localities_southeastern.build)
    assert err and "Cary, NC" in err, f"not caught: {err}"


def test_a_southeastern_county_nothing_keys_is_refused():
    """Cherokee County, Georgia dropped from the keyed bodies. Counties are
    found by the same rule as cities; with no guard a county the rule finds
    would be missing from a figure that says it holds all of them."""
    err = breaks(paths, "built", patch_built("localities_southeastern_bodies",
                                             drop_body("Cherokee County, GA")),
                 build=localities_southeastern.build)
    assert err and "Cherokee County, GA" in err, f"not caught: {err}"


def test_a_maryland_county_nothing_keys_is_refused():
    """Frederick County, Maryland dropped. Maryland has no incorporated place
    of Arlington's size, so its bodies come in only by county, and a gap there
    leaves the state out without a trace."""
    err = breaks(paths, "built", patch_built("localities_southeastern_bodies",
                                             drop_body("Frederick County, MD")),
                 build=localities_southeastern.build)
    assert err and "Frederick County, MD" in err, f"not caught: {err}"


def test_a_keyed_county_below_the_floor_is_refused():
    """Washington County, Maryland at 100,000 in the census file, below the
    floor, while the table still keys it. With no guard a body the rule does
    not hold stays in the figure when the population table moves."""
    def grow(d):
        d.loc[d["county_name"].str.startswith("Washington County, Maryland"), "residents"] = "100000"
        return d
    err = breaks(paths, "built", patch_built("localities_counties", grow),
                 build=localities_southeastern.build)
    assert err and "Washington County, MD" in err, f"not caught: {err}"


def test_a_peer_county_the_census_does_not_carry_is_refused():
    """A county in the crosswalk spelled as the census does not. With no
    guard it reaches localities.csv with no population and no land area,
    and drops out of every per-resident comparison with Arlington."""
    def misspell(d):
        d.loc[d.index[0], "county"] = "Nowhere"
        return d
    err = breaks(build_localities, "source",
                 patch_source(lambda d: {"county", "members"} <= set(d.columns), misspell),
                 build=build_localities.build)
    assert err and "no census population or land area" in err, f"not caught: {err}"


def test_a_mayor_the_council_count_does_not_know_is_refused():
    """A city whose mayor is neither elected at large nor one of the members.
    With no guard the mayor is left out of the council's size, and the city
    is compared with Arlington's Board a member short."""
    def novel(d):
        d.loc[d.locality == "Norfolk", "mayor"] = "appointed"
        return d
    err = breaks(paths, "built", patch_built("localities", novel), build=localities.build)
    assert err and "unknown mayor" in err, f"not caught: {err}"


def test_a_governing_body_outside_the_codes_range_is_refused():
    """A county board keyed as two members. With no guard the county is
    plotted as a body the Code of Virginia does not allow, and the
    comparison with Arlington's five reads the typo as a finding."""
    def two(d):
        d.loc[d.locality == "Arlington", "members"] = "2"
        return d
    err = breaks(paths, "built", patch_built("localities", two), build=localities.build)
    assert err and "three to eleven" in err, f"not caught: {err}"


def test_a_second_arlington_row_in_the_peer_table_is_refused():
    """Arlington keyed twice among the peers. With no guard the county is
    set against itself, and its own rank among the localities is wrong."""
    def twice(d):
        return pd.concat([d, d[d.locality == "Arlington"]], ignore_index=True)
    err = breaks(paths, "built", patch_built("localities", twice), build=localities.build)
    assert err and "exactly one Arlington row" in err, f"not caught: {err}"


# --- the numbers the prose cites ------------------------------------------------

def regenerated_body_text_numbers():
    """What code/analysis/body_text_numbers.py would write now, from the
    clean tables. Run in this process with its two folders on the path, and
    returned, never written."""
    folders = [str(ROOT / "code" / "analysis"), str(ROOT / "style")]
    sys.path[:0] = folders
    try:
        module = importlib.import_module("body_text_numbers")
        return module.tex(module.numbers())
    finally:
        for f in folders:
            sys.path.remove(f)
        for name, m in list(sys.modules.items()):
            file = getattr(m, "__file__", None)
            if file and Path(file).resolve().is_relative_to(ROOT / "code" / "analysis"):
                del sys.modules[name]


def test_a_body_text_number_is_the_clean_tables_number():
    """paper/body_text_numbers.tex is byte-identical to what its script writes
    from the clean tables now: a hand edit, a rounding change, or a file left
    from before a table moved. Per-command derivations, worked out here
    separately, return when the paper's numbers settle."""
    committed = (ROOT / "paper" / "body_text_numbers.tex").read_text()
    assert committed == regenerated_body_text_numbers(), \
        "paper/body_text_numbers.tex is not what code/analysis/body_text_numbers.py writes; run bash run.sh"


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


def test_a_row_has_one_line():
    """Two rows of docs/questions.csv with the same id.

    The tracker merges by union, so a row narrowed on main and edited on a
    branch comes through the merge twice, once in each wording, and the next
    reader cannot tell which is current. One row sat in the file twice
    for a morning on 6 October 2026 after exactly that."""
    ids = [r["id"] for r in tracker_rows()]
    twice = sorted({i for i in ids if ids.count(i) > 1})
    assert not twice, (
        "docs/questions.csv holds more than one row for:\n  " + "\n  ".join(twice) +
        "\nKeep the wording that is current and delete the other line.")


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


def unsearched_defaults(members, negatives):
    """Each (member, field) of a member first seated before 1962 whose race
    or gender is the default, or whose birth year has no source, with no row
    in members_negatives.csv saying what was searched for it. Before 1962 a
    census is open, so a default there is a search that came back empty, and
    the search is the only evidence the default has."""
    searched = {(r["member"], f.strip()) for r in negatives for f in r["field"].split(";")}
    first, gaps = {}, set()
    for m in members:
        first[m["name"]] = min(first.get(m["name"], 9999), int(m["start_year"]))
    for m in members:
        if first[m["name"]] >= 1962:
            continue
        for field in ("race", "gender", "birth_year"):
            if m[f"{field}_source"] in ("assumed", "unsourced") and \
                    (m["name"], field) not in searched:
                gaps.add((m["name"], field))
    return sorted(gaps)


def test_every_early_default_has_its_search_on_record():
    """The real tables: every pre-1962 default names the search behind it,
    and every row of the negatives table names a roster member."""
    members = list(csv.DictReader((ROOT / "data/clean/members.csv").open(newline="")))
    negatives = list(csv.DictReader(
        (ROOT / "data/transcribed/by_claude/members_negatives.csv").open(newline="")))
    gaps = unsearched_defaults(members, negatives)
    assert not gaps, ("members resting on a default with no search on record in "
                      "members_negatives.csv:\n  " + "\n  ".join(f"{n}: {f}" for n, f in gaps))
    names = {m["name"] for m in members} | {"the Board"}
    strays = sorted({r["member"] for r in negatives} - names)
    assert not strays, f"members_negatives.csv names no roster member: {strays}"


def test_a_default_whose_search_is_dropped_is_refused():
    """Take Robinson's gender search out: the check must name him."""
    members = [{"name": "William H. Robinson", "start_year": "1877",
                "race_source": "assumed", "gender_source": "assumed",
                "birth_year_source": "unsourced"}]
    negatives = [{"member": "William H. Robinson", "field": "race; birth_year"}]
    assert unsearched_defaults(members, negatives) == [("William H. Robinson", "gender")], \
        "a default with no search on record was accepted"


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
    """A bib entry with a url that names no copy on file ("Filed in sources
    as", or a path under sources/); or one that says it is not filed.
    Either is allowed only while docs/questions.csv names the key, so an
    entry that admits to holding no copy is tracked rather than rewritten
    into a claim that it is filed."""
    problems = []
    for key, body in bib_entries():
        if re.search(r"not\s+(?:yet\s+)?filed", body, re.I) and key not in questions():
            problems.append(f"{key}: says it is not filed - file it in sources/ and say so, "
                            f"or log a question naming the key")
        has_url = re.search(r"^\s*url\s*=", body, re.M)
        # Whitespace-tolerant: biblatex wraps an annotation anywhere, so a
        # literal match would fail an entry that names its copy across a line.
        held = re.search(r"Filed\s+in\s+sources\s+as", body) or "sources/" in body
        # A page cited only for a count keeps no copy, on purpose: what it said
        # is keyed into data/transcribed/ with the date it was read, and that
        # file is the source a reviewer reads. The keyed file must be named, so
        # "no copy is kept" cannot stand on its own.
        if re.search(r"no\s+copy\s+is\s+kept", body) and "data/transcribed/" in body:
            held = True
        if has_url and not held and key not in questions():
            problems.append(f"{key}: has a url but names no copy - add 'Filed in sources as \"...\"' "
                            f"or the path under sources/, or log a question naming the key")
    assert not problems, "sources with no copy on file:\n  " + "\n  ".join(problems)


def test_a_filed_name_is_read_through_the_quotes_in_a_title():
    """Gilbertson's county is the "Dark Continent", and reading the name only
    as far as the next quotation mark left "of American Politics.txt", which
    matches no file. archive.py reported the copy as named by nobody, and
    --apply would have moved a book the bib names into unplaced/."""
    e = {"annotation": 'Filed in sources as "books/Gilbertson, H. S. 1917 - The County, the '
                       '"Dark Continent" of American Politics.txt", the Internet Archive OCR.'}
    assert archive.filed(e) == ['books/Gilbertson, H. S. 1917 - The County, the '
                                '"Dark Continent" of American Politics.txt'], archive.filed(e)


def test_a_space_after_a_folder_is_a_typo_and_not_a_folder():
    """An annotation typed "legal/statutes/state/ Commonwealth ..." names a
    copy that is really there; the space made the archive call it unplaced."""
    e = {"annotation": 'Filed in sources as "legal/statutes/state/ Commonwealth of Virginia '
                       '1971 - An Act to Conform.pdf".'}
    assert archive.filed(e) == ["legal/statutes/state/Commonwealth of Virginia 1971 - "
                                "An Act to Conform.pdf"], archive.filed(e)


def test_quoted_prose_in_an_annotation_is_not_a_filed_name():
    """The other half: annotations quote the sources they read, and a quoted
    sentence that happens to run past a filename must not be read as one."""
    e = {"annotation": 'The court said "a continuous, contiguous community" of it. '
                       'Filed in sources as "legal/cases/Court 1922 - Bennett v. Garrett.pdf".'}
    assert archive.filed(e) == ["legal/cases/Court 1922 - Bennett v. Garrett.pdf"]


def test_every_filed_name_in_the_bib_is_a_file_that_exists():
    """Every name, against the folder. This is what the two defects above
    broke: a name the parser mangles resolves to nothing, and nothing says so."""
    bib = archive.entries(archive.BIB.read_text())
    named = [(e["key"], n) for e in bib for n in archive.filed(e) if "/" in n]
    assert len(named) > 400, f"only {len(named)} filed names found - is the parser matching?"
    missing = [f"{k}: {n}" for k, n in named if not (archive.SOURCES / n).exists()]
    assert not missing, "filed names that are not files:\n  " + "\n  ".join(missing)


def test_another_localitys_roster_page_is_cited_and_not_filed():
    """A peer locality's council page filed as a copy. Forty-two reached the
    folder in a day, 249MB of screen captures of other counties' commissioners
    for one integer each, and the integer is keyed into data/transcribed/,
    where a reviewer reads it."""
    e = {"type": "online", "key": "planted", "title": "Board of Commissioners",
         "organization": "Buncombe County, North Carolina"}
    assert archive.roster_page(e), "a peer county's roster page read as something else"
    # Arlington's own pages are the report's subject, and a paper writing about
    # a board is not the board publishing about itself.
    for who, title, typ in [("Arlington County, Virginia", "County Board Members", "online"),
                            ("Alexandria Gazette", "Board of Supervisors", "article"),
                            ("Richmond City Charter Review Commission",
                             "Richmond City Charter Review Commission 2023", "report")]:
        other = {"type": typ, "key": "planted", "title": title, "organization": who}
        assert not archive.roster_page(other), f"{who} read as a roster page"


def test_no_roster_page_in_the_bib_names_a_filed_copy():
    """The real bib: a roster page that names a copy, or that does not say
    where its count was keyed, so neither passes unnoticed."""
    bib = archive.entries(archive.BIB.read_text())
    rosters = [e for e in bib if archive.roster_page(e)]
    assert rosters, "no roster pages found at all - has roster_page() stopped matching?"
    filed = [e["key"] for e in rosters if archive.filed(e)]
    assert not filed, ("roster pages with a copy filed in sources/ - cite the page and key the "
                       "count instead:\n  " + "\n  ".join(filed))
    unkeyed = [e["key"] for e in rosters
               if "data/transcribed/" not in e.get("annotation", "")]
    assert not unkeyed, ("roster pages whose annotation does not say where the count is "
                         "keyed:\n  " + "\n  ".join(unkeyed))


def test_a_record_that_is_not_a_census_is_not_filed_as_one():
    """Four Ancestry records - a marriage, a passenger list, a draft card, a
    grave - were filed as censuses because the rule read who published them,
    and landed in the census folder under 1924, 1934, 1942 and 1957, years no census
    was taken in."""
    for title, where in [
            ("John C. Gall in the Virginia, U.S., Select Marriages, 1785-1940", "vital records"),
            ("John Christian Gall in the U.S., World War II Draft Cards", "vital records"),
            ("S. B. Boyd in the 1870 United States Federal Census", "census")]:
        e = {"type": "misc", "key": "planted", "title": title, "organization": "Ancestry.com"}
        assert archive.kind(e) == where, f"{title[:40]} filed as {archive.kind(e)}, not {where}"


def test_a_committees_report_on_the_code_is_not_filed_as_legal():
    """vacodecommission1997sd5, reintroduced: the Virginia Code Commission's
    report recommending a recodification was swept into legal/ because its
    title names the Code, same as the acts and sections it reports on. A
    report is not the law it reports on, and @report was a deliberate type."""
    e = {"type": "report", "key": "planted",
         "title": "Report of the Virginia Code Commission on the Recodification "
                   "of Title 15.1 of the Code of Virginia (excerpt)",
         "organization": "Commonwealth of Virginia, Senate Document No. 5 (1997)"}
    assert archive.kind(e) == "reports", f"filed as {archive.kind(e)}, not reports"


def test_a_census_record_is_filed_as_one_whoever_indexed_it():
    """The FamilySearch record, reintroduced: the rule looked for Ancestry by
    name, so the one census page indexed elsewhere fell through to reports/
    and would have been filed as though a number were not read off it."""
    for who in ("Ancestry", "FamilySearch"):
        e = {"type": "online", "key": "planted", "title": "United States, Census, 1900",
             "organization": who}
        assert archive.kind(e) == "census", f"a {who} census record filed as {archive.kind(e)}"
        base = f"{who} 1900 - United States, Census, 1900.pdf"
        want = {"Ancestry": "genealogy/ancestry/1900", "FamilySearch": "genealogy/familysearch/1900"}[who]
        assert archive.shelf(e, base) == want, f"{base} files in {archive.shelf(e, base)}, not {want}"


def test_press_files_by_outlet_and_legal_by_what_the_document_is():
    """A paper's run belongs in one place, under press, and the law is split
    the way the bibliography's Legal Authorities part is: cases,
    constitutions, statutes, with statutes divided by whose they are."""
    e = {"type": "article", "key": "planted", "title": "Arlington Republicans",
         "organization": "Alexandria Gazette", "pages": "3", "location": "Alexandria"}
    assert archive.shelf(e, "Alexandria Gazette 1873 - Arlington Republicans.pdf") == \
        "press/alexandria_gazette"
    for who, title, where in [
            ("Supreme Court of Appeals of Virginia", "Bennett v. Garrett", "legal/cases"),
            ("Commonwealth of Virginia", "Code of Virginia", "legal/statutes/state"),
            ("Commonwealth of Virginia", "An Act to Provide for the Method of Voting by Ballot",
             "legal/statutes/state"),
            # the legislature acting on the constitution is a statute
            ("Commonwealth of Virginia", "Joint Resolutions Proposing Amendments to Article VII "
             "of the Constitution of Virginia", "legal/statutes/state"),
            ("Commonwealth of Virginia", "Constitution of Virginia", "legal/constitutions"),
            # whose law it is: Congress retroceded the county, Virginia accepted it
            ("United States", "An Act to retrocede the County of Alexandria",
             "legal/statutes/federal")]:
        e = {"type": "legislation", "key": "planted", "title": title, "author": who}
        got = archive.shelf(e, f"{who} 1846 - {title}.pdf")
        assert got == where, f"{who}, {title} filed in {got}, not {where}"


def test_the_census_bureau_is_one_folder_whatever_name_an_entry_gives_it():
    """The HH-6 table, reintroduced: its entry names the Bureau "U.S. Census
    Bureau" where the volumes say "U.S. Bureau of the Census", and the two
    names filed in two folders, one of them under other/."""
    for who in ("U.S. Census Bureau", "U.S. Bureau of the Census"):
        e = {"type": "online", "key": "planted", "title": "HH-6", "author": who,
             "organization": "U.S. Census Bureau, Current Population Survey"}
        got = archive.shelf(e, f"{who} 2025 - HH-6.xls")
        assert got == "government/federal/us_census_bureau", f"{who} files in {got}"


def test_every_filed_copy_is_on_its_shelf():
    """A copy somewhere other than where archive.shelf() puts it: filed by
    hand, or left behind by a rule that changed. archive.py's dry run would
    list it as a move; this stops the build instead."""
    bib = archive.entries(archive.BIB.read_text())
    claims, missing = archive.place(bib, archive.SOURCES)
    assert not missing, f"filed names not found: {missing[:3]}"
    off = [f"{cur} -> {t}" for cur, (t, _) in claims.items() if cur != t]
    assert not off, "copies off their shelf:\n  " + "\n  ".join(off)


def test_the_stages_name_the_same_publisher_folders_and_the_cache_reads_them():
    """code/build/, code/fetch/ and code/transcribe/ each name the folders
    under sources/ they read or write in their own paths.py, so the three
    have to agree, every folder has to exist, and the folders the build reads
    have to be among the inputs run.sh keys the build cache on. A folder
    the key leaves out would let an edited table restore a stale build."""
    import importlib.util
    named = {}
    for stage in ("build", "fetch", "transcribe"):
        spec = importlib.util.spec_from_file_location(f"{stage}_paths_probe", ROOT / "code" / stage / "paths.py")
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(ROOT / "code"))
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.path.pop(0)
        named[stage] = {n: v for n, v in vars(mod).items()
                        if isinstance(v, Path) and v != mod.SOURCES and mod.SOURCES in v.parents}
    for stage, folders in named.items():
        for name, folder in folders.items():
            assert folder.is_dir(), f"code/{stage}/paths.py {name} is not a folder: {folder}"
            for other, others in named.items():
                assert others.get(name, folder) == folder, \
                    f"{name} is {folder} in {stage} and {others[name]} in {other}"
    run = (ROOT / "run.sh").read_text()
    built_by = re.search(r"^BUILT_BY=\((.*?)\)", run, re.M | re.S).group(1).split()
    for name, folder in named["build"].items():
        rel = str(folder.relative_to(ROOT))
        assert rel in built_by, f"run.sh BUILT_BY does not list {rel}, which code/build/paths.py reads as {name}"


def test_a_hyphen_is_not_crowded_against_the_word_before_it():
    """A title's colon becomes a hyphen when it is filed, and "Virginia- A
    History" reads as a typo. A hyphen inside a word keeps its place."""
    e = {"type": "book", "key": "planted", "title": "x", "organization": ""}
    assert archive.canonical(e, "Rose 1976 - Arlington County, Virginia- A History.pdf") == \
        "Rose 1976 - Arlington County, Virginia - A History.pdf"
    assert archive.spaced("U.S. Census Bureau 2025 - HH-6. Households and Family- 1940.xls") == \
        "U.S. Census Bureau 2025 - HH-6. Households and Family - 1940.xls"


def test_an_obituary_is_named_for_the_person_it_is_for():
    """An obituary filed under its writer or the site it was read on. The
    folder answers "do we hold one for Grotos", so the person leads and the
    outlet follows; the Munsey obituary is headed Virdell and the roster says
    Everard, which is why the name comes from `subject` and not the title."""
    e = {"type": "online", "key": "planted", "title": "Virdell Munsey Obituary",
         "subject": "Everard Munsey", "organization": "The Washington Post, via Legacy.com"}
    assert archive.canonical(e, "Legacy.com 2025 - Virdell Munsey Obituary.pdf") == \
        "Munsey 2025 - Virdell Munsey Obituary (Washington Post).pdf"
    scan = {"type": "article", "key": "planted", "title": "Leo C. Lloyd Dies",
            "subject": "Leo C. Lloyd", "pages": "1", "location": "Arlington",
            "journaltitle": "The Arlington Daily"}
    assert archive.canonical(scan, "Arlington Daily 1947 - Leo C. Lloyd Dies (3 November 1947, p. 1).pdf") == \
        "Lloyd 1947 - Leo C. Lloyd Dies (Arlington Daily, 3 November 1947, p. 1).pdf"


def test_every_obituary_names_the_person_it_is_for():
    """`subject` is what the filename is built from, so an obituary without
    one is filed under whoever wrote it and nobody notices."""
    bib = archive.entries(archive.BIB.read_text())
    roster = (ROOT / "data" / "clean" / "members.csv").read_text()
    missing = [e["key"] for e in bib if archive.kind(e) == "obituaries" and not e.get("subject")]
    assert not missing, "obituaries that do not name their subject:\n  " + "\n  ".join(missing)
    unknown = [(e["key"], archive.plain(e["subject"])) for e in bib
               if archive.kind(e) == "obituaries" and archive.plain(e["subject"]) not in roster]
    assert not unknown, ("obituaries whose subject is not a name in data/clean/members.csv:\n  "
                         + "\n  ".join(f"{k}: {w}" for k, w in unknown))


def test_a_press_copy_is_named_for_its_outlet():
    """A filed article named for its byline. The folder is read by someone
    looking for what a paper printed, and the scans were always named for the
    paper, so a page read online that kept its reporter's name sorted away
    from the rest of that paper's coverage."""
    e = {"type": "article", "key": "planted", "title": "Arlington Board Is All-Democratic",
         "author": "Hsu, Spencer", "organization": "The Washington Post",
         "journaltitle": "The Washington Post"}
    assert archive.canonical(e, "Hsu 1987 - Arlington Board Is All-Democratic.pdf") == \
        "Washington Post 1987 - Arlington Board Is All-Democratic.pdf"


def test_every_filed_press_copy_is_named_for_its_outlet():
    """The real bib, so an entry filed under a byline cannot sit unnoticed."""
    bib = archive.entries(archive.BIB.read_text())
    wrong = [(n, archive.canonical(e, n)) for e in bib if archive.kind(e) == "press"
             for n in (f.split("/")[-1] for f in archive.filed(e))
             if archive.canonical(e, n) != n]
    assert not wrong, "press copies not named for their outlet:\n  " + \
        "\n  ".join(f"{a} -> {b}" for a, b in wrong)



def a_legal_entry(key, annotation):
    """A one-entry bib naming a copy that is really on file, so a test can
    put words in its mouth. @jurisdiction is what archive.kind() files under
    legal/, which is the only kind this check reads."""
    return ("@jurisdiction{" + key + ",\n"
            "  title       = {Bennett v. Garrett},\n"
            "  annotation  = {" + annotation + "},\n}\n")


BENNETT = ('Filed in sources as "legal/cases/Supreme Court of Appeals of Virginia 1922 - '
           'Bennett v. Garrett.pdf"')


def test_a_quotation_the_document_does_not_contain_is_refused():
    """The Bennett misattribution, reintroduced: Rose's phrase written as
    the court's own. It stood for months: the opinion was filed all along,
    but nothing checked the quotation against it until this guard."""
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



# --- citekeys named in prose --------------------------------------------------

def test_a_write_up_citing_an_entry_that_was_dropped_is_refused():
    """1971 Ex. Sess. c. 1 was filed twice in one afternoon under two keys.
    One was dropped on the merge, and the tracker row went on citing it: the
    bib was consistent, the build passed, and the row pointed at nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        doc = Path(tmp) / "questions.csv"
        doc.write_text("the 1971 conforming act re-enacts the sections "
                       "without it (vaacts1971c1), so the softening is later.\n")
        assert citekeys.dangling([doc]) == [(doc, "vaacts1971c1")], \
            "a citekey no entry defines was accepted in a write-up"


def test_a_write_up_citing_an_entry_that_exists_passes():
    """The other half: a live key is not flagged, so the check is not
    simply refusing every parenthesis."""
    with tempfile.TemporaryDirectory() as tmp:
        doc = Path(tmp) / "members.md"
        doc.write_text(f"the article's footnote (`{citekeys.ARLHIST_OFFICIALS}`) "
                       f"explains the term, and so does ({citekeys.NOVACK} p. 12).\n")
        assert citekeys.dangling([doc]) == [], "a citekey the bib defines was flagged"


def test_every_citekey_the_write_ups_name_is_in_the_bibliography():
    """Every docs/ file against the real bibliography."""
    docs = sorted((ROOT / "docs").glob("*.md")) + [ROOT / "docs" / "questions.csv"]
    bad = citekeys.dangling(docs)
    assert not bad, "write-ups cite entries paper/bib/sources.bib does not define:\n  " + \
        "\n  ".join(f"{p.relative_to(ROOT)}: {k}" for p, k in bad)


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
    for doc in [ROOT / "paper" / "bib" / "sources.bib", ROOT / "paper" / "arlington-bsap.tex"]:
        for m in re.finditer(r"(?<![\w/.-])(?:code|data|docs|figures|paper|sources|style)/[\w./-]+", doc.read_text()):
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
    """A file under data/ or sources/ with no row in data/contents.csv, a row
    with no file (unless fetched on demand), a file with two rows, or a
    published file whose checksum has moved."""
    data = ROOT / "data"
    listed = [r["path"] for r in csv.DictReader((data / "contents.csv").open())]
    twice = sorted({p for p in listed if listed.count(p) > 1})
    assert not twice, "files with two rows in data/contents.csv:\n  " + "\n  ".join(twice)
    rows = {r["path"]: r for r in csv.DictReader((data / "contents.csv").open())}
    on_disk = {str(p.relative_to(ROOT)) for folder in (data, ROOT / "sources") for p in folder.rglob("*")
               if p.is_file() and not p.name.startswith(".") and p.name != "contents.csv"
               and p.name not in ("index.md", "arlington-bsap-archive.zip")}
    missing = sorted(on_disk - set(rows))
    gone = sorted(p for p in set(rows) - on_disk if rows[p]["in_git"] == "yes")
    assert not missing, "files under data/ or sources/ with no row in data/contents.csv:\n  " + "\n  ".join(missing)
    assert not gone, "rows in data/contents.csv for files that do not exist:\n  " + "\n  ".join(gone)
    moved = [p for p, r in rows.items() if r["layer"] == "published" and (ROOT / p).exists()
             and hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:16] != r["sha256"]]
    assert not moved, ("published files whose checksum does not match data/contents.csv - sources/ "
                       "is never edited:\n  " + "\n  ".join(moved))


def test_a_note_whose_commas_are_unquoted_is_refused():
    """A row of data/contents.csv with more fields than the header.

    An unquoted note splits on its own commas, and csv.DictReader files the
    spill under None rather than complaining, so the row keeps its path and
    its checksum and reads as sound. The 1912-1931 term listing sat that way
    with its note in three pieces until a write that round-tripped the file
    refused it."""
    header, *rows = csv.reader((ROOT / "data" / "contents.csv").open())
    ragged = [(i + 2, len(r)) for i, r in enumerate(rows) if len(r) != len(header)]
    assert not ragged, ("rows of data/contents.csv whose field count is not "
                        f"{len(header)} - a note with a comma needs quoting:\n  "
                        + "\n  ".join(f"line {n}: {c} fields" for n, c in ragged))


def run_sh_steps(name):
    """The steps run.sh lists for one stage: BUILD, CLEAN or FIGURES."""
    run = (ROOT / "run.sh").read_text()
    return re.search(rf"^{name}=\((.*?)\)$", run, re.M).group(1).split()


SUBJECTS = ("residents", "elections", "members", "candidates", "localities", "survey", "comments")


def unproduced_figures(rows, figures, tables):
    """(row id, name) for every name in a row's `affects` that is named like
    a figure - a subject first, then underscores, as figures/pdf/ names are -
    and is neither a figure some step produces nor a table in data/clean/."""
    shape = re.compile(rf"^(?:{'|'.join(SUBJECTS)})(?:_[a-z0-9]+)+$")
    return [(r["id"], name) for r in rows
            for name in (t.strip() for t in re.split(r"[;,]", r["affects"]))
            if shape.match(name) and name not in figures and name not in tables]


def test_a_tracker_row_naming_a_figure_no_step_produces_is_refused():
    """A row's `affects` cell named a figure that had been retired two days
    before, so the row promised a change to a picture that no longer
    existed. Every figure-shaped name there must be a step in run.sh's
    FIGURES or a table the clean stage writes."""
    tables = {p.stem for p in (ROOT / "data" / "clean").glob("*.csv")}
    figures = set(run_sh_steps("FIGURES"))
    stale = unproduced_figures(tracker_rows(), figures, tables)
    assert not stale, ("docs/questions.csv rows whose `affects` names a figure no step produces "
                       "(retired? name its replacement):\n  "
                       + "\n  ".join(f"{i}: {n}" for i, n in stale))
    # The guard fires on the mistake: a row naming a retired figure.
    row = {"id": "x", "affects": "members_by_race; elections_turnout_by_decade"}
    assert unproduced_figures([row], figures, tables) == [("x", "elections_turnout_by_decade")], \
        "a retired figure in `affects` was not found"
    assert unproduced_figures([{"id": "y", "affects": "prose; members_by_race"}], figures, tables) == []


def test_a_step_and_a_module_are_told_apart():
    """A file in a stage folder that run.sh does not list but writes
    something anyway, or one it lists that writes nothing.

    Half of code/clean/ is modules the steps import - the roster readers, the
    terms, the contests - and three of code/analysis/ are too. Nothing in a
    name or a folder says which half a file is in, so the only reading of it
    is run.sh's own list, and a step left out of that list silently never
    runs. The other reading is the file itself: a step writes what it is
    named for, from a __main__ block or, in code/analysis/, from a
    paths.save(). This asserts the two agree, which makes the distinction
    mechanical instead of conventional."""
    problems = []
    for folder, name in (("build", "BUILD"), ("clean", "CLEAN"), ("analysis", "FIGURES")):
        listed = run_sh_steps(name)
        for f in sorted((ROOT / "code" / folder).glob("*.py")):
            if f.name == "paths.py":
                continue
            text = f.read_text()
            writes = 'if __name__ == "__main__":' in text or "paths.save(" in text
            if writes and f.stem not in listed:
                problems.append(f"code/{folder}/{f.name} writes an output but "
                                f"{name} in run.sh does not list it - add it, or make it "
                                f"a module the steps import")
            if f.stem in listed and not writes:
                problems.append(f"{name} in run.sh lists {f.stem}, but "
                                f"code/{folder}/{f.name} writes nothing")
    assert not problems, "a stage's steps and its modules disagree:\n  " + "\n  ".join(problems)


def test_docs_agree_with_run_sh():
    """A `pip install` line in the docs that differs from the one a missing
    venv prints (code/cache.py, which run.sh asks for the venv)."""
    run = (ROOT / "code" / "cache.py").read_text()
    install = re.search(r"pip install ([a-z0-9 ]+)", run).group(1).split()
    problems = []
    for doc in [ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / "docs" / "setup.md"]:
        text = doc.read_text()
        for m in re.finditer(r"pip install ([a-z0-9 ]+)", text):
            if m.group(1).split() != install:
                problems.append(f"{doc.name}: install line says {m.group(1).split()}, code/cache.py says {install}")
    assert not problems, "docs disagree with code/cache.py:\n  " + "\n  ".join(problems)


def test_a_timeline_citation_reaches_the_footnote():
    """A \\autocite inside \\timeline while the preamble does not make tabular
    footnote-safe. LaTeX drops a footnote raised inside a tabular: the
    superscript prints and the note never appears, with no warning and a
    compile that succeeds. Six citations were lost that way before
    \\makesavenoteenv{tabular} was added, so the pairing is checked rather
    than trusted."""
    # The timelines live in docs/timelines/timelines.tex, with a preamble of their own.
    for name, path in paper.SOURCES.items():
        tex = (ROOT / "paper" / path).read_text()
        live = "\n".join(re.sub(r"(?<!\\\\)%.*", "", line) for line in tex.split("\n"))
        cited = len([m for m in re.finditer(r"\\timeline\{(.*?)\n\}", live, re.S)
                     if "autocite" in m.group(1)])
        tabular = re.search(r"\\newcommand\{\\timeline\}.*?\\end\{tabular\}", live, re.S)
        safe = re.search(r"\\makesavenoteenv\{tabular\}", live)
        assert not (cited and tabular and not safe), (
            f"{name}.tex: {cited} timeline(s) cite a source inside a tabular, but the "
            f"preamble has no \\makesavenoteenv{{tabular}}: those footnotes are dropped "
            f"silently. Add \\usepackage{{footnote}} and \\makesavenoteenv{{tabular}}, "
            f"or move the citations into the prose.")


def test_a_source_note_is_filed_in_the_annotation_not_the_footnote():
    """cite.py's --note is what the document says that the report relies on.
    biblatex prints a `note` field in the footnote of every citation, so a
    reading written there lands in the paper: footnotes ran to a paragraph
    until the reading went to the annotation, which is not printed."""
    import types
    a = types.SimpleNamespace(
        key="k", url="https://example.org/x.pdf", author="A", title="T", organization="",
        journal="", location="", date="2026", note="The page says seven members.",
        cite_note="", how="", copy=None, type="online", pages="", field=[])
    entry = cite.entry_text(a, "A 2026 - T.pdf", "documents")
    assert "\n  note " not in entry, "the reading is filed as a note, which prints in the footnote"
    assert "The page says seven members." in entry
    a.cite_note = "Vol. 3, no. 4"
    assert "note        = {Vol. 3, no. 4}" in cite.entry_text(a, "A 2026 - T.pdf", "documents")


def test_cite_writes_entries_the_style_sheet_accepts():
    """What cite.py appends is held to the same sheet as an entry written by
    hand, so a new source does not start life failing test_every_cited_entry_
    is_complete: an unsigned newspaper piece (no author, a braced sortname, a
    masthead without The, a headline-style title), the same read online with no
    page, a case and an act (no author, the sovereign in organization)."""
    import types
    base = dict(key="k", url="https://example.org/x", author="", title="T", organization="",
                journal="", location="", date="2026-01-02", note="Says so.", cite_note="",
                how="", copy=None, type="online", pages="", field=[])

    def made(**change):
        a = types.SimpleNamespace(**{**base, **change})
        e = archive.entries(cite.entry_text(a, "x.pdf", "press"))[0]
        return e, incomplete(e)

    e, problems = made(type="article", journal="The Daily Sun", location="Arlington, Va.", pages="1",
                       title="City charter for Arlington soundly beaten")
    assert problems == [], problems
    assert e["journaltitle"] == "Daily Sun" and e["sortname"] == "{Daily Sun}" and "author" not in e
    assert e["title"] == "City Charter for Arlington Soundly Beaten"
    e, problems = made(type="article", journal="Sun Gazette", location="Arlington, Va.")
    assert problems == [], problems
    assert e["entrysubtype"] == "magazine"
    e, problems = made(organization="ARLnow", title="Board votes 1952-1954")
    assert "sortname" in e and "--" in e["title"]
    e, problems = made(type="jurisdiction", author="Commonwealth of Virginia", title="Bennett v.\\ Garrett",
                       field=["journaltitle=Va.", "volume=132", "pages=397"])
    assert problems == [], problems
    assert "author" not in e and e["organization"] == "Commonwealth of Virginia"


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


def test_a_compile_leaves_no_pdf_in_the_build_folder():
    """A copy left in paper/build/ outlives the compile that wrote it: one
    from 7 October was linked to as the current report for two days. The
    PDF is moved up beside the source, so the build folder holds none."""
    with tempfile.TemporaryDirectory() as tmp:
        build, up = Path(tmp) / "build", Path(tmp) / "report.pdf"
        build.mkdir()
        (build / "report.pdf").write_bytes(b"%PDF-new\n")
        paper.publish(build / "report.pdf", up)
        assert up.read_bytes() == b"%PDF-new\n", "the PDF did not reach paper/"
        assert not list(build.glob("*.pdf")), f"a PDF stayed in the build folder: {list(build.glob('*.pdf'))}"


def test_a_broken_axis_whose_gap_differs_from_the_others_is_refused():
    """The gap is measured from where the axes sit. Two breaks the figure
    drew 0.09 and 0.28 of its width apart were claimed to match, so a
    break_x whose gap is not style.BREAK_GAP, or not the other break's,
    raises."""
    stage_charts, style_mod = style_modules()
    fig, (n1, f1), (n2, f2) = stage_charts.scatter_pair()
    stage_charts.break_x(n1, f1, "x", (0, 10), 5)
    stage_charts.break_x(n2, f2, "x", (0, 10), 5)       # matching gaps pass
    fig = stage_charts.plt.figure()
    near = fig.add_axes([0.1, 0.1, 0.4, 0.8])
    far = fig.add_axes([0.5 + style_mod.BREAK_GAP * 3, 0.1, 0.2, 0.8], sharey=near)
    near.break_ratio = style_mod.BROKEN
    try:
        stage_charts.break_x(near, far, "x", (0, 10), 5)
    except ValueError as e:
        assert "gap" in str(e), e
    else:
        raise AssertionError("a break three times wider than style.BREAK_GAP was drawn")


def style_modules():
    """(charts, style): style/ holds both and has no paths.py, so putting it
    on the path reaches nothing of the data."""
    sys.path.insert(0, str(ROOT / "style"))
    try:
        return importlib.import_module("charts"), importlib.import_module("style")
    finally:
        sys.path.remove(str(ROOT / "style"))


def crowded_scatter(n):
    """A figure with n dots packed in the middle of its plot, each named."""
    import numpy as np
    charts, style_mod = style_modules()
    labels = sys.modules["labels"]
    fig, ax = charts.plt.subplots(figsize=(3.2, 3.2))
    rng = np.random.default_rng(3)
    x, y = rng.uniform(0.4, 0.6, n), rng.uniform(0.4, 0.6, n)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    area = charts.dot_area()
    charts.dots(ax, x, y, area, [style_mod.GREY] * n)
    for i in range(n):
        labels.dot_label(ax, x[i], y[i], f"Name {i}", area)
    return labels, fig, ax


def test_every_name_in_a_crowded_scatter_is_placed_or_the_refusal_names_one():
    """Eight spots beside the dot dropped names in a dense scatter. Ten dots
    in a tenth of the plot need names stood off with a leader line; with the
    stand-off rings switched off (the old behaviour) the same figure is
    refused, and twenty dots are refused with the name that found no place."""
    labels, fig, ax = crowded_scatter(10)
    labels.place(fig)
    assert any(a.arrow_patch.get_visible() for a, *_ in ax.dot_labels), \
        "ten crowded dots were all named beside their dots, so the test no longer crowds them"
    saved, labels.RINGS = labels.RINGS, 0
    try:
        _, fig, ax = crowded_scatter(10)
        try:
            labels.place(fig)
        except AssertionError:
            pass
        else:
            raise AssertionError("without the stand-off rings a crowded scatter was placed: the test proves nothing")
    finally:
        labels.RINGS = saved
    _, fig, ax = crowded_scatter(20)
    try:
        labels.place(fig)
    except AssertionError as e:
        assert "Name " in str(e) and "no clear place" in str(e), e
    else:
        raise AssertionError("twenty names in a tenth of the plot were all placed")


def test_the_county_message_reader_prints_no_resident_unless_asked():
    """The County's messages carry residents' names, phones and addresses,
    and a session printed them into its output. render() shows only counts
    and field names until a resident field is named, and the summary has
    nothing of a message in it at all."""
    import county_messages as cm
    message = {"date": "2025-12-01", "subject": "Dolores Vane on the Board",
               "sender": "dvane@example.org",
               "body": "Dolores Vane, 22 Elm St, 703-555-0142\nFrom: staff@arlingtonva.us"}
    quiet = cm.render(message)
    for secret in ("Dolores", "Vane", "Elm St", "703-555", "example.org"):
        assert secret not in quiet, f"{secret!r} printed with no flag:\n{quiet}"
    assert "body: (resident field" in quiet and "forwarded: true" in quiet, quiet
    loud = cm.render(message, show=["body"])
    assert "703-555-0142" in loud and "Dolores Vane on the Board" not in loud, \
        "naming body should print the body and only the body"
    try:
        cm.render(message, show=["date"])
    except ValueError:
        pass
    else:
        raise AssertionError("a flag naming something that is not a resident field was accepted")
    assert "Vane" not in cm.summary({"Correspondence": 176, "Advisory": 72})


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


def test_a_chair_the_roll_labels_in_a_new_way_is_refused():
    """The 2020 chair, reintroduced. The roll prints "chair" for Libby Garvey
    in 2020, the one year it does not print chairman or chairwoman, and
    OFFICES had no entry for it: the build dropped the year without a word
    and the table showed no chair for 2020 until a count of years found the
    hole. An office label the build cannot read must stop it."""
    roll = pd.DataFrame([{"year": "2020", "name": "Libby Garvey", "office": "chairperson",
                          "event": "took the chair", "event_date": "2020-01-02"}])
    try:
        members_chairs.build(roll)
    except ValueError as e:
        assert "chairperson" in str(e), e
    else:
        raise AssertionError("an office label OFFICES does not read was dropped")


def test_a_survey_cell_that_lost_its_status_is_refused():
    """A cell resting on too few respondents, read as one that is not.
    Twenty of the 132 cells are marked caution by the survey's own
    preparers, and every race and ethnicity category but White and Black is
    among them. If `status` stopped reaching code/clean/survey_rcv.py the
    shares would all still be right, and a figure would show the 37 Hispanic
    respondents as firmly as the 444 White ones with nothing to say so."""
    def mangle(orig):
        def patched(stem):
            frame = orig(stem)
            if stem == "survey_rcv":
                frame = frame.copy()
                frame["status"] = "ok"
            return frame
        return patched
    err = breaks(clean_survey_rcv.paths, "built", mangle, build=clean_survey_rcv.clean)
    assert err and "marked the same way" in err, f"not caught: {err}"


# Above this share of members resting on an assumption or missing, the
# attribute needs a coverage figure; at or below it, a sentence in the
# write-up is enough and the figure may go (Sally, 4 October 2026).
COVERAGE_THRESHOLD = 0.10


def attribute_gaps():
    """Per attribute of members.csv, the share of members it does not rest
    on a source for, and the figure that shows it."""
    terms = pd.read_csv(ROOT / "data/clean/members.csv", dtype=str, keep_default_na=False)
    people = terms.groupby("name").first()
    placed = set(pd.read_csv(ROOT / "data/clean/members_residence.csv", dtype=str)["name"])
    return {
        "members_race_coverage": (people.race_source == citekeys.ASSUMED).mean(),
        "members_residence_coverage": (~people.index.isin(placed)).mean(),
    }


def missing_coverage(gaps, figures, threshold=COVERAGE_THRESHOLD):
    """The coverage figures an attribute is owed but run.sh does not build."""
    return sorted(f for f, share in gaps.items() if share > threshold and f not in figures)


def test_an_attribute_resting_on_an_assumption_has_a_coverage_figure():
    """The race default, reintroduced without its figure. A third of the
    members are White because nothing says otherwise, and with no coverage
    figure the report would show race as known where it is assumed. Any
    attribute whose gap passes COVERAGE_THRESHOLD must be drawn."""
    missing = missing_coverage(attribute_gaps(), run_sh_steps("FIGURES"))
    assert not missing, f"above {COVERAGE_THRESHOLD:.0%} of members, with no figure in run.sh: {missing}"


def test_a_coverage_figure_is_demanded_only_above_the_threshold():
    """The rule itself, on invented numbers: a large gap with no figure is
    named, a small one is not, and a large one with its figure is not."""
    gaps = {"members_race_coverage": 0.33, "members_age_coverage": 0.05}
    assert missing_coverage(gaps, []) == ["members_race_coverage"]
    assert missing_coverage(gaps, ["members_race_coverage"]) == []


def test_a_census_citation_beside_other_sources_still_counts_as_a_census_sheet():
    """The race coverage figure grades each member by the most direct source.
    A member cited to Hjerpe and to a census sheet rests on the sheet; one
    cited to no census rests on a published account; `assumed` is the
    default. If the first case fell to the published grade, the figure would
    understate how much of the early Board a census backs, with no error."""
    basis = members_by_year.race_basis
    assert basis("hjerpe2021 p.2; gazette1875schutt; census1880rowe") == "race_census"
    assert basis("ahs2026newman; dorsey2020") == "race_published"
    assert basis("assumed") == "race_default"


# --- the bibliography the paper prints -----------------------------------------

def cited_keys():
    """Every key the paper's LaTeX cites: the report, its timelines and the
    files they \\input. Read from the source rather than the .bcf, because the
    tests run before the paper is compiled and a .bcf is not committed. The
    timelines live outside paper/ (docs/timelines/), so every directory a
    paper.SOURCES document resolves into is searched too, not just paper/."""
    cited = set()
    dirs = {ROOT / "paper"} | {(ROOT / "paper" / path).resolve().parent
                               for path in paper.SOURCES.values()}
    for d in dirs:
        for tex in d.rglob("*.tex"):
            live = "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in tex.read_text().split("\n"))
            for m in re.finditer(r"\\\w*cite\w*\*?(?:\[[^\]]*\])*\{([^}]*)\}", live):
                cited |= {k.strip() for k in m.group(1).split(",")}
    return cited


# What a footnote may carry in `note`: a page, a volume, a short citation. The
# longest of those is a few words; a sentence of commentary is longer than any
# of them.
NOTE_LIMIT = 80
# An entry that lacks a field the copy does not give says so in its annotation.
NO_PAGE = re.compile(r"\bcopy (?:gives|shows|prints) no page", re.I)
NO_DATE = re.compile(r"\bpage (?:gives|shows|prints) no date", re.I)

def incomplete(e):
    """What a cited entry lacks that the bibliography's style sheet requires of
    its kind, or carries that the sheet forbids, as a list of sentences; empty
    when the entry follows the sheet (docs/repository.md, "The bibliography's
    style sheet"). A newspaper piece, an online piece, a report, a thesis, a
    case, an act and a census record each print differently, so each needs
    different fields and refuses different ones."""
    t, ann, note = e["type"], e.get("annotation", ""), archive.plain(e.get("note", ""))
    has = lambda *fields: any(e.get(f, "").strip() for f in fields)
    kind = archive.kind(e)
    need, out = [], []
    press = t == "article" and kind == "press"
    if press:
        # An unsigned piece has no author: the paper prints once, as journaltitle.
        need += [f for f in ("title", "journaltitle", "location", "date") if not has(f)]
        if not has("pages") and not NO_PAGE.search(ann):
            need.append("pages (or an annotation saying the copy gives no page)")
        if not has("pages") and has("url") and e.get("entrysubtype") != "magazine":
            out.append("has a url and no page: entrysubtype = {magazine}, or the footnote, which drops "
                       "the url, ends in a comma")
        if re.match(r"The\s", archive.plain(e.get("journaltitle", ""))):
            out.append("has a masthead that opens with The, which Chicago drops: Sun, not The Sun")
        for f in ("volume", "number", "issue", "note"):
            if has(f):
                out.append(f"has {f}, which a newspaper piece does not carry: "
                           f"the date and the page find it, and the rest goes in annotation")
    elif t == "article":
        need += [f for f in ("author", "title", "journaltitle", "date") if not has(f)]
    elif t == "online":
        need += [f for f in ("title", "url") if not has(f)]
        if not has("organization", "author"):
            need.append("an organization or an author")
        if not has("date") and not NO_DATE.search(ann):
            need.append("date (or an annotation saying the page gives no date)")
        if re.search(r"\bvia\b", e.get("organization", "")):
            out.append("names a host as well as the outlet (\"via\"): cite the paper that wrote the piece "
                       "as an @article, or the site as the organization, and the url says where it was read")
    elif t == "report":
        need += [f for f in ("title", "date") if not has(f)]
        if not has("institution", "author"):
            need.append("an institution or an author")
        if has("organization"):
            out.append("has organization, which a report does not print: the publisher is the institution")
        if has("author", "institution") and archive.plain(e.get("institution", "\0")) in archive.plain(e.get("author", "")):
            out.append(f"has {archive.plain(e['institution'])!r} as institution and inside its author, "
                       f"which prints twice; the institution is a publisher that differs from the author")
    elif t in ("phdthesis", "mastersthesis", "thesis"):
        need += [f for f in ("author", "title", "date") if not has(f)]
        if not has("institution", "school"):
            need.append("a school")
        if has("url") and re.fullmatch(r"https?://[^/]+/?", e["url"].strip()):
            out.append("has a url that is the repository's home page, not the document: use its handle")
    elif t == "book":
        need += [f for f in ("author", "title", "publisher") if not has(f)]
        if not has("date", "year"):
            need.append("a year")
    elif t == "jurisdiction":
        if not has("date"):
            need.append("date")
        if not re.search(r" v\.", e.get("title", "")):
            need.append("a caption with \"v.\" as its title")
        if not (has("journaltitle", "shortjournal") and has("volume") and has("pages")) \
                and not (has("number") and has("location")):
            need.append("a reporter (journaltitle, volume, pages), or for an unreported case a number and a court")
        for f in ("author", "note"):
            if has(f):
                out.append(f"has {f}: a case prints its caption and its reporter, and the court "
                           f"and the day go in location, date and annotation")
        if not has("sortname"):
            need.append("a sortname, braced (a location would otherwise file it): Legal Authorities sorts by it")
    elif t == "legislation":
        title = archive.plain(e.get("title", ""))
        need += [f for f in ("title", "date", "organization") if not has(f)]
        for f in ("author", "editor", "note"):
            if has(f):
                out.append(f"has {f}: a law is named by its own title, the sovereign goes in organization "
                           f"(it files the copy), and the rest goes in annotation")
        if title.startswith("Act of"):
            need += [f for f in ("titleaddon", "shortjournal", "volume", "shorttitle") if not has(f)]
            if "datedintitle" not in e.get("keywords", ""):
                need.append("keywords = {datedintitle}, since the date is in the title")
        if e.get("sorttitle", "") != e.get("date", "x"):
            need.append("sorttitle equal to its date, which orders Legal Authorities")
        if "Const" in title and e.get("entrysubtype") != "constitution":
            need.append("entrysubtype = {constitution}")
    elif kind == "legal":
        out.append(f"is a {t} about primary law, which prints in the Works Cited: "
                   f"cases are @jurisdiction and acts, constitutions and code sections are @legislation")
    if kind in ("census", "vital records") and "skipbib" not in e.get("options", ""):
        out.append("is a single record, cited in notes only: options = {skipbib}")
    if t not in ("jurisdiction", "legislation") and kind != "legal":
        title = archive.plain(e.get("title", ""))
        if title and archive.headline_case(title) != title:
            out.append(f"has a title that is not in headline style: {archive.headline_case(title)!r}")
    if re.search(r"\d{4}-\d{2,4}", e.get("title", "")):
        out.append("has a hyphen in a year range in its title: use an en dash (--)")
    # An unsigned piece files under its paper or outlet, braced so biber reads an
    # organization and not a person ("Daily Sun" unbraced files under S).
    if press or (t == "online" and kind == "press"):
        sortname = e.get("sortname", "")
        if not has("author") and not (sortname.startswith("{") and sortname.endswith("}")):
            out.append("is unsigned and files under its paper: sortname = {{Name}}, braced")
        if has("author") and sortname:
            out.append("is signed and files under its author: no sortname")
    out = [f"lacks {n}" for n in need] + out
    # The same name as author and as publisher prints twice.
    for f in ("journaltitle", "organization") if t in ("article", "online") else ():
        if has("author") and archive.plain(e["author"]) == archive.plain(e.get(f, "")):
            out.append(f"has {archive.plain(e['author'])!r} as author and as {f}, which prints twice; "
                       f"an unsigned piece has no author")
    if len(note) > NOTE_LIMIT:
        out.append(f"has a note of {len(note)} characters, which prints in the footnote; "
                   f"the footnote is the citation and the page, and the rest goes in annotation")
    return out


def test_an_incomplete_entry_is_refused():
    """Each mistake the Works Cited printed before the style sheet existed,
    built as an entry of its kind and handed to incomplete(). A newspaper entry
    whose author is the paper printed its name twice; one with no place or no
    page printed a citation that could not be found again; an unsigned one
    sorted by its title, or, with its sortname unbraced, under the last word of
    the paper's name. Each valid entry first shows the check is not simply
    refusing everything."""
    def refuses(base, change, saying):
        got = incomplete({**base, **change})
        assert any(saying in g for g in got), f"{change} not caught ({saying!r}): {got}"

    paper = {"type": "article", "key": "k", "title": "T", "journaltitle": "Sun",
             "location": "Arlington, Va.", "date": "1938-11-11", "pages": "1",
             "sortname": "{Sun}"}
    assert incomplete(paper) == [], incomplete(paper)
    for change, saying in (
            ({"author": "{Sun}"}, "prints twice"),
            ({"location": ""}, "location"),
            ({"pages": ""}, "pages"),
            ({"date": ""}, "date"),
            ({"journaltitle": ""}, "journaltitle"),
            ({"journaltitle": "The Sun"}, "opens with The"),
            ({"pages": "", "url": "https://example.org", "annotation": "The copy gives no page."}, "magazine"),
            ({"sortname": ""}, "sortname"),
            ({"sortname": "Sun"}, "sortname"),
            ({"author": "Sawicki, Phillip"}, "no sortname"),
            ({"note": "Vol. III, no. 49"}, "note"),
            ({"volume": "3"}, "volume"),
            ({"title": "Referendum wins by 61 votes"}, "headline style"),
            ({"title": "Voters in 1952-1954"}, "en dash")):
        refuses(paper, change, saying)
    # A copy that numbers no pages says so, and then needs none.
    assert incomplete({**paper, "pages": "", "annotation": "The copy gives no page number."}) == []

    web = {"type": "online", "key": "k", "title": "T", "organization": "ARLnow",
           "date": "2020-05-07", "url": "https://example.org", "sortname": "{ARLnow}"}
    assert incomplete(web) == [], incomplete(web)
    for change, saying in (({"author": "ARLnow"}, "prints twice"), ({"url": ""}, "url"),
                           ({"organization": ""}, "organization"), ({"date": ""}, "date"),
                           ({"organization": "Sun Gazette, via InsideNoVa"}, "via")):
        refuses(web, change, saying)
    assert incomplete({**web, "date": "", "annotation": "The page gives no date."}) == []

    report = {"type": "report", "key": "k", "author": "{FairVote}", "title": "T", "date": "2026-02-23"}
    assert incomplete(report) == []
    refuses(report, {"institution": "FairVote"}, "prints twice")
    refuses(report, {"organization": "FairVote"}, "organization")
    refuses({**report, "author": ""}, {}, "institution")

    thesis = {"type": "phdthesis", "key": "k", "author": "A", "title": "T", "date": "2017",
              "institution": "George Mason University", "url": "https://hdl.handle.net/1920/11125"}
    assert incomplete(thesis) == []
    refuses(thesis, {"url": "https://mars.gmu.edu/"}, "home page")
    refuses(thesis, {"institution": ""}, "school")
    refuses({"type": "book", "key": "k", "author": "A", "title": "T", "publisher": "P"}, {}, "year")

    # Primary law is cited in notes and never listed, so it must be a type
    # biblatex-chicago skips: a case, or an act, constitution or code section.
    case = {"type": "jurisdiction", "key": "k", "title": "Bennett v.\\ Garrett", "date": "1922-06-15",
            "journaltitle": "Va.", "volume": "132", "pages": "397",
            "sortname": "{Bennett v. Garrett}"}
    assert incomplete(case) == [], incomplete(case)
    refuses(case, {"sortname": ""}, "sortname")
    refuses(case, {"pages": ""}, "reporter")
    refuses(case, {"date": ""}, "date")
    refuses(case, {"note": "132 Va. 397 (1922)"}, "note")
    refuses(case, {"title": "Bennett"}, "caption")
    act = {"type": "legislation", "key": "k", "title": "Act of Mar.\\ 20, 1930", "date": "1930-03-20",
           "organization": "Commonwealth of Virginia", "titleaddon": "ch.\\ 167",
           "shortjournal": "Va. Acts", "volume": "1930", "shorttitle": "Act of Mar.\\ 20, 1930",
           "keywords": "datedintitle", "sorttitle": "1930-03-20"}
    assert incomplete(act) == [], incomplete(act)
    refuses(act, {"sorttitle": ""}, "sorttitle")
    for change, saying in (({"author": "{Commonwealth of Virginia}"}, "author"),
                           ({"note": "printed pp. 450--456"}, "note"),
                           ({"organization": ""}, "organization"),
                           ({"keywords": ""}, "datedintitle"),
                           ({"titleaddon": ""}, "titleaddon")):
        refuses(act, change, saying)
    constitution = {"type": "legislation", "key": "k", "title": "Va.\\ Const.\\ of 1869", "date": "1869",
                    "organization": "Commonwealth of Virginia", "entrysubtype": "constitution",
                    "sorttitle": "1869"}
    assert incomplete(constitution) == [], incomplete(constitution)
    refuses(constitution, {"entrysubtype": ""}, "constitution")
    # The mistake that listed some of Virginia's law and not the rest: an act typed @misc.
    refuses({"type": "misc", "key": "k", "title": "Acts of the General Assembly, Session of 1869--70",
             "date": "1870"}, {}, "primary law")

    # A single census line is cited in notes only.
    census = {"type": "misc", "key": "k", "title": "A in the 1880 United States Federal Census, Alexandria County, Virginia",
              "howpublished": "Ancestry.com, 1880 United States Federal Census [database on-line], record 1",
              "date": "1880-06-01", "options": "skipbib"}
    assert incomplete(census) == [], incomplete(census)
    refuses(census, {"options": ""}, "skipbib")


def test_every_cited_entry_is_complete():
    """The keys the paper cites, each through incomplete(). A key the bib does
    not define is the citation check's to refuse, not this one's."""
    bib = {e["key"]: e for e in archive.entries((ROOT / "paper" / "bib" / "sources.bib").read_text())}
    bad = [f"{k}: {p}" for k in sorted(cited_keys() & set(bib)) for p in incomplete(bib[k])]
    assert not bad, "cited entries the Works Cited would print incompletely:\n  " + "\n  ".join(bad)


# --- merging a thread's branch ---------------------------------------------------

def merge_fixture(tmp):
    """A bare remote and a clone with main pushed, a branch `thread` that
    appends a tracker row and edits note.txt, and main moved on by another
    tracker row, so the merge has a union file to resolve and a clean file
    to carry. Returns the clone's path.

    Also a bare, empty 'draft' remote, as publish_fixture makes one, so
    merge.sh's own pull and push steps have a real mirror to talk to and
    nothing to report: these tests are about the merge, not the mirror,
    which test_publish_* above covers on its own."""
    tmp = Path(tmp)
    remote, work = tmp / "remote.git", tmp / "work"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    subprocess.run(["git", "clone", "-q", str(remote), str(work)], check=True,
                   stderr=subprocess.DEVNULL)

    draft = tmp / "draft.git"
    subprocess.run(["git", "init", "-q", "--bare", str(draft)], check=True)
    draft_work = tmp / "draft-work"
    subprocess.run(["git", "clone", "-q", str(draft), str(draft_work)], check=True,
                   stderr=subprocess.DEVNULL)

    def dgit(*args):
        return subprocess.run(["git", "-C", str(draft_work), *args], check=True,
                              capture_output=True, text=True).stdout

    dgit("config", "user.email", "t@t"); dgit("config", "user.name", "t")

    def git(*args):
        return subprocess.run(["git", "-C", str(work), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    git("config", "user.email", "t@t"); git("config", "user.name", "t")
    (work / "code").mkdir(); (work / "docs").mkdir()
    (work / "paper").mkdir(); (work / "figures" / "pdf").mkdir(parents=True)
    # git archive -- paper figures/pdf style/fonts (code/publish.py push) needs
    # all three to hold a committed file, which an empty directory never does.
    (work / "paper" / "arlington-bsap.tex").write_text("\\documentclass{article}\n")
    (work / "figures" / "pdf" / "a.pdf").write_bytes(b"%PDF-fake\n")
    (work / "style" / "fonts").mkdir(parents=True)
    (work / "style" / "fonts" / "Lato-Regular.ttf").write_bytes(b"fake-font\n")
    shutil.copy(ROOT / "code" / "merge.sh", work / "code" / "merge.sh")
    shutil.copy(ROOT / "code" / "merge_questions.py", work / "code" / "merge_questions.py")
    shutil.copy(ROOT / "code" / "publish.py", work / "code" / "publish.py")
    shutil.copy(ROOT / "code" / "merge_punchlist.py", work / "code" / "merge_punchlist.py")
    (work / "docs" / "punchlist.md").write_text("first fix\nsecond fix\n")
    (work / ".gitattributes").write_text(
        "docs/questions.csv merge=questions\ndocs/punchlist.md merge=union\n")
    # The same driver string run.sh registers; merge.sh refuses without it.
    git("config", "merge.questions.driver", "python3 code/merge_questions.py %O %A %B")
    (work / "docs" / "questions.csv").write_text("a,b\n1,2\n")
    (work / "note.txt").write_text("x\n")
    git("add", "-A"); git("commit", "-qm", "base"); git("branch", "-M", "main")
    git("push", "-q", "-u", "origin", "main")
    git("checkout", "-qb", "thread")
    with open(work / "docs" / "questions.csv", "a") as f:
        f.write("3,4\n")
    (work / "note.txt").write_text("thread\n")
    git("commit", "-qam", "thread"); git("push", "-q", "-u", "origin", "thread")
    git("checkout", "-q", "main")
    with open(work / "docs" / "questions.csv", "a") as f:
        f.write("5,6\n")
    git("commit", "-qam", "main2"); git("push", "-q", "origin", "main")
    return work, git


def merge(work, build, compile_, **env):
    """Run code/merge.sh thread in the clone with the build and compile
    commands substituted. PYTHON and DRAFT_REMOTE point publish.py's pull
    and push steps at this fixture's own interpreter and draft remote
    (merge_fixture), so they report "nothing to pull" and a clean publish
    unless a test overrides one to look at the mirror itself. Returns the
    completed process."""
    draft = Path(work).parent / "draft.git"
    return subprocess.run(["bash", "code/merge.sh", "thread"], cwd=work, text=True,
                          capture_output=True,
                          env={**os.environ, "BUILD": build, "COMPILE": compile_,
                               "PYTHON": sys.executable, "DRAFT_REMOTE": str(draft), **env})


def test_a_merge_whose_build_fails_leaves_main_alone():
    """The first slip: a commit chained after a failing build. The script
    stops at step 3, main is where it was, and no worktree is left behind."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git = merge_fixture(tmp)
        before = git("rev-parse", "main")
        run = merge(work, build="false", compile_="true")
        assert run.returncode != 0, "a failing build did not stop the merge"
        assert "build failed" in run.stderr, run.stderr
        assert git("rev-parse", "main") == before, "main moved after a failing build"
        assert git("rev-parse", "origin/main") == before, "origin/main moved after a failing build"
        assert git("worktree", "list").count("\n") == 0, "the scratch worktree was left behind"


def test_a_merge_whose_build_passes_lands_with_what_the_build_rewrote():
    """The happy path, and the third slip: a file the build rewrote in the
    worktree reaches main instead of going with the worktree. The union
    file keeps both sides' rows, the branch is gone here and on the remote."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git = merge_fixture(tmp)
        run = merge(work, build="echo built > note.txt", compile_="true")
        assert run.returncode == 0, run.stdout + run.stderr
        assert (work / "note.txt").read_text() == "built\n", "the build's rewrite was lost"
        assert (work / "docs" / "questions.csv").read_text() == "a,b\n1,2\n5,6\n3,4\n", \
            "the union merge did not keep both sides' rows"
        assert git("rev-parse", "main") == git("rev-parse", "origin/main"), "main was not pushed"
        assert "thread" not in git("branch", "-a"), "the merged branch was not removed"
        assert git("worktree", "list").count("\n") == 0, "the scratch worktree was left behind"


def test_a_merge_with_a_real_conflict_stops_before_building():
    """A conflict outside the union-merged files is a person's decision:
    the script names the file and leaves main alone."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git = merge_fixture(tmp)
        (work / "note.txt").write_text("main side\n")
        git("commit", "-qam", "main3"); git("push", "-q", "origin", "main")
        before = git("rev-parse", "main")
        run = merge(work, build="true", compile_="true")
        assert run.returncode != 0, "a conflicting merge went through"
        assert "note.txt" in run.stderr and "conflicts" in run.stderr, run.stderr
        assert git("rev-parse", "main") == before, "main moved despite the conflict"
        assert git("worktree", "list").count("\n") == 0, "the scratch worktree was left behind"


def delete_on_thread_change_on_main(work, git, path):
    """The 7 October 2026 shape: the thread deletes a tracked file and main,
    which has moved on, changes it. A second figure keeps figures/pdf from
    being empty after the deletion, which the mirror's export needs."""
    git("checkout", "-q", "thread")
    git("rm", "-q", path); git("commit", "-qm", "thread deletes it"); git("push", "-q", "origin", "thread")
    git("checkout", "-q", "main")
    (work / path).write_bytes(b"%PDF-rebuilt on main\n")
    (work / "figures" / "pdf" / "b.pdf").write_bytes(b"%PDF-fake-b\n")
    git("add", "-A"); git("commit", "-qm", "main rebuilds it"); git("push", "-q", "origin", "main")


def test_a_merge_takes_the_branchs_side_of_a_deleted_build_output():
    """A branch deleted figures/pdf/a.pdf while main rebuilt it: git stops
    with modify/delete and no guidance, and a thread had to resolve it in a
    scratch worktree by hand. A build output is the build's to recreate, so
    the branch's side is taken and the merge goes on."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git = merge_fixture(tmp)
        delete_on_thread_change_on_main(work, git, "figures/pdf/a.pdf")
        run = merge(work, build="true", compile_="true")
        assert run.returncode == 0, run.stdout + run.stderr
        assert not (work / "figures" / "pdf" / "a.pdf").exists(), "the deletion was not kept"
        assert git("rev-parse", "main") == git("rev-parse", "origin/main"), "main was not pushed"


def test_a_merge_does_not_bring_back_a_punch_list_line_the_branch_deleted():
    """docs/punchlist.md merges by union, so a branch that clears the last
    item while main appends another leaves one disputed hunk, and the union
    keeps both sides: the cleared item is open again. The merge removes it
    and says which line."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git = merge_fixture(tmp)
        git("checkout", "-q", "thread")
        (work / "docs" / "punchlist.md").write_text("first fix\n")
        git("commit", "-qam", "thread clears the second fix"); git("push", "-q", "origin", "thread")
        git("checkout", "-q", "main")
        with open(work / "docs" / "punchlist.md", "a") as f:
            f.write("third fix\n")
        git("commit", "-qam", "main adds a fix"); git("push", "-q", "origin", "main")
        run = merge(work, build="true", compile_="true")
        assert run.returncode == 0, run.stdout + run.stderr
        left = (work / "docs" / "punchlist.md").read_text()
        assert left == "first fix\nthird fix\n", f"punch list after the merge:\n{left}"
        assert "second fix" in run.stdout, "the removed line was not named"


def test_a_merge_stops_on_a_deleted_file_that_is_not_a_build_output():
    """The same conflict on a file the build does not write is a person's
    decision: the script names it and the two commands that settle it, and
    main is where it was."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git = merge_fixture(tmp)
        git("checkout", "-q", "thread")
        git("rm", "-q", "note.txt"); git("commit", "-qm", "thread deletes it"); git("push", "-q", "origin", "thread")
        git("checkout", "-q", "main")
        (work / "note.txt").write_text("main side\n")
        git("commit", "-qam", "main changes it"); git("push", "-q", "origin", "main")
        before = git("rev-parse", "main")
        run = merge(work, build="true", compile_="true")
        assert run.returncode != 0, "a modify/delete conflict on a non-output went through"
        assert "note.txt" in run.stderr and "git rm -- note.txt" in run.stderr \
            and "--ours -- note.txt" in run.stderr, run.stderr
        assert git("rev-parse", "main") == before, "main moved despite the conflict"
        assert git("worktree", "list").count("\n") == 0, "the scratch worktree was left behind"


def hold_thread_in_worktree(work, git):
    """The thread's own worktree, as a session working on it would have one."""
    git("worktree", "add", "-q", ".claude/worktrees/t", "thread")
    return work / ".claude" / "worktrees" / "t"


def test_a_merge_removes_the_threads_worktree_only_when_it_is_clean_and_unheld():
    """The cleanup that removed two live threads' worktrees on 6 October 2026
    asked nothing of them. Removal needs the branch merged (the fast-forward
    does that), the tree clean, and no lock. A clean unlocked worktree goes;
    a dirty one and a locked one stay, with their branch, and main still
    lands. The remote is origin whatever the environment says."""
    for case in ("clean", "dirty", "locked"):
        with tempfile.TemporaryDirectory() as tmp:
            work, git = merge_fixture(tmp)
            held = hold_thread_in_worktree(work, git)
            if case == "dirty":
                (held / "scratch.txt").write_text("unsaved\n")
            if case == "locked":
                git("worktree", "lock", str(held))
            run = merge(work, build="true", compile_="true", REMOTE="nowhere")
            assert run.returncode == 0, case + ": " + run.stdout + run.stderr
            assert git("rev-parse", "main") == git("rev-parse", "origin/main"), case + ": main was not pushed"
            if case == "clean":
                assert not held.exists(), "a clean, merged, unlocked worktree was left behind"
                assert "thread" not in git("branch"), "its branch was left behind"
            else:
                assert held.exists(), f"a {case} worktree was removed"
                assert "thread" in git("branch"), f"the branch of a {case} worktree was deleted"
                assert "kept" in run.stdout, run.stdout


def test_a_merge_from_a_worktree_says_where_to_run_it():
    """The script refuses in a worktree, and used to refuse without saying
    why. It names the primary checkout and the command to run there."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git = merge_fixture(tmp)
        held = hold_thread_in_worktree(work, git)
        run = subprocess.run(["bash", "code/merge.sh", "thread"], cwd=held, text=True,
                             capture_output=True)
        assert run.returncode != 0, "a merge from a worktree went through"
        assert str(work.resolve()) in run.stderr and "bash code/merge.sh thread" in run.stderr, run.stderr


def test_a_merge_without_the_tracker_driver_refuses():
    """Without the driver git quietly falls back to its own merge of the
    tracker, which is the line-based merge this replaced."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git = merge_fixture(tmp)
        git("config", "--unset", "merge.questions.driver")
        before = git("rev-parse", "main")
        run = merge(work, build="true", compile_="true")
        assert run.returncode != 0 and "merge driver" in run.stderr, run.stdout + run.stderr
        assert git("rev-parse", "main") == before


# --- publishing to the Overleaf mirror ---------------------------------------------------

@contextlib.contextmanager
def draft_remote(url):
    """publish.py's DRAFT_REMOTE override, the way code/merge.sh's REMOTE
    override works, scoped to the block so parallel tests in other worker
    processes never see it."""
    old = os.environ.get("DRAFT_REMOTE")
    os.environ["DRAFT_REMOTE"] = str(url)
    try:
        yield
    finally:
        if old is None:
            os.environ.pop("DRAFT_REMOTE", None)
        else:
            os.environ["DRAFT_REMOTE"] = old


def publish_fixture(tmp):
    """A bare 'whole' remote holding paper/, figures/pdf/, style/fonts/ and a file outside
    both (code/notes.py, which a push must never carry to the mirror), and a
    bare 'draft' remote, empty as a mirror repository is when it has just been
    created, with a clone of it for the tests that act as Overleaf. Returns the work
    clone's path, its git() helper, and the draft-work clone's path for
    simulating an edit made in Overleaf."""
    tmp = Path(tmp)
    whole, draft = tmp / "whole.git", tmp / "draft.git"
    subprocess.run(["git", "init", "-q", "--bare", str(whole)], check=True)
    subprocess.run(["git", "init", "-q", "--bare", str(draft)], check=True)

    draft_work = tmp / "draft-work"
    subprocess.run(["git", "clone", "-q", str(draft), str(draft_work)], check=True,
                   stderr=subprocess.DEVNULL)

    def dgit(*args):
        return subprocess.run(["git", "-C", str(draft_work), *args], check=True,
                              capture_output=True, text=True).stdout


    dgit("config", "user.email", "t@t"); dgit("config", "user.name", "t")

    work = tmp / "work"
    subprocess.run(["git", "clone", "-q", str(whole), str(work)], check=True,
                   stderr=subprocess.DEVNULL)

    def git(*args):
        return subprocess.run(["git", "-C", str(work), *args], check=True,
                              capture_output=True, text=True).stdout

    git("config", "user.email", "t@t"); git("config", "user.name", "t")
    (work / "paper").mkdir(); (work / "figures" / "pdf").mkdir(parents=True)
    (work / "style" / "fonts").mkdir(parents=True)
    (work / "code").mkdir()
    (work / "paper" / "arlington-bsap.tex").write_text("\\documentclass{article}\n")
    (work / "figures" / "pdf" / "a.pdf").write_bytes(b"%PDF-fake\n")
    (work / "style" / "fonts" / "Lato-Regular.ttf").write_bytes(b"fake-font\n")
    (work / "code" / "notes.py").write_text("not published\n")
    git("add", "-A"); git("commit", "-qm", "seed"); git("branch", "-M", "main")
    git("push", "-q", "-u", "origin", "main")
    return work, git, draft_work


def test_publish_push_writes_only_paper_figures_and_fonts():
    """The happy path, on a mirror repository just created and still empty
    (origin/main does not exist): the first push is a root commit pushed as
    main, carrying paper/, figures/pdf/ and style/fonts/ only - code/notes.py
    never reaches the mirror - and a second push on top of it finds that
    commit at the tip and goes through."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        with draft_remote(Path(tmp) / "draft.git"):
            assert publish.push(repo=work), "the first push to an empty mirror reported nothing"
            (work / "paper" / "arlington-bsap.tex").write_text("% second\n")
            git("commit", "-qam", "second")
            assert publish.push(repo=work), "the second push did not go through"
        subprocess.run(["git", "-C", str(draft_work), "pull", "-q", "origin", "main"], check=True)
        tracked = subprocess.run(["git", "-C", str(draft_work), "ls-files"], check=True,
                                 capture_output=True, text=True).stdout.split()
        assert set(tracked) == {"paper/arlington-bsap.tex", "figures/pdf/a.pdf",
                                "style/fonts/Lato-Regular.ttf"}, tracked


def test_publish_push_refuses_when_the_mirror_is_ahead():
    """An edit made in Overleaf must never be silently overwritten: once the
    mirror's tip is not a commit of ours, a push refuses and names the pull
    command instead of discarding what is there."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        with draft_remote(Path(tmp) / "draft.git"):
            publish.push(repo=work)
            subprocess.run(["git", "-C", str(draft_work), "pull", "-q"], check=True)
            (draft_work / "paper" / "arlington-bsap.tex").write_text("% an edit made in Overleaf\n")
            subprocess.run(["git", "-C", str(draft_work), "commit", "-qam", "overleaf edit"], check=True)
            subprocess.run(["git", "-C", str(draft_work), "push", "-q"], check=True)
            try:
                publish.push(repo=work)
                assert False, "a push over an unabsorbed Overleaf edit went through"
            except SystemExit as e:
                assert "pull" in str(e), e


def test_publish_pull_before_any_publish_is_a_noop():
    """Before the first push there is no baseline to read Overleaf's edits
    against, so a pull reports nothing - which code/merge.sh's own first run
    depends on, since its first step is this pull and its last is the first
    push."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        with draft_remote(Path(tmp) / "draft.git"):
            result = publish.pull(repo=work)
        assert result is None, result
        assert "overleaf-" not in git("branch")


def test_publish_pull_refuses_a_change_under_figures():
    """Figures are built here; Overleaf is never the source of one. A pull
    that would bring one back is refused outright, with nothing applied."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        with draft_remote(Path(tmp) / "draft.git"):
            publish.push(repo=work)
            subprocess.run(["git", "-C", str(draft_work), "pull", "-q"], check=True)
            (draft_work / "figures" / "pdf" / "a.pdf").write_bytes(b"%PDF-edited-in-overleaf\n")
            subprocess.run(["git", "-C", str(draft_work), "commit", "-qam", "edited a figure in Overleaf"],
                           check=True)
            subprocess.run(["git", "-C", str(draft_work), "push", "-q"], check=True)
            before = git("rev-parse", "main").strip()
            try:
                publish.pull(repo=work)
                assert False, "a pull touching figures/ went through"
            except SystemExit as e:
                assert "figures" in str(e), e
            assert git("rev-parse", "main").strip() == before, "a refused pull still moved main"
            assert "overleaf-" not in git("branch"), "a refused pull still left a branch behind"


def test_publish_push_refuses_a_tree_holding_a_path_outside_the_two_folders():
    """The guard that runs right before the commit that would ship to
    Overleaf: if anything outside paper/ or figures/pdf/ were ever tracked
    in the mirror - a bug in the export, not something normal use reaches -
    the push stops instead of carrying it there."""
    with tempfile.TemporaryDirectory() as tmp:
        draft = Path(tmp) / "draft"
        subprocess.run(["git", "init", "-q", str(draft)], check=True)
        subprocess.run(["git", "-C", str(draft), "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", str(draft), "config", "user.name", "t"], check=True)
        (draft / "paper").mkdir()
        (draft / "paper" / "arlington-bsap.tex").write_text("x\n")
        (draft / "stray.txt").write_text("should never reach the mirror\n")
        subprocess.run(["git", "-C", str(draft), "add", "-A"], check=True)
        try:
            publish.verify_tree(draft)
            assert False, "a tracked path outside paper/ and figures/pdf/ was not refused"
        except SystemExit as e:
            assert "stray.txt" in str(e), e


def wrapper(body, others=None):
    """A repository's files as publish.unmirrored reads them: a wrapper with
    this body, the font and figure the mirror does carry, and any others."""
    return {"paper/arlington-bsap.tex": body,
            "style/fonts/Lato-Regular.ttf": "", "figures/pdf/a.pdf": "",
            "paper/bib/sources.bib": "", **(others or {})}


def test_the_mirror_refuses_a_paper_that_loads_a_file_it_does_not_carry():
    """The Lato files were missing from the first mirror and Overleaf could not
    compile; Sally found it from a screenshot. Every path the paper loads from
    outside paper/ has to be inside the mirror (publish.ALLOWED), whichever
    way the .tex file names it: a font folder, a figure folder or a figure
    named outright, a bibliography, a file \\input from outside paper/, or
    a file read through an \\input that is itself nested."""
    good = ("\\setmainfont{Lato}[Path = ../style/fonts/, Extension = .ttf]\n"
            "\\graphicspath{{../figures/pdf/}}\n\\addbibresource{bib/sources.bib}\n"
            "\\begin{document}\\includegraphics{a.pdf}\\end{document}\n")
    assert publish.unmirrored(wrapper(good)) == [], publish.unmirrored(wrapper(good))

    def refused(body, path, others=None):
        found = publish.unmirrored(wrapper(body, others))
        assert [p for _, _, p in found] == [path], (body, found)

    refused(good.replace("../style/fonts/", "../style/other/"), "style/other")
    moved = publish.unmirrored(wrapper(good.replace("{{../figures/pdf/}}", "{{../figures/png/}}"),
                                       {"figures/png/a.pdf": ""}))
    assert [p for _, _, p in moved] == ["figures/png", "figures/png/a.pdf"], moved
    refused(good.replace("{a.pdf}", "{../figures/png/b.png}"), "figures/png/b.png",
            {"figures/png/b.png": ""})
    refused(good.replace("bib/sources.bib", "../data/refs.bib"), "data/refs.bib")
    refused(good + "\\input{../code/macros}\n", "code/macros.tex", {"code/macros.tex": ""})
    # Nested: paper/part.tex, read through the wrapper, loads the stray font.
    refused(good + "\\input{part}\n", "style/other",
            {"paper/part.tex": "\\setsansfont{X}[Path=../style/other/]\n"})
    # TeX's own \\input, with no braces, as the roster files are read.
    refused("\\makeatletter\\let\\rosterinput\\@@input\\makeatother\n" + good + "\\rosterinput ../data/r.tex\n",
            "data/r.tex", {"data/r.tex": ""})
    # A commented-out reference loads nothing.
    assert publish.unmirrored(wrapper(good + "% \\input{../code/macros}\n")) == []


def test_the_papers_own_references_are_all_in_the_mirror():
    """The integration test of the guard above, against the committed paper."""
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True,
                             capture_output=True, text=True).stdout.splitlines()
    files = {f: ((ROOT / f).read_text() if f.endswith(".tex") else "")
             for f in tracked if (ROOT / f).exists()}
    assert publish.unmirrored(files) == [], publish.unmirrored(files)


def test_publish_push_refuses_a_paper_that_loads_outside_the_mirror():
    """The same guard where it bites: push stops before exporting anything,
    naming the file, and the mirror has no commit of ours."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        (work / "paper" / "arlington-bsap.tex").write_text(
            "\\setmainfont{Lato}[Path=../style/other/]\n")
        git("commit", "-qam", "loads a font from outside the mirror")
        with draft_remote(Path(tmp) / "draft.git"):
            try:
                publish.push(repo=work)
                assert False, "a push of a paper loading outside the mirror went through"
            except SystemExit as e:
                assert "style/other" in str(e), e
        heads = subprocess.run(["git", "-C", str(Path(tmp) / "draft.git"), "branch"], check=True,
                               capture_output=True, text=True).stdout
        assert heads.strip() == "", "the mirror received a commit"


def test_publish_pull_applies_an_overleaf_edit_on_its_own_branch():
    """The other happy path: a change Overleaf made under paper/ comes back
    on overleaf-<date>, main untouched, ready for code/merge.sh. The branch
    is built and committed in a worktree (see
    test_publish_pull_commits_in_a_worktree_so_a_live_session_cannot_strand_it),
    so the primary checkout itself never leaves main."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        with draft_remote(Path(tmp) / "draft.git"):
            publish.push(repo=work)
            subprocess.run(["git", "-C", str(draft_work), "pull", "-q"], check=True)
            (draft_work / "paper" / "arlington-bsap.tex").write_text("% written in Overleaf\n")
            subprocess.run(["git", "-C", str(draft_work), "commit", "-qam", "overleaf edit"], check=True)
            subprocess.run(["git", "-C", str(draft_work), "push", "-q"], check=True)
            before = git("rev-parse", "main").strip()
            branch = publish.pull(repo=work)
        assert branch and branch.startswith("overleaf-"), branch
        assert git("rev-parse", "main").strip() == before, "pull moved main instead of a new branch"
        assert git("rev-parse", "--abbrev-ref", "HEAD").strip() == "main", \
            "pull left the primary checkout on the new branch instead of a worktree"
        worktree_file = subprocess.run(
            ["git", "-C", str(work), "show", f"{branch}:paper/arlington-bsap.tex"],
            check=True, capture_output=True, text=True).stdout
        assert worktree_file == "% written in Overleaf\n"


def test_publish_pull_commits_in_a_worktree_so_a_live_session_cannot_strand_it():
    """The first fault, found 8 October 2026: pull used to commit its branch
    directly in the primary checkout, which .githooks/pre-commit refuses
    while another session is live there - the pull died with a staged patch
    and no commit. The fix commits in a worktree instead, where the hook
    never runs at all (it answers only for the primary checkout), so a live
    session cannot block it. This reintroduces the hook and a live session
    and checks pull still produces a commit, the primary checkout stays on
    main with nothing staged, and the branch is reachable locally."""
    keep = []
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        (work / ".githooks").mkdir()
        shutil.copy(ROOT / ".githooks" / "pre-commit", work / ".githooks" / "pre-commit")
        (work / ".githooks" / "pre-commit").chmod(0o755)
        (work / ".claude").mkdir()
        shutil.copy(ROOT / ".claude" / "sessions.sh", work / ".claude" / "sessions.sh")
        git("config", "core.hooksPath", ".githooks")
        git("add", "-A"); git("commit", "-qm", "the commit guard, for this test")
        socks = Path(tmp) / "socks"
        socks.mkdir()
        old_socks = os.environ.get("CC_SOCKS")
        os.environ["CC_SOCKS"] = str(socks)
        try:
            a_session(socks, work, keep)   # another session, live in this checkout
            with draft_remote(Path(tmp) / "draft.git"):
                publish.push(repo=work)
                subprocess.run(["git", "-C", str(draft_work), "pull", "-q"], check=True)
                (draft_work / "paper" / "arlington-bsap.tex").write_text("% from overleaf\n")
                subprocess.run(["git", "-C", str(draft_work), "commit", "-qam", "overleaf edit"],
                               check=True)
                subprocess.run(["git", "-C", str(draft_work), "push", "-q"], check=True)
                before = git("rev-parse", "main").strip()
                branch = publish.pull(repo=work)
            assert branch, "pull did not produce a branch while a session was live"
            assert git("rev-parse", "main").strip() == before, "pull moved main"
            assert git("branch", "--show-current").strip() == "main", \
                "pull left the primary checkout on another branch"
            assert git("status", "--porcelain").strip() == "", \
                "pull left something staged in the primary checkout"
            log = subprocess.run(["git", "-C", str(work), "log", "-1", "--format=%s", branch],
                                 check=True, capture_output=True, text=True).stdout
            assert log.strip().startswith("Overleaf edit:"), "the branch carries no commit"
            assert not (work / ".claude" / "worktrees" / branch).exists(), \
                "the worktree pull used was left behind"
        finally:
            if old_socks is None:
                os.environ.pop("CC_SOCKS", None)
            else:
                os.environ["CC_SOCKS"] = old_socks
            close_all(keep)


def test_publish_pull_twice_with_nothing_new_is_a_noop():
    """The second fault: after a pull, nothing marked the mirror's commit as
    absorbed, so merge.sh's next run called pull again, found the same
    diff, and tried to create the same branch - failing on "already
    exists" and stopping the merge. A second pull with nothing new on the
    mirror now reports the existing branch instead of recreating it, and
    changes nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        with draft_remote(Path(tmp) / "draft.git"):
            publish.push(repo=work)
            subprocess.run(["git", "-C", str(draft_work), "pull", "-q"], check=True)
            (draft_work / "paper" / "arlington-bsap.tex").write_text("% from overleaf\n")
            subprocess.run(["git", "-C", str(draft_work), "commit", "-qam", "overleaf edit"],
                           check=True)
            subprocess.run(["git", "-C", str(draft_work), "push", "-q"], check=True)
            first = publish.pull(repo=work)
            assert first, "the first pull produced no branch"
            before = git("rev-parse", first).strip()
            second = publish.pull(repo=work)
        assert second == first, "a second pull with nothing new made a different branch"
        assert git("rev-parse", second).strip() == before, "the second pull changed the branch"
        assert not any((work / ".claude" / "worktrees").glob("*")), \
            "the second pull left a worktree behind"


def test_publish_pull_reports_nothing_to_pull_when_main_already_has_the_edit_by_hand():
    """bd806cb reached main as dcf8391 on 8 October 2026 merged by hand, with
    the branch pull would have made never created and no record anywhere
    that the edit was absorbed. A pull against that state used to try to
    apply the same patch again and fail - the text it is patching in is
    already there. It now recognises the edit is already in main (reversing
    the diff applies cleanly) and reports nothing to pull instead."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        with draft_remote(Path(tmp) / "draft.git"):
            publish.push(repo=work)
            subprocess.run(["git", "-C", str(draft_work), "pull", "-q"], check=True)
            (draft_work / "paper" / "arlington-bsap.tex").write_text("% from overleaf\n")
            subprocess.run(["git", "-C", str(draft_work), "commit", "-qam", "overleaf edit"],
                           check=True)
            subprocess.run(["git", "-C", str(draft_work), "push", "-q"], check=True)
            # The hand-merge: the same change, committed straight to main,
            # with no overleaf-<date> branch and no second push.
            (work / "paper" / "arlington-bsap.tex").write_text("% from overleaf\n")
            git("commit", "-qam", "merged the overleaf edit by hand")
            before = git("rev-parse", "main").strip()
            result = publish.pull(repo=work)
        assert result is None, "a hand-merged edit was pulled again instead of recognised"
        assert git("rev-parse", "main").strip() == before, "pull moved main"
        assert not any((work / ".claude" / "worktrees").glob("*")), \
            "a hand-merged edit still left a worktree behind"


def test_publish_push_accepts_a_hand_merged_edit_as_absorbed():
    """The other side of the same fault: with the edit in main by hand and no
    second push recording it, push used to see the mirror's tip as
    something Overleaf did that main had not absorbed and refuse. It now
    recognises main already carries that edit and publishes on top of the
    mirror's tip, restoring the bookkeeping pull and push both read."""
    with tempfile.TemporaryDirectory() as tmp:
        work, git, draft_work = publish_fixture(tmp)
        with draft_remote(Path(tmp) / "draft.git"):
            publish.push(repo=work)
            subprocess.run(["git", "-C", str(draft_work), "pull", "-q"], check=True)
            (draft_work / "paper" / "arlington-bsap.tex").write_text("% from overleaf\n")
            subprocess.run(["git", "-C", str(draft_work), "commit", "-qam", "overleaf edit"],
                           check=True)
            subprocess.run(["git", "-C", str(draft_work), "push", "-q"], check=True)
            overleaf_tip = subprocess.run(["git", "-C", str(draft_work), "rev-parse", "HEAD"],
                                          check=True, capture_output=True, text=True).stdout.strip()
            (work / "paper" / "arlington-bsap.tex").write_text("% from overleaf\n")
            git("commit", "-qam", "merged the overleaf edit by hand")
            head = publish.push(repo=work)
        assert head, "push refused a state main had already absorbed by hand"
        subprocess.run(["git", "-C", str(draft_work), "pull", "-q"], check=True)
        parent = subprocess.run(["git", "-C", str(draft_work), "rev-parse", "HEAD^"],
                                check=True, capture_output=True, text=True).stdout.strip()
        assert parent == overleaf_tip, "the new publish did not land on top of the mirror's tip"


# --- merging the tracker by row ---------------------------------------------------

TRACKER_HEADER = "id,kind,question\n"


def tracker_merge(base, main, branch):
    """The tracker's three versions merged by real git with the registered
    driver, as code/merge.sh would. Each argument is a list of rows. Returns
    (git's exit code, the file git left)."""
    def text(rows):
        return TRACKER_HEADER + "".join(r + "\n" for r in rows)
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "code").mkdir(); (repo / "docs").mkdir()
        shutil.copy(ROOT / "code" / "merge_questions.py", repo / "code" / "merge_questions.py")
        (repo / ".gitattributes").write_text("docs/questions.csv merge=questions\n")
        tracker = repo / "docs" / "questions.csv"

        def git(*args):
            return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
        git("init", "-q", "-b", "main")
        git("config", "user.email", "t@t"); git("config", "user.name", "t")
        git("config", "merge.questions.driver", "python3 code/merge_questions.py %O %A %B")
        tracker.write_text(text(base)); git("add", "-A"); git("commit", "-qm", "base")
        git("checkout", "-qb", "branch"); tracker.write_text(text(branch)); git("commit", "-qam", "branch")
        git("checkout", "-q", "main"); tracker.write_text(text(main)); git("commit", "-qam", "main")
        merged = git("merge", "-q", "-m", "m", "branch")
        return merged.returncode, tracker.read_text()


# --- raw files stored gzip-compressed -----------------------------------------------

def test_a_fetched_file_is_gzipped_the_same_way_every_time():
    """data/contents.csv holds each raw file's checksum, and a refetch that
    changed it would read as a source that moved. A gzip header carries the
    time and the name by default, so fetch/paths.write_text writes neither:
    the same text gives the same bytes at any hour, and pandas reads it back
    unchanged."""
    text = "name,n\nArlington,1\n"
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a" / "t.csv.gz", Path(tmp) / "b" / "t.csv.gz"
        fetch_paths.write_text(a, text)
        fetch_paths.write_text(b, text)
        assert a.read_bytes() == b.read_bytes(), "the same text gave different gzip bytes"
        assert a.read_bytes()[4:8] == b"\0\0\0\0", "the gzip header carries a time"
        assert pd.read_csv(a).to_csv(index=False) == text, "pandas did not read back what was written"
        plain = Path(tmp) / "p.csv"
        fetch_paths.write_text(plain, text)
        assert plain.read_text() == text, "a path not ending .gz was compressed"


# --- one process per stage ----------------------------------------------------------

def test_a_stage_runs_its_steps_in_one_process_each_checked_against_its_own_reads():
    """code/stage.py runs a stage's steps in one process, which is where a
    list kept at module level (build/paths.py remembers every table a step
    read, for write()'s check) would carry step one's sources into step
    two's check. A step starts with nothing remembered, the steps run in the
    order given, and a step that fails stops the stage with its name."""
    with tempfile.TemporaryDirectory() as tmp:
        code = Path(tmp) / "code"
        (code / "build").mkdir(parents=True)
        shutil.copy(ROOT / "code" / "stage.py", code / "stage.py")
        (code / "build" / "paths.py").write_text(
            "_INPUTS = []\ndef begin_step():\n    _INPUTS.clear()\n")
        steps = {"a": "import paths; paths._INPUTS.append(1); print('a saw', len(paths._INPUTS))",
                 "b": "import paths; print('b saw', len(paths._INPUTS))",
                 "c": "raise ValueError('boom')",
                 "d": "print('d ran')"}
        for name, body in steps.items():
            (code / "build" / f"{name}.py").write_text(body + "\n")

        def run(*names):
            return subprocess.run([sys.executable, str(code / "stage.py"), "build", *names],
                                  capture_output=True, text=True)
        ok = run("a", "b")
        assert ok.returncode == 0, ok.stderr
        assert ok.stdout.split("\n")[:2] == ["a saw 1", "b saw 0"], \
            "a step started with the previous step's reads, or the steps ran out of order: " + ok.stdout
        stopped = run("a", "c", "d")
        assert stopped.returncode != 0, "a failing step did not stop the stage"
        assert "build step c failed" in stopped.stderr and "d ran" not in stopped.stdout, \
            stopped.stdout + stopped.stderr


def test_a_row_closed_on_main_is_not_resurrected_by_a_merge():
    """The union merge kept both sides of every differing hunk, so a row main
    had closed came back when the branch edited a row beside it. Judged by
    id against the ancestor, a row the branch left alone stays gone."""
    base = ["a,x,first", "b,x,second", "c,x,third"]
    code, text = tracker_merge(base, main=["a,x,first", "c,x,third"],
                               branch=["a,x,first", "b,x,second", "c,x,third edited"])
    assert code == 0, text
    assert text == TRACKER_HEADER + "a,x,first\nc,x,third edited\n", text


def test_a_row_edited_on_both_sides_of_a_merge_is_a_conflict():
    """Two sessions editing one row is a person's decision, and the file
    holds both versions for them. An edit against a deletion is the same."""
    base = ["a,x,first", "b,x,second"]
    code, text = tracker_merge(base, main=["a,x,main edit", "b,x,second"],
                               branch=["a,x,branch edit", "b,x,second"])
    assert code != 0, "a row edited on both sides merged cleanly"
    assert "main edit" in text and "branch edit" in text and "<<<<<<<" in text, text
    code, text = tracker_merge(base, main=["a,x,first"], branch=["a,x,first", "b,x,edited"])
    assert code != 0, "an edit against a deletion merged cleanly"


def test_rows_each_side_added_are_both_kept_in_main_order_then_the_branchs():
    """The merge the tracker needs most: sessions append rows in parallel.
    Main's rows keep main's order and the branch's additions follow."""
    code, text = tracker_merge(["a,x,first"], main=["a,x,first", "m,x,main row"],
                               branch=["a,x,first", "n,x,branch row"])
    assert code == 0, text
    assert text == TRACKER_HEADER + "a,x,first\nm,x,main row\nn,x,branch row\n", text


def test_a_quoted_row_of_the_tracker_is_compared_as_one_record():
    """A question is quoted, with commas and doubled quotes inside; the
    driver reads a record, not a line, and writes the bytes it was given."""
    row = 'q,x,"has, a comma and ""quotes"""'
    assert merge_questions.rows(TRACKER_HEADER + row + "\n")[1]["q"] == row + "\n"


# --- the build cache ----------------------------------------------------------

@contextlib.contextmanager
def cache_repo():
    """A throwaway git repository standing in for this one, so the cache
    reads its keys and keeps its entries there and not in the real tree."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        (root / ".venv" / "bin").mkdir(parents=True)     # cache.environment() reads the venv
        (root / ".venv" / "bin" / "python").write_text("")
        saved = cache.ROOT, paper.ROOT, paper.PAPER, paper.BUILD
        cache.ROOT, paper.ROOT, paper.PAPER = root, root, root / "paper"
        paper.BUILD = paper.PAPER / "build"
        try:
            yield root
        finally:
            cache.ROOT, paper.ROOT, paper.PAPER, paper.BUILD = saved


def test_a_cache_key_follows_the_bytes_not_the_time():
    """Why the cache exists: run.sh used to judge a stage unchanged by its
    inputs' modification times, and a fresh worktree gives every file the
    time of the checkout, so every merge rebuilt everything. The same bytes
    at a new time give the same key; one changed byte does not."""
    with cache_repo() as root:
        (root / "inputs").mkdir()
        table = root / "inputs" / "a.csv"
        table.write_text("x,1\n")
        before = cache.key(["inputs"])
        os.utime(table, (1, 1))
        assert cache.key(["inputs"]) == before, "a new modification time changed the key"
        table.write_text("x,2\n")
        assert cache.key(["inputs"]) != before, "a changed byte left the key the same"


def test_an_uncommitted_input_counts_and_an_ignored_file_does_not():
    """A new input not yet committed changes the key, or the stage that reads
    it would be restored from before it existed. A file git ignores - a
    fetched scan the build never reads - does not."""
    with cache_repo() as root:
        (root / "inputs").mkdir()
        (root / "inputs" / "a.csv").write_text("x\n")
        (root / ".gitignore").write_text("inputs/*.pdf\n")
        before = cache.key(["inputs"])
        (root / "inputs" / "scan.pdf").write_text("ignored")
        assert cache.key(["inputs"]) == before, "an ignored file changed the key"
        (root / "inputs" / "b.csv").write_text("y\n")
        assert cache.key(["inputs"]) != before, "an uncommitted input did not change the key"


def test_a_restored_table_is_the_saved_bytes_written_now():
    """A key never saved restores nothing. A saved one puts back exactly the
    saved bytes, with a modification time of now: code/clean/paths.py
    refuses a table older than the run, so a copy that kept the old time
    would stop the clean stage."""
    with cache_repo() as root:
        table = root / "out" / "t.csv"
        table.parent.mkdir()
        table.write_text("saved\n")
        assert not cache.restore("stage", "never"), "a key never saved restored something"
        cache.save("stage", "k", [table])
        for saved in (cache.store() / "stage-k").rglob("*"):
            os.utime(saved, (1, 1))         # saved long before this run
        table.write_text("since\n")
        assert cache.restore("stage", "k"), "a saved key did not restore"
        assert table.read_text() == "saved\n", "the restore did not put back the saved bytes"
        assert table.stat().st_mtime > 1, "the restored table kept its old modification time"


def test_every_worktree_of_a_clone_shares_one_cache():
    """The point of keeping the cache in .git: code/merge.sh merges in a
    scratch worktree, and has to find what the thread's worktree built."""
    with cache_repo() as root:
        (root / "f").write_text("x\n")
        git = ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run([*git, "add", "f"], check=True)
        subprocess.run([*git, "commit", "-qm", "f"], check=True)
        subprocess.run([*git, "worktree", "add", "-q", str(root / "wt")], check=True,
                       stderr=subprocess.DEVNULL)
        here = cache.store().resolve()
        cache.ROOT = root / "wt"
        assert cache.store().resolve() == here, "a worktree keeps a cache of its own"


def test_a_compiles_inputs_come_from_latexmks_record():
    """Which files a PDF depends on is read from the .fls latexmk writes,
    not from a list kept by hand: paths relative to where the compile ran,
    and TeX's own files, outside the repository, left out."""
    with tempfile.TemporaryDirectory() as tmp:
        fls = Path(tmp) / "doc.fls"
        fls.write_text(f"PWD {paper.PAPER}\n"
                       "INPUT /usr/local/texlive/texmf-dist/tex/latex/base/article.cls\n"
                       "INPUT ./arlington-bsap.tex\n"
                       "INPUT ../figures/pdf/members_age.pdf\n"
                       "OUTPUT arlington-bsap.pdf\n")
        found = paper.inputs_read(fls)
    assert found == ["figures/pdf/members_age.pdf", "paper/arlington-bsap.tex"], found


def test_a_worktree_with_no_venv_finds_the_primary_checkouts():
    """Every thread that took a worktree on 7 October 2026 found .venv missing
    (it is gitignored) and symlinked the primary's by hand. run.sh asks
    `code/cache.py venv` for its python instead, so nothing is left to forget.
    Run from a worktree's own copy of the script, as run.sh does; the cache
    key reads the same packages from either checkout, or a worktree would
    never find what the primary built."""
    with tempfile.TemporaryDirectory() as tmp:
        primary = Path(tmp).resolve() / "primary"
        subprocess.run(["git", "init", "-q", str(primary)], check=True)
        (primary / "code").mkdir()
        shutil.copy(ROOT / "code" / "cache.py", primary / "code" / "cache.py")
        python = primary / ".venv" / "bin" / "python"
        python.parent.mkdir(parents=True)
        python.write_text("")
        site = primary / ".venv" / "lib" / "python3.0" / "site-packages" / "pandas-1.dist-info"
        site.mkdir(parents=True)
        git = ["git", "-C", str(primary), "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run([*git, "add", "code"], check=True)
        subprocess.run([*git, "commit", "-qm", "c"], check=True)
        wt = primary / ".claude" / "worktrees" / "w"
        subprocess.run([*git, "worktree", "add", "-q", str(wt)], check=True,
                       stderr=subprocess.DEVNULL)
        assert not (wt / ".venv").exists(), "the fixture's worktree has a venv of its own"
        found = subprocess.run(["python3", str(wt / "code" / "cache.py"), "venv"],
                               cwd=wt, capture_output=True, text=True)
        assert found.stdout.strip() == str(python), found.stdout + found.stderr
        saved = cache.ROOT
        try:
            cache.ROOT = wt
            assert "pandas-1.dist-info" in cache.environment(), "a worktree's cache key ignored the venv's packages"
        finally:
            cache.ROOT = saved
        python.unlink()
        none = subprocess.run(["python3", str(wt / "code" / "cache.py"), "venv"],
                              cwd=wt, capture_output=True, text=True)
        assert none.returncode != 0 and "no venv" in none.stderr, "a missing venv was not reported"


def test_a_compile_leaves_its_files_in_build_and_the_pdf_beside_the_source():
    """paper/ is what a co-author opens, so latexmk works in paper/build/ and
    only the finished PDF is copied up, to the path it has always had. A
    stand-in latexmk writes what the real one does, so this runs without
    LaTeX: it is the copy and the location that are under test."""
    with cache_repo() as root, tempfile.TemporaryDirectory() as bin_dir:
        fake = Path(bin_dir) / "latexmk"
        fake.write_text(
            "#!/usr/bin/env python3\n"
            "import sys, pathlib\n"
            "out = [a.split('=', 1)[1] for a in sys.argv if a.startswith('-outdir=')][0]\n"
            "src = pathlib.Path(sys.argv[-1])\n"
            "d = pathlib.Path(out); d.mkdir(exist_ok=True)\n"
            "(d / (src.stem + '.pdf')).write_bytes(b'%PDF-fake')\n"
            "(d / (src.stem + '.log')).write_text('')\n"
            "(d / (src.stem + '.fls')).write_text('PWD ' + str(pathlib.Path.cwd()) + '\\nINPUT ' + str(src) + '\\n')\n")
        fake.chmod(0o755)
        (root / "paper").mkdir()
        (root / "paper" / "arlington-bsap.tex").write_text("x\n")
        saved_path, saved_stem = os.environ["PATH"], paper.STEM
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{saved_path}"
        try:
            paper.STEM = "arlington-bsap"
            (root / "paper" / "build").mkdir()
            (root / "paper" / "build" / "arlington-bsap.pdf").write_bytes(b"%PDF-stale")
            wrote = paper.main()
        finally:
            os.environ["PATH"], paper.STEM = saved_path, saved_stem
        assert wrote == root / "paper" / "arlington-bsap.pdf", f"main() reported {wrote}"
        left = list((root / "paper" / "build").glob("*.pdf"))
        assert not left, f"a PDF is readable in paper/build/: {left}"
        assert (root / "paper" / "build" / "arlington-bsap.log").exists(), "latexmk's files are not in paper/build/"
        assert (root / "paper" / "arlington-bsap.pdf").read_bytes() == b"%PDF-fake", \
            "the PDF was not copied up beside the source"
        stray = sorted(f.name for f in (root / "paper").iterdir()
                       if f.is_file() and f.suffix in (".aux", ".log", ".fls", ".bcf"))
        assert not stray, f"latexmk left files beside the source: {stray}"


def test_paper_holds_only_what_a_co_author_should_see():
    """paper/ is the whole of what Overleaf shows (code/publish.py), so a
    stray file added to it - a note, a scratch compile, a data file - reaches
    every co-author. Everything tracked at its top level is named here; to add
    a section folder or a generated .tex, add it to this list on purpose."""
    allowed = {"arlington-bsap.tex", "0_summary.tex", "body_text_numbers.tex",
               "1_history", "2_community_input", "3_future_work", "4_appendix.tex",
               "tables", "bib",
               "drafts"}  # dated milestone copies of the compiled report (Sally, 7 October 2026)
    tracked = subprocess.run(["git", "ls-files", "paper"], cwd=ROOT, check=True,
                             capture_output=True, text=True).stdout.split("\n")
    top = {Path(f).parts[1] for f in tracked if f}
    assert top <= allowed, f"paper/ holds something a co-author should not see: {sorted(top - allowed)}"


def test_a_draft_copy_from_30_october_refuses_a_section_only_claude_has_touched():
    """paper/drafts/ holds dated copies of the compiled report, and from 30
    October 2026 every section file in one must hold an entry from a person
    (code/revisions.py), not only Claude's CC: '% revised: CC 8 October 2026;
    SH 9 October 2026'. Builds a small paper/ in a temporary folder, writes a
    copy dated the cutoff while one file is Claude's alone, and asserts the
    check names it; then asserts the same copy passes once a person has an
    entry, that an earlier copy passes meanwhile, that a stamp shows the
    latest entry across a section's files, and that a first line which is not
    a mark is refused rather than read as one."""
    with tempfile.TemporaryDirectory() as tmp:
        paper_dir = Path(tmp) / "paper"
        (paper_dir / "drafts").mkdir(parents=True)
        wrapper = paper_dir / revisions.WRAPPER
        wrapper.write_text("\\sectioninput{a}\n% \\sectioninput{commented_out}\n\\sectioninput{b}\n")
        a, b = paper_dir / "a.tex", paper_dir / "b.tex"
        a.write_text("% revised: CC 8 October 2026; AK 9 October 2026\n\\section{A}\n")
        b.write_text("% revised: CC 8 October 2026\n\\section{B}\n")
        (paper_dir / "drafts" / "arlington-bsap-2026-10-29.pdf").write_bytes(b"%PDF")
        assert not revisions.late_copies_with_unrevised_sections(paper_dir), \
            "a copy before the cutoff was refused"
        (paper_dir / "drafts" / "arlington-bsap-2026-10-30.pdf").write_bytes(b"%PDF")
        found = revisions.late_copies_with_unrevised_sections(paper_dir)
        assert len(found) == 1 and "b.tex" in found[0] and "a.tex" not in found[0], \
            f"the 30 October copy was not refused for the file only Claude touched: {found}"
        b.write_text("% revised: CC 8 October 2026; SH 8 October 2026\n\\section{B}\n")
        assert not revisions.late_copies_with_unrevised_sections(paper_dir), \
            "a copy was refused although a person has an entry in every file"
        # A section's stamp is the latest entry across its files, whoever made it.
        wrapper.write_text("\\sectioninput[c,d]{a}\n\\sectioninput{c}\n\\sectioninput{d}\n")
        c, d = paper_dir / "c.tex", paper_dir / "d.tex"
        c.write_text("% revised: AK 9 September 2026\n")
        d.write_text("% revised: CC 12 October 2026; SH 3 June 2026\n")
        assert [revisions.label([m, *p]) for m, p in revisions.sections(paper_dir)] == ["CC 12 Oct"], \
            "the stamp is not the latest entry across the section's files"
        # A part's line stamps the latest entry across the files it lists.
        wrapper.write_text("\\partinput[a,b]{c}\n\\sectioninput{a}\n\\sectioninput{b}\n")
        assert [(m.name, revisions.label(fs)) for m, fs in revisions.parts(paper_dir)] \
            == [("c.tex", "AK 9 Oct")] and len(revisions.sections(paper_dir)) == 3, \
            "a part's stamp is not the latest entry across its files"
        b.write_text("% revised\n\\section{B}\n")
        wrapper.write_text("\\sectioninput{a}\n\\sectioninput{b}\n")
        try:
            revisions.late_copies_with_unrevised_sections(paper_dir)
        except ValueError:
            pass
        else:
            raise AssertionError("a section whose first line is not a mark was read as revised")


def test_no_real_draft_copy_after_the_cutoff_holds_an_unrevised_section():
    """The same check on the repository's own paper/drafts/."""
    problems = revisions.late_copies_with_unrevised_sections()
    assert not problems, "\n  ".join(problems)


def test_every_tex_file_under_paper_is_reached_from_a_document():
    """The report was split into one file per section, and a file nothing
    \\inputs is a section that silently dropped out of the PDF. Follow every
    \\input (and the roster's \\rosterinput and the sections' \\sectioninput) from each document's root and
    require that every tracked .tex under paper/ was reached."""
    paper_dir = ROOT / "paper"
    reached, todo = set(), [paper_dir / path for path in paper.SOURCES.values()]
    while todo:
        tex = todo.pop()
        if tex in reached:
            continue
        reached.add(tex)
        live = "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in tex.read_text().split("\n"))
        for m in re.finditer(r"\\(?:input|rosterinput|sectioninput|partinput)\s*(?:\[[^\]]*\])?\s*\{?([^}\s]+)\}?", live):
            name = m.group(1)
            target = paper_dir / (name if name.endswith(".tex") else name + ".tex")
            if target.exists():
                todo.append(target)
    tracked = {ROOT / f for f in subprocess.run(
        ["git", "ls-files", "paper/*.tex"], cwd=ROOT, check=True,
        capture_output=True, text=True).stdout.split("\n") if f}
    orphans = sorted(str(f.relative_to(ROOT)) for f in tracked - reached)
    assert not orphans, "no document inputs these, so they are not in any PDF:\n  " + "\n  ".join(orphans)


def test_editing_the_bibliography_changes_a_compiles_key():
    """lualatex's record does not list sources.bib, because biber reads it,
    so a key built from the record alone would copy back a PDF whose
    citations predate an edit to the bibliography."""
    with cache_repo() as root:
        (root / "paper" / "bib").mkdir(parents=True)
        (root / "paper" / "doc.tex").write_text("text\n")
        (root / "paper" / "bib" / "sources.bib").write_text("@misc{a}\n")
        before = paper.compile_key(["paper/doc.tex"])
        (root / "paper" / "bib" / "sources.bib").write_text("@misc{b}\n")
        assert paper.compile_key(["paper/doc.tex"]) != before, \
            "an edit to sources.bib left the compile's key the same"


def run_one(name):
    """Run one test in a worker process: (name, None) if it passed, else
    (name, what it said). A test that raises anything but an AssertionError
    is a failure too, reported with its traceback."""
    # run.sh exports RUN_STARTED, which makes a clean table older than the run
    # an error, and the tests run before the clean stage rewrites them. The
    # one test of that guard sets it for itself.
    os.environ.pop("RUN_STARTED", None)
    try:
        globals()[name]()
        return name, None
    except AssertionError as e:
        return name, str(e)
    except Exception:
        return name, traceback.format_exc()


if __name__ == "__main__":
    # The tests are independent - each builds its own input in memory or in a
    # temporary folder - so they run in a few processes at once, which takes
    # the suite from a minute to well under half of one.
    # Words on the command line keep only the tests whose name contains one:
    #   .venv/bin/python code/tests.py press elections
    words = sys.argv[1:]
    names = sorted(n for n in globals() if n.startswith("test_")
                   and (not words or any(w in n for w in words)))
    if not names:
        raise SystemExit(f"no test name contains {' or '.join(words)!r}")
    with ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
        results = list(pool.map(run_one, names))
    failed = 0
    for name, said in results:
        if said is None:
            print(f"  ok    {name}")
        else:
            failed += 1
            print(f"  FAIL  {name}\n        {said}")
    print(f"\n{len(names) - failed}/{len(names)} passed")
    sys.exit(1 if failed else 0)
