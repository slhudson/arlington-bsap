---
name: prose
description: Write or edit the report's prose and the write-ups in this repository's voice. Use whenever text in paper/ or docs/ is being drafted, rewritten or reviewed, including a figure's caption and a tracker row's sentence.
---

# Prose

The report is read by a county board, by the people it is about, and by
collaborators who will check it. Write so that a reader who knows the subject
but not this project understands a sentence the first time.

Three sources stand behind this, and none of them is a word count.

    Strunk, The Elements of Style (1918)    what to cut and what to prefer
    Orwell, Politics and the English        the escape hatch, below
      Language (1946)
    Williams, Style: Lessons in Clarity     why a sentence reads badly
      and Grace

Strunk says prefer the active voice, write with nouns and verbs, put
statements in positive form, omit needless words. Williams says why those
work: make the characters of a sentence its subjects and their actions its
verbs, put information the reader already has before information that is new,
and end on what you want to land. Orwell says the rest of it can go: "Break
any of these rules sooner than say anything outright barbarous."

That last line governs the others. Nothing here is a limit to be counted.

## How a sentence goes wrong here

These are the failures this project's prose actually makes, drawn from
edits its authors have asked for. Each is a shape to recognise, not a rule to
tally.

**The subject is buried.** "What places a member of those years is his census
sheet" — the reader meets a clause before meeting a thing. Ask who is doing
what, and start there: "A member's home is known only as closely as his census
sheet names it."

**A dash carries two jobs.** An aside between dashes that holds two clauses
makes the reader put the sentence down and pick it up again. One idea in the
aside, or no aside.

**A noun stands where a verb belongs.** "The application of the assumption" is
two words away from "the figures assume". Prefer the verb; the sentence
shortens itself.

**The tense narrates the project.** "This is no longer the question it was"
only parses for someone who knows what it was. State the position: "The
minute books name all three seats in every year from 1870." What changed is in
git, not in the prose (CLAUDE.md, *Questions and decisions*).

**A negative where a positive would do.** "Who was sitting is not the open
question" makes the reader hold a negative to reach a fact. Say what is known.

**Hedges stacked.** "It may perhaps be that some of these are possibly
incomplete" says less than "Two cells are missing." Where something is
genuinely uncertain, name the uncertainty once and move on.

**A list pretending to be a sentence.** Three clauses joined by semicolons
usually want to be three sentences, or a list the reader can see.

## Reading it back

Read the passage aloud. Where you stumble, the reader stops. That test finds
more than any checklist, and it is the one to run before saying a passage is
done.

Then ask of each paragraph: what does it want the reader to know? If the
answer takes two clauses, the paragraph is doing two jobs.

## What the voice is not

Not conversational. The report is formal, and a formal register is not the
same as a dense one — "the county court issued a rule against him" is both
plain and exact.

Not simplified. Keep the technical words the subject needs: magisterial
district, seat-year, enumeration sheet, citekey. A reader of this report knows
them, and a synonym for a term of art costs precision. What goes is the
decoration around them.

Not shorter at the cost of the record. Every number in the prose is checked
against `data/clean/` by `code/analysis/body_text_numbers.py` and
`code/tests.py`. If a rewrite would drop a figure, a citekey or a
qualification that carries a fact, restate the fact in fewer words instead.

## Where each kind of text lives

`paper/` is the report, in prose, and syncs to Overleaf: keep the LaTeX valid,
leave section structure and labels alone unless that is the task, and do not
reflow a section to make an edit look tidy.

`docs/` is one write-up per subject, in the present tense: what each number
is, what backs it, what is assumed where nothing does, and why. It ends with
what still rests on an assumption.

`docs/questions.csv` is the tracker. A row is written for someone who has not
read this conversation: the question in a sentence, and what would settle it.
A recorded negative — a paper searched, a name not found — belongs in the row
and is never trimmed for brevity.

A figure's caption says what the picture shows and what a reader must know to
read it. Not how it was built.

## Corrections this project has made

Kept here so the voice accumulates rather than being re-derived. Add to it
when an author rewrites a passage, with what they said.

**27 September 2026, `paper/arlington-bsap.tex`, pre-1932 residence.** A
rewrite that stated the position rather than the history was still unreadable:
"It may read as a statement. It's terrible writing. Like, incredibly hard to
digest." The faults were a cleft sentence, a dash holding two statutory
clauses, and a closing negative. What replaced it puts a character first in
each sentence and moves the statutory detail to `docs/members.md`, which
carries it in full.

**27 September 2026, on hard rules.** Numeric limits were offered and
declined: "I don't like the idea of like numeric hard rules for writing style.
Like some some rules are meant to be broken." Hence Orwell's last rule above,
and no counts anywhere in this file.
