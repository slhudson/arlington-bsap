"""Assemble the archive the County receives, and its index.

    .venv/bin/python code/sources/archive.py            # dry run: report, move nothing
    .venv/bin/python code/sources/archive.py --apply    # file the folder, write index.md, build the zip

The archive is the repository at HEAD, the census scans data/contents.csv
marks in_git = no, and the Drive documents folder: a copy of every source the
report cites that no number is taken from. Its index is generated from
paper/sources.bib and data/contents.csv, never written by hand, so it cannot
drift from either.

The documents folder is filed by kind, one folder per kind (KINDS), and the
kind of an entry's copy is a rule on the bib entry, kind() below. A dry run
reads everything and prints what --apply would do: the layout, every move,
the files no entry names, the entries with a url and no filed copy. --apply
moves files within the folder and rewrites the filed name in the entry's
annotation to match, so the tests that check those names keep passing. It
deletes nothing: a file no entry names goes to unplaced/. It refuses to run
if a filed name the bib gives is not in the folder, or a scan is not on disk.
"""
import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIB = ROOT / "paper" / "sources.bib"
CONTENTS = ROOT / "data" / "contents.csv"

# sources/documents in the project's Drive, as this Mac mounts it. The link is
# in README.md; on another machine pass --documents.
DOCUMENTS = (Path.home() / "Library/CloudStorage/GoogleDrive-sally@rankedchoiceva.org"
             / ".shortcut-targets-by-id/1M4kZqG-XFRNQ9jele3PcD6mfZog7E5_Q/RCVa/research"
             / "Virginia/Arlington/2026 - Form of Government/team/sources/documents")

# Who indexes the census schedules. Each keys the names off a scan of the same
# NARA microfilm and serves them behind a sign-in, so what we file is a record
# this session read and set out on a page of its own, not the page they serve.
INDEXERS = ("ancestry", "familysearch")

# The makers a census copy's name can begin with: an indexer's record, or the
# Census Bureau's own sheet image. A census copy is filed by maker, then year.
COPIED_BY = ("Ancestry", "FamilySearch", "US Census")

KINDS = ("legal", "reports", "books", "bios", "campaign websites", "press",
         "obituaries", "census", "vital records")
UNPLACED = "unplaced"

# Web outlets whose pages are press when read online; see kind().
PAPERS = ("ARLnow", "InsideNoVa", "Sun Gazette", "Connection", "Washington Post", "Patch",
          "Blue Virginia",
          # papers of the period, read as scanned pages on Chronicling America
          "Alexandria Gazette", "Washington Bee", "Richmond Planet", "Evening Star",
          "National Republican", "The Washington Times",
          # read as scanned pages on Virginia Chronicle
          "Sun", "Commonwealth Monitor")

# Magazines are press, like papers. A historical society's magazine is scholarship: books.
MAGAZINES = ("Arlington Magazine",)
JOURNALS = ("Arlington Historical Magazine", "Florida State University Law Review")

# Biography pages by publisher, and campaign material by publisher or title.
BIO_ORG = re.compile(r"County Board Members|Arlington Historical Society|Center for Local History|Senate of Virginia|Library of Virginia|"
                     r"Dictionary of Virginia Biography|OutHistory", re.I)
BIO_TITLE = re.compile(r"Chair, Arlington County Board|\bbiography\b", re.I)
CAMPAIGN_ORG = re.compile(r"campaign|candidate|Vote Smart", re.I)

# A filed copy is a quoted filename in an entry's annotation, with or without
# the folder it sits in. Two things make it hard to pick out of the prose
# around it. A title carries quotation marks of its own - Gilbertson's county
# is the "Dark Continent" - so the quote that closes a name is not simply the
# next one; and the annotation quotes plenty of other things, so a name is
# recognised by the shape every one of them has, "<who> <year> - <title>.<ext>".
# Hence: find the end, then walk back to the nearest quote that leaves a name.
ENDS = re.compile(r'\.(?:pdf|jpe?g|png|xlsx?|csv|txt)"', re.I)
NAME = re.compile(r'^(?:[^/]+/)*.+ (?:\d{4}[a-z]?|n\.d\.) - .+\.\w+$', re.S)


