"""The county's roll, read -> data/transcribed/by_claude/arlington_county/members_roll.csv

    .venv/bin/python code/transcribe/members_roll.py

One row per member per year from 1932, and a further row for each arrival or
departure the roll dates, with the date as the page prints it. The source is
data/raw/arlington_county/members_roll.pdf, whose text layer is the page's own
characters rather than OCR, so a date is read and not guessed
(docs/members.md, "The county's roll").

    year  name  office  event  event_date  entry  source

`office` is what the page prints beside the name - chairman, vice-chairman,
acting chairman - and is blank where it prints nothing or "Member". `event`
is the arrival or departure the entry records, one of EVENTS, with
`event_date` the date printed for it, `YYYY-MM-DD` where the page gives a
day and `YYYY-MM` where it gives only a month. A member with no event in a
year has one row with both blank. `entry` is the page's own text for that
member, kept so a reader can check the parse against the print.

Nothing here is matched to a Board member or resolved against another
source: code/clean/members_roster_roll.py does that, and the whole-month
rule that turns these dates into terms lives there too.

**Seventy-seven of the ninety-five years parse by rule**, one member to a
line. The other eighteen do not, because the county's pages carry a member's
entry wrapped onto a second line, two members run together on one, notes
about the Board's clerk set in the member column, a year printed twice in two
decade panels, a footnote, and in 1952 two sub-periods of a year that saw
three members removed by a court. No rule covers those without also
mis-splitting a year that is currently fine, so each of the eighteen is read
off the print and written out in AS_READ below, where a reviewer can hold one
block at a time against the page.

AS_READ is checked, not trusted. For each year it declares, every surname and
every date the page prints must appear in the entries given for it
(check_nothing_lost), so an entry dropped or a digit changed in the keying
stops the run. A line in any other year that does not parse stops it too.
"""
import csv
import re

import paths

OUT = paths.BY_CLAUDE / "arlington_county" / "members_roll.csv"
ROLL = paths.RAW / "arlington_county" / "members_roll.pdf"
SOURCE = "arlingtonva2026members"

FIELDS = ["year", "name", "office", "event", "event_date", "entry", "source"]

FIRST, LAST = 1932, 2026

# The page's own words for an arrival or a departure, mapped to the word this
# file uses. Longest first: "resigned as chairman" is not "resigned".
EVENTS = [
    # The chair is a vote of the Board among its own members and says nothing
    # about who holds a seat. It is kept apart from an election to the Board
    # so that code/clean/ cannot read one as the other.
    ("elected as vice-chair", "took the vice-chair"),
    ("elected as vice chair", "took the vice-chair"),
    ("elected as chair", "took the chair"),
    ("resigned as chairman", "left the chair"),
    ("resigned from board", "resigned"),
    ("resigned", "resigned"),
    ("removed", "removed"),
    ("died", "died"),
    ("appointed as circuit court judge", "left for the bench"),
    ("appointed", "appointed"),
    # One phrase, not an election followed by another: the roll writes
    # "Elected in Special Election 4/8/14" for a single event.
    ("elected in special election", "special election"),
    ("special election", "special election"),
    ("took office", "took office"),
    ("elected to state senate", "elected to the senate"),
    ("reelected", "re-elected"),
    ("re-elected", "re-elected"),
    ("elected", "elected"),
]

# A date as the page prints it: 5/13/33, 1/30/96, 7/15/2023, or 11/95 with no
# day. Two-digit years are 1900s through 1999 and 2000s after.
DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b")

# "Elected in March 2012": a month by name, which the roll uses from 2012.
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
NAMED_MONTH = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+((?:19|20)\d\d)\b", re.I)

# A member's line: the name, then the office after a comma, then the entry's
# note after a dash or inside brackets. The name is what comes first.
# "Vice-President" is the page's own slip for the vice-chair, printed once,
# at 1977; without it the title stays in the member's name.
OFFICE = re.compile(r",?\s*(Acting Chairman|Chairman|Vice[- ]Chair(?:man)?|Chair|"
                    r"Vice[- ]President|Member)\b", re.I)

