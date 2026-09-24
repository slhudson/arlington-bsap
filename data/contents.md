# Contents of data/

Three layers, sorted by how the numbers were produced. Which folder something
belongs in depends on that, not on what it is about.

Inside `raw/`, folders are named for **who published the material** —
`us_census_bureau`, `arlington_county`, `va_dept_of_elections`, `arlington_historical_magazine` — not for its
subject. Two documents from the same publisher sit together even if they cover
different things. `transcribed/by_claude/` mirrors those folder names.

| Folder | How it was produced | Written by | Read by |
|---|---|---|---|
| `raw/` | published, as it exists in the world | `code/fetch/`, or saved by hand | `code/transcribe/`, `code/build/` |
| `transcribed/by_ocr/` | an OCR engine read the scan | `code/transcribe/` | people |
| `transcribed/by_claude/` | Claude read a rendered page or text layer | `code/transcribe/`, or Claude directly | `code/build/` |
| `clean/` | computed from the layers above | `code/build/` | `code/analysis/` |

A file in `raw/` is its own citation: the volume is the evidence. A file in
`transcribed/` is not — someone or something read a page and typed what it
said, so every row needs a citation back to the page. That difference is the
whole of the sourcing problem, and the write-ups under `docs/` track it.

`transcribed/by_ocr/` is absent from `code/build/paths.py` and `code/analysis/paths.py`
by design. OCR misreads digits, so it is a finding aid: it locates a table and
a page, and never supplies a number.

---

## raw/us_census_bureau/

Extracts from the published 1870, 1880 and 1890 decennial census volumes,
gathered by Alex Keena in September 2026 while correcting the 1870–1890 county
population figures. Received 2026-09-22. Nothing here should ever change; the
checksums are so that a change would be noticed.

**Where they came from is now established.** The filenames match how the Census
Bureau chunks its scanned volumes, and `code/fetch/census_volumes.py` checks
that byte for byte rather than taking the names on trust: it fetches the
Bureau's copy of a held chunk from each volume and compares checksums. Both
matched on 23 September 2026, and the script refuses to go on if one ever does
not. The 1870 volume still rests on its own title page, which its first chunk
happens to carry.

The same script saves each volume's **first chunk**, which holds the title page
and the letter of transmittal. Those are what `paper/sources.bib` is built from,
so a citation rests on a page in the repository rather than on a filename.

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
| `1880_v1-01.pdf` | 9 | yes, poor OCR | `58f0cadb9d44fff9` |
| `1890a_v1-01.pdf` | 7 | no | `0f79bb0363c8e67b` |

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
Virginia table. One of the two URLs cited inside the delivered workbook. Its
Table 47 gives Arlington by race at **every census from 1900**, not only 1990;
the filename is from when only the 1990 line had been read. Transcribed whole
to `transcribed/by_claude/us_census_bureau/censusgov_pop-twps0076_p1_virginia_arlington.csv`,
which is where residents.csv takes 1900-1970 from.

Read carefully: some rows print American Indian and Asian/Pacific Islander as
one merged cell spanning both columns - Arlington's 1940 and the 1970 15
percent sample - and a text-layer extraction drops that value into whichever
column it overlaps. "-" in the table is zero, which the rows that tie without
it prove; "(X)" and "(NA)" are written as empty in the transcription.

**Data files, 2000–2020.** For 2000, 2010 and 2020 the Bureau publishes
machine-readable data, so there is no page to read and no transcription step —
and therefore no reading error to make. `code/fetch/census.py` saves each table
whole: one row per Virginia county, one column per variable, exactly the shape
it is published in. Arlington is a row in it, which also allows a figure to be
checked against neighbouring counties. Each census gets a data dictionary
beside its tables, so the variable codes are readable without the API
documentation.

## raw/arlington_county/

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

## raw/va_dept_of_elections/

**`county_board_2000-2026.csv`** — every County Board contest the Virginia
Department of Elections' historical database holds, saved as the database's
own CSV by `code/fetch/elections.py`: one row per candidate per precinct per
vote channel, primaries included, with the kind of election, the number of
seats and the candidate's party in their own columns. It starts at 2000
because the database does: its Arlington contests before then are federal,
statewide and General Assembly races only. The 2000–2003 County Board rows
carry no party and, from 2002, no votes; party is recorded from 2007. The
roster uses it from 2022, after checking that it and the county's candidate
history name the same 2021 winner; the party coding uses it from 2007 as a
second source, checked against the county's labels.

**`president_1924-2024.csv`** — Arlington's presidential vote, every general
election from 1924, saved by `code/fetch/president.py`. An extract rather than
the file as published, for size alone: the database returns the whole state
for this office, 470,000 rows and 75 MB. The rows kept are the database's
own, unaltered — one per candidate at the locality level, the state's
canvassed total — and carry the database's party name on every row. 1924 is
where the database's Arlington rows for this office begin.

