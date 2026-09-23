"""Virginia elections database -> data/raw/va_dept_of_elections/county_board_2000-2026.csv

NOT part of `bash run.sh`, deliberately. The build never touches the network:
see code/fetch/census.py for why.

Run by hand when a newer election is needed:

    .venv/bin/python code/fetch/elections.py

The county's own candidate history stops at the 2021 election, and the county
no longer publishes it. From 2022 the source is the Department of Elections'
historical database (historical.elections.virginia.gov), which holds every
County Board contest by precinct and vote channel and offers the search as a
CSV. The file saved here is that CSV, unaltered: every precinct, every
channel, primaries included. The build sums a candidate's rows and reads the
kind of election from the file's own column.

The office is Arlington's alone - no other Virginia locality calls its
governing body a County Board - so the search needs no locality filter.

It starts at 2000 because that is where the database starts for this office.
The database reaches back to 1789 for federal and statewide races, but its
only Arlington contests before 2000 are federal, statewide and General
Assembly ones (checked on 23 September 2026 by searching every 1930-1999
contest and filtering to Arlington divisions). The County Board rows for
2000-2003 carry no party and, from 2002, no votes; party is recorded from
2007. So the county's candidate history remains the roster's source through
2021, and this file is the second source for a member's party where the two
overlap - the build checks that they agree - and the only one from 2022.
"""
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "raw" / "va_dept_of_elections" / "county_board_2000-2026.csv"

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
