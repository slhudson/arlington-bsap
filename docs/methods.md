# Data and methods

What each number in `data/clean/` is, what backs it, what is assumed where
nothing does, and why. Written from what is now known, in the present tense.
How each decision was reached is in the git history, not here.

Every `source` cell in `data/clean/` holds a citekey from `paper/sources.bib`
or one of three placeholders: `unsourced` (a claim exists and its evidence is
not yet named), `derived` (computed from another clean table, whose rows carry
the citations) and `assumed` (no claim exists; the build supplied a value from
a standing assumption). `code/build/citekeys.py` says what each admits to, and
`bash run.sh` counts them on every build.

Questions still open are in `docs/questions.md`, each with an owner. When one
is settled its answer is written here and the question is deleted there.

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
its title is read from the table header and its number and date from the file
path. The bibliography entry says so, and the report must carry a footnote to
that effect (Q23 in `docs/questions.md`).

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

## The Board

### The roster

`data/clean/board_members.csv` holds one row per person per term: name, term
number, district, when service began and ended (to the month), how the term
began, and a source per row. 217 terms, 1870 through 2026, from three sources
in sequence: O'Leary's electoral history to 1915, Novack's roster from 1932 to
1994, and election results after that, the county's candidate history to 2021
and the state's elections database from 2022. Nothing covers 1912–1931 except
the two elections named below.

A term is the natural unit: person-years fall out of it, while a term starting
in May or ending in February cannot be recovered from a list of years. A
vacant seat is not a row, since nobody served. `term_number` counts within a
person, so someone appointed to a vacancy who then won twice has three rows
numbered 1, 2, 3; William A. Rowe has eight, including his move from Jefferson
district to Arlington at term 7.

`seated_by` says how each term began: election, special election,
appointment, or unrecorded where O'Leary writes only that someone was
replaced. Three builds select terms by it, so it is a column rather than
something read out of the note.

**When a term begins depends on the constitution in force.** Under the
magisterial system elections were held in May and the board took office then,
so those terms run May to May. The 1902 constitution moved county and district
elections to November and seated their winners on 1 January following (sec.
112, `vaconstitution1902`), so from the November 1903 election a term runs
January to January; the County Manager plan seats members on 1 January too,
so the convention is unbroken from 1904 on. The Schedule of the 1902
constitution has not been read, so whether the November 1903 winners fell
under sec. 112 or a transitional provision is unconfirmed; the build seats
them in January on the reading that the section is the operative rule and an
exception has to be shown (Sally, 24 September 2026). It moves one handover by
two months in a stretch where every member is coded a white man.

The same convention is why the Arlington Historical Society's roster dates
Newman 1987, Monroe 1999, Dorsey 2015 and Spain 2024 where this one seats them
a year later: each won the November general election of the earlier year and
took office that January. Tejada is the control. He won a special election in
March 2003 and is seated in 2003, because a special election seats its winner
when it is held.

**A term ends when the term ends, not when the listings resume.** Sec. 112
makes it four years, so a November win closes four years on. O'Leary lists the
board in 1907 and in 1915 and not in 1911; reading the 1907 winners through to
1915 would put three named men in a seat for eight years on a source that
speaks to four. Their terms close in January 1912, and nothing names who held
those seats next. The note on such a row says the end is the statute's; where
the next listed election seats a successor on the same date the departure is
sourced and carries no note.

**So the roster stops naming people in 1912, and nothing names anyone until
1932.** For 1912–1931 no source in hand records who served, and the seat
counts for those years are an assumption, stated in `code/build/board_seats.py`
and labelled `assumed`: three seats, filled, held by white men. Two elections
inside the stretch are printed in the county's candidate history under the
district headings rather than under "County Board": November 1923 (Ingram in
Arlington, Duncan in Jefferson, Thornburke in Washington) and November 1927
(Duncan and Thornburke). Duncan is very likely the Duncan who held Jefferson
from 1895 in O'Leary, which would make the gap two seats wide rather than
three. Whether to enter these names in the roster is open.

