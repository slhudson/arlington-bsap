---
name: figures
description: Build or change a figure in this repository. Use whenever a chart, graph, figure or palette for the Arlington BSaP report is being created, edited, restyled or reviewed.
---

# Figures

Every figure is built through the style layer in `style/`. Nothing visual is
set inside a figure script.

    style/style.py             Urban's conventions, the palette, the profiles
    style/urban.mplstyle       the rcParams, cited to the guide
    style/charts.py            the chart types, with legend and note placement
    code/analysis/paths.py     where things are read and written
    code/analysis/<figure>.py  which numbers a figure shows

`style/` has no `paths.py` and therefore no route to `data/`. If something
visual needs a column, that is a sign the figure script should pass it in.

A figure script reads `data/clean/`, calls `charts.*`, and calls
`files.save()`. If it needs a colour, a size, a font, a margin or a legend
position, that belongs in the style layer, not in the script.

The conventions are the Urban Institute's data visualization style guide,
<https://urbaninstitute.github.io/graphics-styleguide/>. **Follow Urban by
default.** The rules below are Sally's, and where they conflict with Urban,
these win. Where the layer already departs from Urban, `style.py` says so and
gives the reason.

## Content

- Raw series only. No benchmark line, trend line or reference line unless
  asked for. The cube-root-law benchmark was removed for this reason.
- No title inside the image. The LaTeX caption carries it, which is also
  Urban's rule for PDF products.
- No value labels on bars.
- Do not re-raise issues already written down in `docs/questions.md`. The
  1970/1990 race totals are the standing example: it is a known, documented,
  owned question and does not need flagging again.

## Layout

- Nothing cramped. The bottom margin especially. Constrained layout is on by
  default; do not switch it off for hand-tuned padding.
- No text collisions anywhere: tick labels, legends, annotations, end labels.
- Two-panel figures go side by side, not stacked. Panel titles are centred and
  plain: `(a) number of residents`.
- An explanatory note that belongs to a mark, such as the 1932 rule, appears
  once per figure, and goes **above the top of the frame**, not inside the
  plot. Inside, it sits on whatever the chart has drawn there - on a filled
  seat chart that is a solid band, and the text stops being legible. Notes
  that belong to the document - sources, caveats, definitions - go in the
  caption, not the image.

## Axes

- The y-axis ends on a round tick, not just clear of the data.
- No y-axis label that repeats the panel title.
- Tick density has to be legible at the profile's width. Decades collide at
  6.25in; use 20-year steps or rotate.

## Legend

- One legend for the whole figure, not one per panel.
- One row, in stacking order, below the figure and outside the axes. Urban
  stretches legends across the top; here they go below, because several
  figures carry a note above the plot and the two compete for that band.
- If labels are too long for one row, shorten the labels. Do not break the row
  and do not shrink the type.
- A category with no data anywhere gets no swatch. An empty legend entry reads
  as a sliver too small to see rather than as zero, and the absence belongs in
  the prose. Test on the data, not on the category name.
- Direct end-labels on a line chart are preferred to a legend where the lines
  allow it. This is Urban's rule and it applies.

## Colour

- The palette is Okabe-Ito, in `style.py`, assigned per subject. Do not
  introduce a colour that is not in it.
- Nothing shares a colour with anything a reader meets beside it. Asian/Pacific
  Islander is blue rather than reddish purple because the reddish purple
  carries women on the gender chart.
- The largest group takes a near-neutral. No group holds a saturated lead
  colour on a chart about representation.

## Labels

- Axis labels and panel titles are lowercase. Group names are capitalised:
  they are names, not descriptions.
- **Black and White are both capitalised in figures.** APA and AMA capitalise
  both; Urban capitalises Black and leaves white lowercase, which in a legend
  beside `Hispanic or Latino` reads as a typo rather than as a position. Prose
  may differ; the figures do not.
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
  figure that prompted it.
- Every note Sally gives becomes a line in this file and applies to every
  figure from then on, not only the one she was looking at.
- Report judgment calls, not fixes. She does not need to be told that a
  collision was corrected; she needs to be told what was decided on her behalf
  and why.
- Never edit `figures/` by hand. Change the script and re-run.
