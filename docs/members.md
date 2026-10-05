# The Board

This write-up covers who held each seat and when, and who they were: what each
number in `data/clean/members.csv` and `data/clean/members_by_year.csv` is,
what backs it, and what is assumed where nothing does. How a decision was
reached is in the git history rather than here. `code/citekeys.py` explains the
placeholders in the `source` columns, and `docs/questions.csv` holds what is
still open.

## What rests on an assumption

**Race, 1889–1986.** Walter G. Willson (1889–92) is Black on the Gazette's
word. Every other seat is coded White on the "first since Reconstruction"
framing. The five Reconstruction-era members rest on Hjerpe's census linking
(`member-demographics-lists`). From the 1962 seating on, no census is open, so
the members seated since rest on the default unless a source names them: 40 of
126 members rest on it, 34 of them seated in 1962 or later.
`members_race_coverage` draws the seat-years that rest on it. Those 34 are
living people in Arlington, so most could be confirmed by asking.
The other six, Smith, Crocker, Robinson, Phillips, Brown and Richards, were
seated before 1962; the press names each without a racial label, which is weak
evidence at most; the searches are rows of `members_negatives.csv` (below).

**Gender.** William H. Robinson and Walter G. Willson rest on the default,
man, both searched without result (`members_negatives.csv`, below).
Every other member has a census listing or a pronoun or honorific in the
press, and `gender_evidence` in `members.csv` says which each rests on.

**Race and gender from the census.** For the members first seated 1932–1966
and 1870–1904, race and gender come from census records. Each index reading
was checked against the sheet, where the row could be found on it. The match to
the member rests on the name, on the district he sat for or on Arlington, and,
where the record gives one, on an occupation, a household or a street. No
census holds Casto, H. L. Brown Jr, Fisher, Lowry or T. W. Richards of the
later era, or H. Dwight Smith, Crocker, Schutt, Robinson or Willson of the
earlier. R. Henry Phillips's only census household is his father's, so his
birth year rests on an obituary and a railroad notice, not a census (below).

**Birth years.** Birth years are held for most members, and they rest
on the ages in census listings and on an age stated in an obituary or a
profile. Each is right to within a year. The age figure draws a year only where
every sitting member either has a birth year or is one of the two the figure
names, and it runs from 1910 to the present, the first census whose ages the
residents figures can set beside the Board's. Four members before 1910 have no
birth year: H. Dwight Smith, Lott W. Crocker, William H. Robinson and Walter G.
Willson, each found in no census under any spelling tried and in no Gazette
item that gives an age (above); they sit outside the figure. The two it names
are Susan Cunningham and Tannia Talento, recent enough that a stated age
should be findable. Naming them rather than allowing a count of unknowns is
what makes the gap a known quantity: a member who arrives without a birth year
and is not among them stops the build. Every other member seated in 1900-2026
has a birth year.

**1912–1931 rests on no assumption.** `arlhist1967officials`, the Historical
Society's own compilation from the Board's minute books, names all three
magisterial seats — Arlington, Jefferson and Washington — for all twenty years.
It states the one vacancy, in the Washington seat in early 1920, rather than
leaving it silent. `members_by_year.py` reads the roster for those years like
any other (below, "The article and the other sources, 1870 to 1931").

**1870–1911 rests on O'Leary's electoral history and the same article
together.** The article settles names, the July–June term year, and
terms O'Leary does not record (below, "The article and the other sources, 1870
to 1931"). The statute behind the July
seating is `vaacts1870` ch. 76 sec. 4, below ("When the Board's year ran").
Two seats that the article gives to a different man are settled, and the roster
follows the article in both.

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
committee (`gazette1894wilson`, `gazette1874smith`).

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
differ, but what each source says is settled, and the census record's bib
entry says why.

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
Board's only Black member that year; Willson, whom the Gazette calls colored,
takes the Washington seat in 1889, and Newman in 1988 is the next Black member
after him. Schutt and Rowe went on their own
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
county's roll records service too, so the roll dates the departures and
arrivals no contest shows, Tannia Talento's appointment of 15 July 2023 among
them, and is a second witness to Novack for 1932 to 1994.
`code/clean/members_roster_roll.py` reads it: `check_against_novack` holds the
two to each other, `OVERRULED` holds the one disagreement read against a third
source (Massey's appointment, which the *Daily Sun* dates with Novack,
`dailysun1952appointees`), and a disagreement with no third source stops the
build.

