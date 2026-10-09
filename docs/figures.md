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

**The paper has two type sizes, not Urban's ladder.** Urban's guide sets chart
text from 8pt to 12pt and says nothing about body text, which lives in its Word
templates. Here the body is one size, and the notes under each figure and the
footnotes share a second, smaller one. Figure titles and headings are bold at the
body size, so weight and not size marks a level.

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

**Whether the categories are ordered decides the palette, not the topic.**
Ordered categories take one sequential ramp, `style.SEQUENTIAL`, drawn on by
`style.ramp(n)`: adjacent bands read as adjacent, and the darker end is the
more of the thing. Unordered categories take Okabe-Ito, where no hue implies
a rank. A figure never defines a ramp of its own.

- Ordered: `residents_by_age` (young to old), `members_residence_coverage`
  (how exactly a home is named), and `elections_turnout_board` (what led the
  ballot, by falling turnout). All three draw from the one ramp, so they read
  as a family; the no-evidence grey in the first two stays outside it, since
  an absence is not a step on the scale.
- Unordered, Okabe-Ito: `members_by_race`, `members_by_gender`, `residents_by_race`,
  and the party and growth figures.

- **Race.** Black orange, Hispanic or Latino bluish green, Asian and Pacific
  Islander blue, White sand. Asian and Pacific Islander takes blue rather
  than reddish purple because the reddish purple carries women on the
  gender chart, and the two should not read as the same category across a
  section.
- **Age.** Ordered: see the palette rule above. Seven bands on the
  sequential profile, `style.ramp(7)`, light for the youngest. The
  near-neutral rule is set aside, as it is for party: there is no largest
  group holding the mass here, since the bands are of comparable size and the
  darkest is not the biggest.
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
  read against, and takes the growth figure's dark grey, in both turnout
  figures. The Board's voters, in elections_turnout_board, are ordered by
  what led the ballot, not categorical, so they take `style.ramp(3)` off the
  one sequential green rather than a family of their own: darkest for a
  presidential year, lighter for a midterm, lightest for a governor's year.
  A House of Delegates year is never drawn (every one is a two-seat gap), so
  it carries no reserved fourth tint; the ramp spans exactly the three
  cycles that are drawn, for the widest separation between them (Sally, 7
  October 2026: a four-stop ramp with the lightest, most distinct step going
  to waste on an undrawn category read as too close together). Grey against
  green, so the Board reads as one thing against the
  presidential line and the three shades read as steps of one scale.
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
- **Candidacies.** One colour, the race figures' Black orange, since every
  mark is a Black candidacy and the figure sits in the race section. Won and
  lost are told apart by fill, a solid dot and an open ring, rather than by
  a second hue: a second colour would read as a second group of people, and
  the palette's other oranges and greys already mean a party, the residual
  or no evidence.
- **The magisterial districts.** Three unordered places, so Okabe-Ito:
  Arlington District bluish green, Jefferson District reddish purple,
  Washington District blue. Jefferson takes reddish purple because the land
  Alexandria annexed was Jefferson's, and on the district map that land is
  the only colour, in tints of the same hue: the line that falls fastest
  between 1910 and 1920 and the land the district lost read as one thing
  across the two figures (Sally, 8 October 2026). Purple is lighter than the
  blue Jefferson had, so the line the race section is about stands out a
  little less; the link to the map was judged worth more. Arlington District
  is not vermilion or orange, which mark the county as a whole elsewhere
  (vermilion the per-seat line and Arlington among its peers) and a Black
  member or candidate on the race charts; of the hues left, bluish green sits
  furthest from the blue beside it, where sky blue would read as a shade of
  it and yellow disappears as a line on white. The reuse of a category's hue
  costs nothing because the lines are named in the legend. The county behind
  them takes the dark grey the growth and peer figures use for a reference
  series, because it is not a fourth district but the thing the three are
  being read against; it leads the legend as Arlington County, and the
  districts follow in alphabetical order. `style.DISTRICTS` and
  `style.WHOLE_COUNTY`.
- **Land Alexandria annexed.** Reddish purple, Jefferson's line colour, at
  full strength for 1915 and thinned toward white for 1930, so the order the
  annexations happened in reads as the fade. Not blue, which on a map reads
  as water at the river's edge, and not vermilion, which marks the county
  itself. Hatching was tried and declined: a texture reads as a second kind
  of thing (6 October 2026). `style.ANNEXED`, `style.tint()`.
