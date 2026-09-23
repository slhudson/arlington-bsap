# The figures

Where each figure came from and why it takes the form it does. Four build.

The visual conventions are not described here — they are in `style/`, which is
where they are enforced. This file covers what each figure *shows* and the
decisions behind that. `style/urban-styleguide.md` covers what the style layer
follows and where it departs.

## The four

### `residents_per_seat`
Two series on one linear axis, 1870–2020: total population, and residents per
Board seat. Both are counts of people, so the vertical distance between them
means the same thing everywhere on the page. Each line is labelled at its own
right-hand end with its final value; no legend.

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

Side by side rather than stacked because the counts panel has to be taller than
it is wide for the decades before 1940 to have any height — Arlington had under
27,000 residents until 1940 and 238,643 by 2020.

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

## Gaps and half seats

1931 is missing in the source and appears as a gap rather than a zero, on both
seat figures. Half-height segments are genuine: a member left mid-year and was
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
