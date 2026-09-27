# The Board

Who held each seat and when, and who they were: what each number in
`data/clean/members.csv` and `data/clean/members_by_year.csv` is, what backs
it, what is assumed where nothing does, and why. Present tense; how a decision
was reached is in the git history. The placeholders in the `source` columns
are explained in `code/citekeys.py`, and what is still open is in
`docs/questions.csv`.

## What rests on an assumption

- 1889–1986 is coded all-White on the "first since Reconstruction" framing,
  and the five Reconstruction-era members rest on Hjerpe's census linking
  (`default-1931-1986`).
- Gender rests on the default (man) for four members: R. Henry Phillips,
  Robinson and Willson, seated before 1912; and W. P. Ames, whose 1940
  record is matched on the name alone and feeds nothing. W. M. Febrey and
  Edward Duncan left this list once joined to their census-sourced terms
  (`febrey-one-member-or-two`, `duncan-one-member-or-three`, 27 September
  2026); H. Dwight Smith, Crocker and Schutt left it on a press honorific the
  day the Alexandria Gazette was searched for all seven (27 September 2026,
  below); Wibirt and Walker left it the same day, joined to a 1920 census
  record each by the full name that same Gazette search gave them (below);
  and Phillips joined it when the record read against him proved to be his
  father's. The other 115 have a census listing or a pronoun or honorific in
  the press.
  `gender_evidence` in `members.csv` says which (`gender-from-names`).
- For the 40 members first seated 1932–1966 and the 38 first seated
  1870–1904, race and gender come from 74 census records covering 67 of the
  78, each index reading checked against the sheet where the row could be
  found on it; the match to the member rests on the name, the district he sat
  for or Arlington, and, where the record gives one, an occupation, a
  household or a street. Ten of those 78 were found in no census: Casto,
  H. L. Brown Jr, Fisher, Lowry and T. W. Richards of the later era, and
  H. Dwight Smith, Crocker, Schutt, Robinson and Willson of the earlier. One
  more, R. Henry Phillips, was found and then withdrawn: the household read
  against his row is his father's, not his (below).
- Birth years, for 88 of 119 members, rest on the census listings' ages and
  on an age stated in an obituary or a profile, each right to within a
  year, and the age figure draws a year only when all but at most
  one sitting member has one. The figure is not in the paper yet, and it
  starts in 1932.
- 1912–1931 named five terms and no more before 27 September 2026. Read
  through that day for `arlhist1967officials`, the Historical Society's own
  compilation from the Board's minute books, the stretch is now named almost
  completely: all three magisterial seats, Arlington, Jefferson and
  Washington, for all twenty years, with one seven-week vacancy in the
  Washington seat in early 1920 that the source itself states rather than
  leaves silent (below, "The roster now names nearly all of 1912 to 1931").
  `members_by_year.py` still states 1912–1931 itself from the standing
  assumption of three seats held by white men and does not read the roster
  for those years by design, so the figure does not yet reflect any of this;
  whether it should is the open decision (`roster-1912-1931`,
  `docs/questions.csv`).
- From 1907 O'Leary's surnames are not joined to earlier full names
  (`surnames-from-1907`).
- 23 terms from 1932 carry no party, three labels are unresolved, and no
  party is attempted before 1932 (`party-unlabelled`, `party-before-1932`).
- Each place carries a precision, from the place's own words by rules in
  `code/clean/members_residence.py`: a house number with a street is an address;
  a street with no number, a street; a neighborhood, civic association or
  named community, a neighborhood; and "North Arlington" or the northernmost
  section, a side; and one of the three magisterial districts of Alexandria
  County, Arlington, Jefferson or Washington, as the 1880–1910 census sheets
  head each page, a district. A place no rule reads stops the build. A house
  number whose street is unread (Ames) counts as a neighborhood.
- Before 1932 the only places are the census sheets' own: 33 of the 41
  members seated 1870–1911 have a record, and for 28 of them the sheet gives
  a magisterial district and nothing finer, since the street column is blank
  outside the towns; Cherrydale, Washington Avenue, Old Glebe Road and
  Saegmuller's Maryland Avenue house in Washington City are the exceptions.
  One of the 33 is a weak match, Roach, flagged in his row. Eight have no
  record in the 1870–1920 indexes under any spelling tried, R. Henry
  Phillips among them since the record once matched to him is his father's
  (`residence-pre-1932`).
- Before 1932 a member seated for a magisterial district has no claim from
  the office, and 1912–1931, where no roster exists, the figure counts no
  seats. Both once rested on the assumption that a supervisor lived in the
  district he represented; no instrument required that before 1903, so the
  assumption was the project's rather than the law's and the 49 derived rows
  are gone. See "Residence in the district" below.
- Where members lived is transcribed but not yet coded, and the 1973 Post map
  that places a whole Board at once has not been seen (`mathews1973-map`);
  two of the 37 members first seated 1932–1962 have none
  (`residence-1932-1962`), 10 of the 25 seated 1964–1999 have none
  (`residence-1964-1999`), two rows postdate the member's service
  (`residence-after-service`), and for Thomas two sources name different
  places (`thomas-residence`). Tillema's and Massey's two sources also
  differ, but which each source says is settled; see "Reading an image".

Each is a row in `docs/questions.csv`, with whose court it waits in and what would settle it.

---
## Local legal authority

The two Dillon's Rule opinions the paper's local legal authority section
cites, `commonwealthvarlington1977` and `arlingtonvwhite2000`, are both held,
read from CourtListener and filed in Drive under `legal/`.

### Residence in the district

A supervisor is required to live in the district he represents only from
1903, by sec. 32 of the 1902 constitution. Nothing before that requires it.

The 1869 constitution creates the office without a residence qualification.
Art. VII sec. 2, under the running head "Townships", provides that "In each
township there shall be elected annually: one Supervisor", and that "The
Supervisors of each township shall constitute the Board of Supervisors for
that county" (`vaconstitution1869`). Where the same constitution does speak
to who may hold office, it points the other way: Art. III, headed "Elective
Franchise and Qualifications for Office", makes the residence a voter needs
twelve months in the state and three months in "the county, city or town in
which he shall offer to vote" (sec. 1), and then provides that "all persons
entitled to vote shall be eligible to any office within the gift of the
people, except as restricted in this Constitution" (sec. 2). Eligibility
follows the vote, the vote is seated in the county, and the exceptions are
reserved to the constitution itself.

The statutes keep the office as the constitution left it. Ch. 76 of the acts
of 1874-5, approved 5 February 1875, declares the townships as they stood on
3 November 1874 to be "the magisterial districts into which the counties are
directed to be distracted" [sic], carrying over their boundaries, names and
voting places; it renames the unit and says nothing about the officer.
Ch. 158 sec. 4, approved 8 March 1875, provides that "In each magisterial
district of the commonwealth there shall be chosen by the qualified voters of
the same, respectively... one supervisor, one constable, three justices, and
one overseer of the poor" (`vaacts1875`). The Code of 1887 carries this
forward in ch. 9 sec. 96 in the same terms (`vacode1887`). In each the
district names the electorate, not a qualification on the candidate.

