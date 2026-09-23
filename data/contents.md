# Contents of data/

Four layers, sorted by how the numbers were produced. Which folder something
belongs in depends on that, not on what it is about.

Inside `raw/`, folders are named for **who published the material** —
`census`, `county`, `virginia`, `arlington_historical_magazine` — not for its
subject. Two documents from the same publisher sit together even if they cover
different things. `transcribed/by_claude/` mirrors those folder names.

| Folder | How it was produced | Written by | Read by |
|---|---|---|---|
| `raw/` | published, as it exists in the world | `fetch/`, or saved by hand | `transcribe/`, `build/` |
| `transcribed/by_ocr/` | an OCR engine read the scan | `transcribe/` | people |
| `transcribed/by_claude/` | Claude read a rendered page or text layer | `transcribe/`, or Claude directly | `build/` |
| `transcribed/by_human/` | keyed in by a person | — | `build/` |
| `clean/` | computed from the layers above | `build/` | `analysis/` |

A file in `raw/` is its own citation: the volume is the evidence. A file in
`transcribed/` is not — someone or something read a page and typed what it
said, so every row needs a citation back to the page. That difference is the
whole of the sourcing problem, and `docs/sources.md` tracks it.

`transcribed/by_ocr/` is absent from `build/files.py` and `analysis/files.py`
by design. OCR misreads digits, so it is a finding aid: it locates a table and
a page, and never supplies a number.

---

## raw/census/

Extracts from the published 1870, 1880 and 1890 decennial census volumes,
gathered by Alex Keena in September 2026 while correcting the 1870–1890 county
population figures. Received 2026-09-22. Nothing here should ever change; the
checksums are so that a change would be noticed.

Where exactly they came from is not recorded. The filenames match how the
Census Bureau chunks its scanned volumes, but that is an inference — see
`docs/questions.md`.

| File | Pages | Text layer | SHA-256 (first 16) |
|---|---|---|---|
| `1870a-01.pdf` | 6 | no | `207a404c63c65609` |
| `1870a-04.pdf` | 36 | no | `0dc7a2a508ffe416` |
| `1870a-09.pdf` | 46 | no | `63f3d4eaac112736` |
| `1880_v1-12.pdf` | 72 | yes, poor OCR | `acc0b1ab4dd6ee88` |
| `1880_v1-13.pdf` | 85 | yes, poor OCR | `6e859908a8bd2a5d` |
| `1890a_v1-11.pdf` | 86 | no | `47903c2e2ec9ed46` |
| `1890a_v1-12.pdf` | 24 | no | `782da690cdf3ca40` |
| `1890a_v1-13.pdf` | 93 | no | `fb1d9e704366cbf4` |
| `1890a_v1-14.pdf` | 73 | no | `42c36586ed15d9f0` |

Seven of the nine have no text layer at all.

**Two published documents** alongside the scans, fetched from census.gov in
September 2026. They are excerpts, like the volume scans beside them.

**`population_of_states_and_counties_1790-1990_virginia.pdf`** — the title
page plus the Virginia pages of *Population of States and Counties of the
United States: 1790-1990*. Printed page 177 carries Arlington County for every
census from 1890 to 1990; page 185 carries the Virginia notes that state
Alexandria city became independent of the county in 1900 and that the county
was renamed Arlington in 1920. The full 236-page document is 14.2 MB, which
would have taken the repository past the 80 MB warning for 229 pages nobody
needs.

**`pop-twps0076_virginia_1990.pdf`** — Census working paper POP-TWPS0076,
Virginia table, giving Arlington's 1990 population by race and Hispanic origin.
One of the two URLs cited inside the delivered workbook.

**Data files, 2000–2020.** For 2000, 2010 and 2020 the Bureau publishes
machine-readable data, so there is no page to read and no transcription step —
and therefore no reading error to make. `fetch/census.py` saves each table
whole: one row per Virginia county, one column per variable, exactly the shape
it is published in. Arlington is a row in it, which also allows a figure to be
checked against neighbouring counties. Each census gets a data dictionary
beside its tables, so the variable codes are readable without the API
documentation.

