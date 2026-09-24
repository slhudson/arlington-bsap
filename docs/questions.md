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
**Owner:** Sally · **Status:** answered 23 Sept 2026 — rebuilt from the crossed
census tables for 1980–2020; 1970 and earlier remain

**The answer is consistent categories, not a correction to the old ones.** The
overlap was never an error to rescale away: race and Hispanic origin are two
census questions, so a person answers both and is counted in two of the four
columns at once.

`code/fetch/census.py` now pulls the table where the Bureau reports both answers
crossed together, for every census from 1980, and `code/build/residents.py`
builds five groups that partition the county exactly:

    Hispanic or Latino of any race, and among those who are not Hispanic:
    White, Black, Asian and Pacific Islander, Other or Multiracial

They tie to the person in all five censuses, and the build refuses to write if
they ever stop doing so. The guard earned itself immediately: it caught a
variable mapping that summed to 308,370 against a county of 189,453.

**Two things the crossed tables settled while being read.**

The 1990 arithmetic below is right to the person. Non-Hispanic Black, American
Indian, Asian and Other sum to 29,119 against the workbook's 29,500 — a
difference of 381, which is exactly the 1990 overshoot.

The delivered columns are not all the same kind of number. `white` is
non-Hispanic white in every year from 1980. `black` is the race total including
Hispanic Black in 1980, 1990 and 2000, and non-Hispanic Black from 2010, so that
column changes meaning partway along. That is why the crossed figures replace
them from 1980 rather than sitting beside them: one column, one meaning, with
`race_source` naming which source each year's figures came from.

**1980 is where it starts, and 1970 cannot join it.** Hispanic origin that year
was asked of a 5 percent sample rather than the full count, the Bureau's own
position is that 1970 is not comparable with later years, and it miscoded people
in the southern and central states into "Central or South American". Before 1970
the question does not exist and `white` means white.

**Where the data came from.** The Census API holds no decennial data before
2000. 1980 and 1990 come from the archived Summary Tape Files at
www2.census.gov, which are fixed-width ASCII and need no key. 1980's record
layout is the Bureau's own published dictionary, saved beside the data; 1990's
is published only as PDF, so the cell offsets are derived from the file and
checked on every fetch against the totals the file itself states, for all 136
Virginia county geographies.

**Still open:** 1900–1970, where race has no traced source at all (Q12), and
how the figures should show the join — 1870–1970 on the workbook's categories,
1980–2020 on the census's.

---

*Original entry, kept for the reasoning:*

In both years the four race categories sum to more than the reported total —
about 4,800 people in 1970 (2.8%) and 400 in 1990 (0.2%).

The figures currently disagree with each other:
Both treatments now sit in one figure, `residents_by_race`, as its two panels:
- panel (b), shares, rescales both years so the bars total 100%
- panel (a), counts, plots them as reported, so those bars sit above the total

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

**In code: nothing, now.** `rescale_to_100()` rescaled panel (b)'s shares
wherever they summed past 100 per cent. No year does any more - the last was
1970, and that turned out to be the transposed columns rather than an overlap
(Q12) - so the function had nothing left to act on. It is deleted, with the
assumptions module it lived in and the `sys.path` hook in
`code/analysis/paths.py` that existed to reach it. Both panels now plot as
reported.

An overshoot cannot reach `data/clean/residents.csv` in the first place:
every stretch is guarded where it is built - 1870-1890 in `early_years()`,
1900-1970 in `twps0076()`, 1980-2020 in the partition check on the crossed
groups - so a figure would fail loudly rather than be quietly rescaled.

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
**Owner:** Sally · **Status:** closed 23 Sept 2026 for the figures that exist —
stated in the caption; reopen only if a figure draws these as lines

Hispanic is blank before 1970 and AAPI before 1950, because the Census did not
tabulate them separately. `fillna(0)` renders that absence as a zero-height
band. A zero and an absence are different claims: one says nobody was there,
the other says nobody counted.

**Why it is closed rather than fixed.** The recommendation was to start each
category the year it is first reported, as the log line chart did. That works
for lines and cannot work for stacked bars: a band of height zero and a band
that has not started yet are the same picture. There is no drawing that
distinguishes them, so for these figures it is a caption matter.

**And the quantity is small.** Each group was tiny the first year it was
counted — Asian and Pacific Islander 57 residents in 1950, 0.04 per cent of
the county — and the real
growth comes well after each question appears, Hispanic reaching 23,089 by
1990. Whatever the zeros hide is unlikely to be much.

One clause that belongs with it and is now in the caption: Hispanic residents
before 1970 were not uncounted, they were counted as white. So the step at 1970
is partly the question appearing rather than people arriving. At 0.8 per cent,
barely.

**From 1980 the question does not arise at all.** The `nh_` columns partition
the county and Hispanic or Latino is a reported category, not a blank. What
remains is 1870–1970.

**In code: nothing, and for a while nothing was.** `not_reported_as_zero()`
was never imported by the figure, which called `.fillna(0)` inline instead -
so this entry described a wiring that did not exist. The function is deleted
with `assumptions.py`; the `.fillna(0)` in `residents_by_race.py` is where
the assumption actually lives, and it is stated in the caption.

### The 1902 constitution's Schedule has not been read
**Owner:** Sally (or an RA) · **Status:** open — small; one term's start month

Va. Const. 1902 sec. 112 is what dates the district-era terms from 1904:
county and district officers are elected on the Tuesday after the first Monday
in November and "enter upon the duties of their offices on the first day of
January next succeeding their election", for a term of four years. Applied in
`seated()` in `code/build/board_roster.py`.

