"""Who held each magisterial district, 1870-1931, from the Historical
Society's "County Officials in Arlington, 1870-1960". A module, not a step:
members_roster.py assembles it with the rest.

The article prints the Board in blocks, each block one stretch with a
settled membership and a named chairman, compiled from the Board's own
minute books. It is read two ways, because what sits under it differs.

For 1912-1931 no other source names the seats, so the blocks are the
roster. A block is not a term: the 1920-23 term is three blocks in the
Washington seat, because the seat stood empty and then changed hands inside
it. So the blocks are merged where the same person holds a district across
them, and cut at the statutory four-year boundaries the article's own
year-blocks follow (January 1912, 1916, 1920, 1924, 1928). A block naming no
one is the vacancy the source states, and a vacant seat is not a row. That
reading is runs(), rows() and terms().

For 1870-1911 O'Leary's elections are already under it, so the article
corrects and adds rather than replacing: names(), what a member is called;
notes(), what the article says about a term another source records; and
early(), the five terms no other source records, with the terms they
interrupt cut to meet them. O'Leary is an electoral history - he lists
elections and their winners and names a departure only where his prose
happens to, recording five handovers in the 1870s and none at all from 1880
through 1911 - so where the article names a supervisor he does not, he is
silent rather than contradicting (Sally, 27 September 2026;
docs/members.md).

Five of the terms the article gives for 1912-1931 are already in the roster
from another source - Wibirt's and Walker's 1916 terms from O'Leary,
Ingram's 1924 and Turnburke's 1924 and 1928 from the county's candidate
history - so terms(earlier) merges into those rows rather than adding a
second one, taking the end date none of the other sources records.
Jefferson is Edward Duncan throughout; his rows are emitted like any other
and members_roster.apply_duncan_join collapses them with the rest of his
service.

One reading here is provisional, Walker's end date; docs/members.md and
docs/questions.csv have it. The readings this source forces onto a term,
settled or not, are marked below in READING_NOTES.
"""
import pandas as pd

import citekeys
import members_roster_oleary as oleary
from members_terms import APPOINTMENT, TERM_YEARS, UNRECORDED, YEAR_RE, listing, month_of
from elections import surname

# The two stretches the article is read for.
EARLY_FIRST_YEAR = 1870
EARLY_LAST_YEAR = 1911
FIRST_YEAR = 1912
LAST_YEAR = 1931
# January of each four-year term inside 1912-1931 (Va. Const. 1902 sec. 112).
TERM_STARTS = range(FIRST_YEAR, LAST_YEAR + 1, TERM_YEARS)

VACANT = "(vacancy)"


