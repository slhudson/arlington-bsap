# Open questions

Methods and data questions that came up while working the files. One line per
question, newest at the bottom of its section. When a question is answered, the
answer is written in here — not just implemented — so the reasoning survives.

**Owner** is who can actually settle it: *Sally*, *Alex*, *Nick*, *archive*
(needs an outside source), or *RA*.

Questions owned by Alex are batched rather than sent one at a time — Sally
works independently for a few days, then sends a consolidated list. Anything
owned by Alex should therefore be written so it can be read cold, without the
surrounding conversation.

Sourcing questions for the descriptive coding live in `docs/sources.md` instead.

Numbers are the order questions were raised, not their order here, and a
number is never reused: Q10 was folded into Q11 and its number retired. Newer
questions are unnumbered. Nothing in the code refers to a number.

---

## Deferred — settle before the report, not before the pipeline

The near-term deliverable is the working environment itself: repo, build,
Overleaf sync, both authors able to use it. These data questions are real and
must be answered before the report ships, but answering them does not move that
along, so they wait.

### Q1. How should 1970 and 1990 race categories be reconciled?
**Owner:** Alex · **Status:** queued for the next batch to Alex — not blocking

In both years the four race categories sum to more than the reported total —
about 4,800 people in 1970 (2.8%) and 400 in 1990 (0.2%).

The figures currently disagree with each other:
- `residents_by_race_share.py` rescales both years so the bars total 100%
- `residents_by_race.py` plots the counts as reported and notes the
  discrepancy in a comment

Both are defensible; they cannot both appear in the same report. Whatever is
decided belongs in `code/build/` so every figure inherits it.

Working hypothesis, unconfirmed: the Census asks race and Hispanic origin as
two separate questions, so a Hispanic resident also answers the race question
and lands in two categories at once. The bar exceeds the population because
some people are counted in it twice.

If that is the cause, the overlap is expected rather than an error, and the
real question is not "rescale or don't" but whether Hispanic belongs in a
stack with the other three at all, given it answers a different question.
Common alternatives: drop it from the stack and show it as a separate line, or
use the Census's non-Hispanic race categories so the four really are mutually
exclusive.

**In code:** `rescale_to_100()` in `code/build/assumptions.py`, applied by
`code/analysis/residents_by_race_share.py`. `code/analysis/residents_by_race.py` applies
nothing and plots as reported.

**Resolved for 1990, from the source the workbook itself cites.** The Census
working paper at `census.gov/library/working-papers/2005/demo/pop-twps0076/vatab.pdf`
gives Arlington 1990 directly. Its race categories partition the population
exactly — white 130,873 + Black 17,940 + American Indian 537 + Asian/Pacific
Islander 11,560 + Other race 10,026 = 170,936 — and Hispanic (23,089) is a
separate question cutting across all five.

The workbook mixes the two systems. Its white, 118,728, is 12,145 below the
source's 130,873, consistent with non-Hispanic white. But its Black and Asian
figures are the source totals, which include Hispanic Black and Hispanic Asian
residents. American Indian and Other race are absent altogether.

A clean partition needs non-Hispanic Black + American Indian + Asian + Other to
be 29,119. The workbook supplies 29,500. The difference is **381 — exactly the
1990 overshoot**, accounted for to the person.

So rescaling is the wrong correction: it spreads a category-definition problem
across all four bands. The fix is consistent categories, which the cited source
already provides. 1970 is very likely the same, and larger — its overshoot is
4,823, and 1970 was the first census to ask Hispanic origin separately.

Two further consequences. The "Other/multiracial/unreported" band shows near
zero for 1990 when the source has 537 American Indian and 10,026 Other race
residents — they were dropped, not unreported. And the same check has not been
run for any other year, because no source is cited for 1900-1980.

**Origin of the current treatment:** the rescaling was introduced while the
figures were being built, as a working choice, and was noted at the time. It
has not since been ratified by either author. The pgfplots chart in the
Overleaf project carries the rescaled values too, so the decision is currently
embedded in three places.

