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
- Part C, Election Method: add the election calendar as a question a review would take up: which cycle the Board is elected on, and what aligning its elections with federal or with state elections would do. Part A's Staggered Terms and Figure 3 (elections_turnout_board) already show the Board's electorate varying with what leads the ballot, presidential, midterm or governor's year; the question points back to that, takes no position, and cites the statute that sets the calendar. Structural: adds a question to the section's two-question framing (Sally, 9 Oct).
- Roster, Table 2 (code/analysis/members_roster.py): columns are now each as wide as their widest entry with the spare width shared equally between them, on branch roster-columns, unmerged until Sally has seen the page (Sally, 9 Oct).
- Presidential turnout figure (elections_turnout_president): the years each line covers are not clear. The President line runs 1872-2024; the new County Board line runs only 1879-1915 (contests with every district contested, dotted across the rest) and stops with no word on why, while the Board from 1932 is Figure 3's. Settle the domain: the figure ends at 1931 with Figure 3 taking over, or keeps 1872-2024 with the caption or an end label saying where the Board line stops and why. Show Sally the options as pictures (Sally, 9 Oct).

## Could not settle
- Board Seats: the federal-office statute (Acts 1883-84 ch. 145) that emptied Perkins W. Squier's seat in 1884 is, as Code 1950 § 2-27, the one Dean v. Paolicelli applied to take the Board's Non-Partisan majority in 1952, so Arlington held four Board contests on 4 November 1952; one provision at both ends of the period, not yet in the paper (paolicelli1952, dailysun1952appointees). (members.md split, 4 Oct)
  Adds a claim tying one statute to two events 68 years apart; wants a Fable session.
- Election Method: the vacancy rule's history is not in the paper: a writ of election at the next November until 1975 c. 636 (a special election in 45-60 days, appointment within 180 days of a term's end), the 1998 filing-deadline amendments, the 2014 window of 60-80 days; and 1993 c. 731, which removed the referendum paragraphs that conditioned Arlington's elected board and staggered terms on a popular vote, is now read and entered as vaacts1993c731 (vaacts1958c207, vaacts1975c636, vaacts1993c731, vaacts1998c345, vaacts2014c573, vacode152705). (members.md split, 4 Oct)
  Adds a legislative history the paper does not yet carry, and a source is unread; wants a Fable session.
- Board Structure: where the 1930 act's text comes from is not in the paper: it follows neither Gilbertson's 1917 model bill nor the 1916 Model City Charter, its five-member board and non-resident manager survive in § 15.2-702, and the carve-out letting a board discuss appointments with its manager first appears in Richland's 1958 charter, not the League's editions of 1927, 1941 or 1957 (gilbertson1917county, nml1927modelcharter, nml1941modelcharter, richland1958charter, vacodecommission1997sd5). The Historical Society's "first county by popular vote" stays unconfirmed (county-manager-statutes-other-states). (members.md split, 4 Oct)
  Adds a claim about the act's origins and leaves one claim unconfirmed; wants a Fable session.
- Board Structure: the chair custom is not in the paper: since 1990 each year's vice-chair chairs the next year, with four breaks each explained by membership, and no chair election is reported contested (arlingtonva2026members, arlnow2026chair). (members.md split, 4 Oct)
  Adds a claim about an unwritten custom the paper does not yet carry; wants a Fable session.
- Part C, Board Structure: the member's salary cap from January 2024 is 119,833 in the County's June 2023 agenda item and 116,343 in the FY 2027 budget summary, so the paper says only "above $116,000"; current pay actually appropriated not found (tracker row board-pay-cap).
  Wants the adopting ordinance or minutes.
