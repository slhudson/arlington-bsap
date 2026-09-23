"""Census -> data/raw/us_census_bureau/<year>/*.csv, whole tables, 1980-2020.

NOT part of `bash run.sh`, deliberately. The build never touches the network:
anyone who clones this repository produces every figure from committed files,
with no account, no API key and no connection. Fetching is a separate act whose
output is committed.

It also keeps figures reproducible. An API can change its answer; a committed
file cannot, which is the standard the scanned volumes are held to.

Run by hand when a year is needed:

    .venv/bin/python code/fetch/census.py

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

**1980 and 1990 come from the archived Summary Tape Files, not the API.** The
Census API holds no decennial data before 2000; its 1990-vintage entries are
the December Current Population Survey. The 1980 and 1990 STF1A files are
published as fixed-width ASCII, one file per state, at www2.census.gov, and
need no key.

They are what makes a consistent set of race categories possible back to 1980:
both carry Hispanic (1980: Spanish) origin crossed with race at county level,
which is the only way to build groups that do not overlap. 1970 is not in this
script and should not be added. Hispanic origin in 1970 was asked of a
5 percent sample rather than the full count, the Bureau's position is that it
is not comparable with later years, and it has a known defect miscoding people
in the southern and central states into "Central or South American".

1980's record layout is the Bureau's own published dictionary, saved beside the
data. 1990's technical documentation is only published as PDF, so its cell
offsets were derived from the file and then checked: the five race cells and
the ten Hispanic-origin-by-race cells each sum to the published county total,
for all 136 Virginia county-level geographies. main() re-runs those checks on
every fetch and refuses to write if one fails.

**What is saved is an extract, not the file as published.** The two 1990
segments are 172MB and the 1980 file 30MB, against an Overleaf budget of
100MB for the whole repository. So these are cut to Virginia county rows and
the tables named below - the same shape as the API years, which are also one
row per Virginia county. It is a departure from saving a source untouched, and
the reason is size alone.
"""
import io
import json
import pathlib
import urllib.parse
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "us_census_bureau"
STATE, COUNTY = "51", "013"   # Virginia, Arlington County

# Which tables to fetch for each census. RACE gives the race partition; the
# Hispanic-origin table gives race crossed with Hispanic origin, which is what
# any consistent set of categories has to be built from - see docs/questions.md.
# Group names differ by census even where the variables do not: 2000 uses
# P003, 2010 the same table as P3, 2020 as P1. Named here rather than derived.
#
# The third table is the same race partition for the population 18 years and
# over, which is the voting-age population: the denominator turnout is put
# over when registration is not known. Its first cell is the total.
TABLES = {
    2000: ("dec/sf1", {"P003": "race", "P008": "hispanic_origin_by_race",
                       "P005": "race_18_and_over"}),
    2010: ("dec/sf1", {"P3": "race", "P5": "hispanic_origin_by_race",
                       "P10": "race_18_and_over"}),
    2020: ("dec/pl", {"P1": "race", "P2": "hispanic_origin_by_race",
                      "P3": "race_18_and_over"}),
}


# --- 1980 and 1990: the archived Summary Tape Files --------------------------
#
# Fixed-width ASCII, one file per state, no key. Positions below are 1-based
# and inclusive of the first character, as the Bureau's dictionaries write them.
# Every cell is 9 characters.
#
# 1980 comes from the published dictionary saved beside the data
# (1980_stf1_datadict.txt): Table 7 is race, Table 8 Spanish origin, Table 9
# the race of persons of Spanish origin. Table 9 is the cross-tab.
#
# 1990's documentation is PDF only, so its offsets were read off the file and
# are checked on every run - see this module's docstring.

# The age groups as the two files cut them, in the Bureau's order.
AGES_1980 = ["under_1", "1_2", "3_4", "5", "6", "7_9", "10_13", "14", "15", "16", "17",
             "18", "19", "20", "21", "22_24", "25_29", "30_34", "35_44", "45_54",
             "55_59", "60_61", "62_64", "65_74", "75_84", "85_over"]
AGES_1990 = ["under_1", "1_2", "3_4", "5", "6", "7_9", "10_11", "12_13", "14", "15", "16",
             "17", "18", "19", "20", "21", "22_24", "25_29", "30_34", "35_39", "40_44",
             "45_49", "50_54", "55_59", "60_61", "62_64", "65_69", "70_74", "75_79",
             "80_84", "85_over"]