**For Alex:** where did the 1970 and 1990 race figures come from — decennial
census tables pulled directly, or a secondary source? If directly from the
Census, the double-count explanation above is almost certainly right.

Until he answers, both scripts keep their current behaviour and neither
treatment moves into `code/build/`. Whatever he says, we can live with — the cost of
waiting is low and the change is a few lines.

### Q2. Should not-reported be plotted as zero?
**Owner:** Sally · **Status:** deferred — not blocking the pipeline

Hispanic is blank before 1970 and AAPI before 1950, because the census did not
separately tabulate them. `fillna(0)` in the stacked charts renders that
absence as a zero-height band; the log chart instead starts each line when the
category is first reported.

A zero and an absence are different claims: one says nobody was there, the
other says nobody counted. As drawn, the stacked charts show a flat zero line
for a century, which asserts the first when the record only supports the
second.

Recommendation when this is taken up: follow the log chart, which starts each
line the year the category is first reported, and add a caption note giving
those years.

**In code:** `not_reported_as_zero()` in `code/build/assumptions.py`, applied by
`code/analysis/residents_by_race.py` and `code/analysis/residents_by_race_share.py`.
`code/analysis/residents_by_race_log.py` applies nothing, so its lines begin when
each category is first reported.

---

## Not blocking the pipeline either

### Q3. What supports "first Black member since Reconstruction"?
**Owner:** archive · **Status:** open — held until the internal discrepancies are reconciled with Alex; then the demographics list goes to the Arlington Historical Society as two short tabs (Black members, women) with the default stated

The 1889–1986 stretch is coded all-White, roughly 490 person-years, resting on
that framing. It is the most load-bearing claim in the report and has not been
independently verified. Detail in `docs/sources.md`.

### Q22. What stands behind the workbook's race and gender coding?
**Owner:** Alex · **Status:** drafted for the next batch to Alex — held until the questions we can settle ourselves are settled

Where a published source names a member — Hjerpe's five, Newman, Monroe,
Dorsey, Tejada, Spain, the women in Novack's roster — the repository records
the source and its words. Every other member takes the coding from Alex's
member workbook, which carries no source column: 70 of 119 people, 136 of 217
person-terms for race and 113 for gender. Those rows read `keena-workbook`.

The plan is to carry that forward as an assumption rather than a citation and
to say so in the report: for these members the coding is Alex's reading, and no
published source has been found that speaks to them. What is being asked is a
confirmation, and whether he was working from something — obituaries, news
coverage, Historical Society material — that could be cited instead.

**Keep it separate from the default.** Before 1932, where no source speaks at
all, the build records a white man: 126 person-terms, reading `assumed`. "Alex
read something we cannot see" and "nobody has looked" are different problems,
and only the second is a finding about the historical record. The draft for the
Data Cleaning doc keeps them as two paragraphs for that reason.

### Q23. POP-TWPS0076 has no front matter to find
**Owner:** Claude · **Status:** closed as far as it can go — the entry stays provisional

The other two provisional entries were settled by fetching their volumes' title
pages. This one cannot be. The Bureau publishes the paper at
`working-papers/2005/demo/pop-twps0076/` as one PDF per state and nothing else —
no cover, no abstract, no combined document; checked 23 September 2026, and the
2005 path is the one the workbook itself cites. What is held is `vatab.pdf`,
the Virginia table.

So its title is read from the table header, and its number and date come from
the path and the workbook rather than from the document. The entry says so.
Anyone who finds the paper itself — a library copy, or a Bureau index that
still lists it — can close this by reading its title page.

### Q21. Hjerpe frames the five Black members as an open question
**Owner:** Claude · **Status:** answered — the row is relabelled, 23 Sept 2026

The sentence naming the five — Rowe, Syphax, Pinn, Pendleton, Allen — sits on
the title page of Hjerpe's paper under the heading **"Lingering Inquiries"**,
her own list of things she is asking readers for help with. It reads "census
records which *seemed to indicate*", and the paragraph goes on to say she has
found little on four of the five.