## raw/county/

Two election documents from Arlington County's voting and elections site. The
folder is named for where they were published, not for who wrote them —
**neither is a primary record, and both say so.**

**`electoral_history_1870-1920.pdf`** — 28 pages, *The Electoral History of
That Part of Alexandria County Now Known as Arlington County, 1870-1920*,
written by **Frank O'Leary**, Arlington County Treasurer. Marked "Version 2".
An essay in the first person, compiling election returns from the Alexandria
Gazette and other newspapers, with commentary. O'Leary describes its limits
himself: record-keeping before the 20th century was "ragged and incomplete",
elections "were not always held (or at least not reported) when it seems that
they should have occurred", and "with few exceptions, party affiliation has to
be inferred".

Pages 9 onward carry election listings, rotated 90° on the page, giving year,
date, office, district, candidate and votes — including who replaced whom
mid-term. That is the material behind the roster before 1916.

O'Leary also notes that race was recorded inconsistently: the label "(colored)"
appears in some Gazette returns but not others, and he believes a majority of
early office holders were African-American without being able to evidence it.

**`candidate_history_1920-present.pdf`** — 122 pages, published by the
**Arlington County Office of Voter Registration and Elections**, last updated
18 November 2021. A table of year, election date, office, candidate and votes
received, 1920 to the 2021 election. Its own preamble states it was compiled
from Electoral Board records *and historical news sources*, that early vote
tallies are incomplete, and that the Board "welcomes any known additions or
corrections". The county has since taken it down; its results page now points
to the state.

**What both are and are not.** They record elections, not service: who ran and
how many votes they received, not who held a seat in a given year. Appointments
and resignations appear only where a compiler noted them in passing. Neither
carries race or gender. The genuinely primary material sits behind them —
newspaper returns and Electoral Board minutes — and has not been consulted.

## raw/virginia/

**`county_board_2021-2026.csv`** — every County Board contest from 2021 on,
from the Virginia Department of Elections' historical database, saved as the
database's own CSV by `fetch/elections.py`: one row per candidate per precinct
per vote channel, primaries included, with the kind of election and the number
of seats in their own columns. It starts at 2021 so that one election overlaps
the county's candidate history, and the build checks that the two agree there.

## raw/arlington_historical_magazine/

**`novack_six_decades_of_arlington_leadership_1994.pdf`** — Norman S. Novack,
"Six Decades of Arlington Leadership", *Arlington Historical Magazine*, 1994.
A complete roster of County Board members with terms of service to the month,
from the County Manager plan in 1930 through 1994, with the circumstances of
each mid-term departure in parentheses beneath the name. Carries no race or
gender.

## transcribed/by_ocr/

OCR of all 521 census pages, one text file per volume, produced by
`transcribe/census.py` using macOS Vision. Not part of `bash run.sh` — it takes
about twelve minutes and its input never changes.

Use it to find a table and a page. Do not read numbers from it: OCR of
19th-century tables misreads digits routinely, and the text layer already
embedded in the 1880 files renders 13,659 as `lB, 659`.

## transcribed/by_claude/

Claude's reading of a page: better than OCR, wrong in different ways, and
confirmed by nobody. Every file cites the page it was read from.

**Census tables** (`1870/`, `1880/`, `1890/`, `1990/`) — one file per printed
table, laid out as the table is laid out rather than reshaped into whatever a
script wanted. Transcribing the whole table means it can be checked against
the page as a whole — a missing row or a misaligned column shows up, where a
list of extracted values hides it. Files are named
`<volume>_p<printed page>_table<n>_<state>_<subject>.csv`, so the filename is
the citation. Each row carries the printed indentation as a `level` column: 0
is the table's own total, 1 its parts, 2 a detail of the line above. Sums take
level 1 only, which is what keeps a sub-line from being added as if it were a
district (the Freedman village case, in `docs/sources.md`). No arithmetic lives in
these files; the subtraction that isolates the Board's territory before 1900
happens in `build/residents.py`.

