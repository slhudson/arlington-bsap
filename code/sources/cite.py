"""A source the report cites but takes no numbers from: fetched, filed in
sources/ and entered in paper/bib/sources.bib, in one step.

    .venv/bin/python code/sources/cite.py KEY URL --author "Hanover County" \\
        --title "Board of Supervisors" --date 2026 --note "Seven members, ..."
    .venv/bin/python code/sources/cite.py KEY URL ... --copy ~/Downloads/page.pdf

A web page is printed to PDF with headless Chrome; a file the url names
(.pdf, .xls, .xlsx, .csv) is saved as published. --copy takes a copy already
in hand instead, a page printed in Sally's own browser when a site refuses
an automated request. The copy is filed where archive.shelf()
puts it, named "<author> <year> - <title>", and the entry is appended to
sources.bib with the url, today's urldate and an annotation naming the file,
which is what code/tests.py and code/sources/archive.py check.

The entry is written as the bibliography's style sheet (docs/repository.md) has
it, so it passes code/tests.py when the paper cites it: a headline-style title,
a newspaper's masthead without its leading The, no author on an unsigned piece or
a law (--author is the sovereign for a law; --field adds a case's reporter or an
act's chapter), and the sortname or sorttitle that files it.

--note is the reader's: what the document says that the report relies on,
built from the document in hand (CLAUDE.md). It goes into the annotation,
which the paper does not print. biblatex prints a `note` field in the footnote
of every citation, so --note must not land there; --cite-note is the one
for what a footnote should carry, a reporter citation or a volume and number.
This script does not read the document for you; it does the filing, so that
reading it is the only work.

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


LAW = ("jurisdiction", "legislation")


def sheet_fields(a):
    """The entry's fields as the style sheet in docs/repository.md has them:
    the title in headline style with year ranges in en dashes, a newspaper's
    masthead without its leading The, an unsigned piece with no author and a
    braced sortname (the paper or outlet is not its author), a law with no
    author and its sovereign in organization, and an article read online with
    no page marked magazine-style so its footnote does not end in a comma."""
    law = a.type in LAW
    title = re.sub(r"(\d{4})-(\d{2,4})", r"\1--\2", a.title)
    if not law:
        title = archive.headline_case(title)
    fields = []
    if a.author and not law:
        fields.append(("author", "{" + a.author + "}"))
    fields.append(("title", title))
    organization = a.organization or (a.author if law else "")
    journal = re.sub(r"^The\s+", "", a.journal)
    if organization:
        fields.append(("organization", organization))
    if journal:
        fields.append(("journaltitle", journal))
    if a.location:
        fields.append(("location", a.location))
    fields.append(("date", a.date))
    if a.pages:
        fields.append(("pages", a.pages))
    for extra in a.field:
        name, _, value = extra.partition("=")
        fields.append((name.strip(), value.strip()))
    if a.type == "jurisdiction":
        fields.append(("sortname", "{" + title.replace("\\ ", " ") + "}"))
    if a.type == "legislation":
        fields.append(("sorttitle", a.date))
    if not a.author and not law and (journal or organization):
        fields.append(("sortname", "{" + (journal or organization) + "}"))
    if journal and not a.pages and a.url:
        fields.append(("entrysubtype", "magazine"))
    return fields


def entry_text(a, filename, folder):
    today = date.today().isoformat()
    fields = sheet_fields(a) + [("url", a.url), ("urldate", today)]
    if a.cite_note:
        fields.append(("note", a.cite_note))     # prints in the footnote
    if a.journal and not a.pages:
        a.note = "The copy gives no page. " + a.note
    fields += [("annotation", f'{a.note.rstrip(".")}. Read {today}. Filed in sources as "{folder}/{filename}", '
                              + (a.how if a.how
                                 else "saved as published" if a.url.lower().endswith(AS_PUBLISHED)
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
    ap.add_argument("--author", default="", help='as the bib prints it, e.g. "Hanover County"; '
                    'omit for an unsigned piece, which files under its paper or outlet, and for a law, '
                    'where it is the sovereign')
    ap.add_argument("--pages", default="", help="the page as printed, e.g. 3 or A-26")
    ap.add_argument("--field", action="append", default=[], metavar="NAME=VALUE",
                    help="another bib field, repeatable: a case's journaltitle, volume and pages, "
                         "an act's titleaddon, shortjournal and volume")
    ap.add_argument("--title", required=True)
    ap.add_argument("--date", required=True, help="YYYY or YYYY-MM-DD, the document's own date")
    ap.add_argument("--note", required=True,
                    help="what the document says that the report relies on; goes in the annotation, "
                         "which the paper does not print")
    ap.add_argument("--cite-note", default="",
                    help="facts a footnote should carry, such as a reporter citation; printed in "
                         "the footnote, so keep it to a few words")
    ap.add_argument("--organization", default="")
    ap.add_argument("--journal", default="", help="a newspaper's name: makes the entry an article filed under press")
    ap.add_argument("--location", default="", help="where the newspaper is published, e.g. \"Alexandria, Va.\"")
    ap.add_argument("--how", default="", help="how the copy was had, replacing the default phrase in the annotation")
    ap.add_argument("--type", default="online", help="the bib entry type (default online)")
    ap.add_argument("--copy", type=Path, help="a copy already in hand, filed instead of fetching")
    ap.add_argument("--sources", type=Path, default=archive.SOURCES)
    a = ap.parse_args()

    bib = archive.BIB.read_text()
    if any(e["key"] == a.key for e in archive.entries(bib)):
        sys.exit(f"{a.key} is already in sources.bib")
    if not a.sources.is_dir():
        sys.exit(f"the sources folder is not at {a.sources}")

    if not (a.author or a.organization or a.journal):
        sys.exit("give --author, or --organization or --journal for an unsigned piece")
    entry = {"type": a.type, "key": a.key, "title": a.title,
             "organization": a.organization, "author": a.author}
    if a.journal:
        entry["journaltitle"] = a.journal
    if archive.roster_page(entry):
        sys.exit(
            f"{a.key} is another locality's own page about its governing body, and no copy of "
            f"one is kept.\n"
            f"  Key the body's voting seats into data/transcribed/by_claude/county_boards.csv, "
            f"with this url and\n"
            f"  the date you read it, and enter the source with no copy: end the annotation\n"
            f'  "The count is keyed into data/transcribed/by_claude/county_boards.csv; no copy '
            f'is kept".\n'
            f"  archive.roster_page() has the rule; the thirteen Virginia counties are the model.")
    ext = a.copy.suffix.lower() if a.copy else next(
        (x for x in AS_PUBLISHED if a.url.lower().endswith(x)), ".pdf")
    year = a.date[:4]
    # A press copy is named for its outlet, not its byline; archive.canonical()
    # has the rule, so a copy is filed under the name the archive would give it.
    stem = archive.canonical(entry, re.sub(r"[/:]", "-", f"{a.author or a.organization or a.journal} {year} - {a.title}"))
    filename = stem + ext
    # A copy lands where archive.shelf() puts it, and the annotation names that path.
    folder = archive.shelf(entry, filename)
    target = a.sources / folder / filename
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
