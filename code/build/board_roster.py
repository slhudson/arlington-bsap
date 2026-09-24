"""Who held each seat and when, 1870 through 2026, as one row per person per term.

A module, not a step: board_members.py takes these terms and attaches race
and gender. A term, not a person-year: name, district, and when service began and ended.
Person-years fall out of this; the reverse does not, because a term that starts
in May or ends in February cannot be recovered from a list of years.

    name  district  start_year  start_month  end_year  end_month  seated_by  source  note

`district` is a magisterial district through 1931 and "at large" from 1932,
when the County Manager plan replaced districts with countywide election.

`seated_by` is how the term began: a regular election, a special election, an
appointment, or unrecorded where O'Leary says only that someone was replaced.
A term that Novack's span is cut at an election the person stood in and lost
continues however it began (Frisbie, appointed in November 1947, stood that
month and did not win, and his 1948 term is still the appointment). This is a
column rather than something read out of `note` because three builds need
it - which terms an election seated, when a special election handed over -
and a reworded note would otherwise move their numbers with nothing to say so.

Months are given where a source gives them and left empty otherwise. Under the
magisterial system elections were held in May and the board took office then,
so those terms run May to May. From the November 1903 election the 1902
constitution moved county and district elections to November and seated their
winners on 1 January following, so those terms run January to January - see
seated() below. Under the County Manager plan members took office on 1 January
too, so those run January to December unless a source says otherwise.

**A vacant seat is not a row.** Nobody served, so there is no person and no
term. Vacancies are recorded in docs/sources.md instead.

Sources:

  oleary2010       1870-1915  who held each magisterial district, by election
  novack1994       1930-1994  terms of service, with mid-term departures

Gaps left empty rather than assumed: 1916-1929, and 1995 onward.
"""
import re

import pandas as pd

import citekeys
import elections
from elections import COUNTY_HISTORY_THROUGH, surname
from paths import TRANSCRIBED

BY_CLAUDE = TRANSCRIBED / "by_claude"
NOVACK_PUBLISHED = 1994
PRESENT = 2026            # the roster is checked month by month up to here;
                          # current terms run to 2029, and board_seats stops here

# The Board's size is a fact about its constitution, not a figure anyone
# counted, so it is stated here and imported by residents.py and
# board_seats.py rather than typed into each. Three magisterial districts
# with one supervisor each from 1870 (Va. Const. 1902 sec. 111 restates it
# for the period it covers); five members elected countywide from the County
# Manager plan, adopted at the November 1931 referendum and seated in January
# 1932 (anderson1958). These are the seats that exist, which is not the same
# question as the seats filled - see docs/questions.md. No source names a
# party before the plan either, so it is also where party begins.
SEATS_DISTRICT = 3.0
SEATS_AT_LARGE = 5.0
AT_LARGE_FROM = 1932

# The values seated_by takes. Named so a consumer compares against a constant
# and a typo is an AttributeError rather than a term that silently matches
# nothing.
ELECTION = "election"
SPECIAL_ELECTION = "special election"
APPOINTMENT = "appointment"
UNRECORDED = "unrecorded"
SEATED_BY = (ELECTION, SPECIAL_ELECTION, APPOINTMENT, UNRECORDED)

# Va. Const. 1902 sec. 112: county and district officers hold office for four
# years. Applied from the November 1903 election; before it, terms ran from one
# May election to the next and the listings are continuous.
TERM_YEARS = 4

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}
MONTH_NAMES = {v: k for k, v in MONTHS.items()}
MONTH_RE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?", re.I)
YEAR_RE = re.compile(r"\b((?:18|19|20)\d\d)\b")
# "Corbett 213 Hagen 189" - a name followed by its vote count, repeated
CANDIDATE_VOTES = re.compile(r"([A-Z][A-Za-z.'’\- ]*?)\s+([\d,]+)(?=\s|$)")


def month_of(text):
    m = MONTH_RE.search(text or "")
    return MONTHS[m.group(1).title()] if m else ""


