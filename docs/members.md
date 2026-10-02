# The Board

This write-up covers who held each seat and when, and who they were: what each
number in `data/clean/members.csv` and `data/clean/members_by_year.csv` is,
what backs it, and what is assumed where nothing does. How a decision was
reached is in the git history rather than here. `code/citekeys.py` explains the
placeholders in the `source` columns, and `docs/questions.csv` holds what is
still open.

## What rests on an assumption

**Race, 1889–1986.** Every seat is coded all-White on the "first since
Reconstruction" framing. The five Reconstruction-era members rest on Hjerpe's
census linking (`member-demographics-lists`).

**Gender.** William H. Robinson and Walter G. Willson rest on the default,
man, both recorded negatives (below, "The members that keep the default").
Every other member has a census listing or a pronoun or honorific in the
press, and `gender_evidence` in `members.csv` says which each rests on.

**Race and gender from the census.** For the members first seated 1932–1966
and 1870–1904, race and gender come from census records. Each index reading
was checked against the sheet, where the row could be found on it. The match to
the member rests on the name, on the district he sat for or on Arlington, and,
where the record gives one, on an occupation, a household or a street. No
census holds Casto, H. L. Brown Jr, Fisher, Lowry or T. W. Richards of the
later era, or H. Dwight Smith, Crocker, Schutt, Robinson or Willson of the
earlier. R. Henry Phillips has a record whose household is his father's, not
his own, so it gives him nothing (below).

**Birth years.** Birth years are held for most members, and they rest
on the ages in census listings and on an age stated in an obituary or a
profile. Each is right to within a year. The age figure draws a year only where
every sitting member either has a birth year or is one of the three the
figure names, and it starts in 1932. Those three are W. P. Ames, found in no
census, and Susan Cunningham and Tannia Talento, recent enough that a stated
age should be findable. Naming them rather than allowing a count of unknowns is
what makes the gap a known quantity: a member who arrives without a birth
year and is not among them stops the build. Every member seated in 1900-31
has a birth year.

**1912–1931 rests on no assumption.** `arlhist1967officials`, the Historical
Society's own compilation from the Board's minute books, names all three
magisterial seats — Arlington, Jefferson and Washington — for all twenty years.
It states the one vacancy, in the Washington seat in early 1920, rather than
leaving it silent. `members_by_year.py` reads the roster for those years like
any other (below, "The roster names 1912 to 1931").