# What the roster calls a member the article names differently, keyed on the
# roster's name and the district, with what settled it. The article is the
# Board's own minute books, so where it prints a full name for a member
# another source leaves as a surname or a pair of initials, that full name is
# the roster's; where two sources spell a surname differently, the note says
# what decided it. The renamed rows carry the note, so which term rests on
# which reading is greppable.
#
# The table is the mechanism and each entry is a ruling, so a variant that is
# not here has not been ruled on. Two rulings leave no entry, because the
# roster already holds the spelling they settle: the article's Perkin for
# O'Leary's Perkins (Arlington, 1883-84), where the 1880 census sheet reads
# Perkins with O'Leary, and its Costolow for his Costello, which its own 1881
# footnote calls the proper form and which appears only in a block outside the
# terms read here (Sally, 27 September 2026).
NAMES = {
    ("Roach", "Jefferson"): ("James C. Roach",
        "Named in full by the article, from the Board's minute books, where "
        "O'Leary gives the surname alone (Sally, 27 September 2026)."),
    ("Corbett", "Arlington"): ("Frederick S. Corbett",
        "Named in full by the article, from the Board's minute books, where "
        "O'Leary gives the surname alone from 1907. The article gives the same "
        "full name to the Arlington member of 1889-91, 1895-97, October "
        "1897-99 and 1899-1901, and the censuses agree on a birth year - the "
        "1880 sheet an age of 24, the 1910 sheet 1856 - so the five terms are "
        "one man (Sally, 27 September 2026)."),
    ("Francis D. Schutt", "Arlington"): ("Francis G. Schutt",
        "One man with the Francis G. Schutt who holds the same seat after "
        "him, from his July 1873 appointment to his May 1874 election with no "
        "gap. Three sources give three middle initials - D in O'Leary, G in "
        "the minute books, C in the Alexandria Gazette of 6 December 1875 "
        "(gazette1875schutt) - and an initial that unstable cannot be what "
        "distinguishes two men; his is the only Schutt household in the county "
        "in 1880 (census1880schutt). Sally, 27 September 2026."),
    ("George N. Saegmulller", "Washington"): ("George N. Saegmuller",
        "Spelled Saegmuller by the article, from the Board's minute books, and "
        "by the 1880 and 1900 census sheets; O'Leary's triple l is a typo on "
        "its face (Sally, 27 September 2026)."),
    ("Millard F. Birth", "Arlington"): ("Millard F. Birch",
        "Spelled Birch by the article, from the Board's minute books, and by "
        "both the 1900 census index and its sheet (census1900birth); O'Leary "
        "alone reads Birth (Sally, 27 September 2026)."),
    ("Wibirt", "Arlington"): ("W. C. Wibirt",
        "Named in full by the article, from the Board's minute books, where "
        "O'Leary gives the surname alone (Sally, 27 September 2026)."),
    ("Walker", "Washington"): ("Robert L. Walker",
        "Named in full by the article, from the Board's minute books, where "
        "O'Leary gives the surname alone (Sally, 27 September 2026)."),
    ("E.C. Thornburke", "Washington"): ("E.C. Turnburke",
        "Spelled Turnburke by the article, from the Board's minute books, by "
        "the 1920 census index and sheet (census1920thornburke) and by the "
        "Alexandria Gazette, which prints Turnburke in 1923 and no Thornburke "
        "anywhere in its run (gazette1923turnburke). The county's candidate "
        "history and Novack print Thornburke; that is a recorded variant of "
        "the name rather than the name (Sally, 27 September 2026)."),
}


# What the article says about a term another source already records, keyed on
# the roster's name, the district and the term's start year. A reading that
# moves no date and no value, so it is written onto the row and nowhere else.
CONTESTED_1897 = (
    "The Arlington election of 1897 gave A. D. Torreyson and Frederick S. "
    "Corbett 209 votes each on the first count; the county court found for "
    "Corbett and declared him a member from 1 July, by which time Torreyson "
    "had been sitting, and he sat on until 11 October. The roster records who "
    "held a seat, not who held title to it, so the court's finding is a note "
    "on both rows rather than a second term (Sally, 27 September 2026; "
    "docs/members.md)."
)
NOTES = {
    ("A. D. Torreyson", "Arlington", 1897): CONTESTED_1897,
    ("Frederick S. Corbett", "Arlington", 1897): CONTESTED_1897,
}


# The five terms the article adds to 1870-1911, keyed on the member and his
# district, with what is still open about each. Every date is the article's:
# the term begins with the first block naming the man, runs to the end of the
# last block he holds without a break or to the month the next term in that
# seat begins, whichever is first, and the man whose block precedes his has
# his own term cut to that block's printed end.
ADDED = {
    ("Francis M. Mills", "Jefferson"): "",
    ("Curtis B. Graham, Jr.", "Arlington"): "",
    ("George W. Saulisbury", "Jefferson"): "",
    ("Frank Hume", "Jefferson"):
        " The county court appointed him on 2 October 1888 "
        "(alexandriagazette1888hume); 13 November is the first record of him "
        "sitting, and the Gazette's Local Matters column of that evening "
        "lists him among the supervisors present "
        "(alexandriagazette1888supervisors). The article dates a term from "
        "the minute books' first record of a man sitting, not from the "
        "instrument that named him, so the two dates answer different "
        "questions (docs/members.md).",
    ("William N. Febrey", "Washington"): "",
}
ADDED_NOTE = (
    "A term no other source records. O'Leary lists elections and their "
    "winners and names a departure only where his prose happens to, recording "
    "five handovers in the 1870s and none at all from 1880 through 1911, so "
    "he is silent here rather than contradicting; the article is the Board's "
    "own minute books (Sally, 27 September 2026; docs/members.md)."
)
# A term the article ends before the roster's next term in the seat begins,
# leaving the seat empty for whole months, keyed on the member, his district
# and the term's start year. Only where the gap covers whole months: the
# article also opens blocks of a few days between an outgoing and an incoming
# member - Arlington, 5 to 25 June 1877 - and on a month grain those are one
# handover, not a vacancy. The months themselves are the article's, read off
# the block that names nobody (vacated()).
VACATED = {
    ("William A. Rowe", "Jefferson", 1877):
        "Resigned 2 April 1879, having moved from Jefferson into Arlington "
        "District, and the seat stood empty until Travis B. Pinn's term began "
        "on 1 July. O'Leary records no departure and gives the whole term to "
        "him (Sally, 27 September 2026; docs/members.md).",
}