`board_demographics.csv` records the basis for that row as "stated directly",
which is stronger than the source is. The three appendix rows are unaffected —
they rest on the reproduced census images, not on this sentence.

**Answered, and the finding is narrower than it first looked.** No member's
coding depends on that sentence. Pinn, Pendleton and Allen each have their own
row resting on a reproduced 1880 census image; Rowe and Allen have narrative
statements elsewhere in the paper; and Syphax has a second row from O'Leary,
who writes that his photograph shows he was African American. **Syphax is Black
on O'Leary's evidence**, not on this.

The row is kept rather than dropped, with its basis now reading "named in the
author's own list of open questions". The file is one row per claim rather than
one per person, so keeping it is what records that two sources speak to Syphax
— and that sentence is the only place in the data where the five are named as a
*group*, which is what `docs/sources.md` leans on. Deleting it would lose that.

What is still open is the report's wording: whether it describes the five as
identified or as proposed. That belongs with Q3 and Q17.

### Q20. Vollin is two cases, and Pratt gives both citations
**Owner:** Claude · **Status:** answered — both entered, both dated

The Drive folder already held Pratt (1995) under the title "Arlington's
Electoral History", which is O'Leary's subject rather than his. Its footnotes
settle what the handoff listed as an open question:

- **Federal.** *George Vollin, Jr., et al. v. Mills E. Godwin, et al.*, U.S.
  District Court, Eastern District of Virginia, Alexandria Division, Civil
  Action No. 173-74-A. Vollin testified in 1974. Eight plaintiffs, named in
  Pratt's note 16.
- **Virginia Supreme Court.** *Vollin v. Arlington County Electoral Board*,
  216 Va. 674. Pratt's note 3 prints it "Yollin", which is the scan misreading
  a V. **The year is not stated in the article** and should not be inferred
  from the volume number without checking a reporter.

So they are two proceedings, not one, and the report should not merge them.
Both are now in `paper/sources.bib` as `vollin1974` and
`vollinelectoralboard`.

**A trap found while entering them.** biblatex-chicago in notes mode silently
drops `@jurisdiction`, `@legal` and `@legislation`: the document compiles with
no warning and the entry simply is not in the bibliography. It was caught by
compiling the file and reading the output. Cases are therefore entered as
`@misc` with the court, reporter and docket in `note`, which prints. Anyone
adding a case later should compile and look rather than trust the entry type.

**The Virginia case is dated.** *Vollin v. Arlington County Electoral Board*,
216 Va. 674, 222 S.E.2d 793, decided 5 March 1976, Record No. 741174, opinion
by Harrison, J. Reading the opinion also confirms Pratt's account that these
are two different actions: the Virginia case is a petition by more than two
hundred voters under Code § 15.1-694 to put district-versus-at-large election
to a vote, denied because the county had already adopted the County Manager
Plan. The federal suit is the constitutional challenge.

**One loose thread.** The respondent is named Cornelia B. Rose. `rose1964`, the
annexation article, is bylined "C. B. Rose, Jr." The initials fit and both are
Arlington figures of the period, but nothing read so far says they are the same
person, so the bibliography notes the possibility and asserts nothing.

### Q19. Hjerpe's page numbers are the PDF's, not the document's
**Owner:** Claude · **Status:** answered — corrected 23 Sept 2026

Hjerpe's document carries its own page numbers, and they run one behind the
PDF's: the page printed "8" is the ninth sheet. The thirteen locators in
`data/transcribed/by_claude/board_demographics.csv` follow the PDF — Appendix 2
is cited `p.9`, and the page it sits on is printed 8.

Chicago cites the page the document prints, so the locators are each one too
high. Before changing them, confirm against the filed snapshot rather than the
live Google Doc, whose pagination can differ again — which is the reason for
snapshotting in the first place.