def seated(year, election_date):
    """When an election's winners take office: (year, month).

    Under the magisterial system elections were held in May and the board took
    office then. The 1902 constitution moved county and district elections to
    November and seated their winners on 1 January following, so from the
    November 1903 election a term begins in the January after the vote, not at
    the vote. Applying the vote's own month would date every term from 1904 on
    two months early and shift each handover's seat-years with it.

    The Schedule's treatment of the first election held under that
    constitution has not been read - see docs/questions.md.
    """
    month = month_of(election_date)
    return (year + 1, 1) if month == 11 else (year, month)


# "Replaced by H. Dwight Smith in Dec." / "Samuel Titus appointed in Dec."
SUCCESSION = re.compile(
    r"(?:replaced by|appointed|successfully contested by)\s+(?:by\s+)?([A-Z][A-Za-z.'\u2019\- ]+?)\s+in\s+"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
    r"(?:\s+((?:18|19)\d\d))?", re.I)
APPOINTED_AFTER_VACANCY = re.compile(
    r"([A-Z][A-Za-z.'\u2019\- ]+?)\s+appointed\s+in\s+"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
    r"(?:\s+((?:18|19)\d\d))?", re.I)


def succession(entry, start_year, start_month):
    """Every handover described in an entry's prose, in order.

    Yields (name, year, month, seated_by) for each person who takes the seat.
    Where a month is given without a year - "in Dec." - the year is carried
    from the previous handover, rolling forward when the month goes backwards.

    How they took it is the verb O'Leary uses: "appointed" is an appointment,
    "successfully contested" is the election, awarded on the contest, and
    "replaced by" says nothing about the mechanism, so nothing is recorded.
    """
    matches = list(SUCCESSION.finditer(entry)) or list(APPOINTED_AFTER_VACANCY.finditer(entry))
    year, month = start_year, start_month or 1
    for m in matches:
        name = m.group(1).strip()
        new_month = MONTHS[m.group(2).title()]
        new_year = int(m.group(3)) if m.group(3) else (year + 1 if new_month < month else year)
        verb = m.group(0).lower()
        how = (APPOINTMENT if "appointed" in verb
               else ELECTION if "contested" in verb else UNRECORDED)
        yield name, new_year, new_month, how
        year, month = new_year, new_month


