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

            term_end_year = int(nxt) if nxt else ""
            term_end_month = (month_of(d[d.year == nxt].election_date.iloc[0])
                              if nxt else "")
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
                yield {"name": who, "district": r.district,
                       "start_year": y0, "start_month": m0,
                       "end_year": y1, "end_month": m1,
                       "source": f"O'Leary (2012) p.{r.page}",
                       "note": note if i == 0 else f"took the seat mid-term; {note}"}


def novack_terms():
    """Terms of service under the County Manager plan, elected at large."""
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
            yield {
                "name": str(r["name"]).strip(), "district": "at large",
                "start_year": start,
                "start_month": MONTHS[months[0].title()] if months else 1,
                "end_year": "" if open_ended else end,
                "end_month": "" if open_ended else (
                    MONTHS[months[-1].title()] if len(months) > 1 else 12),
                "source": f"Novack (1994) p.{r.page}",
                "note": ("still serving at publication in 1994" if open_ended
                         else str(r.notes) if pd.notna(r.notes) else ""),
            }


def build() -> pd.DataFrame:
    d = pd.DataFrame(list(oleary_terms()) + list(novack_terms()))
    return d.sort_values(["start_year", "district", "name"]).reset_index(drop=True)


if __name__ == "__main__":
    write(build(), "board_roster")