**What is not read.** A constitution's Schedule carries the transitional
provisions, including how the first election held under it is treated. The
first November election for Arlington's board was 1903, so the Schedule is
what would say whether those three — Darbey's successors Douglas, Rust and
Febrey — were seated in November 1903 or on 1 January 1904. The build seats
them in January, on the reading that sec. 112 is the operative rule and a
transitional exception has to be shown rather than assumed. Decided by Sally,
24 September 2026.

**Why it is small.** It moves one handover by two months, in a stretch where
every member is coded a white man, so no figure changes. It would matter if
the coding for those years ever became finer.

**Where to read it.** The copy held (`vaconstitution1902`) is a hosted PDF
that stops at sec. 136 and has no Schedule; the Library of Virginia has a scan
at rosetta.virginiamemory.com, behind a viewer. A printed copy would settle it
in a minute.

### Q27. The 1938 referendum margin has no source
**Owner:** Sally + Alex · **Status:** open

The 1938 referendum that introduced staggered terms is recorded as carrying
1,539 to 1,487 - a margin of 52 votes. The referendum itself is named in the
NCL proposal, and the Arlington Historical Society's "County Officials in
Arlington 1870-1960" is cited for the change. Neither is cited for the count.

A vote total is the kind of number a reader assumes came from a record, and a
52-vote margin is exactly the detail a report would lean on. It should either
name the record it came from or come out.

**Where to look:** the county's own canvass returns for 1938, the Historical
Society's officials list if it carries counts as well as names, and the
Alexandria Gazette, which reported Arlington election results at the time.

### Q28. What form does the county-facing version take?
**Owner:** Sally · **Status:** open — the occasion and contents are set
(24 Sept 2026); the form is not

The figures memo is internal: it asks Alex questions and records what changed
and why. A version goes to County Board staff after that, and it is a different
document with a different job - it presents findings rather than soliciting
corrections, and the internal questions do not belong in it at all.

**Settled (Sally, 24 September 2026).** It is a package for a meeting with
County staff **next week**, and it carries two things:

1. **A progress update** — the figures and the timeline.
2. **The asks**, which are the point of the meeting rather than a closing
   section. The demographics verification (Q3) travels here rather than going
   out on its own: the lists are short and land better beside the figures that
   give them context.

**Likely slides rather than a PDF.** A memo is read alone; slides are presented,
which is what a staff briefing is. The repository is already set up for it: the
`screen` profile in `style/style.py` renders every figure at 10 inches wide with
the type scaled up and saved as PNG, which exists for exactly this and has not
been used yet. `figures/png/` is already built on every run.

**Still to settle:** slides or memo, which depends on whether the package is
presented or read ahead; and which figures appear — there are now eight, not
the four this entry was written against, and eight is more than a staff meeting
can absorb. That selection is Q5.

### Q29. What does "party" mean for a Board whose ballot has never carried one?
**Owner:** Sally · **Status:** open — a first coding is built; the rule and its gaps are for review

Party has never been printed on the County Board ballot. The county's own
candidate history says so on its first page: party affiliation "did not
appear on the ballot until 2001, and then only for federal and state offices."
So there is no official record of a member's party, only of whose candidate
they were, and that is what is coded.

**Where the coding comes from.** `board_members.csv` carries `party`,
`party_source` and `party_note` per term, not per person, because a label
changes between elections. Three sources, in order:

1. The county's candidate history, which prints a label in parentheses after
   a name from 1931 — `(D)`, `(R)`, `(ABC)`, `(I)` — though not on every
   winner, and rarely before 1950.
2. The state's elections database, which records party from 2007 and is the
   only source from 2022. Where its general-election row carries no party
   (2023 on), a win in that year's Democratic primary stands in.
3. Reporting, in `data/transcribed/by_claude/board_party.csv`, one quoted and
   cited claim per row, used only where the county prints `(I)` or nothing.
   A cited claim that contradicts a party the county prints stops the build.

**The rule for reporting:** the party or coalition whose candidate the source
says the member was, and a party's open endorsement makes someone its
candidate whatever label they ran under. Settled by Sally on 23 September
2026: an independent openly endorsed by the Republicans is functionally a
Republican, so Dugan in 1946 and Vihstadt in 2014 are coded Republican, with
"ran as an independent" in the note. A source saying only that someone
*leaned* a party's way (Tillema, 1952) is not an endorsement and stays
independent. ABC's endorsement counts as ABC; where a source names both ABC
and a party, the party (Fisher, 1967).

**What it yields, 1932–2026.** 146 terms: 76 Democratic, 18 Republican, 15
ABC, 12 independent, 25 not recorded. The built table reproduces three
compositions reported independently — three Republicans in 1970 and again in
1979, three independents in 1952 — none of which was used to build it.

**Not attempted before 1932.** O'Leary's own summary of the magisterial era is
that "with few exceptions, party affiliation has to be inferred." The
Reconstruction-era Black members were almost certainly Republicans or
Readjusters — the Gazette's "radical Republicans" was applied to Syphax — but
nothing names a party per person, and the Historical Society's officials
list carries none. The figure starts at 1932 with a gap before it.

It is not unrecoverable, only unrecorded in anything held. Local elections of
the period were run on party tickets, and the Alexandria Gazette - O'Leary's
own source, free on the Library of Virginia's Virginia Chronicle - printed
them. An RA with O'Leary's dates could read each May election's coverage and
key a ticket per winner into `board_party.csv`, the same way the 1967-83
terms were filled from reporting; 1916-31, where the roster itself is
missing, would need the Gazette and the Washington Star for names as well.
Election by election, not a dataset, and "inferred" in O'Leary's sense where
the paper names a ticket rather than a person's party. Owner: RA, when one
exists.

**Open:**

