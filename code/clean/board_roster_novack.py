"""Terms of service 1932-1994 under the County Manager plan, elected at
large, from Novack's roster. A module, not a step: board_roster.py
assembles it with the rest.

Novack lists a person once, with their whole service as one string,
"1932-1947", and records no elections, so the span is split at each
election they contested, from the county's candidate history
(board_roster_results.py). Months come from the notes. A member appointed
to a vacancy who then wins a same-day special election is seated by it in
November.
"""
import re

import pandas as pd

import board_roster_results as results
import citekeys
from board_terms import (APPOINTMENT, ELECTION, MONTH, MONTH_RE, SPECIAL_ELECTION, YEAR_RE,
                         listing)
from elections import MONTHS, surname

PUBLISHED = 1994

DATED = re.compile(rf"(?:on|in|from)\s+(?:{MONTH}\s*(?:\d{{1,2}},?)?\s*)?((?:19|20)\d\d)", re.I)
UNTIL = re.compile(rf"until\b.*?{MONTH}\s*(?:\d{{1,2}},?)?\s*((?:19|20)\d\d)", re.I)


def events(notes):
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


def terms():
    """One row per person per term, the spans cut at elections and undated
    departures dated where an appointment fixes them."""
    rows = list(_spans())
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


def _spans():
    """Every span of every member's term string as segments, before the
    departure-dating pass in terms(): read its dates, find the elections
    that cut it, build one segment per cut."""
    stood = results.board_elections()
    winners = results.general_winners()
    specials = results.special_candidates()
    d = listing("novack")
    for _, r in d.iterrows():
        # Novack prints Jr and Sr without the period; the rest of the
        # project's names have it.
        name = re.sub(r"\b(Jr|Sr)$", r"\1.", str(r["name"]).strip())
        last = surname(name)
        found = list(events(r.notes))
        parts = [p for p in str(r.term).split(";") if YEAR_RE.search(p)]
        for k, part in enumerate(parts):
            span = _span_dates(part, k, len(parts), found, last, stood, winners)
            bounds = _span_bounds(span, last, stood)
            yield from _span_segments(name, int(r.page), span, bounds, last, stood, winners, specials)


def _span_dates(part, k, n_parts, found, last, stood, winners) -> dict:
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

    arrive = [e for e in found if e[0] == "arrive"
              and (e[1] == start or (e[1] is None and k == 0))]
    if (not arrive and last in winners.get(start, set())
            and last not in stood.get(start - 1, set())):
        start += 1
    depart = [e for e in found if e[0] == "depart" and not open_ended
              and (e[1] == end or (e[1] is None and k == n_parts - 1))]
    return {
        "start": start, "end": end, "open_ended": open_ended,
        "span_end": PUBLISHED if open_ended else end,
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
    The three private keys feed the departure-dating in terms().
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
