# Sources for the descriptive coding

What backs each claim about a Board member's race, ethnicity and gender — and,
just as importantly, what does not yet back it. The roster is person-level, so
sourcing is recorded per person in a `source` column; this file explains the
scheme and tracks what is outstanding.

This is also the work order for a research assistant.

## Status as of 2026-09-22

| Period | Members | What it rests on | Confidence |
|---|---|---|---|
| 1871–1888 | 5 named Black members | Census-linkable. Grace Hjerpe's 2021 paper demonstrates the method using 1880 manuscript census records. | Small n, verifiable — not yet verified |
| 1889–1986 | Coded all-White | The "first since Reconstruction" framing, and nothing else located so far | **Weakest link.** ~490 person-years |
| 1987–present | Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), Tejada | Contemporary news coverage; Arlington Historical Society maintains a curated entry covering all four | Well documented |
| Gender, all years | All | Naming conventions, with obituaries consulted for some earlier years | Adequate with a methods note; cheap to spot-check |

## The one that matters

The 1889–1986 stretch is a negative claim — that no Black member served for
nearly a century — and a negative claim needs evidence that someone looked.
Right now it rests on a phrase, not a review.

Open: whether that record was ever systematically examined, and by whom. Sally
is contacting the Arlington Historical Society (info@arlingtonhistorical.com),
which authored the curated roster and uses the phrasing, to find out.

If the answer is that nobody has checked, the report should say so plainly
rather than repeat the framing.

## Census population, 1870-1890

The county-only population figures for 1870, 1880 and 1890 were established
from original census records, and the scanned volumes in
`raw/2026-09-22-handoff/Historical Census Records/` are those records.

This corrects an earlier reading. The totals first used for those three decades
counted the City of Alexandria alongside the county, which the Board did not
govern. Arlington County was named Alexandria County before 1920, and the
combined figure is what several sources report. The discrepancy surfaced while
building the residents-per-seat figure: the drop from 18,597 in 1890 to 6,430
in 1900 was too large to be real.

The county-only 1890 figure is **4,596**, from the census volumes. A working
estimate of 4,258 was derived by subtracting a secondary-source city figure
from a secondary-source combined total; it is superseded and should not be
cited.

Race breakdowns for those years are in the corrected spreadsheet. They are
incomplete: in 1870 the White and Black counts total 3,085 of 3,185 residents,
and in 1890 4,318 of 4,596. The remainder appears as "Other/multiracial/
unreported". Whether those census tables list further categories is worth
checking against the scans.

## What the census scans actually are

Nine PDFs, 521 pages, in `raw/2026-09-22-handoff/Historical Census Records/`.
They are extracts from the published 1870, 1880 and 1890 census volumes.

| File | Pages | Searchable? |
|---|---|---|
| `1870a-01.pdf` | 6 | no — page images only |
| `1870a-04.pdf` | 36 | no |
| `1870a-09.pdf` | 46 | no |
| `1880_v1-12.pdf` | 72 | yes, poor OCR |
| `1880_v1-13.pdf` | 85 | yes, poor OCR |
| `1890a_v1-11.pdf` | 86 | no |
| `1890a_v1-12.pdf` | 24 | no |
| `1890a_v1-13.pdf` | 93 | no |
| `1890a_v1-14.pdf` | 73 | no |

Seven of the nine have no text layer, so nothing in them can be searched or
quoted without OCR first. That is the single biggest obstacle to documenting
where the early figures came from.

**What is confirmed.** `1880_v1-13.pdf` p.52 is Table VI, *Population, by Race,
of Cities and Towns*, and its Virginia section lists Alexandria **city** in
1880: total 13,659, white 8,279, colored 5,380.

**What is not.** That is the city, not the county. The spreadsheet's 1880
county figures are 3,887 total, 1,693 white, 2,194 black. Which table produced
them — and whether the county figure was printed as county-excluding-city or
derived by subtracting the city from a combined total — is not recorded
anywhere. The same question stands for 1870 and 1890, and those volumes cannot
even be searched yet.

This matters because the city/county distinction is exactly what the earlier
1890 estimate got wrong. Arlington County was Alexandria County before 1920,
and the City of Alexandria, which the Board did not govern, is counted with it
in several published tables.

