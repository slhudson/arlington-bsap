"""Where the fetch scripts put what they download, and where their keys are.

This one knows sources/ and nothing below it (CLAUDE.md). It also reads
.env, because an account is the other thing this stage needs and the only
stage that needs one.
"""
import gzip
import io
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCES = ROOT / "sources"
# The publishers' folders this stage reads, by the short names it uses.
CENSUS_BUREAU = SOURCES / "government" / "federal" / "us_census_bureau"
ARLINGTON_COUNTY = SOURCES / "government" / "local" / "arlington_county"
VA_ELECTIONS = SOURCES / "government" / "state" / "va_dept_of_elections"
IPUMS = SOURCES / "academic" / "ipums"
RCVA = SOURCES / "other" / "rcva"
MAGAZINE = SOURCES / "press" / "arlington_historical_magazine"
ENV = ROOT / ".env"


def write_text(path, text):
    """Save a fetched table or document. A path ending .gz is written
    gzip-compressed, with no name and no time in the header, so the same text
    gives the same bytes and the checksum in data/contents.csv holds across
    fetches. The published files the build reads and nobody edits are stored this
    way: Overleaf's 7MB cap counts text, and a compressed file is not text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode() if isinstance(text, str) else text
    if path.suffix == ".gz":
        buf = io.BytesIO()
        with gzip.GzipFile(filename="", mode="wb", fileobj=buf, compresslevel=9, mtime=0) as z:
            z.write(data)
        data = buf.getvalue()
    path.write_bytes(data)


def api_key(name):
    """The value of `name` in .env at the repository root. Only this stage
    asks: run.sh never touches the network (CLAUDE.md), so a missing key
    stops a fetch and nothing else."""
    if not ENV.exists():
        raise SystemExit(f"no .env at the repository root; see the docstring of the "
                         f"script you ran for the {name} it wants")
    for line in ENV.read_text().splitlines():
        if line.startswith(f"{name}="):
            return line.split("=", 1)[1].strip()
    raise SystemExit(f"{name} not found in .env; add it from your account with that service")
