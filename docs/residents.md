# Residents

This write-up covers who lived in Arlington at each census, by what race and at
what age: what each number in `data/clean/residents.csv` is, what backs it, and
what is assumed where nothing does. How a decision was reached is in the git
history rather than here. `code/citekeys.py` explains the placeholders in the
`source` columns, and `docs/questions.csv` holds what is still open.


`residents_per_seat` divides by the seats that exist, not the seats filled, and
says so in its label, "residents per seat". A vacant seat therefore adds no
spike: the figure shows the size of the Board, not who sat.

Nothing here rests on an assumption. Every number is a figure the Census
Bureau published or a subtraction between two of them, or, for Arlington
district's 1900 race split and every district's 1890 split, a gap that stays
blank rather than resting on one ("Race by district, counted from the
schedules", below). Where a source merges two categories, the figures carry
the merge rather than splitting it on an assumption; the 1940 and 1980 cases
are below.

---

## What "Arlington County" means here

**Arlington County is the territory the Board governed at each point in
time**, not a fixed plot of land held constant backwards. The report assesses
the Board's performance, and the Board governed whoever lived inside its
boundaries in a given year; when territory moved to another jurisdiction the
Board governed fewer people, and the series should show that. Residents per
seat therefore measures the right thing, and the boundary changes below are
context for reading the figures rather than corrections to make.

That territory is the present-day county: the Arlington, Jefferson and
Washington magisterial districts. **It excludes the City of Alexandria in
every year**, because the Board never governed the city. The name, boundaries
and census treatment all changed across the period:

| Period | Name | What the published county figure contains |
|---|---|---|
| to 1846 | Alexandria County, D.C. | part of the District of Columbia |
| 1847–1919 | Alexandria County, Virginia | the three districts **and** Alexandria city |
| 1920– | Arlington County, Virginia | the three districts only |

Retrocession has several dates, and the prose names the event each time rather
than picking a year (Sally). Virginia accepted the county in
advance by an act of 3 February 1846. Congress passed the act to retrocede it on
9 July 1846, effective "with the assent of the people of the county and town of
Alexandria", and the residents voted for it that September
(`usstat1846retrocession`, 9 Stat. 35, which recites the Virginia act). Virginia
extended her laws over the county by an act of 13 March 1847, and the transfer
took effect then. So "retroceded in 1846" names Congress and the residents'
choice, and "part of Virginia from 1847" names the transfer.

The acceptance act is `vaacts1846acceptance`, ch. 64 of the 1845-46 session,
passed 3 February 1846. The extending act is `vaacts1847`, ch. 53 of the
1846-47 session, passed 13 March 1847, effective 20 March 1847.

Two dates do the work. **In 1900** Alexandria city became independent of the
county for census purposes, so from that census onward the published county
figure already excludes it. **In 1920** the county was renamed; the territory
did not move. So 1870, 1880 and 1890 need a county-only figure derived, by
subtracting the city or summing the three districts, and 1900 onward can be
used directly. (*Population of States and Counties of the United States:
1790-1990*, Virginia notes, printed p.185.)

The census county series measures the jurisdiction as constituted at each
census, not a constant area: the document normalises *states* to present-day
boundaries and says so, and states that county figures "refer to the inclusion
and boundaries of the county in decennial census publications". Arlington's
own row shows it, 18,597 in 1890 and 6,430 in 1900. The document's separate
table, *Population of Counties Including Associated Independent Cities*, is
the nearest thing to a fixed-land series and is not what this project uses.

**Boundary changes after 1900**, for reading the early twentieth century:

| Change | What left Arlington |
|---|---|
| 1915 | 866 acres annexed by Alexandria, effective 1 April 1915: Rosemont, Shuter's Hill, Carlyle, Eisenhower East, the former West End |
| 1930 | A further annexation bounded by Duke Street, Quaker Lane and Four Mile Run, including the Town of Potomac, incorporated in its own right in 1908 |

The first falls between the 1910 and 1920 censuses and the second around the
1930 census, so part of the movement in those decades is territory changing
hands. Sources are under Works cited.

### The three districts, and what sits inside them

The districts are keyed in for every census 1870 through 1930, and
`data/clean/residents_by_district.csv` holds them, one row per census per
district, each as that census drew it. They are the level-1 lines of each
census's table of the county's minor civil divisions, less Alexandria city,
and each census's three sum to the county total in `residents.csv`, or the
build stops. The series crosses two boundary changes, both printed as
footnotes to the tables that follow them: part of Jefferson district is
annexed to Alexandria city in 1915, between the 1910 and 1920 censuses, and
part of Arlington and part of Jefferson, including Potomac town, in 1930.
Each table's earlier-census columns reprint the earlier counts unchanged
rather than restating them to the new lines, so no district is on constant
land across the series. Race below the county is
published for 1870 alone: Jefferson 383 white to 873 colored, Arlington 517 to
857, Washington 275 to 280. Every later volume gives the districts by total
only, so a later date has to be counted from the schedules rather than read
off a page. 1920 is, below.

| District | 1890 | 1880 |
|---|---|---|
| Arlington | 2,013 | 1,754 |
| Jefferson | 1,303 | 1,319 |
| Washington | 942 | 814 |
| **County outside the city** | **4,258** | **3,887** |

### Where the lines ran

`noetzel1907`, a 1907 county map published under the authority of the
Alexandria County Board of Supervisors, rules a dash-dot line between each
pair of districts, distinct from the roads, railroads and streams it also
draws: Washington from Arlington near Hall's Hill and the Glebe Estate, and
Arlington from Jefferson at Four Mile Run near Nauck. It is the only source
found that draws the lines rather than only lettering each district's name
across its own interior, which is what the two other period maps checked,
Hopkins 1879 and Howell and Taylor 1900, do instead; `docs/questions.csv`
held the search before this map was found.
`data/transcribed/by_claude/district_lines.csv` keys the two lines off that
map against the modern street network, extended past the county's edge at
both ends so `code/clean/residents_by_district_boundaries.py` can split the
modern county outline (`data/raw/arlington_county/county_outline.geojson`)
on them cleanly; using the modern outline rather than 1907's removes the
1915 and 1930 annexations without a separate geometry for either. The
figure is `residents_by_district_map`, a stylized rendering in
`style.DISTRICTS`' colors, not a reproduction of the 1907 map. The two
lines are read off the printed map, not surveyed to it: positions are good
to within roughly a few hundred meters at this county's scale, which is
what a figure beside `residents_by_district_race` needs and no more. Still
open: whether the 1907 lines agree, point for point, with the NARA 1910 and
1920 enumeration-district descriptions of each district's interior.

### Race by district, counted from the schedules

Race below the county is printed in one volume only, 1870's. For 1880, 1900,
1910 and 1920 it is counted person by person out of the full-count schedules
instead, and `residents_by_district.csv` carries all five censuses. The figure
is `residents_by_district_race`. Two cells are empty, each for a reason below:
every district in 1890, whose schedules burned, and Arlington in 1900, which
the database is short of by one resident in six.

The Black share of each district, and of the county from `residents.csv`.
`test_the_district_share_table_in_the_write_up_is_current` recomputes it from
the clean tables on every build, so it cannot drift from them:

| District | 1870 | 1880 | 1890 | 1900 | 1910 | 1920 |
|---|---|---|---|---|---|---|
| Arlington | 62% | 56% | — | — | 21% | 12% |
| Jefferson | **70%** | **65%** | — | **56%** | 39% | 27% |
| Washington | 50% | 42% | — | 33% | 22% | 14% |
| The county | 63% | 56% | 50% | 38% | 26% | 16% |

Jefferson is the concentration the district argument rests on, and it holds:
the district with the largest Black share in 1870 is still the only
majority-Black district thirty years later, and still the largest share fifty
years later. Washington fell below half in the 1870s and Arlington in the
1880s or 1890s, but Jefferson was still a majority Black in 1900. **The decade in which Black residents
became a minority of every magisterial district is therefore the 1900s**, and
that does not depend on either empty cell.

**The extracts.** `code/fetch/ipums.py` asks IPUMS USA for the 100 per cent
database of a census, case-selected to Virginia and to the ICPSR county code
0130, which is Arlington under the name it held at the time. Each extract,
and the codebook the API delivers with it, is committed under
`data/raw/ipums/`; the query that produced it is the script, since a
microdata extract is not a published table and cannot be its own citation.
The data are `ipumsfullcount`, and IPUMS's terms of use require that
`ipumsusa` be cited beside it.

**The mapping, and what places each census.** IPUMS gives no variable naming
the magisterial district: `MCDSTR`, which would name it in words, is
published for no full-count sample, so the geography in an extract is the
enumeration district. What ties those to districts differs by census, and
`ED_READ_BY_HAND` in `code/clean/residents_by_district.py` holds every
reading that a description does not make for us.

- **1910 and 1920** have descriptions that name a magisterial district
  outright (`nara1910eds`, `nara1920eds`, NARA T1224), for all but one
  district each. The exception both share is the Fort Myer Military
  Reservation, whose description names none. It is Arlington's: both
  Arlington descriptions in both censuses define themselves as that district
  *excluding* the reservation, so it is the piece they were drawn around.
  The numbering is each census's own — Fort Myer is district 10 in 1910 and
  11 in 1920.
- **1880** has descriptions with no text at all, and does not need them. In
  1880 the census county still contained Alexandria city, which became
  independent of it for census purposes only in 1900, and the extract's eight
  enumeration districts separate cleanly: three of them hold 1,754, 1,320 and
  814 people against the 1,754, 1,319 and 814 the volume prints for Arlington,
  Jefferson and Washington, and the other five hold the city's four wards,
  two of them split in half. One district per district, no partitioning to do.
  The Black counts tie as well: 988, 861 and 343 make 2,192 against the 2,194
  the volume gives the county outside the city. The city's five are dropped;
  the Board never governed it.
- **1900** has descriptions, but IPUMS numbers the districts differently from
  them — the descriptions run 1, 2, 3 and 99 where the extract holds 1, 2, 3,
  15 and 16 — so none of them can be joined by number and all five are read
  by hand. Districts 2 and 3 hold 1,913 and 1,317 people, the published
  Jefferson and Washington totals to the person. 15 and 16 are Fort Myer,
  which the descriptions put at 99: 67 of their 211 people are men of
  nineteen to forty in group quarters.

**Arlington district has no 1900 cell, and none is coming.** The 1900
database holds 5,931 of the county's 6,430 people, and the whole shortfall of
499 is in Arlington district, which it gives as 2,701 against a published
3,200 — one resident in six missing, with nothing to say what race they were.
Jefferson and Washington tie exactly, so they are written and Arlington is not
(`INCOMPLETE`), and the figure's Arlington line and its county line both break
at 1900. The county line is the three districts added together, so two
districts are not a county.

Two routes were checked before settling for that. IPUMS's Full Count Data is
still at version 4.0, the version already in hand — its own revision history
lists no later release of the 1900 database (checked 2026-09-28). And
FamilySearch's own index of Enumeration District 1 (`familysearch1900ed1arlington`)
— a second transcription of the same schedules, keyed by a different
organization from a different scan of the microfilm — was read in full,
image by image: it totals 2,535 people, 1,553 white and 936 Black, with 46
too faint for its indexers to read. Add Fort Myer's 211 and Arlington district
comes to 2,746 people on either digitization, 454 short of the volume. The
same shortfall, on two independent readings of the schedules, means the
missing people are not sitting on a page nobody has read yet — they are not
on any surviving copy of the schedule. No reading recovers a race split for
Arlington in 1900, so the cell stays blank.

**1890 is empty and will stay empty.** The manuscript schedules burned, so
there is no full count to extract and no prospect of one. The county's own
1890 race figure, 49.9 per cent, comes from the published volume as every
county figure does.

**What the mapping is checked against.** Each district's head count in the
extract is compared with the total the volume prints for it, and how close
they must be is a property of each census's database rather than one
allowance: 1880, 1900 and 1920 tie to within a handful of people, and 1910's
database is up to seventy-five short of a district (`TOO_FAR`). A tolerance is
only worth having if it is still tight enough to catch what it exists for, so
the build also tries moving each enumeration district into each other
magisterial district in turn and refuses if any of those would pass the check
too: if the published totals do not identify the mapping, the check is
decorative and the build should stop rather than write a number on it. That
check is what caught a first attempt at 1900, where a tolerance of ten per
cent was wide enough to let Fort Myer's 67 people sit in Jefferson unnoticed.
`code/tests.py` reads 1920's ED 12 into Jefferson and asserts the build
refuses, and widens every tolerance until a move would pass and asserts the
same.

**The counts do not match the volumes exactly.** These are two counts of the
same population — Ancestry's transcription of the manuscript schedules,
re-coded by IPUMS, against the Bureau's own tabulation. The 1920 extract holds
16,043 people where the volume prints 16,040, and 2,559 Black residents where
the county series prints 2,507, two per cent apart; 1910's is 154 short of
10,231. Each share divides by the people its own count records in that place,
not by the volume's total, so each is internally one count; at the county in
1920 that puts the Black share 0.4 points above the published one, and
`residents_by_race`, which reads the published series, is the figure to take
the county's own number from.

**The 1915 annexation sits inside this.** The southern Jefferson district
enumeration district is the part of the county that 1915 took a bite out of;
the 1920 volume's own footnote records the annexation. So Jefferson's fall
in Black share between 1910 and 1920 is partly people leaving the
district for Alexandria city and partly the district's white population
growing. Nothing in `data/` separates the two.

**Freedman village is not a fourth district.** It was a settlement of formerly
enslaved people on the confiscated Lee estate, inside Arlington district. The
1890 census lists it as an indented sub-line, "Arlington district, *including*
Freedman village", the same way it lists Alexandria city's wards beneath the
city total, so its 338 residents are already within Arlington district's
2,013. Counting it as a fourth district adds those people twice and gives
4,596. The three districts alone give 4,258, which is also county 18,597 minus
city 14,339. Each transcribed table carries the printed indentation as a
`level` column and the build sums level 1 only, so the double count cannot be
written; `code/tests.py` reintroduces it and asserts the build refuses.

Three checks for any new early figure: county-outside-city equals the sum of
the three districts; city plus the three districts equals the published
county total; and every line being added is a place rather than a detail of
the line above it. The third is the one that fails.

The settlement matters beyond the arithmetic. The federal government created
it and began removing its residents in 1888, so the 1870 baseline of the race
series is a Reconstruction moment rather than a stable starting point. See
*What the Black share shows* below.

### Men of voting age, by district

`data/clean/residents_by_district_adults.csv` counts the men aged 21 and over
in each district at 1880, 1900, 1910 and 1920, by race, and the county where
all three districts are counted. It is the denominator of
`elections_turnout_by_district`. The build carries sex beside race and age
(`data/built/ipums.csv`); that the age is 21 and the unit a man is decided in
`code/clean/residents_by_district_adults.py`. Each census's enumeration
districts are placed in a magisterial district by `residents_by_district.placed()`
and `ED_READ_BY_HAND`, the same reading as the race table, and the step
refuses if a district's head count is not the one `residents_by_district.csv`
holds.

| District | 1880 | 1900 | 1910 | 1920 |
|---|---|---|---|---|
| Arlington | 452 | 746 | 2,227 | 2,906 |
| Jefferson | 322 | 545 | 769 | 1,107 |
| Washington | 199 | 364 | 439 | 1,084 |

The table also counts the women 21 and over (`women_white`, `women_black`,
`women_other`, `women_all`) and the two together (`adults_all`), by the same
placement. Women could not vote in Virginia before 1920, so the figure that
reads them, `elections_turnout_before_1932_adults`, takes men for the
denominator through 1916 and everyone 21 and over from 1920. 1930 is one county
row from the census volume's printed counts of males and females 21 and over,
with no race and no district.

**Arlington's 1900 count is a floor.** The database holds 2,701 of the 3,200
people the volume prints for the district, so the 746 men are fewer than the
district's. The row is written, since a turnout rate needs a denominator and
the alternative is no 1893 to 1905 line for the district; the county is not
written for 1900, because two districts and a short third are not a county.
A rate that divides by this count is an upper bound.

**A census is a denominator for the years nearest it.** Washington's 439
adult men in 1910 and 1,084 in 1920 are the district doubling, so a vote
divided by the nearer census reads high in 1915, which is five years from
each and is divided by 1910's. Nothing in `data/` interpolates the men.

---

## Population and race, year by year

Every total from 1870 to 2020 is taken from a published Census Bureau document
in `data/raw/us_census_bureau/`, and so is every race figure. 1870–1890 are
derived from the volumes as county minus city; 1900–1970 come from
POP-TWPS0076 Table 47, which prints Arlington by race at every census from
1900; 1980–2020 come from the crossed census tables.

| Year | Total | Total from | Race from |
|---|---|---|---|
| 1870 | 3,185 | `walker1872` | `walker1872` |
| 1880 | 3,887 | `census1880` | `census1880` |
| 1890 | 4,258 | `census1890` | `census1890` |
| 1900 | 6,430 | `forstall1996` | `censusbureau1990twps76` |
| 1910 | 10,231 | `forstall1996` | `censusbureau1990twps76` |
| 1920 | 16,040 | `forstall1996` | `censusbureau1990twps76` |
| 1930 | 26,615 | `forstall1996` | `censusbureau1990twps76` |
| 1940 | 57,040 | `forstall1996` | `censusbureau1990twps76` |
| 1950 | 135,449 | `forstall1996` | `censusbureau1990twps76` |
| 1960 | 163,401 | `forstall1996` | `censusbureau1990twps76` |
| 1970 | 174,284 | `forstall1996` | `censusbureau1990twps76` |
| 1980 | 152,599 | `forstall1996` | `census1980stf1a` |
| 1990 | 170,936 | `forstall1996` | `census1990stf1a` |
| 2000 | 189,453 | `censusapi` | `censusapi` |
| 2010 | 207,627 | `censusapi` | `censusapi` |
| 2020 | 238,643 | `censusapi` | `censusapi` |

`walker1872`, `census1880` and `census1890` are the printed volumes;
`forstall1996` is *Population of States and Counties of the United States:
1790-1990*; `censusapi` the Bureau's data files, fetched whole (every Virginia
county, every variable of the table) so Arlington is a row in a published
table rather than an extract.

