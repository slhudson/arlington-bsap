"""The filed copy of an Ancestry index record, built from the row that cites it.

    .venv/bin/python code/sources/ancestry.py            # report what is missing
    .venv/bin/python code/sources/ancestry.py --apply
    .venv/bin/python code/sources/ancestry.py --apply --redo census1940detwiler

Every census row in data/transcribed/by_claude/members_census.csv cites a
record on Ancestry, and sources/documents keeps a copy of each beside the
sheet image, because a site behind a sign-in cannot be fetched again by
anyone reading this repository. Ancestry refuses an automated request, so
the copy is not the page itself: it is the record as the row already holds
it, the index listing in the row's `quote`, set on a plain page with the
record's url and the date it was read. The docstring of
code/clean/members_census.py says what the row holds. The page says on its
face that it is derived. It does not repeat Ancestry's statement that the
facts in a collection were found using artificial intelligence and may
contain errors, since the 1930 and 1940 record pages carry no such
statement. A record cited in the bib but kept out of the table (William
Duncan's 1910, while duncan-birth-year is open) has no row to build from,
and the script says so each time it runs.

The page is therefore derived, not fetched, which is why this script exists
rather than a filing step done by hand: the row is the only thing anyone
keys, and the filed copy follows from it. It writes a page only where the
bib entry names one that is not on disk, so running it twice changes
nothing; --redo rebuilds the named entries' pages, which is how a page whose
header has gone stale is corrected.

Without --apply it only reports.
"""
import argparse
import csv
import re
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

import archive

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
CENSUS = archive.ROOT / "data" / "transcribed" / "by_claude" / "members_census.csv"

# The provenance sentence every filed page carries, under the record's url.
# It says what the page is, because the page is derived and a reader who
# takes it for a copy of Ancestry's own would be misled. It does not repeat
# Ancestry's statement that the facts in the collection were found using
# artificial intelligence and may contain errors: the 1930 and 1940 census
# record pages carry no such statement.
HEADER = ('{howpublished}, read in the browser on {read}. This is not the page Ancestry '
          'serves: Ancestry refuses an automated request, so the record is set out here '
          "as the repository's own row holds it, field for field. The census sheet "
          'itself is filed beside this page as "{sheet}".')

PAGE = """<!doctype html><meta charset="utf-8"><style>
body {{ font: 11pt/1.45 Georgia, serif; margin: 2cm; }}
p.url {{ font-size: 9pt; word-break: break-all; }}
p.note {{ font-size: 9pt; color: #333; }}
h1 {{ font-size: 15pt; margin: 1.2em 0 0.6em; }}
li {{ margin-bottom: 0.15em; }}
</style>
<p class="url">{url}</p>
<p class="note">{note}</p>
<h1>{title}</h1>
<ul>{fields}</ul>
"""


def filed(annotation, folder):
    """The name the annotation says is filed under `folder`, or None. The
    annotation is wrapped across lines in the bib, so whitespace is collapsed
    before the name is read."""
    m = re.search(rf'"{folder}/[^"/]+/([^"]+)"', " ".join(annotation.split()))
    return m.group(1) if m else None


def month_name(urldate):
    """A bib urldate, 2026-09-26, as the filed pages write it."""
    y, m, d = urldate.split("-")
    months = ("January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December")
    return f"{int(d)} {months[int(m) - 1]} {y}"


def page(entry, sheet):
    """The plain page for one record, as html."""
    quote = entry["quote"].strip("“”")
    fields = "".join(f"<li>{escape(f.strip())}</li>" for f in quote.split(" · "))
    note = HEADER.format(howpublished=entry["howpublished"], sheet=sheet,
                         read=month_name(entry["urldate"]))
    return PAGE.format(url=escape(entry["url"]), note=escape(note),
                       title=escape(entry["title"]), fields=fields)