**Corrected.** Every locator was checked against the filed snapshot by finding
its quoted sentence, not by assuming a uniform shift — the offset turned out to
be a consistent one. Eleven rows moved. The sentence naming the five Black
members is on the first sheet, which carries no number at all, so it is cited
as `title page`; reading it also raised Q21.

### Q18. Where do the prose-only sources live?
**Owner:** Sally · **Status:** answered — folder, convention and four sources filed

`data/` holds only what we take numbers out of, so a source read to settle a
question is cited and not downloaded. Hjerpe, Rose, Anderson (1958), Pratt
(1995) and Bestebreurtje are that kind, and the plan is a shared Drive folder
rather than `data/raw/` — text-only PDFs would eat the Overleaf budget for
nothing (Q6).

The gap that leaves: every entry in `paper/sources.bib` says where its copy is,
by URL or by a `data/raw/` path, except these. A reader with the citation would
have no way to reach the document.

**Answered.** The folder is `documents/` inside the project's Drive folder, and
a file in it is named author, year, title — `Pratt 1995 - Arlington's At-Large
Electoral System.pdf`. Not the citekey: a citekey is a handle for LaTeX and the
`source` columns, a filename tells a person what they are looking at. The
"Filed in Drive as" line in each `paper/sources.bib` entry ties the two
together, and is where you check that a cited source is filed.

Rose, Hjerpe, Pratt and the ACCF resolution are filed and entered. Anderson and
Bestebreurtje are not — neither is in the folder or the repository.

### Q4. Should the roster be extended back to 1871?
**Owner:** Sally · **Status:** open

The person-level roster starts in 1932; the year-level counts start in 1871. So
the 1871–1931 counts — including the Reconstruction-era Black members, among
the most substantive findings — have no person-level backing. Extending the
roster would let both files derive from one source.

### Q5. Which figures go to the County, and with what caveats?
**Owner:** Sally + Nick · **Status:** open

Five exist. The caveats need to be consistent across whichever ship.

---

### Q7. Should any of the set-aside figures be revived?
**Owner:** Sally + Alex · **Status:** open, low priority

Several earlier figures were produced and not carried forward — a combined
three-panel version with census, Board race and Board gender, in percentage and
raw-count forms, and a broken-axis variant of the residents chart. They are not
in `raw/`. Listed in `docs/figures.md`.

### Q8. Three transcription corrections to confirm
**Owner:** Alex · **Status:** open — already applied in the build

Each is a keying-level difference, not a methods disagreement. Alex used the
right tables and the right principle; his workbook formulas show the working,
and they are what identified each cause.

| # | Cell | Workbook | Sources give | Cause |
|---|---|---|---|---|
| 1 | 1870 white | 1,075 | **1,175** | Jefferson district keyed as 283; it is 383 |
| 2 | 1890 total | 4,596 | **4,258** | Freedman village added as a fourth district |
| 3 | 1890 white | 2,195 | **2,135** | foreign-white-female read as 365; it is 305 |

**1. 1870 white.** The workbook formula is `=517+283+275`. Table III,
*Population of Civil Divisions Less Than Counties*, 1870a-09 printed p.279,
gives Jefferson district's white population as **383**, not 283 — so the slip
is one digit inside the sum. With 383 the total is 1,175, which ties: each
district balances internally (517 + 857 = 1,374, 383 + 873 = 1,256, 275 + 280 =
555), and 1,175 + 2,010 = 3,185. Confirmed by a second route: county white
9,444 minus city white 8,269 also gives 1,175.

**2. 1890 total.** The workbook formula is `=2013+338+1303+942`. Table 5,
1890a_v1-11 printed p.346, prints Freedman village as an indented sub-line of
"Arlington district, *including* Freedman village" — its 338 residents are
already inside that district's 2,013. The three districts alone give 4,258,
which also equals county 18,597 minus city 14,339.

