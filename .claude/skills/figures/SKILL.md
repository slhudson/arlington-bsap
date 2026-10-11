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
    style/labels.py            where a name sits beside its dot; reached through charts
    code/analysis/paths.py     where things are read and written
    code/analysis/<figure>.py  which numbers a figure shows

`style/` has no `paths.py` and therefore no route to `data/`. If something
visual needs a column, that is a sign the figure script should pass it in.

A figure script reads a clean table with `paths.read("<stem>")`, calls
`charts.*`, and ends in `paths.save(fig, profile)`, which names the file after
the script itself — a figure's name is never written out in its script. If it
needs a colour, a size, a font, a margin or a legend position, that belongs in
the style layer, not in the script.

The conventions are the Urban Institute's data visualization style guide,
<https://urbaninstitute.github.io/graphics-styleguide/>. **Follow Urban by
default.** The rules below are Sally's, and where they conflict with Urban,
these win. **The reasoning behind every convention lives in `docs/figures.md`**, and
nowhere else. This file states the rules; the style layer states the values;
neither repeats the reasons.

## A figure has a one-sentence point

Before building or keeping a figure, say in one sentence what a reader should take
from it. If the prose already says that sentence and the picture does not make it
plainer, the figure leaves the paper and stays in the repository (the by-district
turnout figure, 5 October 2026). The denominator is the population the section is
about: a section on who could vote divides by residents of voting age, not by
everyone. Where points are spaced irregularly because of what survives rather than
when things happened, the figure itself says so, in the legend or the caption:
an irregular spacing with no stated reason is a question the figure leaves
open (Sally, 5 October 2026).

## The caption's notes

The notes are written for a reader who only ever looks at the figure: that
reader should come away with its story, not with how it was made (Sally, 10
October 2026).

- **Walk the picture, not the method.** Say what the reader is looking at.
  How the figure was built goes in the data appendix, with one line in the
  note pointing there.
- **Name each mark the way the eye sees it**: "the dark pink region", "the
  tan shaded region", not "the 1915 tint".
- **Tell the figure's story in time order**, each mark getting its sentence
  where it enters the story, and end on the present, where the reader stands.

Sally's note for the district map, the model:

> This map outlines the territory known as Alexandria County from 1870 to
> 1915. The dark pink region was annexed by the City of Alexandria in 1915,
> and the remaining territory was renamed Arlington County in 1920. In 1930,
> the City annexed another portion of the County, leaving the tan shaded
> region under the Board's jurisdiction until the present day.

## Content

- **Every mark a reader can see is a question, and the legend or the caption
  answers it, or the mark goes.** A line, a dot, a shade, a label. An edge
  where two legend colours meet answers itself; a bare line does not (the
  stream on the district map, 6 October 2026). A dot for a neighbourhood
  answers wrongly, since a neighbourhood is a region and not a point. Before
  showing a figure, list its marks and find each one's answer.
- No title inside the image. The LaTeX caption carries it, which is also
  Urban's rule for PDF products.
- No value labels on bars.
- Do not re-raise what is already written down: a decision in
  `docs/residents.md`, `docs/members.md` or `docs/elections.md`, or a row in
  `docs/questions.csv` with an owner.
  The vote-per-seat denominator on `turnout` is the standing example.

## Layout

- Nothing cramped. The bottom margin especially. Constrained layout is on by
  default; do not switch it off for hand-tuned padding. `charts.scatter_pair()`
  is the one exception: it places its broken axes itself, so the gaps are exact.
- No text collisions anywhere: tick labels, legends, annotations, end labels.
- Two-panel figures go side by side, not stacked, with one exception: a pair
  of scatters (`charts.scatter_pair()`) stacks, each panel at full width, so
  its names fit. Panel titles are centred and plain: `(a) number of residents`.
- An explanatory note that belongs to a mark, such as the 1932 rule, appears
  once per figure and goes above the top of the frame; `charts.rule()` draws
  it there. Once per *figure*, not once per section: leave the same note on
  every figure that carries the mark. Notes that belong to the document, such
  as sources, caveats and definitions, go in the caption, not the image.

## Horizontal bars

- **Categories whose labels are phrases run down the side**, through
  `charts.hbars()`, `charts.hgrouped_bars()`, `charts.hstacked_bars()` or
  `charts.hdots()`, rather than along the bottom where they would rotate or
  truncate.
- Blocks within one such figure take a bold heading in the axis labels,
  through `hbars(..., groups=)`; nothing is hand-placed.

## Scatters

- Start both axes at zero where possible; break an axis rather than lose a
  far point or start above zero. `charts.break_x()` cuts before one outlier
  (`style.BROKEN`); `charts.break_x_floor()` cuts the empty run up to a set's
  floor, showing only the 0 (`style.BROKEN_FLOOR`). Every break in a figure is
  the same width, `style.BREAK_GAP`, and its axis label is centred under both
  sides. Measure the gaps, do not judge them by eye.
- Squarer than the time series: `charts.scatter()` takes `style.SQUARE`.
  Two scatters may share one figure as two panels when they answer one
  question and one legend and one note serve both: `charts.scatter_pair()`,
  which takes `style.PAIR`. The peer localities are the case. Two panels on
  the same measure may each take their own y range.
