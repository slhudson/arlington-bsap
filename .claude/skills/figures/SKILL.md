---
name: figures
description: Build or change a figure in this repository. Use whenever a chart, graph, figure or palette for the Arlington BSaP report is being created, edited, restyled or reviewed.
---

# Figures

Every figure is built through the style layer in `code/analysis/`. Nothing
visual is set inside a figure script.

    style.py        Urban's conventions, the palette, the two output profiles
    urban.mplstyle  the rcParams, cited to the guide
    charts.py       the four chart types, with legend and note placement built in
    files.py        where things are written
    gallery.py      every chart type, both profiles, each palette candidate

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
  once per figure, inside one panel. Notes that belong to the document -
  sources, caveats, definitions - go in the caption, not the image.

## Axes

- The y-axis ends on a round tick, not just clear of the data.
- No y-axis label that repeats the panel title.
- Tick density has to be legible at the profile's width. Decades collide at
  6.25in; use 20-year steps or rotate.

## Legend

- One legend for the whole figure, not one per panel.
- One row, in stacking order, stretched across the top, outside the axes.
- If labels are too long for one row, shorten the labels. Do not break the row
  and do not shrink the type.
- A category with no data anywhere gets no swatch. An empty legend entry reads
  as a sliver too small to see rather than as zero, and the absence belongs in
  the prose. Test on the data, not on the category name.
- Direct end-labels on a line chart are preferred to a legend where the lines
  allow it. This is Urban's rule and it applies.

## Labels

- Capitalisation is consistent across every label in a figure, including the
  shared group labels in `style.py`.
- Axis labels and panel titles are lowercase. Group names keep their own
  capitalisation as proper nouns.

## Process

- Render the figure, look at the image, and check it against this file before
  showing Sally anything. Every rule above has been broken at least once by
  not looking.
- The gallery is how a style change is reviewed, not five figures one at a
  time. Rebuild it after any change to the style layer.
- Every note Sally gives becomes a line in this file and applies to every
  figure from then on, not only the one she was looking at.
- Report judgment calls, not fixes. She does not need to be told that a
  collision was corrected; she needs to be told what was decided on her behalf
  and why.
- Never edit `figures/` by hand. Change the script and re-run.
