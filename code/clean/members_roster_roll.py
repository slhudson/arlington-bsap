"""The county's own roll, read as terms. A module, not a step:
members_roster.py assembles it with the rest.

    service(year)  the names the roll puts on the Board in a year
    departures()   a name and the month a member left, where the roll dates it
    arrivals()     a name and the month a member was seated without an election
    vacancies()    the months no one held a seat, between a departure and the
                   next arrival

The roll records service, where every other source here records contests
(docs/members.md, "The roster"). That difference is the whole reason it is
read: a member seated by appointment wins nothing, so no election record
holds her, and until this file existed the roster simply did not have Tannia
Talento, appointed in July 2023 to the seat Katie Cristol resigned.

**A month belongs to whoever held the seat for any part of it.** The roll
dates a departure and an arrival to the day; the roster counts whole months
and applies that rule here rather than in any figure, so a seat vacated on 14
December and filled on 30 January is December's and January's, and no month
stands empty. Where a gap does cover a whole month it becomes a vacancy, and
check_seats in members_roster.py holds the roster to it. The reasoning, and
what prorating within a month would cost, is in docs/members.md,
"Seat-years".

Novack covers 1932 to 1994 and the roll covers 1932 on, so for those years
the two are independent records of the same Board. Both are cited on the
terms they agree about, and check_against_novack refuses a year where they
name different people - with EXPECTED declaring the places they differ for a
reason: the roll seats a November winner in the year of the election where
the roster seats him the following January, and 1941 and 1986 print one name
twice where the fifth member should be.
"""

import pandas as pd

from members_terms import APPOINTMENT, SPECIAL_ELECTION, listing

SOURCE = "arlingtonva2026members"

# The roll's events that end a term, and those that begin one. A vote for the
# chair is neither; code/transcribe/members_roll.py keeps it apart.
LEAVES = ("resigned", "removed", "died", "left for the bench")
ARRIVES = ("appointed", "took office", "special election", "elected")

# A November or December "elected" is the regular election, and the roster
# seats its winner the following January (members_roster.py). An "elected" in
# any other month is a seat filled early - the roll writes Libby Garvey's
# March 2012 special election that way - and seats the member that month.
REGULAR_ELECTION = (11, 12)

# Terms the roster carries whose end the roll moves, and the member who took
# the seat next. Nothing is keyed here: the lists are read off the roll and
# printed by corrections() so the diff in data/clean/members.csv shows them.

# The roll names a person as the press of the day did, which is not always
# the roster's name for the same member. Each of these is one person, read
# off the roll against the roster (docs/members.md).
SAME_PERSON = {
    'Allan L. Dean': 'Alan L. Dean',
    'B.M. Smith': 'B. M. Smith',
    'Basil M. Delashmutt': 'Basil M. DeLashmutt',
    'C.B. Garnett': 'Christopher B. Garnett',
    'Christian Dorsey': 'Christian E. Dorsey',
    'Christopher Zimmerman': 'Christopher E. Zimmerman',
    'Dorothy T. Grotos': 'Dorothy Grotos',
    'Ellen M. Bozman': 'Ellen Bozman',
    'James B. Hunter, III': 'James B. Hunter III',
    'James Hunter': 'James B. Hunter III',
    'Jay Fisette': 'G.N. “Jay” Fisette, Jr.',
    'John Vihstadt': 'John E. Vihstadt',
    'John W. Purdy': 'John Purdy',
    'Joseph Fisher': 'Joseph L. Fisher',
    'Joseph Wholey': 'Joseph S. Wholey',
    'Katie Cristol': 'Kate A. "Katie" Cristol',
    'Kenneth Haggerty': 'Dr. Kenneth M. Haggerty',
    'Kenneth M. Haggerty': 'Dr. Kenneth M. Haggerty',
    'Leone Leone B. Buchholz': 'Leone B. Buchholz',
    'Libby Garvey': 'Libby T. Garvey',
    'Lucas H. Bleviins': 'Lucas H. Blevins',
    'Mary Hughes Hynes': 'Mary H. Hynes',
    'Matt de Ferranti': 'Matthew D. "Matt" de Ferranti',
    'Maureen Coffey': 'Maureen E. Coffey',
    'Paul Ferguson': 'Paul F. Ferguson',
    'Stephen H. Detwiler': 'Stephen Detwiler',
    'Susan Cunningham': 'Susan R. Cunningham',
    'Takis Karantonis': 'Takis P. Karantonis',
    'Thomas Richards': 'Thomas W. Richards',
    'W.A.E. McShea': 'W. A. E. McShea',
    'W.P. Ames': 'W. P. Ames',
    'Walter L. Frankland, Jr.': 'Walter Frankland',
}


