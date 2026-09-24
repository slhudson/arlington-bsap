# Open questions

What is still undecided, each with an owner: *Sally*, *Alex*, *Nick*,
*archive* (needs an outside source) or *RA*. Written to be read cold, without
the surrounding conversation, because questions for Alex go out in batches.

When a question is settled its answer is written into `docs/methods.md`, in
the section it belongs to, and the entry here is deleted. What is settled is
not kept here; git has the history.

Numbers are the order questions were raised and are never reused. Newer
questions are unnumbered.

---

## Data

### Q3. What supports "first Black member since Reconstruction"?
**Owner:** archive, through County staff

The 1889–1986 stretch of the Board is coded all-White, about 490 person-years,
on the strength of that framing: the obituaries describing Newman (1987) as
the first Black member since Reconstruction. It is the most load-bearing claim
in the report and has not been independently verified. `docs/methods.md`
(Race and gender of Board members) says what stands behind each period.

**The ask** goes to County staff for the meeting next week (Q28), who may pass
it to the Arlington Historical Society: two short lists from
`board_members.csv`, the ten members recorded as other than White and the
twelve women, with the default stated plainly. Every other member has been
treated as a white man; where is that wrong? Two weaknesses to state rather
than let them be discovered: gender is read from names and honorifics for
most of the roster, and the five district-era identifications are Hjerpe's
reading of 1880 manuscript census records, which nobody on our side has
checked.

Related: whether the report describes the five Reconstruction-era members as
identified or as proposed, since Hjerpe lists them under her own open
inquiries. Verifying them against the 1870 and 1880 manuscript census,
following her method, is a task for an RA.

### Q23. POP-TWPS0076 cannot be fully cited
**Owner:** Sally

`censusbureau1990twps76` supplies the race figures for 1900–1970. The Bureau
publishes the paper as one PDF per state with no cover, abstract or combined
document, so its title is read from the table header and its number and date
from the file path. The entry stays provisional, and `code/tests.py` refuses
to pass while a provisional entry is not named here.

**What is needed:** a footnote in the report saying that what is held is the
Virginia table alone and where the title and number come from. Anyone who
finds the paper itself (a library copy, or a Bureau index that still lists it)
can close this by reading its title page.

### Q25. Bestebreurtje, page 215
**Owner:** Sally + Alex

Two claims rest on "Bestebreurtje, p. 215": the 1930 County Board candidacies
of Mary Harris, Edward Morton and C.H. Mosley, and the displacement question
in the race section. The 2017 dissertation and the 2024 book do not share
pagination and neither is in hand, so nobody has checked which document the
page is in or what it says. The dissertation is
`Bestebreurtje_gmu_0883E_11369.pdf` under handle `1920/11125` at George Mason,
whose repository has moved to digitalcollections.gmu.edu. Until someone reads
the page, neither claim goes into prose.

### Q26. Retrocession is dated 1846 or 1847
**Owner:** Sally

Congress passed the retrocession act in July 1846; Virginia formally accepted
in March 1847. Both dates appear in the literature. The report should use one
throughout and say which event it is dating. No figure begins before 1870, so
this is prose consistency only.

### Q27. The 1938 referendum margin: two sources, two counts
**Owner:** Sally

The county's candidate history (`arlingtonelections2021` p.11) gives the
staggered-terms referendum of 8 November 1938 as 1,539 for, 1,487 against. The
*Sun* of 11 November 1938 (`sun1938referendum`) prints returns for all eleven
precincts totalling 1,540 to 1,479, and says of them "These figures are
unofficial". The likeliest reconciliation is that the county's is the
certified canvass and the Sun's the count as known three days out, an
ordinary canvass correction of 8 votes on one side and 1 on the other. It has
not been shown; the *Sun* of 18 November (`sun1938womenvoters`) is about the
ballot's wording, not the tally, and the Electoral Board's own canvass has
not been found.

**Meanwhile:** if the report uses a margin it should use the county's and say
so, and it should not describe the result as carrying by 52 votes without
naming the source.

For the prose, from the same page: the ballot asked only whether members
should be elected "as provided in Sec. 2773-F1 of the Code of Virginia", the
Commonwealth's Attorney's office fielded calls from voters asking what it
meant, and four of eleven precincts voted against.

### The 1902 constitution's Schedule has not been read
**Owner:** Sally or an RA. Small.

