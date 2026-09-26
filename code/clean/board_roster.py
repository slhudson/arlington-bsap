"""Who held each seat and when, 1870 through 2026, one row per person per term.

A module, not a step: board_members.py takes these terms and attaches race,
gender and party.

    name  district  start_year  start_month  end_year  end_month  seated_by  source  note

`district` is a magisterial district through 1931 and "at large" from 1932.
`seated_by` is how the term began: a regular election, a special election,
an appointment, or unrecorded. Months are given where a source gives them;
a November winner is seated the following January. A vacant seat is not a
row. The reasoning is in docs/board.md.

Sources, in sequence:

  oleary2010       1870-1915  who held each magisterial district, by election
  novack1994       1932-1994  terms of service, with mid-term departures
  election results 1995-      the county's candidate history to 2021, the
                              state's database from 2022

1912-1931 names almost nobody: O'Leary's last listed election is 1915, and
its winners' four-year terms end in January 1912. The county's candidate
history prints the district races of November 1923 and 1927, keyed in
board_terms.csv.
"""
import re

import pandas as pd

import citekeys
import elections
import paths
from elections import COUNTY_HISTORY_THROUGH, MONTHS, surname

NOVACK_PUBLISHED = 1994
PRESENT = 2026            # checked month by month up to here; board_seats stops here

# The seats that exist: three district supervisors from 1870, five members
# at large from January 1932 (anderson1958). Imported by residents.py and
# board_seats.py.
SEATS_DISTRICT = 3.0
SEATS_AT_LARGE = 5.0
AT_LARGE_FROM = 1932

# The values seated_by takes.
ELECTION = "election"
SPECIAL_ELECTION = "special election"
APPOINTMENT = "appointment"
UNRECORDED = "unrecorded"
SEATED_BY = (ELECTION, SPECIAL_ELECTION, APPOINTMENT, UNRECORDED)

# Va. Const. 1902 sec. 112, applied from the November 1903 election.
TERM_YEARS = 4

MONTH_NAMES = {v: k for k, v in MONTHS.items()}


MONTH = rf"({'|'.join(MONTHS)})[a-z]*\.?"          # "Dec", "December", "Dec."
NAME = r"([A-Z][A-Za-z.'’\- ]+?)"
MONTH_RE = re.compile(r"\b" + MONTH, re.I)
YEAR_RE = re.compile(r"\b((?:18|19|20)\d\d)\b")
# "Corbett 213 Hagen 189" - a name followed by its vote count, repeated
CANDIDATE_VOTES = re.compile(r"([A-Z][A-Za-z.'’\- ]*?)\s+([\d,]+)(?=\s|$)")


def listing(kind) -> pd.DataFrame:
    """The rows of one term listing, from data/built/board_claims.csv, every
    cell as keyed in and a blank a blank."""
    c = paths.built("board_claims")
    return c[c.claim == kind].reset_index(drop=True)


def month_of(text):
    m = MONTH_RE.search(text or "")
    return MONTHS[m.group(1).title()] if m else ""


def seated(year, election_date):
    """When an election's winners take office: (year, month). A May election
    seats in May; a November election seats on 1 January following (Va.
    Const. 1902; schedule-1902 in docs/questions.csv)."""
    month = month_of(election_date)
    return (year + 1, 1) if month == 11 else (year, month)


# "Replaced by H. Dwight Smith in Dec." / "Samuel Titus appointed in Dec."
SUCCESSION = re.compile(
    rf"(?:replaced by|appointed|successfully contested by)\s+(?:by\s+)?{NAME}\s+in\s+{MONTH}"
    r"(?:\s+((?:18|19)\d\d))?", re.I)
APPOINTED_AFTER_VACANCY = re.compile(
    rf"{NAME}\s+appointed\s+in\s+{MONTH}(?:\s+((?:18|19)\d\d))?", re.I)