# The two seats the article gives to someone other than the man another
# source seats, keyed on the roster's name, his district and the term's start
# year: the man the article seats instead, or VACANT where it seats nobody,
# and what settled it. The roster records who held a seat rather than who won
# it - the rule Torreyson's fourteen weeks in 1897 settled - and an election
# return names the winner while the minute books name the man who sat, so
# where the two disagree about occupancy the minute books answer the question
# the roster asks (Sally, 27 September 2026; docs/members.md).
SEATED = {
    ("Storm V. Boyd", "Jefferson", 1870): (VACANT,
        "The article prints the Jefferson seat empty from 1 July 1870 and the "
        "reason: the supervisor elected for the township, Boyd, failed to "
        "qualify. O'Leary gives him the seat from May to September on the "
        "election alone. He never sat, so the seat stands vacant until James "
        "C. Roach's appointment that September; his 1870 census record "
        "(census1870boyd) places the man and says nothing about the office "
        "(Sally, 27 September 2026)."),
    ("A. B. Grunwell", "Washington", 1897):
        ("George N. Saegmuller",
        "The article puts Saegmuller in the Washington seat from 1 July 1897, "
        "where O'Leary keeps Grunwell to 1899. The minute books name the man "
        "who sat, so Grunwell's service ends with his 1895-97 term and "
        "Saegmuller holds the seat from July 1897 (Sally, 27 September 2026)."),
}


CUT_NOTE = (
    "The end is the article's, from the Board's minute books, which put "
    "{who} in this district from the same date; O'Leary records no departure "
    "and gives the whole term to one man (Sally, 27 September 2026)."
)


# What this source forces the roster to say about a 1912-1931 member that the
# source does not say itself, by the term each lands on: (the roster's name,
# the term's start year). Each is written onto the term so that members.csv
# carries it, and none changes a figure - the seat is filled either way, and
# every member of this era defaults to White and man (docs/members.md,
# member-demographics-lists). A reading still open ends with its slug in
# docs/questions.csv; a settled one states what settled it.
READING_NOTES = {
    ("Robert L. Walker", 1916):
        "The resignation and its date are the article's, from the Board's minute "
        "books; O'Leary records no departure, so this term would otherwise run to "
        "January 1920 by statute and Ahalt's appointment would not exist. His "
        "1920 census sheet has him a sanitary inspector (census1920walker). "
        "docs/members.md.",
    ("Thomas J. DeLashmutt", 1920):
        "A different man from the Basil M. DeLashmutt of the 1932-62 cohort, and "
        "his father: his 1920 household holds a son, Basil N., 17, born about "
        "1903, the birth year of that cohort's 1930 match "
        "(census1930delashmutt), whose row cites the household as well as the "
        "occupation. docs/members.md.",
}

def month(pair):
    """A (year, month) pair as a month counted from year 0."""
    return pair[0] * 12 + pair[1]


def pair(months):
    """A month counted from year 0 back as (year, month)."""
    return (months - 1) // 12, (months - 1) % 12 + 1