**A month belongs to whoever held the seat for any part of it.** Where a gap
covers a whole month the seat was empty, and these months since 1932 were:
March and April 1990, October 1997, March 1999, February 2003, January and
February 2012, March 2014, and May and June 2020. Each is a seat Arlington left
unfilled while a special election was called, the Board sitting with four
members. `members_roster_roll.EMPTY` names the departure and the arrival that
bracket each, and `check_seats` holds the roster to them: an undeclared gap
stops the build, and so does filling a declared one. No one was appointed to
any of those months; Talento's is the only appointment to the Board since 1975
(`arlnow2014zimmerman`).

**A resignation inside a month the member still holds is no vacancy.** Ellen
Bozman resigned the rest of her first term on 2 December 1977 (`sun1977bozman`);
she held part of December, so the month stays hers and the year reads five
seats.

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
County Manager Plan by referendum on 4 November 1930 (rose1976 pp. 194-196:
2,067 to 1,031 for a change of government, 1,936 to 428 for the Manager Plan
over a Modified Commission Plan, 1,689 to 1,149 for election at large over
election by district) and has operated under it since 1932;
samuel2026 note 8 records that the Plan "appears to be the only county form of
government that does not refer to its Board members as 'supervisors'". The
name, the at-large method and the five seats therefore arrive together.

**The Board won the power to appoint department heads in 1951, and 1952
c. 443 bars its members from the appointments below it.** The Board appointed
the department heads until 1937, when it delegated that power to the manager.
It took the power back by resolution on 27 January 1951 (dailysun1951spicer),
and on 20 March 1951 Judge McCarthy ruled for it on a petition for a
declaratory judgment from Commonwealth's Attorney Denman T. Hucker: the Board
had no right to relinquish the power in 1937, and a change could come only by
amending the manager act (sun1951rulingboard). The police chief lay outside the
ruling, because a special act gave that appointment to the manager and both
sides agreed it was not at issue (sun1951rulingboard). That is the direction
the *Daily Sun* gives on 19 July 1952 (dailysun1952petitions); its 28 November
1951 line that the ruling overruled the Board over the police chief
(dailysun1951policechief) is the one account that runs the other way, and the
report of the day governs. By the winter the Board's advisory committee and the
Arlington Civic Federation wanted the power returned to the manager
(dailysun1951spicer), the new chairman named the same change among the bills he
hoped for in January 1952 (star1952cox), and 1952 c. 198 put it to the voters
(vaacts1952c198).

c. 443 does not move that power. Enacted outright on 1 April 1952, it exempts
"persons appointed by" the Board, and has the Board deal with the
administrative services through the manager and the heads of departments
"whom it may be empowered to appoint" (vaacts1952c443). What prompted it is not
documented in anything held. It is in neither the League's proposals of 29
September 1951 (dailysun1951institute) nor the delegation's bill list of 4
December 1951 (dailysun1951bills), and the Board's friction with its manager
that autumn (dailysun1951lundberg) is context, not a stated cause. No held
report covers its introduction or passage, and the *Daily Sun*'s digitised run
has no issue between 31 December 1951 and 22 April 1952. What would show who
introduced S 431 and why is the Senate's journal for the 1952 session and the
Board's own minutes for February and March 1952.

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

### The election section after 1962

**The rules for electing members of the Board change at the edges after 1958,
and the 1952 questions never return.** The section that opened with the
referendum on biennial elections (§ 15.1-676 after the 1962 recodification,
§ 15.2-705 today) is amended in 1975, 1993, 1997, 1998, 2014 and 2020
(`vacode152705`), and none of the amendments reopens the 1952 package. No
petition was filed in the 1958 window (`vaacts1958c207`), and nothing offers the
voters a second chance.

