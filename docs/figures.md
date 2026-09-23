# The figures

Where each figure came from and why it takes the form it does. Six build.

The visual conventions are not described here — they are in `style/`, which is
where they are enforced. This file covers what each figure *shows* and the
decisions behind that. `style/urban-styleguide.md` covers what the style layer
follows and where it departs.

## The six

### `residents_per_seat`
Two series on one linear axis, 1870–2020: total population, and residents per
Board seat. Both are counts of people, so the vertical distance between them
means the same thing everywhere on the page.

Each line is named beside its own 2020 point, at that point's height, with the
name wrapped above the value. Three placements were tried. Outside the plot on
one line — Urban's placement — needed enough headroom past 2020 to visibly
stretch the axis. In the empty band between the lines, the label sat nowhere
near the line it named, which makes it a caption to be matched up, which is
what a legend already is. Wrapping to two lines halves the room a label needs,
so it sits immediately beside its point and the axis barely moves.

"Seat", not "member". The denominator is seats that exist — three through 1930
and five after — not members actually serving, and the two differ in 1873 and
1990, when a seat sat vacant. "Per member" reads better and would be claiming
something the figure does not measure.

It carried a cube-root-law benchmark and no longer does. The law is
descriptive, not normative — Taagepera observed that assemblies sit near the
cube root of population, he did not argue they should — and its reference class
was national parliaments, which Arlington is not in. As drawn it implied a
62-member Board. Whether any comparison belongs in the report is open; peer
jurisdictions would be the right reference class for one.

A second y-axis was considered and rejected. The Board held three seats before
1932 and five after, so no single right-hand scale is correct for the whole
series, and choosing one decides which era looks like the exception.

### `residents_by_race`
Two panels side by side: (a) counts, (b) shares, 1870–2020.

**Panel (a) is unstacked lines and excludes White.** Stacked bars cannot show
when a group starts being counted: a band of height zero and a band that has
not started are the same picture. A line simply begins — Asian & Pacific
Islander in 1950, Hispanic or Latino in 1970, Other or Multiracial in 1980.
That is what Q2 asked for and what the retired log figure used to do.

**White is plotted until it leaves the axis, and an arrow marks where.** The
axis stops at 50,000 because none of the other four passes 37,362; White
reaches 161,329 by 1970. Plotting its full range would put the other four in
the bottom quarter, and dropping it entirely loses the years when the groups
were comparable. So it is drawn, the axis clips it in the late 1930s, and
`charts.off_scale` puts a triangle where it exits — interpolated from the data,
not written in.

A triangle, not an arrow with a shaft. A shaft is a second stroke at its own
angle and reads as another series; a marker sits on the line's own last point
and adds nothing to argue with. No text either: the legend has already named
the colour, and where the line goes is the caption's business.

That keeps the finding the retired log chart existed for: White is 1,175 in
1870 against Black at 2,010, and Black outnumbered White until about 1890.

White is a shade darker as a line (`style.SAND_LINE`) than as bars — the sand
is tuned as a filled area and is close to invisible as a stroke.

Three things the lines say that the stacked version could not: Hispanic or
Latino passes Black in 1990, Asian & Pacific Islander passes Black in 2010, and
Black is close to flat from 1970 — 10,076 to 20,330 over fifty years — while
the county's population other than White more than quadrupled.

**Two bases, one series, and nothing drawn to mark it.** From 1980 the bands
are the five census groups that partition the county exactly: race crossed with
Hispanic origin, so nobody is counted twice. Before 1980 they are the delivered
race categories, because the Bureau did not ask Hispanic origin of everyone
until 1980 and 1970's sample question is not comparable.

A rule at 1980 was drawn and removed. The change is real but does not alter
what the figure says — Arlington had 1,387 Hispanic residents in 1970, under
one per cent of the county, and none on the Board — so a line across the figure
claimed more importance for it than it has. It belongs in the caption, and the
labels read the same either side of 1980, so they do not mislead. Only 1970
overshoots the county total; 1990, which used to, is exact.

**The residual sits inside the stack, below White.** Other or Multiracial is another kind of not-White; drawn above the sand it split the
non-White population in two and understated how much the county has
diversified. In 2020 the non-White block is 98,990 of 238,643, about 42 per
cent, which the old order gave a reader no way to measure.