- **A map's ground.** The districts on a map share the sand fill
  (`style.MAP_GROUND`): they are named, not coloured, so the only colour on
  the map is the thing its point is about (Sally, 8 October 2026).
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

**Gender runs women, then men**, which is the same shape as race and for the
same reason. The category the sand marks — the majority — takes the ceiling,
and the smaller category sits on the floor, where its band is measured against
the axis instead of floating on top of another band. Ordering the legend some
other way, alphabetically say, would put men first here and leave race ordered
the other way, so the two demographic figures would stop reading as one pair.

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
is. What it holds before and after 1980, and how large it is, is in
`docs/residents.md`.

A qualifier is stated once, in the caption, where a category means the same
thing throughout. On the census basis every group except Hispanic or Latino
is non-Hispanic, but only from 1980, the first census that asked; before it
Black and White are everyone in the race, Hispanic or not. So on
`residents_by_race` the legend says "Black, not Hispanic" and "White,
not Hispanic" (`style.RESIDENTS_CROSSED`), and a dashed rule at 1980 marks
where the definition changes; the caption says what the series before it
are. `members_by_race` reads the same two labels (`style.CROSSED_LABELS`) over
the whole of 1870 to 2026. The Board's race is not a census crosstab, and
Hispanic there is from published research, not a cell, but the figure carries
a Hispanic band, so its Black and White members are not Hispanic, and the two
figures name the same band the same way. Before 1980 no one is coded
Hispanic, so the label is true there by construction.

## Legend

One legend for the whole figure, built from its own handles rather than
collected from the axes, so a figure with two panels showing the same groups
gets one legend rather than two. A swatch is a box unless the series is
drawn as a line and named in `lines=`, in which case it is a line, solid or
(if also named in `dashed=`) the figure's standard dash - `members_age`'s
county median is the case, a line series the box convention would have
misrepresented as an area. One row, in stacking order, which is the order Urban
asks a legend to follow. Wrapped onto more rows where a single row would be
read by scanning a line of text rather than glanced at: five long category
names, or more entries than a row can hold at all, which is what seven age
bands on a narrow figure are. Two rows of four and three is a shape the eye
takes in at once; seven entries edge to edge is a sentence. The type is
never shrunk to buy the row back, because the legend is the one part of a
figure a reader has to read rather than see.

A wrapped legend reads left to right along each row, as text does.
Matplotlib fills a multi-column legend column by column, so seven age bands
over two rows arrive as under 18, 25 to 34, 45 to 54, 65 and over on the top
row and the rest beneath: every other band, with the reader going down and
back up to follow the sequence. Every figure whose legend wraps here carries
ordered categories — age bands, how exactly a residence is known, the
election cycles — and their colours are a light-to-dark ramp doing the same
work. A legend that breaks the sequence while the ramp asserts it is the one
arrangement that cannot be right, so `charts.legend()` reorders the entries
before matplotlib lays them out (decided by Sally, 1 October 2026). For
unordered categories the column-major default would be no worse; the rule is
one rule because two would be a rule nobody could remember.

The legend is centred on the plot region rather than on the canvas. Centring
on the canvas counts the y-axis label and the tick labels as part of what to
centre under, and since both sit on the left, the legend lands left of the
marks it names — far enough on a narrow figure to read as a mistake. The
plot's own span is what a reader sees as the figure, so that is what the
legend is hung beneath. `charts.fit()` places it, after the plot is sized,
because the plot's position is not known until then.

## The survey figures

The survey figures run their categories down the side rather than along the
bottom. Their labels are phrases - "neutral or disagrees", "Asian & Pacific
Islander", "Transparency of the County's decision-making process" - and a
phrase along the bottom either rotates or truncates, both of which this file
rules out elsewhere. Horizontal bars take the words at reading size, and the
rows stack as far as the list is long without the plot changing shape.

