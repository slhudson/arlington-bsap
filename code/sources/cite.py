"""A source the report cites but takes no numbers from: fetched, filed in
the Drive documents folder and entered in paper/sources.bib, in one step.

    .venv/bin/python code/sources/cite.py KEY URL --author "Hanover County" \\
        --title "Board of Supervisors" --date 2026 --note "Seven members, ..."
    .venv/bin/python code/sources/cite.py KEY URL ... --copy ~/Downloads/page.pdf

A web page is printed to PDF with headless Chrome; a file the url names
(.pdf, .xls, .xlsx, .csv) is saved as published. --copy takes a copy already
in hand instead, a page printed in Sally's own browser when a site refuses
an automated request. The copy is filed under the kind archive.kind()
assigns, named "<author> <year> - <title>", and the entry is appended to
sources.bib with the url, today's urldate, the note given and an annotation
naming the file, which is what code/tests.py and code/sources/archive.py check.

The note is the reader's: what the document says that the report relies on,
built from the document in hand (CLAUDE.md). This script does not read the
document for you; it does the filing, so that reading it is the only work.

It refuses to act, and says to print the page in Sally's browser and pass
--copy, when the site answers with an error or a challenge page or the
printed PDF carries no text; and refuses when the key or the filename is
already taken. It never bypasses a site's bot check.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from datetime import date
from pathlib import Path

import archive

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")
AS_PUBLISHED = (".pdf", ".xls", ".xlsx", ".csv", ".txt")
CHALLENGE = re.compile(r"Access Denied|Just a moment|Attention Required|cf-challenge|"
                       r"Pardon Our Interruption|verify you are human", re.I)


def fetch(url, out):
    """The url's body to `out`, or the reason it could not be had."""
    code = subprocess.run(["curl", "-sL", "-A", USER_AGENT, "--max-time", "60",
                           "-o", str(out), "-w", "%{http_code}", url],
                          capture_output=True, text=True).stdout
    if code != "200":
        return f"the site answered {code}"
    head = out.read_bytes()[:20000].decode("utf-8", "replace")
    if CHALLENGE.search(head):
        return "the site answered with a challenge page"
    return None


def print_page(url, out):
    """The page printed to PDF by headless Chrome, or the reason it could not be."""
    subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-agent={USER_AGENT}", f"--print-to-pdf={out}", url],
                   capture_output=True, text=True, timeout=120)
    if not out.exists() or out.stat().st_size < 2000:
        return "headless Chrome printed nothing"
    return text_problem(out)


def text_problem(pdf):
    """None if the PDF carries text, else why it is no copy."""
    import pymupdf
    text = " ".join(p.get_text() for p in pymupdf.open(pdf))
    if len(text.strip()) < 200:
        return "the printed PDF carries no text"
    if CHALLENGE.search(text[:3000]):
        return "the printed PDF is a challenge page"
    return None


def entry_text(a, filename, folder):
    today = date.today().isoformat()
    fields = [("author", "{" + a.author + "}"), ("title", a.title)]
    if a.organization:
        fields.append(("organization", a.organization))
    fields += [("date", a.date), ("url", a.url), ("urldate", today), ("note", a.note),
               ("annotation", f'Read {today}. Filed in Drive as "{folder}/{filename}", '
                              + ("saved as published" if a.url.lower().endswith(AS_PUBLISHED)
                                 else "a copy printed in Sally's own browser" if a.copy
                                 else "printed from the page")
                              + f" on {today}")]
    lines = [f"@{a.type}{{{a.key},"]
    for name, value in fields:
        # Wrapped as the file's other entries are, the continuation under the brace.
        wrapped = textwrap.wrap(value, 62) if name in ("note", "annotation") else [value]
        lines.append(f"  {name:<11} = {{{wrapped[0]}")
        lines += [" " * 17 + w for w in wrapped[1:]]
        lines[-1] += "},"
    return "\n".join(lines) + "\n}\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("key", help="the citekey, new to sources.bib")
    ap.add_argument("url")
    ap.add_argument("--author", required=True, help='as the bib prints it, e.g. "Hanover County"')
    ap.add_argument("--title", required=True)
    ap.add_argument("--date", required=True, help="YYYY or YYYY-MM-DD, the document's own date")
    ap.add_argument("--note", required=True, help="what the document says that the report relies on")
    ap.add_argument("--organization", default="")
    ap.add_argument("--type", default="online", help="the bib entry type (default online)")
    ap.add_argument("--copy", type=Path, help="a copy already in hand, filed instead of fetching")
    ap.add_argument("--documents", type=Path, default=archive.DOCUMENTS)
    a = ap.parse_args()

    bib = archive.BIB.read_text()
    if any(e["key"] == a.key for e in archive.entries(bib)):
        sys.exit(f"{a.key} is already in sources.bib")
    if not a.documents.is_dir():
        sys.exit(f"the Drive documents folder is not mounted at {a.documents}")

    entry = {"type": a.type, "key": a.key, "title": a.title,
             "organization": a.organization, "author": a.author}
    kind = archive.kind(entry)
    ext = a.copy.suffix.lower() if a.copy else next(
        (x for x in AS_PUBLISHED if a.url.lower().endswith(x)), ".pdf")
    year = a.date[:4]
    # A press copy is named for its outlet, not its byline; archive.canonical()
    # has the rule, so a copy is filed under the name the archive would give it.
    stem = archive.canonical(entry, re.sub(r"[/:]", "-", f"{a.author} {year} - {a.title}"))
    filename = stem + ext
    # Three kinds are filed in subfolders, so the folder is archive.subfolder()'s
    # and not the bare kind: a copy lands where the archive would put it, and
    # the annotation names that path.
    folder = archive.subfolder(entry, filename)
    target = a.documents / folder / filename
    if target.exists():
        sys.exit(f"{folder}/{filename} is already in the folder")

    with tempfile.TemporaryDirectory() as tmp:
        got = Path(tmp) / filename
        if a.copy:
            shutil.copy(a.copy, got)
            why = text_problem(got) if ext == ".pdf" else None
        elif ext != ".pdf" or a.url.lower().endswith(".pdf"):
            why = fetch(a.url, got) or (text_problem(got) if ext == ".pdf" else None)
        else:
            why = fetch(a.url, got) or print_page(a.url, got)
        if why:
            sys.exit(f"{a.key}: {why}. Open the page in Sally's own browser, print it "
                     f"to PDF, and run this again with --copy <that file>.")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(got, target)

    archive.BIB.write_text(bib.rstrip("\n") + "\n\n" + entry_text(a, filename, folder))
    print(f"{a.key}: filed as {folder}/{filename}; entry appended to sources.bib")


if __name__ == "__main__":
    main()