def bound(text, is_end):
    """One end of a block's `term` string as (year, month). A printed month
    is that month; a bare year is January, and a bare year closing a block is
    the following January, the month the next term begins."""
    year = int(YEAR_RE.findall(text)[-1])
    month_ = month_of(text)
    if month_:
        return year, month_
    return (year + 1, 1) if is_end else (year, 1)


def blocks(first, last):
    """The article's rows whose block begins in [first, last], in the order
    printed. The article covers 1870-1931 in two stretches read two ways, so
    every reading says which years it is for."""
    d = listing("arlhist")
    begins = d.term.str.partition("-")[0].map(lambda t: int(YEAR_RE.findall(t)[-1]))
    return d[(begins >= first) & (begins <= last)].reset_index(drop=True)


def runs():
    """One dict per term per district, 1912-1931: the article's blocks merged
    where the same person holds the seat across them, cut at the statutory
    boundaries."""
    d = blocks(FIRST_YEAR, LAST_YEAR)
    for district, rows_ in d.groupby("district", sort=False):
        current = None
        for _, b in rows_.iterrows():
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
    """Every 1912-1931 run as a roster row, before it is matched to what
    other sources already record. A term whose note says the member was
    appointed began that way; the article records no election, so the rest
    are unrecorded."""
    for r in runs():
        note = " ".join(r["notes"])
        pages = sorted(set(r["pages"]))
        yield {"name": r["name"], "district": r["district"],
               "start_year": r["start"][0], "start_month": r["start"][1],
               "end_year": r["end"][0], "end_month": r["end"][1],
               "seated_by": APPOINTMENT if "appointed" in note.lower() else UNRECORDED,
               "source": f"{citekeys.ARLHIST_OFFICIALS} p." + "-".join(map(str, pages)),
               "note": note}


def names(earlier: pd.DataFrame) -> pd.DataFrame:
    """The roster with the article's names on it, and the note saying what
    settled each. Applied before the article's own terms are merged in, so
    everything downstream matches on one spelling. An entry matching no row
    is a reading keyed to a term that has moved, and stops the build."""
    d = earlier.copy()
    for (was, district), (now, note) in NAMES.items():
        hit = (d.name == was) & (d.district == district)
        if not hit.any():
            raise ValueError(f"NAMES has no roster row to rename: {was!r} in {district}")
        d.loc[hit, "note"] = [" ".join(filter(None, [n, note])) for n in d.loc[hit, "note"]]
        d.loc[hit, "name"] = now
        d.loc[hit, "source"] = d.loc[hit, "source"] + f"; {citekeys.ARLHIST_OFFICIALS}"
    return d


def notes(earlier: pd.DataFrame) -> pd.DataFrame:
    """The roster with what the article says about a term another source
    already records written onto it. An entry matching no term stops the
    build, for the same reason names() does."""
    d = earlier.copy()
    for (who, district, year), note in NOTES.items():
        hit = (d.name == who) & (d.district == district) & (d.start_year == year)
        if hit.sum() != 1:
            raise ValueError(f"NOTES matches {hit.sum()} roster rows, expected one: "
                             f"{who!r} {district} {year}")
        d.loc[hit, "note"] = [" ".join(filter(None, [n, note])) for n in d.loc[hit, "note"]]
        d.loc[hit, "source"] = d.loc[hit, "source"] + f"; {citekeys.ARLHIST_OFFICIALS} p.42"
    return d


def early_blocks():
    """The article's 1870-1911 blocks, per district in printed order, each as
    its name, its two bounds, its page and its note."""
    out = {}
    for district, rows_ in blocks(EARLY_FIRST_YEAR, EARLY_LAST_YEAR).groupby("district", sort=False):
        out[district] = [{"name": str(b["name"]).strip(),
                          "start": bound(str(b.term).partition("-")[0], is_end=False),
                          "end": bound(str(b.term).partition("-")[2], is_end=True),
                          "page": int(b.page), "note": str(b.note).strip()}
                         for _, b in rows_.iterrows()]
    return out