### What drew the 1930–1950 growth

Bestebreurtje (`bestebreurtje2017`, p. 239) says a large influx of federal
employees and their families came with the New Deal's expanded government, and
(p. 240) that federal expansion continued into the 1940s with the
militarization of the United States before and during the Second World War.
Her figures for the county's permanent population are 57,000 in 1941, 120,000
in 1945 and 135,000 by 1950 (p. 240, citing Rose), and she calls Arlington the
fastest-growing county in the country from 1930 to 1950 (p. 248).

The same chapter says the 1930s-40s houses went up on land Arlington's
comprehensive Zoning Ordinance of 1930 had already classed almost
entirely residential (pp. 249-250), and that the suburbs first developed along
rail lines but were advertised by road access from the early 1920s and by the
1930s were dominated by the personal car (p. 250). The dissertation ties the streetcar
suburbs to the growth before 1930 (Chapter Two, pp. 42-43) and gives no
streetcar cause for 1930-1950.

The Black share's fall from 49.9 per cent in 1890 to 4.8 per cent in 1950
rests on two statements. Bestebreurtje says the fall in the Black share did
not represent an exodus of African Americans but a consistent Black population
where new white residents were entering in droves with suburban land booms
and federal employment (p. 233), and that the vast majority of the new
arrivals and federal positions of the 1930s-40s went to white workers (p. 240).
She puts the White-to-Black ratio in the surrounding suburbs at 12 to 1 in
1950 (pp. 242-243). She gives no cause of the White in-migration beyond
federal employment and suburban building.

