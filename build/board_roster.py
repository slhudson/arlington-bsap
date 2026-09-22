"""The roster: one row per person per term served -> data/clean/board_roster.csv

A term, not a person-year: name, district, and when service began and ended.
Person-years fall out of this; the reverse does not, because a term that starts
in May or ends in February cannot be recovered from a list of years.

    name  district  start_year  start_month  end_year  end_month  source  note

`district` is a magisterial district through 1931 and "at large" from 1932,
when the County Manager plan replaced districts with countywide election.

Months are given where a source gives them and left empty otherwise. Under the
magisterial system elections were held in May and the board took office then,
so those terms run May to May. Under the County Manager plan members took
office on 1 January, so those run January to December unless a source says
otherwise.

**A vacant seat is not a row.** Nobody served, so there is no person and no
term. Vacancies are recorded in docs/sources.md instead.

Sources:

  O'Leary (2012)   1870-1915  who held each magisterial district, by election
  Novack (1994)    1930-1994  terms of service, with mid-term departures

Gaps left empty rather than assumed: 1916-1929, and 1995 onward.
"""
import re

import pandas as pd

from files import TRANSCRIBED, write

BY_CLAUDE = TRANSCRIBED / "by_claude"
NOVACK_PUBLISHED = 1994

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}
MONTH_RE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?", re.I)
YEAR_RE = re.compile(r"\b((?:18|19|20)\d\d)\b")
# "Corbett 213 Hagen 189" - a name followed by its vote count, repeated
CANDIDATE_VOTES = re.compile(r"([A-Z][A-Za-z.'’\- ]*?)\s+([\d,]+)(?=\s|$)")


def month_of(text):
    m = MONTH_RE.search(text or "")
    return MONTHS[m.group(1).title()] if m else ""


# "Replaced by H. Dwight Smith in Dec." / "Samuel Titus appointed in Dec."
SUCCESSION = re.compile(
    r"(?:replaced by|appointed)\s+(?:by\s+)?([A-Z][A-Za-z.'\u2019\- ]+?)\s+in\s+"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
    r"(?:\s+((?:18|19)\d\d))?", re.I)
APPOINTED_AFTER_VACANCY = re.compile(
    r"([A-Z][A-Za-z.'\u2019\- ]+?)\s+appointed\s+in\s+"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
    r"(?:\s+((?:18|19)\d\d))?", re.I)


def succession(entry, start_year, start_month):
    """Every handover described in an entry's prose, in order.

    Yields (name, year, month) for each person who takes the seat. Where a
    month is given without a year - "in Dec." - the year is carried from the
    previous handover, rolling forward when the month goes backwards.
    """
    matches = list(SUCCESSION.finditer(entry)) or list(APPOINTED_AFTER_VACANCY.finditer(entry))
    year, month = start_year, start_month or 1
    for m in matches:
        name = m.group(1).strip()
        new_month = MONTHS[m.group(2).title()]
        new_year = int(m.group(3)) if m.group(3) else (year + 1 if new_month < month else year)
        yield name, new_year, new_month
        year, month = new_year, new_month


def oleary_terms():
    """Who held each magisterial district, from the election listings."""
    d = pd.read_csv(BY_CLAUDE / "county" / "board_1870-1920.csv")
    elections = sorted(d.year.unique())
    for i, year in enumerate(elections):
        nxt = elections[i + 1] if i + 1 < len(elections) else None
        block = d[d.year == year]
        for _, r in block.iterrows():
            entry = str(r.entry)

            # From 1903 the listings give every candidate with a vote count.
            # The highest is taken as the winner; the rest did not serve.
            # Prose about a replacement is never a list of candidates, so the
            # two formats are told apart before either is parsed.
            prose = "(" in entry or re.search(r"replac|vacant|appointed", entry, re.I)
            paired = [] if prose else CANDIDATE_VOTES.findall(entry)
            if paired:
                name = max(paired, key=lambda p: int(p[1].replace(",", "")))[0].strip()
                note = f"contested; votes as printed: {entry.strip()}"
            else:
                name = re.split(r"\s*[(–]", entry, maxsplit=1)[0].strip(" -")
                note = entry[len(name):].strip(" -–")

            # Where there is no next listed election, the end of service is
            # not recorded - O'Leary's listings simply stop. That is not the
            # same as still serving, and is marked so.
            term_end_year = int(nxt) if nxt else ""
            term_end_month = (month_of(d[d.year == nxt].election_date.iloc[0])
                              if nxt else "")
            end_unrecorded = nxt is None
            start_month = month_of(r.election_date)

            # Each handover ends the sitting member's term and begins the
            # successor's. A vacancy produces no row - nobody served - but the
            # person appointed into it does.
            handovers = list(succession(entry, int(year), start_month))
            vacant = name.lower().startswith("vacant") or not name

            holders = [] if vacant else [(name, int(year), start_month)]
            holders += handovers

            for i, (who, y0, m0) in enumerate(holders):
                if i + 1 < len(holders):
                    y1, m1 = holders[i + 1][1], holders[i + 1][2]
                else:
                    y1, m1 = term_end_year, term_end_month
                base = note if i == 0 else f"took the seat mid-term; {note}"
                if end_unrecorded and i == len(holders) - 1:
                    base = ("end of service not recorded; O'Leary's listings stop "
                            "at 1915" + (f"; {base}" if base else ""))
                yield {"name": who, "district": r.district,
                       "start_year": y0, "start_month": m0,
                       "end_year": y1, "end_month": m1,
                       "end_status": "not recorded" if end_unrecorded and i == len(holders) - 1 else "recorded",
                       "source": f"O'Leary (2012) p.{r.page}", "note": base}