**Mid-term handovers are terms like any other.** O'Leary records them as
prose beside the elected member ("Replaced by H. Dwight Smith in Dec.;
replaced by Lott W. Crocker in March 1873, replaced by Francis D. Schutt in
April"), and those are parsed into their own rows: the Arlington seat in
1872–73 is four terms. Where a month is given without a year, the year carries
from the previous handover and rolls forward when the month goes backwards.
Francis D. Schutt holds two consecutive terms in 1873, appointed in April and
elected in May; that is two terms, not a duplicate. From 1907 O'Leary gives
surnames only, so "Corbett" from 1907 is a different person in the roster from
"Frederick S. Corbett" before it; joining them is open.

**Novack's spans are split at elections.** He lists a person once with their
whole service compressed into a string ("1932-1947" for Elizabeth Magruder),
so a span is cut at each November election the person contested, using the
county's candidate history, and the months come from his parentheticals. He
sometimes dates a span from the election rather than from taking office
(Fisher "1963-1974" won in November 1963 and sat from January 1964), so a span
whose first year is one the person won without having stood the year before
begins the following January. A cut at an election the person stood in and
lost continues however the span began: Frisbie, appointed in November 1947,
stood that month and did not win, and his 1948 term is still the appointment.
A member appointed to a vacancy who then wins the seat at a same-day special
election is seated by it that November and the appointment ends then: Wilt,
appointed in January 1960, won the special for Krupsaw's unexpired term that
November, which Novack's note does not record and the county's does. Where an
appointment is dated and no departure accounts for it, the one member whose
span ends that year undated left in the month of the appointment; more than
one candidate stops the build.

**From 1995 a term is built from election results.** A November win starts a
four-year term the following January. A special election fills the rest of a
term that ended early: the member who left is closed at that month, the winner
serves until the seat's next regular election, and where two members' terms
end in the same year the county's own annotation ("to fill Eisenberg's
unexpired term") says whose seat it was; the build refuses to guess when it is
absent. The five people still serving when Novack published have their last
term closed the same way. A check runs every month from 1995 through 2026:
five members at large, six only in a month a special election changed hands.
The county and state sources both hold the 2021 election, and the build
insists they name the same winner there before using the second.

**Recorded vacancies.** Two in the whole period a roster covers, found by
counting the months each term covers against the seats that existed: the
Washington district seat from the May 1873 election until Samuel Titus was
appointed that December, and March and April 1990 between Milliken's
resignation and Hunter's special election. 1912–1931 is the only stretch not
swept, since there is no roster to sweep.

### Seat-years

`data/clean/board_seats.csv` is one row per year, 1870 through 2026: seats
held by each race, each gender and (from 1932) each party, in seat-years, so
a member who sat for four months of a year counts 4/12. It is computed from
`board_members.csv` for every year but 1912–1931, which are the assumption
above. Days are not recorded consistently, Novack giving some and the election
dates others, so the month is the unit, and **the handover month belongs to
the incoming member** (Sally, 22 September 2026).

The denominator is the months the Board existed that year, which is twelve for
every year but its first. Arlington's Board came into existence at the May
1870 election, so 1870 is scaled by the eight months it existed: it reads
three seats filled, because they were, for as long as there was a Board to
fill them. Divided by twelve it would read two, and a chart of that says the
Board grew from two seats to three, which it did not.

The seats held can never exceed the seats that exist (three magisterial
districts with one supervisor each from 1870; five members elected countywide
from the County Manager plan, adopted at the November 1931 referendum and
seated in January 1932), and fall short only in 1873 and 1990; anything else
stops the build. Race, gender and party are independent splits of the same
seats and must account for the same total in every year, which
`code/tests.py` checks by taking a term out of one split and asserting the
build refuses.

The Board's race coding is one code per person, so it is already a set of
categories that do not overlap. A member coded Hispanic carries no separate
race, so `white` here means white and not Hispanic, which is what the census
basis means from 1980; the two files line up and the figures drawn from them
can be read against each other.

`residents_per_seat` divides population by the seats that exist, not the
seats filled. Where a seat sat empty, each serving member represented more
people than the figure shows. Whether to divide by the filled count instead,
which would make the growth figure depend on the roster, is open.

### Race and gender of Board members

Race and gender come from `data/transcribed/by_claude/board_demographics.csv`,
one row per claim a source makes about a member, in the source's own words
with a citation to the page the document prints; and otherwise from a default,
a white man, labelled `assumed`. Each cell of `board_members.csv` says which.
Two sources disagreeing about a person stops the build, and an attributed name
that matches no roster name stops it too, so a near-miss cannot fall silently
into the default. The default is a claim, and this is what stands behind it in
each period:

| Period | Race | Gender |
|---|---|---|
| 1870–1888 | Five Black members named by Hjerpe (2021): Rowe, Syphax, Pinn, Pendleton, Allen. Pinn, Pendleton and Allen each rest on a reproduced 1880 census image; Rowe and Allen on narrative statements in her paper; Syphax on O'Leary, who writes that his photograph shows he was African American. The sentence naming the five as a group sits in her own list of open inquiries, and the file records it as such. O'Leary adds that "a majority of the early office holders" were probably African-American but cannot name them. Nobody on our side has checked the census linking. | Names in O'Leary. |
| 1889–1930 | One collective sentence: the board "became and remained all white for the duration of this system" (Hjerpe 2021, p.4), sourced to the county's election records. No per-person evidence. | Names in O'Leary. |
| 1931–1986 | Nothing per-person from any source. The default rests on Newman (1987) being described as the first Black member since Reconstruction. About 280 person-years. **The weakest stretch.** | Names and honorifics in Novack (1994). |
| 1987–present | Per-person: Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), and Tejada as the first Latino member (Hjerpe 2021). The Arlington Historical Society keeps a curated entry. | Names in the county candidate history. |

