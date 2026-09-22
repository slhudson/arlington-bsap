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
figure currently in `data/transcribed/by_human/`. See questions.md Q8, and Q9 for why the
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
questions.md Q2 matters.

**The categories were never meant to sum.** The census asks race and Hispanic
origin as two separate questions, so a Hispanic resident appears in both a race
count and the Hispanic count. For 1990 the cited source shows this exactly:
white 130,873 + Black 17,940 + American Indian 537 + Asian/PI 11,560 + Other
race 10,026 = 170,936, with Hispanic (23,089) cutting across all five.

The workbook mixes the two systems — non-Hispanic white alongside all-race
Black and Asian totals, with American Indian and Other race dropped. That
accounts for the 1990 overshoot of 381 to the person. See questions.md Q1.

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

| Period | Status |
|---|---|
| 1871–1888 | Five named Black members. Census-linkable: Grace Hjerpe's 2021 paper demonstrates the method using 1880 manuscript census records. Small n, verifiable — not yet verified. |
| 1889–1986 | Coded all-White, resting on the "first since Reconstruction" framing. **Weakest link**, ~490 person-years. |
| 1987–present | Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), plus Tejada. Well documented; the Arlington Historical Society maintains a curated entry. |
| Gender, all years | Naming conventions plus some obituaries. Adequate with a methods note; cheap to spot-check. |

### The one that matters

The 1889–1986 stretch is a negative claim — that no Black member served for
nearly a century — and a negative claim needs evidence that someone looked.
Right now it rests on a phrase, not a review.

Open: whether that record was ever systematically examined, and by whom. Sally
is contacting the Arlington Historical Society
(info@arlingtonhistorical.com), which authored the curated roster and uses the
phrasing.

If nobody has checked, the report should say so plainly rather than repeat the
framing.

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
Q8.

---

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

Record each source as you go — the point is that every coded cell can be
traced.