# The years the print does not lay out one member to a line. Each is read off
# data/raw/arlington_county/members_roll.pdf and written here as the page
# would read if it had: one member's whole entry per string, in the order
# printed. check_nothing_lost holds each block to the page's own text.
AS_READ = {
    # Fellows and Gall share the first line.
    1933: ["Harry A. Fellows, Chairman",
           "John C. Gall – Resigned 5/13/33",
           "C.B. Garnett – Appointed 12/11/33",
           "Fred A. Gosnell, Sr. – Resigned 12/11/33",
           "Lyman M. Kelley",
           "Elizabeth B. Magruder",
           "B.M. Smith – Appointed 6/1/33"],
    # Smith's acting chairmanship is a span, not an arrival.
    1934: ["Lyman M. Kelley, Chairman – Removed 11/3/34",
           "B.M. Smith, Acting Chairman – 11/14/34 – 12/31/34",
           "Harry A. Fellows",
           "Christopher B. Garnett",
           "Elizabeth B. Magruder",
           "W.A.E. McShea – Appointed 11/8/34"],
    # Magruder's entry wraps: she left the chair in March and the Board in May.
    1947: ["Elizabeth B. Magruder, Chairman – Resigned as Chairman 3/11/47 – "
           "Resigned from Board 5/11/47",
           "Basil M. DeLashmutt, Chairman – 3/11/47 – 12/31/47",
           "F. Freeland Chew",
           "Harry W. Cuppett – Appointed 5/17/47",
           "Daniel A. Dugan",
           "Leo C. Lloyd – Died 11/3/47",
           "Alfred E. Frisbie – Appointed 11/26/47"],
    # The court removed three members in September; the page prints the year
    # as two sub-periods, and Frisbie and Peck appear in both. Each person is
    # given once here, with the events the page dates for them.
    1952: ["Robert W. Cox, Chairman – Removed 9/17/52",
           "Allan L. Dean – Removed 9/17/52",
           "Daniel A. Dugan – Removed 9/17/52",
           "Alfred E. Frisbie, Chairman",
           # The page sets Peck's name against the first sub-period's dates
           # and records no event for him; Novack has his term from January.
           "Robert A. Peck",
           "M. Rex Byrne – Appointed 9/18/52 – 11/10/52",
           "John A. Tillema – Appointed 9/18/52 – 11/10/52",
           "Howard R. Massey – Appointed 11/10/52",
           "Leone B. Buchholz – Elected 11/4/52 – Took Office 11/10/52",
           "Robert H. Detwiler – Elected 11/4/52 – Took Office 11/10/52",
           "Alvin F. Kimel – Elected 11/4/52 – Took Office 11/10/52"],
    # Chew is printed twice, as chairman and again as a member.
    1941: ["F. Freeland Chew, Chairman",
           "Edmund D. Campbell",
           "Basil M. DeLashmutt",
           "Leo C. Lloyd"],
    # Notes about the clerk run across all five member lines after the dash.
    1971: ["Joseph L. Fisher, Chairman",
           "Jay E. Ricks, Vice-Chairman",
           "Kenneth M. Haggerty",
           "A. Leslie Phillips",
           "Joseph S. Wholey"],
    # A footnote to Bozman's 1975 arrival sits above the members.
    1978: ["John W. Purdy, Chairman",
           "Ellen M. Bozman, Vice-Chairman",
           "Walter L. Frankland, Jr.",
           "Dorothy T. Grotos",
           "Joseph S. Wholey"],
    # Printed in both the 1972-1981 and the 1982-1991 panel.
    1981: ["Stephen H. Detwiler, Chairman",
           "Dorothy T. Grotos, Vice-Chairman",
           "Ellen M. Bozman",
           "John G. Milliken",
           "Walter L. Frankland, Jr."],
    # Clerk note on the first two lines.
    1982: ["Stephen H. Detwiler, Chairman",
           "Dorothy T. Grotos, Vice-Chairman",
           "Ellen M. Bozman",
           "John G. Milliken",
           "Walter L. Frankland, Jr."],
    # Whipple is printed twice, as chairman and again as a member; Eisenberg's
    # office follows a full stop rather than a comma.
    1986: ["Mary Margaret Whipple, Chairman",
           "Albert C. Eisenberg, Vice-Chairman",
           "Ellen M. Bozman",
           "Michael E. Brunner"],
    # Clerk note on the first two lines.
    1989: ["Ellen M. Bozman, Chairman",
           "Albert C. Eisenberg, Vice-Chairman",
           "John G. Milliken",
           "William T. Newman, Jr.",
           "Mary Margaret Whipple"],
    # Milliken's seat passes to Hunter in May; the page gives the date alone.
    1990: ["Albert C. Eisenberg, Chairman",
           "William T. Newman, Jr., Vice-Chairman",
           "Ellen M. Bozman",
           "John G. Milliken",
           "James Hunter – Took Office 5/15/90",
           "Mary Margaret Whipple"],
    # Newman leaves for the circuit court; the page dates neither his
    # departure nor Winslow's arrival.
    1993: ["James B. Hunter, III, Chairman",
           "Mary Margaret Whipple, Vice-Chairman",
           "Ellen M. Bozman",
           "Albert C. Eisenberg",
           "William T. Newman, Jr. – Appointed as Circuit Court Judge",
           "Benjamin H. Winslow, Jr. – Replaced Newman"],
    # Whipple's line carries the clerk note and runs into Eisenberg's, whose
    # office wraps to the next line.
    1994: ["Mary Margaret Whipple, Chairman",
           "Albert C. Eisenberg, Vice-Chairman",
           "Ellen M. Bozman",
           "James B. Hunter, III",
           "Benjamin H. Winslow, Jr."],
    # Whipple's entry wraps onto a second line.
    1995: ["Albert C. Eisenberg, Chairman",
           "Ellen M. Bozman, Vice-Chairman",
           "James B. Hunter, III",
           "Mary Margaret Whipple – Resigned 12/14/95 – Elected to State Senate 11/95",
           "Benjamin H. Winslow, Jr."],
    # Zimmerman's entry wraps onto a second line.
    1996: ["James B. Hunter, III, Chairman",
           "Ellen M. Bozman, Vice-Chairman",
           "Albert C. Eisenberg",
           "Paul Ferguson",
           "Christopher E. Zimmerman – Special Election 1/30/96: Replaced Mary Margaret Whipple"],
    # Eisenberg resigns from the chair and the Board on one date, and the
    # page records Ferguson and Favola moving up with "until 2/13/99".
    1999: ["Albert C. Eisenberg, Chairman – Resigned as of 2/13/99",
           "Paul Ferguson, Chairman – Vice Chairman until 2/13/99",
           "Barbara A. Favola, Vice Chairman – Member until 2/13/99",
           "Jay Fisette",
           "Christopher Zimmerman",
           "Michael D. Lane – Special Election 4/13/99 for Eisenberg Seat"],
    # A clerk note stands on a line of its own.
    2000: ["Barbara A. Favola, Chairman – Reelected 11/00",
           "Jay Fisette, Vice Chairman",
           "Paul Ferguson",
           "Charles P. Monroe – Elected 11/99 to Lane Seat",
           "Christopher Zimmerman"],
    # Ferguson's and Tejada's entries each wrap onto a second line.
    2003: ["Paul Ferguson, Chairman – Elected as Vice Chairman on 1/1/03; elected as "
           "Chairman on 1/17/03; reelected 11/4/03",
           "Barbara A. Favola, Vice Chairman – Elected as Vice Chairman on 1/17/03",
           "Jay Fisette, Member",
           "Christopher Zimmerman, Member",
           "J. Walter Tejada, Member – Special election on 3/11/03 for seat of Charles P. "
           "Monroe who died 1/11/03; reelected 11/4/03"],
    # Printed in both the 2002-2011 and the 2012-2021 panel.
    2012: ["Mary Hughes Hynes, Chairman – Elected as Chairman on 1/2/12",
           "J. Walter Tejada, Vice Chairman – Elected as Vice Chairman on 1/2/12",
           "Jay Fisette, Member",
           "Libby Garvey, Member – Elected in March 2012",
           "Christopher Zimmerman, Member"],
    # Karantonis's entry wraps onto a second line.
    2020: ["Libby Garvey, Chair – Elected as Chair on 1/2/20",
           "Erik Gutshall, Vice-Chair – Elected as Vice-Chair on 1/2/20",
           "Matt de Ferranti, Member",
           "Katie Cristol, Member",
           "Christian Dorsey, Member",
           "Takis Karantonis, Member – Special election on 7/7/20 for seat of Erik Gutshall "
           "who died 4/16/20"],
}

