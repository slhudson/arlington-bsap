# The correspondence the Board received

Arlington County shared the public correspondence its Board received on the
form of government with the whole study team, and the National Civic League
coded it for the report's part on community input. The folder holds 250
Outlook messages in three batches: 176 of correspondence, 72 receipts from
the advisory group's feedback form, and 2 from the Board meeting testimony
materials. `data/transcribed/by_claude/comments.csv` indexes all 250, one row
per message.

## Why the messages are not in the repository

The messages are 180MB, which is more than this repository holds in total and
would break the Overleaf sync at a stroke (`docs/repository.md`). That alone
settles it, and the second reason would settle it anyway.

Each letter is a public record that any resident could obtain from the County
by request. A permanent, indexed, downloadable archive of 203 residents'
correspondence, carrying their names, their email addresses and the home
addresses in their signature blocks, is a different object from the County's
own file. The person who wrote to their Board about a zoning fight did not
agree to be the first search result for their own name, and this repository
is meant to go public. So the messages stay in the project's Drive folder,
the index carries no name, no address and no message body, and a writer is a
number assigned in the order the files sort. A letter the report quotes is
cited and filed like any other source.

## What the index can count and what it cannot

Of the 250 messages, 195 carry a distinct body; the other 55 are the same
letter filed twice, most often once in each of the correspondence folder's
two halves. The National Civic League reports 218 comments from roughly 156
commenters. Neither number is reachable from this folder: 195 is what the
whole of it yields, and the writers cannot be counted from the messages at
all.

The writer count fails for a reason worth stating. In the correspondence
batch, 26 of the 176 messages were sent from a County address, which means
staff forwarded them, and 72 quote a `From:` header, which means the resident
who wrote them is inside the message rather than in its envelope. In the
advisory group batch every one of the 72 receipts comes from the same County
form address, so the sender column there names the form and not a single
resident. Counting senders gives 58, which is wrong by any reading; counting
every address that appears anywhere inside a body gives 103 for the
correspondence alone, which is also wrong, because a thread quotes everyone
who was ever on it.

Recovering the author of a forwarded message is a judgment about what a
quoted header means, not a parse, so the index records that a message is
forwarded and stops there.

## What the National Civic League's coding has to join on

Their analysis coded each comment for stance toward the review, focus and
motivating principle, and their percentages divide by a universe this index
does not reproduce. The `file` column holds the County's own path to each
message for that reason: it is the one key both sides already have.

## What the letters say about the County's authority under state law

Read on 5 October 2026 from the Drive copies, every distinct body the index
holds except seven the connector would not deliver (c074, c100, c137, c185,
c205, c206, c208, each 7MB or more; with their duplicates, 11 of the 250), so
the counts below are over 188 of the 195 distinct bodies. A message counts
only where the writer's own words raise the Commonwealth's authority; four
that merely quote the Board's draft charge ("Assess the impact of state laws,
including the Dillon Rule") do not.

Fifty-one of the 188 raise it, 62 of the 250 with duplicates, and they raise
it on one premise: that Arlington's form of government is fixed by its own
chapter of the Code of Virginia, so the Board's size, election from districts,
a directly elected chair, staggered terms and the election calendar can change
only with the General Assembly's leave, and Delegate Hope's bill (HB 1225 in
2024, HB 2768 in 2025) is the way to get it. Twelve say the County cannot do a
named thing without that leave: change the Board from five (seven messages),
elect from districts or elect the chair directly (six), alter the staggered
terms or the schedule (five), create neighborhood commissions (four), exceed
the statutory salary caps (one), adopt proportional ranked choice voting
(one). Thirty-one ask the Board to seek or back enabling legislation, fifteen
of them the Hope bill by name; five ask it to hold the bill off, to the 2027
session or past the advisory panel's work, and none of those five says the
County could act on its own. The Board's own statement to the Governor on HB
2768 says the bill "was not solicited by the Arlington County Board" (c153).
No letter argues that the County already has the authority over its form of
government; four say it for narrower things, ranked choice voting under
§ 15.2-705.1 among them. One message cites the Code by section: the Civic
Federation's TiGER report, attached to c017, which names §§ 15.2-702, 15.2-705
and 15.2-705.1 and the School Board sections. "Dillon Rule" appears in five
writers' own words, "home rule" in one, about other states. The messages, by
comment id, with the sentences each says it in, are in the findings memo "Comments on
state authority - findings, 5 October 2026" in the Drive folder's Working notes;
the index carries no body text, so the quotations are not here.

The Local Authority section of Part B states this or the National Civic
League's coding of the same theme, whichever the author team settles on
(`comments-local-authority`).

## What rests on an assumption

- That two messages with the same body, flattened for whitespace and case,
  are one comment. A resident who wrote twice in identical words would be
  counted once.
- That the advisory group's 72 form receipts are 72 separate submissions.
  Every one carries the same sender and the same subject, so nothing in the
  envelope distinguishes them and the index trusts the body.
- That a message raising state authority is one whose writer says so. The
  seven large messages the connector did not deliver are counted in neither
  column; Drive's own index returns no "Dillon" or "Richmond" in them, which
  is weak evidence because the indexed text may be cut short.
