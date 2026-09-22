"""Novack's roster -> transcribed/by_claude/arlington_historical_magazine/*.csv

*Six Decades of Arlington Leadership*, compiled by Norman S. Novack for the
Arlington Historical Magazine, 1994. An alphabetical roster of County Board
members with their terms of service, from the adoption of the County Manager
plan in 1930 to 1994.

It is the only source in the project that records **service** rather than
elections for that period: who held a seat and between which dates, with the
circumstances of every mid-term departure written in parentheses beneath the
name.

NOT part of `bash run.sh`. Run by hand, output committed.

A compilation, not a record. Novack worked from Electoral Board material and
local history; nothing here is a primary document.

    .venv/bin/python build/read_novack.py
"""
import re

import pymupdf

from files import RAW, TRANSCRIBED

SOURCE = (RAW / "arlington_historical_magazine"
          / "novack_six_decades_of_arlington_leadership_1994.pdf")
OUT = (TRANSCRIBED / "by_claude" / "arlington_historical_magazine"
       / "novack_terms_1930-1994.csv")

# "Elizabeth B. Magruder ........................... 1932-1947"
ENTRY = re.compile(r"^(.+?)\s*\.{3,}\s*\.*\s*(.+)$")


def read():
    doc = pymupdf.open(SOURCE)
    current = None
    open_paren = False
    for page_no, page in enumerate(doc, start=1):
        for raw_line in (page.get_text() or "").splitlines():
            line = " ".join(raw_line.split())
            if not line:
                continue
            # A note runs until its closing paren, however many lines that
            # takes. Testing that directly is what keeps a note from being cut
            # short - guessing from the wrapped line's first word does not,
            # because a wrapped line can begin with a capital ("House of
            # Representatives") or follow a footnote marker.
            if current and open_paren:
                # A word broken across lines is rejoined; the page shows one
                # word ("unconstitutional"), and the hyphen is typesetting.
                if current["notes"].endswith("-") and line[:1].islower():
                    current["notes"] = current["notes"][:-1] + line
                else:
                    current["notes"] += " " + line
                open_paren = current["notes"].count("(") > current["notes"].count(")")
                continue
            m = ENTRY.match(line)
            if m and not line.startswith("("):
                if current:
                    yield current
                name, term = m.group(1).strip(), m.group(2).strip()
                # The PDF's text layer splits digits inside some years -
                # "194 7" for 1947, "197 4" for 1974. The page shows no space,
                # so closing it restores what is printed rather than
                # interpreting it. Leftover dot leaders are stripped for the
                # same reason.
                term = re.sub(r"(?<=\d)\s+(?=\d)", "", term)
                term = re.sub(r"^[_\s.]+", "", term).strip()
                name = re.sub(r"[_\s.]+$", "", name).strip()
                # The text layer renders the roman numeral III as 111.
                name = re.sub(r"\b111\b", "III", name)
                current = {"page": page_no, "name": name, "term": term, "notes": ""}
            elif current and line.startswith("("):
                current["notes"] += ("; " if current["notes"] else "") + line
                open_paren = current["notes"].count("(") > current["notes"].count(")")
    if current:
        yield current


def main():
    rows = [r for r in read() if r["name"] not in ("Name", "Term of Service")]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("page,name,term,notes\n")
        for r in rows:
            fh.write(",".join(f'"{str(r[k]).replace(chr(34), chr(39))}"'
                              for k in ("page", "name", "term", "notes")) + "\n")
    print(f"  {OUT.relative_to(RAW.parents[1])}")
    print(f"    {len(rows)} members")


if __name__ == "__main__":
    main()
