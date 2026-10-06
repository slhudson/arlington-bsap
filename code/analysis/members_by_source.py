r"""Which documents name the Board in which years -> figures/members_by_source.pdf, .png

A stacked timeline, one bar per document over the years it names the Board,
in the order the documents start. A bar's span is read off
data/clean/members.csv's source column: the first and last year of any term
that cites the document, so the figure stays true as sources are added or
a term's citation changes. The Alexandria Gazette's items are too few and
too scattered to read as a span, so they draw as a row of ticks instead, at
the year each citekey's own date carries.
"""
import re

import charts
import members
import paths
import style

DOCS = [
    ("arlhist1967officials", "Historical Society list"),
    ("oleary2010", "O'Leary"),
    ("novack1994", "Novack"),
    ("arlingtonva2026members", "County roll"),
    ("arlingtonelections2021", "County election results"),
    ("vaelections", "state election database"),
]
GAZETTE = "Alexandria Gazette"
GAZETTE_KEY = re.compile(r"(?:alexandria)?gazette(\d{4})")


def citekeys(source):
    return [part.strip().split(" ")[0] for part in source.split(";")]


def doc_span(frame, key):
    """The first and last start_year of a term whose source cites `key`
    anywhere - the years this document names a member of the Board."""
    named = frame[frame.source.apply(lambda s: key in citekeys(s))]
    years = named.start_year
    return int(years.min()), int(years.max())


def gazette_years(frame):
    """The year carried in each Gazette citekey cited anywhere in the
    roster, one per distinct citekey."""
    keys = {k for source in frame.source for k in citekeys(source)}
    years = sorted(int(m.group(1)) for k in keys for m in [GAZETTE_KEY.match(k)] if m)
    assert years, "no Gazette citekey found - check the build"
    return years


def main():
    style.apply()
    members_frame = paths.read("members")

    labels = [label for _, label in DOCS] + [GAZETTE]
    spans = [doc_span(members_frame, key) for key, _ in DOCS] + [gazette_years(members_frame)]

    fig, ax = charts.figure()
    charts.hspans(ax, labels, spans, style.SAND_LINE)
    charts.years(ax, 1870, members.LAST, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax)
    paths.save(fig)


if __name__ == "__main__":
    main()