**`registration_2010-2025.csv`** — Arlington's registered voters at each
November election, one row per year, saved by `code/fetch/registration.py`
from the Department's monthly registration statistics: the state's own
locality total (active, inactive and all) from the report dated in the
first days of November, with the report's URL and, where the file states
it, the date the count is as of. A compilation of sixteen locality totals
rather than sixteen whole-state files, for size; the figures are the
files' own. The reports begin in January 2010 and nothing earlier is
online.

## raw/arlington_historical_magazine/

**`novack_six_decades_of_arlington_leadership_1994.pdf`** — Norman S. Novack,
"Six Decades of Arlington Leadership", *Arlington Historical Magazine*, 1994.
A complete roster of County Board members with terms of service to the month,
from the County Manager plan in 1930 through 1994, with the circumstances of
each mid-term departure in parentheses beneath the name. Carries no race or
gender.

## transcribed/by_ocr/

OCR of all 521 census pages, one text file per volume, produced by
`code/transcribe/census.py` using macOS Vision. Not part of `bash run.sh` — it takes
about twelve minutes and its input never changes.

Use it to find a table and a page. Do not read numbers from it: OCR of
19th-century tables misreads digits routinely, and the text layer already
embedded in the 1880 files renders 13,659 as `lB, 659`.

## transcribed/by_claude/

Claude's reading of a page: better than OCR, wrong in different ways, and
confirmed by nobody. Every file cites the page it was read from.

**Census tables** (`us_census_bureau/<year>/`) — one file per printed
table, laid out as the table is laid out rather than reshaped into whatever a
script wanted. Transcribing the whole table means it can be checked against
the page as a whole — a missing row or a misaligned column shows up, where a
list of extracted values hides it. Files are named
`<volume>_p<printed page>_table<n>_<state>_<subject>.csv`, so the filename is
the citation. Each row carries the printed indentation as a `level` column: 0
is the table's own total, 1 its parts, 2 a detail of the line above. Sums take
level 1 only, which is what keeps a sub-line from being added as if it were a
district (the Freedman village case, in `docs/residents.md`). No arithmetic lives in
these files; the subtraction that isolates the Board's territory before 1900
happens in `code/build/residents.py`.

**Machine-readable census years** (`us_census_bureau/1980/` through `2020/`) —
not transcribed, because the Bureau publishes them. 2000, 2010 and 2020 come
from the Census API; 1980 and 1990 from the archived Summary Tape Files, which
the API does not carry. All are one row per Virginia county-level geography,
the same shape for every year, so Arlington is a row and its neighbours are
visible beside it.