# Titles and entry types that make a source law rather than a report.
LEGAL_TITLE = re.compile(r"\b(constitution|code|charter|statutes?|acts?|ordinances?|"
                         r"referendum|v\.)\b", re.I)
LEGAL_TYPE = ("legislation", "jurisdiction", "statute", "bill", "legal", "law")
BOOK_TYPE = ("book", "inbook", "incollection", "thesis", "phdthesis", "mastersthesis")


# A jurisdiction's own page about its governing body: what its council or board
# is called, who sits on it, how many seats it has. The peer set is keyed from
# these, one integer per locality.
# A governing body goes by many names - a council, a commission, a board of
# supervisors, and in Louisiana a police jury - and a jurisdiction may title the
# page about it "About Us".
ROSTER_TITLE = re.compile(r"\b(council|commissioners?|commission|supervisors|police jury|"
                          r"board members|elected officials|members of the board|"
                          r"about (our|us|the board))\b", re.I)
PUBLISHER_IS_A_JURISDICTION = re.compile(r"\b(County|Parish|Borough|Municipality|"
                                         r"Consolidated Government|Police Jury|"
                                         r"Metropolitan Government)\b|"
                                         r"^(City|Town|Village) of\b", re.I)


def roster_page(e):
    """Whether an entry is another locality's own page about its governing
    body. No copy of one is kept: what the report takes from it is how many
    voting seats the body has, which is keyed into data/transcribed/ with the
    url and the date read, and that keyed row is what a reviewer checks. A
    screen capture of a council's photographs attests nothing the keyed row
    does not, and the peer set runs to seventy of them. Arlington's own pages
    are the report's subject and are filed."""
    who = plain(e.get("organization") or e.get("author") or "")
    return (e["type"] == "online" and bool(ROSTER_TITLE.search(plain(e["title"])))
            and bool(PUBLISHER_IS_A_JURISDICTION.search(who))
            and "Arlington" not in who)


def kind(e):
    """Which folder an entry's copy is filed in. The first rule that fits."""
    who = (e.get("howpublished", "") + " " + e.get("organization", "")).lower()
    if any(i in who for i in INDEXERS):
        # What the record is, not who indexed it: the same indexers serve
        # marriages, draft cards, passenger lists and graves, and a census
        # folder is filed by census year, which those records do not have.
        return "census" if re.search(r"\bcensus\b", plain(e["title"]), re.I) else "vital records"
    if re.search(r"\bobituary\b|\bdies\b", e["title"], re.I):
        return "obituaries"
    if e["type"] == "article" and "pages" in e and "location" in e:
        return "press"                               # a printed page, scanned
    org = e.get("organization", "")
    if any(j in org or j in e.get("journaltitle", "") for j in JOURNALS):
        return "books"                                    # a historical society's magazine, however its name is fielded
    if any(m in org for m in MAGAZINES):
        return "press"                                    # a magazine's article
    if e["type"] == "article" and "journaltitle" in e and "pages" not in e:
        return "press"                               # a newspaper's article, read online
    if any(o in org for o in PAPERS):
        return "press"                               # a paper's page, read online
    if CAMPAIGN_ORG.search(org):
        return "campaign websites"                                # a candidate's site or questionnaire
    if BIO_ORG.search(org) or BIO_TITLE.search(e["title"]):
        return "bios"                                     # a biography page
    if e["type"] in BOOK_TYPE or (e["type"] == "article" and "journaltitle" in e):
        return "books"                 # scholarship, whatever law its title names
    if e["type"] in LEGAL_TYPE:
        return "legal"
    # A title-only match is for an entry typed something generic (@online,
    # @misc) whose title alone shows it is a legal text. @report is excluded:
    # a legislative commission's report about the Code - vacodecommission1997sd5
    # is "the Code of Virginia" in its title - is a report on the law, not the
    # law, and the type was a deliberate choice the title should not override.
    if e["type"] != "report" and LEGAL_TITLE.search(e["title"]):
        return "legal"
    return "reports"


