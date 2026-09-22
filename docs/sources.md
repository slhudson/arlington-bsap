# Sources

What backs each number, and what does not yet. Covers both strands: the census
population figures, and the race and gender coding of Board members.

This is also the work order for a research assistant — see the end.

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
figure currently in `data/transcribed/by_human/`. See questions.md for the correction, and for why the
settlement matters beyond the arithmetic.

### Checks for any new early figure

- Does county-outside-city equal the sum of the three districts?
- Does city plus the three districts equal the published county total?
- Is every line being added a place, rather than a detail of the line above it?

The third is the one that failed.

---

## Population totals, year by year

| Year | Workbook | Status |
|---|---|---|
| 1870 | 3,185 | **confirmed** |
| 1880 | 3,887 | **confirmed**, two independent ways |
| 1890 | 4,596 | **contradicted** — the tables give 4,258 |
| 1900 | 6,430 | **confirmed** |
| 1910 | 10,231 | **confirmed** |
| 1920 | 16,040 | **confirmed** |
| 1930 | 26,615 | **confirmed** |
| 1940 | 57,040 | **confirmed** |
| 1950 | 135,449 | **confirmed** |
| 1960 | 163,401 | **confirmed** |
| 1970 | 174,284 | **confirmed** |
| 1980 | 152,599 | **confirmed** |
| 1990 | 170,936 | **confirmed** twice |
| 2000 | 189,453 | not yet checked |
| 2010 | 207,627 | not yet checked |
| 2020 | 238,643 | not yet checked |

Eleven of sixteen totals are traced to a published table. 1900–1990 all come
from one table in *Population of States and Counties of the United States:
1790-1990*, and every one matched exactly.

The per-cell record, with volume, table and page, is
`data/transcribed/by_human/census_verification.csv`. It is compiled here rather than received
— the three workbooks beside it stay exactly as delivered, and a discrepancy is
recorded, never corrected in place.

---

## Race and ethnicity figures

Much less well established than the totals.

| Years | Categories the census reports |
|---|---|
| 1870–1940 | White, Black |
| 1950–1960 | White, Black, AAPI |
| 1970–2020 | White, Black, AAPI, Hispanic/Latino |

The gaps are a feature of the source rather than of this dataset, which is why
questions.md matters.

**The categories were never meant to sum.** The census asks race and Hispanic
origin as two separate questions, so a Hispanic resident appears in both a race
count and the Hispanic count. For 1990 the cited source shows this exactly:
white 130,873 + Black 17,940 + American Indian 537 + Asian/PI 11,560 + Other
race 10,026 = 170,936, with Hispanic (23,089) cutting across all five.

The workbook mixes the two systems — non-Hispanic white alongside all-race
Black and Asian totals, with American Indian and Other race dropped. That
accounts for the 1990 overshoot of 381 to the person. See questions.md.

**1870, 1880 and 1890 are now fully derived from the volumes.** Each year's
county figure comes from subtracting the city, with both the total and the race
split read off published tables:

| Year | | Workbook | From the sources | |
|---|---|---|---|---|
| 1870 | total | 3,185 | 3,185 | confirmed |
| | white | 1,075 | **1,175** | differs by 100 |
| | black | 2,010 | 2,010 | confirmed |
| 1880 | total | 3,887 | 3,887 | confirmed |
| | white | 1,693 | 1,693 | confirmed |
| | black | 2,194 | 2,194 | confirmed |
| 1890 | total | 4,596 | **4,258** | differs by 338 |
| | white | 2,195 | **2,135** | differs by 60 |
| | black | 2,123 | 2,123 | confirmed |

1880 is confirmed in full. In the derived figures, white plus black accounts for
each year's total exactly — no residual in any of the three. The
"Other/multiracial/unreported" band the charts currently show for these years
(3.1% in 1870, 6.0% in 1890) is an artefact of the discrepancies, not a
category of residents.

The 338 in 1890 is the Freedman village double count. The 100 in 1870 and the
60 in 1890 are keying differences with no pattern between them.

---

## What backs the Board data

Nothing is recorded, for either file.

`board_seats.csv` covers 156 years of seat counts with no source noted.
`board_members.csv` covers 497 person-years with race and gender coded on every
row and no source column. The `notes` column holds appointments and
resignations for 276 rows, which is not sourcing.

Unlike the census, there is no primary material behind these anywhere in the
repository — they rest on news coverage, the Arlington Historical Society and
obituaries.

### What the two files can say about each other

Sourcing them needs archival work, but they overlap from 1932 and can be
checked against each other. That has now been done.

**The seat counts are internally coherent everywhere.** Across all 153 reported
years, the four race categories sum to the number of seats, men plus women sum
to the number of seats, and the two totals agree. Three seats through 1930,
five from 1932, fractions included. No drift.

**The roster reproduces the seat counts in 82 of 95 overlapping years.** All 13
exceptions are years in which more people served than there were seats, which
is what the fractional seats encode. So the two files agree wherever nothing
complicated happened.

**One duplicate.** Alfred Frisbie has three rows for 1952. The coding agrees
across them, so nothing is miscoded, but a tally built from the roster would
count him three times. 1952 was a chaotic year: three members removed on 17
September, four appointed the next day, and four more elected in November.

