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


def keys():
    """Every citekey defined in paper/sources.bib."""
    if not BIB.exists():
        raise FileNotFoundError(f"{BIB} missing - the bibliography is the registry")
    return set(re.findall(r"^@\w+\{([^,\s]+)\s*,", BIB.read_text(), re.M))


def key_of(cell):
    """The citekey a source cell cites: "oleary2010 p.6" -> "oleary2010".
    Two sources for one claim are joined with "; ", so a trailing separator
    is dropped. A blank cell cites nothing."""
    cell = (cell or "").strip()
    return cell.split()[0].rstrip(";") if cell else ""


def check(cells, where):
    """Refuse any source cell that is neither a known citekey nor a
    placeholder. Returns a count per placeholder, for run.sh to report."""
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
