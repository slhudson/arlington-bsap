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
- Table 1 (Women and Members of Color): one list in seating order under three headings, 1800s, 1900s, 2000s, in place of the two panels, so the pattern reads off the page: Black men, then white women, then both. Each member appears once (Talento now appears in both panels). Written by code/analysis/members_roster.py's subsets_tex; the title may need to change to say what the table is. (Sally, 5 Oct)
- Table 1 must sit at the foot of the A.3 opening page (page 10 now), under the two paragraphs, not on the next page: raise \bottomfraction (and \textfraction down) in the preamble, or place it [!b], and confirm in the PDF that the page holds the two paragraphs and the table and Gender starts the next page. (Sally, 5 Oct)
- Table 3 (the roster) lost its notes entirely when the per-panel notes were cut. It needs one note, under the last panel only, with the superscript key (c census, p press or profile, a assumption; two marks where two kinds agree) and the dash for a missing value, so the table stands on its own; the census-age caveat stays in the appendix's Age text. (Sally, 5 Oct)
- Data Appendix: move the Elections section before Board Members, since it is short and the roster then closes the appendix; update the figure notes that point to "the Data Appendix, Elections" only if the wording depends on order. (Sally, 5 Oct)

## Could not settle
- Table 2 (Where to Find the Board, by Year) took "written for a replicator" too literally: the headings "Open First" and "Read Beside It" turn a table of sources into an instruction manual. Revisit the form with Sally; the likely shape is Years, Sources (the documents that name the Board in those years, primary first), Members, with the roadmap voice kept in the prose, not the column heads. (Sally, 5 Oct)
  A decision on the table's form, for Sally.
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
