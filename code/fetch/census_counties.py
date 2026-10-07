"""Census counties -> sources/government/federal/us_census_bureau/2020/censusapi_dec_pl_P1_race_us_counties.csv.gz

Run by hand, output committed, stored gzip-compressed (fetch/paths.py); the
build never touches the network (CLAUDE.md). Needs CENSUS_API_KEY in .env at
the repository root.

    .venv/bin/python code/fetch/census_counties.py

The 2020 redistricting file's race table, every county in the United States,
as the Bureau publishes it, with the state's and county's FIPS codes. Only
its total is read: code/clean/localities_southeastern.py checks that the
peer table holds every county of its size in its states.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

import paths

OUT = paths.CENSUS_BUREAU / "2020" / "censusapi_dec_pl_P1_race_us_counties.csv.gz"


def main():
    url = "https://api.census.gov/data/2020/dec/pl?" + urllib.parse.urlencode({
        "get": "NAME,P1_001N", "for": "county:*", "in": "state:*",
        "key": paths.api_key("CENSUS_API_KEY")})
    try:
        with urllib.request.urlopen(url, timeout=180) as r:
            rows = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Census API {e.code}: {e.read().decode(errors='replace')[:200].strip()}")
    head, body = rows[0], sorted(rows[1:], key=lambda r: (r[2], r[3]))
    paths.write_text(OUT, ",".join(head) + "\n" + "".join(
        ",".join(f'"{c}"' if "," in c else c for c in r) + "\n" for r in body))
    print(f"  {OUT.relative_to(paths.ROOT)}  {len(body)} counties")


if __name__ == "__main__":
    main()