def oleary_terms():
    """Who held each magisterial district, from the election listings."""
    d = pd.read_csv(BY_CLAUDE / "arlington_county" / "board_1870-1920.csv")
    listed = sorted(d.year.unique())
    for i, year in enumerate(listed):
        nxt = listed[i + 1] if i + 1 < len(listed) else None
        block = d[d.year == year]
        for _, r in block.iterrows():
            entry = str(r.entry)

            # From 1903 the listings give every candidate with a vote count.
            # The highest is taken as the winner; the rest did not serve.
            # Prose about a replacement is never a list of candidates, so the
            # two formats are told apart before either is parsed.
            prose = "(" in entry or re.search(r"replac|vacant|appointed|contested", entry, re.I)
            paired = [] if prose else CANDIDATE_VOTES.findall(entry)
            if paired:
                name = max(paired, key=lambda p: int(p[1].replace(",", "")))[0].strip()
            else:
                name = re.split(r"\s*[(–]|\s+elected\b", entry, maxsplit=1)[0].strip(" -,")

            start_year, start_month = seated(int(year), r.election_date)

            # What a win entitled someone to, not how long the listings are
            # silent. Under the 1902 constitution the term is four years
            # (sec. 112), so a November win ends four years on whether or not
            # O'Leary lists the election that followed - he lists the board
            # in 1907 and 1915 and not in 1911, and running the 1907 term to
            # 1915 would put three named men in a seat for eight years on a
            # source that speaks to four. Where the next listed election comes
            # first, it wins: that is a seat changing hands early.
            nxt_seated = (seated(int(nxt), d[d.year == nxt].election_date.iloc[0])
                          if nxt is not None else None)
            november = month_of(r.election_date) == 11
            statutory_end = end_unrecorded = False
            if november:
                ends = [(start_year + TERM_YEARS, start_month)]
                if nxt_seated:
                    ends.append(nxt_seated)
                term_end_year, term_end_month = min(ends)
                # Only where the statute is doing the work. Where the next
                # listed election seats a successor on the same date, the
                # departure is sourced and needs no note.
                statutory_end = nxt_seated is None or ends[0] < nxt_seated
            elif nxt_seated:
                term_end_year, term_end_month = nxt_seated
            else:
                term_end_year, term_end_month = "", ""
                end_unrecorded = True

            # Each handover ends the sitting member's term and begins the
            # successor's. A vacancy produces no row - nobody served - but the
            # person appointed into it does.
            handovers = list(succession(entry, start_year, start_month))
            vacant = name.lower().startswith("vacant") or not name

            holders = [] if vacant else [(name, start_year, start_month, ELECTION)]
            holders += handovers

            for i, (who, y0, m0, how) in enumerate(holders):
                if i + 1 < len(holders):
                    y1, m1 = holders[i + 1][1], holders[i + 1][2]
                else:
                    y1, m1 = term_end_year, term_end_month
                # A note explains an irregularity. Nothing else belongs here:
                # not chairmanships, not vote counts, not the fact that someone
                # was re-elected. Most rows have none.
                parts = []
                if i > 0:
                    parts.append("Appointed after the seat fell vacant." if vacant
                                 else "Took the seat after successfully contesting the election."
                                 if "contested" in entry else "Took the seat mid-term.")
                elif "contested" in entry:
                    parts.append("Election successfully contested; the seat passed to "
                                 f"{holders[1][0]}.")
                if end_unrecorded and i == len(holders) - 1:
                    parts.append("End of service not recorded; O'Leary's "
                                 "listings stop at 1915.")
                elif statutory_end and i == len(holders) - 1:
                    parts.append("Term ends by statute (Va. Const. 1902 "
                                 "sec. 112); no source records the departure.")
                base = " ".join(parts)
                yield {"name": who, "district": r.district,
                       "start_year": y0, "start_month": m0,
                       "end_year": y1, "end_month": m1, "seated_by": how,
                       "source": f"{citekeys.OLEARY} p.{r.page}", "note": base}


def board_elections():
    """Regular County Board elections from 1931: year -> surnames who stood.

    Only November general elections: a primary does not start a term, and a
    special election fills one already under way.
    """
    c = elections.county_history()
    c = c[c.november & ~c.primary]
    return {int(y): set(g.surname) for y, g in c.groupby("year")}


def special_candidates():
    """November County Board elections from 1931: year -> surnames the
    county lists in a special contest held that day.

    The county marks a same-day special inconsistently - "County Board
    Special Election" in the office column in 1952, "unexp term David
    Krupsaw" after the candidate's name in 1960 - and the day's own label,
    "General and Special Election", is printed whether or not the Board had
    one. So a row is a special where either its office or its candidate says
    so. Who won is not read here: a person whose service Novack shows
    continuing past that November, and who stood in the special, won it.
    """
    c = elections.county_history()
    c = c[c.november & (c.office.str.contains("special|unexp", case=False)
                        | c.candidate.str.contains("unexp", case=False))]
    return {int(y): set(g.surname) for y, g in c.groupby("year")}


def general_winners():
    """Regular County Board elections: year -> surnames who won.

    Unlike board_elections(), this counts only winners, and only regular
    elections - never a special. It answers a different question: not "did
    this person contest a County Board race that year" (which a Novack span
    already settles, since he says they were serving throughout) but "did
    this person's service *begin* with a win here," which a losing run or a
    special election cannot answer yes to.
    """
    out = {}
    for c in contests():
        if c["special"]:
            continue
        out.setdefault(c["year"], set()).update(surname(w) for w in c["winners"])
    return out


DATED = re.compile(r"(?:on|in|from)\s+(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
                   r"\s*(?:\d{1,2},?)?\s*)?((?:19|20)\d\d)", re.I)