def to_pdf(html, out):
    """The html printed to `out` by headless Chrome."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "page.html"
        src.write_text(html)
        subprocess.run([str(CHROME), "--headless=new", "--disable-gpu",
                        "--no-pdf-header-footer", f"--print-to-pdf={out}", src.as_uri()],
                       capture_output=True, timeout=120)
    if not out.exists() or out.stat().st_size < 2000:
        sys.exit(f"headless Chrome printed nothing for {out.name}")


def records(bib, rows):
    """One dict per census row, with what its bib entry and its row give."""
    entries = {e["key"]: e for e in archive.entries(bib)}
    for row in rows:
        entry = entries.get(row["source"])
        if entry is None:
            sys.exit(f"{row['source']} is in members_census.csv and not in sources.bib")
        annotation = entry.get("annotation", "")
        sheet = filed(annotation, "census/US Census")
        if sheet is None:
            sys.exit(f"{row['source']}: the annotation names no sheet image")
        name = filed(annotation, "census/Ancestry")
        yield {"key": row["source"], "year": row["year"], "quote": row["quote"],
               "sheet": sheet, "name": name,
               "url": " ".join(entry["url"].split()),
               "title": " ".join(entry["title"].split()),
               "howpublished": " ".join(entry["howpublished"].split()),
               "urldate": " ".join(entry["urldate"].split())}


def expected_name(record):
    """The filename an entry should name: the title up to the collection,
    dropping the place that follows it, which the filename leaves to the
    folder."""
    short = re.match(r".*?Federal Census", record["title"])
    short = short.group(0) if short else record["title"]
    number = re.search(r"record (\d+)", record["howpublished"]).group(1)
    return f"Ancestry {record['year']} - {short} (record {number}).pdf"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write the pages")
    ap.add_argument("--redo", nargs="*", default=[], metavar="KEY",
                    help="rebuild these entries' pages even though they are on disk; "
                         "`all` rebuilds every one, which is how a change to the page "
                         "itself reaches the pages already filed")
    ap.add_argument("--documents", type=Path, default=archive.DOCUMENTS)
    ap.add_argument("--file", type=Path, default=CENSUS,
                    help="the census-shaped transcribed csv to file pages for "
                         "(default: members_census.csv)")
    a = ap.parse_args()

    if not a.documents.is_dir():
        sys.exit(f"the documents folder is not at {a.documents}")
    with a.file.open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["source"] not in ("", "unsourced")]
    bib = archive.BIB.read_text()

    unnamed, todo, named = [], [], set()
    for record in records(bib, rows):
        want = expected_name(record)
        if record["name"] is None:
            unnamed.append((record["key"], want))
            continue
        if record["name"] != want:
            sys.exit(f"{record['key']}: the annotation names {record['name']!r}, "
                     f"where the title and the record number give {want!r}")
        out = a.documents / "census" / "Ancestry" / record["year"] / want
        named.add(out)
        if not out.exists() or "all" in a.redo or record["key"] in a.redo:
            todo.append((record, out))

    # A page for a record kept out of the table - one cited while a question
    # about it is open - has no row to be built from, so this script leaves it
    # as it was filed. It says so rather than passing over it.
    loose = sorted(set((a.documents / "census" / "Ancestry").glob("*/*.pdf")) - named)
    for f in loose:
        print(f"{f.name}: filed, and no census row cites it; left as it was made")

    for key, want in unnamed:
        print(f"{key}: the annotation names no filed page; it would be "
              f'"census/Ancestry/.../{want}"')
    for record, out in todo:
        print(f"{record['key']}: {'rewrite' if out.exists() else 'write'} "
              f"census/Ancestry/{record['year']}/{out.name}")
        if a.apply:
            out.parent.mkdir(parents=True, exist_ok=True)
            to_pdf(page(record, record["sheet"]), out)
    if not unnamed and not todo:
        print(f"every census row's filed page is on disk ({len(named)})")
    elif not a.apply:
        print("--apply writes them")


if __name__ == "__main__":
    main()