**`county/board_1870-1920.csv`** — O'Leary's election listings, one row per
district per election, read from the rotated pages by
`transcribe/board_1870_1920.py`. The entry is kept as printed, prose about
replacements included; `build/board_roster.py` parses it.

**`county/candidate_history_1920-present.csv`** — the county's whole candidate
table, every office, read by `transcribe/candidate_history.py`, with the kind
of election ("Democratic Primary", "General Election", "Special Election")
carried from the date column onto every row.

**`arlington_historical_magazine/novack_terms_1930-1994.csv`** — Novack's
roster, one row per person, term string and parenthetical notes as printed,
read by `transcribe/novack_terms.py`.

**`board_demographics.csv`** — what a source says about a named Board
member's race or gender, one row per claim: the category, the basis, the
citation, and the sentence in the source's own words. A member absent from
this file is a white man by default; `build/board_demographics.py` writes
that default out for every person, and `docs/sources.md` says what stands
behind it in each period. The women are here on Claude's reading of their
given names, and the rows say so. Grace Hjerpe's paper and O'Leary's prose
are cited rather than filed in `raw/`: they are read for a handful of claims,
not transcribed table by table.

## transcribed/by_human/

**The three workbooks are under glass.** They are exactly as Alex Keena
delivered them on 2026-09-22 and are never edited here. A discrepancy is
recorded, not corrected.

`census_verification.csv` is the exception: it is compiled in this repository
rather than received, and holds the running record of which workbook figures
have been traced to a source table. See `docs/sources.md`.

**`arlington county demographic data.xlsx`** — 16 census years, 1870–2020:
population totals, race and ethnicity counts, Board seats, and derived
residents-per-seat and cube-root columns. Two source URLs sit in rows below the
data, with no record of which years each covers. The 1870–1890 rows were
corrected in September 2026, after the original figures were found to include
the City of Alexandria, which the Board did not govern.

**`arlington board - descriptive representation (1870-2026).xlsx`** — 156 years
of Board seat counts by race/ethnicity and gender, 1871–2026. No sources
recorded. The header `aapi_m embers` contains a space, corrected in
`build/board_seats.py` rather than here.

**`arlington county board member database (1932-2026).xlsx`** — 497
person-years, 1932–2026, one row per member per year, race and gender coded on
every row. No source column.

| File | SHA-256 (first 16) |
|---|---|
| `arlington board - descriptive representation (1870-2026).xlsx` | `b5de85deed3414fc` |
| `arlington county board member database (1932-2026).xlsx` | `66b511fddac149df` |
| `arlington county demographic data.xlsx` | `fcf4d9bdb4779ae1` |

These are what the project is grounding, not building on. The roster and
demographics in `clean/` are built from the sources above without reading
them; `docs/sources.md` records where the two agree and where they do not.

## clean/

Written by `build/`, read by `analysis/`. Never edited by hand; `bash run.sh`
overwrites it. Committed even though it is generated, so that a change to a
cleaning decision shows up as a reviewable diff — you can see which numbers
moved and by how much.

`residents.csv` — census population by year, with a `source` column naming
the document behind each row, the Board's seat count (`at_large`) and the
residents-per-seat and cube-root columns the figures plot.

`board_roster.csv` — one row per person per term, 1870 through 2026:
name, term number, district, start and end to the month, source, and a note
only where something irregular happened. Nothing covers 1916–1931.

`board_demographics.csv` — one row per person in the roster: race and gender,
each with its own basis and source, "default" where no source said anything.

`board_seats.csv` · `board_members.csv` — Alex's two Board workbooks, read as
delivered. `board_members` is his person-year roster; `board_roster` above is
the one built here from sources. They are compared, never merged.
