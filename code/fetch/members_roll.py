"""The county's roll of Board members -> data/raw/arlington_county/members_roll.pdf

Run by hand; the build never touches the network (CLAUDE.md).

    .venv/bin/python code/fetch/members_roll.py

Arlington publishes its own roll of the County Board, one entry per year
from 1932, each member named with the office held that year and with
arrivals and departures dated to the day: "Resigned 12/14/95", "Special
Election 1/30/96: Replaced Mary Margaret Whipple", "Appointed on 7/15/2023
to fill seat vacated by Katie Cristol". It is the only source this project
holds that records service rather than contests, so it is the one witness to
a member seated without winning an election. docs/members.md, "The roster".

The page keeps each decade in a collapsed accordion, and the county's server
refuses curl, so the copy is the page printed by headless Chrome, which
expands every panel and carries a text layer. The print is 22 pages; the
transcription reads it in code/transcribe/members_roll.py.
"""
import subprocess
import sys

import paths

URL = ("https://www.arlingtonva.us/Government/Departments/County-Board/"
       "County-Board-Members/Historical-Members-1932-Present")
OUT = paths.RAW / "arlington_county" / "members_roll.pdf"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")

# Strings the roll must carry, one per decade of the page's accordions: a
# print that lost a collapsed panel would otherwise look like a good file.
PROBES = ["Appointed 6/1/33", "Appointed 5/17/47", "Appointed 1/29/60",
          "Appointed 1/1/75", "James Hunter (5/15/90)", "Resigned 12/14/95",
          "Special election on 3/11/03", "Resigned 2/10/14",
          "Appointed on 7/15/2023"]


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--user-agent={USER_AGENT}", f"--print-to-pdf={OUT}", URL],
                   capture_output=True, text=True, timeout=180)
    if not OUT.exists() or OUT.stat().st_size < 100_000:
        sys.exit("headless Chrome printed nothing; the page may be behind a check now")
    import pymupdf
    text = "".join(page.get_text() for page in pymupdf.open(OUT))
    missing = [p for p in PROBES if p not in text]
    if missing:
        sys.exit("the print is missing entries the page carries:\n  "
                 + "\n  ".join(missing))
    print(f"{OUT.relative_to(paths.ROOT)}: {OUT.stat().st_size // 1024}KB, "
          f"{len(text)} characters of text")


if __name__ == "__main__":
    main()
