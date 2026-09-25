"""Arlington County election PDFs -> data/transcribed/by_claude/arlington_county/*.csv

Run by hand, output committed.

    .venv/bin/python code/transcribe/candidate_history.py

The candidate history is a positional table: year, election date, office,
candidate and votes at fixed x-offsets. Year, date and office are printed
once per group and carried down. The PDF's own text layer is read. The whole
table is transcribed, every office.
"""
import csv
import re

import pymupdf

from paths import RAW, TRANSCRIBED

SOURCE = RAW / "arlington_county" / "candidate_history_1920-present.pdf"
OUT = TRANSCRIBED / "by_claude" / "arlington_county" / "candidate_history_1920-present.csv"

# Column boundaries in PDF points, read off the printed header.
COLUMNS = [("year", 40, 90), ("date", 90, 215), ("office", 215, 385),
           ("candidate", 385, 585), ("votes", 585, 720)]

YEAR = re.compile(r"^(18|19|20)\d\d$")
# An election date: the month spelled out in full, unlike a term's "Dec. 31,
# 2014" or the revision date "11/18/2021".
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
            # The footer row, split across the same columns as the data.
            if row["year"].startswith("Last Updated"):
                continue
            # The year is in the year column, or from 2008 in the date.
            dated = YEAR_IN_DATE.search(row["date"])
            if YEAR.match(row["year"]):
                year = row["year"]
            elif dated:
                year = dated.group(1)
            # The date column also carries the kind of election, on the rows
            # beneath the date.
            if DATE.match(row["date"]):
                date, kind = row["date"], ""
            elif row["date"] and not row["date"].startswith("Last Updated"):
                kind = (kind + " " + row["date"]).strip()
            # A parenthetical in the office column qualifies the office above it.
            if row["office"].startswith("(") or (
                    row["office"] and office.count("(") > office.count(")")):
                office = f"{office} {row['office']}"
            elif row["office"]:
                office = row["office"]
            # An office name in the candidate column with no vote count is
            # the office for the rows that follow.
            if row["candidate"] == "County Board" and not row["votes"]:
                office = row["candidate"]
                continue
            if not row["candidate"]:
                continue

            # Text that overruns the candidate column lands in votes.
            votes, extra = row["votes"], ""
            if votes and not VOTES.match(votes):
                extra, votes = votes, ""
            candidate = (row["candidate"] + " " + extra).strip()

            yield {"page": page_no, "year": year, "election_date": date,
                   "election_kind": kind, "office": office,
                   "candidate": candidate, "votes": votes}


def main():
    rows = list(read())
    # Every row of an election gets the kind read from any of its rows.
    kinds = {}
    for r in rows:
        k = (r["page"], r["year"], r["election_date"])
        kinds[k] = " ".join(dict.fromkeys((kinds.get(k, "") + " " + r["election_kind"]).split()))
    for r in rows:
        r["election_kind"] = kinds[(r["page"], r["year"], r["election_date"])]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        # Nicknames are printed in double quotes; csv.writer escapes them.
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