The Code of 1873 settles it by contrast, because it states a district
residence requirement for other offices in the same breath and not for this
one. Ch. 6 sec. 9 provides that "In each township of the commonwealth there
shall be chosen by the qualified voters of the townships respectively...
one supervisor, one assessor, one township clerk, one collector, one
commissioner of roads, and one Overseer of the poor". Sec. 10, the next
section on the same page, elects "one overseer of roads, who shall be a
resident of the road district". Ch. 33 sec. 2 provides that "Each assessor
and commissioner shall reside in the township, city or town for which he was
elected, and his removal therefrom shall vacate his office"
(`vacode1873`). In 1546 pages the phrase "resident of the township" occurs
once, of the registrar, and "reside in the township" once, of the assessor.
Neither reaches the supervisor. The Code of 1887 is the same: "resident of
the district" does not occur in it at all, and the one office tied to
residence in a district is the road surveyor, whom sec. 963 requires to be
"a resident and voter thereof" (`vacode1887`).

Nothing local supplies what the general law omits. The office is created by
the constitution and filled under general law, qualifications for it are
reserved to the constitution by Art. III sec. 2, and a Virginia county in
this period holds only the powers the General Assembly grants it
(`commonwealthvarlington1977`), so the instrument that could carry a local
rule is a special act for Alexandria County rather than an order of the
Board. The 1869-70 and 1874-5 session volumes carry no such act; the
remaining sessions to 1902 have not been searched one by one.

No statute required it, but the Board observed it. The minute books, as the
Arlington Historical Society read them in 1967 (`arlhist1967officials`),
record two supervisors leaving their seats on moving out of their district:
Francis G. Schutt in June 1877, on a notation that "he had moved from
Arlington District", and William A. Rowe on 2 April 1879, "moved from
Jefferson to Arlington District". Rowe stood for Arlington District that
July and won it, the same office in his new district. The practice is in the
primary record three times in eleven years, Tibbett Allen's being the third,
and it is a custom rather than a qualification: nothing made a supervisor
ineligible, and the men resigned.

Allen's departure differs in how it was enforced. The Alexandria Gazette of
3 September 1888 reports that "A rule was issued against Tibbett Allen to
show cause why he should not be removed as supervisor of roads Jefferson
District on account of non-residence", in the same sitting of the county
court that removed every previously appointed policeman except Robert
Walker; on 3 October it reports that "Judge Chichester yesterday, before the
adjournment of the County Court, appointed Mr. Frank Hume supervisor of
Jefferson district, in place of Tibbett Allen, resigned"
(`alexandriagazette1888rule`, `alexandriagazette1888hume`). Allen was the
last Black member of the Board until Newman was seated in 1988. Schutt and Rowe went on their own
and no process issued against either.

Three things the record does not support, each of which it would be easy to
assume. The office named in the rule is not certain: "supervisor of roads"
is the Gazette's phrase, and the Code of 1887 ties district residence to the
road surveyor (sec. 963) and not to the Board seat (ch. 9 sec. 96), while
the seat is what fell vacant. Freedman's Village cannot be the cause: the
1890 census puts it inside Arlington district, not Allen's Jefferson
(`census1890`), so the clearing that began in December 1887 was emptying a
settlement in another district. And Frank Hume is not simply the instrument
of a purge: by 1890 he was running for Congress as an independent Democrat
and the Washington Bee endorsed him, writing that "he should receive the
undivided colored vote because he is the colored man's friend"
(`washingtonbee1890hume`) - two years later, and no evidence about 1888.

Where Allen lived is unknown, and no account of why the rule issued has been
found. The episode reached no newspaper that took his side: the Washington
Bee carries nothing on it in any issue from August to December 1888, the
Richmond Planet has one digitized issue in all of 1888 and it is silent, the
People's Advocate had ceased publishing by 1884, and the National
Republican's digitized run ends in May 1888. What would settle it is the
Alexandria County court order book for 1888, which would carry the rule and
its disposition, and the Board's own minute books; neither is online
(`allen-1888`).

---

## The roster

`data/clean/members.csv` holds one row per person per term: name, term
number, district, when service began and ended (to the month), the months the
term held (`held_from` and `held_to`, counted from year 0, the end exclusive),
how the term began, and a source per row. 222 terms, 1870 through 2026, from three sources
in sequence: O'Leary's electoral history to 1915, Novack's roster from 1932 to
1994, and election results after that, the county's candidate history to 2021
and the state's elections database from 2022. Nothing covers 1912–1931 except
the two elections named below.

A term is the natural unit: person-years fall out of it, while a term starting
in May or ending in February cannot be recovered from a list of years. A
vacant seat is not a row, since nobody served. `term_number` counts within a
person, so someone appointed to a vacancy who then won twice has three rows
numbered 1, 2, 3; William A. Rowe has eight, including his move from Jefferson
district to Arlington at term 7.

`seated_by` says how each term began: election, special election,
appointment, or unrecorded where O'Leary writes only that someone was
replaced. Three builds select terms by it, so it is a column rather than
something read out of the note.

**The constitution created the Board; the acts of 1870 stood it up.** The
constitution framed in 1868 and ratified in 1869 divides every county into not
fewer than three townships, has one supervisor elected annually in each, and
provides that "The Supervisors of each township shall constitute the Board of
Supervisors for that county" (art. VII sec. 2, `vaconstitution1869`). The
mechanism is the constitution itself, not an enabling act; prose should say so
rather than "under the post-Civil War constitution". Three acts of the 1869–70
session then made it exist in fact: ch. 39, approved 2 April 1870, has the
governor appoint five commissioners in each county to lay it off into
townships; ch. 76 sec. 14, approved 11 May 1870, has one supervisor chosen in
each township at the May general election; and ch. 188 sec. 2, approved 11
July 1870, repeats the constitutional sentence and gives the board a corporate
name it can sue and be sued by (`vaacts1870`). That order is why the roster
starts at the May 1870 election and not at ratification.

**Townships became magisterial districts in 1875, without a change of unit.**
The amendment to art. VII respecting county organization, agreed to 31
March 1873 and ratified by the people 3 November 1874, struck the section
dividing counties into townships and inserted one dividing them into
magisterial districts instead, each electing one supervisor, three
justices, one constable and one overseer of the poor (`vaacts1873amendment`,
ch. 301 of the 1872–73 session). Ch. 76 of the 1874–75 session, approved 5
February 1875, then declares the townships as they stood on the date of
ratification to be the magisterial districts the amendment directs, keeping
their boundaries, names and voting places; ch. 69, approved 2 February
1875, makes "township" in any earlier statute read as those districts
(`vaacts1875`). The conversion renames units Alexandria County already had,
which is why the roster shows no seat-count change at that point.

**Before 1870 the county court governed, and its justices were elected by
district from 1852.** The 1851 constitution puts a County Court in each
county, "held monthly, by not less than three nor more than five Justices",
with the jurisdiction of the existing county courts, and lays each county off
into districts in which the voters elect four Justices of the Peace for four
years (art. VI secs. 25–27, `vaconstitution1851`). The administrative work is
that court's: the Code of Virginia in force through the period has the county
levy laid by the court of the county, made up annually in May or June "when a
majority of the acting justices of the county is present" (ch. 53 secs. 1 and
3), and the court held "by the justices of the county or corporation, or any
four or more of them" (ch. 157 sec. 1, `vacode1860`). So the 1870 Board is the
county's first elected governing body of this kind, and the elected element
before it reached only the justices who composed the court. Both sources apply
by their terms to every county and name none, so this is Alexandria County's
arrangement by generality, not from a document about this county; nothing held
says the county was treated as an exception.