def empty_months(seq, i):
    """The whole months a vacancy block leaves the seat empty. A block ending
    in the month the next one begins hands over rather than standing empty
    that month, the rule members.held() applies to a term."""
    first, last = month(seq[i]["start"]), month(seq[i]["end"])
    if i + 1 < len(seq) and month(seq[i + 1]["start"]) == last:
        last -= 1
    return range(first, last + 1)


def unseated():
    """Every month a seat stands empty because the article seats nobody where
    another source seats a man, as members_roster.py lists the vacancies."""
    printed = early_blocks()
    out = []
    for (who, district, year), (now, _) in SEATED.items():
        if now != VACANT:
            continue
        seq = printed[district]
        i = next((j for j, b in enumerate(seq)
                  if b["name"] == VACANT and who in b["note"]), None)
        if i is None:
            raise ValueError(f"the article has no empty {district} block naming {who!r}")
        out += [(district, *pair(m)) for m in empty_months(seq, i)]
    return out


def seated(d):
    """`d` with each SEATED term given to the man the article seats, or
    dropped where it seats nobody. Exactly one roster term must match, or the
    reading is keyed to a seat that has moved and the build stops."""
    d = d.copy()
    drop = []
    for (who, district, year), (now, note) in SEATED.items():
        hit = (d.name == who) & (d.district == district) & (d.start_year == year)
        if hit.sum() != 1:
            raise ValueError(f"SEATED matches {hit.sum()} roster terms, expected one: "
                             f"{who!r} {district} {year}")
        i = d.index[hit][0]
        page = early_blocks()[district][0]["page"]
        if now == VACANT:
            drop.append(i)
            continue
        d.loc[i, "name"] = now
        d.loc[i, "source"] = f"{d.loc[i, 'source']}; {citekeys.ARLHIST_OFFICIALS} p.{page}"
        d.loc[i, "note"] = " ".join(filter(None, [d.loc[i, "note"], note]))
    return d.drop(index=drop).reset_index(drop=True)


def vacated():
    """One entry per VACATED term: where the article ends it, and the months
    the seat then stands empty. Both are read off the article - the block the
    member holds, and the block after it, which names nobody. A term whose
    next block names someone is not a vacancy and stops the build."""
    printed = early_blocks()
    out = {}
    for key, note in VACATED.items():
        who, district, _ = key
        seq = printed[district]
        i = next((j for j, b in enumerate(seq)
                  if b["name"] == who and j + 1 < len(seq)
                  and seq[j + 1]["name"] == VACANT), None)
        if i is None:
            raise ValueError(f"the article has no {district} block for {who!r} "
                             "followed by one naming nobody")
        out[key] = {"ends": seq[i]["end"], "note": note,
                    "page": seq[i]["page"],
                    "empty": [(district, *pair(m)) for m in empty_months(seq, i + 1)]}
    return out


def vacancies():
    """Every month a seat stands empty under the article's 1870-1911 reading,
    as members_roster.py lists the other recorded vacancies."""
    return [m for v in vacated().values() for m in v["empty"]]


def spans(seat: pd.DataFrame):
    """A district's terms as first and last month, both counted from year 0,
    an unrecorded end held to the end of its first year."""
    first = seat.start_year * 12 + seat.start_month
    last = (pd.to_numeric(seat.end_year).fillna(seat.start_year) * 12
            + pd.to_numeric(seat.end_month).fillna(12))
    return first, last