## What the spreadsheet cites

Two URLs sit in rows below the data in the census workbook:

- `census.gov/library/working-papers/2005/demo/pop-twps0076/vatab.pdf`
- `arlingtonva.us/.../2000-general-demographics.pdf`

Sixteen census years, two citations, and no record of which years each one
covers. The Census working paper is a county population series, so it would
account for totals but not for the race breakdowns.

## Coverage of the race categories

| Years | Categories present |
|---|---|
| 1870–1940 | White, Black |
| 1950–1960 | White, Black, AAPI |
| 1970–2020 | White, Black, AAPI, Hispanic/Latino |

This matches when the Census began tabulating each category separately, so the
gaps are a feature of the source rather than of this dataset — which is the
reason docs/questions.md Q2 matters.

## What backs the Board data

Nothing is recorded, for either file.

`data/board_seats.csv` covers 1871–2026, 156 years of seat counts, with no
source noted. `data/board_members.csv` covers 1932–2026, 497 person-years, with
race and gender coded on every row and no source column. Its `notes` column
holds appointment, resignation and chair information for 276 rows, which is
useful but is not sourcing.

Adding a `source` column to the roster is straightforward — it is already
person-level, so nothing needs restructuring.

## The verification record

`data/manual/census_verification.csv` is the running record: one row per year
per field, with the workbook value, the source value where one has been found,
and the volume, table and page behind it. It is compiled here, not received
from Alex — the three workbooks beside it stay exactly as delivered.

As of 2026-09-22, of 28 rows: 14 confirmed, 1 contradicted, 4 where the source
covers a different geography, 4 unverified, 2 categories the workbook omits, 1
category mismatch, 1 URL not yet opened.

## The fact that organises all of this

**Alexandria city became independent of the county in 1900, and Alexandria
County was renamed Arlington in 1920.**

That single fact explains the shape of the whole dataset. Before 1900, every
published county figure *includes* the city, so a county-only number has to be
derived by subtraction. From 1900 onward the published county figure already is
the county, and needs nothing done to it.

It is why 1870, 1880 and 1890 are the hard years and everything after is
straightforward — and why the one error found so far is in that early stretch.

Source: *Population of States and Counties of the United States: 1790-1990*,
census.gov, Virginia notes, pdf p185.

## Population totals, year by year

| Year | Workbook | Status |
|---|---|---|
| 1870 | 3,185 | consistent — county incl. city is 16,755, implying a city of 13,570 |
| 1880 | 3,887 | **confirmed** — two independent ways |
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

Eleven of sixteen totals are now traced to a published table. The race and
ethnicity figures are far less well established than the totals.

The method throughout: search `data/extracted/census/` to find a table, then
render the page and read it by eye. OCR located every table cited here and
misread digits on the first one checked, which is why it is never the source of
a number.

## For a research assistant

Roughly in order of value. The first two are mechanical and need no judgement,
so they are the easiest to hand over.

1. **OCR the seven image-only PDFs.** Nothing else about the early census can
   be documented until the volumes are searchable. Output searchable PDFs
   alongside the originals — in a new directory, not in `raw/`, which is
   frozen.

2. **Trace each census figure to a table and page.** For all sixteen years,
   record which volume, which table number and title, and which page produced
   the total and each race count. The deliverable is a citation per cell, not
   prose. 1870, 1880 and 1890 matter most, because those are the years where
   the city/county distinction can go wrong.

3. **Settle how the county-only figures were derived** for 1870–1890: printed
   as such, or computed by subtracting the City of Alexandria. If computed,
   record the arithmetic and both inputs.

4. **Establish what supports the 1889–1986 Board coding.** Start with the
   Arlington Historical Society's reply. This is the judgement-heavy one.

5. **Verify the five Reconstruction-era members** against the 1870 and 1880
   manuscript census, following Hjerpe's method.

6. **Add a `source` column to the roster** and fill it, starting with the
   1987–present members, who are well documented.

7. **Spot-check gender coding** against obituaries for the pre-1950 years.

Record each source in the roster's `source` column as you go, rather than in a
separate document — the point is that every coded cell can be traced.