The build seats the winners of the November 1903 election on 1 January 1904
under sec. 112, on the reading that the section is the operative rule and a
transitional exception has to be shown. The Schedule, which would say how the
first election under the constitution was treated, is not in the copy held
(`vaconstitution1902`, a hosted PDF that stops at sec. 136); the Library of
Virginia has a scan behind a viewer. It moves one handover by two months in a
stretch where every member is coded a white man, so no figure changes.

### Who served from 1912 to 1931
**Owner:** Sally

No source in hand names anyone for these years, and the seat counts are an
assumption. Two elections are printed in the county's candidate history under
the district headings: November 1923 (Ingram, Duncan, Thornburke) and November
1927 (Duncan, Thornburke). Ingram and Thornburke appear in no other source;
both are marked "(inc.)" in 1923, so they were elected at one of the
unrecorded elections after 1915. The Alexandria Gazette and the Washington
Star are where to look for the rest.

**Open:** whether to enter the 1923 and 1927 names in the roster. Fidelity to
the sources argues for it. The obstacle is that `board_seats` derives its
counts from the roster, so a roster covering 1923 and 1927 but not the years
around them would read the rest as unfilled; the two would have to be
decoupled, with the roster naming who is named and the counts keeping the
assumption, which is already how the 1915 winners are carried.

### Gender rests on names for most of the roster
**Owner:** RA

Gender comes from names and honorifics for every member no source describes,
and the rows in `data/transcribed/by_claude/board_demographics.csv` say so.
A published statement per row, an obituary or a profile, would replace
"inferred by Claude from name" with a citation.

### From 1907 O'Leary gives surnames only
**Owner:** Sally, then an RA to check the name forms

From the 1907 election O'Leary lists candidates by surname with a vote count
("Wibirt 99 Hall 35 McShea 24 Robinson 4") where earlier listings give full
names. The roster keys a person on the full name, so "Corbett" from 1907 is a
different person from "Frederick S. Corbett" before it and starts again at
term 1. Two people appear under both forms, Corbett and Duncan. Joining them
needs a rule (surname plus district plus continuity?) or a note per case.

### Q15. Residents per seat divides by the seats that exist
**Owner:** Sally

`residents_per_seat` divides population by three seats through 1930 and five
after, not by the seats filled. Where a seat sat empty (1873, 1990), each
serving member represented more people than the figure shows. Dividing by the
filled count from `board_seats.csv` would fix it and would make the growth
figure depend on the roster, which it currently does not. A coupling to weigh,
not an oversight.

### Q29. Party: what is still unlabelled
**Owner:** RA for the first four; Sally for the last

The rule and its sources are in `docs/methods.md` (Party of Board members).
What remains:

- **23 terms have no label anywhere**, 1932–1960 almost entirely: the first
  two Boards (1932–39), DeLashmutt 1942–45, Campbell 1943–46, Lloyd 1945–47,
  Chew and Cannon 1948–51, Frisbie 1947–52, Blevins 1957–60, and four
  appointees. Where to look: the Northern Virginia Sun and Arlington Daily on
  Virginia Chronicle, and Franklin Felt's 1961 dissertation on ABC (Michigan
  State, d.lib.msu.edu/etd/39978).
- **`(Convention)`** on Kaul and Krupsaw in 1955: nominated by a convention
  the source does not name. They are `(ABC)` in 1959. Not recorded until
  someone says whose convention.
- **`(IM)`** on Buchholz in 1954 is coded independent. If it is the Arlington
  Independent Movement, the conservative counterpart to ABC, it is a group
  like ABC and may deserve its own note or band.
- **Ricks (1968–71) and Brunner (1984–87)** stay independent on the county's
  label. The Washington Post's 1983 preview reportedly calls Brunner a
  Republican; the archive is paywalled and was not read.
- **Party before 1932**, from the tickets the Alexandria Gazette printed for
  each May election, using O'Leary's dates, which would start the figure in
  1870.
- **The non-Democratic County Board candidates since 2023** carry no party
  in the state file and show as "not recorded" on `voters_board`. Ballots or
  press; a few rows.
- **The ten pieces of reporting** cited for party in `paper/sources.bib` are
  each annotated "not yet filed" and need filing in Drive.

Each finding is a row in `data/transcribed/by_claude/board_party.csv`: the
sentence, the citation.

### Q30. The presidential-vote figure
**Owner:** Sally

