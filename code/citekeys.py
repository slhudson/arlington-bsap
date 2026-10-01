"""The registry of sources, read from paper/sources.bib.

Every `source` cell in data/built/ and data/clean/ holds a citekey from the
bibliography.
This module reads the keys out of the .bib and offers them as named
constants. A module, not a step.

A source column holds a citekey, or one of three placeholders; anything
else stops the build.

    UNSOURCED   a claim exists and its evidence is not yet named
    DERIVED     computed from another table in data/clean/, whose rows carry
                the citations
    ASSUMED     no claim exists; the build wrote a value in from a standing
                assumption

run.sh prints a count of each on every build.
"""
import pathlib
import re

BIB = pathlib.Path(__file__).resolve().parents[1] / "paper" / "sources.bib"

UNSOURCED = "unsourced"
ASSUMED = "assumed"
DERIVED = "derived"
PLACEHOLDERS = (UNSOURCED, ASSUMED, DERIVED)

OLEARY = "oleary2010"
NOVACK = "novack1994"
ARLHIST_OFFICIALS = "arlhist1967officials"
ARLINGTON_ELECTIONS = "arlingtonelections2021"
VA_ELECTIONS = "vaelections"
VA_REGISTRATION = "varegistration"
CENSUS_1870 = "walker1872"
CENSUS_1880 = "census1880"
CENSUS_1890 = "census1890"
CENSUS_1900 = "census1900v1"
CENSUS_1910 = "census1910v3"
CENSUS_1920 = "census1920v1"
CENSUS_1930 = "census1930v1"
CENSUS_COUNTY_SERIES = "forstall1996"
CENSUS_DATA_FILE = "censusapi"
CENSUS_1980_STF1A = "census1980stf1a"
CENSUS_1990_STF1A = "census1990stf1a"
CENSUS_TWPS0076 = "censusbureau1990twps76"
CENSUS_GAZETTEER_2020 = "censusgazetteer2020"
# The 1920 full count, and the enumeration district descriptions that say
# which magisterial district each of its six districts covers.
IPUMS_FULL_COUNT = "ipumsfullcount"
# The enumeration district descriptions, where they place the districts. 1880's
# carry no text and 1900's cannot be matched to the extract by number, so those
# two censuses cite the schedules alone.
NARA_EDS = {1910: "nara1910eds", 1920: "nara1920eds"}


def race_source(year):
    """What a district's race split for `year` rests on."""
    eds = NARA_EDS.get(year)
    return f"{IPUMS_FULL_COUNT}; {eds}" if eds else IPUMS_FULL_COUNT


def keys():
    """Every citekey defined in paper/sources.bib."""
    if not BIB.exists():
        raise FileNotFoundError(f"{BIB} missing - the bibliography is the registry")
    return set(re.findall(r"^@\w+\{([^,\s]+)\s*,", BIB.read_text(), re.M))


# A citekey as the write-ups and the tracker name one: a surname or an outlet,
# a year, and sometimes a word for which document it is. Written either in
# backticks, as the markdown does, or in parentheses, as a tracker row does.
MENTIONED = re.compile(r"`([a-z][a-z0-9]*\d{4}[a-z0-9]*)`"
                       r"|\(([a-z][a-z0-9]*\d{4}[a-z0-9]*)(?:[^)]*)\)")


def mentioned(text):
    """Every citekey a write-up or a tracker row names in its prose."""
    return {a or b for a, b in MENTIONED.findall(text)}


def dangling(paths):
    """Every (path, citekey) a doc names that paper/sources.bib does not
    define. Prose citations are checked because nothing else checks them: a
    source column is checked by check() above and a \\autocite by latex, but
    a key in a sentence can outlive the entry it names and say nothing. One
    did - a 1971 act was filed twice under two keys, one was dropped, and the
    tracker row went on citing the dead one."""
    known = keys()
    return [(p, k) for p in paths
            for k in sorted(mentioned(p.read_text())) if k not in known]


def key_of(cell):
    """The citekey a source cell cites: "oleary2010 p.6" -> "oleary2010".
    Two sources for one claim are joined with "; ", so a trailing separator
    is dropped. A blank cell cites nothing."""
    cell = (cell or "").strip()
    return cell.split()[0].rstrip(";") if cell else ""


def check(values, where):
    """Refuse any source cell that is neither a known citekey nor a
    placeholder. Returns a count per placeholder, for run.sh to report."""
    known = keys()
    counts = dict.fromkeys(PLACEHOLDERS, 0)
    bad = set()
    for cell in values:
        key = key_of(cell)
        if not key:
            continue
        if key in counts:
            counts[key] += 1
        elif key not in known:
            bad.add(key)
    if bad:
        raise AssertionError(
            f"{where}: {len(bad)} source value(s) name no entry in {BIB.name} "
            f"and are not placeholders: {', '.join(sorted(bad))}. "
            f"Add the entry to paper/sources.bib, fix the spelling, or - if the "
            f"source genuinely is not known yet - use one of: "
            f"{', '.join(PLACEHOLDERS)}.")
    return counts


def cells(frame):
    """Every source cell in `frame`: a column named `source`, or named for
    what it sources, `<column>_source`. Both data stages ask this of a table
    they are about to write, so it is answered once, here."""
    return (v for c in frame.columns if c == "source" or c.endswith("_source")
            for v in frame[c].astype(str))


def checked(frame, path):
    """Check every source cell in `frame`, and return the line the stage
    prints for the table it writes: the file, its rows, and any placeholders
    among them."""
    counts = check(cells(frame), path.name)
    said = ", ".join(f"{n} {k}" for k, n in counts.items() if n)
    return f"  {path.name:<22} {len(frame):>4} rows" + (f"   [{said}]" if said else "")