ARCHIVE = {
    1980: {
        "url": "https://www2.census.gov/census_1980/stf1a/stf1axva.zip",
        "dictionary": "https://www2.census.gov/census_1980/1980_stf1_datadict.txt",
        "member": "STF1AXVA.TXT",
        # SUMRYLVL 11 is the whole county; state at 34, county FIPS at 40, name at 145.
        "county": lambda r: r[9:11] == "11" and r[33:35] == "51",
        "fips": lambda r: r[39:42],
        "name": lambda r: r[144:204].strip(),
        "tables": {
            "table7_race": (370, ["white", "black", "american_indian", "eskimo", "aleut",
                                  "japanese", "chinese", "filipino", "korean", "asian_indian",
                                  "vietnamese", "hawaiian", "guamanian", "samoan", "other"]),
            "table8_spanish_origin": (505, ["not_spanish_origin", "mexican", "puerto_rican",
                                            "cuban", "other_spanish"]),
            "table9_race_of_spanish_origin": (550, ["total", "white", "black",
                                                    "american_indian_eskimo_aleut_asian_pacific_islander",
                                                    "other"]),
            # Table 10 is "sex by age": 26 age groups for everyone, then the
            # same 26 for women - the dictionary's two strata are Total and
            # Female, and men are the difference. Saved as its two halves.
            # The voting-age population is everyone from "18 years" on, the
            # last fifteen cells of the first half, summed in
            # code/build/turnout.py.
            "table10_age": (595, AGES_1980),
            "table10_female_by_age": (829, AGES_1980),
        },
        # Each table's cells must account for the same population.
        "ties": [("table7_race", None), ("table8_spanish_origin", None),
                 ("table10_age", None)],
    },
    1990: {
        "url": "https://www2.census.gov/census_1990/STF1A_ASCII/90STF1A-VA.ZIP",
        "dictionary": None,
        "member": "STF1AxVA-F01",
        # Summary level 050 is the county; 0001 is the whole county rather than
        # one of its geographic components. County FIPS at 72.
        "county": lambda r: r[10:13] == "050" and r[24:28] == "0001",
        "fips": lambda r: r[71:74],
        # AREANAME runs to the "A!" that begins the area-measurement fields.
        "name": lambda r: r[191:257].strip(),
        "tables": {
            "race": (382, ["white", "black", "american_indian_eskimo_aleut",
                           "asian_pacific_islander", "other"]),
            # P11, age in 31 groups. Located the way the race tables were: the
            # one run of 31 cells in Arlington's record that sums to the county
            # total, whose first cells (1,878 under one year, 4,178 aged one and
            # two) are the shape of an age distribution. Voting age is the 19
            # cells from "18" on.
            "age": (796, AGES_1990),
            "hispanic_origin_by_race": (706, [
                "not_hispanic_white", "not_hispanic_black",
                "not_hispanic_american_indian_eskimo_aleut",
                "not_hispanic_asian_pacific_islander", "not_hispanic_other",
                "hispanic_white", "hispanic_black",
                "hispanic_american_indian_eskimo_aleut",
                "hispanic_asian_pacific_islander", "hispanic_other"]),
        },
        "total_at": 355,
        "ties": [("race", 355), ("hispanic_origin_by_race", 355), ("age", 355)],
    },
}
CELL = 9


def cells(record, begin, n):
    """n consecutive 9-character counts starting at a 1-based position."""
    out = []
    for i in range(n):
        start = begin - 1 + i * CELL
        out.append(int(record[start:start + CELL]))
    return out


def download(url):
    with urllib.request.urlopen(url, timeout=600) as r:
        return r.read()


def archive_year(year, spec):
    """Write one CSV per table for every Virginia county-level geography."""
    out_dir = RAW / str(year)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"  {year}: downloading {spec['url'].rsplit('/', 1)[-1]}")
    with zipfile.ZipFile(io.BytesIO(download(spec["url"]))) as z:
        text = z.read(spec["member"]).decode("latin-1")

    records = [r for r in text.splitlines() if spec["county"](r)]
    assert records, f"{year}: no county records matched"
    fips = [spec["fips"](r) for r in records]
    assert len(set(fips)) == len(fips), f"{year}: duplicate county FIPS"
    records.sort(key=spec["name"])

    # Every table must account for the same population, and where the file
    # states a total, for that total. A layout that has slipped by one cell
    # fails here rather than becoming a figure.
    for table, total_at in spec["ties"]:
        begin, names = spec["tables"][table]
        for r in records:
            got = sum(cells(r, begin, len(names)))
            want = cells(r, total_at, 1)[0] if total_at else None
            if want is not None and got != want:
                raise SystemExit(f"{year} {table}: {spec['name'](r)} sums to {got:,}, "
                                 f"file states {want:,} - check the layout")

    for table, (begin, names) in spec["tables"].items():
        out = out_dir / f"stf1a_{table}_virginia_counties.csv"
        with out.open("w") as fh:
            fh.write("name,state,county," + ",".join(names) + "\n")
            for r in records:
                vals = cells(r, begin, len(names))
                fh.write(f'"{spec["name"](r)}",51,{spec["fips"](r)},'
                         + ",".join(str(v) for v in vals) + "\n")
        arl = next(r for r in records if spec["fips"](r) == COUNTY)
        print(f"  {out.relative_to(ROOT)}  {len(records)} counties, {len(names)} cells"
              f"  (Arlington sums to {sum(cells(arl, begin, len(names))):,})")

    if spec["dictionary"]:
        dic = out_dir / spec["dictionary"].rsplit("/", 1)[-1]
        dic.write_bytes(download(spec["dictionary"]))
        print(f"  {dic.relative_to(ROOT)}  the Bureau's published record layout")


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
    # 2010's codes pad the table number to three digits: table P3 is P003001
    # and P10 is P010001.
    padded = "P" + table[1:].zfill(3) if table[1:].isdigit() else table
    return (code.startswith(table + "_")
            or (code.startswith(table) and code[len(table):].isdigit())
            or (code.startswith(padded) and code[len(padded):].isdigit()))


def first_value(head, table):
    return next(c for c in head if is_value(c, table))


def labels(year, dataset):
    """The Bureau's own label for every variable, so the saved file is readable."""
    return get(f"https://api.census.gov/data/{year}/{dataset}/variables.json")["variables"]


def main(years=None):
    """Everything, or only the censuses named on the command line:

        .venv/bin/python code/fetch/census.py 2000 2010 2020

    names the API years alone, which spares the 200 MB archive downloads
    when a table is added for the machine-readable censuses.
    """
    for year, spec in ARCHIVE.items():
        if not years or year in years:
            archive_year(year, spec)

    key = api_key()
    for year, (dataset, tables) in TABLES.items():
        if years and year not in years:
            continue
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
    import sys
    main({int(a) for a in sys.argv[1:]})