- **23 terms have no label anywhere**, 1932–1960 almost entirely: the first
  two Boards (1932–39), DeLashmutt 1942–45, Campbell 1943–46, Lloyd 1945–47,
  Chew and Cannon 1948–51, Frisbie 1947–52, Blevins 1957–60, and four
  appointees. The county's compilation labels parties inconsistently before
  1950. Where to look: the Northern Virginia Sun and Arlington Daily on
  Virginia Chronicle, which McCaffrey's 2026 pieces draw on; and Franklin
  Felt's 1961 dissertation on ABC (Michigan State, 24.7 MB scan at
  d.lib.msu.edu/etd/39978), which should settle every ABC endorsement of the
  1950s.
- **`(Convention)`** on Kaul and Krupsaw in 1955: nominated by a convention the
  source does not name. They are `(ABC)` in 1959. Not recorded until someone
  says whose convention.
- **`(IM)`** on Buchholz in 1954 is coded independent. If it is the Arlington
  Independent Movement, the conservative counterpart to ABC that McCaffrey
  describes, it is a group like ABC and may deserve its own note or band.
- **Ricks (1968–71) and Brunner (1984–87)** stay independent on the county's
  label. The Washington Post's 1983 preview reportedly calls Brunner a
  Republican; the archive is paywalled and was not read.
- **ABC as its own band.** It could be folded into Democratic, as the coalition
  it was. Kept separate because the county itself recorded it and an
  ABC-majority Board from 1957 to 1966 is a finding.
- **The ten reporting sources are web pages** cited from the page held on
  23 September 2026 and not yet filed in Drive.

### Q30. What measures residents' partisanship, and what does it leave out?
**Owner:** Sally · **Status:** open — a first series and figure are built

Virginia has no party registration, so nothing counts residents by party.
The presidential vote is the standard proxy and the one measure that comes as
a dataset, so `voters_by_party` shows Arlington's presidential vote in three
bands every four years from 1872, in the colours of `board_party`, to be read
against it.

**Where it comes from.** 1924–2024 is the state database's locality total
for Arlington, an extract saved by `code/fetch/president.py` (the whole-state
file is 75 MB). 1872–1920 is O'Leary's compilation of the Alexandria
Gazette, transcribed verbatim by `code/transcribe/president_1872_1920.py`.
The county's own candidate history prints the returns from 1920 and is read
as a check; it agrees with the state within five per cent in every year but
1980. The state database itself begins at 1924 for Arlington: its 1789–1923
presidential rows are for other localities or none.

**What it leaves out, by construction.** It counts voters, not residents.
Before 1966 the electorate was the one the 1902 constitution allowed - poll
tax and literacy test - and before 1920 it was men. The comparison the two
figures invite is therefore Board against *the people who were allowed to
vote*, which is the sharp form of the participation question; the at-large
question is its milder form. The axis label and the file name say "voters"
so that no caption has to.

**Three elections are kept but not drawn**: 1896, 1904 and 1908. O'Leary
prints "?" for 1896's Washington district and total, and writes that the
1904 and 1908 returns "appear incomplete"; 1904 sums to 256 votes against
826 in 1900. `voters.csv` carries them with `complete` false.

**Open:**

- Party before 1924 is the nominee's, named in `code/build/voters.py`, since
  O'Leary prints party for 1912 only. Uncontroversial, but it is a table in
  the build rather than a source.
- Whether to show the two-party share alone. The "other" band is small
  except in 1912, 1968, 1980 and 1992, and a two-line figure of the
  Democratic and Republican shares, labelled where they run, may read more
  easily than three stacked bands. Not tried.
- Whether the 1904 move of local elections from May to November, and the
  poll tax that came with the same constitution, belong on the figure. They
  belong with turnout (Q31) rather than with party, and are not drawn.

**The County Board vote, `voters_board`, added the same day.** Sally's point:
the presidential electorate and the November one that chooses the Board are
not the same, so they are two figures, not one. The Board vote counts each
candidate under the label the county printed, not the party later attached
to the winner - so votes for Grotos in 1975 are "other" here while her seat
is Republican in `board_party`. That is deliberate: one figure is the choice
on the ballot, the other who sat. Two seats are elected in every fourth year
from 1951, and a ballot then carries two votes, so shares are of votes cast;
that distorts a party's share only where it ran fewer candidates than seats,
which the county's record shows in 1951 (one independent), 1959 (one
Democrat, one Republican against two ABC) and 2003 (one Republican). From
2023 the state file carries no party on the general at all, so a Democratic
primary winner is Democratic and every other candidate is "not recorded";
Clement, Fierro and Cambridge are in that band, and a source for their
labels would move them. 1942 and 1949 are gaps: a winner with no count.

### Q31. Who votes in County Board elections?
**Owner:** Sally · **Status:** open — a first series and figure are built, from 1931; the denominators are the open part

`data/clean/turnout.csv` and `turnout` (two panels) hold, per year: votes
cast in the November County Board contests and the seats they filled; the
people that represents (votes per seat: exact for one seat, a lower bound
for two or more); registered voters from 2010; the population 18 and over
at each census from 1980, carried between censuses on a straight line; and
the presidential vote every fourth year from 1872, which is voters.csv's.
Each measure has its own source column.

**What the state does and does not have.** The historical database's
`voterStats` flag was tried on 23 September 2026 and changes nothing: the
download endpoint returns the same 10,629 County Board rows with it on or
off, and the site's GraphQL endpoint refuses introspection. Its contest
rows carry `Total Votes Cast`, which is the sum of the candidates' votes,
and `Total Ballots Cast` only for 2025. So the database gives votes, not
voters, and no registration. Registration comes from the Department's
monthly registration statistics, which are online from January 2010 and no
earlier (`code/fetch/registration.py`, one locality total per year from the
report dated in the first days of November). The Department also posts
turnout files by precinct for every election from 2007 at
apps.elections.virginia.gov, but they were not used: 2008's lacks the
central absentee precinct (76,263 ballots against 109,852 presidential
votes), and in several years a precinct's row is repeated once per district
it sits in. Read with care they would give ballots cast per election, which
is the one number this series lacks. The county's own site points to the
state and publishes no turnout history.