A five-point agreement or satisfaction scale is bipolar, not ordered by
magnitude, so it takes two hues from Okabe-Ito rather than the sequential
ramp: blue for the two agreeing points, orange and vermilion for the two
disagreeing ones. The middle point takes the no-evidence grey. That is the
substantive claim the figure makes: on whether the Board's structure is right
for this community, three in four respondents who do not claim familiarity
answer neutral, and they are abstaining rather than occupying a midpoint
between agreement and disagreement. A sequential ramp would draw that
abstention as a middle opinion.

The three waves of the satisfaction survey are ordered, so they take the
ramp, darkest latest, and each item is one row with a rule joining its dots.
Eleven items over three waves is thirty-three bars and eleven dots-on-a-line;
the second is the one a reader can take in.

A share from a sample carries its interval where the groups differ in size
enough for the difference to matter. The ranked choice voting survey's
Hispanic respondents are thirty-seven against the White category's
four hundred and forty-four, and the weights make that gap wider still -
twenty-three effective respondents against two hundred and ninety. Drawn as
bare bars those two shares look equally firm. The interval is held inside the
scale, since a share cannot pass either end of its own axis and a whisker
through 100 per cent would say it had.

## Size and margins

Every figure is exactly the profile's width: 6.25 inches for the memo's PDF,
Urban's full-width figure, and 10 inches for the deck's PNG, with every type
size stepped up by 1.45 so the type holds the same proportion to the frame.

One kind of figure is an exception. A figure whose axis carries only a few
categories — five censuses of stacked bars — looks wrong at full width: the bars become slabs with as much white between them
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
A fixed height goes stale as soon as a figure is added. Equal plots, not equal
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

**A map's width is `style.MAP_WIDTH`**, because the county is taller than wide:
at the full width of the page a map of it would fill the page, and at the width
of the other single-panel figures it would read as a thumbnail. Its plot is the
shapes' own extent, with a degree of longitude scaled by the cosine of the
latitude, so the aspect is read off the data and not typed.

## Chart types

**Two-panel figures go side by side**, not stacked, because a composition
panel needs to be taller than it is wide when its early values are small.
The exception is a pair of scatters, which stack so that each has the full
width for its names (localities_per_member).

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

**A timeline strip** for events that are counted, not measured: one dot per
event at its year, events in the same year stacked dot on dot upward from
the axis, and no y axis, since the height of a stack is the only quantity
and a reader counts it. The stack is laid out in points, not data units, so
it keeps its shape whatever height the plot is given. A filled dot has no
white edge, unlike a scatter's: events a year apart overlap at this width,
and a white edge cuts the overlap into crescents that read as open rings.
Dots sit over the 1932 rule rather than under it. The strip is flatter than
the time series (`style.STRIP`, 7 to 1): at the time series' 2.2 a stack of
three is a thin line at the foot of an empty frame.

**The 1932 rule** marks the Board's expansion from three to five seats and
the end of magisterial districts. It is drawn identically wherever it
appears, with its note above the top of the frame: inside the axes it would
sit on whatever the chart has drawn there, which on a filled seat chart is
a solid band. On a 0-5 seat axis the note states the numbers, since the
expansion is what the axis shows; elsewhere it is context. The note is drawn
once per figure even where the rule is on every panel, and once per figure
rather than once per section of the report: a reader arriving at the third
figure that carries it needs to reorient as much as at the first, so the
repetition across figures is not repetition to remove.

**Year axes** name every twentieth year, anchored on the last so the most
recent census is named, with an unlabelled tick at each census between.
Decades collide at 6.25 inches, and rotated labels are slower to read and
make a panel look unlike its neighbour.

