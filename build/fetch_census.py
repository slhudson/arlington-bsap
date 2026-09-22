"""Census API -> data/raw/census/<year>/*.csv, whole tables, for 2000-2020.

NOT part of `bash run.sh`, deliberately. The build never touches the network:
anyone who clones this repository produces every figure from committed files,
with no account, no API key and no connection. Fetching is a separate act whose
output is committed.

It also keeps figures reproducible. An API can change its answer; a committed
file cannot, which is the standard the scanned volumes are held to.

Run by hand when a year is needed:

    .venv/bin/python build/fetch_census.py

Needs CENSUS_API_KEY in .env at the repository root. That file is gitignored.

**Whole tables, every county, saved as published.** One row per Virginia
county, one column per variable, exactly the shape the Bureau publishes.
Arlington is a row in it rather than an extract - which is the same rule the
transcriptions follow, and which also allows a figure to be checked against
neighbouring counties.

Picking out the variables today's figure happens to need would hide what sits
beside them, and in this project what sat beside them mattered twice.

Each census also gets a data dictionary, so the column codes are readable
without the API documentation.

For 2000-2020 the Bureau publishes machine-readable data, so there is no page
to read and no transcription step, and therefore no reading error to make. The
scanned volumes are transcribed only because nothing else exists for them.
"""
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "census"
STATE, COUNTY = "51", "013"   # Virginia, Arlington County

# Which tables to fetch for each census. RACE gives the race partition; the
# Hispanic-origin table gives race crossed with Hispanic origin, which is what
# any consistent set of categories has to be built from - see questions.md Q1.
# Group names differ by census even where the variables do not: 2000 uses
# P003, 2010 the same table as P3, 2020 as P1. Named here rather than derived.
TABLES = {
    2000: ("dec/sf1", {"P003": "race", "P008": "hispanic_origin_by_race"}),
    2010: ("dec/sf1", {"P3": "race", "P5": "hispanic_origin_by_race"}),
    2020: ("dec/pl", {"P1": "race", "P2": "hispanic_origin_by_race"}),
}


def api_key():
    env = ROOT / ".env"
    if not env.exists():
        raise SystemExit("no .env at the repository root; see this file's docstring")
    for line in env.read_text().splitlines():
        if line.startswith("CENSUS_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("CENSUS_API_KEY not found in .env")


def get(url):
    """Fetch and decode, surfacing the API's own error text rather than a stack trace."""
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Census API {e.code}: {e.read().decode(errors='replace')[:200].strip()}")


def is_value(code, table):
    """True for a data column of this table, false for annotation columns."""
    if code.endswith(("ERR", "EA", "MA", "_NA")):
        return False
    return (code.startswith(table + "_")
            or (code.startswith(table) and code[len(table):].isdigit())
            or (table in ("P3", "P5") and code.startswith("P00" + table[1:])))


def first_value(head, table):
    return next(c for c in head if is_value(c, table))


def labels(year, dataset):
    """The Bureau's own label for every variable, so the saved file is readable."""
    return get(f"https://api.census.gov/data/{year}/{dataset}/variables.json")["variables"]


def main():
    key = api_key()
    for year, (dataset, tables) in TABLES.items():
        out_dir = RAW / str(year)
        out_dir.mkdir(parents=True, exist_ok=True)
        meta = labels(year, dataset)
        wanted = set()

        for table, name in tables.items():
            # Every county in Virginia, not just Arlington. The published unit
            # is the table, and Arlington is a row in it - which is also what
            # lets a figure be sanity-checked against neighbouring counties.
            url = f"https://api.census.gov/data/{year}/{dataset}?" + urllib.parse.urlencode({
                "get": f"group({table})", "for": "county:*",
                "in": f"state:{STATE}", "key": key})
            rows = get(url)
            head = rows[0]
            keep = [i for i, c in enumerate(head)
                    if c in ("NAME", "state", "county") or is_value(c, table)]
            wanted.update(head[i] for i in keep if head[i] not in ("NAME", "state", "county"))

            out = out_dir / f"censusapi_{dataset.replace('/', '_')}_{table}_{name}_virginia_counties.csv"
            with out.open("w") as fh:
                fh.write(",".join(head[i] for i in keep) + "\n")
                for r in sorted(rows[1:], key=lambda r: r[head.index("NAME")]):
                    fh.write(",".join(f'"{r[i]}"' if "," in str(r[i]) else str(r[i]) for i in keep) + "\n")
            arl = next(r for r in rows[1:] if r[head.index("NAME")].startswith("Arlington"))
            print(f"  {out.relative_to(ROOT)}  {len(rows)-1} counties, {len(keep)} columns"
                  f"  (Arlington total {int(arl[head.index(first_value(head, table))]):,})")

        # One data dictionary per census, so the column codes are readable
        # without the API documentation.
        dic = out_dir / f"censusapi_{dataset.replace('/', '_')}_variables.csv"
        with dic.open("w") as fh:
            fh.write("variable,label\n")
            for code in sorted(wanted):
                label = meta.get(code, {}).get("label", "").replace("!!", " / ").strip(" /")
                fh.write(f'{code},"{label}"\n')
        print(f"  {dic.relative_to(ROOT)}  {len(wanted)} variables")


if __name__ == "__main__":
    main()
