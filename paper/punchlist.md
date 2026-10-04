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

- An introduction section is needed; the equity resolution belongs there, not as a stub at the head of Part A. Budget space for it.
- Board structure and election method are separate. Structure is everything after the election: how many seats, who the members are, and their relationship with the Manager. Election method is how those people are chosen. So the Board-and-Manager material (now A.7), which is short, goes into A.1 Board Structure; Local Legal Authority (now A.8) then becomes the one genuine stapled-on addendum, and the bridge paragraph moves to its head. (Structural; settle in a Fable session before moving text.) Example of the line: the 1938 referendum on staggered terms is election method, not structure.
- A.2 Board Size should foreshadow the comparison across Virginia localities that Part C's Board Structure section makes (Figures on residents per member and density).
- Gender and Race layout, alternative preferred: put the two tables (women, members of color) on one page together, and put the county-by-race figure (now Figure 3) and the Board-by-race figure (now Figure 4) on one page together, so a reader sees the echo of the population's distribution in the Board's. The earlier thought, table before figure within each section, is the fallback. Better still: Tables 1 and 2 become one table on one page with two panels (women; members of color), in the roster's form and columns, as a subset of the roster, pointing to the full roster in the data appendix. Render it from the same build step as the roster.
- Race and Ethnicity text needs serious smoothing. The second paragraph (displacement, Bestebreurtje, Freedman's Village) reads as arguing with the project's own earlier thinking rather than telling the story; no narrative flow. (Prose; a Fable or Sonnet pass against the prose skill, after the structural calls above.)
- Figure 3 (county by race) legend: consider alphabetical order (Asian & Pacific Islander first), since nothing says why Black comes first. The figures skill says a legend follows stacking order, and docs/figures.md sets the stack with the largest group on top; if the legend goes alphabetical, decide whether the stack does too, and apply the same rule to Figure 4 and the gender figure.
- Race: Tibbett Allen gets too much attention, and footnote 19 (the court's rule against him) is excessive; cut to what the argument needs.
- Race: restructure the Board half around the question. Preview the argument: here are the forces that may have been at work (the hypotheses), then investigate each. "Disfranchisement weighs most" is a terrible sentence; no sentence of that shape anywhere.
- A map of the three magisterial districts is needed, perhaps on the same page as Figure 5 (Black share by district). A new figure; needs a boundary source (docs/residents.md has what places each census's enumeration districts).
- Figure 5 legend order: Arlington County, Arlington District, Jefferson District, Washington District. Arlington District must not be orange or vermilion, which marks the county as a whole elsewhere (the per-seat line, the peer figures); pick another Okabe-Ito hue in style.DISTRICTS and docs/figures.md.
- Take the Black Candidates figure (the candidacies strip) out of the Race section; what to do with candidates is undecided (tracker row candidate-analysis). Fold the sentence it carried, that no Black candidate ran 1932-86, back into the prose if it is still needed.
- Age: Figures 7 and 8 (county by age; Board by age) go on the same page so they compare directly.
- Age: soften the Board half. Be cautious about saying the Board is not representative by age: no one under 18 can serve, so the comparison base is adults (or eligible voters), and age correlates with knowledge and professional skill, so the claim needs a conversation before it is made strongly. If the claim stays, it needs a figure that makes the comparison directly, probably in a different format from the two now in the section. (Decision; tracker row age-board-against-county.)
- A.6 Politics may not earn its place as a section. Party likely belongs in the election-method section; turnout, at least before 1932, may belong in Race, where it has to show that voter suppression meant fewer people were choosing at all. Treat A.6 as a holding pen until those homes exist. (Structural; with the election-method decision, tracker row election-method-section.)
- Part B waits on the author-team conversation about how the themes run across the parts (the map note of 4 October: structure, election method, who has served, duties, legal authority, participation). Nothing to do in Part B until then.
- Part C needs parallel structure with Part A, settled in the same conversation. Board Duties (C.1) is not a concept Part A has explored; if the Board-and-Manager material folds into A.1 Board Structure, then duties live inside structure in Part A and C.1 should follow, or Part A grows a duties strand.
- Figures 9 and 10 (the peer-locality scatters in Part C) should fit on one page; there is a lot of white space. Perhaps less square (they take style.SQUARE), or side by side as two panels; a style-layer change, so check every scatter after.
- Name the concept the same way in both parts: Part C's "Legal Constraints" (C.5) is the same thing as Part A's "Local Legal Authority" (A.8); one name for both headings.
- Data Appendix formatting does not match the rest. Set the heading conventions once (what is a part, a section, a subsection, a run-in heading) and apply them to the appendix (it is a starred section with starred subsections now). Paragraph indents are inconsistent, some flush left and some indented, mostly where a figure or table environment precedes a paragraph; pick one convention and enforce it (\noindent after floats, or indent everywhere).
- Data Appendix, Board Members: reorder so membership comes first. Open with how membership is handled (the Seat-Years paragraphs: fractions, vacancies, 1870) and the roster, then the sources for each attribute (gender, race, age, residence) after.
- Roster: each page is a self-contained panel with its own notes: Table 3A "Board Members, 1870--1919, by Year First Seated", 3B, 3C for the pages that follow, each carrying the notes (including a line saying where the source for each member's entry can be found: the repository's members table and the archive delivered to the County, named by their public location once it exists), instead of one longtable with notes only at the end. If the panel titles and notes push a decade (the 1960s) onto the next panel, that is fine; break panels at decade boundaries, never inside one.
- Roster: "Seated By" in title case in the header; space the columns more evenly (Served and Seated by are squeezed against the others); confirm the order Name, Served, Seated by, Born, Gender, Race and Ethnicity (the last column's header matches the section's name).
- Figure 7 (county by age): the Notes line is unnecessary; drop it, keep the Source.

## Could not settle