def succession(entry, start_year, start_month):
    """Every handover in an entry's prose, in order: (name, year, month, seated_by).

    A month without a year carries the previous handover's year, rolling
    forward when the month goes backwards. "Appointed" is an appointment,
    "successfully contested" is the election, "replaced by" is unrecorded.
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
    """Who held each magisterial district, from the election listings.

    From 1903 an entry lists every candidate with a vote count and the
    highest wins; earlier it names the holder, with replacements in prose.
    A November win is a four-year term, or shorter where the next listed
    election seats a successor first. Each handover in the prose ends the
    sitting member's term and begins the successor's.
    """
    d = elections.oleary(elections.SUPERVISORS)
    listed = sorted(d.year.unique())
    for year, nxt in zip(listed, listed[1:] + [None]):
        nxt_seated = (seated(int(nxt), d[d.year == nxt].election_date.iloc[0])
                      if nxt is not None else None)
        for _, r in d[d.year == year].iterrows():
            entry = str(r.entry)
            prose = "(" in entry or re.search(r"replac|vacant|appointed|contested", entry, re.I)
            paired = [] if prose else CANDIDATE_VOTES.findall(entry)
            if paired:
                name = max(paired, key=lambda p: int(p[1].replace(",", "")))[0].strip()
            else:
                name = re.split(r"\s*[(–]|\s+elected\b", entry, maxsplit=1)[0].strip(" -,")

            start_year, start_month = seated(int(year), r.election_date)
            statutory = ((start_year + TERM_YEARS, start_month)
                         if month_of(r.election_date) == 11 else None)
            ends = [e for e in (statutory, nxt_seated) if e]
            term_end = min(ends) if ends else ("", "")
            statutory_end = statutory is not None and (nxt_seated is None or statutory < nxt_seated)
            end_unrecorded = not ends

            vacant = name.lower().startswith("vacant") or not name
            holders = ([] if vacant else [(name, start_year, start_month, ELECTION)]) \
                + list(succession(entry, start_year, start_month))
            for i, (who, y0, m0, how) in enumerate(holders):
                y1, m1 = holders[i + 1][1:3] if i + 1 < len(holders) else term_end
                last = i == len(holders) - 1
                parts = []
                if i > 0:
                    parts.append("Appointed after the seat fell vacant." if vacant
                                 else "Took the seat after successfully contesting the election."
                                 if "contested" in entry else "Took the seat mid-term.")
                elif "contested" in entry:
                    parts.append("Election successfully contested; the seat passed to "
                                 f"{holders[1][0]}.")
                if last and end_unrecorded:
                    parts.append("End of service not recorded; O'Leary's "
                                 "listings stop at 1915.")
                elif last and statutory_end:
                    parts.append("Term ends by statute (Va. Const. 1902 "
                                 "sec. 112); no source records the departure.")
                yield {"name": who, "district": r.district,
                       "start_year": y0, "start_month": m0,
                       "end_year": y1, "end_month": m1, "seated_by": how,
                       "source": f"{citekeys.OLEARY} p.{r.page}", "note": " ".join(parts)}


def county_history_terms():
    """Terms keyed by hand from the county's candidate history, for the
    two 1912-1931 elections it prints under the district headings
    (board_terms.csv). They add names to the roster; board_seats does not
    read them, and states the 1912-1931 seats itself. docs/board.md."""
    d = listing("terms")
    for _, r in d.iterrows():
        yield {"name": r["name"], "district": r.district,
               "start_year": int(r.start_year), "start_month": int(r.start_month),
               "end_year": int(r.end_year) if r.end_year else float("nan"),
               "end_month": int(r.end_month) if r.end_month else float("nan"),
               "seated_by": r.seated_by, "source": r.source, "note": r.note}


def board_elections():
    """Regular November County Board elections from 1931: year -> surnames who stood."""
    c = elections.county_history()
    c = c[c.november & ~c.primary]
    return {int(y): set(g.surname) for y, g in c.groupby("year")}


def special_candidates():
    """November County Board elections from 1931: year -> surnames in a
    same-day special contest, marked in the office column or after the
    candidate's name. Who won is not read here."""
    c = elections.county_history()
    c = c[c.november & (c.office.str.contains("special|unexp", case=False)
                        | c.candidate.str.contains("unexp", case=False))]
    return {int(y): set(g.surname) for y, g in c.groupby("year")}


def general_winners():
    """Regular County Board elections: year -> surnames who won."""
    out = {}
    for c in outcomes():
        if not c["special"]:
            out.setdefault(c["year"], set()).update(surname(w) for w in c["winners"])
    return out


DATED = re.compile(rf"(?:on|in|from)\s+(?:{MONTH}\s*(?:\d{{1,2}},?)?\s*)?((?:19|20)\d\d)", re.I)
UNTIL = re.compile(rf"until\b.*?{MONTH}\s*(?:\d{{1,2}},?)?\s*((?:19|20)\d\d)", re.I)


