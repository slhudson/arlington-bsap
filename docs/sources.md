# Sources

What backs each number in `data/clean/`, by period, and what is still open.
Every `source` cell there holds a citekey from `paper/sources.bib` or one of
three placeholders (`UNSOURCED`, `DERIVED`, `ASSUMED`); `code/build/citekeys.py`
says what each means, and `bash run.sh` counts them on every build.

---

## What "Arlington County" means here

The Board governed a territory whose name, boundaries and census treatment all
changed across the period. Every population figure depends on getting this
right, and the one error found so far came from getting it wrong.

**Arlington County is the territory of the present-day county: the Arlington,
Jefferson and Washington magisterial districts. It excludes the City of
Alexandria in every year**, because the Board never governed the city.

| Period | Name | What the published county figure contains |
|---|---|---|
| to 1846 | Alexandria County, D.C. | part of the District of Columbia |
| 1847–1919 | Alexandria County, Virginia | the three districts **and** Alexandria city |
| 1920– | Arlington County, Virginia | the three districts only |

Two dates do the work. **In 1900** Alexandria city became independent of the
county, so from that census onward the published county figure already excludes
the city. **In 1920** the county was renamed — a name change only, the
territory did not move.

So 1870, 1880 and 1890 need a county-only figure derived, by subtracting the
city or summing the three districts. 1900 onward can be used directly. That is
why the early years are the hard ones.

*Source: Population of States and Counties of the United States: 1790-1990,
census.gov, Virginia notes, pdf p185.*

### The three districts, and what sits inside them

| District | 1890 | 1880 |
|---|---|---|
| Arlington | 2,013 | 1,754 |
| Jefferson | 1,303 | 1,319 |
| Washington | 942 | 814 |
| **County outside the city** | **4,258** | **3,887** |

**Freedman village is not a fourth district.** It was a settlement of formerly
enslaved people on the confiscated Lee estate, inside Arlington district. The
census lists it as an indented sub-line — "Arlington district, *including*
Freedman village" — the same way it lists Alexandria city's wards beneath the
city total. Its 338 residents in 1890 are already within Arlington district's
2,013.

Counting it as a fourth district adds those people twice and gives 4,596, the
figure in the delivered workbook. See questions.md for the correction, and for why the
settlement matters beyond the arithmetic.

### Checks for any new early figure

- Does county-outside-city equal the sum of the three districts?
- Does city plus the three districts equal the published county total?
- Is every line being added a place, rather than a detail of the line above it?

The third is the one that failed.

---

## Population and race, year by year

Every total from 1870 to 2020 is taken from a published Census Bureau
document that is in `data/raw/us_census_bureau/`. The race split is sourced
only for 1870–1890, derived from the volumes as county minus city. From 1900
on it is the delivered workbook's figures: for 1900–1980 no source is
recorded (with Alex, questions.md), and for 1990–2020 the Bureau's own race
tables are in `data/raw/` but are not used until the Hispanic-definition
question is settled, since they count Hispanic across races and the
workbook does not.

| Year | Total | Total from | Race from |
|---|---|---|---|
| 1870 | 3,185 | `walker1872` | `walker1872` |
| 1880 | 3,887 | `census1880` | `census1880` |
| 1890 | 4,258 | `census1890` | `census1890` |
| 1900 | 6,430 | `forstall1996` | `keena-workbook` |
| 1910 | 10,231 | `forstall1996` | `keena-workbook` |
| 1920 | 16,040 | `forstall1996` | `keena-workbook` |
| 1930 | 26,615 | `forstall1996` | `keena-workbook` |
| 1940 | 57,040 | `forstall1996` | `keena-workbook` |
| 1950 | 135,449 | `forstall1996` | `keena-workbook` |
| 1960 | 163,401 | `forstall1996` | `keena-workbook` |
| 1970 | 174,284 | `forstall1996` | `keena-workbook` |
| 1980 | 152,599 | `forstall1996` | `keena-workbook` |
| 1990 | 170,936 | `forstall1996` | `keena-workbook` |
| 2000 | 189,453 | `censusapi` | `keena-workbook` |
| 2010 | 207,627 | `censusapi` | `keena-workbook` |
| 2020 | 238,643 | `censusapi` | `keena-workbook` |

`walker1872`, `census1880`, `census1890` are the printed volumes;
`forstall1996` is *Population of States and Counties of the United States:
1790-1990*; `censusapi` the Bureau's data files.

**Where the built figures differ from the delivered workbook.** Three cells:
1870 white (workbook 1,075; the volume gives 1,175 — Jefferson district keyed
as 283 for 383), 1890 total (4,596; 4,258 — Freedman village counted as a
fourth district when the table prints it inside Arlington district), and 1890
white (2,195; 2,135 — foreign white female keyed as 365 for 305). 1880 and
every total from 1900 on match the workbook exactly. The three are with Alex
to confirm; the build uses the printed figures.

