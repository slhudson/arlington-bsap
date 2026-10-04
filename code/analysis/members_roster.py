r"""The roster the data appendix prints -> paper/members_roster.tex, and the two subsets
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

The roster is printed as panels, one page each, 2A, 2B and 2C in the paper:
\rosterpanel{A}{1870--1919} opens one and \rosterpanelend closes it, and a panel
breaks only between decades, so a page is filled with whole decades until the
next would not fit (PANEL_LINES). The subsets are the women and the members of
color, in the same rows and columns under a bold heading each, and the paper
\input{}s them into one table. The roster and the evidence behind each cell are
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


# A page holds this many lines of a panel: a row is one, a decade's heading
# and the gap above it 1.4, with the panel's title and notes already taken out.
PANEL_LINES = 49
HEADING_LINES = 1.4


def panels(table: list) -> list:
    """The decades, each a list of rows, packed in order into pages: a decade
    joins the page it follows unless that would pass PANEL_LINES, and then it
    opens the next. A panel never breaks inside a decade."""
    out, used = [], 0.0
    for d in sorted({r.decade for r in table}):
        group = [r for r in table if r.decade == d]
        size = len(group) + HEADING_LINES
        if not out or used + size > PANEL_LINES:
            out.append([])
            used = 0.0
        out[-1].append((d, group))
        used += size
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
    for k, panel in enumerate(panels(table)):
        first, last = panel[0][0], panel[-1][0] + 9
        out.append("\\rosterpanel{%s}{%d--%d}\n" % (chr(ord("A") + k), first, min(last, present)))
        for j, (d, group) in enumerate(panel):
            out.append(("\\rosterheading{%ds}" if j == 0 else "\\rosterdecade{%ds}") % d + "\n")
            for i, r in enumerate(group):
                out.append(line(r, len(group) > 1 and i in (0, len(group) - 2)) + "\n")
        out.append("\\rosterpanelend\n")
    return "".join(out)


def subsets_tex(table: list) -> str:
    """The women and then the members of color, in the roster's order and
    columns, each under a bold panel heading."""
    out = [COMMENT]
    for k, (title, pick) in enumerate((("Panel A. Women", lambda r: r.woman),
                                       ("Panel B. Members of Color", lambda r: r.of_color))):
        group = [r for r in table if pick(r)]
        assert group, f"{title} is empty"
        out.append(("\\rosterheading{%s}" if k == 0 else "\\rosterdecade{%s}") % title + "\n")
        out += [line(r) + "\n" for r in group]
    return "".join(out)


if __name__ == "__main__":
    members = paths.read("members")
    table = rows(members)
    assert len(table) == members.name.nunique()
    present = int(paths.read("members_by_year").year.max())
    paths.MEMBERS_ROSTER.write_text(tex(table, present))
    paths.MEMBERS_ROSTER_SUBSETS.write_text(subsets_tex(table))