def rows():
    """The roll as transcribed, one row per member per year and one per
    event it dates."""
    return listing("roll")


def name_of(printed):
    """The roster's name for a member the roll prints."""
    return SAME_PERSON.get(printed.strip(), printed.strip())


def month_of(date):
    """A roll date as (year, month). The roll gives a day where it has one
    and a month where it does not; the month is all this stage keeps."""
    year, month = date.split("-")[:2]
    return int(year), int(month)


def service(year=None):
    """The names the roll puts on the Board, as {year: {name, ...}}, or one
    year's set."""
    by_year = {}
    for _, r in rows().iterrows():
        by_year.setdefault(int(r.year), set()).add(name_of(r["name"]))
    return by_year if year is None else by_year.get(year, set())


def events(kinds):
    """Every dated event of the kinds given: (name, year, month, event)."""
    out = []
    for _, r in rows().iterrows():
        if r.event in kinds and r.event_date:
            year, month = month_of(r.event_date)
            out.append((name_of(r["name"]), year, month, r.event))
    return out


# The two mid-term departures after 1932 that the roll leaves undated, each
# dated by another source the roster already holds or cites.
#
# John G. Milliken resigned in February 1990 on his appointment as Virginia's
# secretary of transportation, which Novack dates; the roll records it only as
# "John G. Milliken - James Hunter (5/15/90)".
#
# Barbara A. Favola won the state Senate in November 2011 and the roll lists
# her through 2011 and not in 2012, whose entry names the five members at the
# Board's organising meeting of 2 January without her. ARLnow reports the
# court order setting the special election for her seat as issued on 19
# December 2011 and that "the date could not be set until Favola formally
# resigned from the County Board", so her resignation was in hand by then
# (arlnow2011favolaseat). Neither source gives the effective day, and the
# month is all this stage keeps.
DATED_ELSEWHERE = {
    ("John G. Milliken", 1990): ((1990, 2), "novack1994"),
    ("Barbara A. Favola", 2011): ((2011, 12), "arlnow2011favolaseat"),
}


def departures():
    """{(name, year): (year, month)} for every departure the roll dates, and
    the two DATED_ELSEWHERE dates for it."""
    out = {(name, year): (year, month) for name, year, month, _ in events(LEAVES)}
    for key, (when, _) in DATED_ELSEWHERE.items():
        out.setdefault(key, when)
    return out


def dated_by(name, year):
    """The citekey behind a departure the roll does not date, or the roll."""
    found = DATED_ELSEWHERE.get((name, year))
    return found[1] if found else SOURCE


def arrivals():
    """{(name, year): (year, month, event)} for every arrival the roll
    dates."""
    return {(name, year): (year, month, event)
            for name, year, month, event in events(ARRIVES)}


def seats(name, year, month, event):
    """Whether an arrival the roll dates begins a term in that month."""
    if event == "elected" and month in REGULAR_ELECTION:
        return False
    return True


def ends_at(d):
    """{index: (year, month)} for each roster term the roll ends earlier than
    the roster does.

    The roll dates a departure; the roster, with no record of one, runs the
    term to the month its successor was seated. Where the two differ the
    roll wins: it is the county's own record of service, and the roster's end
    was never a claim about when the member left, only about when the next
    member arrived (docs/members.md, "The roster").
    """
    out = {}
    for (name, _), (year, month) in departures().items():
        leaves = year * 12 + month
        for i, t in d.iterrows():
            if t["name"] != name or t.district != "at large":
                continue
            begins = int(t.start_year) * 12 + int(t.start_month)
            if pd.isna(t.end_year):
                continue
            ends = int(t.end_year) * 12 + int(t.end_month)
            if begins <= leaves < ends:
                out[i] = (year, month)
    return out