A figure narrow enough to hold every label names them all instead, at
`style.DENSE_TICKS`, 0.85 of the profile's tick size, through
`charts.years(dense=True)`. The general rule exists because decades collide
at the full width; where they do not collide, an unnamed bar the reader has
to count along to identify is the worse cost. The size is a fraction in the
style layer rather than a point size in a figure script, so the dense axes
stay one size as a set, and it is the one place type is stepped down: a
legend that will not fit in one row is broken into two instead, because
there the labels can be shortened and here the years cannot.

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
  and as drawn it implied a 62-member Board (localities_per_member is the comparison instead).
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

  It begins at 1910 while the Board figures begin at 1870, and the two are
  not drawn on a shared range. A county age distribution needs either a
  published county table or the schedules counted, and neither reaches
  further back without a hole: 1890's schedules burned and its published
  county table counts school, militia and voting ages only (Table 79), 1900's
  is the same (Table 11 of the Virginia school, militia and voting ages
  bulletin) and its database lacks 499 people whose ages cannot be recovered.
  1870 and 1880 could be counted from the schedules, but a bar at each of
  them with 1890 and 1900 empty between would be two islands, so the figure
  begins at the first census after the hole. 1910 and 1920 are counted from
  the schedules and 1930 on is read from the volumes and files, so the
  note says "1910 and 1920 are counted from the full-count schedules; from
  1930, the published county age tables". Eleven bars at `style.NARROW` leave
  room to name every census, so this axis is `dense` rather than every
  twentieth year. The 14 people of unknown age in 1930 are
  in no band, so that bar stops 0.05 per cent short of the top, which no
  one can see and nothing marks. The figure is a benchmark for the
  residents section and is never put on a panel with the Board's ages:
  there is no defensible right age for a Board member, and a shared panel
  would imply there is. Two figures in two sections, each on the range its
  own sources support.

- **residents_by_district_map.** The county as it stood before 1915, the whole
  Virginia side of the ten-mile square less the city of Alexandria, in the
  three magisterial districts as they stood from 1870 until 1932. It sits in
  Board Seats, where the three districts are first named, and the race
  section points back to it, since residents_by_district_race_adults names
  the districts without saying where they were. The districts share the sand
  ground and are each outlined whole in dark grey, `charts.edges()`, the
  annexed land inside them, so every dark line is a district line or the
  county's edge; the land Alexandria annexed in 1915 and 1930 is the only
  colour, and where the fill changes is its only edge (Sally, 8 October
  2026). Each district is named at the centroid of the land it kept, so
  Jefferson's name stays off the annexed land, `charts.area_names()`, which
  stops the build if a centroid falls outside its area. The two annexations
  are keyed in the lower left corner the shape leaves empty, under the
  heading "annexed by Alexandria", `charts.map_legend()`: a name set on the
  1915 piece would not fit, and a leader was a line no legend answered.
  The districts are named "Arlington District" and not "Arlington" because
  this report is about Arlington County. Nothing else is on the map: a
  neighbourhood is a region, so a dot answers wrongly, and a stream, a road
  or a railway would be a mark the legend does not answer. The city is left
  blank, which the caption says, and the Potomac is the right-hand edge.
  `style.AREA_EDGE` and `style.AREA_EDGE_COLOR` are the district edge. While
  the 1915 area waits on a decision a grey DRAFT runs across the empty upper
  corner, `charts.draft_mark()`. What the lines rest on is in
  `docs/residents.md`, "Where the lines ran".

- **residents_by_district_race_adults.** The figure the paper carries, in
  place of the all-residents version (Sally, 6 and 7 October 2026). One line
  per district over the censuses that give race below the county, the county
  behind them. A line breaks wherever a census has nothing and a dotted
  segment bridges the gap, so the break reads as a missing census and not as
  a series ending (Sally, 4 October 2026). The shares are of the men aged 21
  and over, because the passage it sits in is about who could vote, and
  family size may differ by race and children are in the all-residents
  count. Men only, since the table carries race for men and
  women but the turnout figures it sits beside count men before 1920. Four
  censuses, 1880, 1900, 1910 and 1920, with a dotted segment across the years
  between and across 1890. Arlington district's 1900 point is a share of the
  men the database holds there, which are fewer than the district's, and the
  county line breaks at 1900 for the same reason. 1870 is an open ring on
  each line, joined to 1880 by a solid segment: the volume prints race by township for all residents
  and the extract places no one in a township, so the ring is a share of
  residents of every age and sex, a different count from the line's, which the
  caption says, and the segment is solid because it joins two censuses and
  crosses no gap (Sally, 6 October 2026). The axis starts at 1870 so the ring
  sits at its own census. `docs/residents.md` has the adults table.

- **members_by_race, members_by_gender, members_by_party.** Seat counts rather than
  shares, so the 1932 expansion is legible on the axis. All bands are drawn,
  men and White included: they are the denominator, and without them two
  seats of five and two of three look the same. A category holding no seat
  in any year gets no band and no legend entry, because an empty swatch
  reads as a sliver too small to see rather than as zero, and the absence is
  a finding for the prose. The test is on the data, not the category name.