**1975 c. 636 replaces the vacancy rule.** Until then a vacancy was filled by a
writ of election, held at the next regular November election when the term had
a year or more to run, and the member so elected served the rest of the term
(`vaacts1958c207`). Chapter 636, approved 24 March 1975, has the circuit judge
call a special election for the remainder of the term, to be held not less
than forty-five and not more than sixty days afterward; where the vacancy
falls within 180 days of the term's end, the remaining members fill it by
appointment within thirty days, after a public hearing (`vaacts1975c636`). A
clause written for 1975 alone has the Board appoint, before 4 November, a
person to hold the seat expiring on 31 December of that year from 5 November
on, and lets the judge's appointee serve until that person qualifies. The act
leaves the 1958 referendum paragraphs standing, apart from updated
cross-references, and chapter 517 of the same session carries them through again
(`vaacts1975c517`). The acts do not say why the rule changed.

**By 1996 the referendum paragraphs are gone and the Board is elected at
large.** The Code Commission's draft of the 1997 recodification prints the
section as it then stood: it opens "in any county operating as of December 1,
1993, under the county manager plan", provides for two members in November
1995 and one each in 1994, 1996 and 1997, and sets four-year terms beginning on
1 January, with no petition, no ballot question and no districts
(`vacodecommission1997sd5`, p. 104). The history line names one act between 1975
and 1997, 1993 c. 731, so that act made the change. Its text is not in a source
held: the 1993 volume of the Acts is not in full view at HathiTrust and
needs a law-library login.

**1997 c. 587 moves the at-large sentence and repeals § 15.1-691.** The
Commission draft folds the sentence "The members of the board shall be elected
from the county at large" into § 15.2-705(A), relocated from § 15.1-691, and
repeals § 15.1-691, which carried the 1930 text that abolished the magisterial
districts and let the referendum choose districts or the county at large
(`vacodecommission1997sd5`, pp. 104, 128; `vaacts1930c167`, sec. 2773-k). The
draft calls the whole section "no substantive change in the law". The enrolled
act, H 1667, prints only its title at the Legislative Information System, so
the report is the text read.

**Three later acts adjust the vacancy rule and add the ranked-choice option.**
Chapters 345 (S 61) and 369 (H 396) of 1998, both approved 11 April, add to
subsection C that the local electoral board announces the candidate filing
deadline for the special election within three business days after the judge's
call (`vaacts1998c345`, `vaacts1998c369`). Chapter 573 of 2014, approved 4 April,
lengthens the window for the special election to between sixty and eighty days
(`vaacts2014c573`). Chapter 713 of 2020, approved 6 April, adds to subsection B
that the board may provide by ordinance for nomination or election by instant
runoff voting, and adds § 15.2-705.1, which defines the method, authorizes it
for the nomination and election of members in a county under the manager plan,
and has the State Board of Elections write the rules; the Department of
Elections' technology costs fall on the localities that choose it
(`vaacts2020c713`).

### What the County Code and the Board's own papers add to the split

**The statute draws the line; the County's written rules for the Board and the
Manager are few and mostly procedural.** The 1930 act has the Board appoint a
manager, who holds the county's administrative and executive powers and
"the power of appointment of all officers and employees whose appointment or
election is not otherwise provided by law", while the Board may not change a
budget allocation without the manager's recommendation and may not move any
allocation by more than ten per cent (`vaacts1930c167`, secs. 2773-g and
2773-h). The County Code restates the Manager's half of it in one place, Chapter 6, and
the rest of its chapters show the Manager as the officer who runs permits and
enforcement. None of them sets rules for how a Board member deals with the
Manager's staff; that rule is § 15.2-703 and nothing else (`vaacts1962c623`).