UNTIL = re.compile(r"until\b.*?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
                   r"\s*(?:\d{1,2},?)?\s*((?:19|20)\d\d)", re.I)


def novack_events(notes):
    """Arrivals and departures in Novack's parentheticals, with their dates.

    Novack's term strings give years - "1932-1933" - and the month sits in
    the note: "(Resigned on May 31, 1933)". Each irregular clause becomes an
    event: ("arrive" | "depart", year, month, text), with year and month None
    where the clause is undated. Chairmanships are not events. An appointment
    "until filled by election on Nov. 10, 1952" is both an arrival and a
    departure.
    """
    raw = str(notes) if pd.notna(notes) else ""
    clauses = [c.strip(" ();.") for c in re.split(r"[;)]\s*", raw) if c.strip(" ();.")]
    for c in clauses:
        if re.search(r"\b(chairman|chairwoman|chair)\b", c, re.I):
            continue
        if re.search(r"appointed|elected", c, re.I):
            kind = "arrive"
        elif re.search(r"resign|died|removed", c, re.I):
            kind = "depart"
        else:
            continue
        text = re.sub(r"\s+\d{1,3}$", "", c).rstrip(" ,;.")   # footnote markers
        text = text[0].upper() + text[1:] + "."
        dated = DATED.search(c)
        yield (kind, int(dated.group(2)) if dated else None,
               MONTHS[dated.group(1).title()] if dated and dated.group(1) else None, text)
        until = UNTIL.search(c) if kind == "arrive" else None
        if until:
            yield "depart", int(until.group(2)), MONTHS[until.group(1).title()], ""


def novack_terms():
    """Terms of service under the County Manager plan, elected at large.

    Novack lists a person once, alphabetically, with their whole service
    compressed into a single string - "1932-1947" for Elizabeth Magruder, who
    stood and won repeatedly across those years. He records no elections, so
    the span is split here at each election she contested, using the county's
    candidate history. Members elected in November take office the following
    January, so a win in year Y begins a term in Y+1 - unless the win was to
    fill an unexpired term, in which case it began at once and is not a cut.

    Months come from the notes (novack_events): an arrival dated in the
    span's first year sets its first month, a departure dated in its last
    year sets its last month. Undated ones belong to the first or last span.
    The arrival note goes on the span's first term, the departure note on
    its last.

    A member appointed to a vacancy who then wins the seat at a same-day
    special election - Wilt, appointed in January 1960, elected to
    Krupsaw's unexpired term that November - is seated by it in November,
    as election_terms() seats a special election's winner, and the
    appointment ends then. Novack does not record the special; the county's
    candidate history does, and the term's source says so.
    """
    rows = list(_novack_spans())
    # Novack dates most departures, not all: Magruder "1932-1947" has no
    # note saying when in 1947 she left, while Cuppett is "Appointed on May
    # 17, 1947". Where a year has an appointment that no dated departure
    # accounts for, and exactly one member's span ends that year undated,
    # that member left in the month of the appointment (the month itself
    # goes to the incoming member, as always). More than one candidate is
    # ambiguous and stops the build.
    for year in sorted({r["end_year"] for r in rows if not r["_end_dated"]}):
        appointed = sorted(r["start_month"] for r in rows
                           if r["start_year"] == year and r["_appointed"])
        departed = sorted(r["end_month"] for r in rows
                          if r["end_year"] == year and r["_end_dated"])
        for m in departed:                       # each dated departure accounts for one appointment
            later = [a for a in appointed if a >= m]
            if later:
                appointed.remove(later[0])
        # A member appointed that same year sits until the seat is filled at
        # the election, so their span ending at year-end is not a gap.
        undated = [r for r in rows if r["end_year"] == year and not r["_end_dated"]
                   and not r["_open"] and r["start_year"] < year]
        if appointed and len(undated) == 1:
            undated[0]["end_month"] = appointed[0]
            undated[0]["note"] = (undated[0]["note"] + " " if undated[0]["note"] else "") + \
                f"Left during {year}; the month is that of the appointment that filled the seat."
        elif appointed:
            raise ValueError(f"{year}: {len(appointed)} appointment(s) with no dated departure, "
                             f"and {len(undated)} members ending the year undated: "
                             f"{[r['name'] for r in undated]}")
    for r in rows:
        yield {k: v for k, v in r.items() if not k.startswith("_")}


