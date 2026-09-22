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

### Q8. How were the 1870-1890 county census figures obtained?
**Owner:** Alex · **Status:** open — for the next batch

The scanned volumes in `raw/` are the primary sources for the county-only
population figures, but nothing records which table in which volume produced
which number, or how the county was separated from the City of Alexandria.
That separation is what the superseded 4,258 estimate for 1890 got wrong, so
it is worth pinning down.

Four questions, in rough order of value:

1. **Where did the volumes come from?** The filenames (`1880_v1-12`,
   `1890a_v1-11`) look like the Census Bureau's own scans of its published
   decennial volumes, but that is a guess from the naming. A URL or a citation
   per file would settle it.

2. **Which table and page gives the county-only figure for each of 1870, 1880
   and 1890?** Volume, table number, page.

3. **Was the county figure printed as such, or computed?** "Data for
   Alexandria County without Alexandria City" could mean either a table that
   reports the county separately, or subtracting the city from a combined
   total. If computed, the arithmetic and both inputs are worth recording.

4. **Do those volumes list race categories beyond White and Black?** In 1870
   the White and Black counts total 3,085 of 3,185 residents, and in 1890
   4,318 of 4,596. The remainder currently renders as
   "Other/multiracial/unreported". If the tables break it out — the 1890
   volumes have a table classifying the colored population as Negro, mulatto,
   quadroon, octoroon, Chinese, Japanese and civilized Indian — those counts
   could be recorded instead.

*Not blocking.* `data/census_ocr/` now makes all nine volumes searchable, so
questions 2 and 3 can be narrowed without Alex if it is quicker to look than
to ask. Whatever is found should still be confirmed with him, since he read
these tables himself.

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