### `board_gender`
Board seats by gender, 1870–2026, as counts on a 0–5 scale rather than shares,
so the 1932 expansion is legible: the stack tops out at 3 before it and 5
after.

Both bands are drawn. Men are not redundant with women — they are the
denominator, and without them two seats of five and two of three look the same.

### `board_race`
The same size, scale and treatment as `board_gender`, so the two read as a
pair.

A category holding no seat in any year gets no band and no legend entry. An
empty swatch reads as a sliver too small to see rather than as zero; that no
Asian American or Pacific Islander member has served is a finding, and a
finding is a sentence in the prose. The test is on the data rather than the
category name, so a future member restores the band with no edit.

### `voters_by_party`
The voters' side of `board_party`: Arlington's presidential vote in three
bands, Democratic from the axis, other in the middle, Republican from the
top, in the same colours, every four years from 1872. Stacked bars rather
than steps because an election is a point in time; a step would claim the
share held for four years.

**Voters, not residents.** Virginia has no party registration, so the
presidential vote is the proxy, and it counts the people who voted, in an
electorate narrowed before 1966 by the poll tax and the 1902 constitution.
The axis says "share of voters" for that reason. Q30 in `docs/questions.md`.

**Three bars are missing by decision**: 1896, 1904 and 1908, whose returns
are incomplete on O'Leary's page. The build keeps the rows and marks them;
the figure leaves a gap, which says so where a short bar would not.

### `board_party`
The same frame, scale and 1932 rule as the other two seat charts, so the three
read as a set. It begins at 1932 with a gap before it: no source names a
party for the magisterial-district Board, and a gap says so where a band of
"not recorded" would say the question had been asked.

**Party is whose candidate a member was**, because it has never been on the
ballot. The county's own record gives it for most winners; reporting fills
the 1967–83 stretch the county marks "(I)", which is what turns that stretch
from a wall of independents into a Republican majority. Q29 in
`docs/questions.md` has the rule and the residue.

**The two parties take the two edges of the frame.** Democrats grow up from
the axis, Republicans hang down from the five-seat line, and ABC, "not
recorded" and independent sit between them. Every category keeps one place
for the whole run, and a majority reads as the block that crosses the middle.
Sorting each year by size was rendered and rejected: it puts the majority on
the floor, which reads quickly, but the Democratic band then hops between
floor and ceiling through the 1940s and 1950s, splitting one party's history
across two places on the page.

**"Not recorded" is a band, not a gap**, because the seats existed and were
held; what is missing is the label. It is most of the first two Boards and
much of the 1940s. Its colour is a lighter grey than independent, so an
absence of evidence never reads as a category.

**ABC has its own band.** Arlingtonians for a Better County was a nonpartisan
coalition allied with the Democrats, and could be folded in; it is kept
because the county recorded it as a label and a Board with an ABC majority
from 1957 to 1966 is a finding.

**Partisan colours are the ones readers bring**, at Okabe-Ito values: sky blue
and vermilion. This sets aside the rule that the largest group takes the
near-neutral, deliberately — a sand band labelled Democratic would be read
against the convention rather than as neutral. Vermilion also draws the
per-seat line on the growth figure; that line is named where it runs, so the
hue carries no meaning there and the reuse costs nothing.

## Gaps and half seats

1931 is missing in the source and appears as a gap rather than a zero, on all
three seat figures. Half-height segments are genuine: a member left mid-year and was
replaced.

Two years sit below the full Board, and both are real. 1873 shows two and a
half seats because Washington district was vacant from June to November, and
1990 shows a seat short between a February resignation and a May special
election.

1870 does not, though it once did. The Board came into existence at the May
1870 election, so only eight months of that year exist; measured against the
calendar year it read two seats, and the chart then said the Board grew from
two to three. It is now measured against the months the Board existed, which
is what every other year is measured against too — see `docs/sources.md`.

## Retired

- `board_seats`, split into `board_race` and `board_gender`.
- `residents_by_race_share`, folded into `residents_by_race` as its second panel.
- `residents_by_race_log`, a log-scale line chart. Its finding — that Black
  residents outnumbered White residents in 1870 and 1880 — is in the prose, and
  no section had a place for the figure.
- A combined three-panel version with census, Board race and Board gender; a
  broken-axis variant of the residents chart with the y-axis split at 40,000;
  and an unbroken linear variant. None are in `data/raw/`. Whether any should
  be revived is in `docs/questions.md`.

All are recoverable from git history.