def _novack_spans():
    stood = board_elections()
    winners = general_winners()
    specials = special_candidates()
    d = pd.read_csv(BY_CLAUDE / "arlington_historical_magazine"
                    / "novack_terms_1930-1994.csv")
    for _, r in d.iterrows():
        name = str(r["name"]).strip()
        last = surname(name)
        events = list(novack_events(r.notes))
        parts = [p for p in str(r.term).split(";") if YEAR_RE.search(p)]
        for k, part in enumerate(parts):
            years = [int(y) for y in YEAR_RE.findall(part)]
            start, end = years[0], (years[-1] if len(years) > 1 else years[0])
            # A trailing dash means still serving when Novack published.
            open_ended = part.strip().endswith("-")
            # "1981-Feb. 1990": the month is on the end's side of the dash.
            before, _, after = part.partition("-")
            month_before = MONTH_RE.findall(before)
            month_after = MONTH_RE.findall(after)
            span_end = NOVACK_PUBLISHED if open_ended else end

            arrive = [e for e in events if e[0] == "arrive"
                      and (e[1] == start or (e[1] is None and k == 0))]
            # Novack sometimes dates a span from the election rather than
            # from taking office: Fisher "1963-1974" won in November 1963
            # and sat from January 1964. Where the span's first year is a
            # year this person won the regular election, and no note dates
            # an arrival in it, the term begins the following January.
            # Someone who stood the year before took office in January of
            # this year and is simply being re-elected, so the shift applies
            # only when they did not.
            if (not arrive and last in winners.get(start, set())
                    and last not in stood.get(start - 1, set())):
                start += 1
            depart = [e for e in events if e[0] == "depart" and not open_ended
                      and (e[1] == end or (e[1] is None and k == len(parts) - 1))]
            first_month = (arrive[0][2] if arrive and arrive[0][2] else
                           MONTHS[month_before[0].title()] if month_before else 1)
            last_month = (depart[0][2] if depart and depart[0][2] else
                          MONTHS[month_after[-1].title()] if month_after else 12)
            arrive_note = " ".join(e[3] for e in arrive if e[3])
            depart_note = " ".join(e[3] for e in depart if e[3])

            # Each election this person contested inside the span starts a new
            # term the following January - except the one that brought them
            # in, when they were elected mid-term to an unexpired seat.
            elected_in = arrive and re.search(r"elected", arrive[0][3] or "", re.I) and arrive[0][1] == start
            cuts = sorted(y + 1 for y, who in stood.items()
                          if last in who and start < y + 1 <= span_end
                          and not (elected_in and y == start))
            bounds = [start] + cuts + [span_end + 1]

            # How the span began is in its note, or it began at a regular
            # election. Each later segment begins at an election the person
            # stood in: the regular election if they won it, a special if
            # they stood in one that day and are still serving, and one they
            # lost continues the segment before it, however that began.
            began = (APPOINTMENT if arrive and re.search(r"appointed", arrive[0][3] or "", re.I)
                     else SPECIAL_ELECTION if arrive else ELECTION)
            segments = []
            for i in range(len(bounds) - 1):
                first, final = bounds[i], bounds[i + 1] - 1
                is_last = final == span_end
                won_special = False
                if i > 0 and last in winners.get(first - 1, set()):
                    began = ELECTION
                elif i > 0 and last in specials.get(first - 1, set()):
                    began, won_special = SPECIAL_ELECTION, True
                open_end_year = None
                if open_ended and is_last:
                    # Novack's trailing "-" means still serving in 1994, with
                    # no end date of his own. A segment that began the January
                    # after an election this person won is on the seat's
                    # four-year clock and runs to first+3; one that began by
                    # appointment or special election runs to the next regular
                    # election this person stood in. election_terms() shortens
                    # either if a special election followed.
                    if last in winners.get(first - 1, set()):
                        open_end_year = first + 3
                    else:
                        later = [y for y, who in stood.items() if last in who and y >= first]
                        if not later:
                            raise ValueError(f"{name} was serving when Novack published and "
                                             "never stood again; the term's end cannot be inferred")
                        open_end_year = min(later)
                if final < first:
                    continue
                if won_special:
                    # Seated in the month of the special election, and the
                    # segment before it - the appointment - ends there.
                    segments[-1]["end_year"], segments[-1]["end_month"] = first - 1, 11
                segments.append({
                    "name": name, "district": "at large",
                    "start_year": first - 1 if won_special else first,
                    "start_month": 11 if won_special else first_month if i == 0 else 1,
                    "end_year": open_end_year if (open_ended and is_last) else final,
                    "end_month": 12 if (open_ended and is_last) else (last_month if is_last else 12),
                    "seated_by": began,
                    "source": f"{citekeys.NOVACK} p.{r.page}"
                              + (f"; term boundaries from {citekeys.ARLINGTON_ELECTIONS}"
                                 if cuts or (open_ended and is_last) else ""),
                    "note": " ".join(filter(None, [
                        arrive_note if i == 0 else "",
                        f"Elected in a special election in Nov {first - 1} to fill an "
                        "unexpired term; the appointment ended then." if won_special else "",
                        depart_note if is_last else ""])),
                    # private, for the departure-dating pass above
                    "_end_dated": bool(is_last and ((depart and depart[0][2]) or month_after)) or not is_last,
                    # An appointment that names whose seat it filled ("to fill
                    # the unexpired term of Joseph L. Fisher") is accounted
                    # for already; only an unexplained one dates a departure.
                    "_appointed": bool(i == 0 and arrive
                                       and re.search(r"appointed", arrive[0][3] or "", re.I)
                                       and not re.search(r"term of", arrive[0][3] or "", re.I)),
                    "_open": bool(open_ended and is_last),
                })
            yield from segments


