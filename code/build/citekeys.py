"""The registry of sources, read from paper/sources.bib.

Every `source` cell in data/clean/ holds a citekey from the bibliography, so a
sentence in the report and a cell in a table point at the same entry. This
module is what makes that checkable: it reads the keys out of the .bib and
offers them to the build as named constants, so a typo fails the run instead of
shipping a citation that points at nothing.

It is a mechanism module, like elections.py - it produces no data layer.

**Three kinds of value can appear in a source column.**

    a citekey       the claim rests on a document, named in sources.bib
    a placeholder   the claim rests on something we cannot yet cite
    anything else   a mistake; the build stops

The placeholders are the honest part. This is draft work over an incomplete
historical record, and a scheme with no way to say "we do not know yet" only
buys its tidiness by pretending. Each one says something different:

    UNSOURCED   a claim exists and we cannot yet name its evidence - a
                member sat as somebody's candidate, but the county printed
                no label and no reporting has been found, so there is a real
                assertion here whose basis is a research errand.
    DERIVED     the row is computed from another table in data/clean/, whose
                own rows carry the citations - board_seats.csv counts seats
                out of board_members.csv, so its sources are that file's.
    ASSUMED     no claim ever existed. Nobody said anything, so the build
                wrote a value in from a standing assumption - a member absent
                from every source is recorded as a white man, and the years
                with no roster at all as three seats held by white men.

Keeping them apart matters. The first is a gap in our records; the second is a
gap in the historical record, and one of the findings of the study. Collapsing
them into a single "no source" would hide the weaker of the two.

run.sh prints a count of each on every build, so both numbers are in front of
whoever is working rather than found by going looking. They should fall over
time. docs/residents.md, docs/board.md and docs/voters.md say what stands
behind them meanwhile.
"""
import pathlib
import re

# Its own path rather than paths.py's, so that paths.py can import this module
# without the two importing each other. This one knows about paper/, not data/.
BIB = pathlib.Path(__file__).resolve().parents[2] / "paper" / "sources.bib"

# A claim exists; its evidence is not yet named. A research errand.
UNSOURCED = "unsourced"
# No claim existed; the build supplied one. A finding about the record.
ASSUMED = "assumed"
# Computed from another clean table; the citations live on that table's rows.
DERIVED = "derived"

PLACEHOLDERS = (UNSOURCED, ASSUMED, DERIVED)

# Named here rather than spelled out at each use, so a rename is one edit and
# a typo is an ImportError rather than a dangling citation nobody notices.
OLEARY = "oleary2010"
NOVACK = "novack1994"
ARLINGTON_ELECTIONS = "arlingtonelections2021"
VA_ELECTIONS = "vaelections"
VA_REGISTRATION = "varegistration"
CENSUS_1870 = "walker1872"
CENSUS_1880 = "census1880"
CENSUS_1890 = "census1890"
CENSUS_COUNTY_SERIES = "forstall1996"
CENSUS_DATA_FILE = "censusapi"
# The archived Summary Tape Files, which the API does not carry.
CENSUS_1980_STF1A = "census1980stf1a"
CENSUS_1990_STF1A = "census1990stf1a"
# POP-TWPS0076, Table 47: Arlington by race at every census from 1900.
CENSUS_TWPS0076 = "censusbureau1990twps76"


def keys():
    """Every citekey defined in paper/sources.bib."""
    if not BIB.exists():
        raise FileNotFoundError(f"{BIB} missing - the bibliography is the registry")
    return set(re.findall(r"^@\w+\{([^,\s]+)\s*,", BIB.read_text(), re.M))


def key_of(cell):
    """The citekey a source cell cites, ignoring any locator after it.

    Cells read "oleary2010 p.6" or "vaelections contest 163432": the key comes
    first, the page or contest id after it. Two sources for one claim are
    joined with "; ", so a key with no locator can arrive as "mccaffrey2009;"
    and the separator is dropped. A blank cell cites nothing.
    """
    cell = (cell or "").strip()
    return cell.split()[0].rstrip(";") if cell else ""


def check(cells, where):
    """Refuse any source cell that is neither a known citekey nor a placeholder.

    Raises rather than warns. A dangling citekey means a number in the report
    cannot be traced to a document, which is the one thing this project exists
    to prevent - and unlike a warning, a raise cannot be scrolled past.

    Returns a count per placeholder, for run.sh to report.
    """
    known = keys()
    counts = dict.fromkeys(PLACEHOLDERS, 0)
    bad = set()
    for cell in cells:
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
