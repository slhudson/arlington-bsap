r"""Two complete tables under paper/tables/, each a title line, a table
environment, the rows and the notes, included by one \input line each:
paper/tables/members_roster.tex (the data appendix) and
paper/tables/members_subsets.tex (the body).

One row per person who has served, in the order they first took a seat, with
the gender, race and birth year the report uses for each and a mark saying
what the value rests on, and an asterisk after the name of a member who has
chaired the Board (data/clean/members_chairs.csv).

    Name & Served & Seated By & Born & Gender & Race and Ethnicity \\

The marks, which each table's notes explain: \textsuperscript{c} a census
sheet, \textsuperscript{p} the press or a published profile,
\textsuperscript{a} assumed because no source says otherwise; a value that
rests on both a census sheet and the press carries both, c then p, as
\textsuperscript{c,\,p}, and is
never also marked assumed; a dash where no source gives the value. Rows fall
in groups by the decade of first seating, each under a bold heading.

The roster is printed as four panels, one era each, 3A through 3D in the
paper, each its own numbered table so a reader can cite one panel. The eras
are fixed (1870-1899, 1900-1949, 1950-1999, 2000-present), each a whole run of
decades; a panel breaks only between decades, and longtable carries it across
as many pages as it needs. The subset is every member who was a woman or a
member of color, once each, in the same rows and columns under a bold heading
for the century they first took a seat, in one table the body \input{}s. The
roster and the evidence behind each cell are data/clean/members.csv.
"""
from typing import NamedTuple

import pandas as pd

import paths

MARK = {"census": "c", "press": "p", "assumed": "a"}
SEATED = {"election": "election", "appointment": "appointment",
          "special election": "special election", "unrecorded": "---"}

# The header row and the marks note, shared by both tables; paper/'s preamble
# keeps only what every table shares (\figurenotes, the Q column type).
HEADER = (r"\textit{Name} & \textit{Served} & \textit{Seated By} & "
          r"\textit{Born} & \textit{Gender} & \textit{Race and Ethnicity} \\")
MARKS_TEXT = ("Superscripts indicate the source for each record: the "
              "US census (c), press or published profile (p), or assumption (a). Two "
              "superscripts mean two kinds of source agree. A dash means no source gives the "
              "value. An asterisk after a name marks a member who has chaired the Board.")


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
    past the last year the seat table covers. A member who has ever chaired
    the Board carries an asterisk after the name."""
    present = paths.read("members_by_year").year.max()
    offices = paths.read("members_chairs")
    chairs = set(offices[offices.office == "chair"].name)
    assert chairs <= set(members.name), chairs - set(members.name)
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
        out.append(Row((name + ("*" if name in chairs else ""), years, SEATED[first.seated_by],
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
    r"""One table row, cells joined by &, ending \\* where the page may not
    break after it."""
    return " & ".join(esc(c) for c in r.cells) + (r" \\*" if keep else r" \\")


def heading(label: str, first: bool) -> str:
    """A bold heading row spanning all six columns; every heading after the
    first in a table gets a gap above it."""
    row = r"\multicolumn{6}{@{}l}{\bfseries %s} \\*" % label
    return row if first else "\\addlinespace[1.4ex]\n" + row


# No blank line after the comments: a blank line is a \par at the start of
# the next material, and the first heading's \multicolumn would then find a
# paragraph already begun.
COMMENT = ("% Generated by code/analysis/members_roster.py from data/clean/members.csv.\n"
           "% Never edit by hand: bash run.sh rewrites it.\n")


def tex(table: list, present: int) -> str:
    r"""The roster as four panels, each its own numbered table: a title line,
    a longtable environment with the decade headings and rows, and the marks
    note. \rosterk (no page break after) goes on a group's first row and on
    the row before its last, so a break never strands one row. The first
    panel claims the table number with \refstepcounter and \label{tab:roster};
    the rest reuse it through \rostertable, since all four are "Table 3"."""
    out = [COMMENT]
    for k, (start, end, decade_groups) in enumerate(panels(table)):
        letter = chr(ord("A") + k)
        last = present if end is None else end
        out.append("\\clearpage\\begingroup\n")
        if k == 0:
            out.append("\\refstepcounter{table}\\label{tab:roster}\\xdef\\rostertable{\\thetable}\n")
        out.append("\\tabletitle[\\rostertable{}%s]{Board Members, First Seated %d--%d}\n"
                    % (letter, start, min(last, present)))
        out.append("\\medskip\n")
        out.append("\\footnotesize\\setlength{\\tabcolsep}{8pt}"
                    "\\setlength{\\LTpre}{0pt}\\setlength{\\LTpost}{0pt}\n")
        out.append("\\begin{longtable}{Q}\n")
        out.append("\\toprule %s \\midrule \\endfirsthead\n" % HEADER)
        out.append("\\toprule %s \\midrule \\endhead\n" % HEADER)
        out.append("\\bottomrule \\endfoot\n")
        for j, (d, group) in enumerate(decade_groups):
            out.append(heading(f"{d}s", first=(j == 0)) + "\n")
            for i, r in enumerate(group):
                out.append(line(r, len(group) > 1 and i in (0, len(group) - 2)) + "\n")
        out.append("\\end{longtable}\\par\\smallskip\n")
        out.append("\\noindent\\figurenotes{Notes: %s}{}\\endgroup\n" % MARKS_TEXT)
    return "".join(out)


def subsets_tex(table: list) -> str:
    """The subset as one numbered table: every member who was a woman or a
    member of color, once each, in the roster's order and columns, under the
    century they first took a seat."""
    out = [COMMENT]
    group = [r for r in table if r.woman or r.of_color]
    assert group, "no woman or member of color found"
    centuries = sorted({r.decade // 100 * 100 for r in group})
    out.append("\\begin{table}[b]\n")
    out.append("\\refstepcounter{table}\\label{tab:subsets}\n")
    out.append("\\tabletitle{Women and Members of Color on the Board}\n")
    out.append("\\medskip\n")
    out.append("\\begingroup\\footnotesize\\setlength{\\tabcolsep}{8pt}\n")
    out.append("\\begin{tabular}{Q}\n")
    out.append("\\toprule\n%s\n\\midrule\n" % HEADER)
    for k, c in enumerate(centuries):
        out.append(heading(f"{c}s", first=(k == 0)) + "\n")
        out += [line(r) + "\n" for r in group if r.decade // 100 * 100 == c]
    out.append("\\bottomrule\n\\end{tabular}\\endgroup\n")
    out.append("\\par\\smallskip\n")
    out.append("\\figurenotes{Notes: %s This table is a subset of the full roster, "
                "Table~\\ref{tab:roster} in the Data Appendix.}{}\n" % MARKS_TEXT)
    out.append("\\end{table}\n")
    return "".join(out)


if __name__ == "__main__":
    members = paths.read("members")
    table = rows(members)
    assert len(table) == members.name.nunique()
    present = int(paths.read("members_by_year").year.max())
    paths.MEMBERS_ROSTER.write_text(tex(table, present))
    paths.MEMBERS_ROSTER_SUBSETS.write_text(subsets_tex(table))