TWO_SEATS = re.compile(r"two seats|2 seats|vote for 2|two elected", re.I)
SPECIAL = re.compile(r"special|unexpired", re.I)
# "(to fill Eisenberg's unexpired term)", "(... following death of Charles Monroe)"
FILLS = re.compile(r"to fill ([A-Za-z]+)['\u2019]s unexpired term|death of ([A-Za-z. ]+?)\)", re.I)
PARTY = re.compile(r"\s*\((?:[^)]+)\)\s*$")


def county_contests():
    """Each County Board general election from 1993 to 2021: who won, how many seats.

    The county's candidate history lists primaries and generals under the
    same office; its own label for the election ("Democratic Primary",
    "General Election", "Special Election") tells them apart.
    A parenthetical on the office - "(Two Seats)", "(to fill Zimmerman's
    unexpired term)" - qualifies the contest, so rows are grouped on the
    office with it stripped, and the qualifiers of every row in the group
    (write-ins included, since the annotation can sit on any row) are read
    together.
    """
    c = elections.county_history()
    c["base"] = c.office.str.replace(r"\s*\(.*", "", regex=True).str.strip()
    key = ["year", "election_date", "base"]
    qualifiers = c.groupby(key).office.agg(" ".join)
    general = c[~c.primary & c.person]
    for k, g in general.groupby(key):
        year, date, base = k
        text = qualifiers[k]
        seats = 2 if TWO_SEATS.search(text) else 1
        won = g.nlargest(seats, "votes")
        fills = FILLS.search(text)
        yield {"year": year, "month": MONTHS[date[:3]],
               "special": bool(SPECIAL.search(text)) or not date.startswith("November"),
               "page": int(g.page.iloc[0]),
               "fills": surname(fills.group(1) or fills.group(2)) if fills else None,
               "winners": [PARTY.sub("", n).strip() for n in won.candidate],
               "stood": [PARTY.sub("", n).strip() for n in g.candidate]}