def surname(name):
    """The surname, ignoring the qualifiers the sources hang off a name.

    Candidate entries carry party, status and outcome - "*Elizabeth B. Magruder
    (holdover)", "Elizabeth B. Magruder (won)" - so anything in parentheses,
    anything after a comma or dash, and honorifics are dropped before the last
    word is taken. Without this, Magruder's surname reads as "won".
    """
    s = re.sub(r"\(.*?\)", " ", str(name))          # (won), (D), (holdover)
    s = re.split(r"[,\u2013-]", s)[0]                 # ", conservative", " - removed for..."
    s = re.sub(r"\b(Jr|Sr|II|III|IV|Dr|Mrs|Mr)\b\.?", "", s)
    s = re.sub(r"[^A-Za-z ]", " ", s).split()
    return s[-1].lower() if s else ""


def board_elections():
    """Years the County Board was on the ballot, and who stood, from 1931."""
    c = pd.read_csv(BY_CLAUDE / "county" / "candidate_history_1920-present.csv")
    c = c[c.office.str.contains("County Board", na=False)].dropna(subset=["year"])
    out = {}
    for _, r in c.iterrows():
        out.setdefault(int(r.year), set()).add(surname(r.candidate))
    return out


def novack_terms():
    """Terms of service under the County Manager plan, elected at large.

    Novack lists a person once, alphabetically, with their whole service
    compressed into a single string - "1932-1947" for Elizabeth Magruder, who
    stood and won repeatedly across those years. He records no elections, so
    the span is split here at each election she contested, using the county's
    candidate history. Members elected in November take office the following
    January, so a win in year Y begins a term in Y+1.

    A span with no election inside it stays a single term.
    """
    elections = board_elections()
    d = pd.read_csv(BY_CLAUDE / "arlington_historical_magazine"
                    / "novack_terms_1930-1994.csv")
    for _, r in d.iterrows():
        for part in str(r.term).split(";"):
            years = [int(y) for y in YEAR_RE.findall(part)]
            if not years:
                continue
            start, end = years[0], (years[-1] if len(years) > 1 else years[0])
            # A trailing dash means still serving when Novack published.
            open_ended = part.strip().endswith("-")
            months = MONTH_RE.findall(part)
            name = str(r["name"]).strip()
            last = surname(name)
            span_end = NOVACK_PUBLISHED if open_ended else end

            # Each election this person contested inside the span starts a new
            # term the following January.
            cuts = sorted(y + 1 for y, who in elections.items()
                          if last in who and start < y + 1 <= span_end)
            bounds = [start] + cuts + [span_end + 1]

            first_month = MONTHS[months[0].title()] if months else 1
            last_month = "" if open_ended else (
                MONTHS[months[-1].title()] if len(months) > 1 else 12)
            note = ("still serving at publication in 1994" if open_ended
                    else str(r.notes) if pd.notna(r.notes) else "")

            for i in range(len(bounds) - 1):
                first, final = bounds[i], bounds[i + 1] - 1
                if final < first:
                    continue
                yield {
                    "name": name, "district": "at large",
                    "end_status": ("still serving at publication"
                                   if open_ended and final == span_end else "recorded"),
                    "start_year": first,
                    "start_month": first_month if i == 0 else 1,
                    "end_year": "" if (open_ended and final == span_end) else final,
                    "end_month": "" if (open_ended and final == span_end) else (
                        last_month if final == span_end else 12),
                    "source": f"Novack (1994) p.{r.page}"
                              + ("; term boundaries from Arlington County (2021)"
                                 if cuts else ""),
                    "note": note if i == 0 else "re-elected",
                }


def build() -> pd.DataFrame:
    d = pd.DataFrame(list(oleary_terms()) + list(novack_terms()))
    d = d.sort_values(["name", "start_year", "start_month"]).reset_index(drop=True)

    # A counter within each person: their first term is 1, the term beginning
    # after the next election is 2, and so on. Someone appointed to a vacancy
    # who then wins twice has three rows numbered 1, 2, 3.
    # Keyed on the full name: two members can share a surname, and did.
    d["term_number"] = d.groupby(d.name.str.strip()).cumcount() + 1

    cols = ["name", "term_number", "district", "start_year", "start_month",
            "end_year", "end_month", "end_status", "source", "note"]
    return d[cols].sort_values(["start_year", "start_month", "district", "name"]).reset_index(drop=True)


if __name__ == "__main__":
    write(build(), "board_roster")