def novack_events(notes):
    """Arrivals and departures in Novack's parentheticals: ("arrive" |
    "depart", year, month, text), with year and month None where undated.
    Chairmanships are not events. "Appointed ... until filled by election
    on Nov. 10, 1952" is both an arrival and a departure."""
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

    Novack lists a person once, with their whole service as one string,
    "1932-1947", and records no elections, so the span is split at each
    election they contested, from the county's candidate history. Months
    come from the notes. A member appointed to a vacancy who then wins a
    same-day special election is seated by it in November.
    """
    rows = list(_novack_spans())
    # Where a year has an appointment that no dated departure accounts for,
    # and exactly one member's span ends that year undated, that member
    # left in the month of the appointment. More than one is ambiguous.
    for year in sorted({r["end_year"] for r in rows if not r["_end_dated"]}):
        appointed = sorted(r["start_month"] for r in rows
                           if r["start_year"] == year and r["_appointed"])
        departed = sorted(r["end_month"] for r in rows
                          if r["end_year"] == year and r["_end_dated"])
        for m in departed:
            later = [a for a in appointed if a >= m]
            if later:
                appointed.remove(later[0])
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
    """Every span of every member's term string as segments, before the
    departure-dating pass in novack_terms(): read its dates, find the
    elections that cut it, build one segment per cut."""
    stood = board_elections()
    winners = general_winners()
    specials = special_candidates()
    d = listing("novack")
    for _, r in d.iterrows():
        name = str(r["name"]).strip()
        last = surname(name)
        events = list(novack_events(r.notes))
        parts = [p for p in str(r.term).split(";") if YEAR_RE.search(p)]
        for k, part in enumerate(parts):
            span = _span_dates(part, k, len(parts), events, last, stood, winners)
            bounds = _span_bounds(span, last, stood)
            yield from _span_segments(name, int(r.page), span, bounds, last, stood, winners, specials)


def _span_dates(part, k, n_parts, events, last, stood, winners) -> dict:
    """One span - "1932-1947", "1981-Feb. 1990", "1991-" - read into its years
    and months, with the notes that date them.

    Where the first year is one this person won the regular election and
    they did not stand the year before, the term begins the following
    January. An arrival dated in the first year sets the first month and a
    departure dated in the last sets the last; undated ones belong to the
    first or last span. A trailing dash is still serving when Novack
    published.
    """
    years = [int(y) for y in YEAR_RE.findall(part)]
    start, end = years[0], (years[-1] if len(years) > 1 else years[0])
    open_ended = part.strip().endswith("-")
    before, _, after = part.partition("-")           # "1981-Feb. 1990"
    month_before = MONTH_RE.findall(before)
    month_after = MONTH_RE.findall(after)

    arrive = [e for e in events if e[0] == "arrive"
              and (e[1] == start or (e[1] is None and k == 0))]
    if (not arrive and last in winners.get(start, set())
            and last not in stood.get(start - 1, set())):
        start += 1
    depart = [e for e in events if e[0] == "depart" and not open_ended
              and (e[1] == end or (e[1] is None and k == n_parts - 1))]
    return {
        "start": start, "end": end, "open_ended": open_ended,
        "span_end": NOVACK_PUBLISHED if open_ended else end,
        "first_month": (arrive[0][2] if arrive and arrive[0][2] else
                        MONTHS[month_before[0].title()] if month_before else 1),
        "last_month": (depart[0][2] if depart and depart[0][2] else
                       MONTHS[month_after[-1].title()] if month_after else 12),
        "arrive": arrive, "depart": depart, "month_after": month_after,
        "arrive_note": " ".join(e[3] for e in arrive if e[3]),
        "depart_note": " ".join(e[3] for e in depart if e[3]),
    }


def _span_bounds(span, last, stood) -> list:
    """Where a span is cut into terms: its first year, the January after each
    election the person contested inside it (except the one that brought
    them in mid-term), and the year after its last."""
    arrive, start, span_end = span["arrive"], span["start"], span["span_end"]
    elected_in = arrive and re.search(r"elected", arrive[0][3] or "", re.I) and arrive[0][1] == start
    cuts = sorted(y + 1 for y, who in stood.items()
                  if last in who and start < y + 1 <= span_end
                  and not (elected_in and y == start))
    return [start] + cuts + [span_end + 1]


def _span_segments(name, page, span, bounds, last, stood, winners, specials) -> list:
    """One term per pair of bounds, with how it began and where it ends.

    The first segment began as its note says, or at a regular election. A
    later one began at the regular election if the person won it, a special
    if they stood in one that day, and a lost election continues the segment
    before it. An open-ended last segment runs to first+3 if it began with a
    regular win, else to the next regular election the person stood in.
    The three private keys feed the departure-dating in novack_terms().
    """
    arrive, open_ended, span_end = span["arrive"], span["open_ended"], span["span_end"]
    arrive_note = arrive[0][3] or "" if arrive else ""
    cuts = bounds[1:-1]
    began = (APPOINTMENT if re.search(r"appointed", arrive_note, re.I)
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
            segments[-1]["end_year"], segments[-1]["end_month"] = first - 1, 11
        segments.append({
            "name": name, "district": "at large",
            "start_year": first - 1 if won_special else first,
            "start_month": 11 if won_special else span["first_month"] if i == 0 else 1,
            "end_year": open_end_year if (open_ended and is_last) else final,
            "end_month": 12 if (open_ended and is_last) else (span["last_month"] if is_last else 12),
            "seated_by": began,
            "source": f"{citekeys.NOVACK} p.{page}"
                      + (f"; term boundaries from {citekeys.ARLINGTON_ELECTIONS}"
                         if cuts or (open_ended and is_last) else ""),
            "note": " ".join(filter(None, [
                span["arrive_note"] if i == 0 else "",
                f"Elected in a special election in Nov {first - 1} to fill an "
                "unexpired term; the appointment ended then." if won_special else "",
                span["depart_note"] if is_last else ""])),
            "_end_dated": bool(is_last and ((span["depart"] and span["depart"][0][2])
                                            or span["month_after"])) or not is_last,
            # An appointment that names whose seat it filled is accounted for.
            "_appointed": bool(i == 0 and re.search(r"appointed", arrive_note, re.I)
                               and not re.search(r"term of", arrive_note, re.I)),
            "_open": bool(open_ended and is_last),
        })
    return segments


def outcomes():
    """Every County Board general election from 1931, from both records: who
    won, who stood, how many seats. Both records hold 2021 and must name the same
    winner there."""
    c = elections.contests()
    c = c[c.person & ~c.primary]
    out = []
    for _, g in c.groupby("contest", sort=False):
        first = g.iloc[0]
        won = g.nlargest(int(first.seats), "votes")
        out.append({"record": first.record, "year": int(first.year), "month": int(first.month),
                    "special": bool(first.special), "fills": first.fills,
                    "source": first.source,
                    "winners": list(won.name), "stood": list(g.name)})
    overlap = [(c["record"], sorted(map(surname, c["winners"]))) for c in out
               if c["year"] == COUNTY_HISTORY_THROUGH and not c["special"]]
    if len(overlap) != 2 or overlap[0][1] != overlap[1][1]:
        raise ValueError(f"county and state sources disagree on {COUNTY_HISTORY_THROUGH}: {overlap}")
    return [c for c in out if c["record"] == "county" or c["year"] > COUNTY_HISTORY_THROUGH]


def election_terms(earlier: pd.DataFrame):
    """Terms from 1995 on, from election results.

    A regular November win in year Y is a four-year term from January Y+1. A
    special election's winner serves until the next regular election they
    stand in, and the member whose term covered that date and ended then is
    closed at the special; that member must be unique. A person is named as
    Novack spells them where the surname matches, otherwise as the county
    spells them the first time they win.
    """
    rows = list(outcomes())
    known = {surname(n): n for n in earlier.name}

    def canonical(n):
        return known.setdefault(surname(n), n)

    terms = [{"name": canonical(w), "district": "at large",
              "start_year": c["year"] + 1, "start_month": 1,
              "end_year": c["year"] + 4, "end_month": 12,
              "seated_by": ELECTION, "source": c["source"], "note": ""}
             for c in rows if not c["special"] and c["year"] >= 1994
             for w in c["winners"]]
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
                covers &= d.name.map(surname) == surname(c["fills"])
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
                             "seated_by": SPECIAL_ELECTION, "source": c["source"],
                             "note": f"Elected in a special election in {when} to fill an unexpired term."}
    return d


def check_five_seats(d: pd.DataFrame, first=1995, last=PRESENT):
    """Five members at large in every month; six in a handover month."""
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
    """Every term says how it began, in one of the four words, and none is
    unrecorded from 1932."""
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
    d = pd.DataFrame(list(oleary_terms()) + list(county_history_terms()) + list(novack_terms()))
    d = election_terms(d)
    check_names(d)
    check_seated_by(d)
    check_five_seats(d)
    # A blank end is missing, not a float: the columns stay whole numbers.
    d[["end_year", "end_month"]] = d[["end_year", "end_month"]].astype("Int64")
    d = d.sort_values(["name", "start_year", "start_month"]).reset_index(drop=True)
    # Each person's terms numbered from 1, keyed on the full name.
    d["term_number"] = d.groupby(d.name.str.strip()).cumcount() + 1
    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "seated_by", "source", "note"]
    return d[cols].sort_values(["start_year", "start_month", "district", "name"]).reset_index(drop=True)


def seats(year):
    """The seats that existed in a year."""
    return SEATS_DISTRICT if year < AT_LARGE_FROM else SEATS_AT_LARGE