**3. 1890 white.** The workbook formula is `=(5262+5415+379+365)-9226`. In
Table 22, 1890a_v1-14 printed p.520, the foreign-white-female figure is 305,
not 365. The table settles it without re-reading the glyph: native born plus
foreign born is 18,597, the confirmed county total, and only 305 makes white
plus colored tie to that same 18,597. With 365 the row overshoots itself by
exactly 60.

**Also worth telling him:** 1880 came out identical to his in every value, which
is the control case — the method agrees when nothing slips. And the corrected
figures leave no "Other/multiracial/unreported" residents in 1870 or 1890,
where the workbook leaves 100 and 278 unexplained.

### Q12. Where did the 1900-1980 race figures come from?
**Owner:** Alex · **Status:** open — no source traced

Every population total is now traced to a published source. The race and
ethnicity figures are not, for nine censuses.

The workbook shows working for exactly the three years Alex re-derived:
1870, 1880 and 1890 carry formulas. From 1900 on, every race figure is a bare
typed number. The sheet cites two URLs — the 1990 Census working paper and a
2000 Arlington County demographics page — and neither covers 1900-1980. There
are no comments, no notes and no other references, in that workbook or in the
two Board workbooks.

So those figures came from somewhere he did not cite and did not hand over.

**For Alex:** what source did you use for the race and ethnicity counts from
1900 to 1980? If it was a published Census volume, the volume and table would
let us transcribe it directly.

**Already checked, so nobody repeats it:**

- *POP-TWPS0056, Table 61, "Virginia — Race and Hispanic Origin: 1790 to 1990".*
  The sibling of POP-TWPS0076, which the workbook does cite, so a natural
  guess. It is **state-level only** — no counties.
- *Arlington County's own Historical Census Data page*, `arlingtonva.us`.
  Plausible, since the workbook cites an arlingtonva.us URL. It holds **2000
  and later only**.

What remains are the scanned decennial volumes, decade by decade, or a paid
aggregator such as Social Explorer or NHGIS. Several hours either way, which is
why the question is worth asking before the work.

**Still genuinely open, not a correction:**

- ~~Where the scanned volumes came from — a citation per file.~~ **Answered
  23 September 2026.** `code/fetch/census_volumes.py` fetches the Bureau's own
  copy of a held chunk from each volume and compares checksums; both the 1880
  and 1890 files matched byte for byte, so the filenames are confirmed rather
  than assumed, and the script refuses to go on if one ever stops matching. It
  also saves each volume's first chunk, which carries the title page, so the
  bibliography is built from a page in the repository. The 1870 volume already
  carried its own title page.
- Whether those volumes break out race categories beyond White and Black. The
  1890 volumes include a table classifying the colored population as Negro,
  mulatto, quadroon, octoroon, Chinese, Japanese and civilized Indian.

### Q13. What rule sets the size of a fractional seat?
**Owner:** Alex · **Status:** built 2026-09-22 — `board_seats.csv` weights by months served from 1932; the delivered counts remain for 1916–1931

**Decided (Sally, 2026-09-22): a seat-year is months served ÷ 12.** The
roster now records every term from 1932 to the month, so the even split is no
longer needed. Days are not recorded consistently — Novack gives some, the
election dates give others — so the month is the unit, and **the handover
month belongs to the incoming member.** 1916–1931 has no terms and stays on
the delivered seat counts. To be built as `board_seats` computed from
`board_members`, with the delivered counts kept for comparison.

The seat counts carry fractions — 3.5 white and 0.5 Black in 2003 — and the
figure note explains when one appears: "Half seats occur when a Board member
resigned or died before the end of the year and was subsequently replaced."
That says when, not how much.

The evidence suggests the seat is split evenly between its occupants regardless
of timing. Charles Monroe died on 11 January 2003, having served eleven days,
and 2003 is still recorded as half and half.

**Decided (Sally, 2026-09-22):** an even split is a reasonable simplification
for now, and the figures keep it. **Time-weighting is where this should end up**
— a seat counted by the share of the year each person actually served.