- **members_race_coverage.** A diagnostic: of the seat-years in each year,
  what the occupant's race rests on, as a stacked step area on the seat axis,
  so it reads like the seat figures and like `members_residence_coverage`, and
  a reader can see at once which years the race figure stands on a default.
  Its legend says what each shade is in words ("race from a census sheet",
  "race from the press or a profile", "assumed White, no source"), so the
  figure needs no note; it shares one figure, as panel (a), with the residence
  figure as panel (b), under one short note (Sally, 4 October 2026).
  It reads `members_by_year`, as does every figure on the seat axis, so a
  vacancy is decided once, in the clean stage, and shows as a notch in all of
  them. Counts rather than a share, because two of three and four of five are
  different situations and a share would say they were the same. Ordered, so
  the same green ramp as residence: darkest a census sheet, paler a published
  or press account with no census citation, and the no-evidence grey for the
  default. A member counts as a census sheet when any citekey in `race_source`
  is a census, whatever else is cited beside it (`race_basis` in
  `code/clean/members_by_year.py`). The grey is almost all after 1962, when no
  census is open, which is the point of drawing it: the members it covers are
  living and can be asked. A coverage figure exists for an
  attribute while more than a tenth of members rest on an assumption or lack
  a source; `code/tests.py` refuses a run.sh without one, and below that
  threshold a sentence in the write-up replaces the figure. Birth year is
  under it, so there is no age coverage figure (Sally, 4 October 2026).
- **members_residence_coverage.** A diagnostic to show the County: of the
  seat-years in each year, how exactly the occupant's home is known, as a
  stacked step area on the seat axis. It counts seat-years, like
  `members_by_race`, and not the members sitting on 1 July, so a vacancy shows
  as a gap below the seats that exist and a partial year as a fractional band;
  a 1 July count would draw a full Board through both. Its yearly total is
  asserted equal to men + women in `members_by_year`. One hue, darkest
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
  (`residence-after-service`). 1912 to 1931 reads the roster like every other
  stretch; no place has been sought for the five members the Historical
  Society's article names there, so they draw as no location found.
- **members_age.** A Lexis diagram, age against year, the standard demographic
  form for it. Behind, the youngest-to-oldest span of the members sitting
  on 1 July of each year, as a step area; over it, one diagonal per member
  from the age they arrived to the age they left. Terms less than twelve
  months apart are one stroke, so a member's stroke is their tenure; longer
  gaps (six cases of two years or more) are two strokes. A member with no
  birth year does not appear; the write-up names the few. The question is what range of ages the Board holds at a given
  moment, so the band is the minimum and maximum rather than a quartile
  range or three lines: when the oldest member leaves and no one older
  replaces them the ceiling drops, and that step (1997 to 1998) is the
  finding, which a smoothed band hides. The band is sampled by month, from
  the months each term held in `members.csv`, so the figure and the
  seat table agree on who sits when, and a term with no recorded end holds
  to the end of its first year there. A month is drawn only when all but at
  most one sitting member has a birth year.
  A stroke's age is the year less the birth year less a half, since a birth
  year alone puts the birthday at mid-year, and the band's edges are
  measured the same way, so the youngest and oldest strokes run along the
  band's edges and the band moves only when the Board changes (Sally). There
  is no legend: the caption names the
  band and the strokes (same decision).
  The figure runs from 1910 to the present, where the censuses' ages begin
  and every sitting member has a birth year but two recent ones (named in
  UNKNOWN), so the band is one continuous ribbon; the four early members
  without a birth year sit before it (Sally, 4 October 2026). Before 1932 the
  Board has three seats, not five. The 1932 rule is drawn, since it is no
  longer the figure's left edge. A member seated
  before 1932 who was still sitting after it is clipped at the edge, and one
  who left earlier is not drawn. The
  band takes the near-neutral sand and the strokes the growth figure's dark
  grey, since nothing is a category, with no new colour. Strokes are thin
  and opaque: at 60 percent opacity a stroke reads as dashed where it
  crosses the band's edge, and around 2013, where four lines sit inside ten
  years, thin strokes separate without it. The age axis runs 0 to 100, read
  from zero; the year axis steps by twenty, like the other 1870-2026 axes.

  A dashed line carries the county's own adult median age at each census
  (`residents.adult_median_age`), added once the question was not whether
  the Board's ages differ from the county's but by how much (Sally, 5
  October 2026). It is the one series in the figure that is a category
  rather than a measurement of the band or the strokes, so it takes a
  saturated colour, vermilion, where the rest of the figure is near-neutral
  - the same choice `residents_per_seat` and `localities_per_member` make for
  Arlington's own series against reference lines, even though here it marks
  the reference (the county) and not the subject (the Board); Sally chose
  it anyway; see "Colour" above for where that convention usually points
  the other way. The county's shown as a flat 18-and-over adult median, not
  a voting-age cutoff: a first attempt switched to 21-and-over before 1971
  and labelled the line "voting-age eligible", which claimed more than an
  age cutoff can support - neither sex (women couldn't vote in 1910 or the
  January 1920 census) nor disenfranchisement (poll taxes and other Jim Crow
  mechanisms through the mid-1960s) is modelled; Sally shelved the
  voting-eligibility comparison for the flat adult one on 5 October 2026 and
  confirmed the figure on 6 October (`docs/members.md`). Now that a category
  needs naming, the figure
  has a legend after all: member age, member age range, county adult median
  age, in that order, the first and last as line swatches rather than boxes
  since that is how the figure draws them (`charts.legend(..., lines=,
  dashed=)`, general enough for the next figure that mixes line and area
  series in one legend).