**Chapter 6 gives the Manager the County's hiring and firing and keeps the
Board to the pay plan.** The chapter's authority is § 15.2-721; the Board
created the Civil Service Commission under it on 15 June 1951
(`arlingtoncode6civilservice`, § 6-1). The Commission has five members, qualified voters with
management or public-affairs experience who may hold no paid County
employment, candidacy or party office while serving; the Board appoints them
for four-year terms, reconsiders its choice of chair at its first meeting each
year, and removes a member only "for good cause shown by a majority vote",
after a written statement and a public hearing (§§ 6-2, 6-3, 6-5, 6-7). The Commission advises the Board, the Manager and the
Director of Personnel on policy and hears appeals; its finding on a
disciplinary appeal "shall be binding", and it may order back pay (§§ 6-8,
6-18). The Manager, not the Board, "appoint[s] and, when necessary for the good
of the service, remove[s] employees in the competitive service", appoints the
Director of Personnel, and adopts the administrative regulations, which take
effect "when approved by the Manager" after the Commission has reviewed a
draft (§§ 6-10, 6-11, 6-15). The chapter sorts every employee into one of three
services. The competitive service is every position under the Manager's control
and appointed by him; the executive management service, which the Code created
on 15 June 2003 (Ord. No. 03-15), is the Deputy and Assistant County Managers,
the department directors and the legislative liaison, who "serve at the will of
the County Manager" and fall outside the merit rules; and the noncompetitive
service is the Board's members, the other elected officials, the County
Manager, the County Attorney, the Clerk to the County Board, "heads of
departments whose appointment is vested by law in the County Board", and the
staffs of the constitutional officers (§ 6-14). The Manager is
himself outside the merit rules, and nothing in the chapter gives his office a
term or a ground for removal. The Board's share is the pay plan. The Manager
forwards the plan with the Commission's comments, the Board approves it, and
the Board "shall not increase or decrease any salaries of individual members of
the competitive service" (§ 6-20); the Board also approves the classification
system (§ 6-19) and decides, by appropriation, whether the housing and retiree
medical benefits are paid (§§ 6-28, 6-29).

The chapter reaches the Board's own seats in three places. A County employee
elected to a Board seat must resign on taking office, and a department director
or an employee in the Offices of the Manager or the County Attorney must resign
on becoming a candidate (§ 6-23). Collective bargaining runs through the
Manager, who names the County's negotiators in his "sole discretion"; a
tentative agreement binds the County only after a fiscal impact study, a public
hearing and a Board resolution committing to fund it, and the resolution "remains
subject to actual appropriation" (§ 6-30). Where a non-binding arbitration
award is not implemented, the Manager explains why "at the next meeting of the
County Board". The copy held is the Code as updated in July 2023.

**The County Attorney's office rests on a general statute, not on the manager
plan and not on the Code.** The 1952 act that would have created the office
for a county under the plan was a referendum that never took place
(`vaacts1952c569`, `vaacts1962c623`). Chapter 695 of 1968, approved 5 April,
added § 15.1-9.1:1 for every county: "the governing body of any county may
create the office of county attorney", appointed "to serve at the pleasure of
the governing body" at a salary the body fixes, with the Commonwealth's
attorney relieved of civil advice, ordinances and civil suits, and the county
attorney "accountable to the governing body" (`vaacts1968c695`). No vote of the
people is required. It survives as § 15.2-1542 (`vacode1521542`). No chapter of
the County Code creates the office. Chapter 6 puts the County Attorney in the
noncompetitive service beside the Manager and the Clerk to the County Board,
sends his employees through the merit rules with their own appointing authority
and the Commission's jurisdiction, and counts his office among the
"confidential" ones for collective bargaining and among the Group 2 offices for
political activity (`arlingtoncode6civilservice`, §§ 6-14, 6-17, 6-23, 6-30). The Board appointed Ryan Samuel by a
4-0 vote at a special meeting on 2 December 2025, and the office reports to the
Board, not the Manager (`arlnow2025countyattorney`, `arlingtonva2025samuel`).
The resolution that made the appointment is not in a source held, and
§ 15.2-1542 is the only authority found for it.

