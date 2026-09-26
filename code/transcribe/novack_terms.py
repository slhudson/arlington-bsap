"""Novack's roster -> transcribed/by_claude/arlington_historical_magazine/*.csv

*Six Decades of Arlington Leadership*, compiled by Norman S. Novack for the
Arlington Historical Magazine, 1994: an alphabetical roster of County Board
members with their terms of service, 1930-1994, and the circumstances of
each mid-term departure in parentheses beneath the name. Run by hand,
output committed.

    .venv/bin/python code/transcribe/novack_terms.py
"""
import re

import pymupdf

from paths import BY_CLAUDE, RAW

SOURCE = (RAW / "arlington_historical_magazine"
          / "novack_six_decades_of_arlington_leadership_1994.pdf")
OUT = (BY_CLAUDE / "arlington_historical_magazine"
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
            # takes; a word broken across lines is rejoined.
            if current and open_paren:
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
                # The text layer splits digits inside some years ("194 7")
                # and leaves dot leaders; the page shows neither.
                term = re.sub(r"(?<=\d)\s+(?=\d)", "", term)
                term = re.sub(r"^[_\s.]+", "", term).strip()
                name = re.sub(r"[_\s.]+$", "", name).strip()
                # The text layer renders the roman numeral III as 111.
                name = re.sub(r"\b111\b", "III", name)
                # The text layer also runs an initial into the word before it
                # ("HerbertL."), and the trailing-dot strip above takes the
                # period off Jr and Sr; the rest of the project writes both
                # with the period and initials with a space after each.
                name = re.sub(r"(?<=[a-z])(?=[A-Z]\.)", " ", name)
                name = re.sub(r"\b([A-Z])\.(?=[A-Z])", r"\1. ", name)
                name = re.sub(r"\b(Jr|Sr)$", r"\1.", name)
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
