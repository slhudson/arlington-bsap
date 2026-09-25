"""O'Leary's electoral history -> transcribed/by_claude/arlington_county/board_1870-1920.csv

The Board of Supervisors entries from *The Electoral History of That Part
of Alexandria County Now Known as Arlington County, 1870-1920*, by Frank
O'Leary. Run by hand, output committed.

    .venv/bin/python code/transcribe/board_1870_1920.py

The listing pages are rotated 90 degrees, so a column on the page is a
line of the table, read left to right by x-offset. Each election begins a
block - "1872 May 25 Board of Supervisors" - and the columns that follow
give a district and who held it, with replacements and vacancies in prose
beside the name. The prose is kept verbatim; parsing it is
code/build/board_roster.py's job.
"""
import re

import pymupdf

from paths import BY_CLAUDE, RAW

SOURCE = RAW / "arlington_county" / "electoral_history_1870-1920.pdf"
OUT = BY_CLAUDE / "arlington_county" / "board_1870-1920.csv"

DISTRICTS = ("Arlington", "Jefferson", "Washington")

# Printed at the top of every listing page; stripped.
PAGE_FURNITURE = ("Year Election Date Office Candidate Votes",
                  "Arl Jeff Wash Total", "City County Total", "Version 2")
MONTHS = ("January|February|March|April|May|June|July|"
          "August|September|October|November|December")
ELECTION = re.compile(rf"^((?:18|19)\d\d)\s+({MONTHS})\s*(\d+)?\s+(.*)$")


def columns(page):
    """A rotated page's columns, left to right: each is a printed line."""
    cols = {}
    for w in page.get_text("words"):
        cols.setdefault(round(w[0] / 6), []).append(w)
    for x in sorted(cols):
        yield " ".join(w[4] for w in sorted(cols[x], key=lambda w: -w[1])).strip()


def read():
    doc = pymupdf.open(SOURCE)
    year = date = ""
    in_board = False
    current = None

    for page_no, page in enumerate(doc, start=1):
        if page.rotation != 90:
            continue
        for line in columns(page):
            # An office line without a year carries the previous year forward.
            if not ELECTION.match(line) and line.startswith("Board of Supervisors"):
                if current:
                    yield current
                    current = None
                in_board = True
                continue

            m = ELECTION.match(line)
            if m:
                if current:
                    yield current
                    current = None
                year, month, day, office = m.groups()
                date = f"{month} {day}" if day else month
                in_board = "Board of Supervisors" in office
                continue
            if not in_board:
                continue
            if line.startswith(("Constable", "Clerk", "Commissioner",
                                "Commonwealth", "Sheriff", "Treasurer",
                                "House of", "Senate", "President", "Governor")):
                if current:
                    yield current
                    current = None
                in_board = False
                continue

            for junk in PAGE_FURNITURE:
                line = line.replace(junk, "").strip()
            if not line:
                continue

            district = next((d for d in DISTRICTS if line.startswith(d)), None)
            if district:
                if current:
                    yield current
                current = {"page": page_no, "year": year, "election_date": date,
                           "district": district,
                           "entry": line[len(district):].strip()}
            elif current and line:
                # A continuation of a note, or a further candidate; both
                # are kept verbatim.
                current["entry"] += " " + line
    if current:
        yield current


def main():
    rows = list(read())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("page,year,election_date,district,entry\n")
        for r in rows:
            fh.write(",".join(f'"{str(r[k]).replace(chr(34), chr(39))}"'
                              for k in ("page", "year", "election_date",
                                        "district", "entry")) + "\n")
    years = sorted({r["year"] for r in rows})
    print(f"  {OUT.relative_to(RAW.parents[1])}")
    print(f"    {len(rows)} district-entries, {years[0]}-{years[-1]}")


if __name__ == "__main__":
    main()