None of the three roster sources states anyone's race or gender. Race comes
from Hjerpe and O'Leary; gender comes from names and honorifics, which is a
weaker attribution than a statement and is labelled as such in the file. The
seat counts for 1870–1888 are therefore Hjerpe's identifications applied to
O'Leary's roster; Alex Keena's earlier year-level counts were a replication
of the same source and are not a second one.

What any source says, in full, is ten members recorded as other than White
and twelve women (Magruder, Cannon, Buchholz, Bozman, Grotos, Whipple, Favola,
Hynes, Garvey, Cristol, Coffey and Cunningham). Everyone else, 109 of 119
people, is recorded as a white man because no source speaks to them. The
verification to ask of County staff, and through them the Historical Society,
is therefore the default rather than the lists: every other member has been
treated as a white man; where is that wrong? That is Q3 in
`docs/questions.md`.

Two things from the record bear on the report's argument. Monroe first stood
in the April 1999 special election for Eisenberg's unexpired seat and lost to
Michael D. Lane by 169 votes, 9,530 to 9,361; he won the two-seat general that
November. Hjerpe argues that the at-large era's members of color all won in
cycles where two seats were up; Monroe is the case where the same candidate
loses the one-seat contest and wins the two-seat one seven months later. And
the *Sun*'s coverage of the November 1938 staggered-terms referendum carries
two contemporaneous claims about women and Board structure: the Arlington
County Woman's Democratic Club opposed the change, holding that staggering
would make it "virtually impossible for a woman to be elected to the board"
(`sun1938referendum`), and a week later the Organised Women Voters of
Arlington County objected to the ballot's wording (`sun1938womenvoters`).
Florence E. Cannon is elected parliamentarian of the Organised Women Voters
in the second notice and sits on the Board from 1948 to 1951.

### Party of Board members