- **candidates.** A timeline strip of every candidacy a source says
  was a Black candidate's, in a regular or special election, filled if won
  and a ring if lost, from `candidates.csv`. It answers whether Black
  candidates ran and lost or stopped running, so the years with no dot are
  the finding and are left bare: what the sources say about each empty
  stretch, a stated negative or a record that cannot show a loss, is in
  `docs/members.md` and belongs in the caption. A primary and the general in
  the same year are one run, with the general's outcome, so they do not
  stack as two runs for one seat; a primary the candidate lost is a run
  lost and is drawn, because in Arlington the Democratic primary decides
  the seat and a figure about running and losing cannot leave Spain's 2023
  loss out (Sally). The 1932 rule is drawn, since the three losses of 1931
  are the first at-large election. One legend, won and lost, below.
- **elections_president.** Stacked bars, because an election is a point in
  time; a step would claim the share held for four years. Incomplete years
  are left out rather than drawn short.
- **elections_board.** A step area, because the series is annual. A separate
  figure from elections_president rather than a panel, because they are not the
  same voters and a shared frame would say they were.
- **elections_turnout_president.** One panel, 1872 to the present, shares
  only, since the counts say nothing the shares do not (Sally, 6 October
  2026). One grey line, the presidential vote. Three dated rules, the Walton
  Act of 1894, the constitution of 1902 and women voting in 1920, their notes
  placed not to collide, `charts.rule(tier=)`, because the 1894 and 1902
  notes cannot sit side by side on a 150-year axis without the 1920 rule
  running through one of them. The poll tax falling in 1966 is not ruled
  off, though it is sourced (docs/elections.md, *Harper v. Virginia Board of
  Elections*): the recovery is already underway by then, so the line shows
  no kink there for a rule to anchor, unlike the other three (Sally, 7
  October 2026). The denominator is men 21 and over through 1916, everyone
  21 and over from
  1920 and 18 and over from 1971, a count at every census and a straight line
  between; nothing marks 1971, which, as with residents_by_race at 1980, is
  real but small, and a rule would claim more for it than it has. The caption
  carries it, and that the denominator is every resident of voting age,
  citizen or not, disfranchised or not. This is the half of the old single
  figure (Sally, 7 October 2026: cut at 1932) that Race's "A Shrinking
  Electorate" reads: its point is the collapse after 1894 and 1902 and the
  long recovery, and the 1876 point, the left edge, is its baseline before
  the collapse.
