# Figures

How the figures are drawn and why: the reasoning behind every visual
convention in `style/` and `style/charts.py`, and behind each figure
script's form. Present tense; how a decision was reached is in the git
history. The rules themselves are in `.claude/skills/figures/SKILL.md`,
which states them and points here.

The conventions are the Urban Institute's data visualization style guide,
<https://urbaninstitute.github.io/graphics-styleguide/>, loaded as rcParams
from `style/urban.mplstyle`. Where this project departs from Urban, the
departure is listed here.

## Departures from Urban

**The palette is Okabe-Ito, not Urban's.** Urban's categorical colours are
designed for the web, not for colour vision deficiency. Okabe and Ito's set
("Color Universal Design (CUD): How to make figures and presentations that
are friendly to colorblind people") is built for exactly that, and holds
four separable hues under simulated deuteranopia where Urban's magenta goes
olive. It gives up some tonal spread in greyscale, which costs nothing
unless the memo is printed in black and white.

**The legend sits below the figure, not above it.** Urban stretches it
across the top. Several figures carry a note above the plot (the 1932
rule), and the two would compete for the same band.

**No group holds the lead colour.** Urban's hierarchy runs blue first, then
yellow and magenta, with grey for residuals. Applied straight down a stack
about racial representation that hands one group the primary colour, which
is a claim rather than a convention. So the neutral goes to the largest
group, White, which is the background mass on every one of these charts,
and the saturated hues go to the groups the section examines. Gender
follows the same logic: men are the mass and take the neutral.

**Legend text is the size of axis labels.** Urban puts legend text a point
above axis labels, to build a hierarchy. Here a legend entry and a tick
label both name a mark and neither outranks the other.

Sources and notes go below the figure in the document, as Urban has them:
here, in the LaTeX caption. The one exception is an annotation attached to a
mark, such as the 1932 rule, which stays in the panel.

## Colour

Two near-neutrals are added to the set. The sand, `#D9D3C4`, is the mass:
White residents, and men. The grey, `#8C8C8C`, is the residual: Other or
Multiracial, and independents. The sand is tuned as a filled area and is
close to invisible as a stroke on white paper, so a line chart uses a darker
taupe of the same hue, `#A3997F`, and White is recognisably the same
category in both.

Colours are assigned per subject rather than through numbered slots, and
nothing shares a colour with anything it appears beside.

- **Race.** Black orange, Hispanic or Latino bluish green, Asian and Pacific
  Islander blue, White sand. Asian and Pacific Islander takes blue rather
  than reddish purple because the reddish purple carries women on the
  gender chart, and the two should not read as the same category across a
  section.
- **Age.** The county's seven age bands are ordered, and seven unrelated
  hues would say they were not: a reader would have to consult the legend
  to know which band sits next to which. They take one hue that darkens
  with age, `#DEDBEF` to `#332B62`, the way the residence diagnostic takes
  one green that darkens as the place is named more exactly. The hue is
  indigo because no other subject uses it: age is the only figure in the
  report where a band is neither a race, a party nor a gender, and it
  should not be mistaken for one. The near-neutral rule is set aside, as it
  is for party: there is no largest group holding the mass here, since the
  bands are of comparable size and the darkest is not the biggest.
- **Gender.** Women reddish purple, men sand. Urban's guide says: "Urban
  tries not to use color palettes that reinforce gender or racial
  stereotypes (e.g., pink for women and blue for men)." Half the pairing
  goes: men take the same near-neutral the largest group takes everywhere
  else, so the figure reads the way the race figures do, the mass as
  backdrop and the subject carrying the colour, rather than as a gendered
  pair.
- **Growth.** Two counts of people, no categories: population dark grey
  `#5C5859`, residents per seat vermilion. Not Okabe-Ito's blue, which is
  Asian and Pacific Islander on the race charts; the growth figure comes
  first in the report, and a reader would meet the colour as a series
  before meeting it as a category. Vermilion also carries Republican on the
  party chart, the one reuse in the set; it costs nothing because the line
  is named where it runs.
- **Turnout.** The presidential vote is the reference the Board's voters are
  read against, and takes the growth figure's dark grey. The Board's voters
  are four lines, one per place in the four-year cycle, from the top of the
  ticket down: vermilion for the presidential year, then orange, bluish
  green and black in falling order of turnout. Each is a category elsewhere
  in the set and none reads as one here, because the lines are named in the
  legend and never share a page with a race chart.
- **Party.** The two partisan hues are the ones readers bring with them, at
  Okabe-Ito's values: sky blue for Democratic, vermilion for Republican.
  Neither is Okabe-Ito's blue, which is Asian and Pacific Islander. Yellow
  for ABC, the nonpartisan coalition allied with the Democrats, sits between
  the two on the stack. The near-neutral rule is set aside here
  deliberately: partisan colours are a convention readers already hold, and
  a sand band labelled Democratic would be read against it. Independents
  take the residual grey; "not recorded" takes a lighter grey still,
  `#DDDDDD`, so that an absence of evidence never reads as a category.
- **Voters.** The presidential vote uses the party chart's colours, with
  "other" in the independents' grey. The County Board vote has the seat
  chart's bands in the seat chart's order, with "other" where "independent"
  stands there.
- **Peers.** Cities dark grey, counties the sand stroke, Arlington the
  per-seat vermilion. The two neutrals are close on purpose: the kind of
  government is context, and a second saturated hue would compete with
  Arlington, which is what the figure is for.

## Stacking order

Axis upward. Race: Black, Hispanic or Latino, Asian and Pacific Islander,
then White; on the residents figure the residual sits between the counted
groups and White, because it is another kind of not-White and belongs with
them. Above the sand it splits the non-White population in two and
understates how much the county has diversified.

Gender: women, then men. The same shape as race, and for the same reason:
the category the sand marks - the majority - takes the ceiling, and the
smaller category sits on the floor where its band is measured against the
axis rather than floating on top of another band. Ordering the legend some
other way, alphabetically say, would put men first here and leave race
ordered the other way, so the two demographic figures would stop reading as
one pair.

Age: youngest at the base, children first, so the stack runs the way the
axis does and the band a reader is looking for is where its number puts it.
With the hue darkening as the band ages, the stack also runs light at the
floor to dark at the ceiling, which is the order a reader expects of a ramp.

Party: Democratic, ABC, not recorded, independent, Republican. The two
parties take the two edges of the frame, so each category keeps one place
on the page for the whole run and a majority reads as the block that crosses
the middle. Sorting each year by size puts the Democratic band on the floor
in one decade and on the ceiling in the next.

## Labels

Legend entries capitalise proper nouns and nothing else. Racial and ethnic
identifiers are proper nouns and keep their capitals; "women" and "men" are
not, under anyone's convention, and do not. "Multiracial" keeps its capital:
it is a racial identifier and belongs with Black, White and Hispanic or
Latino, and a lowercase entry among the four it is the residual of would
read as a lesser category rather than a smaller one. Both Black and White
are capitalised: APA and AMA capitalise both, and Urban's lowercase "white"
beside "Hispanic or Latino" reads as a typo rather than as a position. Axis
labels and panel titles are lowercase, which is Urban's sentence case.

Category names are the Bureau's own wording, with no slashes. "Asian and
Pacific Islander" is what the 1980 dictionary calls the category; from 2000
the Bureau splits it, and this series combines the two, so the older name is
the accurate one. "Hispanic or Latino" is the Bureau's wording from 2000;
1980 says "Spanish origin". The ampersand in the legend is for width, since
the legend is one row. "ABC" rather than the full name for the same reason;
the caption expands it.

The residual band is "Other or Multiracial", not "unreported": nothing in it
is. Before 1980 it is people in race categories the source did not break
out, never above 0.12 per cent of the county; from 1980 it is American
Indian and Alaska Native, some other race, and two or more races, all
counted, and in 2020 two or more races is 12,196 of its 13,945.

A qualifier is stated once, in the caption. On the census basis every group
except Hispanic or Latino is non-Hispanic; the legend says "Black", "White"
and so on, and the caption says so.

## Legend

One legend for the whole figure, built from patches rather than collected
from the axes, so a figure with two panels showing the same groups gets one
legend rather than two. One row, in stacking order, which is the order Urban
asks a legend to follow. Wrapped onto more rows where a single row would be
read by scanning a line of text rather than glanced at: five long category
names, or more entries than a row can hold at all, which is what seven age
bands on a narrow figure are. Two rows of four and three is a shape the eye
takes in at once; seven entries edge to edge is a sentence. The type is
never shrunk to buy the row back, because the legend is the one part of a
figure a reader has to read rather than see.

The legend is centred on the plot region rather than on the canvas. Centring
on the canvas counts the y-axis label and the tick labels as part of what to
centre under, and since both sit on the left, the legend lands left of the
marks it names — far enough on a narrow figure to read as a mistake. The
plot's own span is what a reader sees as the figure, so that is what the
legend is hung beneath. `charts.fit()` places it, after the plot is sized,
because the plot's position is not known until then.

No legend where the lines can be labelled directly. A direct label sits
beside the point it names, at that point's height, inside the axes. Urban
puts line labels at the far right just outside the plot; that needs headroom
past the last data point, and a label long enough to be readable needs
enough of it to visibly stretch the axis, which distorts the series to buy
room for its own caption. Which side of the point depends on the line: to
the left, ending at the point, for a line with empty space behind it; above
or below, for a line another runs close to. Wrapping the name over lines
halves the room it needs. A label is one block of a few short lines, not one
long line, because a long line is read rather than glanced at.

## Size and margins

Every figure is exactly the profile's width: 6.25 inches for the memo's PDF,
Urban's full-width figure, and 10 inches for the deck's PNG, with every type
size stepped up by 1.45 so the type holds the same proportion to the frame.

One exception, added when `residents_by_age` was drawn. A figure whose axis
carries only a few categories — five censuses of stacked bars — looks
wrong at full width: the bars become slabs with as much white between them
as ink in them, and the figure reads as though a series has been left out
of it rather than as though it is complete. Such a figure takes
`style.NARROW`, 0.7 of the profile's width. The fraction is a name in
`style` rather than a number in the figure script, so that the narrow
figures stay one size as a set the way the full-width ones do, and the
plot's shape is still solved from `PLOT_ASPECT`, so it is the same plot,
smaller. Two sizes is a set; a size per figure is not, and the rule stays
that a figure takes the full width unless it is one of these.

Three things want to be constant across the figures and only two can be:
the canvas width, the margin of white around the edge, and the plot region.
They are tied together, and the label block is not the same width in every
figure, because "0" to "5" on a seat chart is narrower than "250,000" on a
population one. The canvas width and the margin are held; the plot absorbs
the difference. Plots come out within about 7 per cent of each other in size
and identical in shape, which is invisible between figures that never sit
side by side, and every figure is still exactly one text width.

The plot's shape is fixed per profile: 2.2 times as wide as tall for the
memo, 3.0 for the deck. Its height is
solved from that rather than set, because a figure's height is its plot plus
whatever a title, a legend and an axis label need, which differs per figure.
Fixed heights went stale as figures were added. Equal plots, not equal
canvases, are what a reader sees: on a slide a figure with a taller plot
fits by height and is letterboxed beside its neighbours.

The two differ because the destinations do. The memo page is portrait and a
2.2 plot sits well on it. A slide's content column is 1664 by 824 pixels,
about 2.0 to 1, and what is placed on it is the saved file, not the plot: the
title, legend and axis labels around the plot are stepped up by 1.45 with the
type and take a larger share of a 10-inch canvas than of a 6.25-inch one. At
2.2 the deck's PNGs came out near 1.6 to 1, about 300 pixels narrower than
the space they were given, and the decades on the two-panel figures ran into
each other. 3.0 lands the figures with a legend at 1.96 and the two-panel ones
at 1.9; those without a legend come out wider, and are fitted by width. The
figure to size against is the file, so the value is worked back from the
rendered aspect rather than chosen from the plot alone. The narrow figure
(`NARROW`, 0.7 of the width) takes the same plot shape and needs no value of
its own. The two-panel figures label the census years every 40 rather than
every 20, since each panel is under half the canvas.

The margin is 0.037 of the width on all four sides, measured to the first
ink rather than to the plot frame, because what a reader sees as the edge
of a figure is where its ink starts. Pinning the frame instead reserves the
width of "250,000" on a chart that prints "0" and carries the difference as
a visible gap. One number for all four sides: set separately, the figures
carried two and a half times more white on the left than on the right.
Constrained layout pads the top and bottom by different rules, so the
vertical margins are measured from the rendered white and fixed directly.
The legend is re-placed after the plot is sized, 0.2 inches below the
lowest ink, because whatever distance it was first given no longer means
anything by then.

## Chart types

**Two-panel figures go side by side**, not stacked, because a composition
panel needs to be taller than it is wide when its early values are small.

**Stacked bars** for composition at intervals, at a width about twice the
gap between bars, which is Urban's rule. No band is textured: a single
hatched band among flat ones reads as emphasis, and a residual is the last
thing that should be emphasised. The axis clears half a bar at each end, so
that the first and last bars are drawn whole: a bar centred on the first or
last year is otherwise sliced by the frame, and a sliced bar reads as a
narrower category rather than as a clipped one. It only bites on a short
series — over 150 years the ordinary padding is already wider than half a
bar — which is why `residents_by_age` found it and the others did not.
`charts.years(..., bars=...)` takes the width and widens the limits.

**Stacked step areas** for composition over continuous years, each year's
value spanning the year, filled run by run so a year the source does not
report stays a gap rather than being drawn through.

**Lines** carry a marker on every point where the points are the
observations, one per census or one per election, and none on an annual
series, where ninety dots are noise.

**A series that leaves the axis** is clipped, with a triangle on its last
on-scale point, so the exit is a statement rather than a line that stops
for no reason. A triangle, not an arrow with a shaft: a shaft is a second
stroke at its own angle, which reads as another series.

**The 1932 rule** marks the Board's expansion from three to five seats and
the end of magisterial districts. It is drawn identically wherever it
appears, with its note above the top of the frame: inside the axes it would
sit on whatever the chart has drawn there, which on a filled seat chart is
a solid band. On a 0-5 seat axis the note states the numbers, since the
expansion is what the axis shows; elsewhere it is context. The note is drawn
once per figure even where the rule is on every panel.

**Year axes** name every twentieth year, anchored on the last so the most
recent census is named, with an unlabelled tick at each census between.
Decades collide at 6.25 inches, and rotated labels are slower to read.

## Each figure

- **residents_per_seat.** Two series on one linear axis. Both are counts of
  people, so the vertical distance between them means the same thing
  everywhere on the page, which a second y-axis would not give: the Board
  held three seats before 1932 and five after, so no single right-hand scale
  is right for the whole series, and picking one decides which era looks
  like the exception. "Seat", not "member": the denominator is seats that
  exist, and the two differ where a seat sat vacant, which the label "residents per
  seat" says and which keeps a vacancy from drawing a spike. A cube-root-law benchmark is not drawn: the law is
  descriptive, not normative, its reference class is national parliaments,
  and as drawn it implied a 62-member Board (`peer-localities` in
  `docs/questions.csv` is the comparison the report might want instead).
- **residents_by_race.** Counts as unstacked lines, because a stacked band
  of height zero and one that has not started are the same picture, and a
  line simply begins the year the Census first reported that group. White
  is clipped at 50,000 and marked where it leaves, which keeps the decades
  when the groups were comparable without giving three quarters of the axis
  to one series. Shares as stacked bars. Nothing marks the 1980 change of
  basis: the change is real but small, and a rule across the figure claims
  more visual importance for it than it has; the caption carries it, and
  the labels are the same either side.
- **residents_by_age.** One panel of stacked bars, shares rather than
  counts. A counts panel was drawn first and dropped: once the shares are
  seen to be nearly flat, the counts panel only restates the growth that
  `residents_per_seat` already shows, and a second panel that repeats a
  figure the reader has met is worse than no second panel. Six lines were
  tried before the stack and fail for a different reason: the bands are of
  comparable size, so five of them run together in a band a few thousand
  people deep, and a ramp chosen so that neighbouring bands read as
  neighbours is exactly the wrong palette for lines that cross.

  Children are a band, though they cannot vote. They are a seventh of the
  county and no one on the Board represents them in the sense the rest of
  this section measures, so leaving them out would make the figure a
  picture of the electorate when what the section is about is the county.
  For the same reason the denominator is every resident, not every adult.

  It begins at 1980 while the Board figures begin at 1870, and the two are
  not drawn on a shared range. Nothing is lost by that. The Board series
  reaches back to 1870 because a Board member is one person whose birth
  year can be found in a census sheet or an obituary; a county age
  distribution has to come from a published table, and the Bureau's
  machine-readable county tables begin with the 1980 Summary Tape File.
  Earlier censuses did print county age tables, but only in the bound
  volumes, so carrying the series back would mean keying them in the way
  the 1870-1890 totals were keyed in. That is a job the report has not
  asked for; `adults-before-1980` in `docs/questions.csv` holds it, for
  this figure and for the turnout one. The figure is a benchmark for the
  residents section and is never put on a panel with the Board's ages:
  there is no defensible right age for a Board member, and a shared panel
  would imply there is. Two figures in two sections, each on the range its
  own sources support.
- **board_race, board_gender, board_party.** Seat counts rather than
  shares, so the 1932 expansion is legible on the axis. All bands are drawn,
  men and White included: they are the denominator, and without them two
  seats of five and two of three look the same. A category holding no seat
  in any year gets no band and no legend entry, because an empty swatch
  reads as a sliver too small to see rather than as zero, and the absence is
  a finding for the prose. The test is on the data, not the category name.
- **board_age_coverage.** A diagnostic: of the members sitting on 1 July
  of each year, how many have a birth year and how many do not, as a
  stacked step area on the seat axis, so it reads like the seat figures
  and a reader can see at once which years the age figure can stand on.
  Counts rather than a share, because two of three and four of five are
  different situations and a share would say they were the same. With a
  birth year takes the sand, without takes the no-evidence grey, as
  "not recorded" does on the party chart. Years with no roster are gaps.
- **board_residence_coverage.** A diagnostic to show the County: of the
  members sitting on 1 July of each year, how exactly a home is known, as a
  stacked step area on the seat axis like the age coverage. One hue, darkest
  green for a street address, then a street name, a neighborhood, then one
  shade for a north/south side or a magisterial district of Alexandria
  County, and the no-evidence grey for no location; darker means closer to
  the address a payroll or filing record would give. The clean table keeps
  side and district apart, but they are the same grade of knowledge, which
  half of the County, and differ only in the era of the source: a side comes
  from twentieth-century reporting, a district from the 1880–1910 census
  sheets, which name the district and leave the street column blank. So the
  figure reads them as one and drops a step from the ramp. A member counts
  at the most exact place any source gives, whenever dated, so it can show a
  member as known from a source written after their service
  (`residence-after-service`). Years with no roster, 1912 to 1931, take
  their three seats from the seat table and count as no place found, so the
  Board's size is unbroken.
- **board_age.** A Lexis diagram, age against year, the standard demographic
  form for it. Behind, the youngest-to-oldest span of the members sitting
  on 1 July of each year, as a step area; over it, one diagonal per member
  from the age they arrived to the age they left. Terms less than twelve
  months apart are one stroke, so a member's stroke is their tenure; longer
  gaps (six cases of two years or more) are two strokes. A member with no
  birth year does not appear, and `board_age_coverage` in front of it says
  how many. The question is what range of ages the Board holds at a given
  moment, so the band is the minimum and maximum rather than a quartile
  range or three lines: when the oldest member leaves and no one older
  replaces them the ceiling drops, and that step (1997 to 1998) is the
  finding, which a smoothed band hides. The band is a step because each
  year's value is the Board on 1 July, and 1 July because a Board seated
  in January and reshuffled by a November election is the same people at
  mid-year; which months a term held comes from `board_members.csv`, so the
  figure and the seat table agree on it, and a term with no recorded end
  holds to the end of its first year there. A year is drawn only when all
  but at most one sitting member has a birth year.
  A stroke's age is the year less the birth year less a half: a birth year
  alone puts the birthday at mid-year, so the stroke crosses the band's edge
  values on 1 July. The stroke still runs smoothly through a band that steps
  each January, so an edge stroke sits up to half a year off the band's
  edge.
  The figure starts in 1932. Before it the Board has three seats, the rule
  is met in eight scattered years and 40 percent of member-years in 1900-31
  have no birth year, so a band there would be fragments; the 1932 rule
  therefore sits at the left edge and needs no note. The band is five seats
  wide throughout. A member seated before 1932 who was still sitting after
  it is clipped at the edge, and one who left earlier is not drawn. The
  band takes the near-neutral sand and the strokes the growth figure's dark
  grey, since nothing is a category, with no new colour. Strokes are thin
  and opaque: at 60 percent opacity a stroke reads as dashed where it
  crosses the band's edge, and around 2013, where four lines sit inside ten
  years, thin strokes separate without it. The axis runs 0 to 100, so the
  age is read from zero, and every decade is labelled: the axis is 95 years
  long, and the decades do not collide at the profile's width, unlike the
  1870-2026 axes that step by twenty. There is no legend and no direct
  label; the caption says what band and stroke are.
- **voters_president.** Stacked bars, because an election is a point in
  time; a step would claim the share held for four years. Incomplete years
  are left out rather than drawn short.
- **voters_board.** A step area, because the series is annual. A separate
  figure from voters_president rather than a panel, because they are not the
  same voters and a shared frame would say they were.
- **turnout.** The Board's voters as four series, one per place in the
  four-year cycle, each every fourth year. Drawn as one annual line the
  series is a sawtooth, and the teeth are the ballot, not the Board; drawn
  as four, the trend in each is visible. The presidential vote is the
  reference line. The district-era counts and the registered voters are in
  the table and not drawn: the registration series is fifteen years long,
  and the prose can state it in a sentence. The share panel starts where its
  denominator does, so its frame is not half empty.
- **board_peers_residents, board_peers_density.** Arlington beside every
  Virginia city and county of 100,000 or more, two separate figures rather
  than panels, because each answers a different question about who
  Arlington's peers are: places its size, and places as dense. Both axes
  start at zero; the residents axis breaks so that Fairfax, at 1.15
  million, stays in view without pressing the other seventeen into a third
  of the width. Squarer than the time series (`style.SQUARE`), since both
  axes are measures and neither is time. Dots are one size: area was tried
  for population and for density, and in both a reader could not read the
  third measure off it. Residents per member rather than members per
  resident, to match residents_per_seat. Names are placed by
  `charts.place_labels()`: every name sits nearer its own dot than half the
  distance to any other, touches nothing, and a name beside a dot is
  centred on it at three or nine o'clock; each cluster carries at least one
  name, and a dot too crowded to name beside it (Alexandria, on the
  7-member row) is named with a short leader.

## Output

Both backends stamp the time of the run into the file, so the stamp is
suppressed: otherwise an unchanged figure is a changed file, and `figures/`
is committed precisely so a change shows up as a reviewable diff.
