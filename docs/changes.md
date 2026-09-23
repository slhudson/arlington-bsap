# What changed about the figures

September 2026. A summary for reading cold, alongside the repository.

The short version: the figure set went from five to four, the race categories
were rebuilt on a basis where nobody is counted twice, and the figures now sit
on a shared style layer rather than each making its own choices.

## The race categories

This is the substantive change, and it answers Q1.

Race and Hispanic origin are two separate census questions. A person answers
both, so someone who is Hispanic and white is counted in a race column *and* in
the Hispanic column. That is why the four delivered columns sum to more than
the county in 1970 and 1990 — about 4,800 people in 1970 and 400 in 1990.

The fix is not to rescale, which spreads a category-definition problem across
all four bands. It is to use the table where the Bureau reports both answers
crossed together. `code/fetch/census.py` now pulls that table for every census
from 1980, and `code/build/residents.py` builds five groups that partition the
county exactly:

    Hispanic or Latino (any race), and, among those who are not Hispanic:
    White, Black, Asian and Pacific Islander, Other or multiracial

They tie to the person in all five censuses, and the build refuses to write if
they ever stop doing so. The guard earned itself immediately: it caught a
variable mapping that summed to 308,370 against a county of 189,453.

Two things the crossed tables settled while being read:

- The 1990 arithmetic in Q1 was right to the person. Non-Hispanic Black,
  American Indian, Asian and Other sum to 29,119 against the workbook's
  29,500 — a difference of 381, which is exactly the 1990 overshoot.
- The delivered columns are not all the same kind of number. `white` is
  non-Hispanic white in every year from 1980. `black` is the race total
  including Hispanic Black in 1980, 1990 and 2000, and non-Hispanic Black from
  2010, so that column changes meaning partway along. The delivered columns are
  kept as received rather than patched; the new set is what the figures use.

**Where it stops.** 1980, because that is the first census to ask Hispanic
origin of every household. 1970 asked it of a 5 percent sample, the Bureau's
own position is that 1970 is not comparable with later years, and it miscoded
people in the southern and central states into "Central or South American". A
1970 non-Hispanic figure would not be the same quantity as the others; it would
only look like one. Before 1970 the question does not exist and white means
white.

**Where the data came from.** The Census API holds no decennial data before
2000. 1980 and 1990 come from the archived Summary Tape Files, which are
fixed-width ASCII at www2.census.gov and need no key. 1980's record layout is
the Bureau's own published dictionary, saved beside the data. 1990's is
published only as PDF, so the cell offsets were derived from the file and are
checked on every fetch against the totals the file itself states, for all 136
Virginia county geographies.

## The figure set

Five figures became four.

- `board_seats` carried race and gender as two panels. The report's first
  section develops them separately, so it is now `board_race` and
  `board_gender` — same size and scale, read as a pair.
- `residents_by_race_share` folded into `residents_by_race` as its second
  panel. The two were always read together: how many residents, and what share.
- `residents_by_race_log` is retired. Its finding — that Black residents
  outnumbered White residents in 1870 and 1880 — is in the prose, and no
  section had a place for the figure.
- `residents_per_seat` lost the cube-root-law benchmark. See the question
  below.

All are recoverable from git history.

Two further changes inside `residents_by_race`. The residual band now sits with
the other groups rather than on top of White: it is another kind of not-White,
and stacked above the sand it split that population in two. In 2020 the
non-White block is 98,990 of 238,643, about 42 percent, which the old order
gave a reader no way to measure. And the residual is called "Other or
Multiracial" rather than "Other, multiracial or unreported", because nothing in
it is unreported — before 1980 it is the residents the four reported categories
do not account for, never more than 202 people, and from 1980 it is American
Indian and Alaska Native, some other race, and two or more races, all counted.

## The style layer

The figures now share one set of conventions, in `style/`, taken from the Urban
Institute's data visualization style guide rather than decided per figure. The
guide itself is committed at `style/urban-styleguide.html` so the conventions
can be checked offline, and `style/urban-styleguide.md` lists where this project
departs from it and why.

No figure script sets a colour, a size, a font, a margin or a legend position.
The palette is Okabe and Ito's Color Universal Design set, which is built so
that no two hues collapse into one another under colour vision deficiency.

## Questions

**1. Can the cube-root benchmark go?**

`residents_per_seat` plotted actual residents per seat against the cube root of
population, with the gap shaded. It has been taken out, and the question is
whether that is right.

The reasoning: Taagepera's cube-root law is a stylised fact, not best-practice
guidance. He observed that assemblies tend to sit near the cube root of
population; he did not argue that they should. And his data was national
parliaments. Arlington is not in that reference class — there is a 2025 *Public
Choice* paper extending the law to local assemblies, which exists because the
original did not cover them, and which finds a different exponent and an
imperfect fit. As drawn, the cube root of 239,000 is about 62, so the figure
implied Arlington should have a 62-member Board and is twelvefold short.

If a comparison belongs in the report at all, peer jurisdictions would be the
right reference class — other Virginia counties, or similarly sized US
localities. That is more work: county board sizes are not published in one
machine-readable place and would need keying by hand.

The `cube_root_p` and `cube_root_resident_ratio` columns are still built, so
nothing has to be rebuilt if the answer is to keep it.

**2. Where did the 1900–1980 race figures come from?** (Q12)

1980 onward is now sourced to the person. 1900–1980 rests on the workbook with
no source traced, which is most of the series.

**3. Why is 1931 blank when 1916–1930 are not?**

1931 is the one year no source reaches: O'Leary's listings stop at the 1915
election, Novack begins with the County Manager plan in 1932, and the workbook
covers 1916–1931 but leaves 1931 empty. It sits exactly at the restructuring,
so it may be a real transitional year rather than a gap — the build cannot tell
those apart.