**1870–1890.** County minus city, from the volumes. The 1870 white figure is
1,175 (Jefferson district's 383, not 283), the 1890 total 4,258 (above), and
the 1890 white figure 2,135 (foreign white female 305, not 365: a `0` reading
as a `6` on a low-quality scan, settled because only 305 makes white plus
colored tie to the county's 18,597). Each race split must account for its own
total to within five people or the build stops. These three cells differ from
the figures Alex Keena compiled before the volumes were read, and he confirms
all three; 1880 agrees in every value.

**1900–1970.** POP-TWPS0076 Table 47, transcribed from the rendered page.
White, Black and Asian/Pacific Islander are taken as printed; American Indian
and other race are not columns, and reach the figures as the remainder, the
same way the fifth group does from 1980. Every year ties to its printed total
exactly. Two years do not give everything. *1940* prints American Indian and
Asian/Pacific Islander as a single merged cell of 10 people, so `aapi` is left
empty that year and the ten reach the remainder. *Hispanic origin* is not
available at full count for any year here; 1970 has it only as a sample
estimate, 6,315 on the 15 percent sample against 4,890 on the 5 percent, which
is a different kind of number from the full counts beside it. The
transcription carries the sample rows and the build does not read them.

The Bureau publishes this paper as one PDF per state with no front matter, so
the copy held names neither the paper nor its date — only its own table. The
Bureau's page for the working paper does: *Historical Census Statistics on
Population Totals by Race, 1790 to 1990, and by Hispanic Origin, 1970 to 1990,
for Large Cities and Other Urban Places in the United States*, by Campbell
Gibson and Kay Jung, February 2005, working paper POP-WP076, served under the
path `pop-twps0076`. The bibliography entry is built from that page and says
so; what the held PDF itself carries is its `annotation`.

**1980–2020.** Race and Hispanic origin are two census questions, so a
Hispanic resident appears in both a race count and the Hispanic count, and
the four published race columns never summed to the county. The Bureau also
publishes the two answers crossed, and those categories partition the county
exactly:

    Hispanic or Latino of any race, and among those who are not Hispanic:
    White, Black, Asian and Pacific Islander, Other or Multiracial

The build refuses to write a year in which the five do not sum to the county
total. 1980 and 1990 come from the archived Summary Tape Files (fixed-width
ASCII at www2.census.gov, cut to Virginia's county rows for size); 2000–2020
from the API. 1980's "Spanish origin" is the same question. In 1980 the file
does not split American Indian from Asian among persons of Spanish origin, so
the two are subtracted together and carried in `nh_aapi` rather than split on
an assumption. The 1980 `aapi` band therefore holds the county's 384
American Indian, Eskimo and Aleut residents of all origins beside its 6,792
Asian and Pacific Islanders, where 1990 and later put them in the residual;
the point is about five per cent high on that band, once. It stays as the
source prints it and the caption says so, rather than being corrected from
a second table that is not crossed with Spanish origin (Sally): the figure
keeps fidelity to the table it reads and states the
grouping, instead of a quiet adjustment that mixes two tables.

**The Hispanic series begins in 1980**, the first census to ask the question
of everyone (decided by Sally). Before 1970 the question
did not exist and `white` means white; Hispanic residents were counted as
white, so the step at 1980 is partly the question appearing rather than people
arriving. At under one per cent of the county in 1970, barely.

| Years | Categories the census reports |
|---|---|
| 1870–1940 | White, Black |
| 1950–1960 | White, Black, AAPI |
| 1970 | White, Black, AAPI; Hispanic on a sample only |
| 1980–2020 | White, Black, AAPI, Hispanic or Latino, crossed |

**A blank is not a zero.** `hisp` is empty before 1980 and `aapi` before 1950
because the census did not tabulate them. A stacked figure cannot draw the
difference between a band of height zero and a band that has not started, so
`residents_by_race` fills blanks with zero on its shares panel and the caption
says so; its counts panel draws lines, which simply begin. Each group was tiny
the first year it was counted (Asian and Pacific Islander 57 residents in 1950,
0.04 per cent of the county) and the real growth comes well after the
question appears.

**The residual band** is what the four written columns leave of the total.
Nothing in it is unreported: before 1980 it is people in race categories the
source did not break out, 0 to 202 people, never above 0.12 per cent of the
county; from 1980 it is American Indian and Alaska Native, some other race,
and two or more races, all counted, and in 2020 two or more races is 12,196 of
its 13,945. It is drawn inside the stack below White, because it is another
kind of not-White and stacking it on top would split that population in two.

### The 1970s population fall

Arlington's population fell from 174,284 in 1970 to 152,599 in 1980, a drop of
21,685. Over the same decade the county's housing stock grew:
the 1970 Census of Housing counted 71,241 housing units in Arlington
(`census1970housing`, Table 1, p. 48-7), and the 1980 Census of Housing counted
75,182 (`census1980housing`, Table 46, p. 48-200), a gain of 3,941 units. Units rose while population fell, so the decade's loss is people
per household falling faster than the county could add units to hold them,
not a shrinking housing stock — the pattern of the era's inner-ring suburbs
generally, not something particular to Arlington.

The story behind the arithmetic is the baby boom growing up. Nationally the
average household fell from 3.14 people in 1970 to 2.76 in 1980, and almost
all of the fall is children: members under 18 per household went from 1.09
to 0.79 while adults per household barely moved (`censushh6`). The children
born to the young families who filled Arlington in the 1940s and 50s turned
18 across the 1970s and left, to careers and households of their own, and
fewer were born behind them. A built-out inner suburb of small units feels
that hardest. Arlington's own age bands show it: residents under 18 fell from
41,564 in 1970 to 24,969 in 1980, while
those 18 and over fell only from 132,720 to 127,630.

### What the White count does at 1980

The White count falls from 161,329 in 1970 to 120,250 in 1980, a drop of
41,079 in a county that lost 21,685 people over the same decade. The fall in
the one category is nearly twice the fall in the whole, so most of it is not
people leaving.

The difference is exact: every other category grew by 19,394, and 41,079 is
21,685 plus 19,394. Part of that growth is the question changing. The 1980
census asked Hispanic origin of everyone and crossed it with race, so `white`
stops meaning white and starts meaning not-Hispanic white, and the 8,863
Hispanic residents counted that year sat inside the 1970 White count or
arrived during the decade. That is an upper bound on the recategorisation,
and it is 21.6 per cent of the fall. The rest is the Black count rising from
10,076 to 13,852, the AAPI count from 1,387 to 6,792, and the residual band
from 1,492 to 2,842.

So recategorisation accounts for at most a fifth of what the White series
does at 1980. The larger part is the county losing people, which *The 1970s
population fall* above accounts for, and the remainder is the other
categories growing.

### What the Black share shows

Panel (b) of `residents_by_race` shows the Black share of Arlington falling
from 63 per cent in 1870 to 8.5 per cent in 2020. Panel (a) is why the levels
are drawn beside it: Black residents went from 2,010 to 20,330, a tenfold
increase, while the county went from 3,185 to 238,643, seventy-five-fold. No
census records a substantial fall; the only decreases are 2,645 to 2,507
across the 1910s and a flat stretch from 1990 to 2010. The share falls because
everything else grew faster. Two things go with that. County totals cannot
rule out displacement, because they aggregate over exactly the geography where
it happens; Arlington's Black population was concentrated in a few
neighbourhoods, and nothing in `data/` speaks to them (Bestebreurtje, under
Works cited, is where to look). And the 1870 baseline reflects Freedman
village, a settlement the federal government created and then dismantled.
How much of this the prose says is an open question.


---

## Age, 1910 onward

`residents.csv` carries the county in seven age bands from 1910: `ageunder18`,
`age18to24`, `age25to34`, `age35to44`, `age45to54`, `age55to64` and
`age65plus`. With `ageunknown` they sum to `total` at every census from 1930, and
`residents_by_age` draws them as shares of it. `ageunknown` is the 14 people
whose age the 1930 census did not record; from 1940 the Bureau's tables print
no such line, and the column is 0. There is no `adults` column: the adult
population is the six bands above `ageunder18`, summed where something needs
it.

**1910 and 1920 are counted from the schedules**, in the county less Alexandria
city, from the full-count extracts' single years of age
(`code/clean/residents.py`, `schedule_ages`), placed by the same enumeration
district mapping the district figures use. The schedules and the volume are
two counts of the same population, so the bands sum to the people the
schedules hold, not to `total`: 154 short in 1910 and three over in 1920, and
the build refuses a gap wider than `AGE_TOO_FAR`. The figure divides each
census by the people its own count holds. No other census before 1930 has an
age distribution to take. 1890 and 1900 print county ages only as school
(5 to 17 or 20), militia (males 18 to 44) and voting (males 21 and over)
ages, which no band here is built from without interpolating; 1890's
schedules burned and 1900's database lacks 499 people, all in Arlington
district, whose ages nothing recovers. 1870 and 1880 could be counted from
the schedules, but nothing reads them.

**The cuts are the ones every census from 1930 shares.** 1930 prints 35 to
44, 45 to 54, 55 to 64 and 65 to 74 as single groups, and 1980 does the same
for 35 to 44, 45 to 54, 65 to 74 and 75 to 84, so no cut at 40, 50, 70 or 80
exists to take without splitting a published group, which would mean
inventing a number. Every cut the bands do use — 18, 25, 35, 45, 55, 65 — is
a boundary printed for all ten censuses, so no year is interpolated and the
bands are the same object in 1930 as in 2020.

**`adult_median_age` is the one interpolated column.** `members_age` sets it
against the Board's own ages, and a band count alone has no single age to
plot, so `code/clean/residents.py` finds the band holding the midpoint of the
six adult bands and assumes residents are spread evenly within it: the
median falls where that fraction of the band's width sits above its lower
cut. `age65plus` has no printed upper edge; it is treated as 65 to 85, the
same open-top convention `members_age.py` draws its own band to. A reader
comparing this line to `residents_by_age`, which plots the printed bands
directly with no assumption at all, should read the two differently: one is
the county's own data, the other this project's reading of it.

**1930 to 1970 are keyed in from the census volumes**, one file per printed
table under `data/transcribed/by_claude/us_census_bureau/`, every line of
Arlington's block as printed. Each was read off the rendered page and ties
out: every run of lines the table prints in full sums to the county total it
is printed against, and that total is the one the `total` column already
holds.

| Year | Age from | Tables |
|---|---|---|
| 1930 | `census1930v3p2` | Table 11, age, p.1150; Table 13, composition, p.1161 |
| 1940 | `census1940v2p7` | Table 22, age, p.173; Table 21, composition, p.164 |
| 1950 | `census1950va` | Table 41, age, p.46-74 |
| 1960 | `census1960va` | Table 27, age, p.48-76 |
| 1970 | `census1970va` | Table 35, age, p.48-122 |

1950 to 1970 print a line at 18 in the age table itself: single years to 20
in 1960 and 1970, and "16 and 17" and "18 and 19" beneath 15 to 19 in 1950.
1930 and 1940 do not; their age tables run in five-year groups, and 15 to 19
crosses 18. Each volume's composition table prints the population at the
ages that cut there, so no band is estimated:

- **1940.** Table 21 prints the persons 5 and 6, 7 to 13, 14 and 15, 16 and
  17, 18 to 20, and 21 to 24 years old. `ageunder18` is Table 22's under 5
  and Table 21's four groups to 17; `age18to24` is Table 21's 18 to 20 and
  21 to 24. The two tables agree: Table 21's six groups make Table 22's 5
  to 24, 16,730, and the 1950 volume's 1940 column prints 16 and 17 as 1,463,
  as Table 21 does.
- **1930.** Table 13 prints the persons 18 to 20 and the men and women 21 and
  over. Everyone of known age is under 18, 18 to 20, or 21 and over, so
  `ageunder18` is the county less the 14 of unknown age and those two
  counts, and `age18to24` is 18 to 20 and 21 and over less Table 11's groups
  from 25. Each is checked to lie between the printed groups either side of
  its cut. The two counts each have a second reading: 18 to 20 against the
  number attending school and the per cent printed beneath it, and 21 and
  over against the 1940 volume's 1930 column, which prints 16,443.

**Where each census's ages come from.** 1980 and 1990 from the archived
Summary Tape Files, which name their age groups; 2000, 2010 and 2020 from
the Bureau's sex-by-age table, which numbers them, men and women summed. The
2020 figures come from a different release than the 2020 race figures beside
them: the redistricting file gives age only as an 18-and-over total, so sex
by age is fetched from the Demographic and Housing Characteristics file.
Both are `censusapi`.

| Year | Age from | Table |
|---|---|---|
| 1980 | `census1980stf1a` | Table 10, age |
| 1990 | `census1990stf1a` | P11, age |
| 2000 | `censusapi` | SF1 P012, sex by age |
| 2010 | `censusapi` | SF1 P12, sex by age |
| 2020 | `censusapi` | DHC P12, sex by age |

**Four guards, because a misread or mis-mapped band would be silent.** A
keyed-in table whose printed runs do not sum to their totals, or a line whose
men and women do not make it, is a misreading and stops the build. The bands must
name every age group the source table has, exactly once — a group left out
of all seven would simply never be counted, and the county total would still
tie. The bands must then sum to the same county total the `total` column
carries. And `elections_turnout.csv`, which counts adults from a different table
altogether (race by 18 and over), must agree exactly with the six adult
bands summed; it does, at all five censuses from 1980, and in 1970, where
the one reads the single years and the other the five-year groups.
`code/tests.py` reintroduces each mistake and asserts the build refuses.

**Children are counted.** They cannot vote, and the report's other age
figure is about people who can serve, but a large share of Arlington is under 18
and the section is about the county rather than the electorate.
`docs/figures.md` carries that reasoning and the rest of the figure's form.

The series starts at 1930, the earliest census whose volume is keyed in.

---

## The census scans

Eleven PDFs, 537 pages, from the published 1870, 1880 and 1890 volumes:
three title-page chunks, on which the bibliography entries rest, and eight
interior chunks carrying the tables the transcriptions were read from. Seven
of the eleven have no text layer; `data/transcribed/by_ocr/` holds OCR of the
nine that were held first, on the author's Mac and not in git, since the OCR
is a finding aid and would take 1.8MB of Overleaf's text cap. The method is to search the OCR to locate a table,
then render the page and read it by eye. OCR misread digits on the first
table checked (17,546 as 17,516, 14,339 as 14,830), which is why it is never
the source of a number.

**Six of the eleven are not committed.** The 1880 and 1890 interior chunks
are 50MB the build never opens, against Overleaf's 100MB ceiling for the
whole repository. They are the Bureau's own files at stable URLs, and
`data/contents.csv` records each one's URL and checksum;
`code/fetch/census_volumes.py` fetches whichever is missing and refuses a
download whose checksum differs, so a page cited from one of them is the
page that was read. `bash run.sh` says at the end of every build if they are
absent. The three 1870 chunks are committed, and carry a URL as well. The Bureau's
current copies at 1870/population/ are chunked differently — 69 chunks there,
of 7 and 3 pages against the 36 and 46 held — but its legacy tree at
prod2/decennial/documents/ still serves the older 19-chunk run, and the three
held files match it byte for byte. `code/fetch/census_volumes.py` therefore
checks them against that path like any other chunk, and a full checkout is a
provenance audit that downloads nothing.

**The 1930 to 1970 volumes** are ten more PDFs, none committed: for each
census the Bureau's front-matter file, on which the bibliography entry rests,
and the chapter holding Arlington's age tables, 127MB between them. They are
fetched and checked the same way. None has a text layer and none is OCR'd;
each table was found by rendering the chapter's page headers and read off
the page at 200 dpi. The magisterial districts for 1900 to 1930 come from four
more volumes fetched the same way, each front-matter file with the chunk
holding the district table. `data/raw/us_census_bureau/README.md` lists all
twenty-four files fetched on demand.