Three tables per year: race; race crossed with Hispanic origin (Spanish
origin, in 1980's wording); and, for the voting-age population, race for
those 18 and over from 2000, and the age distribution in 1980 (table 10,
saved as its two halves, everyone and women) and 1990 (P11), whose cells
from "18" on are summed by `code/build/turnout.py`. The cross-tab is the point. Race and Hispanic
origin are separate census questions, so the categories only stop overlapping
once they are crossed — see `docs/residents.md`.

1980 keeps the Bureau's published record layout beside the data
(`data/raw/us_census_bureau/1980/1980_stf1_datadict.txt`). 1990's is published
only as PDF, so `code/fetch/census.py` derives the cell offsets and checks them
on every run against the totals the file itself states.

These are extracts rather than the files as published: the 1990 segments are
172MB and 1980's 30MB, against an Overleaf budget of 100MB for the whole
repository. Size is the only reason.

**`arlington_county/board_1870-1920.csv`** — O'Leary's election listings, one row per
district per election, read from the rotated pages by
`code/transcribe/board_1870_1920.py`. The entry is kept as printed, prose about
replacements included; `code/build/board_roster.py` parses it.

**`arlington_county/president_1872-1920.csv`** — O'Leary's presidential
returns, one line per candidate as printed, read from the rotated pages by
`code/transcribe/president_1872_1920.py` with the same page reader as the
Board listings; `code/build/voters.py` parses them and says which years it
treats as incomplete.

**`arlington_county/candidate_history_1920-present.csv`** — the county's whole candidate
table, every office, read by `code/transcribe/candidate_history.py`, with the kind
of election ("Democratic Primary", "General Election", "Special Election")
carried from the date column onto every row.

**`arlington_historical_magazine/novack_terms_1930-1994.csv`** — Novack's
roster, one row per person, term string and parenthetical notes as printed,
read by `code/transcribe/novack_terms.py`.

**`board_party.csv`** — what a source says about whose candidate a named
Board member was at one election, one row per claim, keyed on the name and
the term's start year: the party, the basis, the citation, and the sentence
in the source's own words. Read only where the county's candidate history
prints `(I)` or no label; the rule is in `docs/board.md`.

**`board_demographics.csv`** — what a source says about a named Board
member's race or gender, one row per claim: the category, the basis, the
citation, and the sentence in the source's own words. It sits above the
publisher folders because it draws on several. A member absent from it takes
Alex's workbook coding from 1932, and is a white man by default before that;
`code/build/board_members.py` writes which of the three applies on every row, and
`docs/board.md` says what stands behind the default in each period. The women are here on Claude's reading of their
given names, and the rows say so. Grace Hjerpe's paper and O'Leary's prose
are cited rather than filed in `raw/`: they are read for a handful of claims,
not transcribed table by table.

## raw/arlington_sun/

**`sun_1938-11-11_p1.pdf`** — the front page of the *Sun* (Arlington) for
11 November 1938, vol. III no. 49, as digitised by the Library of Virginia's
Virginia Chronicle. SHA-256 begins `1e955e238e45baac`.

It carries "Referendum Wins By 61 Votes; Board Will Be 'Staggered'", the
report of the 8 November referendum that put the County Board on staggered
terms, with the returns for all eleven precincts and their totals. It is here
rather than cited in `docs/sources.md` because a number is taken out of it -
the count disagrees with the county's own candidate history, which is
`referendum-1938-margin` in `docs/questions.csv`.

The paper is the *Sun*, not the Alexandria Gazette: Virginia Chronicle has 21
items on this referendum in the Sun across 1938 and none in the Gazette. The
folder is named for the publisher, like the others.

## transcribed/by_human/

**Gone, 24 September 2026.** The folder held three workbooks delivered by Alex
Keena on 2026-09-22 - census figures by year, Board seat counts by race and
gender, and a member database - and for a while they were what several columns
were built from.

Nothing reads them now. Every figure they fed takes a published source or a
stated assumption instead: the census race figures from POP-TWPS0076 and the
crossed census tables, the seat counts from the roster, and the years no
source covers from an assumption written in `code/build/` and labelled
`assumed`. A spreadsheet standing in for an assumption only made the
assumption look like a source.

They are in the git history and on their author's own machine, so deleting
them loses nothing but the implication that the build still depends on them.

## clean/

**Every source column holds a citekey from `paper/sources.bib`**, so a cell in
a table and a footnote in the report name the same entry. `bash run.sh` refuses
to write a file whose source column names an entry that is not there.

Four values are not citekeys, and each says something different about what is
missing. `keena-workbook` - a real claim whose evidence Alex did not record.
`assumed` - no claim existed and the build supplied one. `derived` - computed
from another table in `clean/`, whose rows carry the citations. `unsourced` -
the general case of the first. Every build prints how many of each, so the
numbers are in front of whoever is working; `code/build/citekeys.py` says why they
are kept apart.

Written by `code/build/`, read by `code/analysis/`. Never edited by hand; `bash run.sh`
overwrites it. Committed even though it is generated, so that a change to a
cleaning decision shows up as a reviewable diff — you can see which numbers
moved and by how much.

`residents.csv` — census population by year, with `total_source` and
`race_source` columns naming the document behind each, the Board's seat count
(`at_large`) and the residents-per-seat column the growth figure plots.

From 1980 the four race columns come from the census table that crosses race
with Hispanic origin, so `hisp` is Hispanic of any race and the other three are
non-Hispanic, and nobody is counted twice. 1900–1970 are POP-TWPS0076's
printed counts and 1870–1890 the volumes'. `race_source` says which, year by
year. See `docs/residents.md`.

The `cube_root_p` and `cube_root_resident_ratio` columns are built and no
figure uses them. `residents_per_seat` carried a cube-root-law benchmark and no
longer does; whether any comparison belongs in the report is open, so the
columns stay until that is settled rather than being removed and rebuilt.

`voters.csv` — Arlington's vote by party, one row per election and
`office`: for President every fourth year 1872–2024, and for County Board
every year from 1939 and in 1931 and 1935. Votes for Democratic,
Republican, ABC and other candidates, for candidates given no label, and
the total, with a `complete` flag the figures honour and a source per row —
O'Leary and the county's candidate history where they reach, the state
database after. A Board candidate is counted under the label the county
printed, not the party later attached to the winner in `board_members.csv`.
Voters, not residents: the file is named for what it counts.

`turnout.csv` — who votes for the County Board, one row per year with any
measure, 1872–2025: the year's place in the four-year ballot cycle
(president, governor, midterm, delegates), votes cast in the November Board
contests and the seats they filled, the people that represents (votes per seat), registered
voters from 2010, the population 18 and over at each census from 1980 and
a straight-line estimate between censuses, and the presidential vote. A
`_complete` flag for the four years the county's tallies do not cover, and
a source column per measure. `docs/voters.md`, Turnout.

`board_members.csv` — one row per person per term, 1870 through 2026: name,
term number, district, start and end to the month, source, a note only where
something irregular happened; then race and gender, each with its own source
and note — a cited attribution, "Keena workbook", or "default"; then party,
from 1932, with its source and note — the county's label, the state's record,
or a cited attribution — and `unsourced` where none speaks. Nothing
covers 1916–1931.

`board_seats.csv` — seats held per year by race, by gender and, from 1932,
by party (`dem`, `abc`, `rep`, `ind`, `unrecorded`; empty before), 1870–2026,
in seat-years (months served ÷ 12), computed from `board_members.csv`;
1916–1931 from Alex's seat-count workbook, the only thing that covers those
years. A `source` column says which.