# What the page prints for a year that AS_READ does not account for, and need
# not: notes about the Board's clerk, a footnote, the sub-period headings, and
# the second printing of a year that two decade panels both carry. Each is
# the reason its year is in AS_READ, named so the check below can pass.
SET_ASIDE = {
    1941: ["F. Freeland Chew"],                        # printed twice
    1952: ["1/1/52", "9/17/52", "11/10/52", "12/31/52"],   # sub-period headings
    1971: ["Phyllis", "Ferrari", "Clerk", "died", "8/13/71", "Lou", "Hollingshead",
           "appointed", "Acting", "from", "to", "8/17/71", "1/17/72", "Ms", "Dottie",
           "L", "Bowen", "Clerk", "1/1/72"],
    1978: ["Filling", "unexpired", "term", "of", "Joseph", "Fisher"],   # a footnote
    1981: ["Stephen", "Detwiler", "Dorothy", "Grotos", "Ellen", "Bozman",
           "John", "Milliken", "Walter", "Frankland"],  # printed twice
    1982: ["Jean", "Julian", "appointed", "Clerk", "6/1/82"],
    1986: ["Mary", "Margaret", "Whipple"],             # printed twice
    1989: ["Janice", "Collis", "NISBET", "appointed", "clerk", "4/8/89"],
    1994: ["Sabra", "Jones", "appointed", "clerk", "1/10/94"],
    2000: ["Toni", "Copeland", "appointed", "Clerk", "1/1/00", "on"],
    2012: ["Mary", "Hughes", "Hynes", "Walter", "Tejada", "Jay", "Fisette",
           "Libby", "Garvey", "Christopher", "Zimmerman", "Elected",
           "Chairman", "Vice", "March", "Member", "1/2/12"],   # printed twice
}