**The Independent Policing Auditor moved from the Manager to the Board in 2026,
and the state act came first.** Chapter 372 of the 2026 Acts, approved 8 April,
added § 15.2-709.3: the board of a county under the manager plan "may appoint an
independent policing auditor to support any law-enforcement civilian oversight
body", who has the oversight body's powers "to the extent such powers are
delegated", may have staff "independent of the administrative staff of the
county", and "shall serve at the pleasure of the board" (`vaacts2026c372`). The
Board followed with Ordinance No. 26-12, adopted 13 June 2026 and effective 1
July, which Chapter 69, the 2021 chapter that created the Law Enforcement
Community Oversight Board, names as the history of every section but four.
Section 69-11 now reads
"The County Board shall hire an Independent Policing Auditor", on the basis of
merit and at the existing pay scales, in an office outside any Police
Department facility, to "serve at the pleasure of the County Board"; § 69-12(k)
carries the oversight board's delegated powers to the auditor, as the statute
does (`arlingtoncode69oversight`). The Manager keeps three places in the
chapter: he signs the memorandum of understanding between the oversight board
and the Police Department with its chair, the auditor and the Police Chief
(§ 69-2(c)); the Police Department withholds records tied to an open matter
until it is completed or the Manager determines that release will not
compromise it (§ 69-8(c)); and when the auditor cannot get a witness or record
from the Department, the Manager decides within four business days whether to
require it, may not deny the request "unreasonably", and if he does deny it the
oversight board may by a two-thirds vote have the auditor apply to the Arlington
Circuit Court for a subpoena (§ 69-9). Any dispute over what the chapter means among the
oversight board, the Police Chief, the auditor and the Manager is the Board's to
settle with the County Attorney, and its decision "shall be final" (§ 69-13).
ARLnow reports the change and that the Board approved the auditor's employment
agreement in August (`arlnow2026policingauditor`); the amendment's wording is
in the chapter, but the ordinance's staff report and the agreement are not in a
source held, and the text of §§ 69-11 and 69-12 before the amendment is not
either, so what the Manager's hand in the office was before 1 July is known only
from the press.

**The County Auditor is the Board's by a statute older than the Policing
Auditor's.** Section 15.2-709.2, added in 2015 (c. 282), lets the board of a
county under the plan appoint a county auditor "for the audit and review of
county agencies and county-funded functions", with the power to review
performance and make "such special studies and reports as the board directs";
the auditor serves at the board's pleasure, and a removal "shall not be subject
to review by any other employee, agency, board, or commission of the county" or
to the grievance procedure (`vacode1527092`). The Policing Auditor's statute
copies the staffing and pleasure language of this one. Chapter 6 does not name the County Auditor; the office falls under "heads of
departments whose appointment is vested by law in the County Board" only on the
reading that § 15.2-709.2 is that law.

**The Audit Committee gives the Board a channel to the Manager, not around the
office.** Its charter seats the County Manager and the Director of Management
and Finance with two Board members, who co-chair, and says its creation "is not
intended to materially alter the responsibility and authority of either the
County Board, OCA, or the County Manager". The committee advises the Manager on
the resources the County Auditor's office needs before the proposed budget,
gives feedback on the Board's annual review of the County Auditor, and, when it
wants staff to explain corrective action, "may request that the County Manager
direct staff" to attend (`arlingtonva2025auditcharter`).

**The Board appropriates by department, and the Manager moves money within one.**
The FY 2027 appropriations resolution lists the County Board, County Manager,
County Attorney and the other departments with an amount each, returns any
general-fund surplus to the General Fund and carries unspent capital and
restricted balances forward; it contains no transfer clause. The budget's own
glossary supplies the rule: "the County Manager has the authority to approve
transfer of funds within a department or agency"
(`arlingtonva2026budgetresolution`). Against the 1930 act, which forbids any
change in an allocation without Board approval, that is a delegation to the
Manager; the sources held do not show when it was made. The Financial and Debt
Management Policies, updated in 2024, reserve to the Board any draw on the
operating or self-insurance reserve and any use of the contingent, and have the
Manager submit the ten-year Capital Improvement Plan every two years
(`arlingtonva2024debtpolicies`).