**What the county's history gives.** Votes for every November Board contest
1931–2021, complete except 1931 (the page says others ran who are not
listed), 1942 and 1949 (no counts at all) and 1947 (Frisbie has no count
and the totals are from 8 of 11 precincts). Those four are gaps in the
figure. O'Leary reports a count for the district-era Board in two elections
only, 1907 (756 voters across three districts) and 1915 (876); every other
Board election 1870–1911 is "(No returns.)". Both are in the table and not
drawn.

**Seats are counted from the roster, not read off the page.** The county
prints "Vote for 2" on some two-seat contests and nothing on others, so the
build counts the terms in `board_members.csv` that began the following
January, or that November for a same-day special election, appointments and
off-month specials excluded. That makes 1931, 1935 and 1939 five-seat
elections (the whole Board, before terms were staggered), 1943 and 1960
two, 1947 three, 1952 four (three same-day specials beside the regular
seat) and 1997 two. The heading alone would have read every one of those as
a single seat.

**What the figure shows.** The Board's vote is drawn as four series, by
what else the November ballot carried (a `cycle` column: president,
governor, midterm, delegates), because drawn as one line it is a sawtooth
whose teeth are the ballot and not the Board. In a presidential year about
nine in ten of the county's presidential voters also vote for the Board
(0.84–0.98 in every presidential year since 1940 but 1960, 1980 and 1996,
which are multi-seat years and so understated). As a share of the county's
adults, the presidential-year Board vote rose from about a third in 1980 to
57 per cent in 2024; the House of Delegates years, when the Board tops the
ballot, from a fifth to 30 per cent in 2023, and understated because those
are the two-seat years; the midterm and governor's years sat at a third for
decades and have converged on the presidential-year level since 2017
(2018: 51 per cent; 2021 and 2025: 43 and 47). The presidential vote itself
went from about half of adults in the 1980s to two thirds from 2008.
Registration reached 85 per cent of adults in 2020. A snapshot for the
prose: in November 2024, 196,563 adults (the 2020 count), 164,865 active
registered voters, 128,362 who voted for President and 113,209 for the
County Board.

**Milestones**, for the prose and not the figure. 1870, the Board is
created, elected in May by district. 1904, local elections move from May to
November under the 1902 constitution, whose poll tax and literacy test
shrank the electorate until the 1960s (cite the Arlington Historical
Society's "County Officials in Arlington 1870–1960" for the date; not yet
in `paper/sources.bib`). 1920, women vote: O'Leary's presidential returns
go from 804 in 1916 to 1,831 in 1920. 1932, the at-large Board of five,
staggered from 1940 so that the Board is on every November ballot. 1966,
the poll tax falls (Harper v. Virginia Board of Elections). 1971, the vote
at 18. 2020, no-excuse absentee and early voting.

**Open:**

- **Adults before 1980.** The 1930–1970 censuses printed the county's
  population 21 and over (18 and over from 1970) in the state volumes;
  none is in `data/raw/`. With them the share panel would reach 1931, and
  the 1971 change of age would need a note. Owner: RA, from the printed
  volumes at census.gov.
- **Adults after 2020** are the 2020 count carried forward, which overstates
  the 2021–25 shares a little. The Bureau's annual estimates would replace
  it, at the cost of a second source for one column. Owner: Sally.
- **Registration before 2010** exists in the State Board of Elections'
  printed annual reports and nowhere online found. Owner: archive.
- **Ballots cast, not votes per seat.** The two-seat years (every fourth
  year since 1951, the odd year before a presidential one) sit below their
  true voters by up to half. The state's turnout files could supply ballots
  for 2009–2022 if their repeated rows are understood; before that only the
  Electoral Board's own canvass would. Owner: Sally.
- **"Eligible" is not one series.** Citizenship by county exists only in
  the ACS from 2005; before 1966 the poll tax and before 1920 sex decided
  eligibility. Adults is the denominator that can be held constant, with
  the milestones as the caveat.
- **Whether the county-facing version wants the shares panel alone.** Panel
  (a) is the sourced baseline and shows the electorate growing tenfold;
  panel (b) is the question. Q28.

### Q25. Bestebreurtje is cited as two different documents
**Owner:** Sally + Alex · **Status:** open — blocks two claims

`sources.bib` holds `bestebreurtje2024` as the book: *Built by the People
Themselves*, University of South Carolina Press, 7 November 2024, 298 pages. The
figures work cites "Bestebreurtje, *Built by the People Themselves* (GMU
dissertation), p. 215" for the 1930 candidacies of Mary Harris, Edward Morton
and C.H. Mosley.

The book grew out of the dissertation, but they are two documents and do not
share pagination, so p. 215 points at one of them and we do not know which.
Neither is in hand: the bib entry was built from the publisher's catalogue page,
which its own annotation says.

**Two claims rest on this.** The 1930 candidacies, and the displacement question
in the race section — Bestebreurtje is the source named there for whether the
falling Black share reflects neighbourhood clearance that county totals cannot
see.

**To settle:** find which document carries p. 215, add a separate entry for the
dissertation if that is the one, and get hold of whichever is cited. Until then
neither claim should go into prose.

### Q26. Retrocession is dated 1846 or 1847 depending on the source
**Owner:** Sally · **Status:** open — small, but pick one

Congress passed the retrocession act in July 1846; Virginia formally accepted in
March 1847. Both dates appear in the literature and both are defensible. The
figures memo currently says 1847.

The report should use one throughout, and say which event it is dating. Nothing
in `data/` turns on it — no figure begins before 1870 — so this is a prose
consistency question rather than a data one.