**The Board's name changed with its form.** Members elected by magisterial
district were supervisors: the county's own returns print "Supervisor Jefferson
District" for the election of 8 November 1927 (arlingtonelections2021 p.4), and
Corbett's 1910 census occupation is "Supervisor, County". Arlington adopted the
County Manager Plan by referendum in 1930 and has operated under it since 1932;
samuel2026 note 8 records that the Plan "appears to be the only county form of
government that does not refer to its Board members as 'supervisors'". The
name, the at-large method and the five seats therefore arrive together, and
prose should not carry one back across 1932 without the others.

**When a term begins depends on the constitution in force.** Under the
magisterial system elections were held in May and the board took office then,
so those terms run May to May. The 1902 constitution moved county and district
elections to November and seated their winners on 1 January following (sec.
112, `vaconstitution1902`), so from the November 1903 election a term runs
January to January; the County Manager plan seats members on 1 January too,
so the convention is unbroken from 1904 on. The Schedule of the 1902
constitution governs the first election held under it, and confirms this: its
sec. 10 holds the first election of county and district officers "under this
Constitution" on the Tuesday after the first Monday in November 1903, terms
"to begin on the first day of January, next after their election" - the same
rule sec. 112 states for every later election. Sec. 10's second paragraph
names "supervisors of the several counties" among the offices whose sitting
holders are continued only "until January the first, nineteen hundred and
four", so the incoming November 1903 winners are seated then and not before.
The November 1903 handover therefore falls in January 1904 like every other,
in a stretch where every member is coded a white man.

The same convention is why the Arlington Historical Society's roster dates
Newman 1987, Monroe 1999, Dorsey 2015 and Spain 2024 where this one seats them
a year later: each won the November general election of the earlier year and
took office that January. Tejada is the control. He won a special election in
March 2003 and is seated in 2003, because a special election seats its winner
when it is held.

**A term ends when the term ends, not when the listings resume.** Sec. 112
makes it four years, so a November win closes four years on. O'Leary lists the
board in 1907 and in 1915 and not in 1911; reading the 1907 winners through to
1915 would put three named men in a seat for eight years on a source that
speaks to four. Their terms close in January 1912, and nothing names who held
those seats next. The note on such a row says the end is the statute's; where
the next listed election seats a successor on the same date the departure is
sourced and carries no note.

**"So the roster names almost nobody from 1912 to 1931," until 27 September
2026.** Until that day, no source in hand recorded who served, and the seat
counts for those years were an assumption, stated in
`code/clean/members_by_year.py` and labelled `assumed`: three seats, filled,
held by white men. Two elections inside the stretch were printed in the
county's candidate history under the district headings rather than under
"County Board": November 1923 (Ingram in Arlington, Duncan in Jefferson,
Thornburke in Washington, each the only name listed) and November 1927
(Duncan and Thornburke, each with the highest vote). They are keyed in
`data/transcribed/by_claude/members_terms.csv`, page 2 and page 4, as five
terms seated the following January, with no end recorded: the county gives
neither a start nor an end, so the January start was the build's rule for a
November winner and each term held to the end of its first year (1924 and
1928). Jefferson's "Duncan" is Edward Duncan, resolved
(`duncan-one-member-or-three`, 27 September 2026): not the William Duncan who
held Jefferson from 1895, but the same man as the roster's earlier "E. Duncan"
(1908–12) and "Duncan" (1916–20), one continuous term from 1908 to 1932
(below).

**The roster now names nearly all of 1912 to 1931 (27 September 2026).**
`arlhist1967officials`, the Historical Society's "County Officials in
Arlington, 1870-1960," gives Board membership by magisterial district, term
by term, compiled from the Board's own minute books; it was read for four
individual questions on 26 September 2026 (below) and read through for this
stretch the next day. It covers 1908 through 1931 without a gap, in the
overlapping term-blocks the source itself prints, keyed in
`data/transcribed/by_claude/arlington_historical_magazine/arlhist_terms_1912-1931.csv`.
Of the sixty seat-years the three districts hold across those twenty years,
every one is now named by this source or by `members_terms.csv` above, save a
single vacancy: the Washington seat sat empty from 1 January to 20 February
1920, after Clarence R. Ahalt, elected to it, moved from the district before
the term began — the source states the vacancy rather than falling silent
about it, so it is recorded as one, not left as an unknown. Arlington runs W.
C. Wibirt (1912–19, joining the term already keyed above), Thomas J.
DeLashmutt (1920–23), W. J. Ingram (1924–27, closing the open end above) and
B. M. Hedrick (1928–31); Washington runs Robert L. Walker (1912 to his
resignation 27 March 1919), Clarence R. Ahalt (appointed to the rest of
1919), the seven-week vacancy, Frank Upman and W. T. Weaver (both appointed,
in quick succession, to the balance of the 1920–23 term) and E. C.
Turnburke — printed that way in the article, "Thornburke" in
`arlingtonelections2021` and in Novack, so read as the same misprint the
county's own records do not repeat — for 1924–27 and 1928–31, closing the
open end above; Jefferson is Edward Duncan throughout, as already sourced.
The article gives no race for any of them, so a member drawn from this
listing defaults to White and man like the rest of the era
(`default-1931-1986`, above) rather than being looked into on its own: the
all-White coding of 1889–1986 is a separate question waiting on the County,
and this reading does not reopen it.

`members_by_year.py` has not been changed to read either file: it still
states 1912–1931 itself, by design, so the seat table and the figure built
from it show the same three assumed seats they showed before this reading.
Whether it should now change, and how a year that is part sourced and part
assumed would be represented for the seven weeks in 1920, is the decision
that follows from this count, tracked as `roster-1912-1931` in
`docs/questions.csv`.