- One dot size. Area does not carry a third measure a reader can read.
- Name dots with `charts.dot_label()` and let `labels.place()` choose
  where. A dot too crowded to name beside it takes `leader=True`; `first=`
  steers a leader away from a dot touching its own. A name that finds no
  clear place stops the build: drop the name, never the check.
- **A name sits to the right of its dot** unless something stops it: the
  easiest place to read (Sally, 9 October 2026). Where the frame is all that
  stops it, widen the axis.
- **Which dots get names is a question about the reader**, not about coverage
  (Sally, 9 October 2026). Name the places the reader knows and the prose
  compares; in a figure for the County, Virginia's places, as many as fit.
  A second panel names only what it adds that the first does not: the
  southeastern panel names Arlington alone, because what it adds is where
  Arlington stands among places its size, not which peer is which. A dot is
  never named only to stand for its cluster.

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
- **A figure with few categories along the axis may take less than the full
  width.** `charts.figure(profile, of_width=...)` takes the fraction, and the
  fraction is a name in `style` — `style.NARROW` — never a number in the
  figure script, so the narrow figures stay one size as a set.
  `residents_by_age` is the standing example. The height still comes from
  `style.PLOT_ASPECT`, so the plot keeps its shape.

- **A timeline of events, whose y axis carries no measure, takes
  `style.STRIP`** through `charts.figure(profile, aspect=style.STRIP)` and
  draws with `charts.events()`. `candidates` is the example.

## Axes

- The y-axis ends on a round tick, not just clear of the data.
- **Every bar is drawn whole.** Pass the bar width to
  `charts.years(..., bars=...)`, which widens the limits to clear half a bar
  at each end.
- No y-axis label that repeats the panel title.
- Tick density has to be legible at the profile's width: name every twentieth
  year and let the minor ticks mark the rest. Never rotate the labels.
- **Where the labels do fit, name them all.** A figure at `style.NARROW`, or
  any axis with few enough years, takes `charts.years(..., dense=True)`,
  which names every one at `style.DENSE_TICKS`. This is the only place type
  is stepped down, and it is never a reason to shrink a legend.
  `residents_by_age` is the standing example.
- **Both panels of a figure label their axes the same way.** A bar panel does
  not need a label under every bar to be readable; the minor ticks locate the
  unlabelled ones.
- Where the labelled interval is wider than the data's interval, add unlabelled
  minor ticks at the data's interval, so a reader can find 1890 or 1910 on an
  axis that only names every twentieth year. `charts.years()` does this.

## Maps

- **A map draws the territory its chart counted.** The district map beside
  `residents_by_district_race_adults` draws the county as it stood when the census
  counted it, with the land Alexandria annexed in 1915 and 1930 shown inside
  the districts that held it, not today's outline (Sally, 6 October 2026).
  The same rule as the denominator: the land is the population.
- **A map colours only what its point is about.** The districts share one
  neutral ground, `style.MAP_GROUND`, are drawn whole as they stood with a
  dark edge, `charts.edges()`, and are named at their centres,
  `charts.area_names()`; the annexed land is the only colour, two tints of
  one hue, and the fill changing is its only edge (Sally, 8 October 2026).
- **No blue fill on a map**: it reads as water (Sally, 8 October 2026).
- **A shape traced from a published map is fitted to a modern outline the
  map also draws**, and the fit's miss is stated in each vertex's basis, as
  the 1907 sheet's corners and the city of Alexandria's boundary maps are.
- **No place names unless a name can be placed truthfully.** A
  neighbourhood is a region, not a dot; a stream or a road is a mark the
  legend has to answer. The caption names the river at the frame's edge.
- **The legend sits inside the frame where the shape leaves a corner
  empty**, stacked, since a map has no axes to keep clear of:
  `charts.map_legend()`, a heading with its swatches under it.

## Legend

- One legend for the whole figure, not one per panel, where one is needed.
- **Related swatches sit together, indented under their parent.** Two tints
  of one hue read as parts of that category only when the legend shows them
  that way: "annexed by Alexandria", then 1915 and 1930 beneath it (Sally, 6
  and 8 October 2026).
- One row, in stacking order, below the figure and outside the axes.
  `charts.legend()` puts it there.
- **Centred on the plot region, not on the canvas.** `charts.fit()` does this
  for every figure; nothing in a figure script sets it.
- **A wrapped legend reads left to right along each row**, not down each
  column, which is matplotlib's default. `charts.legend(fig, entries, ncol=)`
  does the reordering; nothing in a figure script arranges entries.
- If labels are too long for one row, shorten the labels first. Where there
  are still too many entries to read across one row — seven age bands, or a
  narrow figure — **break it into two rows rather than shrinking the type or
  cramming the swatches.** `charts.legend(fig, entries, ncol=...)` sets the
  entries per row. Never shrink the type.
- **A map names its districts on the map and keys only its colour.** The
  district names sit at each district's centre; the annexed land, too small
  and too split to name in place, is keyed in the corner (Sally, 8 October
  2026, replacing the 6 October rule of no legend on a map).