# Two years the roll itself leaves a seat short, printing one member's name
# twice where the fifth should be. The Board had five members in both, and
# Novack names the fifth; the roll is simply wrong here, so these years
# witness four and the roster's fifth seat rests on Novack alone.
SHORT = {1941: "F. Freeland Chew is printed as chairman and again as a member",
         1986: "Mary Margaret Whipple is printed as chairman and again as a member"}

DECADE_HEADING = re.compile(r"^\d{4}\s*[-–]\s*(\d{4}|Present)$")
YEAR_HEADING = re.compile(r"^(19[3-9]\d|20[0-2]\d)$")


def printed(pdf=ROLL):
    """The roll's lines, year by year, as the print carries them."""
    import pymupdf
    text = "".join(page.get_text() for page in pymupdf.open(pdf))
    lines = [ln.replace("\xa0", " ").strip() for ln in text.split("\n")]
    # The page's own heading repeats after the breadcrumb; the roll starts there.
    start = max(i for i, ln in enumerate(lines)
                if ln == "Historical Members: 1932 - Present")
    years, year = {}, None
    for ln in (ln for ln in lines[start + 1:] if ln):
        if DECADE_HEADING.match(ln):
            continue
        if YEAR_HEADING.match(ln):
            year = int(ln)
            years.setdefault(year, [])
        elif year is not None:
            years[year].append(ln)
    return years


def words(text):
    """The words and dates in a stretch of the page, for comparing a block
    of AS_READ against the print. Case and punctuation are dropped; a date
    keeps its slashes."""
    marks = ".,;:()*\"'"
    kept = (w.strip(marks) for w in re.split(r"[\s–-]+", text))
    # A lone initial carries nothing a keying slip could hide behind, and the
    # clerk notes this check sets aside are full of them.
    return {w for w in kept if len(w) > 1}


def check_nothing_lost(year, lines, entries):
    """Every word and date the page prints for a year is in the entries read
    for it, or in SET_ASIDE as a reason that year is read by hand at all."""
    missing = words(" ".join(lines)) - words(" ".join(entries)) - set(SET_ASIDE.get(year, []))
    if missing:
        raise AssertionError(
            f"{year}: the entries in AS_READ do not account for what the roll prints: "
            + ", ".join(sorted(missing))
            + "\n  the print reads:\n    " + "\n    ".join(lines)
            + "\n  AS_READ gives:\n    " + "\n    ".join(entries))


# A note that turns to the member before: "Special election on 7/7/20 for
# seat of Erik Gutshall who died 4/16/20". What follows the marker is that
# person's departure, not this row's arrival, and the roll records some of
# those nowhere else - Gutshall's death and Monroe's are each printed only on
# the note of the member who replaced them.
ANOTHER = re.compile(r"\b(?:for seat of|to fill seat vacated by|replaced)\s+"
                     r"(?P<name>(?:[A-Z][\w.'-]*\s*){1,4}?)(?=\s+who\b|[,;.]|$)", re.M)


def note_begins(entry):
    """Where a member's entry stops being a name and an office and starts
    recording what happened. The page marks that boundary three ways - a
    dash, a bracket, or nothing at all, as in "James B. Hunter, III Resigned
    9/8/97" - so the earliest of the three wins."""
    marks = [entry.find(" – "), entry.find(" (")]
    low = entry.lower()
    for printed_word, _ in EVENTS:
        marks.append(low.find(" " + printed_word))
    date = DATE.search(entry)
    if date:
        marks.append(date.start())
    found = [m for m in marks if m > 0]
    return min(found) if found else len(entry)