### Q24. The Historical Society's roster dates terms a year earlier
**Owner:** Claude · **Status:** answered 23 Sept 2026 — no discrepancy; two
conventions

The Arlington Historical Society's roster gives Newman 1987, Monroe 1999,
Dorsey 2015 and Spain 2024. `board_members.csv` seats all four a year later.
The difference is the convention, not the record: each won the November general
election of the earlier year and took office that January.

| Member | AHS | Built roster | Election |
|---|---|---|---|
| William T. Newman, Jr | 1987 | 1988 | 3 November 1987 |
| Charles P. Monroe | 1999 | 2000 | 2 November 1999 |
| Christian E. Dorsey | 2015 | 2016 | 3 November 2015 |
| Julius D. "JD" Spain, Sr. | 2024 | 2025 | 5 November 2024 |

This is the same distinction settled for Fisher in 1963 and recorded in
`docs/sources.md`: Novack dated his span from the election, the county's
candidate history showed he sat from the following January, and the build reads
a span that way wherever its first year is one the person won the November
election without having stood the year before.

Tejada is the control. He won a *special* election in March 2003 and the roster
seats him in 2003, because a special election seats its winner in the year it is
held. So the offset is not applied blindly to everyone.

**A finding that came out of the check.** Monroe first stood in the April 1999
special election for Eisenberg's unexpired seat and lost to Michael D. Lane by
169 votes, 9,530 to 9,361; he won the two-seat general that November. Hjerpe
argues that the at-large era's members of color all won in cycles where two
seats were up and would have lost in any other. Monroe is the case where that
can be seen directly: the same candidate, the same year, losing the one-seat
contest and winning the two-seat one seven months later. Relevant to Q3 and to
whatever the report says about the at-large system.

### Q3. What supports "first Black member since Reconstruction"?
**Owner:** archive · **Status:** open — the hold is lifted; the route is County
staff, who may pass it to the Arlington Historical Society

The 1889–1986 stretch is coded all-White, roughly 490 person-years, resting on
that framing. It is the most load-bearing claim in the report and has not been
independently verified. Detail in `docs/sources.md`.

**The hold is lifted, 24 September 2026.** This question was held until the
internal discrepancies were reconciled with Alex, so that nothing went out
carrying a contradiction we already knew about. Q8 and Q17 are now answered,
which was the condition.

**The route (Sally, 24 September 2026): County staff, for independent
verification, potentially by the Arlington Historical Society.** Earlier the
plan named the Society directly. Going through staff is the better order — the
County is the study's client, the Society is a volunteer body, and an ask that
arrives from the County carries standing that one arriving from us does not.

**What goes out.** Two short lists from `board_members.csv`, the whole of what
any source says about race and gender:

- **Ten members recorded as other than White**, all from Hjerpe (2021) except
  Spain: Rowe, Syphax, Pinn, Pendleton and Allen in the district era; Newman,
  Monroe, Dorsey and Spain as Black members of the at-large Board, and Tejada
  as its first Latino member.
- **Twelve women**, from Novack (1994) and the county's candidate history:
  Magruder, Cannon, Buchholz, Bozman, Grotos, Whipple, Favola, Hynes, Garvey,
  Cristol, Coffey and Cunningham.

Everyone else — 109 of 119 people — is recorded as a white man because no
source speaks to them, not because one says so. **The ask is the default, not
the lists**: every other member has been treated as a white man; where is that
wrong? The lists are short enough to check by eye, and 1931–1986 is where an
answer would matter most.

**Two weaknesses to state rather than let them be discovered.** Gender is read
from names and honorifics for most of the roster, which is an inference and is
labelled as one in the file. And the five district-era identifications are
Hjerpe's reading of 1880 manuscript census records; nobody on our side has
checked that linking (Q17).

**Q22 does not gate this.** The workbook adds no name to the published
sources, so the lists are the same whatever stands behind its coding.

**Where it goes (Sally, 24 September 2026): inside the county-facing package**
for next week's staff meeting, as one of the asks rather than as a request of
its own. Q28.

### Q22. What stands behind the workbook's race and gender coding?
**Owner:** Alex · **Status:** closed 24 Sept 2026 — not asked, and the
workbooks are out of the build

**Closed without asking him** (Sally, 24 September 2026). The workbook coded
nobody non-White and no woman whom a published source does not already name -
zero cases in 217 terms - so it was a second application of the same default
from the same sources. It added no fact, and recording it as a source of its
own overstated what stood behind 136 race terms and 113 gender terms.

Those terms now fall through to the build's own default and read `assumed`.
No value moved. The three delivered workbooks are no longer read by anything
and have been removed from the repository; `keena-workbook` is gone from
`code/build/citekeys.py` with them.

The verification this question used to gate never depended on the answer:
Alex's list of women and ours are the same list, so the names going to County
staff and the Historical Society are the same either way. That is Q3.

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

**The workbook adds nothing to the published sources, and that is checkable.**
It never codes anyone non-White or a woman where no published source does:
zero cases in 217 terms. Every non-default value in `board_members.csv` traces
to Hjerpe, Novack, the county's candidate history or the state database. So
the coding is consistent with a default - a white man unless a source says
otherwise - which is what Alex says he did for 1916-1931.

**Which means the action this question used to gate does not depend on the
answer** (Sally, 24 September 2026). His list of women and ours are the same
list, so the names going to County staff and the Arlington Historical Society
are the same either way, and so is the ask. That verification is Q3 and it
proceeds.

**What is left is the label.** 136 race terms and 113 gender terms read
`keena-workbook`, which means a claim whose evidence one person can still
name. If the coding is the default, they are not that. Race would read
`assumed`; gender is likelier a reading of names, which the file already
records as a note on the sourced rows rather than as an absence, and should
not collapse into `assumed`. One line in the next mail to Alex settles it:
for the members from 1932 on, was it the same default, and was gender read
off names?