- **elections_turnout_board.** One panel, 1932 to the present, the other half
  of the same cut. The presidential vote is one grey line throughout and the
  thread of the figure; the Board's vote is `style.BOARD_FAMILY`, three
  shades off the one sequential green ramp (`style.ramp(3)`, Colour above),
  by what led the ballot, presidential, midterm and governor's year, darkest
  first, drawn only in years with one seat on the ballot. Grey against green
  so the Board reads as one thing against the presidential line, three shades
  of one ramp so the trend in each cycle is visible and the three read as
  steps rather than three unrelated hues; drawn as one annual line the series
  is a sawtooth, and the teeth are the ballot, not the Board.
  A two-seat year is a gap, not a floor, because it records votes and not
  voters; from 1943 that is every House of Delegates year, and the caption
  says so. No rule marks 1966: this section is not making a voter-suppression
  claim, and the poll tax, like the Walton Act, the constitution and women
  voting, is the president figure's (Sally, 7 October 2026). The five
  district-era squares the pre-1932 figure once added up by district are the
  president figure's too. The legend is flat, `charts.legend()` with
  `lines=`, one row of four: the president line and the three Board shades
  each named for what it is, "Board, presidential year" and so on, rather
  than stacked under a heading, which read as a lot of white space for four
  things (Sally, 7 October 2026). `style.BOARD_FAMILY` has no entry for a
  House of Delegates year: no one-seat year is a delegates year, so the ramp
  spans only the three cycles that are drawn rather than reserving a fourth,
  more-distinct stop for a shade nothing uses (Sally, 7 October 2026). The
  squares that once carried that shade are gone with the pre-1932 range. The
  registered voters are in the table and
  not drawn: the series is fifteen years long, and the prose can state it in
  a sentence. The axis reads from 1930, a decade before the first point,
  labelled every ten years, `charts.years(step=10)`: the Board's five seats
  were filled all at once in 1931, 1935 and 1939, so no Board line starts
  until staggered single-seat elections begin in 1940, and a reader who does
  not already know that would otherwise read the empty decade as missing
  data. A dashed rule marks 1940, the first staggered election, not the 1938
  referendum that approved it (Sally, 7 October 2026: the line is where the
  Board line starts, not where the vote happened), placed `ha="left"` because
  it sits too close to the axis's own start for a
  note running leftward to fit. The caption says so (Sally, 7 October 2026).
  The two pre-1932 figures and the by-district figure stay retired (Sally, 6
  October 2026): the first two are the president figure's left third, and the
  third's one finding, that Jefferson fell steepest, is a sentence in the
  prose with its own built numbers. The figure sits in Election Method under
  Staggered Terms, as the electorate half of that subsection's claim: seats
  elected a year apart are chosen by electorates of different size, which is
  a 1932-on sawtooth, not a 150-year collapse.