# --- reading ------------------------------------------------------------------

# An outlet as a filename wants the paper, not how we reached it or where it
# circulates: "Sun Gazette, via InsideNoVa" and "Patch, Arlington, VA" are the
# Sun Gazette and Patch.
OUTLET_TAIL = re.compile(r",\s*(?:via\b.*|Connection Newspapers|Arlington,\s*VA)$", re.I)

# "<who> <year> - <title>", the shape every filed name has.
FILED_NAME = re.compile(r"^(.*?) (\d{4}[a-z]?) - (.*)$", re.S)


def outlet(e):
    """The paper or magazine that published a press entry. A leading article
    is dropped: the folder sorts by name, and a shelf of papers filed under
    "The" tells a reader nothing."""
    o = OUTLET_TAIL.sub("", plain(e.get("organization") or e.get("journaltitle") or "")).strip()
    return re.sub(r"^The\s+", "", o)


# A generational suffix is not the name a folder sorts under.
SUFFIX = re.compile(r"^(Jr|Sr|I{1,3}|IV|V)\.?$", re.I)


def surname(who):
    """The word a person is filed under: the last of their name that is not a
    generational suffix, so James B. Hunter III files under Hunter."""
    parts = [w for w in plain(who).split() if not SUFFIX.match(w)]
    return parts[-1] if parts else ""


# A title's colon becomes a hyphen in a filename, and a hyphen against the word
# before it and a space after reads as a typo: "Virginia- A History". A hyphen
# inside a word is left alone, so HH-6 and 1870-1960 keep theirs.
TIGHT_HYPHEN = re.compile(r"(?<=\w)- (?=\S)")


def spaced(name):
    """A filed name with no hyphen crowding the word before it."""
    return TIGHT_HYPHEN.sub(" - ", name)


def canonical(e, base):
    """What a filed copy is called.

    A press copy is named for its outlet and not its byline: the folder is
    read by someone looking for what a paper printed, who knows the Sun
    Gazette and not which of its reporters wrote this. A scan of a printed
    page was always named this way; this is what makes a page read online
    match it.

    An obituary is read the other way round - whether we hold one for Grotos -
    so it leads with the person it is for, from `subject`, which is the
    roster's name for them and not always the headline's, and carries its
    outlet at the end. Every other kind keeps its author's name."""
    base = spaced(base)
    m = FILED_NAME.match(base)
    if not m or not outlet(e):
        return base
    who, year, rest = m.groups()
    if kind(e) == "press":
        return f"{outlet(e)} {year} - {rest}"
    if kind(e) == "obituaries" and e.get("subject"):
        stem, dot, ext = rest.rpartition(".")
        if outlet(e) not in stem:
            # A scan already ends with the page it was printed on, and the
            # paper belongs in front of that rather than in parentheses of
            # its own: "(Arlington Daily, 3 November 1947, p. 1)".
            m2 = re.search(r"\(([^()]*)\)$", stem)
            stem = (stem[:m2.start()] + f"({outlet(e)}, {m2.group(1)})" if m2
                    else f"{stem} ({outlet(e)})")
        return f"{surname(e['subject'])} {year} - {stem}{dot}{ext}"
    return base


def entries(text):
    """Every entry in the bib as a dict of its fields, with type, key and the
    span of the whole entry in the text. Field values keep their braces
    balanced, so {{Arlington County}} and \\cite{x} read through."""
    out = []
    for m in re.finditer(r"^@(\w+)\{([^,\s]+)\s*,", text, re.M):
        end = re.compile(r"^\}", re.M).search(text, m.end()).end()
        body = text[m.end():end]
        if re.search(r"^@\w+\{", body, re.M):
            sys.exit(f"{m.group(2)}: no closing brace before the next entry")
        e = {"type": m.group(1).lower(), "key": m.group(2), "body": body}
        for f in re.finditer(r"^\s*(\w+)\s*=\s*\{", body, re.M):
            i, depth = f.end(), 1
            while depth:
                depth += {"{": 1, "}": -1}.get(body[i], 0)
                i += 1
            # A `type` field (a thesis's "PhD dissertation") is biblatex's
            # subtype; the entry type kind() reads is the one after the @.
            e["subtype" if f.group(1).lower() == "type" else f.group(1).lower()] = body[f.end():i - 1]
        out.append(e)
    return out