**For Alex, narrowly:** confirm that an even split is what the counts do, so the
methods note can say so. A reader will otherwise assume time-weighting.

**What time-weighting would need**, in order:

1. The roster's note dates turned into real date columns — item 8 of the
   research-assistant work order. Nothing can be time-weighted until service
   dates are machine-readable.
2. A rule for members whose dates are unknown or partial.
3. The build to compute seats from the roster rather than read them from the
   counts file, at which point the two Board files collapse into one source.

It moves numbers: Charles Monroe served eleven days of 2003 and currently
counts as half a seat, where time-weighting would give him about a thirtieth.
Small in any one year, and it accumulates across every turnover year in the
series.

**Why it cannot be checked here.** The roster records `appointed`, `resigned`,
`died` and `removed` as yes/no flags, with the actual dates only in free-text
notes — "Removed 9/17/52", "until death on Jan 11". So no fraction can be
verified against service dates without parsing prose. Turning those note dates
into real date columns would make every fraction checkable, and is a contained
piece of work for a research assistant.

**Also worth telling him:** Alfred Frisbie has three rows for 1952 in the
roster. The coding agrees across all three, so nothing is miscoded, but any
tally built from the roster counts him three times.

### Q17. The Reconstruction-era Black member counts disagree
**Owner:** Alex, with Sally · **Status:** open — affects the report's central finding

O'Leary's electoral history names every Board member by district from 1870.
Cross-referencing those names against the five men Hjerpe identifies as Black —
Rowe, Syphax, Pinn, Pendleton, Allen — gives a count per term that matches the
delivered seat counts for 1871-1880 and from 1889, and disagrees in three
places.

| Term | Board as elected | Implied Black members | Delivered counts |
|---|---|---|---|
| 1881-82 | Rowe, Pinn, Costello | **2** | 1, 1 |
| 1883-84 | Squier, Pendleton, Costello | **1** | missing ("." in the source) |
| 1885-86 | Veitch, Johnston, Payne | **0** | 1, 1 |
| 1887-88 | Ball, **Allen**, Grunwell | **1** | 0, 0 |

1885-86 and 1887-88 look transposed, and 1881-82 is one short: William A. Rowe
held Arlington district while Travis B. Pinn held Jefferson, which is two.

**What this rests on, and does not.** O'Leary gives names, not race. The
identification of those five men as Black is Hjerpe's, from 1880 manuscript
census records reproduced in her appendices. So this is a disagreement between
the delivered counts and what Hjerpe's identifications imply — not proof the
counts are wrong. Confirming it needs the census linking checked, which is the
research-assistant task in sources.md.

**Why it matters more than the census corrections.** These are the years the
report's most substantive finding rests on. The delivered data has no
person-level backing before 1932, so until now there was nothing to check the
Reconstruction-era counts against at all.

### Q16. Fetch and transcribe the Arlington election records
**Owner:** Sally (or an RA) · **Status:** done for both documents

Grace Hjerpe's paper cites two primary sources for Board membership that we had
not found, both published by Arlington County:

- *The Electoral History of That Part of Alexandria County Now Known as
  Arlington County, 1870-1920*, Office of Frank O'Leary
- *Candidate History, 1920-Present*, Arlington County Elections

Between them they cover the whole period. This is the primary material the
Board data has been missing entirely, and it needs nobody's permission — it is
published by the County.

What it would settle:

- Who served on the board from 1870 to 1915, which the roster now covers
- Whether the seat counts are right for those years
- The "first since Reconstruction" claim, from candidate records rather than
  from a phrase
- Vacancies, if the records show when seats went unfilled

What it will not settle: race and gender coding, which these records do not
carry.

### Who served from 1916 to 1931?
**Owner:** Alex · **Status:** open

O'Leary's listings stop at the 1915 election and Novack begins with the County
Manager plan in 1932. The county's candidate history starts at 1920 but its
first County Board contest is 1931. The roster has nothing for these years.
Alex's seat counts do cover them, so he had some way of knowing who served;
that source is the question.

