"""Virginia elections database -> sources/government/state/va_dept_of_elections/president_1924-2024.csv.gz

Run by hand after a presidential election; the build never touches the
network (CLAUDE.md).

    .venv/bin/python code/fetch/president.py

Arlington's presidential vote every four years from 1924, where the
database's Arlington rows for this office begin, from the Department of
Elections' historical database. Only Arlington's locality-level general
election rows are kept, unaltered, because the whole-state CSV is 75MB
against an Overleaf budget of 100MB; locality rows are the state's
canvassed totals and are what every year has. Party is the database's own
`candidate_party_name`.
"""
import io
import json
import urllib.parse
import urllib.request

import pandas as pd

import paths

ROOT = paths.ROOT
OUT = paths.VA_ELECTIONS / "president_1924-2024.csv.gz"

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
    paths.write_text(OUT, keep.to_csv(index=False))
    years = sorted(pd.to_datetime(keep.election_date).dt.year.unique())
    print(f"  {OUT.relative_to(ROOT)}  ({len(keep):,} of {len(d):,} rows; {years[0]}-{years[-1]}, {len(years)} elections)")


if __name__ == "__main__":
    main()