def tidy_name(s):
    """A filed name as the folder has it: whitespace collapsed, and no space
    around a folder's slash, which is a typo in the annotation rather than a
    folder whose name begins with one."""
    return re.sub(r"\s*/\s*", "/", " ".join(s.split()))


def _filed_spans(text):
    """Every filed name in a stretch of bib text, as (start, end, name) over
    the text between its quotes. One pass serves both reading the names and
    rewriting them, so the two cannot drift."""
    for m in ENDS.finditer(text):
        for q in reversed([q.start() for q in re.finditer('"', text[:m.start()])]):
            name = tidy_name(text[q + 1:m.end() - 1])
            if NAME.match(name):
                yield q + 1, m.end() - 1, name
                break


def filed(e):
    """The filenames an entry says are filed in Drive, whitespace collapsed. A
    space around a folder's slash is a typo in the annotation and not a folder
    whose name begins with one, so it is read through rather than turned into
    a copy the folder does not have."""
    return [n for _, _, n in _filed_spans(e.get("annotation", ""))]


def plain(s):
    """A bib value as text: braces off, LaTeX quotes and dashes rendered."""
    s = " ".join(s.split())
    s = re.sub(r"\\cite\{([^}]*)\}", r"\1", s)
    for a, b in (("\\&", "&"), ("---", "\u2014"), ("--", "\u2013"), ("``", '"'),
                 ("''", '"'), ("`", "'"), ("{", ""), ("}", ""), ("~", " ")):
        s = s.replace(a, b)
    return s


def cell(s):
    return plain(s).replace("|", "\\|")


def who(e):
    """The entry's author, or whoever stands in for one."""
    return cell(e.get("author") or e.get("editor") or e.get("organization") or "")


def row(e, last):
    return f"| {e['key']} | {who(e)} | {cell(e.get('date', 'n.d.'))} | {cell(e['title'])} | {last} |"


def raw_rows():
    return [r for r in csv.DictReader(CONTENTS.open()) if r["layer"] == "raw"]


def raw_paths(e, rows):
    """The data/raw/ files behind an entry: the rows whose source cites its
    key, the way data/contents.csv writes one, "... (citekey)"."""
    return [r["path"] for r in rows if f"({e['key']})" in r["source"]]


