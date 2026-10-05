# Paper punch list

Small fixes to the report noticed while reading the PDF: a wording, a title, a
table's spacing, a figure's placement. One line per item, in plain words, with
the page or section if you have it. No compiling and no decisions belong here;
a decision that changes a number, a citation or a figure's form is a row in
`docs/questions.csv`.

Cleared in batches: a session takes the whole list, makes each change, builds
the paper, commits, and deletes the lines it cleared. What it cannot settle
stays, with a one-line reason under it.

## Open
- Race and Ethnicity, A Shrinking Electorate: the prose still gives votes per 100 residents (17 to 23, falling to 13 in 1900 and 3 in 1904) while Figure 2 beside it now divides by residents of voting age. Restate the prose in the figure's numbers (read them from data/clean/, not the picture), from 1880. (Sally, 5 Oct)
- Election Method, Ranked Choice: two sentences overreach. "A single-winner count changes how the votes are tallied and nothing about who wins" is not true in general; say only what the count does. And 2023 as "the one contest in any Arlington Board election where a group smaller than the largest won a seat" reads Roy's first-choice lead as a bloc and calls a nomination a seat; say what happened: Roy led on first choices and Coffey was nominated on transfers. (Sally, 5 Oct)
- Part C opening paragraph: cut the narration ("under the same four headings... Naming them is not a recommendation... not as a sequence or a priority"); keep only the sentence that the four questions overlap. Part C, Age: the tracker slug in parentheses leaves the prose; a % waits on: mark instead. (Sally, 5 Oct)
- A.3 Age: cut "There is no defensible optimal age for a Board member, so the two figures are not drawn on one panel, which would imply that there is" (the county median is now drawn on the Board figure); cut the sentence that five members spread wider than three; cut the paragraph explaining that the band is not quartiles. Each defends a decision or refutes a question the reader never raised. (Sally, 5 Oct)
- Data Appendix, Race and Ethnicity: cut "they are living people in Arlington who can confirm or correct it" (a request; the tracker row member-demographics-lists holds the ask). Sources and Age both say census birth years are accurate to within a year; say it once, in Age. (Sally, 5 Oct)
- Data Appendix, Seat-Years: keep it, and write it for the reader of the figures: a member who sat part of a year counts as a fraction, which is why the stacked figures (gender, race, party) have ragged edges where a member left mid-year, and why 1870 is half a year. Show one case. (Sally, 5 Oct)

## Could not settle
- Board Seats: the federal-office statute (Acts 1883-84 ch. 145) that emptied Perkins W. Squier's seat in 1884 is, as Code 1950 § 2-27, the one Dean v. Paolicelli applied to take the Board's Non-Partisan majority in 1952, so Arlington held four Board contests on 4 November 1952; one provision at both ends of the period, not yet in the paper (paolicelli1952, dailysun1952appointees). (members.md split, 4 Oct)
  Adds a claim tying one statute to two events 68 years apart; wants a Fable session.
- Election Method: the vacancy rule's history is not in the paper: a writ of election at the next November until 1975 c. 636 (a special election in 45-60 days, appointment within 180 days of a term's end), the 1998 filing-deadline amendments, the 2014 window of 60-80 days; and 1993 c. 731, which removed the referendum paragraphs, is unread (vaacts1958c207, vaacts1975c636, vaacts1998c345, vaacts2014c573, vacode152705). (members.md split, 4 Oct)
  Adds a legislative history the paper does not yet carry, and a source is unread; wants a Fable session.
- Board Structure: where the 1930 act's text comes from is not in the paper: it follows neither Gilbertson's 1917 model bill nor the 1916 Model City Charter, its five-member board and non-resident manager survive in § 15.2-702, and the carve-out letting a board discuss appointments with its manager first appears in Richland's 1958 charter, not the League's editions of 1927, 1941 or 1957 (gilbertson1917county, nml1927modelcharter, nml1941modelcharter, richland1958charter, vacodecommission1997sd5). The Historical Society's "first county by popular vote" stays unconfirmed (county-manager-statutes-other-states). (members.md split, 4 Oct)
  Adds a claim about the act's origins and leaves one claim unconfirmed; wants a Fable session.
- Board Structure: the chair custom is not in the paper: since 1990 each year's vice-chair chairs the next year, with four breaks each explained by membership, and no chair election is reported contested (arlingtonva2026members, arlnow2026chair). (members.md split, 4 Oct)
  Adds a claim about an unwritten custom the paper does not yet carry; wants a Fable session.
- Figure 3 (county by race) legend: consider alphabetical order (Asian & Pacific Islander first), since nothing says why Black comes first. The figures skill says a legend follows stacking order, and docs/figures.md sets the stack with the largest group on top; if the legend goes alphabetical, decide whether the stack does too, and apply the same rule to Figure 4 and the gender figure.
  A decision on stacking order, for Sally.
