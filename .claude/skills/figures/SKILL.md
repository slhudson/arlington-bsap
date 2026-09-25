---
name: figures
description: Build or change a figure in this repository. Use whenever a chart, graph, figure or palette for the Arlington BSaP report is being created, edited, restyled or reviewed.
---

# Figures

Every figure is built through the style layer in `style/`. Nothing visual is
set inside a figure script.

    style/style.py             the palette, the profiles, which colour each group takes
    style/urban.mplstyle       the rcParams, cited to the guide
    style/charts.py            the chart types, with legend and note placement
    code/analysis/paths.py     where things are read and written
    code/analysis/<figure>.py  which numbers a figure shows

`style/` has no `paths.py` and therefore no route to `data/`. If something
visual needs a column, that is a sign the figure script should pass it in.

A figure script reads `data/clean/`, calls `charts.*`, and calls
`paths.save()`. If it needs a colour, a size, a font, a margin or a legend
position, that belongs in the style layer, not in the script.

The conventions are the Urban Institute's data visualization style guide,
<https://urbaninstitute.github.io/graphics-styleguide/>. **Follow Urban by
default.** The rules below are Sally's, and where they conflict with Urban,
these win. **The reasoning behind every convention lives in `docs/figures.md`**, and
nowhere else. This file states the rules; the style layer states the values;
neither repeats the reasons.

## Content

- Raw series only. No benchmark line, trend line or reference line unless
  asked for. The cube-root-law benchmark was removed for this reason.
- No title inside the image. The LaTeX caption carries it, which is also
  Urban's rule for PDF products.
- No value labels on bars.
- Do not re-raise what is already written down: a decision in
  `docs/residents.md`, `docs/board.md` or `docs/voters.md`, or a row in
  `docs/questions.csv` with an owner.
  The vote-per-seat denominator on `turnout` is the standing example.

## Layout

- Nothing cramped. The bottom margin especially. Constrained layout is on by
  default; do not switch it off for hand-tuned padding.
- No text collisions anywhere: tick labels, legends, annotations, end labels.
- Two-panel figures go side by side, not stacked. Panel titles are centred and
  plain: `(a) number of residents`.
- An explanatory note that belongs to a mark, such as the 1932 rule, appears
  once per figure and goes above the top of the frame; `charts.rule()` draws
  it there. Once per *figure*, not once per section: the same
  note on three figures is not repetition to remove, because a reader
  arriving at the third one needs to reorient just as much as at the first.
  Notes that belong to the document, such as sources, caveats and
  definitions, go in the caption, not the image.

## Type

- Never write a point size into a figure script. Every size is a rcParam in
  `urban.mplstyle`, stepped up together by the profile's scale in
  `style.apply()`; a note or label drawn by hand takes
  `plt.rcParams["font.size"]`, as `charts.rule()` does.

## Size

- Never set a width or a height in a figure script. Every figure is the
  profile's width, and `charts.fit()` solves each figure's height from
  `style.PLOT_ASPECT`, so every plot has the same shape. A ratio typed into a figure script
  is how a set of figures stops looking like a set.
- A two-panel figure gives each panel about half the width, so its bars read
  narrower than a single-panel chart's even though the frame is identical.
  That is the cost of panelling, not a bug to fix by widening the figure.

## Axes

- The y-axis ends on a round tick, not just clear of the data.
- No y-axis label that repeats the panel title.
- Tick density has to be legible at the profile's width. Decades collide at
  6.25in, so name every twentieth year and let the minor ticks mark the rest.
  Prefer that to rotating the labels: rotated text is slower to read and it
  makes a panel look unlike its neighbour.
- **Both panels of a figure label their axes the same way.** A bar panel does
  not need a label under every bar to be readable; the minor ticks locate the
  unlabelled ones.
- Where the labelled interval is wider than the data's interval, add unlabelled
  minor ticks at the data's interval, so a reader can find 1890 or 1910 on an
  axis that only names every twentieth year. `charts.years()` does this.

## Legend

- **No legend at all where the lines can be labelled directly.** A legend is
  a lookup table the reader has to hold in their head; getting rid of one is a
  gain, not an inconsistency to correct. The growth figure has none.
- One legend for the whole figure, not one per panel, where one is needed.
- One row, in stacking order, below the figure and outside the axes.
  `charts.legend()` puts it there.
- If labels are too long for one row, shorten the labels. Do not break the row
  and do not shrink the type.
- A category with no data anywhere gets no swatch. An empty legend entry reads
  as a sliver too small to see rather than as zero, and the absence belongs in
  the prose. Test on the data, not on the category name.
- Direct end-labels on a line chart are preferred to a legend where the lines
  allow it. This is Urban's rule and it applies.
- **A direct label sits beside the point it names, at that point's height.**
  Anywhere else it is a caption the reader has to match to a line, which is
  what a legend already is. `charts.end_label()` takes which side.
  Wrap the name above the value: two short lines need half the room of one
  long one, so it fits without the axis visibly stretching to hold it.

## Colour

- The palette is `style.OKABE_ITO`, assigned per subject in `style.py`. Do
  not introduce a colour that is not in it, and do not move a colour between
  groups without reading `docs/figures.md`: several are placed so that
  nothing shares a colour with anything a reader meets beside it.
- **No textures.** Distinguish with colour.
- **Name a residual for what is in it.** Check the data before writing the
  label. `Other, multiracial or unreported` was wrong: nothing in that band
  is unreported. `style.RESIDUAL` carries the current name; `docs/figures.md` its basis.
- The largest group takes a near-neutral. No group holds a saturated lead
  colour on a chart about representation.

## Labels

These are settled; `docs/figures.md` carries the reasoning. Do not
revisit.

- **Legend entries capitalise proper nouns and nothing else.** Racial and
  ethnic identifiers are proper nouns: `Black`, `White`, `Hispanic or Latino`,
  `Asian & Pacific Islander`, `Other or Multiracial`. `women` and `men` are
  not, under anyone's convention, and stay lowercase.
- **`Multiracial` is capitalised**, and **Black and White are both
  capitalised**, Urban's lowercase `white` notwithstanding.
- **Axis labels and panel titles are lowercase**: `residents`, `census year`,
  `(a) number of residents`.
- **No slashes in category names.** Use the Bureau's own wording: `Hispanic or
  Latino`, `Asian & Pacific Islander`. The ampersand is for width, since the
  legend is one row.
- **State a qualifier once, in the caption, not in every key entry.** On the
  census basis every group except Hispanic or Latino is non-Hispanic; the
  legend says `Black`, `White` and so on, and the caption says "groups other
  than Hispanic or Latino are non-Hispanic". Repeating it five times in the
  legend is the thing to avoid.

## Process

- Render the figure, look at the image, and check it against this file before
  showing Sally anything. Every rule above has been broken at least once by
  not looking.
- After any change to the style layer, rebuild every figure and look at all of
  them. A change to a shared colour, size or placement is never local to the
  figure that prompted it. `run.sh` names the figures a run changed; if it
  names one you did not expect, look at it before committing.
- Never commit a change to a figure script without re-running. The committed
  figures are what the paper compiles, and a stale PDF looks exactly like a
  current one.
- Every note Sally gives becomes a line in this file and applies to every
  figure from then on, not only the one she was looking at. If the note is a
  visual convention, the value goes in the style layer, the reason in
  `docs/figures.md`, and this file gets the rule.
- Report judgment calls, not fixes. She does not need to be told that a
  collision was corrected; she needs to be told what was decided on her behalf
  and why.
- Never edit `figures/` by hand. Change the script and re-run.