def sha16(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


CENSUS_COPY = re.compile(r"^(" + "|".join(COPIED_BY) + r") (\d{4}) - ")


# What a law is, from its title. A joint resolution proposing an amendment is
# the legislature acting, so it is read before the constitution it would amend.
# Whose law it is, from whoever enacted or decided it. Everything else here is
# Virginia's.
FEDERAL = re.compile(r"\bUnited States\b|\bU\.S\.\b|\bCongress\b|\bFederal\b", re.I)

STATUTE = re.compile(r"\bAn act\b|\bActs (?:of|and)\b|\bJoint Resolutions\b|\bCode of Virginia\b", re.I)
CONSTITUTION = re.compile(r"\bConstitution\b", re.I)
# A charter is the fourth kind of primary law the report reads: a locality's
# own instrument, read for the clauses Virginia's statute was drawn from. An
# act granting one is a statute, so this is tested last.
CHARTER = re.compile(r"\bcharter\b", re.I)


def legal_subfolder(e, base):
    """Which kind of law a filed copy is, and whose. The report turns on which
    sovereign acted - Virginia writes Arlington's form of government, Congress
    retroceded the county - so the folder says, and a copy whose kind or
    sovereign cannot be read stops the run rather than landing wherever it
    fell: this folder holds primary law only, so anything else in it is a
    filing mistake."""
    whose = "federal" if FEDERAL.search(plain(e.get("author") or e.get("organization") or "")) \
        else "state"
    if e["type"] == "jurisdiction" or " v. " in plain(e["title"]):
        return f"legal/{whose} courts"
    if STATUTE.search(plain(e["title"])):
        return f"legal/{whose} statutes"
    if CONSTITUTION.search(plain(e["title"])):
        return f"legal/{whose} constitutions"
    if CHARTER.search(plain(e["title"])):
        return f"legal/{whose} charters"
    # An act cited as "Act of <date>" has no "An act" or "Acts of" in its title,
    # so the sheet's own forms are read from the type: biblatex-chicago's
    # entrysubtype says a constitution, and any other legislation is a statute.
    if e.get("entrysubtype") == "constitution":
        return f"legal/{whose} constitutions"
    if e["type"] == "legislation":
        return f"legal/{whose} statutes"
    sys.exit(f'legal copy "{base}" is not an opinion, a statute, a constitution '
             f'or a charter: '
             f'file it under another kind, or name what it is in archive.legal_subfolder()')


def subfolder(e, base):
    """The folder a copy is filed in.

    Three kinds are split, because each is large enough that one flat folder
    stops answering a question. Census copies go by who made them, an
    indexer's record or the Census's own sheet image, then by census year.
    Press goes by outlet, so a paper's run is in one place. Legal goes by what
    the document is: an opinion, a statute, a constitution or a charter. Every
    other kind is one flat folder."""
    k = kind(e)
    if k == "census":
        m = CENSUS_COPY.match(base)
        if not m:
            sys.exit(f'census copy "{base}" does not start with one of '
                     f'{", ".join(COPIED_BY)} and a year')
        return f"census/{m.group(1)}/{m.group(2)}"
    if k == "press":
        return f"press/{outlet(e)}"
    if k == "legal":
        return legal_subfolder(e, base)
    return k


def folder_files(documents):
    """Every file in the documents folder, as a path relative to it. Dotfiles,
    the index and a zip are not documents."""
    return sorted(p.relative_to(documents).as_posix() for p in documents.rglob("*")
                  if p.is_file() and not p.name.startswith(".")
                  and p.name != "index.md" and p.suffix != ".zip")


# --- placing ------------------------------------------------------------------

def place(bib, documents):
    """Where every filed copy is and where it belongs.

    Returns (claims, missing): claims maps each file's current path in the
    folder to (target path, entry); missing lists filed names found nowhere in
    the folder. A name is looked for at the path the bib gives, then by its
    basename anywhere in the folder, so a file dropped at the top or left in
    an old subfolder is found and moved rather than reported missing."""
    present = folder_files(documents)
    by_name = {}
    for p in present:
        by_name.setdefault(Path(p).name, []).append(p)
    claims, missing = {}, []
    for e in bib:
        for name in filed(e):
            base = Path(name).name
            if name in present:
                current = name
            elif len(by_name.get(base, [])) == 1:
                current = by_name[base][0]
            elif len(by_name.get(base, [])) > 1:
                sys.exit(f"{e['key']}: \"{base}\" is in the folder more than once: "
                         f"{', '.join(by_name[base])}")
            else:
                missing.append((e["key"], name))
                continue
            base = canonical(e, base)
            target = f"{subfolder(e, base)}/{base}"
            if current in claims and claims[current][0] != target:
                sys.exit(f"\"{current}\" is claimed by {claims[current][1]['key']} as "
                         f"{claims[current][0]} and by {e['key']} as {target}")
            claims[current] = (target, e)
    return claims, missing


def rewrite_bib(text, bib, claims):
    """The bib text with every filed name that moved replaced by its new
    path. Only the quoted name changes; the rest of the file is untouched."""
    new = {}
    for e in bib:
        for name in filed(e):
            for current, (target, owner) in claims.items():
                if owner is e and Path(current).name == Path(name).name and name != target:
                    new[name] = target

    out, last = [], 0
    for a, b, name in _filed_spans(text):
        if name in new:
            out.append(text[last:a])
            out.append(new[name])
            last = b
    out.append(text[last:])
    return "".join(out), len(new)


def append_annotation(text, keys, phrase):
    """The bib with `phrase` added to each named entry's annotation, where a
    tool has changed the filed copy and the entry should say so. Returns the
    new text and the keys it could not place, which are the annotations whose
    last sentence is not the one about the copy."""
    missed = []
    for key in keys:
        m = re.search(r"^@\w+\{" + re.escape(key) + r",", text, re.M)
        end = re.compile(r"^\}", re.M).search(text, m.end()).start()
        a = re.search(r"^(\s*annotation\s*=\s*\{)(.*?)(\},?\s*)$", text[m.end():end],
                      re.S | re.M)
        if not a or phrase.strip(", ") in a.group(2):
            if not a:
                missed.append(key)
            continue
        body = a.group(2).rstrip()
        trail = a.group(2)[len(body):]
        if not re.search(r"\d{4}$|article$|removed$|dpi$", body):
            missed.append(key)
            continue
        i = m.end() + a.start(2)
        text = text[:i] + body + phrase + trail + text[i + len(a.group(2)):]
    return text, missed


# --- the index ------------------------------------------------------------------

def index_text(bib, claims, rows, unplaced, commit):
    by_entry = {}
    for current, (target, e) in claims.items():
        by_entry.setdefault(e["key"], []).append(target)
    scans = [r for r in rows if r["in_git"] == "no"]
    out = [
        "# Arlington BSaP: sources archive",
        "",
        f"Written by `code/sources/archive.py` on {date.today().isoformat()} from commit {commit} of the "
        "`slhudson/arlington-bsap` repository. Generated: rerun the script rather than edit it.",
        "",
        "- `repository/` is the repository at that commit. `bash run.sh` rebuilds every "
        "figure from it; its `README.md` says how. The scans it fetches on demand rather "
        f"than commits ({len(scans)} files under `data/raw/us_census_bureau/`) are included "
        "at their paths.",
        "- `documents/` holds a copy of every source the report cites that no number is "
        "taken from, filed by kind. The first column of each table is the entry's key in "
        "`repository/paper/sources.bib`; the entry's `annotation` says what the copy is "
        "and when it was taken.",
        "",
        "## Documents",
        "",
        "One folder per kind. Which folder a copy belongs in is a rule on its bib entry, "
        "`kind()` in `code/sources/archive.py`; three kinds are split further, by `subfolder()`: "
        "census by who made the copy, an indexer's record or the Census's own sheet image, then "
        "by census year; press by outlet, so a paper's run is in one place; and legal by what the "
        "document is, an opinion, a statute, a constitution or a charter. The kinds: "
        "census: an index record and the Census sheet image; "
        "press: a newspaper's or magazine's page or article, printed or read online; obituaries; "
        "bios: biography pages; campaign websites: candidate sites, "
        "questionnaires and campaign material; legal: constitutions, statutes and the like; "
        "books: scholarship, including a historical society's magazine; reports: everything else.",
        "",
        "A copy is named `<who> <year> - <title>`. A press copy leads with the paper that "
        "printed it rather than the reporter who wrote it, and an obituary with the person it "
        "is for, followed by the paper; everything else leads with its author. "
        "`canonical()` in the same script has the rules.",
    ]
    for k in KINDS:
        held = sorted((sorted(files)[0], e) for e in bib
                      for key, files in [(e["key"], by_entry.get(e["key"], []))]
                      if files and files[0].startswith(k + "/"))
        out += ["", f"### {k} ({len(held)} {'entry' if len(held) == 1 else 'entries'})", ""]
        if not held:
            out.append("(none)")
            continue
        out += ["| key | author | date | title | file |", "|---|---|---|---|---|"]
        for _, e in held:
            out.append(row(e, "<br>".join(f"`{Path(f).name}`" for f in sorted(by_entry[e["key"]]))))
    out += ["", "## Sources held in the repository", "",
            "Entries whose copy is under `repository/data/raw/`, because a number is taken "
            "from it.", "",
            "| key | author | date | title | in data/raw/ |", "|---|---|---|---|---|"]
    for e in bib:
        paths = raw_paths(e, rows)
        if paths:
            out.append(row(e, "<br>".join(f"`{p}`" for p in paths)))
    out += ["", "Every file under `data/raw/`, from `data/contents.csv`: what it is, "
            "who published it, and the first sixteen hex digits of its SHA-256.", "",
            "| path | source | sha256 | committed |", "|---|---|---|---|"]
    for r in rows:
        out.append(f"| `{r['path']}` | {cell(r['source'])} | `{r['sha256']}` | "
                   f"{'yes' if r['in_git'] == 'yes' else 'no, fetched on demand; in this archive'} |")
    out += ["", "## Sources with no copy held", "",
            "Cited, but neither filed in `documents/` nor held under `data/raw/`; the "
            "entry's `annotation` says why.", "",
            "| key | author | date | title | url |", "|---|---|---|---|---|"]
    for e in bib:
        if e["key"] not in by_entry and not raw_paths(e, rows):
            out.append(row(e, plain(e["url"]) if "url" in e else ""))
    if unplaced:
        out += ["", f"## {UNPLACED}", "",
                "Files in the folder that no entry names. Each is either a source not yet "
                "entered in the bib or a stray; nothing is deleted.", ""]
        out += [f"- `{Path(p).name}`" for p in unplaced]
    return "\n".join(out) + "\n"


# --- the zip --------------------------------------------------------------------

def build_zip(zip_path, documents, index, scans):
    prefix = "arlington-bsap/"
    tmp = zip_path.with_suffix(".zip.part")
    subprocess.run(["git", "archive", "--format=zip", f"--prefix={prefix}repository/",
                    "-o", str(tmp), "HEAD"], cwd=ROOT, check=True)
    with zipfile.ZipFile(tmp, "a", zipfile.ZIP_DEFLATED) as z:
        for p in scans:
            z.write(ROOT / p, f"{prefix}repository/{p}")
        for rel in folder_files(documents):
            z.write(documents / rel, f"{prefix}documents/{rel}")
        z.writestr(f"{prefix}documents/index.md", index)
        z.writestr(f"{prefix}index.md", index)
    tmp.replace(zip_path)


# --- main -----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("--apply", action="store_true",
                    help="move files, rewrite the bib, write index.md and build the zip")
    ap.add_argument("--documents", type=Path, default=DOCUMENTS, help="the Drive documents folder")
    ap.add_argument("--index", type=Path,
                    help="where to write index.md (default: the top of the documents folder; "
                         "a dry run writes it only if this is given)")
    ap.add_argument("--zip", type=Path, help="the zip to build (default: beside the documents folder)")
    a = ap.parse_args()
    documents = a.documents
    if not documents.is_dir():
        sys.exit(f"documents folder not found: {documents}")
    zip_path = a.zip or documents.parent / "arlington-bsap-archive.zip"
    would = "" if a.apply else "would "

    text = BIB.read_text()
    bib = entries(text)
    rows = raw_rows()
    claims, missing = place(bib, documents)
    present = folder_files(documents)

    # Everything that stops the run is checked before anything moves. A dry
    # run reports each blocker and carries on, so the rest can be read, and
    # ends nonzero.
    blockers = []
    if missing:
        print(f"named in the bib, not in the folder ({len(missing)}):")
        for key, name in missing:
            print(f"  {key}: \"{name}\"")
        blockers.append(f"{len(missing)} filed cop{'y' if len(missing) == 1 else 'ies'} not found: "
                        "file each in Drive, or correct the annotation")
    scans = [r["path"] for r in rows if r["in_git"] == "no"]
    absent = [p for p in scans if not (ROOT / p).exists()]
    if absent:
        print(f"scans not on disk ({len(absent)} of {len(scans)}):")
        for p in absent:
            print(f"  {p}")
        blockers.append("scans not on disk: .venv/bin/python code/fetch/census_volumes.py fetches them")
    moved = [p for p in scans if p not in absent
             and sha16(ROOT / p) != next(r["sha256"] for r in rows if r["path"] == p)]
    if moved:
        print("scans whose checksum does not match data/contents.csv:")
        for p in moved:
            print(f"  {p}")
        blockers.append("a scan's checksum has moved: refetch it")
    if blockers and a.apply:
        sys.exit("--apply refused:\n  " + "\n  ".join(blockers))

    print(f"documents: {documents}")
    print(f"  {len(present)} files; {len(bib)} bib entries, {len(claims)} filed copies")
    print("layout, by kind:")
    for k in KINDS:
        n = sum(1 for t, _ in claims.values() if t.startswith(k + "/"))
        print(f"  {k:16} {n:3}")

    moves = sorted((c, t) for c, (t, _) in claims.items() if c != t)
    unplaced = [p for p in present if p not in claims]
    to_unplace = [p for p in unplaced if not p.startswith(UNPLACED + "/")]
    for p in to_unplace:
        target = f"{UNPLACED}/{Path(p).name}"
        if (documents / target).exists() or target in dict(moves):
            sys.exit(f"cannot place \"{p}\": {UNPLACED}/ already holds a file of that name")
        moves.append((p, target))

    print(f"moves ({len(moves)}"
          + (f", of which {len(to_unplace)} to {UNPLACED}/ because no entry names them" if to_unplace else "")
          + "):" if moves else "moves: none, every file is where the bib says")
    for current, target in moves:
        print(f"  {current}\n    -> {target}")
        if a.apply:
            (documents / target).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(documents / current, documents / target)
    for d in sorted({Path(c).parent for c, _ in moves if Path(c).parent != Path(".")}, reverse=True):
        left = [p for p in present if p.startswith(f"{d}/") and p not in dict(moves)]
        filled = any(t.startswith(f"{d}/") for _, t in moves)
        if not left and not filled:
            print(f"{would}remove the empty folder {d}/")
            if a.apply and not any((documents / d).iterdir()):
                (documents / d).rmdir()

    new_text, changed = rewrite_bib(text, bib, claims)
    if changed:
        print(f"bib: {would}rewrite {changed} filed names to their new paths")
        if a.apply:
            BIB.write_text(new_text)

    no_copy = [e for e in bib if "url" in e and not filed(e) and not raw_paths(e, rows)]
    print(f"entries with a url and no filed copy ({len(no_copy)}):" if no_copy
          else "entries with a url and no filed copy: none")
    for e in no_copy:
        print(f"  {e['key']}: {plain(e['url'])}")

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.strip()
    unplaced_after = sorted(t for _, t in moves if t.startswith(UNPLACED + "/")) \
        + [p for p in unplaced if p.startswith(UNPLACED + "/")]
    index = index_text(bib, claims, rows, unplaced_after, commit)
    index_path = a.index or documents / "index.md"
    if a.apply or a.index:
        index_path.write_text(index)
        print(f"index: wrote {index_path}")
    else:
        print(f"index: would write {index_path} ({len(index.splitlines())} lines)")

    renamed = dict(moves) if a.apply else {}   # `present` names the files as they were before --apply moved them
    size = sum((ROOT / p).stat().st_size for p in scans if p not in absent) \
        + sum((documents / renamed.get(p, p)).stat().st_size for p in present)
    if not a.apply:
        print(f"zip: would build {zip_path} (documents and scans {size >> 20}MB before the repository)")
    elif changed or dirty:
        print("zip: not built - the working tree has uncommitted changes"
              + (" (the bib was just rewritten)" if changed else "")
              + "; commit, then rerun --apply")
    else:
        build_zip(zip_path, documents, index, scans)
        print(f"zip: built {zip_path} ({zip_path.stat().st_size >> 20}MB) from commit {commit}")
    if blockers:
        sys.exit("--apply will refuse until:\n  " + "\n  ".join(blockers))


if __name__ == "__main__":
    main()