**Keep it separate from the default.** Before 1932, where no source speaks at
all, the build records a white man: 126 person-terms, reading `assumed`. "Alex
read something we cannot see" and "nobody has looked" are different problems,
and only the second is a finding about the historical record. The draft for the
Data Cleaning doc keeps them as two paragraphs for that reason.

### Q23. POP-TWPS0076 has no front matter to find
**Owner:** Sally · **Status:** open — `censusbureau1990twps76` stays provisional, and the report must say so in a footnote

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

**This has to reach the reader.** The 1990 race and Hispanic-origin figures
rest on it, and a bibliography line looks as solid as any other. The report
should carry a footnote saying what is held is the Virginia table alone, and
that the paper's title and number are taken from the table header and the file
path. That is the outstanding item here; `code/tests.py` refuses to pass while
a provisional entry is unlogged, so this question cannot quietly disappear.

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
**Owner:** Sally · **Status:** answered — folder, convention and five sources filed

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

Rose, Hjerpe, Pratt, Anderson and the ACCF resolution are filed and entered.
Bestebreurtje is entered from the author's own site but not in hand, so its
publisher and year are still missing.

### Q4. Should the roster be extended back to 1871?
**Owner:** Sally · **Status:** open

The person-level roster starts in 1932; the year-level counts start in 1871. So
the 1871–1931 counts — including the Reconstruction-era Black members, among
the most substantive findings — have no person-level backing. Extending the
roster would let both files derive from one source.

### Q5. Which figures go to the County, and with what caveats?
**Owner:** Sally + Nick · **Status:** open — now due, for next week's meeting

Eight exist, not the four this entry was written against: `residents_by_race`,
`residents_per_seat`, `board_race`, `board_gender`, `board_party`,
`voters_board`, `voters_president` and `turnout`. The caveats need to be
consistent across whichever ship, and several carry open questions that a
caption has to state — the 1970 categories, the vote-per-seat denominator in
two-seat years, and party before 1932.

---

### Should the report compare Arlington to other localities?
**Owner:** Sally · **Status:** open — not started, and not part of the figure
restructuring

Separate work, logged so it is not mistaken for a change to an existing figure.

`residents_per_seat` used to plot residents per seat against a cube-root-law
benchmark, and no longer does: the law is a stylised fact about national
parliaments rather than guidance, and Arlington is not in that reference class.
If a comparison belongs in the report at all, peer jurisdictions are the right
one — how Arlington's residents per member compares to localities of its size.

**A source already exists for part of it.** The 2023 Richmond City Charter
Review Commission final report, Appendix D, lists all 38 Virginia independent
cities with approximate 2021 population and council composition; Appendix E
adds 19 southeastern cities of 180,000–300,000 with council size and form of
government. Three Virginia localities sit at Arlington's size — Norfolk
235,000 with 8, Richmond 227,000 with 9, Chesapeake 251,000 with 9 — against
Arlington's 238,643 with 5.

What it does not have is counties. Arlington is not mentioned in it, and
neither is any county board of supervisors, so Fairfax, Henrico, Chesterfield,
Loudoun and Prince William would need keying by hand.

Three things to settle before any of it is built:

- **Which peer class.** Arlington is a county that behaves like a city:
  urbanised, at-large elections, a county manager. Richmond and Norfolk may be
  more informative comparisons than rural Virginia counties. That should be
  decided rather than defaulted into.
- **The counts are not consistently defined** in that appendix. Some entries
  read "9 Council members … 1 Mayor elected at large" and others "5 Council
  members … 1 of which serves as Mayor". Each needs reading, not parsing.
- **Population there is rounded to the thousand and secondary.** Take the
  governing-body size from the report and the population from the Census.

If it goes ahead it is a new figure and a new source under `data/`, not a
change to `residents_per_seat`.

### Does the falling Black share read as displacement?
**Owner:** Sally · **Status:** open — for whoever writes the race section

Panel (b) of `residents_by_race` shows the Black share of Arlington falling
from 63 per cent in 1870 to 8.5 per cent in 2020. On its own that invites a
displacement reading, and at county level it would be wrong.

Panel (a) is why the levels are drawn. Black residents went from 2,010 to
20,330, a tenfold increase, while the county went from 3,185 to 238,643,
seventy-five-fold. No census records a substantial fall: the only decreases are
2,645 to 2,507 across the 1910s and a flat stretch from 1990 to 2010. The share
falls because everything else grew faster, not because people left.

**Two things that should be said with it.**

*County totals cannot rule out displacement.* They aggregate over exactly the
geography where it happens. Arlington's Black population was concentrated in a
few neighbourhoods, and a community can be destroyed while the county count
rises. Nothing in `data/` speaks to this. Bestebreurtje is cited under the
prose-only sources in `docs/sources.md` and is where to look.

*The 1870 baseline is a Reconstruction figure.* 63 per cent reflects Freedman
village, the settlement of formerly enslaved people on the Arlington estate,
which is Q9 and still open. It is a moment rather than a stable starting point,
and a sentence that reads "the Black share has fallen from 63 per cent" without
saying so is doing work the number cannot support.

### Q7. Should any of the set-aside figures be revived?
**Owner:** Sally + Alex · **Status:** open, low priority

Several earlier figures were produced and not carried forward — a combined
three-panel version with census, Board race and Board gender, in percentage and
raw-count forms, and a broken-axis variant of the residents chart. They are not
in `raw/`. Listed in `docs/figures.md`.

### Q8. Three transcription corrections
**Owner:** Alex · **Status:** answered 24 Sept 2026 — all three confirmed; the
build had already applied them

Each is a keying-level difference, not a methods disagreement. Alex used the
right tables and the right principle; his workbook formulas show the working,
and they are what identified each cause.

