"""Virginia elections database -> data/raw/va_dept_of_elections/county_board_2021-2026.csv

NOT part of `bash run.sh`, deliberately. The build never touches the network:
see fetch/census.py for why.

Run by hand when a newer election is needed:

    .venv/bin/python fetch/elections.py

The county's own candidate history stops at the 2021 election, and the county
no longer publishes it. From 2022 the source is the Department of Elections'
historical database (historical.elections.virginia.gov), which holds every
County Board contest by precinct and vote channel and offers the search as a
CSV. The file saved here is that CSV, unaltered: every precinct, every
channel, primaries included. The build sums a candidate's rows and reads the
kind of election from the file's own column.

The office is Arlington's alone - no other Virginia locality calls its
governing body a County Board - so the search needs no locality filter. It
starts at 2021 so that one election overlaps the county's candidate history;
the build checks that the two agree there.
"""
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "va_dept_of_elections" / "county_board_2021-2026.csv"

ENDPOINT = "https://va2.elstats.civera.com/api/download_search.csv"
COUNTY_BOARD_MEMBER = 546            # the database's id for the office
YEARS = {"from": 2021, "to": 2026}

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
