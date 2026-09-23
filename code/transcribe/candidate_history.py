"""Arlington County election PDFs -> data/transcribed/by_claude/arlington_county/*.csv

NOT part of `bash run.sh`. Like census.py beside it, this runs on demand and its
output committed, so the build reads only committed files.

The candidate history is a positional table: year at one x-offset, election
date at another, then office, candidate and votes. Year, date and office are
printed once per group and carried down, exactly as a reader would follow them.
This reads the PDF's own text layer rather than an image, so it is not OCR -
but it is still a machine reading a document, which is why the output lands in
by_claude/ and not by_human/.

The whole table is transcribed, every office, not only the County Board rows.
Picking out today's rows would hide what sits beside them, and the file should
be checkable against the page as a whole.

    .venv/bin/python code/transcribe/candidate_history.py
"""
import csv
import re

import pymupdf

from files import RAW, TRANSCRIBED

SOURCE = RAW / "arlington_county" / "candidate_history_1920-present.pdf"
OUT = TRANSCRIBED / "by_claude" / "arlington_county" / "candidate_history_1920-present.csv"

# Column boundaries in PDF points, read off the printed header.
COLUMNS = [("year", 40, 90), ("date", 90, 215), ("office", 215, 385),
           ("candidate", 385, 585), ("votes", 585, 720)]

YEAR = re.compile(r"^(18|19|20)\d\d$")
# An election date with the month spelled out in full, ending in a year.
# The document abbreviates months only when describing a term ("Unexpired
# term ending Dec. 31, 2014"), and prints its revision date numerically
# ("11/18/2021"); neither is an election date, and neither matches.
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
YEAR_IN_DATE = re.compile(rf"^(?:{MONTHS}) \d{{1,2}},? ((?:19|20)\d\d)$")
DATE = re.compile(rf"^(?:{MONTHS}|Nomveber) \d{{1,2}}\b")   # one date is printed "Nomveber 3"
VOTES = re.compile(r"^[\d,]+$")
HEADERS = {"Year", "Election Date", "Office/Question", "Candidate/Selection", "Votes Rcd."}


def cells(page):
    """Group the page's words into rows, then into columns by x-offset."""
    lines = {}
    for w in page.get_text("words"):
        lines.setdefault(round(w[1] / 4), []).append(w)
    for y in sorted(lines):
        row = {name: [] for name, _, _ in COLUMNS}
        for w in sorted(lines[y], key=lambda w: w[0]):
            for name, lo, hi in COLUMNS:
                if lo <= w[0] < hi:
                    row[name].append(w[4])
                    break
        yield {k: " ".join(v).strip() for k, v in row.items()}


def read():
    doc = pymupdf.open(SOURCE)
    year = date = office = kind = ""
    for page_no, page in enumerate(doc, start=1):
        for row in cells(page):
            if row["year"] in HEADERS or row["candidate"] in HEADERS:
                continue
            # Every page ends with a footer row - "Last Updated: 11/18/2021 |
            # Arlington County | Electoral Board | Page N of 122" - split
            # across the same columns as the data. Left unfiltered, its
            # "Arlington County" lands in the office column and overwrites
            # the carried-down office for whatever row follows on the next
            # page (this is how Ellen Bozman's 1989 County Board win was
            # once mis-labelled "Arlington County").
            if row["year"].startswith("Last Updated"):
                continue
            # From 2008 the year column is blank and the year is written into
            # the date instead ("November 6, 2012"), so a year is taken from
            # either place.
            dated = YEAR_IN_DATE.search(row["date"])
            if YEAR.match(row["year"]):
                year = row["year"]
            elif dated:
                year = dated.group(1)
            # A date is a cell beginning with a month name. The document's own
            # revision date ("11/18/2021") sits in the same column and would
            # otherwise be carried down over unrelated years.
            # The date column also carries what kind of election it was -
            # "General Election", "Democratic Primary", "Special Election
            # (to fill ...)" - on the rows beneath the date.
            if DATE.match(row["date"]):
                date, kind = row["date"], ""
            elif row["date"] and not row["date"].startswith("Last Updated"):
                kind = (kind + " " + row["date"]).strip()
            # A parenthetical in the office column qualifies the office above
            # it - "(Two Seats)", "(to fill Zimmerman's unexpired term)" - so
            # it is appended rather than taken as a new office.
            if row["office"].startswith("(") or (
                    row["office"] and office.count("(") > office.count(")")):
                office = f"{office} {row['office']}"
            elif row["office"]:
                office = row["office"]
            if not row["candidate"]:
                continue

            # Text that overruns the candidate column lands in votes. Only a
            # bare number is a vote count; anything else belongs to the name.
            votes, extra = row["votes"], ""
            if votes and not VOTES.match(votes):
                extra, votes = votes, ""
            candidate = (row["candidate"] + " " + extra).strip()

            yield {"page": page_no, "year": year, "election_date": date,
                   "election_kind": kind, "office": office,
                   "candidate": candidate, "votes": votes}


def main():
    rows = list(read())
    # The kind of election is printed under the date, so the first candidate
    # row of each election is read before it. Every row of an election gets
    # the kind read from any of them.
    kinds = {}
    for r in rows:
        k = (r["page"], r["year"], r["election_date"])
        kinds[k] = " ".join(dict.fromkeys((kinds.get(k, "") + " " + r["election_kind"]).split()))
    for r in rows:
        r["election_kind"] = kinds[(r["page"], r["year"], r["election_date"])]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        # Some candidates are printed with a nickname in straight double
        # quotes - 'Kate A. "Katie" Cristol" - which is exactly the
        # character every field here is also quoted with. A naive strip
        # once dropped the quotes (and the point of transcribing them)
        # instead of escaping them, so csv.writer does the escaping.
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(["page", "year", "election_date", "election_kind", "office",
                    "candidate", "votes"])
        for r in rows:
            w.writerow([r[k] for k in ("page", "year", "election_date", "election_kind",
                                        "office", "candidate", "votes")])
    board = [r for r in rows if "County Board" in r["office"]]
    years = sorted({r["year"] for r in board if r["year"]})
    print(f"  {OUT.relative_to(RAW.parents[1])}")
    print(f"    {len(rows):,} rows, {doc_pages()} pages")
    print(f"    County Board rows: {len(board):,}, {years[0]}-{years[-1]}")


def doc_pages():
    return pymupdf.open(SOURCE).page_count


if __name__ == "__main__":
    main()