**Confirmed (Alex, 24 September 2026), all three.** He agrees the 1870 white
figure was mis-keyed, that Freedman village should not have been counted as a
fourth district and that this is what produced the 1890 overcount, and that
the 1890 foreign-white-female figure is almost certainly a `0` reading as a
`6` on a low-quality scan.

That last one is worth keeping rather than folding into "keying error". It
makes the cause the scan and not the hand, so any other figure read off the
same 1890 pages carries the same risk, and a digit that ties arithmetically
is better evidence than a second look at the glyph.

Nothing in the build changes: it has used the printed figures since 22
September. What changes is that the three cells now rest on a confirmation
instead of on an open question.

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

### Q12. Where did the 1900-1970 race figures come from?
**Owner:** Alex · **Status:** answered 24 Sept 2026 — POP-TWPS0076, the source
the workbook already cites for 1990; built from it, and no race figure in
residents.csv now comes from the workbook

**Answered (Alex, 24 September 2026).** He named
`census.gov/library/working-papers/2005/demo/pop-twps0076/vatab.pdf`, which is
the document already held as `pop-twps0076_virginia_1990.pdf` and already
cited for 1990. Its Table 47 prints Arlington at **every census from 1900**,
not only 1990, with a footnote saying the county is shown separately from 1900
when Alexandria city was first reported as independent of it. Nobody had read
past the 1990 line.

**What it settles, and two errors it turns up.** Every year 1900-1970 now ties
to its printed total exactly, which the workbook's figures did not.

- **1900 Black is 2,467, not 2,437.** The workbook is thirty short, leaving
  the year at 6,400 against a county of 6,430. A fourth transcription error of
  the same kind as Q8's three.
- **1970's two columns are transposed, and that is the whole of the 1970
  overshoot.** The workbook records Hispanic 1,387 and AAPI 6,315. In the
  source, 1,387 is the Asian/Pacific Islander **full count** and 6,315 is
  Hispanic from the **15 percent sample** - a sample estimate standing in a
  stack of full counts. Corrected, 1970 partitions to the person: white
  161,329 + Black 10,076 + American Indian 271 + Asian/PI 1,387 + other race
  1,221 = 174,284. The 4,823 overshoot this question and Q1 both treated as a
  Hispanic-overlap artifact was never one.

**American Indian and other race were dropped, in every year.** That is why
the figures' "other" band reads near zero before 1980. It no longer does: the
build writes white, Black and AAPI and leaves the rest as the remainder, the
same shape the 1980-2020 groups already use. The remainder is now 1,492 in
1970, 202 in 1960, 95 in 1950.

**Two years do not give everything.**

*1940* prints American Indian and Asian/Pacific Islander as a single merged
cell - 10 people spanning both columns - so neither can be read alone. `aapi`
is empty for 1940 and those ten reach the remainder. Read off the rendered
page rather than the text layer, which places a merged cell in whichever
column it happens to overlap.

*Hispanic origin is (NA) at full count for every year before 1980.* 1970 has
it only as a sample - 6,315 on the 15 percent, 4,890 on the 5 percent.
**Decided (Sally, 24 September 2026): the Hispanic series begins in 1980**,
the first census to ask the question of everyone. The transcription carries
the sample rows so the decision can be revisited against them; the build does
not read them.

**Where it is.** `data/transcribed/by_claude/us_census_bureau/censusgov_pop-twps0076_p1_virginia_arlington.csv`,
every printed row of the Arlington block including the sample lines, with the
merged cell in its own column. The build asserts each full-count row's race
columns account for its printed total before using it.

*Original entry:*

1980 through 2020 are now built from census tables (Q1), so this is the
remaining stretch: seven censuses whose race counts are typed numbers in the
workbook with no source recorded.

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
**Owner:** Alex, with Sally · **Status:** answered 24 Sept 2026 — the
discrepancy is an aggregation error in the delivered counts, not a source
disagreement; Hjerpe's own identifications remain unverified (Q3)

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

**Answered (Alex, 24 September 2026).** His counts are a replication of
Hjerpe, not an independent record: he worked from her report, which cites
O'Leary, and he has not validated either. So the two columns above were never
two sources. They are one source and a transcription of it, and where they
differ the difference was introduced on the way from her names to his
year-level counts. Alex defers to the roster.

Nothing in the build changes. `board_seats.csv` has been computed from
`board_members.csv` for 1870–1915 since the roster was built; the delivered
counts are carried alongside for comparison and are not read. What this
settles is which of the two to believe where they differ, and why.

**What it does not settle, and the distinction matters.** That the five men
were Black still rests entirely on Hjerpe's reading of 1880 manuscript census
records. Agreeing that she is the best source available is not the same as
having checked her. The census linking is still the research-assistant task
in `docs/sources.md`, and the 1889–1986 all-White stretch still rests on the
"first since Reconstruction" framing rather than on evidence — Q3. Closing
this question removes a contradiction inside our own files; it does not add
support to the finding.

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
**Owner:** Alex · **Status:** answered 24 Sept 2026 — nothing stood behind the
counts; five of the names turn out to be in a document already held; and the
stretch is four years longer than it looked

O'Leary's listings stop at the 1915 election and Novack begins with the County
Manager plan in 1932. The county's candidate history starts at 1920 but its
first County Board contest is 1931. The roster has nothing for these years.
Alex's seat counts do cover them, so he had some way of knowing who served;
that source is the question.

**Answered (Alex, 24 September 2026): there was no source.** The counts are an
assumption — three white men — and he says so directly. For race he offers two
supports: the obituaries describing Newman (1987) as the first Black member
since Reconstruction, which implies nobody in this period was; and the county's
demographics, which make any other coding unlikely. For gender he does not
claim the assumption is safe, which is the right call.