**The Purchasing Resolution keeps large construction contracts with the Board.**
"No contract for a capital construction improvement project or professional
services related to a capital construction improvement project that exceeds
$1,000,000 shall be awarded without the approval of the County Board", in the
July 2025 text of a resolution first adopted in December 1982
(`arlingtonva2025purchasingresolution`).

**The Chair controls the agenda, and the Manager drafts it.** Under the Board's
2026 meeting procedures the Manager prepares a list of proposed items about
two weeks before a regular meeting, the Chair approves the agenda, and a Board
member adds an item by writing to the Chair eight days ahead. The Manager may
recommend items for the consent agenda "with the consent of the County Board
Chair" (`arlingtonva2026procedures`).

### Where the 1930 act's text comes from

**The 1930 act matches neither model it could have followed.** Chapter 167 of the
1930 session, approved 20 March 1930 [H B 342], adds chapter 109-a to the Code
with two optional forms for a county of 500 or more people to the square mile,
a "modified commission plan" and the "county manager plan", chosen with the
question of at-large or district election at a single referendum on the
petition of two hundred voters (`vaacts1930c167`). Gilbertson's *The County*
(1917) prints a county manager bill introduced in the New York legislature
(Appendix D) and argues the plan in chapter form (`gilbertson1917county`). The
act shares no run of eight words with Appendix D and two with the whole book;
against the National Municipal League's 1916 Model City Charter it shares four
(`nml1916modelcharter`). The phrases that recur are generic ones ("need not be
a resident", "elect one of its members as chairman", "a majority of those
voting thereon"). The text the act does carry is its own: section 2773-f, on the
five-member board, the chairman "with a vote but no veto" and the manager who
"need not be a resident of the county or of the State", reappears in the Code
Commission's draft of § 15.2-702 with "Commonwealth" for "State"
(`vacodecommission1997sd5`, p. 102), so the phrasing the Code still carries
is the 1930 act's.

**The carve-out that lets a council discuss appointments with its manager is
not in the Model City Charter before 1958.** The three editions between 1916
and the Richland charter each carry the clause on council interference and none
has a sentence letting the council discuss appointments. The revised edition of
1927, sec. 48, bars the council, its committees and members from directing or
requesting an appointment or removal "or in any manner" taking part in it, and
makes a violation a misdemeanor that forfeits the office
(`nml1927modelcharter`, printed p. 34). The fifth edition of 1941, a complete
revision, keeps the same bar in sec. 11, adds that a councilman who votes for
a resolution or ordinance in violation of it is guilty of the misdemeanor, and
also has no such sentence (`nml1941modelcharter`). The League's 1957 imprint of
the fifth edition reads sec. 11 in the same words (`nml1957modelcharter`).
Richland's charter of 1958 then adds the sentence to the same clause
(`richland1958charter`), so the carve-out is Richland's or a source between
1957 and 1958 that is not held, and it is not the League's text before then.
Each edition's page is filed as a transcript of the text layer HathiTrust
serves, and only the page with the clause. The 1933 edition (HathiTrust
`uiug.30112106251876`) and the League's 1948 revision are not read; no sentence
in 1927, 1941 or 1957 suggests the clause changed between them.

**Whether Arlington was the first county to adopt the form by popular vote is
unconfirmed from the sources held.** The Arlington Historical Society's
account calls it "the first county in the United States to adopt by popular
vote any kind of a County Manager system" without naming a source, and
nothing held covers the North Carolina counties that adopted the form after
1927.

### What remains unread

The 1993 act (c. 731) is not read: HathiTrust does not show the volume in full
view and the Acts for 1993 need a law-library login. Wager's *County
Government Across the Nation* (1950), which covers the North Carolina counties
that adopted the form after 1927, is unread and needs a library copy, so the
first-county claim is open; so are the North Carolina session laws for
the counties that adopted it, which would say whether any did so by act or by
vote. The Manager's employment agreement and the Board's real-estate signing
authority are not in a source held; the County would have to supply the
agreement and whatever resolution lets the Manager sign deeds and leases.
Ordinance No. 26-12's staff report and the Policing Auditor's agreement are the
County's too.

### The article and the other sources, 1870 to 1931

`arlhist1967officials`, the Historical Society's compilation from the Board's
minute books, names all three seats for 1912 to 1931 save the one vacancy it
states, and for 1870 to 1911 corrects and adds to O'Leary's elections. How it
is read, and every name it settles, term it adds, vacancy it states and seat it
gives to another man, is in `code/clean/members_roster_arlhist.py` (`NAMES`,
`ADDED`, `VACATED`, `SEATED`, `READING_NOTES`), and each row of `members.csv`
it changes carries a note saying what settled it. Three rulings stand behind
those entries:

- the article dates a term from the first record of a man sitting, not from
  the instrument that named him: Hume was appointed on 2 October 1888 and is
  first shown present on 13 November, the date the roster uses;
- the roster records who held a seat, not who held title to it, so where an
  election return and the minute books disagree about who sat, the minute
  books answer: Torreyson holds the Arlington seat to 11 October 1897 and
  Corbett from then, Boyd never holds the Jefferson seat of 1870, and the
  Washington seat of 1897-99 is Saegmuller's (Sally);
- O'Leary is an electoral history, naming a departure only where his prose
  happens to, so where the article names a supervisor he does not, he is
  silent rather than contradicting (Sally).

**Where these readings bear on the central figure.** Some of them shorten a
Black member's recorded service:

- the added terms close Pinn's, Pendleton's and Allen's mid-term, where
  O'Leary's elections would run them out;
- the July term year moves a start off May in each year a Black member's
  service begins, 1871, 1872, 1879 and 1887;
- Rowe's resignation stands the Jefferson seat empty from April to June 1879. Reading
O'Leary's elections alone would give every one of those months to a sitting
member. `members_by_race` counts what the roster holds, and no count of it is
kept here.

`members_roster.check_district_seats` holds the reading in place: each of the
three districts has exactly one member in every month from 1870 to 1931, save
the six months before the Board sat and three recorded vacancies: Washington
from July to November 1873, Jefferson from April to June 1879, after Rowe's
resignation, and Washington in January 1920, after Clarence R. Ahalt, elected
to it, moved from the district before the term began. A gap anywhere else
stops the build, and so does filling one of these.

### When the Board's year ran

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

## Seat-years

`data/clean/members_by_year.csv` is one row per year from 1870: seats
held by each race, each gender, (from 1932) each party, what the member's race rests on
(a census sheet, a published or press account, or the default), and the most exact place any source gives, in seat-years, so a
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
countywide from the County Manager plan, which the referendum of 4 November 1930
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
| Neighborhood | 10 | 1 | 4 | 2 | 17 |
| Side of the County | 1 | 1 | 0 | 0 | 2 |
| Nothing | | | | | 13 |

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

Each census record matched to a member is one row of
`data/transcribed/by_claude/members_census.csv`, holding records from the
1870, 1880, 1900, 1910, 1920, 1930, 1940 and 1950 schedules. What each column
holds, what counts as a match and how the printed values are coded is in the
docstring of `code/clean/members_census.py`; how the claim files keep words
rather than categories is in `code/clean/members.py`. Which rows have not
yet been read for a tie is `census-match-quality`.

One record is filed and cited but kept out of the table, because its birth
year disagrees with the member's other record and the build stops on two
sources disagreeing: William Duncan's 1910 (`census1910duncanwilliam`), which
waits on `duncan-birth-year`.

### Reading an image

How a record or a page is read off its image is in the `sources` skill,
"Reading an image".

### What has been searched for the members who keep a default

Every search that came back empty is a row of
`data/transcribed/by_claude/members_negatives.csv`: the member, the field
sought, the collection searched, the span, how, and what came back.
`code/tests.py` refuses a member first seated before 1962 whose race, gender or
birth year rests on the default with no row there. What a missing racial label
is worth depends on the paper's habit, which the report's Data Appendix sets out
under Race and Ethnicity: it is no confirmation of White.

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
| 1889–1930 | Willson (1889–92) is Black on the Gazette's word, three notices that read "colored" (above). For every other member, one collective sentence: the board "became and remained all white for the duration of this system" (Hjerpe 2021, p.4), sourced to the county's election records, which the Gazette contradicts for 1889 and 1891. No per-person evidence. | Names in O'Leary; initials only before 1912. No source names a first woman member, so "all men before Magruder (1932)" is assumed. |
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

### The voting-rights era

One secondary source, the Congressional Research Service's history of the Act
(`crs2023votingrightsact`), covers all four items the race timeline may name.

- The Voting Rights Act is signed on 6 August 1965 (P.L. 89-110) and prohibits
  discrimination in registration and voting on the basis of race, color or
  language-minority status (Table 2, p. 5; Summary); its Section 5 requires
  federal review of voting changes before they take effect in certain
  jurisdictions (Table 1, p. 3).
- Section 4(b) covers six states entirely when the Act is enacted in 1965,
  Virginia among them (p. 14).
- *City of Mobile v. Bolden* (22 April 1980) reads Section 2 to require proof
  of discriminatory intent, and Congress amends the Act in 1982 in response
  (Table 2, p. 5; p. 21).
- *Thornburg v. Gingles* (30 June 1986) sets the standard for vote-dilution
  claims under Section 2, which the report ties to the 1982 amendment's
  attention to at-large elections (Table 2, p. 5; p. 22).

Arlington is covered by Section 5 from the start, and the Justice Department's
published records name it in submissions but in no objection.

- **Coverage.** Virginia is covered in its entirety under the 1965 formula,
  coverage dating from 1 November 1964, so the state and all its political
  subdivisions need preclearance for voting changes
  (`doj2023section4bailouts`; `doj2023section5covered`, the Virginia row).
  Neither page names a locality as covered. Arlington is not among the
  Virginia jurisdictions listed as bailed out, the first being the City of
  Fairfax on 21 October 1997 (`doj2023section4bailouts`, the bailout list).
- **Submissions naming Arlington.** The Division's periodic notices of
  preclearance activity list each submission by state, county and subject.
  Twelve notices between 19 February 1999 and 6 July 2001 carry a line for
  Arlington County, one submission each: two vacancy special-election
  procedures (February 1999, July 2000), voter registration hours or
  locations (May 1999, October 2000), four changed polling places (July to
  November 1999), a bond election (September and October 2000), a voting
  machine (June 2001) and a precinct realignment (July 2001). The notices
  record receipt and requests only and state no outcome, and they do not say
  whether the vacancy procedures concerned Board seats. They are cited
  nowhere: the changes are administrative and none concerns how the Board
  is chosen, so no source entry is kept for them; the notices are at
  justice.gov/crt under "Notice of Preclearance Activity".
- **Objections naming Arlington.** None. The Division's list of Virginia
  objection letters runs from 26 June 1970 to 21 October 2003, 33 entries
  for the State of Virginia and named cities and counties, and does not name
  Arlington (`doj2015section5virginiaobjections`).
- **Statewide records covering Arlington without naming it.** The objections
  to the State's own changes - Senate and House multi-member districts
  (7 May 1971), redistricting (1981, 1982 and 1991) and a prohibition on
  candidates assisting voters (3 August 1984) - apply to every Virginia
  locality including Arlington
  (`doj2015section5virginiaobjections`, entries for the State of Virginia);
  they are the State's changes and the list does not say what they meant for
  Arlington.

No submission or objection on election method is found. The Board's at-large
election dates from November 1931, before the Act, and no record found in
the notices or the objection list shows the method itself, or any change to
it, going before the Justice Department. The 479 notices held run from April 1998 to August 2008, as published
at the two addresses the Division uses for them; submissions before April 1998 or after August 2008 are not in
anything held, and the Division's own list of changes by type and year is
national and names no locality. Whether Arlington submitted anything between
1965 and 1998, and what became of the twelve submissions, rests on
the County's own record of its submissions; no published Division record
found gives an outcome for a submission it did not object to. Neither *City of Mobile v. Bolden* nor *Thornburg v. Gingles* is tied to
Arlington by any source held.

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
