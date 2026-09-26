# Residents

Who lived in Arlington at each census, by what race and at what age: what each number in
`data/clean/residents.csv` is, what backs it, what is assumed where nothing
does, and why. Present tense; how a decision was reached is in the git
history. The placeholders in the `source` columns are explained in
`code/citekeys.py`, and what is still open is in `docs/questions.csv`.


`residents_per_seat` divides by the seats that exist, not the seats filled, and
says so in its label, "residents per seat". A vacant seat therefore adds no
spike: the figure shows the size of the Board, not who sat.

## What rests on an assumption

- Retrocession is dated 1846 or 1847 depending on the source; the report has
  to pick one (`retrocession-date`).
- The 1970–80 population decline is unexplained. It is most likely the
  national fall in average household size, which cost inner-ring suburbs
  population while their housing stock grew, but that is untested here
  (`population-decline-1970-80`).
- The age bands start at 1980, because nothing earlier is held in a
  machine-readable form (`adults-before-1980`).

Each is a row in `docs/questions.csv`, with an owner and what would settle it.

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

| District | 1890 | 1880 |
|---|---|---|
| Arlington | 2,013 | 1,754 |
| Jefferson | 1,303 | 1,319 |
| Washington | 942 | 814 |
| **County outside the city** | **4,258** | **3,887** |

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

**1870–1890.** County minus city, from the volumes. The 1870 white figure is
1,175 (Jefferson district's 383, not 283), the 1890 total 4,258 (above), and
the 1890 white figure 2,135 (foreign white female 305, not 365: a `0` reading
as a `6` on a low-quality scan, settled because only 305 makes white plus
colored tie to the county's 18,597). Each race split must account for its own
total to within five people or the build stops. These three cells differ from
the figures Alex Keena compiled before the volumes were read, and he confirmed
all three on 24 September 2026; 1880 agrees in every value.

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
an assumption.

**The Hispanic series begins in 1980**, the first census to ask the question
of everyone (decided by Sally, 24 September 2026). Before 1970 the question
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

## Age, 1980 onward

`residents.csv` carries the county in seven age bands from 1980: `ageunder18`,
`age18to24`, `age25to34`, `age35to44`, `age45to54`, `age55to64` and
`age65plus`. They sum to `total` at every census, and `residents_by_age`
draws them as shares of it. There is no `adults` column: the adult
population is the six bands above `ageunder18`, summed where something needs
it.

**The cuts are the ones every census from 1980 shares.** 1980's Summary Tape
File prints 35 to 44, 45 to 54, 65 to 74 and 75 to 84 as single groups, so
no cut at 40, 50, 70 or 80 exists to take without splitting a published
group, which would mean inventing a number. Every cut the bands do use — 18,
25, 35, 45, 55, 65 — is a boundary printed in all five censuses, so no year
is interpolated and the bands are the same object in 1980 as in 2020.

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

**Three guards, because a mis-mapped band would be silent.** The bands must
name every age group the source table has, exactly once — a group left out
of all seven would simply never be counted, and the county total would still
tie. The bands must then sum to the same county total the `total` column
carries. And `turnout.csv`, which counts adults from a different table
altogether (race by 18 and over), must agree exactly with the six adult
bands summed; it does, at all five censuses. `code/tests.py` reintroduces
each mistake and asserts the build refuses.

**Children are counted.** They cannot vote, and the report's other age
figure is about people who can serve, but a seventh of Arlington is under 18
and the section is about the county rather than the electorate.
`docs/figures.md` carries that reasoning and the rest of the figure's form.

The series starts at 1980 because the Bureau's machine-readable county
tables do. Earlier censuses printed county age tables in the bound volumes,
and carrying the series back would mean keying them in by hand
(`adults-before-1980`, which the turnout figure shares).

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