**The categories were never meant to sum.** The census asks race and Hispanic
origin as two separate questions, so a Hispanic resident appears in both a
race count and the Hispanic count. For 1990 the cited source shows this
exactly: white 130,873 + Black 17,940 + American Indian 537 + Asian/PI 11,560
+ Other race 10,026 = 170,936, with Hispanic (23,089) cutting across all five.
The workbook mixes the two systems — non-Hispanic white alongside all-race
Black and Asian totals — which is the 1970 and 1990 overshoot. Whether to
recode Hispanic as an ethnicity across races is with Alex (questions.md).

| Years | Categories the census reports |
|---|---|
| 1870–1940 | White, Black |
| 1950–1960 | White, Black, AAPI |
| 1970–2020 | White, Black, AAPI, Hispanic/Latino |

---

## What backs the Board data

Two delivered workbooks — seat counts by year, 1871–2026, and a member
database, 1932–2026 — carry no source column, and the material they were
compiled from is not in the repository. The roster, the race and gender
attributions, and the seat-years below were built so that a source stands
behind each row; the workbooks fill what nothing else covers (1916–1931
seats; race and gender from 1932 where no source speaks) and are otherwise
what the built files are checked against.

### A roster built from sources

`data/clean/board_members.csv` holds one row per person per term: name,
term number, district, and when service began and ended. 217 terms, 1870 through 2026
(the next election is November 2026), from three sources in sequence: O'Leary's electoral
history to 1915, Novack's roster from 1932 to 1994, and election results
after that - the county's candidate history to 2021, the state's elections
database from 2022. Nothing covers 1916-1931.

`term_number` counts within a person, so someone appointed to a vacancy who
then won twice has three rows numbered 1, 2, 3. William A. Rowe has eight,
including his move from Jefferson district to Arlington at term 7.

Novack records a person once with their whole service compressed into a string
— "1932-1947" for Elizabeth Magruder — so those spans are split at each
election the person contested, using the county's candidate history. Magruder
becomes four terms rather than one block. Members elected in November take
office the following January.

**From 1995 a term is built from election results.** A November win starts
a four-year term the following January. A special election fills the rest of
a term that ended early: the member who left is closed at that month, and the
winner serves until the seat's next regular election. Where two members' terms
end in the same year, the county's own annotation ("to fill Eisenberg's
unexpired term") says whose seat it was, and the build refuses to guess when
it is absent. The five people still serving when Novack published have their
last term closed the same way. A check runs every month from 1995 through 2026: five
members at large, six only in a month a special election changed hands.

The county and state sources both hold the 2021 election, and the build
insists they name the same winner there before using the second.

A term is the natural unit — person-years fall out of it, while the reverse
does not, because a term starting in May or ending in February cannot be
recovered from a list of years.

A vacant seat is not a row: nobody served, so there is no person and no term.

**Mid-term handovers are terms like any other.** O'Leary records them as prose
beside the elected member — "Replaced by H. Dwight Smith in Dec.; replaced by
Lott W. Crocker in March 1873, replaced by Francis D. Schutt in April" — and
those are parsed into their own rows. The Arlington seat in 1872-73 is four
terms: Syphax from May to December 1872, Smith to March 1873, Crocker to April,
Schutt to the May election. Where a month is given without a year, the year
carries from the previous handover and rolls forward when the month goes
backwards.

Francis D. Schutt holds two consecutive terms in 1873 — appointed in April,
then elected in May. That is two terms, not a duplicate.

**Recorded vacancies.** A vacant seat produces no row, since nobody served.
One is documented in this period: the Washington district seat was vacant from
the May 1873 election until Samuel Titus was appointed that December. Titus has
a term; the vacancy is recorded here.

### Seat-years

`data/clean/board_seats.csv` is one row per year, 1870 through 2026: seats
held by each race and by each gender, in seat-years, so a member who sat for
four months of a year counts 4/12. From 1932 (and for 1870–1915) it is
computed from `board_members.csv`; the handover month belongs to the incoming
member (Q13). 1916–1931 has no terms and stays on the delivered counts, and a
`source` column says which. The seats held can never exceed the seats that
exist, and fall short only in 1870 (the Board began in May), 1873 (a recorded
vacancy) and 1990 (a February resignation, a May special election); anything
else stops the build.

Against the delivered counts, 138 years overlap: 120 identical, 128 within
half a seat. The rest are the three Reconstruction terms in Q17 and handover
years where the delivered file's half-and-half split and the months disagree.

### Compared with the delivered roster

The delivered member database and the built roster overlap from 1932 to
1994, and **agree on membership in 60 of 63 years** — two files assembled independently, one from an unrecorded source,
reaching the same answer for sixty years.

The three exceptions:

- **1957** — the delivered roster reads `Bleviins`; Novack has Lucas H.
  **Blevins**. A doubled letter.
- **1939** — Novack ends Ames, McShea and Yeatman in 1939 and begins Campbell,
  DeLashmutt and Lloyd in 1940; the delivered roster seats the incoming three
  in 1939.
- **1963** — Novack writes Fisher "1963-1974"; the delivered roster seats him
  from 1964. The county's candidate history settles it: Fisher won in
  November 1963, so he sat from January 1964, and Novack dated the span from
  the election. The build now reads a span that way wherever its first year
  is one the person won the November election without having stood the year
  before.

1939 is the same question in the other direction — Novack seats Campbell,
DeLashmutt and Lloyd from 1940, after their November 1939 wins — and there
the build follows Novack.

## Race and gender of Board members

Race and gender come, in order, from `data/transcribed/by_claude/board_demographics.csv`
— one row per claim a source makes about a member, in the source's own words
with a citation — then from the delivered member database for 1932 on, and
otherwise from a default: a white man. Each cell of `board_members.csv` says
which. Where an attribution and the workbook both speak, they agree everywhere.
The default is a claim, and the table below says what stands behind it in each
period.

| Period | Race | Gender |
|---|---|---|
| 1870–1888 | Five Black members named by Hjerpe (2021), identified from 1880 manuscript census records; O'Leary (2012) adds that "a majority of the early office holders" were probably African-American but lacks evidence to name them. The five are in the attributions file. Not yet verified against the census ourselves. | Names in O'Leary. |
| 1889–1930 | One collective sentence: the board "became and remained all white for the duration of this system" (Hjerpe 2021, p.4), which she sources to the county's election records. No per-person evidence. | Names in O'Leary. |
| 1931–1986 | Nothing per-person from any source. The default rests on Newman (1987) being described as the first Black member since Reconstruction. About 280 person-years. **The weakest stretch.** | Names and honorifics in Novack (1994). |
| 1987–present | Per-person: Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), and Tejada as the first Latino member (Hjerpe 2021). The Arlington Historical Society keeps a curated entry. | Names in the county candidate history. |

None of the three roster sources — O'Leary, Novack, the county candidate
history — states anyone's race or gender. Race comes from Hjerpe and from
whatever the Historical Society can add. Gender comes from names and
honorifics, which is a weaker attribution than a statement and is labelled as
such in the file.

**What is being asked of the Arlington Historical Society.** The attributions
file, presented as two short lists — Black members and women — with the
default stated plainly: every other member has been treated as a white man;
where is that wrong? The lists are short enough to check by eye, and the
1931–1986 stretch is where an answer would matter most.

---

## The census scans

Nine PDFs, 521 pages, in `data/raw/us_census_bureau/`, from the published 1870, 1880 and
1890 volumes. Seven have no text layer. `data/transcribed/by_ocr/` holds OCR of
all of them.

**The method:** search the OCR to locate a table, then render the page and read
it by eye. OCR found every table cited here and misread digits on the first one
checked — 17,546 as 17,516, 14,339 as 14,830 — which is why it is never the
source of a number.

Where the volumes came from is not recorded. The filenames match how the Census
Bureau chunks its scanned volumes, but that is an inference. See questions.md
questions.md.

---

## Works cited

Every source named on this page has an entry in `paper/sources.bib`, which the
prose and the data share: a `source` cell in `data/clean/` holds the same
citekey a footnote in the report will. `bash run.sh` refuses to build if a cell
names an entry that is not there, so a number that cannot be traced to a
document stops the build rather than reaching a figure.

Three entries are marked provisional in their annotations, because the excerpt
we hold carries no front matter: the 1880 and 1890 volumes, whose identity is
inferred from the filename, and working paper POP-TWPS0076. That is the open
question below, now visible in the bibliography as well as in prose.

Two details were corrected against the documents while the entries were built.
**O'Leary's electoral history is dated March 2010** in its own text; the 2012
previously carried in the data was the PDF file's creation date. And the
county's compilation is titled **Arlington County Election Results**;
"Candidate History, 1920-Present" was the website's link text.

The sources below are consulted to settle a question rather than to take
numbers from. They are cited here rather than saved into `data/`, which holds
only material we take numbers out of.

**Their copies live in `documents/` in the project's Drive folder**, named for
a person reading the folder rather than for a machine: author, then year, then
the title as the document prints it — `Pratt 1995 - Arlington's At-Large
Electoral System.pdf`. That is deliberately not the citekey. A citekey is a
handle for LaTeX and for the `source` columns, where short matters; a filename
answers "what is this?" at a glance. Each entry in `paper/sources.bib` carries
a "Filed in Drive as" line, which is where the two are tied together and where
you check that a cited source is actually filed. Hjerpe's is a PDF snapshot
rather than the live Google Doc, which belongs to someone outside the project
and can change or be withdrawn; cite the snapshot.