Party has never been printed on the County Board ballot; the county's own
candidate history says so on its first page. So there is no official record
of a member's party, only of whose candidate they were, and that is what is
coded, per term rather than per person, because a label changes between
elections (Bozman ran as ABC's candidate five times and as a Democrat once).
Three sources, in order:

1. The county's candidate history, which prints a label in parentheses after
   a name from 1931, `(D)`, `(R)`, `(ABC)`, `(I)`, though not on every winner
   and rarely before 1950.
2. The state's elections database, which records party from 2007 and is the
   only source from 2022. Where its general-election row carries no party
   (2023 on), a win in that year's Democratic primary stands in.
3. Reporting, in `data/transcribed/by_claude/board_party.csv`, one quoted and
   cited claim per row, used only where the county prints `(I)` or nothing.

Where the county and the state both name a party they must agree, and a cited
claim that contradicts a party the county prints stops the build. A label the
build has not been told what to record stops it too: `elections.LABELS` in
`code/build/` maps every label a County Board candidate has carried, and a
winner under a label only losers have carried is a decision, not a default.

**The rule for reporting** (Sally, 23 September 2026): the party or coalition
whose candidate the source says the member was, and a party's open
endorsement makes someone its candidate whatever label they ran under. Dugan
in 1946 and Vihstadt in 2014 are coded Republican with "ran as an independent"
in the note. A source saying only that someone *leaned* a party's way
(Tillema, 1952) is not an endorsement and stays independent. ABC's endorsement
counts as ABC; where a source names both ABC and a party, the party (Fisher,
1967). ABC is its own band rather than folded into Democratic, because the
county recorded it and an ABC-majority Board from 1957 to 1966 is a finding.

| Period | Source | What it gives |
|---|---|---|
| 1932–1950 | County candidate history, where it prints a label | 9 of 32 terms. The rest are `unsourced` except where McCaffrey (2026a) names the 1949–52 independents and the 1952 appointees. |
| 1951–1966 | County candidate history | Every winner but Blevins (1956) and the two `(Convention)` nominees of 1955. `(ABC)` appears from 1957. |
| 1967–1983 | County prints `(I)` on most winners; reporting names the party | Fisher, Munsey, Purdy and Wholey as Democrats; Bozman as ABC's candidate; Grotos, Frankland and Detwiler as Republicans. Ricks stays `(I)`. |
| 1984–2006 | County candidate history | Every winner labelled. Bozman `(I)` through 1989, `(D)` in 1993. |
| 2007–2021 | County and state, checked against each other | Agree on every winner. |
| 2022– | State database | Party on the 2022 general; from 2023, the Democratic primary win. |

The reporting file has 26 rows, each a sentence in the source's own words
with its citation, keyed on the name and the term's start year: pieces by
Scott McCaffrey for the Sun Gazette and ARLnow (2009–2026), the Library of
Virginia's biography of Joseph Fisher, Joseph Wholey's obituary and an ARLnow
report of the 2020 special election. What it yields for 1932–2026 is 146
terms: 76 Democratic, 18 Republican, 15 ABC, 12 independent, 25 not recorded.
The built table reproduces three compositions reported independently, three
Republicans in 1970 and again in 1979 and three independents in 1952, none of
which was used to build it.

**Not attempted before 1932.** O'Leary's own summary of the magisterial era
is that "with few exceptions, party affiliation has to be inferred", and
nothing held names a party per person; the figure starts at 1932 with a gap
before it. It is recoverable: local elections of the period were run on party
tickets and the Alexandria Gazette printed them, so an RA with O'Leary's dates
could key a ticket per winner into the reporting file. The 23 terms no source
labels, mostly 1932–1960, are listed in Q29 of `docs/questions.md` with where
to look.

`board_seats.csv` carries the split as `dem`, `abc`, `rep`, `ind` and
`unrecorded`, seat-years from 1932, empty before. "Not recorded" is a band
rather than a gap because the seats existed and were held; what is missing is
the label.

---

## Voters

`data/clean/voters.csv` is Arlington's vote by party for two offices, one row
per election and office.

**For President**, every fourth year from 1872. Virginia has no party
registration, so nothing counts residents by party; the presidential vote is
the standard proxy and the one measure that arrives as a dataset. It counts
voters, not residents, and before 1966 the electorate was the one the 1902
constitution allowed, poll tax and literacy test, and before 1920 it was men.
The comparison the figures invite is therefore the Board against the people
who were allowed to vote, which the file name and axis label say so that no
caption has to. 1872–1920 is O'Leary's compilation of the Alexandria Gazette,
transcribed verbatim and parsed in `code/build/voters.py`. Party before 1924
is the nominee's, named in the build, since O'Leary prints it for 1912 only;
a name the build does not know stops it rather than falling into "other".
Three elections are kept and marked incomplete, and the figure leaves them
out: 1896, where the Washington district and the total are printed "?", and
1904 and 1908, of which O'Leary writes that the returns "appear incomplete"
(1904 sums to 256 votes against 826 four years earlier). 1924–2024 is the
state database's locality rows, which carry party on every candidate; its
Arlington rows for this office begin in 1924. The county's own candidate
history prints the same returns from 1920 and is read as a check: it agrees
with the state within five per cent in every year but 1980, where the
county's Carter figure is 25,003 against the state's 26,502 and the state's
canvass is kept.

**For County Board**, every year from 1931. This is what the smaller November
electorate did with the candidates it was offered, and it is not coded the
same way as the roster: a candidate is counted under the label the county
prints after their name, not under the party reporting later attached to the
winner. Votes for Dorothy Grotos in 1975 sit in "other" here while her seat
is Republican in `board_party`, deliberately; one figure is the choice on the
ballot, the other who sat. 1931–2021 is the county's candidate history, every
general and special contest in a year summed; 2022 on is the state database,
which names a party on the 2022 general and none after, so from 2023 a
Democratic primary winner is Democratic and everyone else is unrecorded
(Clement, Fierro and Cambridge are in that band). A year is incomplete where a
member the roster seats by election has no vote count: 1942 and 1949. Two
seats are elected in every fourth year from 1951 and a ballot then carries
two votes, so shares are of votes cast; that distorts a party's share only
where it ran fewer candidates than seats, which the county's record shows in
1951 (one independent), 1959 (one Democrat and one Republican against two
ABC) and 2003 (one Republican).

---

## Turnout

`data/clean/turnout.csv` puts four measures side by side, one row per year:
votes cast in the November County Board contests and the seats they filled;
the people that represents; registered voters; the population 18 and over;
and the presidential vote. Each measure has its own source column, because a
row draws on up to four documents at once.

**Votes are not voters.** A Board ballot carries one vote per seat being
filled, so `board_voters` divides the votes by the seats: exactly the number
of people who voted for the Board when one seat was filled, and a lower bound
when more than one was. **Seats are counted from the roster, not read off the
page.** The county prints "Vote for 2" on some two-seat contests and nothing
on others, so the build counts the terms in `board_members.csv` that an
election seated the following January, or a special election seated that
November. That makes 1931, 1935 and 1939 five-seat elections (the whole
Board, before terms were staggered), 1943 and 1960 two (1960 is the regular
seat and Wilt's special), 1947 two (Frisbie, appointed after the election, is
listed with no count), 1952 four (three same-day specials beside the regular
seat) and 1997 two. Since 1951 every two-seat year has been a House of
Delegates year, so the understatement lives in that one line and the caption
says so. Ballots cast would be the right number and no source in hand holds
it.

**Which years are not the county's vote.** The county's own page says its
tallies are complete only from 1971. A year is marked incomplete and not drawn
where a named candidate has no count (1942, 1949, and Frisbie in 1947, whose
page also says its totals are from 8 of 11 precincts) or where the page says
others ran who are not listed (1931). Before 1932 the Board was elected by
district, one seat each, so every voter cast one vote; O'Leary reports the
count for 1907 (756 voters across three districts) and 1915 (876) and "(No
returns.)" for the rest. Both are in the table and not drawn.

