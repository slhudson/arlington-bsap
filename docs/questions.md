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
decided belongs in `build/` so every figure inherits it.

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

**In code:** `rescale_to_100()` in `build/assumptions.py`, applied by
`analysis/residents_by_race_share.py`. `analysis/residents_by_race.py` applies
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
treatment moves into `build/`. Whatever he says, we can live with — the cost of
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

**In code:** `not_reported_as_zero()` in `build/assumptions.py`, applied by
`analysis/residents_by_race.py` and `analysis/residents_by_race_share.py`.
`analysis/residents_by_race_log.py` applies nothing, so its lines begin when
each category is first reported.

---

## Not blocking the pipeline either

### Q3. What supports "first Black member since Reconstruction"?
**Owner:** archive · **Status:** open — Sally contacting Arlington Historical Society

The 1889–1986 stretch is coded all-White, roughly 490 person-years, resting on
that framing. It is the most load-bearing claim in the report and has not been
independently verified. Detail in `docs/sources.md`.

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
| 1 | 1870 white | 1,075 | **1,175** | the three districts are 517 + 383 + 275 |
| 2 | 1890 total | 4,596 | **4,258** | Freedman village added as a fourth district |
| 3 | 1890 white | 2,195 | **2,135** | foreign-white-female read as 365; it is 305 |

**1. 1870 white.** Table III, *Population of Civil Divisions Less Than
Counties*, 1870a-09 printed p.279, gives Arlington 517, Jefferson 383,
Washington 275 — summing to 1,175. The workbook's own formula for the 1870
total, `=1374+1256+555`, uses the same three district rows. Each district also
ties internally (517 + 857 = 1,374, and so on), and 1,175 + 2,010 = 3,185, the
total. Confirmed by a second route: county white 9,444 minus city white 8,269
also gives 1,175.

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

**Still genuinely open, not a correction:**

- Where the scanned volumes came from — a citation per file. The filenames
  match how the Census Bureau chunks its scans, but that is an inference.
- Whether those volumes break out race categories beyond White and Black. The
  1890 volumes include a table classifying the colored population as Negro,
  mulatto, quadroon, octoroon, Chinese, Japanese and civilized Indian.

### Q11. Is "Arlington County" the governed territory or a fixed plot of land?
**Owner:** Sally + Alex · **Status:** A chosen for now; needs Alex's sign-off

Two possible definitions:

**A. The territory the Board governed at each point in time.** Boundaries move
as the county's boundaries moved.

**B. A fixed plot of land** — the present-day county — held constant backwards.

**A is chosen.** It is what makes residents-per-seat mean anything: a claim
about how many people each Board member represented needs the population the
Board actually governed. It is also the basis on which Alexandria city is
excluded from 1870-1890.

**Two things make this a question rather than a settled decision.**

First, the definition in docs/sources.md is written by Claude from the
evidence, not by Alex. What exists from him is a single sentence in a chat
message, about one case — "the census population data for 1870, 1880 and 1890
erroneously includes the City of Alexandria, which was not governed by the
board." Correct, and correctly applied, but never written down as a definition
or generalised beyond that case. So it needs his sign-off rather than his
confirmation.

Second, A has only been applied to the one boundary change we knew about. The
Census county series does not hold geography constant — 1890 includes the city
and 1900 does not — and the Virginia notes record that annexations from
counties to cities were common. Whether Arlington's boundaries moved again
after 1900 is unresearched. If they did, the population series has silent steps
where territory left, and a flattening could be a boundary change rather than
people moving. That would matter most for residents-per-seat.

Under B the same problem appears differently: the early figures would need
adjusting to today's boundaries instead.

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