**City of Alexandria.** *A History of the Boundaries of the City of Alexandria,
Virginia: 1749-2024.*
`alexandriava.gov/sites/default/files/2024-06/History of the Boundaries of Alexandria 1749-2024.pdf`
— Establishes that Alexandria annexed land from Alexandria County in 1915 and
again in 1930, the second including the Town of Potomac. Used for questions.md
questions.md.

**Rose, C. B.** "Annexation of a Portion of Arlington County by the City of
Alexandria in 1915." *Arlington Historical Magazine*, 1964.
`arlhist.org/wp-content/uploads/2017/02/1964-4-Annex.pdf`
— Gives the size and effective date of the 1915 annexation: 866 acres from
Arlington County, effective 1 April 1915. Used for questions.md.

**Hjerpe, Grace.** *A History of Representation on the Arlington County Board,
1870-Present.* Updated 15 July 2021. Google Doc, shared with Sally.
— The paper the handoff refers to. Names all five Black members of the
Reconstruction-era board, with 1880 manuscript census records reproduced as
appendices, and tabulates every Board member by district from 1871 to 1888. It
also documents the 1930 change-of-government referendum, the 1974 Vollin case,
and that the federal government began removing residents from Freedman's
village in 1888 — the year Tibbett Allen, the last Black member, was removed
for "non-residence".

Its footnotes point at two primary sources we had not found:

**O'Leary, Frank.** *The Electoral History of That Part of Alexandria County
Now Known as Arlington County, 1870-1920.* Version 2. Arlington County
Treasurer. Now in `data/raw/arlington_county/`.

**Arlington County Office of Voter Registration and Elections.** *Candidate
History, 1920-Present.* Last updated 18 November 2021. Now in
`data/raw/arlington_county/`. The county has since taken it down; its results page
points to the state.

**Virginia Department of Elections.** *Historical Elections Database.*
`historical.elections.virginia.gov`. Every County Board contest from 2021 on,
by precinct and vote channel, saved as the database's own CSV in
`data/raw/va_dept_of_elections/` by `code/fetch/elections.py`. Cited by contest id,
which is the database's own key for a race.

— Between them these cover Board elections for the whole period. **Both are
compilations rather than primary records**, and both say so: O'Leary compiles
from the Alexandria Gazette with party affiliation "inferred", and the
Electoral Board's own preamble notes incomplete early tallies and invites
corrections. They record elections rather than service, and neither carries
race or gender.

Hjerpe's 2021 footnotes point at `vote.arlingtonva.us`, which now returns a
not-found page *rendered as a PDF* — a naive fetch gets an 85 KB file that
looks like a document. The live copies are on `vote.arlingtonva.gov`.

**Novack, Norman S.** "Six Decades of Arlington Leadership." *Arlington
Historical Magazine*, 1994. `arlhist.org/wp-content/uploads/2020/02/1994-6-Decades.pdf`
— A complete roster of County Board members with terms of service to the month,
from the adoption of the County Manager plan in 1930 through 1994, including
the circumstances of each mid-term departure and special election.

The roster's source for 1932–1994. It carries no race or gender. The PDF is
in `data/raw/arlington_historical_magazine/` and the transcription in
`data/transcribed/by_claude/`.

**U.S. Census Bureau.** *Population of States and Counties of the United
States: 1790-1990.* Virginia notes, printed p.185.
— Establishes that Alexandria city became independent of the county in 1900 for
census purposes and that the county was renamed Arlington in 1920; and that
county figures reflect boundaries as reported at each census rather than a
constant area. The Virginia pages are excerpted into `data/raw/us_census_bureau/`
because numbers are taken from them; the notes are cited here.

## For a research assistant

Roughly in order of value. The first items are mechanical and need no
judgement, so they are the easiest to hand over.

1. **Trace the race splits for 1870, 1880 and 1890.** The tables found so far
   cover the county including the city; a county-only split may not exist in
   published form, in which case record how it must be derived.
2. **Establish where the scanned volumes came from** — a citation per file.
3. **Establish what supports the 1931–1986 default.** Start with the
   Historical Society's reply. The judgement-heavy one.
4. **Verify the five Reconstruction-era members** against the 1870 and 1880
   manuscript census, following Hjerpe's method.
5. **Find a published statement for each gender row** in
   `data/transcribed/by_claude/board_demographics.csv` — an obituary, a
   profile — to replace "inferred by Claude from name".
6. **Check the roster's name forms from 1907**, where O'Leary gives surnames
   only (see questions.md).

Record each source as you go — the point is that every coded cell can be
traced. A new source means an entry in `paper/sources.bib`, built from the
document rather than from memory, and the citekey written into the `source`
cell it backs. Until then the cell says `unsourced`, and every build counts it.