### Q15. Vacancies are invisible in the data
**Owner:** Sally + Alex · **Status:** open — affects residents-per-seat

The seat counts always sum to exactly three or five. A seat that sat empty
cannot be represented, so every year looks fully staffed.

At least one year was not. John Milliken resigned in February 1990 and James
Hunter III was elected in a special election in May 1990 to fill the unexpired
term. For roughly three months the Board had four members, and 1990 still
records five filled seats.

**Why it matters beyond bookkeeping.** `residents_per_seat` divides population
by the number of seats — three through 1930, five after. If seats sat empty,
each serving member represented more people than that figure shows, which is
the opposite direction from the story the figure tells.

**It is also an argument for time-weighting.** Under an even split Milliken and
Hunter take half a seat each and the vacancy vanishes. Weighted by service they
account for about ten months between them, and the remaining two months are
genuinely unfilled — 1990 would then total less than five seats, which is what
happened.

**Not yet known:** how many such gaps there are. *Six Decades of Arlington
Leadership* (see sources.md) lists terms of service to the month for every
member through 1994, so the gaps are findable for that period. After 1994 they
are not yet sourced.

### Q14. Three missing service dates
**Owner:** Alex · **Status:** open — small

The roster records the dates of mid-year arrivals and departures in its notes
column, in prose: "Removed 9/17/52", "until death on Jan 11". Twenty-nine of
the thirty-two rows flagged as appointed, resigned, died or removed carry one.
Three do not.

| Year | Person | Note as written |
|---|---|---|
| 1990 | John Milliken | *(flagged resigned, no note)* |
| 1993 | William Newman Jr. | "Appointed as Circuit Court Judge" |
| 1993 | Benjamin Winslow Jr. | "Replaced Newman" |

**Answered from the record**, pending Alex's confirmation. *Six Decades of
Arlington Leadership*, Arlington Historical Magazine 1994, gives:

