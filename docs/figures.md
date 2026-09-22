# The figures

Where each figure came from, and why it takes the form it does. The five
figures were developed in an exploratory working session in September 2026,
alongside several alternatives that were tried and set aside. That session was
a first pass, and its reasoning is recorded here so the choices are visible and
can be revisited deliberately.

A transcript of the session exists and is held by Sally. It is not in the repo.
Anything from it that bears on the work is written up here, in `docs/sources.md` or
in `docs/questions.md`.

## The five

### `residents_by_race`
Stacked bars, raw census counts, linear scale, on a 4 x 8 inch canvas — twice
as high as wide.

The proportions are deliberate. Arlington had under 27,000 residents until
1940 and about 239,000 by 2020, so on a linear axis the early decades are
almost invisible. The 1:2 canvas roughly doubles their height, and each year's
total is printed above its bar so the early figures remain readable. No 1932
line on this figure.

Counts are plotted as reported, so the 1970 and 1990 bars sit slightly above
the county total — see `questions.md`.

### `residents_by_race_log`
Log-scale line chart, one line per group plus a dashed total.

This exists because the log scale shows something the stacked version cannot:
Black residents outnumbered White residents in 1870 and 1880, the two were
close in 1890, and White residents pulled ahead by 1900. Lines begin the year
each category is first reported rather than at zero. There is no "Other"
band, since the total line already accounts for the remainder.

A log axis shows proportional change, not absolute change — worth a caption
note wherever it appears.

### `residents_by_race_share`
Stacked bars, each group's share of residents, 0–100%.

Every bar reaches 100%, so the early decades read as clearly as the later ones.
The 1970 and 1990 columns are rescaled to sum to 100%, and Hispanic before 1970
and AAPI before 1950 are plotted as 0%. Both are open — see `questions.md`.

### `residents_per_seat`
Log-scale lines: actual residents per seat against the cube-root-law benchmark,
with the gap between them shaded.

The benchmark is population divided by the cube root of population — the
residents per seat that would obtain if the Board's size followed the cube-root
law. The log axis is necessary because the benchmark is roughly a tenth of the
actual figure. This figure keeps the 1932 line and annotation.

### `board_seats`
Two panels sharing an x-axis: (a) race/ethnicity, (b) gender, both as seat
counts on a 0–5 scale rather than shares.

Seat counts rather than percentages make the 1932 expansion legible — the stack
tops out at 3 before 1932 and 5 after. Both panels carry the 1932 line and
annotation. Half-height segments are genuine: they occur when a member left
mid-year and was replaced, and the figure carries a note saying so.

AAPI appears in the legend with no visible area, because no AAPI member has
served in any year. That is a finding rather than a gap in the data.

## Colors

The palette is shared across figures so a group keeps its color everywhere:
Black `#E69F00`, Hispanic/Latino `#009E73`, AAPI `#CC79A7`, White `#D9D3C4`,
Other `#E6E6E6` with a `#8C8C8C` edge and hatching. Gender uses coral `#E8A598`
for women and slate `#A9BBCB` for men.

White and the gender pair were both revised during the working session toward
softer tones. The current values are chosen to stay distinguishable for
colorblind readers and in grayscale. They live in `analysis/style.py` and are imported by every
figure, so a palette change is a single edit.

## Where the code is

Each figure is one script in `analysis/`, reading only from `data/`. The
cleaning that produces `data/` is in `build/residents.py`. The two contested
treatments — the 1970/1990 overlap and whether not-reported reads as zero —
are in `build/assumptions.py`, called explicitly by the figures that use them,
so it is greppable which figure takes which position.

## Set aside

Earlier versions were produced and not carried forward:

- a combined figure with census, Board race and Board gender in three panels,
  in both percentage and raw-count forms
- a broken-axis version of the residents chart, with the y-axis split at 40,000
- an unbroken linear variant kept alongside it

These are not in `raw/`. Whether any should be revived is in `questions.md`.
