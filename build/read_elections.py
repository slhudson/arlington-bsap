"""Arlington County election PDFs -> data/transcribed/by_claude/county/*.csv

NOT part of `bash run.sh`. Like ocr_census.py, this is run by hand and its
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

    .venv/bin/python build/read_elections.py
"""
import re

import pymupdf

from files import RAW, TRANSCRIBED

SOURCE = RAW / "county" / "candidate_history_1920-present.pdf"
OUT = TRANSCRIBED / "by_claude" / "county" / "candidate_history_1920-present.csv"

# Column boundaries in PDF points, read off the printed header.
COLUMNS = [("year", 40, 90), ("date", 90, 215), ("office", 215, 385),
           ("candidate", 385, 585), ("votes", 585, 720)]

YEAR = re.compile(r"^(18|19|20)\d\d$")
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
    year = date = office = ""
    for page_no, page in enumerate(doc, start=1):
        for row in cells(page):
            if row["year"] in HEADERS or row["candidate"] in HEADERS:
                continue
            if YEAR.match(row["year"]):
                year = row["year"]
            # A date only belongs to the election it heads. The document's own
            # revision date appears in the same column and would otherwise be
            # carried down over unrelated years, which is how 1927 rows came to
            # be stamped 11/18/2021.
            if row["date"] and (YEAR.match(row["year"]) or not date):
                date = row["date"]
            if row["office"]:
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
                   "office": office, "candidate": candidate, "votes": votes}


def main():
    rows = list(read())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("page,year,election_date,office,candidate,votes\n")
        for r in rows:
            fh.write(",".join(f'"{str(r[k]).replace(chr(34), "")}"'
                              for k in ("page", "year", "election_date", "office",
                                        "candidate", "votes")) + "\n")
    board = [r for r in rows if "County Board" in r["office"]]
    years = sorted({r["year"] for r in board if r["year"]})
    print(f"  {OUT.relative_to(RAW.parents[1])}")
    print(f"    {len(rows):,} rows, {doc_pages()} pages")
    print(f"    County Board rows: {len(board):,}, {years[0]}-{years[-1]}")


def doc_pages():
    return pymupdf.open(SOURCE).page_count


if __name__ == "__main__":
    main()