**The denominators.** Votes for the Board are the county's candidate history
1931–2021 and the state database from 2022, write-ins included. Registered
voters are the Department of Elections' monthly locality report for October
of each year from 2010 (`varegistration`), dated in the first days of
November, which is as the books stood for the election; nothing earlier is
online. The active list is `registered` and the inactive list is added in
`registered_all`. The population 18 and over is the census: the 1980 and 1990
Summary Tape Files' age tables and the API's tables for 2000–2020, all checked
against the county total on every fetch, and carried between censuses on a
straight line for the figure's share panel (`voting_age_est`, marked
`derived`); after 2020 the 2020 count is carried forward, which overstates
the 2021–25 shares a little. The presidential vote is `voters.csv`'s and is
marked `derived`. Three guards: the Board's voters can never exceed the
registered voters, nor the presidential vote of the same year, and the
registered can never exceed the adults.

The state's historical database gives votes, not voters, and no registration:
its `Total Votes Cast` is the sum of the candidates' votes, and `Total Ballots
Cast` appears only for 2025. The Department's precinct turnout files from
2007 were not used; 2008's lacks the central absentee precinct, and in several
years a precinct's row is repeated once per district it sits in.

**What the series shows.** The Board's vote is drawn as four series by what
else the November ballot carried (the `cycle` column: president, governor,
midterm, delegates), because drawn as one line it is a sawtooth whose teeth
are the ballot and not the Board. In a presidential year about nine in ten of
the county's presidential voters also vote for the Board. As a share of the
county's adults, the presidential-year Board vote rose from about a third in
1980 to 57 per cent in 2024; the House of Delegates years, when the Board tops
the ballot, from a fifth to 30 per cent in 2023; and the midterm and
governor's years sat at a third for decades and have converged on the
presidential-year level since 2017. In November 2024: 196,563 adults (the 2020
count), 164,865 active registered voters, 128,362 who voted for President and
113,209 for the County Board.

**Milestones, for the prose.** 1870, the Board is created, elected in May by
district. 1904, local elections move from May to November under the 1902
constitution, whose poll tax and literacy test shrank the electorate until the
1960s. 1920, women vote: O'Leary's presidential returns go from 804 in 1916 to
1,831 in 1920. 1932, the at-large Board of five, staggered from 1940 so that
the Board is on every November ballot. 1966, the poll tax falls (*Harper v.
Virginia Board of Elections*). 1971, the vote at 18. 2020, no-excuse absentee
and early voting.

---

## The census scans

Nine PDFs, 521 pages, in `data/raw/us_census_bureau/`, from the published
1870, 1880 and 1890 volumes. Seven have no text layer;
`data/transcribed/by_ocr/` holds OCR of all of them. The method is to search
the OCR to locate a table, then render the page and read it by eye. OCR
misread digits on the first table checked (17,546 as 17,516, 14,339 as
14,830), which is why it is never the source of a number.

The files are the Bureau's own. `code/fetch/census_volumes.py` fetches the
Bureau's copy of a chunk already held from each volume and compares checksums;
both the 1880 and 1890 files matched byte for byte on 23 September 2026, and
the script refuses to go on if one ever stops matching. It also saves each
volume's first chunk, which carries the title page, so the bibliography is
built from a page in the repository.

---

## Works cited

Every source named on this page has an entry in `paper/sources.bib`, which the
prose and the data share: a `source` cell in `data/clean/` holds the same
citekey a footnote in the report will. `bash run.sh` refuses to build if a
cell names an entry that is not there.

One entry is still marked provisional in its annotation, POP-TWPS0076, for the
reason given under Population and race. Two details were corrected against the
documents while the entries were built: O'Leary's electoral history is dated
March 2010 in its own text (the 2012 once carried was the PDF's creation
date), and the county's compilation is titled *Arlington County Election
Results*; "Candidate History, 1920-Present" was the website's link text.

Sources consulted to settle a question rather than to take numbers from are
cited here rather than saved into `data/`. **Their copies live in the
project's Drive folder**, in `sources/documents`
(<https://drive.google.com/drive/folders/10SGuURB-ldC1AzM3ClsdL_tAiWeFIZB4>),
named for a person reading the folder: author, year, then the title as the
document prints it, `Pratt 1995 - Arlington's At-Large Electoral System.pdf`.
Each entry in `paper/sources.bib` carries a "Filed in Drive as" line, which is
where you check that a cited source is filed. Hjerpe's is a PDF snapshot
rather than the live Google Doc, which belongs to someone outside the project
and can change; cite the snapshot. The ten pieces of reporting cited for
party are not yet filed.