def early(earlier: pd.DataFrame) -> pd.DataFrame:
    """`earlier` with the five terms the article adds to 1870-1911, and the
    term each interrupts cut back to meet it.

    Each added term is found by its blocks: the first block naming the man in
    that district, and every block after it he holds without a break. The
    term ends where those blocks end or where the roster's next term in the
    seat begins, whichever is first - Hume's appointed part-term runs to his
    own election that July, though the article carries him on to 1895.

    The man he follows is the name on the block before his, and the roster
    row covering that month is his; exactly one must, and its surname must be
    the one the article prints, or the reading is keyed to a seat that has
    moved and the build stops.
    """
    d = seated(earlier)
    printed = early_blocks()
    for (who, district, year), v in vacated().items():
        hit = (d.name == who) & (d.district == district) & (d.start_year == year)
        if hit.sum() != 1:
            raise ValueError(f"VACATED matches {hit.sum()} roster terms, expected one: "
                             f"{who!r} {district} {year}")
        d.loc[hit, ["end_year", "end_month"]] = list(v["ends"])
        d.loc[hit, "source"] = (d.loc[hit, "source"]
                                + f"; {citekeys.ARLHIST_OFFICIALS} p.{v['page']}")
        d.loc[hit, "note"] = [" ".join(filter(None, [n, v["note"]])) for n in d.loc[hit, "note"]]
    new = []
    for (who, district), open_note in ADDED.items():
        seq = printed[district]
        i = next((j for j, b in enumerate(seq) if b["name"] == who), None)
        if i is None:
            raise ValueError(f"{who!r} heads no block of the article's {district} seat")
        if i == 0:
            raise ValueError(f"{who!r} opens the article's {district} seat, so no term is cut")
        last = i
        while last + 1 < len(seq) and seq[last + 1]["name"] == who:
            last += 1
        start, cut_to = seq[i]["start"], seq[i - 1]["end"]
        pages = sorted({b["page"] for b in seq[i:last + 1]})
        article = f"{citekeys.ARLHIST_OFFICIALS} p." + "-".join(map(str, pages))

        seat = d[d.district == district]
        opens, closes = spans(seat)
        # The blocks run on past the term where the roster already has the
        # next one: Hume's part-term ends at his own election that July.
        follows = opens[opens > month(start)]
        end = pair(min([month(seq[last]["end"])] + ([int(follows.min())] if len(follows) else [])))

        covers = seat[(opens <= month(start)) & (month(start) <= closes)]
        if len(covers) != 1:
            raise ValueError(f"{len(covers)} roster terms hold {district} in "
                             f"{start[0]}-{start[1]:02d}, expected the one {who} "
                             f"takes it from:\n{covers.to_string()}")
        cut = covers.index[0]
        if surname(d.loc[cut, "name"]) != surname(seq[i - 1]["name"]):
            raise ValueError(f"the article has {who} follow {seq[i - 1]['name']!r} in "
                             f"{district}, the roster {d.loc[cut, 'name']!r}")
        d.loc[cut, ["end_year", "end_month"]] = list(cut_to)
        d.loc[cut, "source"] = f"{d.loc[cut, 'source']}; {article}"
        d.loc[cut, "note"] = " ".join(filter(None, [d.loc[cut, "note"],
                                                    CUT_NOTE.format(who=who)]))

        block_note = " ".join(filter(None, [b["note"] for b in seq[i:last + 1]]))
        new.append({"name": who, "district": district,
                    "start_year": start[0], "start_month": start[1],
                    "end_year": end[0], "end_month": end[1],
                    "seated_by": (APPOINTMENT if "appointed" in block_note.lower()
                                  else UNRECORDED),
                    "source": article,
                    "note": " ".join(filter(None, [block_note, ADDED_NOTE, open_note.strip()]))})
    return pd.concat([d, pd.DataFrame(new)], ignore_index=True)


def terms(earlier: pd.DataFrame) -> pd.DataFrame:
    """The article's 1912-1931 terms, merged into `earlier`.

    A person another source already records in the same district is named as
    that source names them, since the attributions and the census records are
    keyed on the roster's spelling; names() has already settled the spelling
    on both sides, so the match here is a plain surname. Their district seat
    with the same start year is then one term, not two: the row keeps the
    name and the beginning that source gives it and takes the article's end
    date, its citation and its note. Everything else is a new row. More than
    one row matching is ambiguous and stops the build.

    A merged row loses O'Leary's sentence about an end he does not record:
    the article records it.
    """
    d = earlier.copy()
    district = d[d.district != "at large"]
    known = {surname(n): n for n in district.name}
    new = []
    for r in rows():
        last = surname(r["name"])
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
