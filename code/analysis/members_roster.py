r"""The roster the data appendix prints -> paper/members_roster.tex, and the subset
the body prints -> paper/members_roster_subsets.tex

One row per person who has served, in the order they first took a seat, with
the gender, race and birth year the report uses for each and a mark saying
what the value rests on. The paper \input{}s the files; they carry the rows
and, for the roster, the panels, while the heading's wording, the notes and the
type size stay in the paper where the other tables keep theirs.

    \roster{Name}{Served}{Seated By}{Born}{Gender}{Race and Ethnicity}

The marks, which the paper's note explains: \textsuperscript{c} a census
sheet, \textsuperscript{p} the press or a published profile,
\textsuperscript{a} assumed because no source says otherwise; a value that
rests on both a census sheet and the press carries both, c then p, as
\textsuperscript{c,\,p}, and is
never also marked assumed; a dash where no source gives the value. Rows fall
in groups by the decade of first seating, each under a bold heading;
\rosterk is a row the page may not break after, used so that no group leaves a
single row alone at the foot or head of a page.

The roster is printed as four panels, one era each, 3A through 3D in the
paper: \rosterpanel{A}{1870--1899} opens one and \rosterpanelend closes it.
The eras are fixed (1870-1899, 1900-1949, 1950-1999, 2000-present), each a
whole run of decades; a panel breaks only between decades, and longtable
carries it across as many pages as it needs. The subset is every member who
was a woman or a member of color, once each, in the same rows and columns
under a bold heading for the century they first took a seat, and the paper
\input{}s it into one table. The roster and the evidence behind each cell are
data/clean/members.csv.
"""
from typing import NamedTuple

import pandas as pd

import paths

MARK = {"census": "c", "press": "p", "assumed": "a"}
SEATED = {"election": "election", "appointment": "appointment",
          "special election": "special election", "unrecorded": "---"}


def basis(source) -> list:
    """The kinds of source a value rests on, in the fixed order census, press:
    census if any citekey begins with census, press if any other citekey is
    present. Assumed only when the column is exactly "assumed", so a value is
    never both assumed and sourced. Empty when nothing gives the value."""
    s = "" if pd.isna(source) else str(source).strip()
    if s in ("", "unsourced"):
        return []
    if s == "assumed":
        return ["assumed"]
    keys = [k.strip() for k in s.split(";") if k.strip()]
    kinds = []
    if any(k.startswith("census") for k in keys):
        kinds.append("census")
    if any(not k.startswith("census") for k in keys):
        kinds.append("press")
    return kinds


def marked(value, source) -> str:
    if pd.isna(value):
        return "---"
    v = str(int(value)) if isinstance(value, float) else str(value)
    marks = ",\\,".join(MARK[k] for k in basis(source))
    return v + (r"\textsuperscript{%s}" % marks if marks else "")



class Row(NamedTuple):
    """One person: the cells the table prints, the decade of first seating
    that groups the row, and the two raw values the subsets select on."""
    cells: tuple
    decade: int
    woman: bool
    of_color: bool


def rows(members: pd.DataFrame) -> list:
    """One Row per person, in the order of first seating. Years run from the
    first term's start to the last term's end, left open for a term that runs
    past the last year the seat table covers."""
    present = paths.read("members_by_year").year.max()
    out = []
    ordered = members.sort_values(["start_year", "start_month"], kind="stable")
    for name, g in ordered.groupby("name", sort=False):
        g = g.sort_values(["start_year", "start_month"])
        first, last = g.iloc[0], g.iloc[-1]
        years = f"{int(first.start_year)}--"
        if last.end_year < present:
            years += str(int(last.end_year))
        if years == f"{int(first.start_year)}--{int(first.start_year)}":
            years = str(int(first.start_year))  # one year of service prints once
        out.append(Row((name, years, SEATED[first.seated_by],
                        marked(first.birth_year, first.birth_year_source),
                        marked(first.gender, first.gender_source),
                        marked(first.race, first.race_source)),
                       int(first.start_year) // 10 * 10,
                       first.gender == "woman",
                       first.race != "White"))
    return out


# The four fixed eras a panel covers, in place of pagination by line count;
# the last is open-ended, to the most recent year the seat table covers.
ERAS = [(1870, 1899), (1900, 1949), (1950, 1999), (2000, None)]


def panels(table: list) -> list:
    """The decades, each a list of rows, grouped into the four fixed eras.
    An era with no decade in it is skipped. A panel never breaks inside a
    decade; longtable carries a panel across as many pages as it needs."""
    out = []
    decades = sorted({r.decade for r in table})
    for start, end in ERAS:
        group = [d for d in decades if d >= start and (end is None or d <= end)]
        if group:
            out.append((start, end, [(d, [r for r in table if r.decade == d]) for d in group]))
    return out


def esc(s: str) -> str:
    return s.replace("&", r"\&")


def line(r: Row, keep: bool = False) -> str:
    r"""One \roster line; \rosterk where the page may not break after it."""
    return (r"\rosterk" if keep else r"\roster") + "".join("{%s}" % esc(c) for c in r.cells)


# No blank line after the comments: inside the longtable a blank line is a
# \par at the start of the first cell, and the heading's \multicolumn then
# finds the cell already begun.
COMMENT = ("% Generated by code/analysis/members_roster.py from data/clean/members.csv.\n"
           "% Never edit by hand: bash run.sh rewrites it.\n")


def tex(table: list, present: int) -> str:
    r"""The roster as panels: \rosterpanel{letter}{years}, a bold \rosterdecade
    heading (1870s, 1880s, ...) above each decade's group, then \rosterpanelend.
    \rosterk (no page break after) goes on a group's first row and on the row
    before its last, so a break never strands one row."""
    out = [COMMENT]
    for k, (start, end, decade_groups) in enumerate(panels(table)):
        last = present if end is None else end
        out.append("\\rosterpanel{%s}{%d--%d}\n" % (chr(ord("A") + k), start, min(last, present)))
        for j, (d, group) in enumerate(decade_groups):
            out.append(("\\rosterheading{%ds}" if j == 0 else "\\rosterdecade{%ds}") % d + "\n")
            for i, r in enumerate(group):
                out.append(line(r, len(group) > 1 and i in (0, len(group) - 2)) + "\n")
        out.append("\\rosterpanelend\n")
    return "".join(out)


def subsets_tex(table: list) -> str:
    """Every member who was a woman or a member of color, once each, in the
    roster's order and columns, under the century they first took a seat."""
    out = [COMMENT]
    group = [r for r in table if r.woman or r.of_color]
    assert group, "no woman or member of color found"
    centuries = sorted({r.decade // 100 * 100 for r in group})
    for k, c in enumerate(centuries):
        heading = f"{c}s"
        out.append(("\\rosterheading{%s}" if k == 0 else "\\rosterdecade{%s}") % heading + "\n")
        out += [line(r) + "\n" for r in group if r.decade // 100 * 100 == c]
    return "".join(out)


if __name__ == "__main__":
    members = paths.read("members")
    table = rows(members)
    assert len(table) == members.name.nunique()
    present = int(paths.read("members_by_year").year.max())
    paths.MEMBERS_ROSTER.write_text(tex(table, present))
    paths.MEMBERS_ROSTER_SUBSETS.write_text(subsets_tex(table))