**1870–1911 rests on O'Leary's electoral history and the same article
together.** The article settles names, the July–June term year, and
terms O'Leary does not record (below, "The article corrects and adds for 1870
to 1911"). The statute behind the July
seating is `vaacts1870` ch. 76 sec. 4, below ("The Board's year ran 1 July
to 30 June through 1901"). Two seats that the article gives to a
different man are settled, and the roster follows the article in both: see "Two
seats go to the man the minute books show sitting" below.

**Party.** Terms from 1932 that no source labels carry no party, and some
labels are unresolved. No party is attempted before 1932 (`party-unlabelled`, `party-before-1932`).

**Every place carries a precision**, read from the place's own words by rules
in `code/clean/members_residence.py`:

- a house number with a street is an address;
- a street with no number is a street;
- a neighborhood, civic association or named community is a neighborhood;
- "North Arlington" or the northernmost section is a side;
- one of Alexandria County's three magisterial districts — Arlington,
  Jefferson or Washington, as the 1880–1910 census sheets head each page — is
  a district.

A place no rule reads stops the build. A house number whose street is unread
(Ames) counts as a neighborhood.

**Before 1932 the only places are the census sheets' own.** Most members
seated 1870–1911 have a record. For nearly all of those the sheet gives a
magisterial district and nothing finer, because the street column is blank
outside the towns; Cherrydale, Washington Avenue, Old Glebe Road and
Saegmuller's Maryland Avenue house in Washington City are the exceptions.
Roach is a weak match, flagged in his row. The 1870–1920 indexes hold no record
for the remaining members under any spelling tried, R. Henry Phillips among
them — the one household read against him is his father's
(`residence-pre-1932`). The Gazette places two of them without a census:
Willson on six acres by Ballston and Smith on the Arlington township's party
committee (below, "Smith, Crocker, Robinson, Willson and Phillips").

**The seat itself places nobody before 1932.** No instrument required a
supervisor to live in the district he represented before 1903, so a member
seated for a magisterial district has no claim from the office, and every place
comes from a record. See "Residence in the district" below.

**Modern residence is transcribed but not yet coded.** The 1973 Post map that
places a whole Board at once has not been seen (`mathews1973-map`). Some
of the members first seated 1932–1962 have no place (`residence-1932-1962`), and
so do some of those seated 1964–1999 (`residence-1964-1999`). Two rows postdate
the member's service (`residence-after-service`). For Thomas, two sources name
different places (`thomas-residence`). Tillema's and Massey's sources also
differ, but what each source says is settled; see "Reading an image".

Each of these is a row in `docs/questions.csv`, naming whose court it waits in
and what would settle it.

---
## Residence in the district

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

The record does not support three things it would be easy to assume.

First, the office named in the rule is not certain. "Supervisor of roads" is
the Gazette's phrase, and the Code of 1887 ties district residence to the road
surveyor (sec. 963), not to the Board seat (ch. 9 sec. 96) — while the seat is
what fell vacant.

Second, Freedman's Village cannot be the cause. The 1890 census puts it inside
Arlington district, not Allen's Jefferson (`census1890`), so the clearing that
began in December 1887 was emptying a settlement in another district.

Third, Frank Hume is not simply the instrument of a purge. By 1890 he was
running for Congress as an independent Democrat, and the Washington Bee
endorsed him, writing that "he should receive the undivided colored vote
because he is the colored man's friend" (`washingtonbee1890hume`). That is two
years later, and it is no evidence about 1888.

Where Allen lived is unknown, and no account of why the rule issued has been
found. The episode reached no newspaper that took his side: the Washington
Bee carries nothing on it in any issue from August to December 1888, the
Richmond Planet has one digitized issue in all of 1888 and it is silent, the
People's Advocate had ceased publishing by 1884, and the National
Republican's digitized run ends in May 1888. What would settle it is the
Alexandria County court order book for 1888, which would carry the rule and
its disposition and name the policemen removed at the same sitting, and the
Board's own minute books; neither is online (`allen-1888`).

## Seats that changed hands

### Hume's two dates

The rule against Allen and Hume's appointment are two events three weeks
apart, and Hume's first appearance in the record is a third, six weeks after
that. The Gazette of 3 October reports the appointment as made "yesterday",
2 October. `arlhist1967officials` opens Hume's term on 13 November, and the
Gazette's own Local Matters column of that evening, reporting the Board's
session "to-day", lists him for the first time among the supervisors
present: "the Board of Supervisors were in session at the County... to-day;
present, A. B. Grunwell, chairman, and Messrs. Frank Hume [and] Horatio
Ball" (`alexandriagazette1888supervisors`). This is the same convention the
Historical Society used for Saulisbury below: the article dates a term from
the minute books' first record of a man sitting, not from the instrument
that named him. The roster's start date and the court's appointment date
answer different questions.

### Pendleton to Saulisbury, November 1884

Between Pendleton's second term beginning 1 April 1884 and Saulisbury's
first recorded appearance on 15 November, `arlhist1967officials` states
only that "[n]othing in the record shows why Saulisbury took Pendleton's
place, nor exactly when." The Gazette was searched for Pendleton, for
Saulisbury (and the more common spelling "Salisbury"), and for "Board of
Supervisors" across the weeks bracketing 15 November 1884, with no report
of a resignation, a court action or a Board seating found. The paper
covered Allen's removal because a court rule made it news; whatever moved
Pendleton out generated none (`saulisbury-1884`).

### Pinn to Mills, August 1881

Pinn resigned 15 August 1881 in Virginia's Readjuster year, replaced the
same day by Francis M. Mills; O'Leary gives him the whole term and Mills no
part of it. Twelve days before the resignation, the Gazette covered a
"Republican Convention - A 'Split'" at Alexandria's Colored Odd Fellows'
Hall on 3 August: forty-five delegates met to choose delegates to the
Republican state convention, called to order by William A. Rowe (himself a
supervisor, above); a Mahone Readjuster faction walked out, and the
remaining "Straightout" convention heard speeches from Benjamin Austin,
T. B. Pinn and Van Miller "declaring that the boast of the Mahone
readjuster leaders that they had captured the republicans of this city and
county of Alexandria was false in every particular"
(`alexandriagazette1881split`). Pinn was a Straightout Republican leader in
active opposition to the Readjuster coalition twelve days before he left
the Board; the Gazette was then searched for the resignation itself, for
Mills's appointment, and for "Board of Supervisors" through early September
1881, with nothing found naming a reason. The convention speech establishes
where Pinn stood, not why he left (`pinn-1881`).

### Squier, the control

The same roster prints a fourth Jefferson-adjacent departure in Pendleton's
year: Perkins W. Squier, Arlington district. A footnote in
`arlhist1967officials` explains his term without ambiguity —
"Postmaster of Alexandria City. Court declared seat vacant under the
Virginia law prohibiting Federal employees from holding office in the
State, and appointed a successor." Squier was White. Where Allen's rule
alleged non-residence and was never brought to a disposition, Squier's
removal named a statute and Squier held a second public office the statute
reached; the Historical Society's own record, not a newspaper search, is
what settles this one. The county court removed a White supervisor on a
stated legal ground in the same window it moved against Allen on an
unresolved one.

The statute the court applied is the one that empties three more seats
seventy years later. Virginia barred holders of federal office from state
and county office in 1788, and the General Assembly added the clause making
acceptance of a federal post *ipso facto* vacate the Virginia one by Acts of
1883-84, ch. 145, approved 22 February 1884 and in force from its passage —
five weeks before the county court seated Squier's successor. The Supreme
Court of Appeals upheld that provision, by then Code of 1950 sec. 2-27, in
*Dean v. Paolicelli*, declaring Alan L. Dean's seat vacant from the first day
of January 1952 because he held a post at the Bureau of the Budget, and
restraining the treasurer from paying him (`paolicelli1952`). The decision
took the Board's whole Non-Partisan majority at once — Dean, Robert W. Cox
and Daniel A. Dugan — so Arlington held four County Board contests on 4
November 1952, the three unexpired terms and the seat Alfred E. Frisbie was
leaving on 31 December (`dailysun1952appointees`). One provision reaches the
Board at both ends of the period this report covers.

---

## The roster

`data/clean/members.csv` holds one row per person per term: name, term
number, district, when service began and ended (to the month), the months the
term held (`held_from` and `held_to`, counted from year 0, the end exclusive),
how the term began, and a source per row. The terms run from 1870 and come from
four sources in sequence: O'Leary's electoral history to 1915, the Historical Society's
article for 1870–1931, Novack's roster from 1932 to
1994, and election results after that, the county's candidate history to 2021
and the state's elections database from 2022.

A term is the natural unit: person-years fall out of it, while a term starting
in May or ending in February cannot be recovered from a list of years. A
vacant seat is not a row, since nobody served. `term_number` counts within a
person, so someone appointed to a vacancy who then won twice has three rows
numbered 1, 2, 3; William A. Rowe's rows run longer, and include his move from
Jefferson district to Arlington.

`seated_by` says how each term began: election, special election, appointment,
or unrecorded where O'Leary writes only that someone was replaced. Three builds
select terms by it, so it is a column, not something read out of the note.

### What the county's roll adds

**Novack records service and election returns record contests**, and the
county's roll records service too. That difference is why the roll is read.
Novack writes a mid-term arrival or departure into his parentheticals, which
is how the terms between 1933 and 1975 that began in an appointment are
known. The county's candidate history and the state's database name the
winners of contests, so until the roll was read a term that ended early showed
only in the win that filled it, and a seat filled without a contest showed not
at all.

Both things followed from that. Some terms ran months longer than their
holders served, because the roster ended each at its successor's seating for
want of a record of the departure itself: Whipple, Hunter, Eisenberg, Monroe,
Favola, Zimmerman, Gutshall and Cristol. The roll dates most of them; it
leaves Milliken's 1990 departure and Favola's to Novack and to ARLnow
(`members_roster_roll.DATED_ELSEWHERE`). And Tannia Talento, appointed on 15 July 2023
to the rest of Cristol's term, was in the roster not at all, having won
nothing. The roll dates every one of those departures and her arrival, and
`members_roster_roll.py` applies them.

The roll is also a second witness where Novack already speaks. For 1932 to
1994 the two are independent records of the same Board, both are cited on the
terms they agree about, and `check_against_novack` refuses a year where they
name different people. They agree on every departure the roll dates in
those years and on the membership of every year but 1939, 1941 and 1986, each
declared: the
roll seats a November winner in the year of the election where the roster
seats him the following January (1939), and in 1941 and 1986 it prints one
name twice where the fifth member should be, leaving out Elizabeth Magruder
and John Milliken, whom Novack names.

**Neither record wins by default, so a disagreement is read against a third
source.** Novack is a historian working from the Board's records and is the
better witness to what a term was; the roll is the county's administrative
list and the better witness to a date, but it misspells Blevins, prints a
name twice in two years and leaves a member out each time. One disagreement
has arisen and `members_roster_roll.OVERRULED` holds it: the roll dates
Howard Massey's appointment to 10 November 1952, alongside the three members
elected on 4 November, where Novack has him appointed on 18 September to
serve until that election. The Daily Sun of 11 September 1952 settles it in
Novack's favour, naming Massey one of three the judge appointed that month -
"Picks Byrne, Tillema, Massey; Replaces Dugan, Dean And Cox 'Til After Nov. 4
Vote" (`dailysun1952appointees`). A disagreement with no third source to
read it against stops the build rather than being resolved here.

**A month belongs to whoever held the seat for any part of it.** The roll
dates a departure and an arrival to the day; the roster counts whole months,
and applies that rule in `members_roster_roll.py` rather than in any figure.
A seat vacated on 14 December 1995 and filled on 30 January 1996 is therefore
Whipple's in December and Zimmerman's in January, and no month stands empty.
Where a gap does cover a whole month the seat was empty, and these
months since 1932 were: March and April 1990, October 1997, March 1999, February
2003, January and February 2012, March 2014, and May and June 2020. Each is a seat Arlington left unfilled
while a special election was called, the Board sitting with four members.
`members_roster_roll.EMPTY` names the departure and the arrival that bracket
each, read off the roll, and `check_seats` holds the roster to them: an
undeclared gap stops the build, and so does filling a declared one. Prorating
within a month would be more exact and would make a seat-year a fraction of a
month, which nothing else here counts below.

**No one was appointed to any of those months.** The roll names an
appointment in each of 1933, 1934, 1947, 1952, 1960, 1975 and 2023 and in no
year after 1975 but 2023, and ARLnow reports the Board in February 2014
operating "with four members until a special election is held"
(`arlnow2014zimmerman`). Talento's is the only appointment to the Board
since 1975.

**The three stretches `arlhist1967officials` left outside any term block are
not gaps.** Before the roll, Magruder's, Lloyd's and Krupsaw's departures were
dated only by the election or appointment that followed, so the days between
a seat falling vacant and being filled — 10–17 May 1947, 3–26 November 1947
and 21–29 January 1960 — fell in no term block the article named. The roll
dates each departure and arrival to the day and, on the same month-grain rule
above, closes all three: Magruder's seat runs through May 1947 and Cuppett's
begins then; Lloyd's runs through November 1947 and Frisbie's begins then;
Krupsaw's and Wilt's both hold January 1960. Nothing here was ever
unrecorded, only undated to the day.

### What the law made the Board, and when a term ran

**The constitution created the Board; the acts of 1870 stood it up.** The
constitution framed in 1868 and ratified in 1869 divides every county into not
fewer than three townships, has one supervisor elected annually in each, and
provides that "The Supervisors of each township shall constitute the Board of
Supervisors for that county" (art. VII sec. 2, `vaconstitution1869`). The
mechanism is the constitution itself, not an enabling act. Three acts of the 1869–70
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
name, the at-large method and the five seats therefore arrive together.

**A separate County Attorney needed its own act, and its 1952 referendum was
never called.** The League of Women Voters proposed a Board-appointed counsel
apart from the Commonwealth's Attorney on 29 September 1951
(dailysun1951institute), and 1952 c. 569 offered the voters a referendum on
creating the office (vaacts1952c569); it was not among the seven questions on
the 4 November 1952 ballot (dailysun1952lwv), so it was never held. Unlike the
election-term referendum of the same 1952 package, reopened in 1954 and 1958
(vaacts1954c151, vaacts1958c207), no later session is known to have reopened
this one: the 1962 recodification carries the act forward essentially
unchanged as sec. 15.1-680, still opening "in the year nineteen hundred
fifty-two", and today's Title 15.2 chapter 7 carries no county attorney
section the way its neighbors carry secs. 15.2-707 to 15.2-709
(vaacts1962c623). Edmund D. Campbell was already acting as the Board's
counsel in the autumn of 1952, before any such office existed
(paolicelli1952), so his role rests on something other than this act.

**When a term begins depends on the constitution in force.** Under the
magisterial system elections were held in May and the winners took office on
1 July following, so those terms run July to June (below). The 1902
constitution moved county and district
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
speaks to four. Their terms close in January 1912, where the Historical
Society's article picks the seats up (below). The note on such a row says the end is the statute's; where
the next listed election seats a successor on the same date the departure is
sourced and carries no note.

### The roster names 1912 to 1931

**Two elections of 1912 to 1931 come from the county's candidate history.** It
prints them under the district headings, not under "County Board": November
1923 (Ingram in Arlington, Duncan in Jefferson, Thornburke in Washington, each
the only name listed) and November 1927 (Duncan and Thornburke, each with the
highest vote). They are keyed in
`data/transcribed/by_claude/members_terms.csv`, page 2 and page 4, as five
terms seated the following January, with no end recorded: the county gives
neither a start nor an end, so the January start was the build's rule for a
November winner and each term held to the end of its first year (1924 and
1928). Jefferson's "Duncan" is Edward Duncan: not the William Duncan who held
Jefferson from 1895, but the same man as the roster's "E. Duncan" (1908–12) and
"Duncan" (1916–20), one continuous term from 1908 to 1932 (below).

**The article covers the whole era from the minute books.**
`arlhist1967officials`, the Historical Society's "County Officials in
Arlington, 1870-1960," gives Board membership by magisterial district, term
by term, compiled from the Board's own minute books. It covers 1908 through 1931 without a gap, in the overlapping term-blocks the
source itself prints, keyed in
`data/transcribed/by_claude/arlington_historical_magazine/arlhist_terms_1912-1931.csv`.
The three districts hold a seat in each of those twenty years, and this
source or `members_terms.csv` above names every seat-year but a single
vacancy. The Washington seat sat empty from 1 January to 20 February 1920,
after Clarence R. Ahalt, elected to it, moved from the district before the term
began. The source states that vacancy rather than falling silent about it, so it
is recorded as a vacancy and not left as an unknown.

The three seats run as follows.

- **Arlington:** W. C. Wibirt (1912–19, joining the term keyed above), Thomas
  J. DeLashmutt (1920–23), W. J. Ingram (1924–27, closing the open end above)
  and B. M. Hedrick (1928–31).
- **Washington:** Robert L. Walker (1912 to his resignation on 27 March 1919),
  Clarence R. Ahalt (appointed to the rest of 1919), the seven-week vacancy,
  then Frank Upman and W. T. Weaver, both appointed in quick succession to the
  balance of the 1920–23 term, and E. C. Turnburke for 1924–27 and 1928–31,
  closing the open end above. The article prints the name Turnburke, and the
  roster carries it (below).
- **Jefferson:** Edward Duncan throughout, as sourced above.

The article gives no race for any of them, so a member drawn from this listing
defaults to White and man like the rest of the era (`member-demographics-lists`, above)
rather than being looked into on its own. The all-White coding of 1889–1986 is
a separate question waiting on the County, and this reading does not reopen
it.

### The article as a source

**The article over 1932–1960, where three sources overlap.** The same
compilation covers 1932 through 1960, keyed in
`data/transcribed/by_claude/arlington_historical_magazine/arlhist_terms_1932-1960.csv`,
where Novack and the county's candidate history already name the Board.
Across every row the three agree on membership: the same members in the
same seats, so nothing there moves a seat-month and no figure turns on it.
Six particulars differ, and they matter because the roster is itself a work
product the County receives, not only an input to the figures. Two are facts
about a man and both are settled. Harry W. Cuppett's given name is Harry, as
the article and Novack give it against the county's Henry: the 1950 census
index and sheet
read Harry W Cuppett, as do the Daily Sun and the Sun of 1947 printing his
house at 1011 North Stafford Street (`census1950cuppett`, `tad1947cuppett`,
`sun1947candidates`), so Henry is a variant of it. And John C. Gall resigned
on 31 May 1933 rather than dying in office as the county's history has it
(below). The remaining four are labels the roster cannot state, so no source
has to win. It records months, not days, and records no chairmanships at all:
Magruder's seat ends in May 1947 whether she gave up the chair on 11 February
or 11 March, Buchholz's term begins in November 1952 whether the election was
the 4th or the 11th, B. M. Smith's 1934–35 chairmanship is absent whether or
not Novack's Acting belongs on it, and Loyd is read as Lloyd. The County's
copy follows the article for term blocks, as it does throughout, and claims
none of the four (Sally).

**How the article is read.** The article prints the Board in blocks, each
block one stretch with a settled membership and a named chairman, so a block
is not a term: the 1916–19 term is three blocks in the Washington seat,
because the seat changed hands twice inside it. `members_roster_arlhist.py`
merges the blocks where the same person holds a district across them and
cuts the result at the statutory four-year boundaries the article's own
year-blocks follow, January 1912, 1916, 1920, 1924 and 1928. A bare year
closing a block is the following January, the month the next term begins; a
printed date is its own month, so Walker's term closes in March 1919 and
Ahalt's opens there, and the handover month goes to the incoming member by
the rule in "Seat-years" below. The article records no election, so a term
begins `unrecorded` unless its note says the member was appointed.

Some of the terms are in the roster from another source as well — Wibirt's
and Walker's 1916 terms from O'Leary, Ingram's 1924 and Turnburke's 1924
and 1928 from the county's candidate history — so the article merges into
those rows rather than adding a second one, taking the end date none of the
other sources records and dropping O'Leary's sentence about a departure he
does not record. A person another source also names is matched to them by
surname; which spelling the roster then carries is settled first, in `NAMES`
in the same module, and the census records and the attributions are keyed on
it. Where the article prints a full name another source leaves short, the
full name wins: O'Leary's "Wibirt" and "Walker" become the article's "W. C.
Wibirt" and "Robert L. Walker". Jefferson is Edward Duncan throughout and his rows are emitted
like any other; `apply_duncan_join` collapses them with the rest of his
service, and checks that the rows it joins reach 1908 to 1932 without a
gap rather than counting them, since four sources name overlapping stretches
of the one seat.

`members_by_year.py` reads the roster for these years like every other year,
so 1920 counts 2 + 11/12 seats.
`members_roster.check_district_seats` holds the reading in place: each of the
three districts has exactly one member in every month from 1870 to 1931, save
the six months before the Board sat and the three recorded vacancies —
Washington from July to November 1873, Jefferson from April to June 1879, and
Washington in January 1920. The exceptions are the point: a gap anywhere else
stops the build, and so does filling one of these.

### The article corrects and adds for 1870 to 1911

The same compilation covers 1870 onward, keyed in
`data/transcribed/by_claude/arlington_historical_magazine/arlhist_terms_1870-1911.csv`,
but here O'Leary's elections sit underneath it, so it is read a
second way: `names()`, `notes()` and `early()` in `members_roster_arlhist.py`
correct what a member is called, write onto a term what the article says
about it, and add the terms no other source records. O'Leary is an electoral
history. He lists elections and their winners and names a departure only
where his prose happens to, recording five handovers in the 1870s and not one
from 1880 through 1911, which cannot be what happened; where the article
names a supervisor he does not, he is silent rather than contradicting
(Sally).

**The article dates a term from the first record of a man sitting**, not from
the instrument that named him — the minute books record meetings, not
appointments. "Hume's two dates" above works this out on the one case where
both dates survive, and Saulisbury's footnote states it outright: "[n]othing
in the record shows why Saulisbury took Pendleton's place, nor exactly when;
the meeting of 11/15/84 is the first in which he is shown as 'present.'" It
is a property of every date the article gives, not a fact about either man.

**The Board's year ran 1 July to 30 June through 1901.** Elected in November,
start in January; elected in May, start in July. Being elected is not taking
office, and the two halves rest on different things:
`members_roster_oleary.seated()` carries the November half on
`vaconstitution1902` sec. 112, and the May half on ch. 76 sec. 4 of the 1870
acts: the term of "all corporation and township officers chosen at a general
election ... shall commence on the first day of July next thereafter," and
sec. 14 of the same chapter makes a supervisor a township officer, chosen at
the May general election (`vaacts1870`). Every term block
the article prints for 1870–1901 runs 1 July to 30 June. Its own footnote at
1901 corroborates the arithmetic. The 1902 constitution moved the Board to
four-year calendar terms, and "the extra six months of this Board covered the
transition period" — a term running 1 July 1901 to 31 December 1903, which is
thirty months on a July–June year and thirty-two on a May one. `BOARD_FROM`
moves with it: the Board elected in May 1870 first sat on 1 July, so the three
seats are empty for six months of 1870, not four.

The article prints "township" through the block ending 30 June 1874 and
"district" from 1 July 1874 on, four months before the amendment was ratified.
The roster says districts throughout, and that is correct, not a
simplification: ch. 76 sec. 1 of the 1874–75 acts, approved 5 February 1875,
declares the townships as they stood on 3 November 1874 to be the magisterial
districts, keeping their boundaries, names and voting places, and ch. 69 sec. 1
directs that "township" in any earlier statute be read as the district
(`vaacts1875`). Same lines, same three names. The townships began with the 1869
constitution and did not predate 1870, so nothing is carried back across a
boundary change that never happened.

**Names the article settles.** Each is an entry in `NAMES` in
`members_roster_arlhist.py`, applied before anything matches on a name, and
the renamed rows carry a note saying what settled it. A variant not in that
table has not been ruled on.

- **Frederick S. Corbett**, one man across all his terms. O'Leary gives surnames only
  from 1907, so he names the Arlington member of 1908–11 by surname alone,
  apart from the Frederick S. Corbett of 1889–91, 1895–97, October 1897–99 and
  1899–1901. The article gives every one of them the same full name from the minute
  books, and the censuses agree on a birth year: the 1880 sheet an age of 24,
  the 1910 sheet 1856. No figure turns on it — a White man either way, and
  `members_age` starts at 1932 — but the two census rows keyed "Corbett" and
  "Frederick S. Corbett" describe one man and agree on the year. - **Francis G.
  Schutt**, one man. Three sources give three middle initials — D in O'Leary, G
  in the minute books, C in the Alexandria Gazette of 6 December 1875
  (`gazette1875schutt`) — and an initial that unstable cannot be what
  distinguishes two people. The seat passes from his July 1873 appointment to
  his May 1874 election with no gap, and his is the only Schutt household in
  the county in 1880 (`census1880schutt`). The 1873–74 Arlington terms carry
  that census match rather than race `assumed`. - **James C. Roach** (Jefferson, 1870), **W. C. Wibirt** and
  **Robert L. Walker**: a bare surname in O'Leary, named in full by the minute
  books. - **Saegmuller**, not Saegmulller. The article, the 1880 sheet and the
  1900 sheet all spell it with two; O'Leary's third l is a typo on its face. -
  **Turnburke**, not Thornburke. The Gazette prints "Turnburke" in 1923 and no
  "Thornburke" anywhere in its run (`gazette1923turnburke`), agreeing with the
  minute books and the 1920 census index and sheet against the county's
  candidate history and Novack. Those two print a recorded variant of the name
  rather than the name. His identity is not in doubt: read as two men the
  Washington seat double-fills and `check_district_seats` refuses the build.

Two spellings of the same shape are settled, and they fall opposite ways.
**Birch**, not Birth: the article, the 1900 census index and its sheet all
read Birch against O'Leary alone (Arlington, 1891–93), so `NAMES` carries the
entry and the roster reads Millard F. Birch. **Perkins**, not Perkin: here
O'Leary and the 1880 census sheet agree against the article, and the sheet
ties to the man by his district and by the postmastership that cost him the
seat (`census1880squier`), so the roster already spells him Perkins W. Squier
and the ruling leaves no entry to make.

**Terms the article adds**, taken as one set with those it supplies
for 1912–1931 (Sally).
Each is an entry in `ADDED`, and every date is read off the article's blocks
rather than written into the table:

- the term begins with the first block naming the man;
- it runs to the end of the last block he holds without a break, or to the
  month the roster's next term in that seat begins, whichever comes first;
- the man whose block precedes his has his own term cut to that block's
  printed end.

| member | district | from | O'Leary gives the term to |
| --- | --- | --- | --- |
| Francis M. Mills | Jefferson | 15 August 1881 | Travis B. Pinn |
| Curtis B. Graham, Jr. | Arlington | 1 April 1884 | Perkins W. Squier |
| George W. Saulisbury | Jefferson | 15 November 1884 | John W. Pendleton |
| Frank Hume | Jefferson | 13 November 1888 | Tibbett Allen |
| William N. Febrey | Washington | 1 July 1892 | Walter G. Willson |

A further departure the article states is the same ruling applied to a vacancy,
not a successor: **William A. Rowe resigned the Jefferson seat on 2 April
1879**, having moved into the Arlington District, and it stood empty until
Travis B. Pinn's term began on 1 July. That is `VACATED` in the same module,
and `members_roster.VACANT_1879` reads the empty months straight off it, so the
cut and the vacancy cannot drift apart. The article also opens blocks of a few
days between an outgoing and an incoming member — Arlington, 5 to 25 June 1877
— and on a month grain those are one handover, not a vacancy; the month stays
the unit, and no member's whole service in the article is shorter than a month.

**Where these readings bear on the central figure.** Some of them shorten a
Black member's recorded service, and each is stated above:

- the added terms close Pinn's, Pendleton's and Allen's mid-term, where
  O'Leary's elections would run them out;
- the July term year moves a start off May in each year a Black member's
  service begins, 1871, 1872, 1879 and 1887;
- Rowe's resignation stands the Jefferson seat empty from April to June 1879. Reading
O'Leary's elections alone would give every one of those months to a sitting
member. `members_by_race` counts what the roster holds, and no count of it is
kept here.

**A contested election seats the man who sat.** The Arlington District election
of 1897 gave A. D. Torreyson and Frederick S. Corbett 209 votes each on the
first count; the county court found for Corbett and declared him a member from
1 July, by which time Torreyson had been sitting, and he sat on until 11
October (`arlhist1967officials` p.42). Both men have a claim on the same
fourteen weeks, the only term of its kind in the roster. The roster records who
held a seat, not who held title to it, so Torreyson holds it to 11 October 1897
and Corbett from then, and the court's finding is a note on both rows, not a
second term (Sally). A man who sat and voted on the Board
was a member of it whatever a later judgment says he should have been.
Recording title instead would either seat two men in one seat for fourteen
weeks, which `members_by_year.py` refuses, or delete a member the minute books
show sitting.

#### Two seats go to the man the minute books show sitting

The article gives
two seats to someone other than the man O'Leary seats, and the roster follows
it in both (`SEATED` in `code/clean/members_roster_arlhist.py`). The Jefferson
seat of 1870 is empty, not Storm V. Boyd's: the article prints the supervisor
elected for the township as having failed to qualify, and O'Leary gives him the
seat on the election return alone, so the seat stands vacant from 1 July until
James C. Roach's appointment that September. The Washington seat of 1897–99 is
George N. Saegmuller's, not A. B. Grunwell's, so Grunwell's service ends with
his 1895–97 term. The ground is the one Torreyson's fourteen weeks settled: an
election return names the winner and the minute books name the man who sat, and
the roster records who held a seat, so where the two disagree about occupancy
the minute books answer the question the roster asks (Sally). Boyd's 1870
census record (`census1870boyd`) places the man and is not a
claim about a member, since he never was one. The article's William N. Febrey
of 1892–93 keeps his own roster row, by the article's own typography, though
the census settles him as the same man as the W. N. Febrey of 1904–11
(below, "W. N. Febrey is one household"); there are three Febreys in the
roster.

**Two readings are written onto the terms they land on**, in `READING_NOTES`
in `members_roster_arlhist.py`, because the roster has to say them on the term
itself: Walker's end date, and which man the 1920–23 DeLashmutt term belongs
to (below). Neither changes a figure, since the seat is filled either way and
every member of this era defaults to White and man.

- **Walker's end date.** The article has him
  resigning on 27 March 1919 to become the county's Sanitary Inspector, and
  Ahalt appointed to the rest of the term. O'Leary records no departure, so
  his 1916 term would otherwise run to January 1920 by statute. The article is
  the minute books and names the day, so its date is taken. The reason is
  corroborated: Walker's 1920 census sheet reads occupation Inspector, industry
  Sanitary, on Chain Bridge Road in the Washington district
  (`census1920walker`), so he did take the post. The day and the appointment
  rest on the article alone. The Alexandria Gazette prints neither, though it
  puts Ahalt in the district that year twice over — elected on 4 November over
  W. H. Payne, 241 to 204 (`gazette1919ahaltelected`), and assuming office on
  New Year's Day (`alexandriagazette1919duncan`). Wibirt's term is
  the same shape a month apart: the article closes it 31 December 1919 where
  O'Leary's statute would close it that January.
  The Washington Evening Star for spring 1919 has not been searched. It could
  confirm the day but not move the seat, so the article's date is settled.

**Most of the 1912–1931 members the article adds are settled to the
census.** Thomas J. DeLashmutt, Frank Upman and W. T. Weaver each match a
single, unique household in the right district in the 1920 census, read off the
sheet (`census1920delashmutt`, `census1920upman`, `census1920weaver`); B. M.
Hedrick, whose term runs 1928–31, is **Benjamin M. Hedrick**, an attorney in
the Glenarlyn subdivision of the Arlington district in the 1930 census
(`census1930hedrick`) and is in no 1920 index for the county under that name.
All four read White and male from the sheet, so they rest on a record, not on
the era default (`member-demographics-lists`). **Clarence R. Ahalt** is in no 1920
census index for the former Alexandria County under that name or a close
spelling (the county-wide search, 32 nationwide results, none local, is
recorded so a later thread does not repeat it), but he is in the 1930 census
(`census1930ahalt`): an attorney on Mt. Vernon Boulevard in the Jefferson
district, 41, born in Maryland, the only Clarence R Ahalt in Virginia that
year, which fits the 1933 letter (below, "The members that keep the default")
naming him an Arlington County man of twenty years' residence. The record
gives him White, a man and a birth year, 1889 within a year.

Thomas J. DeLashmutt's household carries a son, **Basil N. Delashmutt, 17**,
born about 1903 — the same birth year as the **Basil M. DeLashmutt** of the
1932–1962 cohort's 1930 match (`census1930delashmutt`, `residence-1932-1962`),
a 27-year-old civil engineer. The two Basils are the same man
(Sally): Thomas J. DeLashmutt's son, not the 1920–23 Arlington
member himself under a variant reading. The census row's `basis` and match
carry the family tie (`occupation; household`), which is why
`residence-1932-1962` does not count him among its weak matches.

### How each source is cut into terms

**Mid-term handovers are terms like any other.** O'Leary records them as
prose beside the elected member ("Replaced by H. Dwight Smith in Dec.;
replaced by Lott W. Crocker in March 1873, replaced by Francis D. Schutt in
April"), and those are parsed into their own rows: the Arlington seat in
1872–73 is a term for each man. Where a month is given without a year, the year carries
from the previous handover and rolls forward when the month goes backwards.
Francis D. Schutt holds two consecutive terms in 1873, appointed in April and
elected in May; that is two terms, not a duplicate. From 1907 O'Leary gives
surnames only, so "Corbett" from 1907 is a different person in the roster from
"Frederick S. Corbett" before it and starts again at term 1. Corbett and Duncan
appear under both forms; joining them needs a rule (surname plus
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

**Gall resigned; he did not die in office.** The
Historical Society's article for 1932-1960
(`arlington_historical_magazine/arlhist_terms_1932-1960.csv`, keyed the same
way as the 1912-1931 stretch above but not read into the roster) and
Novack both print John C. Gall's term as ending in a resignation, 31 May 1933.
The county's candidate history alone calls it a death in office. The two
agreeing sources are the Board's own minute books, and the roster carries the
resignation from Novack (`novack1994`, source column), so no value in
`members.csv` rests on the county's version.

The press was searched and carries nothing. The Evening Star (Chronicling
America) prints no obituary, death notice or successor-appointment story naming
him, either around his departure or later in 1933, under several searches on his
name, on "Aurora Hills" and on Benjamin M. Smith's appointment to the seat. The
Washington Post for the same weeks is ProQuest, which neither Claude nor Sally
can reach.

Gall is instead demonstrably alive afterward, in three records:

- a ship's manifest has him landing in New York on 28 November 1934, married,
  eighteen months after the county's dated death (`passenger1934gall`);
- a Fairfax County World War II draft card registers him at 41 on 16 February
  1942, next of kin "Elsie J Gall" (`draft1942gall`);
- a Find a Grave index entry gives his death as 13 December 1957, at Ivy Hill
  Cemetery in Upperville, Fauquier County (`findagrave1957gall`).

All three share his exact birth date, 1 February 1901, with `census1940gall`.
The draft card and the grave record share his parents' and his wife's names with
a 1924 Herndon marriage record (`marriage1924gall`): John (Jacob) Gall and
Bertha Gall, and Elsie G. Rosenberger / Elsie Grafton Gall. The county's own
work product, not the Board's minute books, is the one in error.

**From 1995 a term is built from election results.** A November win starts a
four-year term the following January. A special election fills the rest of a
term that ended early. The member who left is closed at that month, and the
winner serves until the seat's next regular election. Where two members' terms
end in the same year, the county's own annotation ("to fill Eisenberg's
unexpired term") says whose seat it was, and the build refuses to guess when
that annotation is absent. The five people still serving when Novack published have their last
term closed the same way. A check runs every month from 1995 through 2026:
five members at large, six only in a month a special election changed hands.
The county and state sources both hold the 2021 election, and the build
insists they name the same winner there before using the second.

**Recorded vacancies.** Counting the months each term covers against the seats
that existed finds these:

- the Washington district seat, from the May 1873 election until Samuel Titus
  was appointed that December;
- March and April 1990, between Milliken's resignation and Hunter's special
  election;
- the Washington seat again, from 1 January to 20 February 1920 (above).

The month is the unit, so the seven weeks of the last count as January alone,
and 1920 holds 2 + 11/12 seat-years.

## Seat-years

`data/clean/members_by_year.csv` is one row per year from 1870: seats
held by each race, each gender and (from 1932) each party, in seat-years, so a
member who sat for four months of a year counts 4/12. Every year is computed
from `members.csv`. Days are not recorded consistently — Novack gives some and
the election dates others — so the month is the unit, and **the handover month
belongs to the incoming member** (Sally). An end no source
records holds to the end of the term's first year. Both rules are applied once,
in `held_from` and `held_to` on `members.csv`; the seat-years and the figures
of who was sitting on 1 July read those columns, not the dates.

The denominator is the months the Board existed that year, which is twelve for
every year but its first. Arlington's Board came into existence at the May
1870 election, so 1870 is scaled by the eight months it existed: it reads
three seats filled, because they were, for as long as there was a Board to
fill them. Divided by twelve it would read two, and a chart of that says the
Board grew from two seats to three, which it did not.

The seats held can never exceed the seats that exist: three magisterial
districts with one supervisor each from 1870, and five members elected
countywide from the County Manager plan, which the November 1931 referendum
adopted and which seated its first Board in January 1932. The seats held fall
short only in 1873 and 1990. Anything else stops the build. Race, gender and party are independent splits of the same
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

## The chair

The Board elects its chair and vice-chair from among its own members at its
first meeting of the year, which the roll dates to the first days of January
(`arlingtonva2026members`). The statute, `vacode2020chairelection`, enacted in 1997,
lets a governing body set the officer's term, makes it one year where none is
set and allows successive terms, so nothing in law gives the chairship to a
member in the year the seat is up. `data/clean/members_chairs.csv` holds the
chair of every year from 1932 and the vice-chair from 1967, read off the
county's roll (`arlingtonva2026members`), and the table is kept out of
`members.csv`, where every row is a term.

**The custom is succession, not the ballot.** The ARLnow report of the January
2026 meeting says the new vice-chair, Maureen Coffey, "will rotate in as chair
in 2027, assuming all goes as is typical" (`arlnow2026chair`). Since 1990 the
roll bears that out: each year's vice-chair is the next year's chair, and the
four breaks each have a reason in the Board's own membership. James B. Hunter III took the chair
in 1996 ahead of Ellen Bozman, the vice-chair, who took it in 1997; Charles Monroe, vice-chair
in 2002, left the Board in January 2003; J. Walter Tejada's term ended in
December 2015; and Erik Gutshall, vice-chair in 2020, left the Board that April.
Between the first vice-chair in 1967 and 1989 the vice-chair was often passed
over: A. Leslie Phillips and Jay E. Ricks held the office and never chaired.

The test the custom was first put as, that a member chairs in the year the
seat is up, fails. Jay Fisette chaired in 2010 and 2014, each the first year of
a term he had just won, and Katie Cristol in 2018 and 2022, the third year of
hers. The five-member Board gives each member a turn about every fifth year
whatever the election calendar says, and the long gaps, Bozman from 1976 to
1983 and Whipple from 1986 to 1994, are members the order skipped over, not
members waiting for a ballot.

Before 1967 the roll names no vice-chair and the chair changes almost every
year. The years that break the pattern are the Board's own crises: Lyman
Kelley was removed in November 1934, a court removed the chairman in September
1952, Elizabeth Magruder resigned the chair in March 1947, and Eisenberg resigned
his in February 1999. Magruder alone chaired three years running, 1938 to 1940;
Harry Fellows, Wesley Cooper and Bozman chaired two. No source found reports a
chair election contested on the floor: the County's releases and ARLnow for 2025
and 2026 report none, and the press before them is unread (ProQuest).

Members of colour who served a full term took the chair in turn: William
Newman in 1991, the fourth year of his first term, Walter Tejada in 2008 and
2013, Christian Dorsey in 2019 and 2023. The members who never chaired are those
the order never reached, the part-term members, among them Gutshall and Monroe,
each of them vice-chair when they left.

**A figure of chair-years by race and gender is not built.** Because the chair
follows the vice-chair, who follows the order of the Board, chair-years by race
and gender would repeat the seat-years figures with a year's delay. The report
can state the first Black chair, Newman in 1991, and the first woman to chair in the roll, Magruder
in 1938, in a sentence of prose.

## Where members lived

`data/clean/members_residence.csv` holds one row per claim about a member's
home: the place as the source names it, how exactly (`precision`: a street
address, a street name, a neighborhood, a side of the County or a
magisterial district), the year the source gives, and the source. Nothing is
coded North or South and no claim is chosen over another; the coverage
figure takes each member's most exact dated place in each year.

**How much is known, for the members first seated from 1932 on.** A member
is counted under the most exact kind of place any source gives him, and dated
by the best-dated row of that kind: during service if the row's year falls
inside a term, otherwise by the distance to the nearest term's ends. Every
census read moves these numbers, so the count is not kept by hand:
`test_the_residence_coverage_table_in_the_write_up_is_current` in
`code/tests.py` recomputes it from the clean tables on every build and fails
with both sets of figures when the table below stops matching.

| Most exact place held | Dated during service | Within 5 years of it | 6 or more years from it | Undated | Members |
|---|---|---|---|---|---|
| Street address | 14 | 19 | 8 | 0 | 41 |
| Street name | 2 | 0 | 1 | 0 | 3 |
| Neighborhood | 10 | 0 | 4 | 2 | 16 |
| Side of the County | 1 | 1 | 0 | 0 | 2 |
| Nothing | | | | | 14 |

So most members have a place of some kind and many a street address, but
only a minority are placed by a source dated to their service. The
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
trait from it rather than each trait being keyed separately. The table holds
records from the 1870, 1880, 1900, 1910, 1920, 1930, 1940 and
1950 schedules. Its columns:

| Column | Holds |
|---|---|
| `name`, `source` | the roster name and the record's citekey, `census<year><surname>` |
| `year` | the census year |
| `basis` | what ties the record to the member, stated once: the name, the place, and an occupation, a spouse or a house number where one agrees; where the index misreads a name, what it reads |
| `match` | what ties the record to the member besides the name, from a fixed list, several joined with `; `: `district` (the district he sat for), `occupation`, `household` (a spouse or child another source names), `address` (a house or street a newspaper also prints), `unique` (the only person of the name in the county's index that year), or `none`. Blank where no one has yet read the record for a tie |
| `checked` | what was read against the image: `read against the sheet, which agrees`, or what the sheet gives where it differs from the index. Every row names the sheet; see "Reading an image" |
| `gender`, `race`, `age`, `birthplace`, `occupation` | as the index prints them: `Male`, `Mulatto`, `39` |
| `birth_year` | a birth year the index prints as a date, not as its `abt` estimate from the age (the 1900 schedule records a month and year); blank otherwise |
| `place` | the street and house number as read for residence, from the sheet where the sheet was read; blank where no one has read it for that purpose |
| `quote` | the index listing verbatim |
| `sheet` | the sheet's lines verbatim, where they were read |

A name alone with nothing else in agreement is no match. A row whose
`match` is `none` stays in the table, so that the search and the reading are
on record, and gives the member nothing: no birth year, race, gender or
place, which then fall to the default or to the member's other sources
(Sally). A blank `match` has not been read for a tie
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

One record is filed and cited but kept out of the
table, since it gives a birth year that disagrees with the member's other
record and the build stops on two sources disagreeing: William Duncan's 1910
record (`census1910duncanwilliam`, 1857 against the 1900 record's August
1854). Which year is Duncan's is open (`duncan-birth-year`); the row is added
when it is settled. His death is filed (`alexandriagazette1910duncan`): killed
by a freight train in the Potomac railroad yards early Saturday night, 8
October 1910, his survivors (a widow, four sons and one daughter) matching
`census1900duncan`'s household exactly and confirming the deputy marshal and
former supervisor as the Jefferson-district member. The notice's own age,
"about forty-five," agrees with neither census record and is too imprecise to
arbitrate between them.

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

**The 1892–93 William N. Febrey is this same man.** No William or W. M.
Febrey besides him appears in the county's 1880–1930 census record, so the
29-year-old son in Henry W. Febrey's 1880 household — the only candidate
the record offers — is who held the Washington seat a Febrey son would be
expected to hold, twelve years on, at 41. His age in 1880 puts his birth at
1851, within a year of the November 1851 the 1900 schedule prints, the two
census readings of one record agreeing rather than conflicting. The
Alexandria Gazette's notice of 10 October 1893 (`gazette1893febrey`), naming
a "Mr. W. N. Febrey" elected chairman of the county Republican committee
mid-way through the 1892–93 term, places a man of that name in county
politics at the right moment, though the notice alone ties on name only.
There is no 1890 census to check him against directly, and no source
distinguishes a second Febrey; the question is settled one man, not two.

**Edward Duncan held Jefferson continuously from 1908 to 1932, one term, not
four.** He appears in three sources under three names, "E. Duncan" (1908–12),
"Duncan" (1916–20) and "Edward Duncan" (1924–28), and O'Leary's and the
county's own records give an election for 1908, 1916, 1920 and 1924 but nothing
for the two four-year cycles between them, 1912–16 and 1920–24. The Alexandria
Gazette fills both gaps: he is named chairman of the board of supervisors in
three pieces spanning May 1913 to December 1915 (`alexandriagazette1913duncan`,
`alexandriagazette1914duncan`, `alexandriagazette1915duncan`), an explicit
December 1919 notice re-elects him for a term starting January 1920
(`alexandriagazette1919duncan`), and an October 1921 piece still names him a
sitting member, with leadership by then rotated to Frank Ballenger
(`alexandriagazette1921duncan`). He did not run again in November 1931: a
Washington Times election wrap-up has him a distant third in the sheriff's
race, "considered [the] most formidable rival because of his 24 years'
experience on the county board of supervisors" (`washingtontimes1931duncan`),
naming the same 24 years as his October 1938 obituary (`star1938duncan`; the
Washington Times's own notice the next day, `washingtontimes1938duncan`, names
the same figure). Twenty-four years back from a term ending January 1932
is 1908 — his first election. This is one term, not one row per election
(Sally): 1908, 1916, 1920 and 1924 are each a sourced
election win; 1912 and 1928 are known only because he is shown in office both
before and after each, not by a recorded win in either year, so the roster
cannot say those two renewals were contested.

The two census records that place him, `census1910duncan` (Jefferson, an
engineer, a one-year-old son Morton) and `census1920duncan` (the same household
ten years on, Morton now ten, the same trade and Irish parents, "the only
Edward Duncan in the county that year"), independently confirm one man, not
three, and his race and gender attach from both. They disagree on his birth
year, though — 1872 by the 1910 sheet's age, "abt 1870" by the 1920 sheet's,
neither a printed date — so both are named in `AGE_MISREPORTED`. His birth
year, 1867, is the obituary's: the Evening Star's death notice and news story of
10 October 1938 give him aged 71 at his death on 9 October, the notice naming
his wife Katie I. and a son Morton, as the censuses do; the Washington Times's
own notice and "Duncan Rites Wednesday" piece the next day
(`washingtontimes1938duncan`) give the same age independently, and his Ivy
Hill Cemetery footstone, photographed for his Find a Grave memorial
(`findagrave1938duncan`), is carved "EDWARD DUNCAN, 1867 :: 1938" - a fourth
source for 1867, naming no day or month, beside the same wife and children.
That is three to five years earlier than either census age, and nothing
arbitrates, so the census records stay excluded and the year is 1867.

The Historical Society's article names him in the Jefferson seat in every one
of its blocks from 1912 to 1931, which is the minute books' own confirmation
of the continuity the Gazette pieces establish; it is cited on the joined term
with the rest.

The filed copy of each record's Ancestry page is written by
`code/sources/ancestry.py` from the row's own `quote`, since Ancestry refuses an
automated request and the page cannot be fetched by anyone reading this
repository. The page says on its face that it is derived. It does not repeat
Ancestry's statement that the facts in the collection were found using
artificial intelligence and may contain errors, since the 1930 and 1940 census
record pages carry no such statement. The one page the script does not write
is William Duncan's 1910: the record is cited but kept out of the table while
`duncan-birth-year` is open, so there is no row to build it from, and the
script says so each time it runs.

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
because the records are few and the cost of a wrong one is silent.

`code/build/members_claims.py` enforces the half of that rule a machine can
check. A row whose `checked` names neither the sheet nor the index stops the
build, and so does a `place` on a row the sheet was never read against, since
a street is the field the index gets wrong. `code/tests.py` reintroduces both
mistakes.

For a page read through OCR — a newspaper claim in `members_residence.csv` —
the quoted sentence is read off the page image before the row is written, and
any house number in it is read off the image, never off the OCR. Rows entered
before this rule are cleared a page at a time, whole pages, not a sample of
rows, since opening the page is the cost and the rows on it are then free.

That reading has found one wrong value. Across the census records that
had only ever been indexed, and the newspaper pages carrying quoted addresses,
the error is this: Detwiler's
1940 sheet gives his birthplace as **Minnesota** where the index reads
Wisconsin, and spells the surname Detwiler, as the Board member does, where
the index reads Detweiler. Birthplace is not a column the build reads, so no
figure turns on it. Two smaller disagreements need no fix: the index's street name
for Buchholz, `1`, is a column number and not a street; and Byrne's sheet
gives 202 N. Highland St., which the *Daily Sun* of 11 September 1952 prints
as well. A third is settled below. The figures keyed from the 1870, 1880
and 1890 volumes and the whole of the POP-TWPS0076 Arlington block agree with
the printed pages.

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

**The pre-1912 sheets, read twice.** Six fields the
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

**Phillips's household is his father's.** What settles the 1900 household is a
source outside the sheet, not a third reading of the same smudge: an 80-year-
old father-in-law named Andrew Barbour and a daughter Margueritte born about
1889 are unusual enough to search on directly. WikiTree's profile for Robert
Augustus Phillips (`wikitreephillips2024`), compiled from Find A Grave and the
census, gives a birth of 14 Jul 1833 in Dryden, Tompkins Co., NY, matching the
sheet's birth date and birthplace exactly, and a marriage to Mary Imogene
Barbour on 27 Dec 1880, matching the sheet's spouse and marriage year; its own
sources cite this same 1900 record, roll 1698, page 10, ED 3, as his. The
household is his, and the second reading, **A**, is right. It is not the
member's: Robert Augustus had an elder son by an earlier marriage, a distinct
man named Robert Henry Phillips (1865–1942), who does not appear in the 1900
household. The sheet puts Robert Augustus in the Washington district of
Alexandria County, the district the member sat for, which is what makes the two
men easy to confuse; what separates them is the roster's middle name, Henry,
against the sheet's A. He married in Washington, D.C. in 1880 and died there in
1912. So `census1900phillips` has `match` `none` and gives R. Henry Phillips,
the member of 1893–95, nothing: his race (**White**) rests on the default, as
it does for every member before 1912 except Roach, and he has no residence
claim at all, standing with the members for whom no census record has
been found (`residence-pre-1932`). Robert Henry Phillips himself is in no
record found for Alexandria County or Arlington; if one turns up later, it is
the one to try, and his father's household in the Washington district is a
reason to look there.

**Members the census places, not the era default.** The censuses of the years
each served were searched for every member whose gender rests on the default,
and these carry a record, and with it a gender, a race and a birth year read
from a source: **B. M. Smith** (below); **Edward Duncan**, of Duncan Lane in
the Jefferson district, the household of `census1910duncan` ten years on by his
son Morton, his trade and his Irish parents; **W. J. Ingram**, a hardware
salesman at 204 Virginia Ave in the Arlington district in 1920, whose widow
Julia keeps the house in 1930 with their son William; and **E. C. Turnburke**,
whom the sheet and the index both call Eugene C. Turnburke, a house painter at
35 Preston Avenue in the Washington district. Storm V. Boyd's 1870 sheet reads
the same way — a farmer in the Jefferson township, its middle initial B where
the roster gives V, so the match rests on the district — and it is no row in
the table, because he never sat (above, "Two seats go to the man the minute
books show sitting").

**Some members rest on a press honorific**, the census holding nothing for
them. The Alexandria Gazette (Library of Congress, Chronicling America),
searched by name and district over each member's term, carries a contemporary
honorific for these: **H. Dwight Smith** presided over an 1873 meeting of the
Arlington Republicans as "Captain H. Dwight Smith" (`gazette1873smith`);
**Lott W. Crocker** is "Mr. L. W. Crocker, President" of the Arlington
Turnpike Company the same year (`gazette1873crocker`); and a Board of
Supervisors meeting of 6 December 1875 has "Mr. Rowe nominated Mr. Vanderberg
for chairman, but upon his declining, Mr. Schutt was unanimously re-elected"
(`gazette1875schutt`) — that piece names him F. C. Schutt of Jefferson,
read against the only Schutt household the county's 1880 census holds
(`census1880schutt`), the same one the roster's Francis D. Schutt of
1873–74 and Francis G. Schutt of 1874–81 are read against.

The same line swaps both men's districts: it puts Schutt in Jefferson and
Rowe in Arlington where the minute books and O'Leary both have Schutt in
Arlington and Rowe in Jefferson through 1877. It is read as a transposition
and yields no residence claim. The reading that would rescue it — that the
paper named where each man lived rather than the seat he held — asks both
men to have moved years before the Board acted, and the Board did not wait:
it took Rowe's resignation on 2 April 1879, the day it recorded his move
from Jefferson to Arlington, and Schutt's in June 1877 on the notation that
he had moved from Arlington District. Each was still living in the district
the roster gives him in December 1875. Where the two men lived is a claim
those notations can carry, and this line cannot (Sally).

**Wibirt and Walker take a census record once the Gazette gives their full
names.** The Gazette calls the Arlington-district supervisor "W. C." or
"William C. Wibirt" — a nominee for the seat in October 1915, a pallbearer in
1918, and the county's assessor of 1910 named again in 1921 — and its election
notice of 30 October 1915 gives Walker's full name, "Washington district, W. T.
Weaver, Robert L. Walker," among the nominees for supervisor
(`gazette1915wibirtwalker`). Neither piece attaches a pronoun or honorific to
either man, and on a surname alone neither can be told from his namesakes: the
Arlington district holds two Wibirt households in 1920, William C. and
Clarence. Searched on the full names, the census ties a record to each:
**William C. Wibirt**, the older of those two households (born about 1855,
against Clarence's born about 1865), alone in his household, his occupation
reading "none" on the sheet, so nothing beyond the name and the district favors
the assessor the press names over any other William C. Wibirt
(`census1920wibirt`); and **Robert L. Walker**, the only Robert L. Walker
keeping house in the Washington district that year, an inspector in the
sanitary trade, with his wife Annie and six children (`census1920walker`). Each
gives a man, a race (White) and a birth year (1855, 1876) from the census, not
the default.

### The members that keep the default, and what has been searched for them

These do, and both have been searched past the Gazette into every Virginia
paper Chronicling America and Virginia Chronicle hold, so that nobody repeats
the search. **William H. Robinson** appears in the Gazette once, named
plainly among the Board of Supervisors of 18 September 1878, with no pronoun
or honorific attached to him; a full-text search of both sites for "William
H. Robinson" in Virginia, 1877-79, turns up nothing else - every other
Robinson the papers print in those years (a Richmond coal committee, a King
George visitor, a deceased tailor) is a different man. **Walter G. Willson**
turns up only as a Harvey Willson unrelated to him and, on the same two
sites for 1888-94, as bare initials in a road-fund ledger line - "W G
Willson as member road board," a fee paid, Alexandria Gazette, 22 October
1891 - with no honorific attached. **Clarence R. Ahalt**, a third member
once kept on the same default, is sourced instead: a 4 November 1933 letter
to the editor in the *Commonwealth Monitor*, urging his election as
Attorney General, calls him "Mr. Ahalt" three times and "an Arlington
County man" (`commonwealthmonitor1933ahalt`). He remains a recorded
negative in the 1920 census, 32 nationwide results checked, which the press
reading and the 1930 census record (above) now make moot. **Edward Duncan** has no record
after 1920: Arlington County holds no Duncan of his age in 1930, so the 1920
sheet is the later of his two.

**Smith, Crocker, Robinson, Willson and Phillips have no birth year, and two
have a place.** No record found gives any of the five an age, so none enters
`members_age` before 1932 (`age-pre-1932`).

- **Willson** is printed Walter G. Wilson: "Walter G. Wilson, of Washington
  District" at the Board's meeting of 10 June 1890, where he is authorized to
  have the Pimmit Run bridge near Chain Bridge repaired (`gazette1890wilson`).
  His place is the six acres "near Wunder's cross roads, about one mile north
  of Ballston" sold in 1894 under a deed of trust of 20 April 1892 by Walter G.
  Wilson and Mildred A., his wife, "the same land formerly owned by Walter G.
  Wilson" (`gazette1894wilson`). The notice names no district, so the row
  rests on the widow: the Gazette has the Washington district supervisor "W. G.
  Wilson, colored" dead by 5 July 1892 (`gazette1892wilsondeath`) and the
  county court granting administration on the estate of Walter G. Wilson to
  "his widow, Mildred A. Wilson" on 5 September (`gazette1892wilsonestate`),
  the wife of the deed, and the land is "formerly owned" two years on. The
  Gazette's other full-text hits on the name are the 1894 sale notices and a
  Philadelphia bakery. No item gives an age or the day of death; a census,
  will or burial naming Mildred A. is the way to one (`willson-race` has the
  race question).
- **Smith** chaired the Arlington township Radicals' meeting of 25 May 1874 and
  sat on its township committee (`gazette1874smith`), a party office that
  places him in the township and says nothing of a house; his row says so.
  He was elected president of the Arlington Turnpike Company in July 1875,
  when Crocker, its president, was ill (`gazette1875smith`). A deed of trust of
  2 July 1877 from "H. Dwight Smith and wife" covers sixty-five acres near the
  Columbia turnpike's junction with the road to Alexandria, "now and lately in
  possession of Samuel Cochrane" when it is sold in 1887 (`gazette1887smith`);
  land he held is no residence, so it is no row.
- **Crocker** is "Lott M. Crocker" on a committee of 1870 to view a county
  road with S. B. Corbett (`gazette1870crocker`) and the Arlington Turnpike's
  president in 1873 and 1875. Every item is a county or turnpike office; none
  gives a house or an age.
- **Robinson** is a "W. H. Robinson", initials only, with 87 votes against W.
  A. Rowe's 184 for Supervisor in the Arlington District in the county returns
  of 1879 (`gazette1879robinson`). The seat places nobody, so it gives no row.
  A J. H. Robinson stands for justice in the same returns.
- **Phillips** is paid as a member of the Board in the accounts for the year
  to 30 June 1895, with mileage of 60 miles against Hume's 36 and Clark's 54,
  and the same accounts pay an "R A Phillips" 203.50 for stone
  (`gazette1895phillips`). Robert Henry Phillips, who is "R. Henry" in the
  record of the 1900 household's elder son, was born 21 January 1865 in
  Georgetown by the *Evening Star* obituary of 10 March 1942 and in May 1865
  in Arlington by Find a Grave, and died in Washington on 9 March 1942, a
  trolley-line engineer and Lehigh graduate of 1887. Nothing in either puts
  him on the Board, so no birth year is entered.

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

**Ames, 1940.** Sheet 21B, read at full resolution,
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

Birth years come from the same files as race and gender, one row per source,
and reach `members.csv` as `birth_year` with a source and a note. With no
source the year is blank and `unsourced`, because no standing assumption stands
in.

Two kinds of source give a year. A census listing gives an age, and the year is
the census year less the age, so it is right to within a year — except where
the index prints a birth date. An obituary or a profile gives a birth date, or
an age on a date, and the row's basis says which.

`birth_year_precision` in `members.csv` records which case a row is, `exact` or
`within a year`; most are within a year. The age figures draw both the
same way, as a stroke assuming a mid-year birthday, because the half-year is
below what a stroke can show (Sally). What the report
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
| 1870–1888 | Five Black members named by Hjerpe (2021): Rowe, Syphax, Pinn, Pendleton, Allen. Pinn, Pendleton and Allen each rest on a reproduced 1880 census image; Rowe and Allen on narrative statements in her paper; Syphax on O'Leary, who writes that his photograph shows he was African American. The sentence naming the five as a group sits in her own list of open inquiries, and the file records it as such. O'Leary adds that "a majority of the early office holders" were probably African-American but cannot name them. Nobody on our side has checked the census linking. | Names in O'Leary; two before 1912, Robinson and Willson, still rest on the default (above, "What rests on an assumption"). |
| 1889–1930 | One collective sentence: the board "became and remained all white for the duration of this system" (Hjerpe 2021, p.4), sourced to the county's election records. No per-person evidence. | Names in O'Leary; initials only before 1912. No source names a first woman member, so "all men before Magruder (1932)" is assumed. |
| 1931–1986 | Nothing per-person from any source, except that the county's list of the November 1931 candidates marks three of its 51 names "(Col)" and none of the five elected (`docs/candidates.md`, "Black candidacies"). The default rests on Newman (1987) being described as the first Black member since Reconstruction. **The weakest stretch.** | Census listing or a press honorific or pronoun for all but B. M. Smith (1933). |
| 1987–present | Per-person: Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), and Tejada as the first Latino member (Hjerpe 2021). The Arlington Historical Society's Newman entry names Newman, Monroe and Dorsey as African American members, and its Center for Local History entry gives Tejada's Latin American heritage; Monroe also rests on the Arlington NAACP president's words at his death, and Dorsey on his own statement (2020). | A press pronoun or honorific for every member. |

In November 1931 three Black candidates ran for the Board and all lost; who
they were, and every other Black candidacy, is in `docs/candidates.md` under
"Black candidacies".

No roster source states anyone's race or gender. Race comes
from Hjerpe and O'Leary; gender comes from a census listing or from the
pronoun or honorific a paper uses for the member, and where neither has been
found the default stands, labelled `assumed`. The
seat counts for 1870–1888 are therefore Hjerpe's identifications applied to
O'Leary's roster; Alex Keena's year-level counts are a replication
of the same source and not a second one.

What any source says, in full, is that Rowe, Syphax, Pinn, Pendleton, Allen,
Newman, Monroe, Dorsey, Spain, Tejada and Talento are recorded as other than
White and that Magruder, Cannon, Buchholz, Bozman, Grotos, Whipple, Favola,
Hynes, Garvey, Cristol, Talento, Coffey and Cunningham are women. Every other member is recorded
as a white man because no source speaks to them. The verification to ask of
County staff, and through them the Historical Society, is therefore the
default, not the lists: every other member has been treated as a white man;
where is that wrong? That is `member-demographics-lists` in `docs/questions.csv`.

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
candidate history says so on its first page. So there is no official record of
a member's party, only of whose candidate they were, and that is what is coded,
per term, not per person, because a label changes between elections (Bozman ran
as ABC's candidate five times and as a Democrat once). Three sources, in order:

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

**The rule for reporting** (Sally): the party or coalition
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
| 1932–1950 | County candidate history, where it prints a label | The county's label where it prints one, newspaper reporting for 1933 and 1942–49, McCaffrey (2026a) for the 1949–52 independents and the 1952 appointees; the rest are `unsourced`. |
| 1951–1966 | County candidate history | Every winner but Blevins (1956) and the two `(Convention)` nominees of 1955. `(ABC)` appears from 1957. |
| 1967–1983 | County prints `(I)` on most winners; reporting names the party | Fisher, Munsey, Purdy and Wholey as Democrats; Bozman as ABC's candidate; Grotos, Frankland and Detwiler as Republicans. Ricks stays `(I)`. |
| 1984–2006 | County candidate history | Every winner labelled. Bozman `(I)` through 1989, `(D)` in 1993. |
| 2007–2021 | County and state, checked against each other | Agree on every winner. |
| 2022– | State database | Party on the 2022 general; from 2023, the Democratic primary win. |

The reporting file holds a sentence in the source's own words for each
claim, with its citation, keyed on the name and the term's start year: pieces by
Scott McCaffrey for the Sun Gazette and ARLnow (2009–2026), the Library of
Virginia's biography of Joseph Fisher, Joseph Wholey's obituary and an ARLnow
report of the 2020 special election. The built table reproduces three compositions reported independently, three
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

**What is not labelled.** These terms have no label anywhere: the four 1932
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
