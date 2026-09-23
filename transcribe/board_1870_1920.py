"""O'Leary's electoral history -> transcribed/by_claude/arlington_county/board_1870-1920.csv

The Board of Supervisors entries from *The Electoral History of That Part of
Alexandria County Now Known as Arlington County, 1870-1920*, by Frank O'Leary.
This is the only source covering 1871-1931, which the person-level roster does
not reach.

NOT part of `bash run.sh`. Run by hand, output committed.

The listing pages are rotated 90 degrees, so a column on the page is a line of
the table. Reading left to right by x-offset recovers the printed order. Each
election begins a block - "1872 May 25 Board of Supervisors" - and the columns
that follow give a district and who held it, with replacements and vacancies
written in prose beside the name.

Those notes are kept verbatim rather than parsed. "Vacant - Samuel Titus
appointed in Dec." and "Replaced by H. Dwight Smith in Dec.; replaced by Lott
W. Crocker in March 1873" carry more than any set of columns would, and
splitting them here would be a second machine reading of an already
machine-read page.

**A compilation, not a record.** O'Leary writes that pre-20th-century
record-keeping was "ragged and incomplete" and that elections were "not always
held (or at least not reported)". Absence of an entry is not evidence of
absence.

    .venv/bin/python transcribe/board_1870_1920.py
"""
import re

import pymupdf

from files import RAW, TRANSCRIBED

SOURCE = RAW / "arlington_county" / "electoral_history_1870-1920.pdf"
OUT = TRANSCRIBED / "by_claude" / "arlington_county" / "board_1870-1920.csv"

DISTRICTS = ("Arlington", "Jefferson", "Washington")

# Printed at the top of every listing page. Rotated, these land at the end of
# whichever entry was last on the page, so they are stripped rather than kept.
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
            # From 1903 the office line often drops the year, which is then
            # carried forward from the previous election on the page.
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
                # Many later entries give only a month - "1879 May Board of
                # Supervisors" - so the day is optional.
                date = f"{month} {day}" if day else month
                in_board = "Board of Supervisors" in office
                continue
            if not in_board:
                continue
            if line.startswith(("Constable", "Clerk", "Commissioner",
                                "Commonwealth", "Sheriff", "Treasurer",
                                "House of", "Senate", "President", "Governor")):
                # a different office begins; the Board block has ended
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
                # Either a continuation of a note, or - from 1903 - a further
                # candidate for the same district. Both are kept verbatim;
                # separating them is interpretation, not transcription.
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