def corrections(d: pd.DataFrame):
    """Every term end the roll moves, moved, with the roll cited beside the
    source that was there and a note saying what the roll records. Returns
    the table and {(name, year, month): (year, month)} - where each seat
    changed hands, against the end the roster had given it."""
    d = d.copy()
    cut = {}
    for i, (year, month) in ends_at(d).items():
        cut[(d.at[i, "name"], year, month)] = (int(d.at[i, "end_year"]),
                                               int(d.at[i, "end_month"]))
        was = f"{int(d.at[i, 'end_year'])}-{int(d.at[i, 'end_month']):02d}"
        d.at[i, "end_year"], d.at[i, "end_month"] = year, month
        cites = dated_by(d.at[i, "name"], year)
        if cites not in d.at[i, "source"]:
            d.at[i, "source"] = f"{d.at[i, 'source']}; {cites}"
        d.at[i, "note"] = (
            (d.at[i, "note"] + " " if d.at[i, "note"] else "")
            + f"Left the seat in {year}-{month:02d}, which {cites} dates; the "
              f"roster ran the term to {was}, the month the next member was seated, having "
              f"no record of the departure itself."
        ).strip()
    return d, cut


def terms(d: pd.DataFrame, was: dict):
    """A term for every member the roll puts on the Board in a year the
    roster has nobody of that name in at all.

    One so far: Tannia Talento, appointed in July 2023 to the rest of Katie
    Cristol's term. She won no contest, so no election record holds her, and
    the roster had the seat still with Cristol until corrections() cut it.

    `was` is what corrections() cut: {(name, year, month): (year, month)},
    the month a seat changed hands against the end the roster had given the
    departing member's term. That end is the term being filled - the seat's
    next regular election is not moved by who sits out the remainder - so the
    incoming member takes it.
    """
    names = set(d["name"])
    for (name, year), (y, month, event) in sorted(arrivals().items(), key=lambda kv: kv[1][:2]):
        if name in names or not seats(name, y, month, event):
            continue
        ends = [end for (_, cy, cm), end in was.items() if (cy, cm) == (y, month)]
        if len(ends) != 1:
            raise ValueError(
                f"{name} is seated in {y}-{month:02d} and the roster has no term for them, "
                f"but {len(ends)} seats changed hands that month, so which term is being "
                f"filled is not determined. Read the roll and key the term.")
        yield {"name": name, "district": "at large",
               "start_year": y, "start_month": month,
               "end_year": ends[0][0], "end_month": ends[0][1],
               "seated_by": APPOINTMENT if event == "appointed" else SPECIAL_ELECTION,
               "source": SOURCE,
               "note": "Seated without winning a contest, so no election record holds this "
                       "term; the county's roll is the only source for it. The term runs to "
                       "the end the seat already had, which the next regular election fills."}


# Years the roll and Novack name different people, each for a reason that is
# not a disagreement about who served.
EXPECTED = {
    # The roll seats a November winner in the year of the election; the
    # roster seats him the following January (docs/members.md).
    # Both halves of the same difference: the roll seats the three November
    # winners in 1939 and drops the three they replaced, where the roster
    # holds the outgoing three to the end of the year.
    1939: {"Edmund D. Campbell", "Basil M. DeLashmutt", "Leo C. Lloyd",
           "George M. Yeatman", "W. A. E. McShea", "W. P. Ames"},
    1952: {"Howard R. Massey"},     # the roll appoints him in November, Novack in September
    # The roll prints one name twice where the fifth member should be, so the
    # member Novack names in that seat is in no roll entry: F. Freeland Chew
    # is printed twice in 1941 and Mary Margaret Whipple in 1986, and these
    # are the two the page leaves out.
    1941: {"Elizabeth B. Magruder"},
    1986: {"John G. Milliken"},
}