def state_contests():
    """Each County Board general election from 2022, from the state database.

    The file is the Department of Elections' own CSV, one row per candidate
    per precinct per vote channel, so a candidate's votes are summed. Its
    `election_type` column says what kind of election it was, and
    `number_seats` how many were filled. Names are taken as the state spells
    them, which differs from the county's ("Matthew David De Ferranti" for
    "Matthew D. \"Matt\" de Ferranti"), so a person is matched by surname.
    """
    c = elections.state_results()
    general = c[c.person & c.election_type.str.startswith("General")]
    for (date, contest), g in general.groupby(["date", "contest_id"]):
        by_name = g.groupby("candidate_name").votes.sum().sort_values(ascending=False)
        seats = int(g.number_seats.iloc[0])
        yield {"year": date.year, "month": date.month,
               "special": date.month != 11,
               "page": None, "contest": int(contest), "fills": None,
               "winners": list(by_name.index[:seats]),
               "stood": list(by_name.index)}


def contests():
    """Every County Board general election from 1993, from both sources.

    The county's candidate history runs to 2021 and the state database is
    used from 2022. Both hold 2021, and the build insists they name the same
    winner there before trusting the second source for what follows.
    """
    county = list(county_contests())
    state = list(state_contests())
    overlap = [(c["year"], sorted(map(surname, c["winners"]))) for c in county + state
               if c["year"] == COUNTY_HISTORY_THROUGH and not c["special"]]
    if len(overlap) != 2 or overlap[0][1] != overlap[1][1]:
        raise ValueError(f"county and state sources disagree on {COUNTY_HISTORY_THROUGH}: {overlap}")
    return county + [c for c in state if c["year"] > COUNTY_HISTORY_THROUGH]


def cite(c):
    if c["page"] is not None:
        return f"{citekeys.ARLINGTON_ELECTIONS} p.{c['page']}"
    return f"{citekeys.VA_ELECTIONS} contest {c['contest']}"


def election_terms(earlier: pd.DataFrame):
    """Terms from 1995 on, built from election results.

    Novack ends in 1994; from there each regular November win in year Y is a
    four-year term from January Y+1. A special election fills the rest of a
    term that ended early: the winner serves until the seat's next regular
    election, which is the next November contest they stand in, and the
    member whose term covered that date and ended then is closed at the
    special election. If that member cannot be identified uniquely the build
    stops rather than guess.

    A person is named as Novack spells them where the surname matches one of
    his; otherwise as the county spells them the first time they win.
    """
    rows = list(contests())
    known = {surname(n): n for n in earlier.name}
    def canonical(n):
        return known.setdefault(surname(n), n)

    terms = []
    for c in rows:
        if c["special"] or c["year"] < 1994:
            continue
        for w in c["winners"]:
            terms.append({"name": canonical(w), "district": "at large",
                          "start_year": c["year"] + 1, "start_month": 1,
                          "end_year": c["year"] + 4, "end_month": 12,
                          "seated_by": ELECTION, "source": cite(c), "note": ""})
    d = pd.concat([earlier, pd.DataFrame(terms)], ignore_index=True)

    for c in sorted((c for c in rows if c["special"] and c["year"] >= 1995),
                    key=lambda c: (c["year"], c["month"])):
        for w in c["winners"]:
            w = canonical(w)
            nxt = [r["year"] for r in rows if not r["special"] and r["year"] >= c["year"]
                   and any(canonical(s) == w for s in r["stood"])]
            if not nxt:
                raise ValueError(f"{w} won a special election in {c['year']} and never "
                                 "stood again; the seat's cycle cannot be inferred")
            end = min(nxt)
            when = f"{MONTH_NAMES[c['month']]} {c['year']}"
            covers = ((d.start_year * 12 + d.start_month <= c["year"] * 12 + c["month"])
                      & (d.end_year == end) & (d.end_month == 12) & (d.name != w))
            if c["fills"]:
                covers &= d.name.map(surname) == c["fills"]
            if covers.sum() != 1:
                raise ValueError(f"special election {when}: {covers.sum()} members "
                                 f"hold a term ending {end}, expected 1:\n"
                                 f"{d[covers][['name', 'start_year', 'end_year']]}")
            i = d.index[covers][0]
            d.loc[i, ["end_year", "end_month"]] = [c["year"], c["month"]]
            d.loc[i, "note"] = (d.loc[i, "note"] + " " if d.loc[i, "note"] else "") + \
                f"Left the seat before the end of the term; filled by special election in {when}."
            d.loc[len(d)] = {"name": w, "district": "at large",
                             "start_year": c["year"], "start_month": c["month"],
                             "end_year": end, "end_month": 12,
                             "seated_by": SPECIAL_ELECTION, "source": cite(c),
                             "note": f"Elected in a special election in {when} to fill an unexpired term."}
    return d