**The fractional seats cannot currently be reconstructed.** The roster records
`appointed`, `resigned`, `died` and `removed` as yes/no flags, with the actual
dates only in free-text notes — "Removed 9/17/52", "until death on Jan 11". So
the halves in the seat counts cannot be checked against service dates without
parsing prose. Nor is the convention obviously proportional: in 2003 Charles
Monroe died on 11 January and the year is still split half and half.

Turning those note dates into real date columns would make every fraction
checkable. Twenty-nine of the thirty-two flagged rows already carry a date;
three do not, and are a question for Alex.
The rule itself is in questions.md.

All three checks that could be made structural now run in `build/` and were
verified by breaking them deliberately.

| Period | Status |
|---|---|
*Six Decades of Arlington Leadership* (Works cited) covers membership and terms
from 1930 to 1994, which is most of the roster's span. It carries no race or
gender, so it verifies who served rather than how they were coded.

| 1871–1888 | Five named Black members. Census-linkable: Grace Hjerpe's 2021 paper demonstrates the method using 1880 manuscript census records. Small n, verifiable — not yet verified. |
| 1889–1986 | Coded all-White, resting on the "first since Reconstruction" framing. **Weakest link**, ~490 person-years. |
| 1987–present | Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), plus Tejada. Well documented; the Arlington Historical Society maintains a curated entry. |
| Gender, all years | Naming conventions plus some obituaries. Adequate with a methods note; cheap to spot-check. |

### The one that matters

The 1889–1986 stretch is a negative claim — that no Black member served for
nearly a century — and a negative claim needs evidence that someone looked.

**That has changed.** Grace Hjerpe's paper addresses it directly: after 1888 the
board "became and remained all white for the duration of this system", and no
Black candidate is recorded as running for the county board again until after
1930. She sources this to Arlington County's own election records rather than
to the phrase, and those records are listed under Works cited.

So the claim now rests on candidate histories kept by the Elections Office,
which is a different and much stronger thing than a curator's wording. What
remains is to fetch those records and check them, rather than to find out
whether anyone ever looked.

Sally is still contacting the Arlington Historical Society
(info@arlingtonhistorical.com), which may hold more.

---

## The census scans

Nine PDFs, 521 pages, in `data/raw/census/`, from the published 1870, 1880 and
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

Prose sources consulted to settle a question. They are cited here rather than
saved into `data/`, which holds only material we take numbers out of.

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

**Office of Frank O'Leary.** *The Electoral History of That Part of Alexandria
County Now Known as Arlington County, 1870-1920.*
`vote.arlingtonva.us/files/assets/vote/elections/electionresults/pre-1920_candidate_history.pdf`

**Arlington County Elections.** *Candidate History, 1920-Present.*
`vote.arlingtonva.us/files/assets/vote/elections/electionresults/candidate-history.pdf`

— Between them these cover Board membership for the whole period the report
addresses. They are the primary source the Board data has been missing. Not yet
fetched or transcribed.

**Novack, Norman S.** "Six Decades of Arlington Leadership." *Arlington
Historical Magazine*, 1994. `arlhist.org/wp-content/uploads/2020/02/1994-6-Decades.pdf`
— A complete roster of County Board members with terms of service to the month,
from the adoption of the County Manager plan in 1930 through 1994, including
the circumstances of each mid-term departure and special election.

This is the first source found for the Board membership data, which otherwise
has nothing behind it. It does not carry race or gender, so it cannot settle
the descriptive coding — but it can verify who served and when, and it is the
basis for the three dates in questions.md. If those dates enter the build it
moves into `data/raw/` and stops being a citation.

**U.S. Census Bureau.** *Population of States and Counties of the United
States: 1790-1990.* Virginia notes, printed p.185.
— Establishes that Alexandria city became independent of the county in 1900 for
census purposes and that the county was renamed Arlington in 1920; and that
county figures reflect boundaries as reported at each census rather than a
constant area. The Virginia pages are excerpted into `data/raw/census/`
because numbers are taken from them; the notes are cited here.

## For a research assistant

Roughly in order of value. The first items are mechanical and need no
judgement, so they are the easiest to hand over.

1. **Verify 2000, 2010 and 2020 totals.** The only unchecked totals left.
2. **Trace the race splits for 1870, 1880 and 1890.** The tables found so far
   cover the county including the city; a county-only split may not exist in
   published form, in which case record how it must be derived.
3. **Establish where the scanned volumes came from** — a citation per file.
4. **Establish what supports the 1889–1986 Board coding.** Start with the
   Historical Society's reply. The judgement-heavy one.
5. **Verify the five Reconstruction-era members** against the 1870 and 1880
   manuscript census, following Hjerpe's method.
6. **Add a `source` column to the roster** and fill it, starting with
   1987–present.
7. **Spot-check gender coding** against obituaries for pre-1950 years.
8. **Turn the roster's note dates into date columns.** `appointed`, `resigned`,
   `died` and `removed` are yes/no flags; the dates sit in free text. This is
   the prerequisite for time-weighting the fractional seats, which is where
   questions.md is headed — nothing can be weighted by service until the
   dates are machine-readable.

Record each source as you go — the point is that every coded cell can be
traced.
