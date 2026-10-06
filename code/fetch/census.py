"""Census -> data/raw/us_census_bureau/<year>/*.csv.gz, whole tables, 1980-2020.

Run by hand when a year is needed, output committed; the build never
touches the network (CLAUDE.md). Needs CENSUS_API_KEY in .env at the
repository root, which is gitignored.

    .venv/bin/python code/fetch/census.py [2000 2010 2020]

Whole tables, every Virginia county, one column per variable, as the Bureau
publishes them, with a data dictionary per census so the codes are readable.
2000-2020 come from the API, 2020 from two of its releases: the
redistricting file carries race and Hispanic origin but no age detail, so sex
by age comes from the Demographic and Housing Characteristics file. 1980 and
1990 come from the archived Summary Tape Files at www2.census.gov, since the
API holds no decennial data before 2000; they carry Hispanic (1980: Spanish) origin crossed with race, which is
what a consistent set of categories back to 1980 is built from. 1970 is not
here and should not be added: its Hispanic origin is a 5 percent sample the
Bureau does not hold comparable with later years.

1980's record layout is the Bureau's published dictionary, saved beside the
data. 1990's is PDF only, so its cell offsets were derived from the file;
main() checks on every fetch that each table's cells sum to the published
county total for all 136 Virginia geographies, and refuses to write if one
does not. The STF files are cut to Virginia county rows and the tables
named below - 200MB against an Overleaf budget of 100MB - which is the one
departure from saving a source untouched.
"""
import io
import json
import urllib.parse
import urllib.request
import zipfile

import paths

ROOT = paths.ROOT
RAW = paths.RAW / "us_census_bureau"
STATE, COUNTY = "51", "013"   # Virginia, Arlington County

# The tables to fetch for each census: race, race crossed with Hispanic
# origin, race for the population 18 and over (turnout's denominator; its
# first cell is the total), and sex by age. Table names differ by census, and
# a census may publish them across more than one release, so each year holds
# a list of (dataset, tables).
TABLES = {
    2000: [("dec/sf1", {"P003": "race", "P008": "hispanic_origin_by_race",
                        "P005": "race_18_and_over", "P012": "sex_by_age"})],
    2010: [("dec/sf1", {"P3": "race", "P5": "hispanic_origin_by_race",
                        "P10": "race_18_and_over", "P12": "sex_by_age"})],
    # 2020's redistricting file is deliberately minimal: it gives age only as
    # an 18-and-over total, so sex by age comes from the fuller Demographic
    # and Housing Characteristics release, published three years later.
    2020: [("dec/pl", {"P1": "race", "P2": "hispanic_origin_by_race",
                       "P3": "race_18_and_over"}),
           ("dec/dhc", {"P12": "sex_by_age"})],
}


# --- 1980 and 1990: the archived Summary Tape Files --------------------------
# Fixed-width ASCII, one file per state, every cell 9 characters. Positions
# are 1-based, as the Bureau's dictionaries write them. 1980's tables are
# from the published dictionary (Table 7 race, 8 Spanish origin, 9 the
# cross-tab); 1990's offsets were read off the file and are checked on
# every run.

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
            # Table 10, sex by age: 26 groups for everyone, then for women.
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
            # P11, age in 31 groups: the one run of 31 cells in Arlington's
            # record that sums to the county total.
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

    # A layout that has slipped by one cell fails here.
    for table, total_at in spec["ties"]:
        begin, names = spec["tables"][table]
        for r in records:
            got = sum(cells(r, begin, len(names)))
            want = cells(r, total_at, 1)[0] if total_at else None
            if want is not None and got != want:
                raise SystemExit(f"{year} {table}: {spec['name'](r)} sums to {got:,}, "
                                 f"file states {want:,} - check the layout")

    for table, (begin, names) in spec["tables"].items():
        out = out_dir / f"stf1a_{table}_virginia_counties.csv.gz"
        paths.write_text(out, "name,state,county," + ",".join(names) + "\n" + "".join(
            f'"{spec["name"](r)}",51,{spec["fips"](r)},'
            + ",".join(str(v) for v in cells(r, begin, len(names))) + "\n"
            for r in records))
        arl = next(r for r in records if spec["fips"](r) == COUNTY)
        print(f"  {out.relative_to(ROOT)}  {len(records)} counties, {len(names)} cells"
              f"  (Arlington sums to {sum(cells(arl, begin, len(names))):,})")

    if spec["dictionary"]:
        dic = out_dir / spec["dictionary"].rsplit("/", 1)[-1]
        dic.write_bytes(download(spec["dictionary"]))
        print(f"  {dic.relative_to(ROOT)}  the Bureau's published record layout")


def get(url):
    """Fetch and decode, surfacing the API's own error text rather than a stack trace."""
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Census API {e.code}: {e.read().decode(errors='replace')[:200].strip()}")


def is_value(code, table):
    """True for a data column of this table, false for annotation columns."""
    if code.endswith(("ERR", "EA", "MA", "NA")):
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
    """Every census, or only those named on the command line."""
    for year, spec in ARCHIVE.items():
        if not years or year in years:
            archive_year(year, spec)

    key = paths.api_key("CENSUS_API_KEY")
    for year, releases in TABLES.items():
        if years and year not in years:
            continue
        out_dir = RAW / str(year)
        out_dir.mkdir(parents=True, exist_ok=True)
        for dataset, tables in releases:
            meta = labels(year, dataset)
            wanted = set()

            for table, name in tables.items():
                url = f"https://api.census.gov/data/{year}/{dataset}?" + urllib.parse.urlencode({
                    "get": f"group({table})", "for": "county:*",
                    "in": f"state:{STATE}", "key": key})
                rows = get(url)
                head = rows[0]
                keep = [i for i, c in enumerate(head)
                        if c in ("NAME", "state", "county") or is_value(c, table)]
                wanted.update(head[i] for i in keep
                              if head[i] not in ("NAME", "state", "county"))

                out = out_dir / f"censusapi_{dataset.replace('/', '_')}_{table}_{name}_virginia_counties.csv.gz"
                paths.write_text(out, ",".join(head[i] for i in keep) + "\n" + "".join(
                    ",".join(f'"{r[i]}"' if "," in str(r[i]) else str(r[i]) for i in keep) + "\n"
                    for r in sorted(rows[1:], key=lambda r: r[head.index("NAME")])))
                arl = next(r for r in rows[1:] if r[head.index("NAME")].startswith("Arlington"))
                print(f"  {out.relative_to(ROOT)}  {len(rows)-1} counties, {len(keep)} columns"
                      f"  (Arlington total {int(arl[head.index(first_value(head, table))]):,})")

            dic = out_dir / f"censusapi_{dataset.replace('/', '_')}_variables.csv.gz"
            paths.write_text(dic, "variable,label\n" + "".join(
                f'{code},"{meta.get(code, {}).get("label", "").replace("!!", " / ").strip(" /")}"\n'
                for code in sorted(wanted)))
            print(f"  {dic.relative_to(ROOT)}  {len(wanted)} variables")


if __name__ == "__main__":
    import sys
    main({int(a) for a in sys.argv[1:]})