**This is what the build already does, and already says.** Those years read
`keena-workbook` in `board_seats.csv`, and the build's standing default for a
member no source speaks to is a white man, recorded as `assumed`. So nothing
moves. What changes is that the workbook is now known to be an assumption
rather than a compilation, which is a different kind of gap — Q22's
distinction between "Alex read something we cannot see" and "nobody has
looked". This is the second.

**The sentence above about the candidate history is wrong, and the correction
matters.** Its first contest *labelled* "County Board" is 1931, but the board
races before that are printed under the district headings, which is why they
were missed. They are already in
`data/transcribed/by_claude/arlington_county/candidate_history_1920-present.csv`:

| Election | District | Candidate | Votes |
|---|---|---|---|
| 6 Nov 1923 | Arlington | W. J. Ingram (inc.) | not printed |
| 6 Nov 1923 | Jefferson | Edward Duncan | not printed |
| 6 Nov 1923 | Washington | E.C. Thornburke (inc.) | not printed |
| 8 Nov 1927 | Jefferson ("Supervisor") | Edward Duncan | 790 |
| 8 Nov 1927 | Washington ("Supervisor") | E.C. Thornburke | 484 |

1923 is a complete Board, all three districts, from a county-published source.
1927 prints two of the three, which is what Alex observed independently.

**Duncan is very likely continuous from the 1890s.** O'Leary has a Duncan
holding Jefferson in 1895, 1897 and 1901 as "William Duncan", in 1907 as
"E. Duncan" and in 1915 as "Duncan" — O'Leary gives surnames only from 1907,
which is its own open question. If they are one man, Jefferson district had the
same member for more than thirty years and the 1916–1931 gap is only two seats
wide, not three.

Ingram and Thornburke appear in no source held. Both are marked "(inc.)" in
1923, so they were already serving — elected at one of the unrecorded elections
after 1915, where O'Leary has Wibirt in Arlington and Walker in Washington. The
Alexandria Gazette and the Washington Star are where to look, the same errand
as the pre-1932 party coding.

**Gender for these five still rests on names**, which is the roster's weakest
attribution everywhere and is labelled as such. Duncan is named in full in the
1923 listing; Ingram and Thornburke are initials.

**The stretch is 1912-1931, not 1916-1931** (Sally, 24 September 2026). O'Leary
does not list the November 1911 election, so the men elected in 1907 have a
term that closes in January 1912 and nobody is named after them. The roster
used to run them through to the next listed election in 1915; it no longer
does. The seat counts for 1912-1915 now come from the workbook, like the years
after them. No value changes - both give three white men - but four more years
are now marked as an assumption rather than a record.

**Still open: whether to put the 1923 and 1927 names in the roster.** The
principle is fidelity to what the sources say, which argues for entering them:
five names the county published, sitting only in the transcription. The
obstacle is that `board_seats` derives its counts from the roster, and a
roster covering 1923 and 1927 but not the years around them would read the
rest as unfilled seats. The two files can be decoupled - the roster names who
is named, the counts keep taking 1912-1931 from the workbook - which is
already how the 1915 winners are carried, named in the roster and holding no
seat-years. Owner: Sally.

### Q15. Vacancies in the seat counts
**Owner:** Sally + Alex · **Status:** partly answered 23 Sept 2026 — vacancies
are now representable and two are recorded; how many others exist is open, and
`residents_per_seat` still divides by seats that exist

**What has changed.** This entry used to read "the seat counts always sum to
exactly three or five" and "1990 still records five filled seats". Neither has
been true since seat-years were time-weighted (Q13). `board_seats.csv` now
records 1873 at two and a half seats — Washington district vacant from June to
November — and 1990 at four and five sixths, after John Milliken resigned in
February and James Hunter III was elected in a May special election. Both show
on the board figures, and the build asserts that those are the only two years
falling short.

1870 is deliberately not among them. The Board came into existence at the May
1870 election, so that year is measured against the eight months the Board
existed rather than the calendar year — see `docs/sources.md`. Measured against
twelve it read two seats, and a chart of that says the Board grew from two
seats to three, which it did not.

**What is still open, and it is the substance of the question.**

*How many other gaps there are.* Two are recorded because two are sourced. The
figure is only as complete as the roster's dates. *Six Decades of Arlington
Leadership* lists terms of service to the month for every member through 1994,
so gaps in that period are findable; after 1994 they are not yet sourced. Until
that sweep is done, "two vacancies since 1870" is a statement about the roster,
not about the Board.

*`residents_per_seat` divides by the seats that exist, not the seats filled.*
`residents.csv` carries `board_seats` as three through 1930 and five after, and
the figure divides population by that. Where a seat sat empty, each serving
member represented more people than the figure shows — the opposite direction
from the story it tells. Dividing by the filled count from `board_seats.csv`
instead would fix it, and would make the growth figure depend on the roster,
which it currently does not. That is a real coupling to weigh, not an
oversight to correct quietly.

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

### 1890 county population is 4,258
**Settled:** 2026-09-22 at 4,596, from the scanned 1890 volumes in `raw/`;
**corrected to 4,258** on re-reading the table, and confirmed by Alex on
24 September 2026.

The entry is kept because the number moved twice and the reasons differ. A
first working estimate of 4,258 came from subtracting a secondary-source city
figure from a combined total, which was superseded by reading the volumes. The
volumes then gave 4,596 only by counting Freedman village as a fourth
district: Table 5 prints it as an indented sub-line of "Arlington district,
*including* Freedman village", so its 338 residents are already inside that
district's 2,013. The three districts alone give 4,258, which is also county
18,597 minus city 14,339.

So the figure returned to its first value on different and better evidence.
`code/tests.py` reintroduces the double count and asserts the build refuses.
See Q8.

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
