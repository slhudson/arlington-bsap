"""Virginia elections database -> data/raw/va_dept_of_elections/county_board_2000-2026.csv

Run by hand when a newer election is needed; the build never touches the
network (CLAUDE.md).

    .venv/bin/python code/fetch/elections.py

Every County Board contest in the Department of Elections' historical
database (historical.elections.virginia.gov), as the CSV its search offers,
unaltered: every precinct, every vote channel, primaries included. The
office is Arlington's alone, so no locality filter is needed. It starts at
2000 because the database does for this office (checked 23 September 2026
against every 1930-1999 contest); 2000-2003 carry no party and, from 2002,
no votes, and party is recorded from 2007. It is the second source for a
member's party where it overlaps the county's candidate history, and the
only one from 2022.
"""
import json
import urllib.parse
import urllib.request

import paths

ROOT = paths.ROOT
OUT = paths.RAW / "va_dept_of_elections" / "county_board_2000-2026.csv"

ENDPOINT = "https://va2.elstats.civera.com/api/download_search.csv"
COUNTY_BOARD_MEMBER = 546            # the database's id for the office
YEARS = {"from": 2000, "to": 2026}

SEARCH = {
    "global": {"years": YEARS},
    "contests": {"candidates": [], "divisions": [],
                 "offices": [{"id": COUNTY_BOARD_MEMBER}]},
    "specialElectionsOnly": False, "voterStats": False, "stages": [],
}


def main():
    url = ENDPOINT + "?" + urllib.parse.urlencode({"search": json.dumps(SEARCH)})
    with urllib.request.urlopen(url) as r:
        body = r.read()
    if not body.startswith(b"contest_id,"):
        raise SystemExit("unexpected response - not the results CSV")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(body)
    print(f"  {OUT.relative_to(ROOT)}  ({body.count(b'\n'):,} rows)")


if __name__ == "__main__":
    main()
