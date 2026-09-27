"""Who held each magisterial district, 1912-1931, from the Historical
Society's "County Officials in Arlington, 1870-1960". A module, not a step:
members_roster.py assembles it with the rest.

The article prints the Board in blocks, each block one stretch with a
settled membership and a named chairman, compiled from the Board's own
minute books. A block is not a term: the 1920-23 term is three blocks in the
Washington seat, because the seat stood empty and then changed hands inside
it. So the blocks are merged where the same person holds a district across
them, and cut at the statutory four-year boundaries the article's own
year-blocks follow (January 1912, 1916, 1920, 1924, 1928). A block naming no
one is the vacancy the source states, and a vacant seat is not a row.

Five of the terms the article gives are already in the roster from another
source - Wibirt's and Walker's 1916 terms from O'Leary, Ingram's 1924 and
Thornburke's 1924 and 1928 from the county's candidate history - so
terms(earlier) merges into those rows rather than adding a second one,
taking the end date none of the other sources records. Jefferson is Edward
Duncan throughout; his rows are emitted like any other and
members_roster.apply_duncan_join collapses them with the rest of his service.

Three readings here are provisional; docs/members.md and docs/questions.csv
have each. They are marked below.
"""
import pandas as pd

import citekeys
import members_roster_oleary as oleary
from members_terms import APPOINTMENT, TERM_YEARS, UNRECORDED, YEAR_RE, listing, month_of
from elections import surname

# The article covers 1908-1931; these are the years it is read for.
FIRST_YEAR = 1912
LAST_YEAR = 1931
# January of each four-year term inside that stretch (Va. Const. 1902 sec. 112).
TERM_STARTS = range(FIRST_YEAR, LAST_YEAR + 1, TERM_YEARS)

VACANT = "(vacancy)"

# A surname the article spells one way and the rest of the roster another.
# Matching is by surname, so a spelling read as the same man must be said
# here; the reading itself is in READING_NOTES below.
SPELLINGS = {"turnburke": "thornburke"}

# What this source forces the roster to say about a person that the source
# does not say itself, by the term each lands on: (the roster's name, the
# term's start year). Each is written onto the term so that members.csv
# carries it, and none changes a figure - the seat is filled either way, and
# every member of this era defaults to White and man (docs/members.md,
# default-1931-1986). A reading still open ends with its slug in
# docs/questions.csv; a settled one states what settled it.
READING_NOTES = {
    ("Walker", 1916):
        "The resignation and its date are the article's, from the Board's minute "
        "books; O'Leary records no departure, so this term would otherwise run to "
        "January 1920 by statute and Ahalt's appointment would not exist "
        "(roster-walker-end-date).",
    ("E.C. Thornburke", 1924):
        "Read as the Thornburke the other two sources print, so the article closes "
        "the county's open-ended term rather than standing beside it as a second "
        "man (roster-turnburke-spelling).",
    ("E.C. Thornburke", 1928):
        "Read as the Thornburke the other two sources print, so the article closes "
        "the county's open-ended term rather than standing beside it as a second "
        "man (roster-turnburke-spelling).",
    ("Thomas J. DeLashmutt", 1920):
        "A different man from the Basil M. DeLashmutt of the 1932-62 cohort, and "
        "his father: his 1920 household holds a son, Basil N., 17, born about "
        "1903, the birth year of that cohort's 1930 match "
        "(census1930delashmutt), whose row cites the household as well as the "
        "occupation. docs/members.md.",
}


def bound(text, is_end):
    """One end of a block's `term` string as (year, month). A printed month
    is that month; a bare year is January, and a bare year closing a block is
    the following January, the month the next term begins."""
    year = int(YEAR_RE.findall(text)[-1])
    month = month_of(text)
    if month:
        return year, month
    return (year + 1, 1) if is_end else (year, 1)


def runs():
    """One dict per term per district: the article's blocks merged where the
    same person holds the seat across them, cut at the statutory boundaries."""
    d = listing("arlhist")
    for district, blocks in d.groupby("district", sort=False):
        current = None
        for _, b in blocks.iterrows():
            before, _, after = str(b.term).partition("-")
            start, end = bound(before, is_end=False), bound(after, is_end=True)
            name = str(b["name"]).strip()
            if name == VACANT:
                if current:
                    yield current
                current = None
                continue
            if (current is None or name != current["name"]
                    or (start[1] == 1 and start[0] in TERM_STARTS)):
                if current:
                    yield current
                current = {"name": name, "district": district, "start": start,
                           "pages": [], "notes": []}
            current["end"] = end
            current["pages"].append(int(b.page))
            if str(b.note).strip():
                current["notes"].append(str(b.note).strip())
        if current:
            yield current


def rows():
    """Every run as a roster row, before it is matched to what other sources
    already record. A term whose note says the member was appointed began
    that way; the article records no election, so the rest are unrecorded."""
    for r in runs():
        note = " ".join(r["notes"])
        pages = sorted(set(r["pages"]))
        yield {"name": r["name"], "district": r["district"],
               "start_year": r["start"][0], "start_month": r["start"][1],
               "end_year": r["end"][0], "end_month": r["end"][1],
               "seated_by": APPOINTMENT if "appointed" in note.lower() else UNRECORDED,
               "source": f"{citekeys.ARLHIST_OFFICIALS} p." + "-".join(map(str, pages)),
               "note": note}


def terms(earlier: pd.DataFrame) -> pd.DataFrame:
    """The article's terms, merged into `earlier`.

    A person another source already records in the same district is named as
    that source names them, since the attributions and the census records are
    keyed on the roster's spelling: the article's "W. C. Wibirt" is O'Leary's
    "Wibirt". Their district seat with the same start year is then one term,
    not two: the row keeps the name and the beginning that source gives it
    and takes the article's end date, its citation and its note. Everything
    else is a new row. More than one row matching is ambiguous and stops the
    build.

    A merged row loses O'Leary's sentence about an end he does not record:
    the article records it.
    """
    d = earlier.copy()
    district = d[d.district != "at large"]
    known = {surname(n): n for n in district.name}
    new = []
    for r in rows():
        last = SPELLINGS.get(surname(r["name"]), surname(r["name"]))
        r["name"] = known.get(last, r["name"])
        r["note"] = " ".join(filter(None, [
            r["note"], READING_NOTES.get((r["name"], r["start_year"]), "")]))
        same = district[(district.district == r["district"])
                        & (district.name.map(surname) == last)
                        & (district.start_year == r["start_year"])]
        if len(same) > 1:
            raise ValueError(f"{r['name']} {r['district']} {r['start_year']}: "
                             f"{len(same)} roster rows already start that year, expected "
                             "one or none:\n" + same.to_string())
        if same.empty:
            new.append(r)
            continue
        i = same.index[0]
        was = d.loc[i, "note"]
        for stale in (oleary.UNRECORDED_END, oleary.STATUTORY_END):
            was = was.replace(stale, "")
        d.loc[i, ["end_year", "end_month"]] = [r["end_year"], r["end_month"]]
        d.loc[i, "source"] = f"{d.loc[i, 'source']}; {r['source']}"
        d.loc[i, "note"] = " ".join(filter(None, [was.strip(), r["note"]]))
    return pd.concat([d, pd.DataFrame(new)], ignore_index=True)