| Person | Term |
|---|---|
| John G. Milliken | 1981 – Feb 1990 |
| James B. Hunter III | May 1990 – *(special election, Milliken's unexpired term)* |
| William T. Newman Jr. | 1988 – March 1993 |
| Benjamin H. Winslow Jr. | April 1993 – *(special election, Newman's unexpired term)* |

Month precision, not day. Enough to weight a seat by month, which is finer than
the even split in use now.

**For Alex:** does that match your own record, and do you have day-level dates?

Why it is worth asking now: those notes are the only record of when anyone
served part of a year, and they are the prerequisite for time-weighting the
fractional seats — see the fractional-seat question. With these three, the
roster supports weighting every turnover in the series; without them, three
rows need a rule for unknown dates.

**Noted while checking this:** fractions only appear in the seat counts when
the people sharing a seat differ in race or gender. Newman and Winslow are
coded alike, so 1993 shows whole numbers even though the seat changed hands.
The convention is applied consistently; it is just not always visible. Of the
years that do show fractions — 1952, 2003 and 2023 — all have dates.

### Q11. Is "Arlington County" the governed territory or a fixed plot of land?
**Settled:** 2026-09-22 (Sally) — the governed territory. Tell Alex; no decision needed from him.

**Arlington County means the territory the Board governed at each point in
time.** Not a fixed plot of land held constant backwards.

The reasoning: the report assesses the Board's performance. The Board governed
whoever lived inside its boundaries in a given year. When territory moved to
another jurisdiction, the Board genuinely governed fewer people, and the
population series should show that. A time-invariant definition of a plot of
land would answer a different question.

So residents-per-seat measures the right thing as it stands, and the boundary
changes below are context for reading the figures rather than a correction to
make.

### The boundary changes, for the record

| Change | What left Arlington |
|---|---|
| 1900 | Alexandria city reported separately from the county (independent since 1871) |
| 1915 | 866 acres annexed by Alexandria, effective 1 April 1915 — Rosemont, Shuter's Hill, Carlyle, Eisenhower East, the former West End |
| 1930 | A further annexation bounded by Duke Street, Quaker Lane and Four Mile Run — including the Town of Potomac, incorporated in its own right in 1908 |

Sources cited in `docs/sources.md` under Works cited.

The 1915 change falls between the 1910 and 1920 censuses and the 1930 change
around the 1930 census, so part of the movement in those decades is territory
changing hands. Worth a figure note wherever the early 20th century is
discussed.

### The census series matches this definition

The Census county series measures the jurisdiction as constituted at each
census, not a constant area. The document normalises *states* to present-day
boundaries and says so; it makes no such claim for counties, and states that
county figures "refer to the inclusion and boundaries of the county in
decennial census publications." Arlington's own row shows it — 18,597 in 1890
and 6,430 in 1900.

The document also carries a separate table, *Population of Counties Including
Associated Independent Cities*, which exists because the main table does not
hold geography constant. That parallel series is the nearest thing to the
fixed-land definition, and is not what this project uses.

**Still Alex's to see rather than decide:** the definition in `docs/sources.md`
was written here, from the evidence. What exists from him is one sentence in a
chat about the 1870-1890 city problem. Worth him reading it and saying whether
it matches what he intended.

### Q9. How should Freedman village be treated, and described?
**Owner:** Sally + Alex · **Status:** open

Freedman village was a settlement of formerly enslaved people on the Arlington
estate. The census returns it separately in 1890, at 338 residents, and does
not return it separately in 1880 — so its visibility in the published record
changes between the two censuses, independently of who lived there.

Whatever the resolution of Q8, this is substantively relevant to a report about
race and representation in Arlington, and it is currently invisible in the data
and the figures alike. Worth deciding whether it appears in the report at all,
and if so whether as a caption note, a data point, or a marked feature of the
1890 figures.

Treating it only as an arithmetic discrepancy would miss what it is.

### Q6. One repo, or paper/ split into its own repo?
**Settled:** 2026-09-22 (Sally) — one repo, revisit later

Overleaf syncs an entire repository; it cannot be scoped to `paper/` and
`figures/`, contrary to what the handoff assumed. So Overleaf will carry the
census scans too, and the project starts at 67MB against Overleaf's
recommended 100MB ceiling.

One repo was chosen because the case being made to Alex is that this setup is
simpler than emailing files around, and pushing figures across a repo boundary
would undercut that on day one.

**Revisit when** the repo approaches 100MB — `run.sh` warns at 80MB, so this
does not depend on anyone remembering. At that point the options are splitting
`paper/` into its own repo, or downsampling the scans and keeping the
originals in Drive.

Zipping the scans was measured and rejected: they are already-compressed page
images, so zip recovers 1-3% (67MB -> 65MB) while making them unbrowsable on
GitHub and Overleaf and undiffable in git.

### 1890 county population is 4,596
**Settled:** 2026-09-22, from the scanned 1890 volumes in `raw/`. An earlier
working estimate of 4,258 — derived by subtracting a secondary-source city
figure from a combined total — is superseded.

### Figure formatting is not fixed
**Settled:** 2026-09-22 (Sally). The rebuilt figures differ from the
figures as received by a few pixels, from a newer matplotlib. Formatting is open for
redesign, so visual fidelity to the originals is not a goal and versions are
not pinned. Regression checks target the numbers, not the rendering.

### From 1907 O'Leary gives surnames only
**Owner:** Sally · **Status:** open

From the 1907 election O'Leary lists candidates by surname with a vote count -
"Wibirt 99 Hall 35 McShea 24 Robinson 4" - where earlier listings give full
names. The roster keys a person on the full name, so "Corbett" from 1907 is a
different person from "Frederick S. Corbett" before it, and starts again at
term 1. Whether they are the same man is a fact about the sources; joining
them would need a rule (surname plus district plus continuity?) or a note per
case. Two people appear under both forms: Corbett and Duncan.