def check_against_novack(d: pd.DataFrame, first=1932, last=1994):
    """The roll and Novack are independent records of the same Board for
    1932-1994, so every year they both cover must name the same people.

    Both are cited on the terms they agree about, which is most of them: the
    two records give the same departure month for all ten the roll dates in
    these years. What this refuses is a year where one names somebody the
    other does not, save the differences EXPECTED declares above.
    """
    held = {}
    for _, t in d.iterrows():
        if t.district != "at large" or pd.isna(t.end_year):
            continue
        for year in range(int(t.start_year), int(t.end_year) + 1):
            held.setdefault(year, set()).add(t["name"])
    rolled = service()
    for year in range(first, last + 1):
        ours, theirs = held.get(year, set()), rolled.get(year, set())
        only_ours, only_theirs = ours - theirs, theirs - ours
        allowed = EXPECTED.get(year, set())
        if (only_ours | only_theirs) - allowed:
            raise ValueError(
                f"{year}: the roster and the county's roll name different members.\n"
                f"  the roster alone: {sorted(only_ours - allowed) or 'none'}\n"
                f"  the roll alone:   {sorted(only_theirs - allowed) or 'none'}\n"
                "  if the difference is a convention and not a disagreement, declare it "
                "in EXPECTED in code/clean/members_roster_roll.py.")


def witnessed(d: pd.DataFrame) -> pd.DataFrame:
    """The roll cited beside the source already there, on every term it
    witnesses: 1932 on, where the two records agree about the member."""
    d = d.copy()
    rolled = service()
    for i, t in d.iterrows():
        if t.district != "at large" or SOURCE in t.source:
            continue
        years = range(int(t.start_year),
                      (int(t.end_year) if pd.notna(t.end_year) else int(t.start_year)) + 1)
        if any(t["name"] in rolled.get(y, set()) for y in years):
            d.at[i, "source"] = f"{t.source}; {SOURCE}"
    return d


# Every stretch after 1932 when an at-large seat stood empty: the member who
# left, the month they left, the member who took the seat and the month they
# were seated. Both months belong to their holder - a month belongs to
# whoever held the seat for any part of it - so what stands empty is the
# months strictly between.
#
# The pairs are read off the roll, which is why they are written out rather
# than computed from it: the roll dates arrivals and departures but does not
# say which seat each belongs to, and in a year like 1952, when a court
# removed three members at once, nothing in the record pairs them. Taking
# the next arrival after each departure gives whole years of false vacancies
# in the 1930s and 1960s. Here the reader checks six pairs against the page.
#
# John G. Milliken's is the one departure the roll leaves undated, recording
# it only as "John G. Milliken - James Hunter (5/15/90)". Novack dates his
# resignation to February 1990, on his appointment as Virginia's secretary
# of transportation, and that month stands.
EMPTY = [
    ("John G. Milliken", (1990, 2), "James B. Hunter III", (1990, 5)),
    ("Barbara A. Favola", (2011, 12), "Libby T. Garvey", (2012, 3)),
    ("James B. Hunter III", (1997, 9), "Barbara A. Favola", (1997, 11)),
    ("Albert C. Eisenberg", (1999, 2), "Michael D. Lane", (1999, 4)),
    ("Charles P. Monroe", (2003, 1), "J. Walter Tejada", (2003, 3)),
    ("Christopher E. Zimmerman", (2014, 2), "John E. Vihstadt", (2014, 4)),
    ("Erik Gutshall", (2020, 4), "Takis P. Karantonis", (2020, 7)),
]


def vacancies():
    """The months no one held an at-large seat, from EMPTY above."""
    out = set()
    for _, (ly, lm), _, (ay, am) in EMPTY:
        for m in range(ly * 12 + lm + 1, ay * 12 + am):
            out.add(((m - 1) // 12, (m - 1) % 12 + 1))
    return out


def check_empty_is_the_roll(d: pd.DataFrame):
    """Every pair in EMPTY is a departure and an arrival the roll dates, in
    the month given, so the table above cannot drift from the source. Only
    Milliken's departure is exempt, being Novack's date."""
    dated = {(name, year, month) for name, year, month, _ in events(LEAVES)}
    comes = {(name, y, m) for (name, _), (y, m, _) in arrivals().items()}
    for left, (ly, lm), came, (ay, am) in EMPTY:
        if (left, ly, lm) not in dated and (left, ly) not in DATED_ELSEWHERE:
            raise ValueError(f"EMPTY has {left} leaving in {ly}-{lm:02d}, which the roll "
                             f"does not date")
        if (came, ay, am) not in comes:
            raise ValueError(f"EMPTY has {came} seated in {ay}-{am:02d}, which the roll "
                             f"does not date")