**City of Alexandria.** *A History of the Boundaries of the City of
Alexandria, Virginia: 1749-2024.*
`alexandriava.gov/sites/default/files/2024-06/History of the Boundaries of Alexandria 1749-2024.pdf`
— Alexandria annexed land from Alexandria County in 1915 and again in 1930,
the second including the Town of Potomac.

**Rose, C. B.** "Annexation of a Portion of Arlington County by the City of
Alexandria in 1915." *Arlington Historical Magazine*, 1964.
`arlhist.org/wp-content/uploads/2017/02/1964-4-Annex.pdf`
— The size and effective date of the 1915 annexation: 866 acres, effective
1 April 1915.

**Anderson, Robert Nelson.** "Arlington Adopts the County Manager Form of
Government." *Arlington Historical Magazine*, 1958, 52–67.
— A first-hand account of the 1930 referendum and the 1931 election, by a
founder of the Historical Society.

**Bestebreurtje, Lindsey.** *Built by the People Themselves: African American
Community Development in Arlington, Virginia, from the Civil War through Civil
Rights.* Two documents with one title, entered separately: the 2017 George
Mason University dissertation (`bestebreurtje2017`, from its own title page)
and the 2024 University of South Carolina Press book (`bestebreurtje2024`,
from the publisher's catalogue). A digital exhibit at lindseybestebreurtje.org
is a third. Neither document is in hand; the page cited for the 1930
candidacies of Harris, Morton and Mosley has not been read (Q25).

**Pratt, Sherman W.** "Arlington's At-Large Electoral System: A Study of Its
History, Strengths, and Weaknesses." *Arlington Historical Magazine*, October
1995, 19–35.
— Heard Vollin's testimony and holds his own tape recordings of him. The
source for both Vollin citations, which are two proceedings, not one: the
federal suit, *George Vollin, Jr., et al. v. Mills E. Godwin, et al.*, E.D.
Va., Civil Action No. 173-74-A, in which Vollin testified in 1974
(`vollin1974`); and *Vollin v. Arlington County Electoral Board*, 216 Va. 674,
222 S.E.2d 793, decided 5 March 1976 (`vollinelectoralboard`), a petition to
put district-versus-at-large election to a vote, denied because the county had
already adopted the County Manager Plan. Cases are entered as `@misc` with the
court and docket in `note`, because biblatex-chicago in notes mode silently
drops the legal entry types.

**Hjerpe, Grace.** *A History of Representation on the Arlington County Board,
1870-Present.* Updated 15 July 2021. Google Doc, shared with Sally.
— Names all five Black members of the Reconstruction-era board, with 1880
manuscript census records reproduced as appendices, and tabulates every Board
member by district from 1871 to 1888. Also documents the 1930
change-of-government referendum, the 1974 Vollin case, and that the federal
government began removing residents from Freedman's village in 1888, the year
Tibbett Allen, the last Black member, was removed for "non-residence". Cited
by the page the document prints, which runs one behind the PDF's. Its
footnotes point at `vote.arlingtonva.us`, which now returns a not-found page
rendered as a PDF; the live copies are on `vote.arlingtonva.gov`.

**O'Leary, Frank.** *The Electoral History of That Part of Alexandria County
Now Known as Arlington County, 1870-1920.* Version 2, March 2010. Arlington
County Treasurer. In `data/raw/arlington_county/`.

**Arlington County Office of Voter Registration and Elections.** *Arlington
County Election Results* ("Candidate History, 1920-Present"). Last updated
18 November 2021. In `data/raw/arlington_county/`. The county has since taken
it down; its results page points to the state.

— Between them these cover Board elections for the whole period. Both are
compilations rather than primary records, and both say so: O'Leary compiles
from the Alexandria Gazette with party affiliation "inferred", and the
Electoral Board's preamble notes incomplete early tallies and invites
corrections. They record elections rather than service, and neither carries
race or gender.

**Virginia Department of Elections.** *Historical Elections Database.*
`historical.elections.virginia.gov`. Every County Board contest from 2000 and
Arlington's presidential vote from 1924, saved as the database's own CSV in
`data/raw/va_dept_of_elections/`. Cited by contest id, the database's own key
for a race. Its monthly *Registration Statistics* supply registered voters
from 2010.

**Novack, Norman S.** "Six Decades of Arlington Leadership." *Arlington
Historical Magazine*, 1994.
`arlhist.org/wp-content/uploads/2020/02/1994-6-Decades.pdf`
— A complete roster of County Board members with terms of service to the
month, from the County Manager plan through 1994, with the circumstances of
each mid-term departure. The roster's source for 1932–1994. Carries no race or
gender. In `data/raw/arlington_historical_magazine/`.

**U.S. Census Bureau.** *Population of States and Counties of the United
States: 1790-1990.* Virginia notes, printed p.185.
— Establishes that Alexandria city became independent of the county in 1900
for census purposes, that the county was renamed Arlington in 1920, and that
county figures reflect boundaries as reported at each census. The Virginia
pages are excerpted into `data/raw/us_census_bureau/` because numbers are
taken from them.

**The Sun (Arlington).** 11 November 1938, p.1 (`sun1938referendum`) and 18
November 1938, p.4 (`sun1938womenvoters`), from the Library of Virginia's
Virginia Chronicle. The first is in `data/raw/arlington_sun/` because a number
is taken from it (Q27).
