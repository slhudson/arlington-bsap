r"""Which documents carry the election returns in which years -> figures/elections_by_source.pdf, .png

One row per publisher, read off the source columns of
data/clean/elections_results.csv, elections_turnout.csv and
elections_margins.csv. A publisher whose years leave no long gap is a solid bar
from its first year to its last, coloured for what it carries: the presidential
vote, the Board's vote, or both. One whose items are scattered draws a tick a
year instead. Rows are sorted by first year, earliest at the top, the press last.
"""
import charts
import members
import paths
import style

COLOR = {k: v[1] for k, v in style.ELECTION_RETURNS.items()}
# A publisher whose years leave no gap longer than this reads as one span;
# one with longer gaps is a set of dated items and draws as ticks.
SPAN_GAP = 8

# A citekey's prefix names who published it, the first match winning; a
# newspaper's page, the Gazette's included, falls through to the press row.
PUBLISHERS = [
    (("warrock",), "Warrock-Richardson Almanack"),
    (("vasecretary",), "Secretary of the Commonwealth"),
    (("oleary",), "O'Leary (2010)"),
    (("arlingtonelections",), "Arlington County Dept. of Elections"),
    (("vaelections",), "Virginia Dept. of Elections"),
]
OTHER = "Various Press Outlets"


def publisher(key):
    for prefixes, label in PUBLISHERS:
        if key.startswith(prefixes):
            return label
    return OTHER


def keys(source):
    return [part.strip().split(" ")[0] for part in str(source).split(";") if part.strip()]


def ticks():
    """(year, publisher, contest) for every year a publisher carries a contest."""
    out = set()
    results = paths.read("elections_results")
    for r in results.itertuples():
        contest = "president" if r.office == "president" else "board"
        out |= {(int(r.year), publisher(k), contest) for k in keys(r.source)}
    turnout = paths.read("elections_turnout")
    for r in turnout[turnout.board_source.notna() & turnout.board_votes.notna()].itertuples():
        out |= {(int(r.year), publisher(k), "board") for k in keys(r.board_source)}
    margins = paths.read("elections_margins")
    for r in margins[margins.votes_cast.notna()].itertuples():
        out |= {(int(r.year), publisher(k), "board") for k in keys(r.source)}
    return out


def entries(found):
    """{publisher: (span or years, colour)}: a publisher with no long gap is one
    bar from its first year to its last, in the colour of what it carries
    (president, board or both); one with gaps is a tick a year, a year with both
    contests a single tick of the both colour."""
    contests = {}
    for year, label, contest in found:
        contests.setdefault(label, {}).setdefault(year, set()).add(contest)
    out = {}
    for label, by_year in contests.items():
        years = sorted(by_year)
        carried = set().union(*by_year.values())
        gap = max((b - a for a, b in zip(years, years[1:])), default=0)
        if gap <= SPAN_GAP:
            kind = "both" if len(carried) == 2 else carried.pop()
            out[label] = ((years[0], max(years[-1], years[0] + 1)), COLOR[kind])
        else:
            kinds = ["both" if len(by_year[y]) == 2 else next(iter(by_year[y])) for y in years]
            out[label] = (years, [COLOR[k] for k in kinds])
    # The press row, a set of scattered items, closes the list.
    return dict(sorted(out.items(), key=lambda kv: (kv[0] == OTHER, kv[1][0][0])))


def main():
    style.apply()
    fig, ax = charts.figure()
    charts.hspans(ax, entries(ticks()))
    charts.years(ax, 1870, members.LAST, step=20, label="year", through=members.LAST + 1)
    charts.rule(ax, note=None)
    charts.legend(fig, dict(style.ELECTION_RETURNS.values()))
    paths.save(fig)


if __name__ == "__main__":
    main()
