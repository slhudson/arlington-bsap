r"""Which documents name the Board in which years -> figures/members_by_source.pdf, .png

A stacked timeline, one bar per document over the years it names the Board,
sorted by the year each starts - earliest at the top - so the row order is
read off the same computation as the bars rather than typed separately. A
bar's span is read off data/clean/members.csv's source column: the first and
last year of any term that cites the document, so the figure stays true as
sources are added or a term's citation changes. The Alexandria Gazette's
items are too few and too scattered to read as a span, so they draw as a row
of ticks instead, at the year each citekey's own date carries, and the row
sorts by its earliest tick like any other.

A document either records who held the seat or who won it, and the two
shades of the one ramp carry that distinction, service the darker (style.SOURCE_KIND): the Gazette row is mixed,
an appointment or a press mention of a sitting member beside a candidate list
or an election return, so its ticks take the colour of the item, not the row.
"""
import re

import charts
import members
import paths
import style

SERVICE = style.SOURCE_KIND["service"][1]
ELECTION = style.SOURCE_KIND["election"][1]

DOCS = [
    ("arlhist1967officials", "Arlington Historical Society (1967)", SERVICE),
    ("oleary2010", "O'Leary (2010)", ELECTION),
    ("novack1994", "Novack (1994)", SERVICE),
    ("arlingtonva2026members", "Arlington County Board (2026)", SERVICE),
    ("arlingtonelections2021", "Arlington County Elections (2021)", ELECTION),
    ("vaelections", "Virginia Department of Elections", ELECTION),
]
GAZETTE = "Alexandria Gazette"
GAZETTE_KEY = re.compile(r"(?:alexandria)?gazette(\d{4})")
# Each item's own kind, read off its entry in paper/bib/sources.bib: an
# appointment, a qualification or a press mention of a sitting member is
# service; a candidate list or an election return is a contest.
GAZETTE_KIND = {
    "gazette1872smithappointed": "service",
    "gazette1873crockerappointed": "service",
    "gazette1873schuttqualified": "service",
    "gazette1892febreyappointed": "service",
    "gazette1911districtcandidates": "election",
    "alexandriagazette1913duncan": "service",
    "alexandriagazette1914duncan": "service",
    "alexandriagazette1915duncan": "service",
    "alexandriagazette1919duncan": "service",
    "alexandriagazette1921duncan": "service",
    "alexandriagazette19191105p1": "election",
}


def citekeys(source):
    return [part.strip().split(" ")[0] for part in source.split(";")]


def doc_span(frame, key):
    """The first and last start_year of a term whose source cites `key`
    anywhere - the years this document names a member of the Board."""
    named = frame[frame.source.apply(lambda s: key in citekeys(s))]
    years = named.start_year
    return int(years.min()), int(years.max())


def gazette_items(frame):
    """(year, colour) for each Gazette citekey cited anywhere in the roster,
    one per distinct citekey, earliest first."""
    keys = {k for source in frame.source for k in citekeys(source)}
    matched = [(k, m) for k in keys for m in [GAZETTE_KEY.match(k)] if m]
    assert matched, "no Gazette citekey found - check the build"
    missing = [k for k, _ in matched if k not in GAZETTE_KIND]
    assert not missing, f"no service/election kind recorded for {missing} - add it to GAZETTE_KIND"
    items = sorted((int(m.group(1)), style.SOURCE_KIND[GAZETTE_KIND[k]][1]) for k, m in matched)
    return [y for y, _ in items], [c for _, c in items]


def main():
    style.apply()
    members_frame = paths.read("members")

    entries = {label: (doc_span(members_frame, key), color) for key, label, color in DOCS}
    entries[GAZETTE] = gazette_items(members_frame)
    entries = dict(sorted(entries.items(), key=lambda kv: min(kv[1][0])))

    fig, ax = charts.figure()
    charts.hspans(ax, entries)
    charts.years(ax, 1870, members.LAST, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax, note=None)
    charts.legend(fig, dict(style.SOURCE_KIND.values()))
    paths.save(fig)


if __name__ == "__main__":
    main()