**Mid-term handovers are terms like any other.** O'Leary records them as
prose beside the elected member ("Replaced by H. Dwight Smith in Dec.;
replaced by Lott W. Crocker in March 1873, replaced by Francis D. Schutt in
April"), and those are parsed into their own rows: the Arlington seat in
1872–73 is four terms. Where a month is given without a year, the year carries
from the previous handover and rolls forward when the month goes backwards.
Francis D. Schutt holds two consecutive terms in 1873, appointed in April and
elected in May; that is two terms, not a duplicate. From 1907 O'Leary gives
surnames only, so "Corbett" from 1907 is a different person in the roster from
"Frederick S. Corbett" before it and starts again at term 1. Two people appear
under both forms, Corbett and Duncan; joining them needs a rule (surname plus
district plus continuity) or a note per case.

**Novack's spans are split at elections.** He lists a person once with their
whole service compressed into a string ("1932-1947" for Elizabeth Magruder),
so a span is cut at each November election the person contested, using the
county's candidate history, and the months come from his parentheticals. He
sometimes dates a span from the election rather than from taking office
(Fisher "1963-1974" won in November 1963 and sat from January 1964), so a span
whose first year is one the person won without having stood the year before
begins the following January. A cut at an election the person stood in and
lost continues however the span began: Frisbie, appointed in November 1947,
stood that month and did not win, and his 1948 term is still the appointment.
A member appointed to a vacancy who then wins the seat at a same-day special
election is seated by it that November and the appointment ends then: Wilt,
appointed in January 1960, won the special for Krupsaw's unexpired term that
November, which Novack's note does not record and the county's does. Where an
appointment is dated and no departure accounts for it, the one member whose
span ends that year undated left in the month of the appointment; more than
one candidate stops the build.

**From 1995 a term is built from election results.** A November win starts a
four-year term the following January. A special election fills the rest of a
term that ended early: the member who left is closed at that month, the winner
serves until the seat's next regular election, and where two members' terms
end in the same year the county's own annotation ("to fill Eisenberg's
unexpired term") says whose seat it was; the build refuses to guess when it is
absent. The five people still serving when Novack published have their last
term closed the same way. A check runs every month from 1995 through 2026:
five members at large, six only in a month a special election changed hands.
The county and state sources both hold the 2021 election, and the build
insists they name the same winner there before using the second.

**Recorded vacancies.** Found by counting the months each term covers against
the seats that existed: the Washington district seat from the May 1873
election until Samuel Titus was appointed that December, March and April 1990
between Milliken's resignation and Hunter's special election, and the
Washington seat again from 1 January to 20 February 1920 (above). 1912–1931
is otherwise not swept this way, since `members_by_year.py` does not read the
roster for those years (above).

## Seat-years

`data/clean/members_by_year.csv` is one row per year, 1870 through 2026: seats
held by each race, each gender and (from 1932) each party, in seat-years, so
a member who sat for four months of a year counts 4/12. It is computed from
`members.csv` for every year but 1912–1931, which are the assumption
above whatever the roster holds for them. Days are not recorded consistently, Novack giving some and the election
dates others, so the month is the unit, and **the handover month belongs to
the incoming member** (Sally, 22 September 2026). An end no source records
holds to the end of the term's first year. Both rules are applied once, in
`held_from` and `held_to` on `members.csv`; the seat-years and the
figures of who was sitting on 1 July read those columns rather than the dates.

The denominator is the months the Board existed that year, which is twelve for
every year but its first. Arlington's Board came into existence at the May
1870 election, so 1870 is scaled by the eight months it existed: it reads
three seats filled, because they were, for as long as there was a Board to
fill them. Divided by twelve it would read two, and a chart of that says the
Board grew from two seats to three, which it did not.

The seats held can never exceed the seats that exist (three magisterial
districts with one supervisor each from 1870; five members elected countywide
from the County Manager plan, adopted at the November 1931 referendum and
seated in January 1932), and fall short only in 1873 and 1990; anything else
stops the build. Race, gender and party are independent splits of the same
seats and must account for the same total in every year, which
`code/tests.py` checks by taking a term out of one split and asserting the
build refuses.

The Board's race coding is one code per person, so it is already a set of
categories that do not overlap. A member coded Hispanic carries no separate
race, so `white` here means white and not Hispanic, which is what the census
basis means from 1980; the two files line up and the figures drawn from them
can be read against each other.

`residents_per_seat` divides population by the seats that exist, not the
seats filled. Where a seat sat empty, each serving member represented more
people than the figure shows. Whether to divide by the filled count instead,
which would make the growth figure depend on the roster, is open.

## Where members lived

`data/clean/members_residence.csv` holds one row per claim about a member's
home: the place as the source names it, how exactly (`precision`: a street
address, a street name, a neighborhood, a side of the County or a
magisterial district), the year the source gives, and the source. Nothing is
coded North or South and no claim is chosen over another; the coverage
figure takes each member's most exact dated place in each year.

**How much is known, for the 75 members first seated from 1932 on.** A member
is counted under the most exact kind of place any source gives him, and dated
by the best-dated row of that kind: during service if the row's year falls
inside a term, otherwise by the distance to the nearest term's ends. Every
census read moves these numbers, so the count is not kept by hand:
`test_the_residence_coverage_table_in_the_write_up_is_current` in
`code/tests.py` recomputes it from the clean tables on every build and fails
with both sets of figures when the table below no longer matches.

| Most exact place held | Dated during service | Within 5 years of it | 6 or more years from it | Undated | Members |
|---|---|---|---|---|---|
| Street address | 14 | 19 | 8 | 0 | 41 |
| Street name | 2 | 0 | 1 | 0 | 3 |
| Neighborhood | 10 | 0 | 4 | 2 | 16 |
| Side of the County | 1 | 1 | 0 | 0 | 2 |
| Nothing | | | | | 13 |

So 41 of the 75 have a street address and 62 have a place of some kind,
but only 27 of the 62 are placed by a source dated to their service. The
sources found online give a place at the time of writing, an obituary's
address is where the person died, and a candidate profile's is where they
lived when they ran; County records may give an address at taking office
(`residence-county-records`). Whether a place dated after service should
count, and within what window, is `residence-after-service`; the coverage
figure counts any dated place, since it shows the state of the evidence,
and the window matters to the neighborhood analysis, which is not yet built.

## Census records

A census listing names a person, not a Board member, and gives several
traits at once, so each record matched to a member is one row of
`data/transcribed/by_claude/members_census.csv`, and the build derives each
trait from it rather than each trait being keyed separately. 80 records, for
73 members, from the 1870, 1880, 1900, 1910, 1920, 1930, 1940 and 1950
schedules. The columns:

| Column | Holds |
|---|---|
| `name`, `source` | the roster name and the record's citekey, `census<year><surname>` |
| `year` | the census year |
| `basis` | what ties the record to the member, stated once: the name, the place, and an occupation, a spouse or a house number where one agrees; where the index misreads a name, what it reads |
| `match` | what ties the record to the member besides the name, from a fixed list, several joined with `; `: `district` (the district he sat for), `occupation`, `household` (a spouse or child another source names), `address` (a house or street a newspaper also prints), `unique` (the only person of the name in the county's index that year), or `none`. Blank where no one has yet read the record for a tie |
| `checked` | what was read against the image: `read against the sheet, which agrees`, or what the sheet gives where it differs from the index. Every row names the sheet; see "Reading an image" |
| `gender`, `race`, `age`, `birthplace`, `occupation` | as the index prints them: `Male`, `Mulatto`, `39` |
| `birth_year` | a birth year the index prints as a date rather than as its `abt` estimate from the age (the 1900 schedule records a month and year); blank otherwise |
| `place` | the street and house number as read for residence, from the sheet where the sheet was read; blank where no one has read it for that purpose |
| `quote` | the index listing verbatim |
| `sheet` | the sheet's lines verbatim, where they were read |

A name alone with nothing else in agreement is no match. A row whose
`match` is `none` stays in the table, so that the search and the reading are
on record, and gives the member nothing: no birth year, race, gender or
place, which then fall to the default or to the member's other sources
(Sally, 26 September 2026). A blank `match` has not been read for a tie
and stands until it is; which rows are blank, and the revisit once the age
and neighborhood analyses are settled, are `census-match-quality`.

`code/clean/members_census.py` codes the printed values: `Male` a man,
`Female` a woman, `White` White, and both `Black` and `Mulatto` Black, as
Hjerpe codes Pinn's 1880 record. A printed value it has no code for stops
the build, since a dropped claim would fall silently into the default, and
so does a row whose `checked` names neither the sheet nor the index. The
birth year is the one the index prints as a date, or else the census year
less the age, and the note on it says which. The place joins the claims in
`data/transcribed/by_claude/members_residence.csv` in
`data/clean/members_residence.csv`, one row per claim, none chosen over
another and nothing coded.

The claim files keep words, not categories. `members_demographics.csv` has
`race_words` and `gender_words` (the pronoun, honorific or description as
the source prints it), and `members_party.csv` has `party_words`; the tables
that say what each means are `RACE_WORDS`, `GENDER_WORDS` and `PARTY_WORDS`
in `code/clean/members.py`, where a word not listed stops the build.
`members_terms.csv` keeps the election date the county prints; the January
start, the missing end and the election as how the seat was gained are
`code/clean/members_roster_results.py`'s. A press or obituary age is keyed the
same way: `members_demographics.csv` has
`age` and `age_date` (as printed: "25 April 2019", "1960"), and
`birth_year` only where a source prints a birth date or year. The transcriber
never subtracts. `code/clean/members.py` takes the year of the date
less the age, refuses an age with no year in its date, and refuses a row that
gives both a birth year and an age.

One record read on 25 September 2026 is filed and cited but kept out of the
table, since it gives a birth year that disagrees with the member's other
record and the build stops on two sources disagreeing: William Duncan's 1910
record (`census1910duncanwilliam`, 1857 against the 1900 record's August
1854). Which year is Duncan's is open (`duncan-birth-year`); the row is added
when it is settled.

**W. N. Febrey is one household, born November 1851.** The county's 1900,
1910 and 1920 schedules hold one William N. Febrey household, not two. All
three give the same marriage year, 1882 — eighteen years married in 1900,
twenty-eight in 1910 — and a wife born in the District of Columbia about
1860; the daughter is Annie L. in 1900, Louise E. in 1910 and Annie E.,
married to Ira H. Arnold, in 1920, whose son is entered Walter Febrey
Arnold; the son Henry W., born July 1891, keeps his own house in the same
district by 1910. No second household of the name stands beside them in
1900, 1910, 1920 or 1930: the wife is Eliza F. in 1900 and 1920 and Fannie
N. in 1910, and the two names are never in the same year. The 1910 sheet's
wife's given name and its age of 51 are that sheet's own errors, as are the
ages of 66 in 1920 and about 78 in 1930.

The *Evening Star*'s death notice of 23 January 1940 (`star1940febrey`)
closes the household: William N. Febrey died on 22 January 1940, "beloved
father of Henry W. Febrey and Mrs. Annie Louise Arnold" — the son and the
daughter of the 1900 sheet, the daughter by the married name the 1920 and
1930 records give her. It names no office.

His birth year is the one the 1900 schedule records as a date, **November
1851**; the ages in the later records would give 1859, 1854 and 1852, and
`AGE_MISREPORTED` in `code/clean/members_census.py` names the records no birth
year is read from. He is the William, 29, that the 1880 sheet enters in
Henry W. Febrey's household, and Henry W. Febrey sat for the same Washington
district in 1872-73. For the members seated 1870–1911 the 1880, 1900 and 1910
sheets name a magisterial district at the head of each page and, outside
the towns, leave the street column blank, so the district is the place
recorded, in the sheet's own words.

**Edward Duncan held Jefferson continuously from 1908 to 1932, one term, not
four.** The roster previously carried him as four separate rows across three
names, "E. Duncan" (1908–12), "Duncan" (1916–20) and "Edward Duncan" (1924–28,
two terms): O'Leary's and the county's own records give an election for 1908,
1916, 1920 and 1924, but nothing for the two four-year cycles between them,
1912–16 and 1920–24. The Alexandria Gazette fills both gaps: he is named
chairman of the board of supervisors in three pieces spanning May 1913 to
December 1915 (`alexandriagazette1913duncan`, `alexandriagazette1914duncan`,
`alexandriagazette1915duncan`), an explicit December 1919 notice re-elects him
for a term starting January 1920 (`alexandriagazette1919duncan`), and an
October 1921 piece still names him a sitting member, with leadership by then
rotated to Frank Ballenger (`alexandriagazette1921duncan`). He did not run
again in November 1931: a Washington Times election wrap-up has him a distant
third in the sheriff's race, "considered [the] most formidable rival because
of his 24 years' experience on the county board of supervisors"
(`washingtontimes1931duncan`), naming the same 24 years as his October 1938
obituary (read in prose, not yet filed with a citekey). Twenty-four years
back from a term ending January 1932 is 1908 — his first election. Sally
decided (27 September 2026) to record this as one term rather than one row
per election: 1908, 1916, 1920 and 1924 are each a sourced election win;
1912 and 1928 are known only because he is shown in office both before and
after each, not by a recorded win in either year, so the roster cannot say
those two renewals were contested (`duncan-one-member-or-three`).

The two census records that place him, `census1910duncan` (Jefferson, an
engineer, a one-year-old son Morton) and `census1920duncan` (the same
household ten years on, Morton now ten, the same trade and Irish parents,
"the only Edward Duncan in the county that year"), independently confirm one
man rather than three: race and gender attach from both records once the
roster carries one name across the whole term. They disagree on his birth
year, though — 1872 by the 1910 sheet's age, "abt 1870" by the 1920 sheet's,
neither a printed date — so both are named in `AGE_MISREPORTED` and he has no
birth year in the table (`duncan-edward-birth-year`).

**`members_by_year.py` does not yet reflect this.** It states 1912–1931
itself, from the standing assumption of three seats held by white men, and
does not read the roster for those years by design (above); Edward Duncan's
now-continuous term does not change what that table or the figure built from
it shows. Whether it should is an open decision, not yet made.

The filed copy of each record's Ancestry page is written by
`code/ancestry.py` from the row's own `quote`, since Ancestry refuses an
automated request and the page cannot be fetched by anyone reading this
repository. The page says on its face that it is derived. The copies filed before that
script carried a sentence saying Ancestry states the facts in the collection
were found using artificial intelligence and may contain errors; the 1930 and
1940 census record pages carry no such statement, so it is gone from all 80.
The one exception is William Duncan's 1910 page, which keeps its original
wording: the record is cited but kept out of the table while
`duncan-birth-year` is open, so there is no row for the script to build it
from, and it says so each time it runs.

Only the census record itself goes in this table. What a newspaper, an
obituary or a secondary source says, Hjerpe's reading of an 1880 record
included, is a separate claim and stays in `members_demographics.csv` or
`members_residence.csv`. `code/transcribe/members_census.py` moves any row that
cites a census record out of those two files and into the table, merging
it with the record's row where there is one, and stops where the two
disagree. A new record is keyed into the table directly, and the build
refuses a row citing a census record in either claim file, so the script
is run when it does.

### Reading an image

**Nothing leaves an image on one reading.** A census record is read against
its own enumeration sheet before any of its fields is used, and its `checked`
column says what the sheet gives. Ancestry's index is a finding aid, the same
standing as the OCR under `data/transcribed/by_ocr/`: it locates the line, it
does not read it. That is a second reading of every record, not a sample,
because there are only 72 of them and the cost of a wrong one is silent.

`code/build/members_claims.py` enforces the half of that rule a machine can
check. A row whose `checked` names neither the sheet nor the index stops the
build, and so does a `place` on a row the sheet was never read against, since
a street is the field the index gets wrong. `code/tests.py` reintroduces both
mistakes.

For a page read through OCR — a newspaper claim in
`members_residence.csv` — the quoted sentence is read off the page image before
the row is written, and any house number in it is read off the image, never
off the OCR. Where rows were entered before this rule, the backlog is cleared
a page at a time, whole pages rather than a sample of rows, since opening the
page is the cost and the rows on it are then free.

A pass over the rows that predate the rule, on 25 September 2026, read the
seven census records that had only ever been indexed, and two newspaper pages
carrying seven of the quoted addresses. It found one wrong value: Detwiler's
1940 sheet gives his birthplace as **Minnesota** where the index reads
Wisconsin, and spells the surname Detwiler, as the Board member does, where
the index reads Detweiler. Birthplace is not a column the build reads, so no
figure moved. Two smaller disagreements need no fix: the index's street name
for Buchholz, `1`, is a column number and not a street; and Byrne's sheet
gives 202 N. Highland St., which the *Daily Sun* of 11 September 1952 prints
as well. A third is settled below. The 103 figures keyed from the 1870, 1880 and 1890 volumes and the
whole of the POP-TWPS0076 Arlington block were re-read against the printed
pages and every one agreed.

**Tillema and Massey.** Both have a census row and a *Daily Sun* row of 11
September 1952 that name different streets, and the 1952 page prints exactly
what the rows quote — the disagreement is between the two sources, not in the
transcription. Tillema's 1950 sheet reads **N. Harvard St.**, and Arlington
has a North Harvard Street and no North Howard Street, so the Sun's "1903
North Howard Street" is its misprint. Massey's sheet reads **23rd Rd**, where
the Sun prints "4300 North 23rd Street"; North 23rd Road and North 23rd
Street are both real and both in North Arlington, so this is a different
house, not a different side. Neither changes what the build does: it carries
every claim with its source and chooses none.

**The pre-1912 sheets, read twice (26 September 2026).** Six fields the
rows mark as uncertain are read a second time off the filed sheet images,
each enlarged with its column heading and set against the same enumerator's
hand elsewhere on the sheet: Grunwell's initials (1880, page 451D, line 23),
Schutt's surname (1880, page 457B, line 34), Torreyson's given name (1900,
sheet 20B, line 89), William Duncan's age (1900, sheet 13A, line 49),
Phillips's middle initial (1900, sheet 10A, line 40) and Corbett's age
(1910, sheet 6B, line 52). The second reading was made with the first in
view, so it checks the reading rather than repeating it blind. Five agree.
Grunwell's **A. B.** and Schutt's double t, under one cross-stroke, are
firm. Duncan's **40** is firm, its second digit an oval like the
enumerator's 0 in the 40 on line 21 and unlike his 8, so its disagreement
with an August 1854 birth is the sheet's own. Torreyson's **A. Duke**
agrees: the initial sits under a later pencil mark, and the D is the
enumerator's D in *Daughter*, not his H. Corbett's age agrees with the row
that it is not legible: a 5, then a second digit written over. One
disagrees. Phillips's middle initial reads **A** on the second reading,
the shape of the A in *Andw* on line 43, where the row reads H; the letter
sits under a later pencil mark, and this enumerator's H in *Head* is
pointed too, so neither reading was firm on its own and a source outside
the sheet was sought (below). Two more 1900 fields the rows mark are then
read again, Darby's given name (sheet 22B, line 87), **Rezin**, and
Costello's street label (sheet 9A, lines 5–8), **Cherrydale**, and both
agree. Seven of eight agree, and none of the eight moves a number: Duncan's
and Corbett's birth years come from printed dates, not ages. The other
pre-1912 readings stand as read.

**Phillips's household is his father's (27 September 2026).** A second
source was sought for the 1900 household rather than a third reading of the
same smudge: an 80-year-old father-in-law named
Andrew Barbour and a daughter Margueritte born about 1889 are unusual
enough to search on directly. WikiTree's profile for Robert Augustus
Phillips (`wikitreephillips2024`), compiled from Find A Grave and the
census, gives a birth of 14 Jul 1833 in Dryden, Tompkins Co., NY, matching
the sheet's birth date and birthplace exactly, and a marriage to Mary
Imogene Barbour on 27 Dec 1880, matching the sheet's spouse and marriage
year; its own sources cite this same 1900 record, roll 1698, page 10,
ED 3, as his. The household is his, and the second reading, **A**, is
right. It is not the member's: Robert Augustus had an elder son by an
earlier marriage, a distinct man named Robert Henry Phillips (1865–1942),
who does not appear in the 1900 household. The sheet puts Robert Augustus
in the Washington district of Alexandria County, the district the member
sat for, which is why the match looked right for as long as it did; what
separates the two men is the roster's middle name, Henry, against the
sheet's A. He married in Washington, D.C. in 1880 and died there in 1912.
`census1900phillips`'s match is withdrawn (`match`
set to `none`) and it gives R. Henry Phillips, the member of 1893–95,
nothing: his race (**White**) now rests on the default, as it does for
every member before 1912 except Roach, and he has no residence claim at
all, joining the seven members with no census record found
(`residence-pre-1932`). No record of Robert Henry Phillips himself in
Alexandria County or Arlington was found in this search; if one turns up
later, it is the one to try, and his father's household in the Washington
district is a reason to look there.

**Five members off the assumed list (26 September 2026).** The censuses of
the years each served were searched for the members whose gender rested on
the default. Five gained a record, and with it a gender, a race and a birth
year read from a source rather than assumed: **B. M. Smith** (below),
**Storm V. Boyd**, a farmer in the Jefferson township in 1870 whose sheet
gives the middle initial as B where the roster gives V, so the match rests
on the district; **Duncan** of 1916–20, the Edward Duncan of Duncan Lane in
the Jefferson district, the household of `census1910duncan` ten years on by
his son Morton, his trade and his Irish parents; **W. J. Ingram**, a
hardware salesman at 204 Virginia Ave in the Arlington district in 1920,
whose widow Julia keeps the house in 1930 with their son William; and
**E. C. Thornburke**, whom the sheet and the index both call Eugene C.
Turnburke, a house painter at 35 Preston Avenue in the Washington district.

Nine members keep the default, and the searches that found nothing are in
`gender-from-names` so that nobody repeats them. Two are worth stating
here. **Wibirt** has two households in the Arlington district in 1920,
William C. and Clarence, and this search alone found nothing to choose
between them, so neither is a row (below, "Wibirt and Walker settled by the
Gazette and the census," has what settled it the next day). **Edward
Duncan** of 1924–28 has no record of his own: Arlington County holds no
Duncan of his age in 1930, and the 1920 record above is entered against the
roster's Duncan of 1916–20, the term its year falls in.

**Three more off the assumed list, from the press (27 September 2026).**
The census route being exhausted for the seven members named in
`gender-from-names`, the Alexandria Gazette (Library of Congress,
Chronicling America) was searched instead, by name and district, over each
member's term. Three carry a contemporary honorific and leave the assumed
list: **H. Dwight Smith** presided over an 1873 meeting of the Arlington
Republicans as "Captain H. Dwight Smith" (`gazette1873smith`); **Lott W.
Crocker** is "Mr. L. W. Crocker, President" of the Arlington Turnpike
Company the same year (`gazette1873crocker`); and a Board of Supervisors
meeting of 6 December 1875 has "Mr. Rowe nominated Mr. Vanderberg for
chairman, but upon his declining, Mr. Schutt was unanimously re-elected"
(`gazette1875schutt`) — that piece names him F. C. Schutt of Jefferson,
read against the only Schutt household the county's 1880 census holds
(`census1880schutt`), the same one the roster's Francis D. Schutt of
1873–74 and Francis G. Schutt of 1874–81 are already read against.

Two remain on the assumed list, and are not settled by this search.
**William H. Robinson** appears once, named plainly among the Board of
Supervisors of 18 September 1878, with no pronoun or honorific attached to
him; every other Robinson the Gazette prints in his years (a Richmond coal
committee, a King George visitor, a deceased tailor) is a different man.
**Walter G. Willson** turns up only as a Harvey Willson unrelated to him,
and as bare initials in an 1889 road-fund ledger; nothing ties a Gazette
pronoun to him. **Wibirt** and **Walker** are placed more precisely by this
search, which is what let the census settle them the same day (below): the
Gazette consistently calls the Arlington-district supervisor "W. C." or
"William C. Wibirt" — a nominee for the seat in October 1915, a pallbearer
in 1918, and the county's assessor of 1910 named again in 1921 — and its
election notice of 30 October 1915 gives Walker's full name, "Washington
district, W. T. Weaver, Robert L. Walker," among the nominees for
supervisor. Neither piece attaches a pronoun or honorific to either man.
The searches themselves, and what each found, are kept in
`gender-from-names` rather than repeated here.

**Wibirt and Walker settled by the Gazette and the census (27 September
2026).** The 1915 election notice above (`gazette1915wibirtwalker`) gives
both men full names for the first time, and the census, retried against
those names, now ties a record to each: **William C. Wibirt**, the older of
the Arlington district's two 1920 Wibirt households (born about 1855,
against Clarence's born about 1865), alone in his household, his
occupation reading "none" on the sheet, so nothing beyond the name and the
district favors the assessor of `gazette1873smith`-style press mentions
over any other William C. Wibirt (`census1920wibirt`); and **Robert L.
Walker**, the only Robert L. Walker keeping house in the Washington
district that year, an inspector in the sanitary trade, with his wife Annie
and six children (`census1920walker`). Both leave `gender-from-names` a
man, a race (White) and a birth year (1855, 1876) from the census rather
than the default.

**B. M. Smith, 1930 and 1940.** The member appointed in June 1933 is
**Benjamin M. Smith**, a real-estate salesman in 1930 and a broker in 1940,
working on his own account both years. The *Evening Star* calls its B. M.
Smith a real-estate dealer with an office at 443 Columbia Pike; this man
lives at 439 Columbia Pike in 1930 and 2908 Columbia Pike in 1940, and is
the only B. M. Smith in the county's index in either year in the trade. Both
streets were read off the sheet, where the name is written across the lines
in the left margin. The 1940 sheet's residence column for 1 April 1935 reads
**same house**, which dates the address inside his term, and the two ages
give him a birth year, 1885, within a year. **Lowry** is still unplaced: he
is in no 1940 or 1950 census index under Roye or any near spelling, and
Ancestry holds no Arlington city directory at all (`residence-1932-1962`).

**Detwiler's sheet number, 1940.** The sheet is **63A**, and Ancestry's
index's 62A is the sheet before it. The sheet's own number is a 3 written
over a 7, which is why it has been read as 63A or 67A. The images of
enumeration district 7-13 settle it: image 64 is 62A, stamped 222 by the
National Archives, image 65 is its blank B side, image 66 is Detwiler's
sheet, stamped 223, and image 67 is 63B. The stamp runs one to a sheet, so
Detwiler's is the sheet after 62. The bib entry and the filed image's name
carry 63A.

**Ames, 1940.** Sheet 21B, read again at full resolution on the same day,
gives W. P. Ames's house no street. The label W. Lee, with an abbreviation
of a looped capital (H, P or B) and one or two letters, is written against
lines 72 to 76, and a heavy wavy rule crosses the location columns between
lines 76 and 77. Ames is line 77, below the rule, where the street column is
blank to the foot of the sheet; W. Lee is the label of the household above
him, 3294 at line 74. His house number reads 68 and then a 5 or an 8, not
the index's 436. Neither is firm, so the row keeps Clarendon, the
unincorporated place in the sheet's heading, as its one firm place
(`ames-residence`).

## Race, gender and birth year of Board members

Birth years come from the same files as race and gender, one row per
source, and reach `members.csv` as `birth_year` with a source and a
note; with no source the year is blank and `unsourced`, since no standing
assumption stands in. A census listing gives an age, and the year is the
census year less the age, so it is right to within a year, except where
the index prints a birth date; an obituary or a profile gives a birth
date, or an age on a date, and the row's basis says which. Which case it
is reaches `members.csv` as `birth_year_precision`, `exact` or
`within a year` (86 of 107 are within a year); the age figures draw both
the same, a stroke assuming a mid-year birthday, since the half-year is
below what a stroke can show (Sally, 26 September 2026). What the report
does with such distinctions is the data appendix's to explain
(`data-appendix`). For members
seated 1960 on the sources are obituaries on legacy.com,
Dignity Memorial and InsideNoVa, candidate profiles in the Connection,
ARLnow and Patch, a Senate of Virginia member page, and the Post's archive
where it shows the paragraph that carries the age. The build refuses a year
that would seat a member under 18 or over 100, and two sources disagreeing
stop it. `election_year` on each elected term is the election that seated
it, a January start following a November election, so a figure can
subtract without re-deriving that rule.

Race and gender come from `data/transcribed/by_claude/members_demographics.csv`,
one row per claim a source makes about a member, in the source's own words
with a citation to the page the document prints, and from the census records
above; and otherwise from a default,
a white man, labelled `assumed`. Each cell of `members.csv` says which, and
`gender_evidence` says how a gender is known: `record` (a census listing),
`press` (the pronoun or honorific a paper uses for the member; each such row
of the claim file quotes the sentence and cites the page), both joined with
`; `, or `none` where the default stands. Two sources disagreeing about a person stops the build, and an attributed name
that matches no roster name stops it too, so a near-miss cannot fall silently
into the default. The default is a claim, and this is what stands behind it in
each period:

| Period | Race | Gender |
|---|---|---|
| 1870–1888 | Five Black members named by Hjerpe (2021): Rowe, Syphax, Pinn, Pendleton, Allen. Pinn, Pendleton and Allen each rest on a reproduced 1880 census image; Rowe and Allen on narrative statements in her paper; Syphax on O'Leary, who writes that his photograph shows he was African American. The sentence naming the five as a group sits in her own list of open inquiries, and the file records it as such. O'Leary adds that "a majority of the early office holders" were probably African-American but cannot name them. Nobody on our side has checked the census linking. | Names in O'Leary, but seven members before 1912 appear by initials only (`gender-1870-1912`). |
| 1889–1930 | One collective sentence: the board "became and remained all white for the duration of this system" (Hjerpe 2021, p.4), sourced to the county's election records. No per-person evidence. | Names in O'Leary; initials only before 1912. No source names a first woman member, so "all men before Magruder (1932)" is assumed. |
| 1931–1986 | Nothing per-person from any source, except that the county's list of the November 1931 candidates marks three of its 51 names "(Col)" and none of the five elected (see "Black candidacies"). The default rests on Newman (1987) being described as the first Black member since Reconstruction. About 280 person-years. **The weakest stretch.** | Census listing or a press honorific or pronoun for all but B. M. Smith (1933). |
| 1987–present | Per-person: Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), and Tejada as the first Latino member (Hjerpe 2021). The Arlington Historical Society's Newman entry names Newman, Monroe and Dorsey as African American members, and its Center for Local History entry gives Tejada's Latin American heritage; Monroe also rests on the Arlington NAACP president's words at his death, and Dorsey on his own statement (2020). | A press pronoun or honorific for every member. |

In November 1931 three Black candidates ran for the Board and all lost; who
they were, and every other Black candidacy, is under "Black candidacies"
below.

None of the three roster sources states anyone's race or gender. Race comes
from Hjerpe and O'Leary; gender comes from a census listing or from the
pronoun or honorific a paper uses for the member, and where neither has been
found the default stands, labelled `assumed`. The
seat counts for 1870–1888 are therefore Hjerpe's identifications applied to
O'Leary's roster; Alex Keena's earlier year-level counts were a replication
of the same source and are not a second one.

What any source says, in full, is ten members recorded as other than White
and twelve women (Magruder, Cannon, Buchholz, Bozman, Grotos, Whipple, Favola,
Hynes, Garvey, Cristol, Coffey and Cunningham). Everyone else, 109 of 119
people, is recorded as a white man because no source speaks to them. The
verification to ask of County staff, and through them the Historical Society,
is therefore the default rather than the lists: every other member has been
treated as a white man; where is that wrong? That is `default-1931-1986`
in `docs/questions.csv`.

Two things from the record bear on the report's argument. Monroe first stood
in the April 1999 special election for Eisenberg's unexpired seat and lost to
Michael D. Lane by 169 votes, 9,530 to 9,361; he won the two-seat general that
November. Hjerpe argues that the at-large era's members of color all won in
cycles where two seats were up; Monroe is the case where the same candidate
loses the one-seat contest and wins the two-seat one seven months later. And
the *Sun*'s coverage of the November 1938 staggered-terms referendum carries
two contemporaneous claims about women and Board structure: the Arlington
County Woman's Democratic Club opposed the change, holding that staggering
would make it "virtually impossible for a woman to be elected to the board"
(`sun1938referendum`), and a week later the Organised Women Voters of
Arlington County objected to the ballot's wording (`sun1938womenvoters`).
Florence E. Cannon is elected parliamentarian of the Organised Women Voters
in the second notice and sits on the Board from 1948 to 1951.

## Party of Board members

Party has never been printed on the County Board ballot; the county's own
candidate history says so on its first page. So there is no official record
of a member's party, only of whose candidate they were, and that is what is
coded, per term rather than per person, because a label changes between
elections (Bozman ran as ABC's candidate five times and as a Democrat once).
Three sources, in order:

1. The county's candidate history, which prints a label in parentheses after
   a name from 1931, `(D)`, `(R)`, `(ABC)`, `(I)`, though not on every winner
   and rarely before 1950.
2. The state's elections database, which records party from 2007 and is the
   only source from 2022. Where its general-election row carries no party
   (2023 on), a win in that year's Democratic primary stands in.
3. Reporting, in `data/transcribed/by_claude/members_party.csv`, one quoted and
   cited claim per row, used only where the county prints `(I)` or nothing.

Where the county and the state both name a party they must agree, and a cited
claim that contradicts a party the county prints stops the build. A label the
build has not been told what to record stops it too: `elections.LABELS` in
`code/build/` maps every label a County Board candidate has carried, and a
winner under a label only losers have carried is a decision, not a default.

**The rule for reporting** (Sally, 23 September 2026): the party or coalition
whose candidate the source says the member was, and a party's open
endorsement makes someone its candidate whatever label they ran under. Dugan
in 1946 and Vihstadt in 2014 are coded Republican with "ran as an independent"
in the note. A source saying only that someone *leaned* a party's way
(Tillema, 1952) is not an endorsement and stays independent. ABC's endorsement
counts as ABC; where a source names both ABC and a party, the party (Fisher,
1967). ABC is its own band rather than folded into Democratic, because the
county recorded it and an ABC-majority Board from 1957 to 1966 is a finding.

| Period | Source | What it gives |
|---|---|---|
| 1932–1950 | County candidate history, where it prints a label | 23 of 33 terms: the county for 9, newspaper reporting for 1933 and 1942–49, McCaffrey (2026a) for the 1949–52 independents and the 1952 appointees; the rest are `unsourced`. |
| 1951–1966 | County candidate history | Every winner but Blevins (1956) and the two `(Convention)` nominees of 1955. `(ABC)` appears from 1957. |
| 1967–1983 | County prints `(I)` on most winners; reporting names the party | Fisher, Munsey, Purdy and Wholey as Democrats; Bozman as ABC's candidate; Grotos, Frankland and Detwiler as Republicans. Ricks stays `(I)`. |
| 1984–2006 | County candidate history | Every winner labelled. Bozman `(I)` through 1989, `(D)` in 1993. |
| 2007–2021 | County and state, checked against each other | Agree on every winner. |
| 2022– | State database | Party on the 2022 general; from 2023, the Democratic primary win. |

The reporting file has 41 rows, each a sentence in the source's own words
with its citation, keyed on the name and the term's start year: pieces by
Scott McCaffrey for the Sun Gazette and ARLnow (2009–2026), the Library of
Virginia's biography of Joseph Fisher, Joseph Wholey's obituary and an ARLnow
report of the 2020 special election. What it yields for 1932–2026 is 146
terms: 76 Democratic, 18 Republican, 15 ABC, 12 independent, 25 not recorded.
The built table reproduces three compositions reported independently, three
Republicans in 1970 and again in 1979 and three independents in 1952, none of
which was used to build it.

**Not attempted before 1932.** O'Leary's own summary of the magisterial era
is that "with few exceptions, party affiliation has to be inferred", and
nothing held names a party per person; the figure starts at 1932 with a gap
before it. It is recoverable from the Alexandria Gazette (Chronicling
America, sn85025007), which prints the result of each May election. Tried:
1895 (Grunwell, Corbett and Duncan were elected on "the entire republican
ticket", 24 May 1895, p. 3) and 1871 (Deeble on "the whole Conservative
ticket", 26 May 1871, p. 3; Smith and Rowe unlabelled). 1872–73 were read
and print no party beside the supervisors; 1874–75 were fetched and not read. Paused, and no row is keyed for
any of these: the County has not said it wants these data used.

**What is not labelled.** 12 terms have no label anywhere: the four 1932
winners (Magruder, Fellows, Gall, Kelley), B. M. Smith 1933, McShea 1934,
the four 1936 winners (Magruder, Chew, Yeatman, McShea), Wilt 1960 and
Richards 1975. Read and settled from the Sun, Daily Sun, Northern Virginia
Sun and Evening Star: DeLashmutt 1942, Campbell 1943, Lloyd 1945, Cuppett,
Frisbie (three terms), Chew and Cannon 1948, Garnett 1933, Krupsaw, Kaul,
Blevins, Ricks and Buchholz 1955. `(Convention)` on Kaul and Krupsaw in 1955
is ABC's nominating meeting (Daily Sun, 25 May 1955). `(IM)` on Buchholz in
1954 is the Arlington Independent Movement, whose nominee the Evening Star
calls her; AIM candidates (Buchholz, Blevins) are coded independent, so
whether AIM is a band of its own is open. Ricks was backed by ABC and the
Democratic party and is coded Democratic, as Fisher is.

The 1931 election was non-partisan in what the papers print: the Washington
Times of 4–5 November 1931 labels Gosnell alone ("Republican nominee"), the
Evening Star of 5 November prints no party, and on 2 January 1936 the Sun
calls Ames "the only Republican" on the Board. That leaves the other 1932 and
1936 winners without a printed party. Not found: Smith 1933, McShea 1934
(Evening Star searches by name returned no article) and Wilt 1960 (the
Northern Virginia Sun's OCR for January 1960 is too poor to search). Brunner
(1984–87) stays on the county's `(I)`; the 1983 Post preview is not read.

`members_by_year.csv` carries the split as `dem`, `abc`, `rep`, `ind` and
`unrecorded`, seat-years from 1932, empty before. "Not recorded" is a band
rather than a gap because the seats existed and were held; what is missing is
the label.