- Whether to show the two-party share alone. The "other" band is small except
  in 1912, 1968, 1980 and 1992, and a two-line figure of the Democratic and
  Republican shares, labelled where they run, may read more easily than three
  stacked bands. Not tried.
- Party before 1924 is the nominee's, named in `code/build/voters.py`. It is
  a table in the build rather than a source.
- Whether the 1904 move of local elections to November and the poll tax that
  came with the same constitution belong on the figure. They belong with
  turnout (Q31) rather than party, and are not drawn.

### Q31. Turnout: the denominators
**Owner:** as listed

- **Adults before 1980.** The 1930–1970 censuses printed the county's
  population 21 and over (18 and over from 1970) in the state volumes; none is
  in `data/raw/`. With them the share panel would reach 1931, with a note at
  the 1971 change of age. Owner: RA, from the printed volumes at census.gov.
- **Adults after 2020** are the 2020 count carried forward. The Bureau's
  annual estimates would replace it, at the cost of a second source for one
  column. Owner: Sally.
- **Registration before 2010** exists in the State Board of Elections'
  printed annual reports and nowhere online found. Owner: archive.
- **Ballots cast, not votes per seat.** The two-seat years sit below their
  true voters by up to half. The state's precinct turnout files could supply
  ballots for 2009–2022 if their repeated rows are understood; before that,
  only the Electoral Board's own canvass. Owner: Sally.
- **"Eligible" is not one series.** Citizenship by county exists only in the
  ACS from 2005; before 1966 the poll tax and before 1920 sex decided
  eligibility. Adults is the denominator that can be held constant, with the
  milestones as the caveat.

## The report

### Q5. Which figures go to the County, and with what caveats?
**Owner:** Sally + Nick. Due for next week's meeting.

Eight figures exist: `residents_by_race`, `residents_per_seat`, `board_race`,
`board_gender`, `board_party`, `voters_board`, `voters_president` and
`turnout`. Eight is more than a staff meeting can absorb. The caveats need to
be consistent across whichever ship, and several carry open questions a
caption has to state: the Hispanic series beginning in 1980, the
vote-per-seat denominator in two-seat years, party before 1932.

### Q28. What form does the county-facing package take?
**Owner:** Sally

Settled: it is a package for a meeting with County staff next week, carrying a
progress update (the figures and the timeline) and the asks, which are the
point of the meeting; the demographics verification (Q3) travels in it. Likely
slides rather than a memo, since a staff briefing is presented; the `screen`
profile in `style/style.py` renders every figure at 10 inches wide as PNG for
exactly this. **Still to settle:** slides or memo, which depends on whether
the package is presented or read ahead; and which figures appear (Q5).

### Does the falling Black share read as displacement?
**Owner:** whoever writes the race section

The facts are in `docs/methods.md` (What the Black share shows): the share
falls because everything else grew faster, county totals cannot rule out
displacement, and the 1870 baseline is Freedman village. What is open is how
much the prose says. A sentence reading "the Black share has fallen from 63
per cent" without the second and third points is doing work the number cannot
support.

### Should the report compare Arlington to other localities?
**Owner:** Sally. Not started.

`residents_per_seat` used to plot a cube-root-law benchmark and no longer
does: the law is a stylised fact about national parliaments, and Arlington is
not in that reference class. If a comparison belongs in the report, peer
jurisdictions are the right one. The 2023 Richmond City Charter Review
Commission final report, Appendix D, lists all 38 Virginia independent cities
with approximate 2021 population and council composition, and Appendix E adds
19 southeastern cities of 180,000–300,000; three Virginia localities sit at
Arlington's size (Norfolk 235,000 with 8, Richmond 227,000 with 9, Chesapeake
251,000 with 9, against Arlington's 238,643 with 5). It has no counties, so
Fairfax, Henrico, Chesterfield, Loudoun and Prince William would need keying
by hand. To settle first: which peer class (Arlington is a county that behaves
like a city); that the appendix's counts are not consistently defined and
need reading rather than parsing; and that its populations are rounded and
secondary, so population should come from the Census. If it goes ahead it is a
new figure and a new source under `data/`, not a change to
`residents_per_seat`.

### Q7. Should any of the set-aside figures be revived?
**Owner:** Sally + Alex. Low priority.

A combined three-panel version with census, Board race and Board gender, in
percentage and raw-count forms, and a broken-axis variant of the residents
chart. Listed in `docs/figures.md`; recoverable from git history.