- A category with no data anywhere gets no swatch. An empty legend entry reads
  as a sliver too small to see rather than as zero, and the absence belongs in
  the prose. Test on the data, not on the category name.

## Colour

- The palette is `style.OKABE_ITO`, assigned per subject in `style.py`. Do
  not introduce a colour that is not in it, and do not move a colour between
  groups without reading `docs/figures.md`: several are placed so that
  nothing shares a colour with anything a reader meets beside it.
- **A bipolar scale is not an ordered one.** A five-point agreement or
  satisfaction scale takes `style.AGREEMENT`: two hues from Okabe-Ito for the
  two ends and the no-evidence grey for the middle, never the sequential ramp.
- **A share from a sample carries its interval** where the groups being
  compared differ in size, through `charts.hwhiskers()`, which holds the
  interval inside the scale.
- **Ordered categories take `style.ramp(n)`; unordered take Okabe-Ito.** Age
  and residence coverage are ordered. Never define a ramp in a figure. Lines and dots take
  `style.line_ramp(n)`, whose lightest step reads on white (9 October 2026).
- **Where a category's definition changes mid-figure, the legend does not
  relabel silently.** `residents_by_race` says "not Hispanic" (`style.RESIDENTS_CROSSED`)
  and rules off 1980; the Board figures keep `style.RACE`.
- **Race and gender together: a man takes his race's hue and a woman its
  darker shade, White women the taupe** (`style.RACE_GENDER`, Sally, 9
  October 2026). The label is `Latino` or `Latina`, not `Hispanic or Latino`, on the
  members figures (`Latino men`, `Latina women`). The legend is
  `charts.legend_grid()`, three columns, Black, Latino, White, men above
  women. The stack is ordered by size, smallest group at the bottom.
  Before 1932 the Board is lanes by district, `charts.district_lanes()`.
- **No textures.** Distinguish with colour. Tested on the district map, 6
  October 2026: hatching for the two annexations was rendered and declined
  for two tints. A filled dot against an open
  ring of the same colour is a fill, not a texture: `style.CANDIDACY`.
- **A series the sources report at some censuses and not others breaks,
  and a dotted segment bridges the gap** (`charts.lines(..., bridge=True)`),
  so the silent census reads as a gap in the record, not the end of a series
  (Sally, 4 October 2026). Never draw the solid line through it: that asserts
  a path nothing recorded. `residents_by_district_race_adults` is the standing
  example, and the caption says what the gap is.
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
  Latino`, `Asian & Pacific Islander`.
- **State a qualifier once, in the caption, not in every key entry.** On the
  census basis every group except Hispanic or Latino is non-Hispanic; the
  legend says `Black`, `White` and so on, and the caption says "groups other
  than Hispanic or Latino are non-Hispanic".

## Process

- **A new or reshaped figure is iterated with Sally before it is finished.**
  A first render rarely matches the finished figure (Sally, 7 October 2026). So the
  order is: build the quickest honest render, show it as a picture, wait,
  change what she says, show again, and only when she says it is right do
  the finishing - caption notes, `docs/figures.md`, the full build, the
  merge. A thread that renders once and runs to merge has spent its budget
  on the wrong picture. The brief for a figure thread says so; "merge when
  done" is not the default for figures.
- **While editing one figure, run only that figure:** `bash run.sh <figure>`,
  about five seconds. It skips the tests and the data stages when nothing
  they depend on has changed. The full `bash run.sh`, about a minute, is for
  once before a commit, and after any change to the style layer.
- **A request that is a choice is answered with both pictures.** "Start it
  in 1950 instead of 1930" is a decision the person asking wants to make by
  looking. Build the alternative, copy its png out of `figures/` to a
  scratch path, put the script back, and show the committed version and the
  alternative side by side. Change what is committed only after they choose.
- **Review a figure in two passes before showing it, in this order.** First
  legibility: every label, tick and line reads at the size the paper prints
  it, nothing collides, every name is unambiguously its own dot's, what
  should match does (two breaks, two axis labels), and nothing claimed about
  the picture (two gaps equal, a label beside its dot) is asserted without
  being measured. Then storytelling: the figure's one-sentence point is what
  a reader sees first, and the named marks are the ones that point and this
  reader need. A figure can pass the first and fail the second. A picture
  with a fault you know of is not sent; fix it, or name it at the top.
- Render the figure, look at the image, and show it, before saying anything
  about it. Check it against this file first. Every rule above has been broken at least once by
  not looking.
- Every revision goes to Sally as a picture, in the message, not as a path
  or a description of what changed. A thread on 6 October 2026 described
  three rounds of label changes and she had to ask to see them.
- A figure proposed to her comes as two or three rendered options, not one
  sketch and a question; she chooses by looking ("see more than one
  option", 6 October 2026). An unrequested mark (a stream, a dot for a place)
  is a question the legend or caption has not yet answered, so nothing goes
  on a proposal that the legend or caption does not answer.
- Where a figure sits in the paper is settled before it is built in place.
  The district map moved three times on 6 October 2026 and each move was
  a merge; propose the placement with the picture, build once she says.
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
