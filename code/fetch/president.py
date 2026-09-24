"""Virginia elections database -> data/raw/va_dept_of_elections/president_1924-2024.csv

NOT part of `bash run.sh`, deliberately. The build never touches the network:
see code/fetch/census.py for why.

Run by hand after a presidential election:

    .venv/bin/python code/fetch/president.py

Arlington's presidential vote, every four years from 1924, from the
Department of Elections' historical database (historical.elections.virginia.gov).
1924 is where the database's Arlington rows for this office begin; the county's
own candidate history and O'Leary's electoral history carry 1872-1920, and the
build takes those years from them.

**An extract, not the file as published, and size is the only reason.** The
database offers the search as one CSV for the whole state - 470,000 rows and
75 MB for this office, against an Overleaf budget of 100 MB for the whole
repository - so only Arlington's rows are kept. The rows kept are the
database's own, unaltered: one per candidate per general election at the
locality level, which the database carries for every year, including the
years from 1996 for which it also holds precincts. Locality rows are the
state's canvassed totals and are what the earlier years have; taking them
throughout keeps every year on the same basis.

Party is the database's own `candidate_party_name`, present on every row.
"""
import io
import json
import urllib.parse
import urllib.request

import pandas as pd

import paths

ROOT = paths.ROOT
OUT = paths.RAW / "va_dept_of_elections" / "president_1924-2024.csv"

ENDPOINT = "https://va2.elstats.civera.com/api/download_search.csv"
PRESIDENT = 1                        # the database's id for the office
YEARS = {"from": 1789, "to": 2026}   # the whole range; Arlington's rows start in 1924

SEARCH = {
    "global": {"years": YEARS},
    "contests": {"candidates": [], "divisions": [], "offices": [{"id": PRESIDENT}]},
    "specialElectionsOnly": False, "voterStats": False, "stages": [],
}


def main():
    url = ENDPOINT + "?" + urllib.parse.urlencode({"search": json.dumps(SEARCH)})
    with urllib.request.urlopen(url, timeout=600) as r:
        body = r.read()
    if not body.startswith(b"contest_id,"):
        raise SystemExit("unexpected response - not the results CSV")
    d = pd.read_csv(io.BytesIO(body), low_memory=False)
    keep = d[(d.division_type == "Locality") & (d.division_name == "Arlington County")
             & d.election_type.str.startswith("General")]
    if keep.empty:
        raise SystemExit("no Arlington County locality rows - has the database changed shape?")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    keep.to_csv(OUT, index=False)
    years = sorted(pd.to_datetime(keep.election_date).dt.year.unique())
    print(f"  {OUT.relative_to(ROOT)}  ({len(keep):,} of {len(d):,} rows; {years[0]}-{years[-1]}, {len(years)} elections)")


if __name__ == "__main__":
    main()
