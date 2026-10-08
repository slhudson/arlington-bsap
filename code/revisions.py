"""Who has touched each section of the report last, and whether a person has revised it.

    .venv/bin/python code/revisions.py     # each section file, its mark, a count

The first line of every section file under paper/ is a comment:

    % revised: CC 8 October 2026
    % revised: CC 8 October 2026; SH 9 October 2026

Initials and a date, one entry for each time someone rewrote the file, oldest
first, separated by "; ". Claude is an author and signs as CC (Sally, 8
October 2026); reading a section does not count. The wrapper's \\sectioninput
reads that same line and stamps the latest entry beside the section on the
contents page (a part's line, from the files it lists with \\partinput), so the file is the one place the record lives.

The sections are the files the wrapper pulls in with \\sectioninput, so a new
section is listed here by listing it there. A section whose subsections sit in
files of their own lists them as the optional argument, and its stamp is the
latest entry across them. A section has been revised by a person when every one
of its files holds an entry that is not CC; a copy of the report written to
paper/drafts/ on or after DRAFT_CUTOFF must have no file without one
(code/tests.py).
"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
WRAPPER = "arlington-bsap.tex"
DRAFT_CUTOFF = date(2026, 10, 30)  # the milestone copy at which every section has been revised (Sally, 7 October 2026)

MONTHS = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December")
REVISION = rf"[A-Z]{{2,3}} \d{{1,2}} (?:{MONTHS}) \d{{4}}"
MARK = re.compile(rf"^% revised: ({REVISION}(?:; {REVISION})*)$")
CLAUDE = "CC"  # Claude signs as an author; its entries do not count as a person's revision


def _calls(paper_dir):
    live = [re.sub(r"(?<!\\)%.*", "", line)
            for line in (paper_dir / WRAPPER).read_text().split("\n")]
    return [(m.group(1), [paper_dir / (n + ".tex") for n in (m.group(2) or "").split(",") if n],
             paper_dir / (m.group(3) + ".tex"))
            for m in re.finditer(r"\\(sectioninput|partinput)(?:\[([^\]]*)\])?\{([^}]+)\}",
                                 "\n".join(live))]


def sections(paper_dir=PAPER):
    """[(file, [its subsection files])] in the order the wrapper reads them.
    A subsection file is read by its own \\sectioninput line too, and is
    listed only under its section. The file that opens a part (\\partinput)
    is listed alone."""
    calls = _calls(paper_dir)
    subs = {f for kind, fs, _ in calls if kind == "sectioninput" for f in fs}
    return [(main, fs if kind == "sectioninput" else [])
            for kind, fs, main in calls if main not in subs]


def parts(paper_dir=PAPER):
    """[(opening file, every file the part's line stamps from)]."""
    return [(main, [main, *fs]) for kind, fs, main in _calls(paper_dir) if kind == "partinput"]


def section_files(paper_dir=PAPER):
    """Every file the wrapper reads as a section or part of one, in order."""
    return [f for main, parts in sections(paper_dir) for f in [main, *parts]]


def mark(path):
    """The text after "revised:" on the file's first line. Raises when the line
    is missing or malformed, so a section cannot go unmarked unnoticed."""
    lines = path.read_text().split("\n")
    m = MARK.match(lines[0]) if lines else None
    if not m:
        raise ValueError(f"{path.name}: the first line must read like '% revised: CC 8 October 2026', "
                         f"not {lines[0]!r}")
    return m.group(1)


def _key(revision):
    """A revision 'SH 7 October 2026' as (year, month, day), to find the latest."""
    who, day, month, year = revision.split()
    return int(year), MONTHS.split("|").index(month), int(day)


def entries(path):
    return mark(path).split("; ")


def label(files):
    """What the contents page stamps for a section made of these files: the
    latest entry across them, as 'SH 7 Oct'."""
    who, day, month, year = max((r for f in files for r in entries(f)), key=_key).split()
    return f"{who} {day} {month[:3]}"


def without_a_person(paper_dir=PAPER):
    """The files whose every entry is Claude's."""
    return [p for p in section_files(paper_dir)
            if all(r.split()[0] == CLAUDE for r in entries(p))]


def draft_copies(paper_dir=PAPER):
    """(date, path) for each dated copy in paper/drafts/."""
    out = []
    for p in sorted((paper_dir / "drafts").glob("*.pdf")):
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})$", p.stem)
        if not m:
            raise ValueError(f"{p.name}: a draft copy is named arlington-bsap-YYYY-MM-DD.pdf")
        out.append((date(*map(int, m.groups())), p))
    return out


def late_copies_with_unrevised_sections(paper_dir=PAPER):
    """Problems: a copy dated on or after the cutoff while a file has no entry but Claude's."""
    left = without_a_person(paper_dir)
    return [f"{p.name} is dated on or after {DRAFT_CUTOFF:%-d %B %Y} but "
            f"{len(left)} section file(s) have no entry from a person: "
            + ", ".join(f.name for f in left)
            for d, p in draft_copies(paper_dir) if d >= DRAFT_CUTOFF and left]


def main():
    files = section_files()
    width = max(len(str(f.relative_to(PAPER))) for f in files)
    for f in files:
        print(f"  {str(f.relative_to(PAPER)):<{width}}  {mark(f)}")
    stamps = [label([main, *parts]) for main, parts in sections()]
    left = len(without_a_person())
    for main, files_of_part in parts():
        print(f"  part line of {main.name}: {label(files_of_part)}")
    print(f"\n{len(files) - left} of {len(files)} files have an entry from a person, "
          f"{left} are Claude's alone ({len(stamps)} sections)")


if __name__ == "__main__":
    sys.exit(main())
