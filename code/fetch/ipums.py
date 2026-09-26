"""IPUMS USA -> data/raw/ipums/<year>/, one full-count extract per census.

Run by hand when a census is needed, output committed; the build never
touches the network (CLAUDE.md). Needs IPUMS_API_KEY in .env at the
repository root, which is gitignored, and ipumspy in the venv.

    .venv/bin/python code/fetch/ipums.py [1920]

A published table is its own citation, and the rest of data/raw/ holds
published tables. A microdata extract is not one: it is a query, so the
query is here in code and the answer is committed beside the codebook the
API delivers with it, which names the sample, the variables and the case
selection that produced it. Anyone can reread the file against that
codebook without an IPUMS account.

Why an extract at all: race below the county is published for 1870 alone,
so the districts at the end of the period can only be counted from the
manuscript schedules (docs/residents.md, `race-by-district-after-1870`).

Each census is one county's worth of people. Case selection is on the
state and the county, and the county is the ICPSR code, which is the
three-digit FIPS code with a zero added: Arlington County is 0130 in every
year, under the name it held at the time. Alexandria city is 5100 and is
therefore not in the extract, which is what the report wants - the Board
never governed the city.

The 1920 enumeration districts are numbered within a supervisor's
district rather than within the county, so SUPDIST comes with ENUMDIST;
together they name a district uniquely. MCDSTR, which would name the
magisterial district in words, is not available for 1920, so which
district an enumeration district sits in is a decision made in
code/clean/ against the 1920 district descriptions.

main() refuses to write a census whose head count is not close to the
published county total, which is the one number about the extract that is
known in advance.
"""
import gzip
import hashlib
import shutil
import tempfile
from pathlib import Path

from ipumspy import IpumsApiClient, MicrodataExtract
from ipumspy.api.extract import Variable

import paths

ROOT = paths.ROOT
RAW = paths.RAW / "ipums"

# Per census: the sample, the county, and the published county total the head
# count is checked against. The total is the one in data/clean/residents.csv,
# repeated here so the check does not reach across stages.
CENSUSES = {
    1920: {
        "sample": "us1920c",              # 1920 100% database
        "state": "51",                    # Virginia
        "county": "0130",                 # Arlington/Alexandria, ICPSR
        "county_in_year": "Alexandria County",
        "published_total": 16_040,
    },
}

# The geography the districts are read from, the person's race, sex and age,
# and the household. YEAR, SAMPLE, SERIAL, PERNUM and the weights come with
# every extract whether or not they are asked for.
VARIABLES = ["STATEFIP", "COUNTYICP", "ENUMDIST",
             "GQ", "SEX", "AGE", "RACE", "HISPAN"]

# A head count this far from the published total is refused: the wrong county,
# the wrong sample, or a truncated download, any of which would otherwise
# reach code/clean/ looking like a finding about the census.
TOLERANCE = 0.05


def api_key():
    env = ROOT / ".env"
    if not env.exists():
        raise SystemExit("no .env at the repository root; see this file's docstring")
    for line in env.read_text().splitlines():
        if line.startswith("IPUMS_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("IPUMS_API_KEY not found in .env; add it from your IPUMS account")


def request(year, spec):
    """The extract this census needs, as a query the API will accept."""
    return MicrodataExtract(
        collection="usa",
        samples=[spec["sample"]],
        description=(f"Arlington BSaP: {spec['county_in_year']}, Virginia, "
                     f"{year} full count, race by enumeration district"),
        data_format="csv",
        variables=[Variable(name="STATEFIP", case_selections={"general": [spec["state"]]}),
                   Variable(name="COUNTYICP", case_selections={"general": [spec["county"]]})]
        + [Variable(name=v) for v in VARIABLES if v not in ("STATEFIP", "COUNTYICP")],
    )


def delivered(client, extract, into: Path):
    """Submit, wait, and download into `into`; return the files as delivered."""
    client.submit_extract(extract)
    print(f"  extract {extract.collection}:{extract.extract_id} submitted; waiting")
    client.wait_for_extract(extract)
    client.download_extract(extract, download_dir=into)
    return sorted(p for p in into.rglob("*") if p.is_file())


def head_count(data: Path) -> int:
    """The people in the delivered data file, read as the codebook describes it."""
    opener = gzip.open if data.suffix == ".gz" else open
    with opener(data, "rt") as fh:
        return sum(1 for _ in fh) - 1          # less the header row


def census(client, year, spec):
    """Fetch one census, check the head count, and write data/raw/ipums/<year>/."""
    extract = request(year, spec)
    with tempfile.TemporaryDirectory() as tmp:
        files = delivered(client, extract, Path(tmp))
        data = next(p for p in files if ".csv" in p.suffixes or p.suffix == ".csv")

        people = head_count(data)
        published = spec["published_total"]
        if abs(people - published) > TOLERANCE * published:
            raise SystemExit(
                f"{year}: the extract holds {people:,} people and the published "
                f"{spec['county_in_year']} total is {published:,}, a difference of "
                f"{abs(people - published) / published:.1%}. Nothing written: check "
                f"the sample and the county in CENSUSES before trusting the file.")
        print(f"  {people:,} people against a published {published:,} "
              f"({(people - published) / published:+.2%})")

        out_dir = RAW / str(year)
        out_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            dest = out_dir / f.name
            shutil.copy2(f, dest)
            digest = hashlib.sha256(dest.read_bytes()).hexdigest()[:16]
            print(f"  {dest.relative_to(ROOT)}  {dest.stat().st_size // 1024:,}KB  {digest}")

        # The extract number is what an IPUMS account holder reopens the query
        # with, so it goes in data/contents.csv beside the checksum.
        print(f"  extract number: usa:{extract.extract_id}")


def main(years=None):
    client = IpumsApiClient(api_key())
    for year, spec in CENSUSES.items():
        if not years or year in years:
            print(f"{year}: {spec['county_in_year']}, Virginia, {spec['sample']}")
            census(client, year, spec)


if __name__ == "__main__":
    import sys
    main({int(a) for a in sys.argv[1:]})
