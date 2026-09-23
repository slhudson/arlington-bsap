"""O'Leary's electoral history -> transcribed/by_claude/arlington_county/president_1872-1920.csv

The presidential returns from *The Electoral History of That Part of
Alexandria County Now Known as Arlington County, 1870-1920*, by Frank
O'Leary - the only source for the county's presidential vote before the
state database begins in 1924.

NOT part of `bash run.sh`. Run by hand, output committed.

Read the same way as board_1870_1920.py, and using its page reader: a
rotated page's columns are the table's lines. A "President" line inside an
election block starts the returns, and each line after it is one candidate
with the district counts as printed - "Grant 226 157 72 455" for Arlington,
Jefferson, Washington and the total, or a single county figure from 1904.
Lines are kept verbatim, "?" and parentheses included; parsing them is
code/build/voters.py's job.

**A compilation, not a record**, in O'Leary's own words, and the returns
for 1896, 1904 and 1908 are visibly incomplete on the page. The build says
what it does with them.

    .venv/bin/python code/transcribe/president_1872_1920.py
"""
import pymupdf

from board_1870_1920 import ELECTION, PAGE_FURNITURE, SOURCE, columns
from files import RAW, TRANSCRIBED

OUT = TRANSCRIBED / "by_claude" / "arlington_county" / "president_1872-1920.csv"

OTHER_OFFICES = ("Constable", "Clerk", "Commissioner", "Commonwealth", "Sheriff",
                 "Treasurer", "House of", "Senate", "Governor", "Board of Supervisors",
                 "Lt.", "Attorney", "Congress", "Justice", "Overseer", "Supervisor", "U.S.")


def read():
    doc = pymupdf.open(SOURCE)
    year = date = ""
    in_president = False
    for page_no, page in enumerate(doc, start=1):
        if page.rotation != 90:
            continue
        for line in columns(page):
            m = ELECTION.match(line)
            if m:
                year, month, day, office = m.groups()
                date = f"{month} {day}" if day else month
                in_president = office.strip().startswith("President")
                if in_president:
                    line = office.strip()[len("President"):].strip()
                    if not line:
                        continue
                else:
                    continue
            elif line.startswith("President"):
                in_president = True
                line = line[len("President"):].strip()
                if not line:
                    continue
            elif line.startswith(OTHER_OFFICES):
                in_president = False
                continue
            if not in_president:
                continue
            for junk in PAGE_FURNITURE:
                line = line.replace(junk, "").strip()
            if line:
                yield {"page": page_no, "year": year, "election_date": date, "entry": line}


def main():
    rows = list(read())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("page,year,election_date,entry\n")
        for r in rows:
            fh.write(",".join(f'"{str(r[k]).replace(chr(34), chr(39))}"'
                              for k in ("page", "year", "election_date", "entry")) + "\n")
    years = sorted({r["year"] for r in rows})
    print(f"  {OUT.relative_to(RAW.parents[1])}")
    print(f"    {len(rows)} candidate lines, {years[0]}-{years[-1]}, {len(years)} elections")


if __name__ == "__main__":
    main()
