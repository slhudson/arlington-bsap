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

Sourcing questions for the descriptive coding live in `SOURCES.md` instead.

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
- `make_residents_by_race_chart_pct.py` rescales both years so the bars total 100%
- `make_residents_by_race_chart.py` plots the counts as reported and notes the
  discrepancy in a comment

Both are defensible; they cannot both appear in the same report. Whatever is
decided belongs in `build/` so every figure inherits it.

Working hypothesis, unconfirmed: Hispanic/Latino is an ethnicity the census
tabulates *across* races, so Hispanic residents are counted twice — once by
race, once as Hispanic. If that is the cause, the overlap is expected rather
than an error, and the honest fix is to stop treating the four categories as a
partition at all.

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

---

## Not blocking the pipeline either

### Q3. What supports "first Black member since Reconstruction"?
**Owner:** archive · **Status:** open — Sally contacting Arlington Historical Society

The 1889–1986 stretch is coded all-White, roughly 490 person-years, resting on
that framing. It is the most load-bearing claim in the report and has not been
independently verified. Detail in `SOURCES.md`.

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

## Settled

### 1890 county population is 4,596
**Settled:** 2026-09-22, from the scanned 1890 volumes in `raw/`. An earlier
working estimate of 4,258 — derived by subtracting a secondary-source city
figure from a combined total — is superseded.

### Figure formatting is not fixed
**Settled:** 2026-09-22 (Sally). The rebuilt figures differ from Alex's
originals by a few pixels, from a newer matplotlib. Formatting is open for
redesign, so visual fidelity to the originals is not a goal and versions are
not pinned. Regression checks target the numbers, not the rendering.