def split_entry(entry):
    """A member's entry as name, office and note."""
    at = note_begins(entry)
    head, note = entry[:at], entry[at:].lstrip(" –(").rstrip(")")
    office = ""
    found = OFFICE.search(head)
    if found:
        office = found.group(1).strip()
        head = head[:found.start()] + head[found.end():]
    name = head.strip().strip(",").strip()
    if office.lower() == "member":
        office = ""
    low = note.lower()
    if office.lower().startswith("vice-pres") or office.lower().startswith("vice pres"):
        office = "Vice-Chairman"
    if not office and "as vice-chair" in low or not office and "as vice chair" in low:
        office = "Vice-Chairman"
    elif not office and "as chair" in low:
        office = "Chairman"
    return name, office.lower().replace("vice chairman", "vice-chairman"), note.strip()


def a_date(match):
    """A printed date as YYYY-MM-DD, or YYYY-MM where no day is given."""
    one, two, three = match.groups()
    if three is None:                      # 11/95: a month and a year
        year = int(two) + (1900 if int(two) >= 30 else 2000)
        return f"{year}-{int(one):02d}"
    year = int(three)
    if year < 100:
        year += 1900 if year >= 30 else 2000
    return f"{year}-{int(one):02d}-{int(two):02d}"


def events(note):
    """The arrivals and departures a note records: (event, date). A note with
    a word from EVENTS and no date gives the event with a blank date; a date
    with no word gives nothing, since what happened is not stated."""
    low = note.lower()
    found = []
    for printed_word, event in EVENTS:
        for m in re.finditer(re.escape(printed_word), low):
            if any(m.start() < s or m.end() > e for s, e in []):
                continue
            found.append((m.start(), m.end(), event))
    # Keep the longest reading of each stretch: "resigned as chairman" over
    # "resigned", "appointed as circuit court judge" over "appointed".
    found.sort(key=lambda f: (f[0], -(f[1] - f[0])))
    kept = []
    for start, end, event in found:
        if kept and start < kept[-1][1]:
            continue
        kept.append((start, end, event))
    out = []
    for i, (_, end, event) in enumerate(kept):
        until = kept[i + 1][0] if i + 1 < len(kept) else len(note)
        date = DATE.search(note, end, until)
        if date:
            out.append((event, a_date(date)))
            continue
        named = NAMED_MONTH.search(note, end, until)
        if named:
            month = MONTHS.index(named.group(1).title()) + 1
            out.append((event, f"{named.group(2)}-{month:02d}"))
        else:
            out.append((event, ""))
    return out


def rows():
    """One row per member per year, and one per event the roll dates."""
    years = printed()
    have = sorted(years)
    if have != list(range(FIRST, LAST + 1)):
        raise AssertionError(f"the roll prints {have[0]}-{have[-1]}, "
                             f"expected {FIRST}-{LAST}")
    unparsed = []
    for year in have:
        entries = AS_READ.get(year)
        if entries is not None:
            check_nothing_lost(year, years[year], entries)
        else:
            entries = years[year]
        seen = set()
        for entry in entries:
            name, office, note = split_entry(entry)
            if not name or DATE.search(name) or len(name.split()) > 5:
                unparsed.append((year, entry))
                continue
            if name in seen:
                unparsed.append((year, f"{entry}  (a second entry for {name})"))
                continue
            seen.add(name)
            # A note that names the member before carries that member's
            # departure; it is their row, not this one's.
            other = ANOTHER.search(note)
            mine, theirs = (note[:other.start()], note[other.end():]) if other else (note, "")
            found = events(mine)
            if not found:
                yield dict(year=year, name=name, office=office, event="",
                           event_date="", entry=entry, source=SOURCE)
            for event, date in found:
                yield dict(year=year, name=name, office=office, event=event,
                           event_date=date, entry=entry, source=SOURCE)
            for event, date in events(theirs):
                yield dict(year=year, name=other.group("name").strip(), office="",
                           event=event, event_date=date, entry=entry, source=SOURCE)
        if len(seen) < 5 and year not in SHORT:
            unparsed.append((year, f"only {len(seen)} members read"))
    if unparsed:
        raise AssertionError(
            "lines of the roll no rule reads, and no year in AS_READ covers:\n  "
            + "\n  ".join(f"{y}: {line}" for y, line in unparsed)
            + "\n\nread the year off data/raw/arlington_county/members_roll.pdf and "
              "write it into AS_READ.")


def main():
    out = list(rows())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(out)
    dated = sum(1 for r in out if r["event_date"])
    print(f"{OUT.relative_to(paths.ROOT)}: {len(out)} rows, "
          f"{len({r['name'] for r in out})} people, {FIRST}-{LAST}, "
          f"{dated} dated events, {len(AS_READ)} years read by hand")


if __name__ == "__main__":
    main()
