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
- Figure 9 (Arlington among Virginia's larger cities and counties): the top panel is squished, about 60 percent of the bottom panel's height. The fix measured on 5 October: `height_ratios=(1.5, 1)` on the outer gridspec in `charts.scatter_pair` makes the two panels equal; apply it through the style layer and check both panels print the same height. (Sally, 5 Oct)
- The southeastern-peers figure (`localities_southeastern`, built, not in the paper since the two Virginia scatters became one stacked figure on 4 October) goes back into C.1 Board Structure after Figure 9, with a caption in the same form. (Sally, 5 Oct)
- The Data Appendix shows that white space is not separating sections: a section head gets 12pt above, the same as a subsection, so the levels run together where sections run on. Set a scheme once for the whole report (part, section, subsection, run-in) and show before and after; this is the same job as the headings-and-spacing line under Could not settle, so do both at once. (Sally, 5 Oct)
- Data Appendix, Residence: replace the subsection with a placeholder, one bracketed italic sentence, until the County's records settle the addresses; the prose it holds now moves to the archive, not the paper. (Sally, 5 Oct)
- Table 3 (the roster): break the panels into four eras, 1870-1899, 1900-1949, 1950-1999 and 2000-present, in place of the decades. Cut the note under each panel (the superscript key, the dashes, the census-age caveat); the source key lives in the appendix's Sources text. (Sally, 5 Oct)
- Paired figure pages still need formatting work (two figures, notes and source on one page); fold into the spacing scheme above. (Sally, 5 Oct)

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
- Headings and spacing are not yet nailed for skimmability (Sally, 4 October 2026, looking at the data appendix): the part, section, subsection and run-in levels need a deliberate scheme of weight, style and white space above and below so the eye finds the structure at a glance; a typographic pass over the whole document, one scheme applied everywhere, shown before and after.
  Sets a scheme for the whole document; wants a Fable session.