def check_five_seats(d: pd.DataFrame, first=1995, last=PRESENT):
    """Five members at large in every month, apart from a handover month.

    A member who leaves mid-term and the one elected to replace them share
    that month, so it shows six; any other count means a term is wrong.
    """
    at_large = d[d.district == "at large"]
    start = at_large.start_year * 12 + at_large.start_month
    end = pd.to_numeric(at_large.end_year) * 12 + pd.to_numeric(at_large.end_month)
    handover = set(start[at_large.seated_by == SPECIAL_ELECTION])
    for m in range(first * 12 + 1, last * 12 + 13):
        n = ((start <= m) & (end >= m)).sum()
        expected = 6 if m in handover else 5
        if n != expected:
            raise ValueError(f"{(m - 1) // 12}-{(m - 1) % 12 + 1:02d}: {n} members "
                             f"at large, expected {expected}")


NOT_A_NAME = re.compile(r"\b(?:elected|contested|replaced|appointed|vacant|resigned|died)\b|\d", re.I)


def check_names(d: pd.DataFrame):
    """A name is a name. Prose that reached this column was not parsed."""
    bad = d[d.name.str.contains(NOT_A_NAME, regex=True)]
    if len(bad):
        raise ValueError("these names read as prose, not people:\n"
                         + "\n".join(f"  {n!r}" for n in bad.name))


def check_seated_by(d: pd.DataFrame):
    """Every term says how it began, in one of the four words.

    A consumer selects terms by this column - the ones an election seated,
    the ones a special election handed over - so a value outside the set
    would not stop anything; the term would just match no selection and
    drop out of a count. From 1932 every source says how, so an unrecorded
    term there is a reading that needs a person.
    """
    bad = d[~d.seated_by.isin(SEATED_BY)]
    if len(bad):
        raise ValueError("seated_by must be one of "
                         f"{', '.join(SEATED_BY)}; these are not:\n"
                         + "\n".join(f"  {r['name']} {r.start_year}: {r.seated_by!r}"
                                     for _, r in bad.iterrows()))
    unrecorded = d[(d.start_year >= 1932) & (d.seated_by == UNRECORDED)]
    if len(unrecorded):
        raise ValueError("seated_by is unrecorded for terms after 1931, where every "
                         "source says how a term began:\n"
                         + "\n".join(f"  {r['name']} {r.start_year}"
                                     for _, r in unrecorded.iterrows()))


def build() -> pd.DataFrame:
    d = pd.DataFrame(list(oleary_terms()) + list(novack_terms()))
    d = election_terms(d)
    check_names(d)
    check_seated_by(d)
    check_five_seats(d)
    d = d.sort_values(["name", "start_year", "start_month"]).reset_index(drop=True)

    # A counter within each person: their first term is 1, the term beginning
    # after the next election is 2, and so on. Someone appointed to a vacancy
    # who then wins twice has three rows numbered 1, 2, 3.
    # Keyed on the full name: two members can share a surname, and did.
    d["term_number"] = d.groupby(d.name.str.strip()).cumcount() + 1

    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "seated_by", "source", "note"]
    return d[cols].sort_values(["start_year", "start_month", "district", "name"]).reset_index(drop=True)