- **localities_per_member.** Arlington beside its peers on one measure,
  residents per member against residents, in two panels that share a legend:
  (a) every Virginia city and county of 100,000 or more, (b) every
  southeastern city and county of 150,000 to 300,000. Each panel answers
  a different question about who Arlington's peers are (Virginia's larger
  places; places its size across the region), and on the same measure a
  reader carries what (a) shows into (b). The two panels were two figures,
  and (a) once set members against residents and a third panel set
  residents per member against density; residents per member against
  residents says what the first did, and density's one point, that only
  Alexandria is denser, is a sentence in the prose (Sally, 9 October 2026).
  The panels are stacked, each at full width (Sally, 4 October 2026: side by
  side, at half width, they made no sense and could not carry their names),
  and each takes its own y range, (b) running to 70,000 so its top dots
  clear the title. Both residents axes start at zero and break, and both
  breaks are drawn the same: one gap width, `style.BREAK_GAP`, and the same
  cut mark on each side. Panel (a) breaks where Fairfax, at 1.15 million,
  stands alone (`style.BROKEN`, the near side wide); panel (b) breaks
  between zero and its set's floor (`style.BROKEN_FLOOR`, the near side
  only wide enough to show the 0), so the empty run up to 150,000 is cut
  rather than drawn, and its far side starts at 140,000 so the first dot
  clears the cut. The axis label is centred under both sides of a break.
  The two sides are placed with `add_axes()` and not a nested gridspec:
  constrained layout does not hold an explicit `wspace` on a nested
  gridspec, and it once drew the two panels' gaps at different widths.
  Residents and residents per member are in thousands, so the tick labels
  stay short. Dots are one size: area was tried for population and for
  density, and in both a reader could not read the third measure off it.
  Residents per member rather than members per resident, to match
  residents_per_seat. Panel (a) names as many Virginia places as fit, the
  places a reader of the report knows; panel (b) names only Arlington,
  since what it adds is where Arlington stands among places its size, not
  which peer is which (Sally, 9 October 2026). A name sits to the right of
  its dot where nothing stops it, and (a)'s near side runs to 640,000 so
  that Virginia Beach's can; a dot too crowded to name beside it takes a
  short leader (Alexandria and Norfolk in (a), Arlington in (b), whose dot
  touches Lafayette's, so its name sits above and to the left). The figure
  sits in Part A's Board Seats, at the end of the history it lands: where
  nearly a century of five seats leaves Arlington beside places like it
  (Sally, 9 October 2026). Part C's Board Seats points back to it.
- **elections_by_source.** The election-return counterpart of
  `members_by_source`: one row per publisher over the years it supplies the
  presidential vote, the Board's vote or both, read off the source columns of
  `elections_results`, `elections_turnout` and `elections_margins`
  (`style.ELECTION_RETURNS`). The three kinds are ordered by how much of the
  vote a source carries, so they take the sequential ramp, lightest first:
  Board, President, both (Sally, 7 October 2026). A publisher whose years leave
  no gap over eight years draws as one solid bar; the rest are ticks, since a
  bar would assert coverage nothing records. Every newspaper, the Gazette
  included, is one press row, last. Row labels are the publisher's plain name,
  chosen by Sally.
- **members_by_source.** A stacked timeline, one bar per document naming the
  Board, sorted by the year each bar starts rather than typed in by hand, so
  the row order is read off the same computation as the bars - the
  Alexandria Gazette row sorts in by its own earliest tick, not pinned to the
  bottom (Sally, 6 October 2026). Every row label is an author-date
  citation, the way a reader skimming the paper would expect to see a source
  named - a person's surname or an institution's short name, parenthesised
  year - rather than the project's own shorthand for a document: Arlington
  Historical Society (1967), O'Leary (2010), Novack (1994), Arlington County
  Board (2026), Arlington County Elections (2021), Virginia Department of
  Elections. An institution's name is shortened to what names it without its
  full legal title - Arlington County Elections, not Arlington County Office
  of Voter Registration and Elections - and a source with no date of its own,
  read off a page revised as the Board changes, carries no year rather than
  the year it happened to be accessed (Sally, 6 October 2026; two earlier
  versions tried the project's own handles for these documents - "County
  roll", "O'Leary's history" - which read as internal shorthand rather than
  something a first-time reader could place).
  A bar's span is read off `data/clean/members.csv`'s source column - the
  first and last start year of a term that cites the document anywhere, not
  only where it is the primary citation - so two bars over the same years is
  the figure's own evidence that two documents confirm each other, and the
  figure stays true as sources are added. The Alexandria Gazette is too few,
  too scattered items to read as a span, and draws as a row of narrow bars
  instead, one per citekey, at the year its own date carries
  (`charts.hspans()`, `style.SPAN_TICK` wide); two items the same year sit
  side by side rather than one over the other. A first version drew these as
  dots, which read as a different kind of mark from the bars above them
  rather than the same row continued (Sally, 6 October 2026).

  A document either records who held the seat or who won it, and that is
  the one substantive distinction among the sources themselves, so it
  stays in the near-neutral family rather than taking a category's hue
  (`style.SOURCE_KIND`): the lighter sand fill for members elected, the
  taupe stroke colour for members served, lighter first in the legend
  (Sally, 6 October 2026). The Gazette row is the case the distinction is
  for: an appointment, a qualification or a press mention of a sitting
  member is service, a candidate list or an election return is a contest,
  read off each citekey's own entry in `paper/bib/sources.bib` rather than
  guessed from its name (`members_by_source.GAZETTE_KIND`), so two ticks the
  same year can be two different colours - 1919 carries both, the Gazette's
  report of who assumed office that January beside its return of who had
  just won. A legend names the two kinds; the row labels still name the
  documents and the caption carries the citations.

## Output

Both backends stamp the time of the run into the file, so the stamp is
suppressed: otherwise an unchanged figure is a changed file, and `figures/`
is committed precisely so a change shows up as a reviewable diff.
