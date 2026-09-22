# Sources for the descriptive coding

What backs each claim about a Board member's race, ethnicity and gender — and,
just as importantly, what does not yet back it. The roster is person-level, so
sourcing is recorded per person in a `source` column; this file explains the
scheme and tracks what is outstanding.

This is also the work order for a research assistant.

## Status as of 2026-09-22

| Period | Members | What it rests on | Confidence |
|---|---|---|---|
| 1871–1888 | 5 named Black members | Census-linkable. Grace Hjerpe's 2021 paper demonstrates the method using 1880 manuscript census records. | Small n, verifiable — not yet verified |
| 1889–1986 | Coded all-White | The "first since Reconstruction" framing, and nothing else located so far | **Weakest link.** ~490 person-years |
| 1987–present | Newman (1987), Monroe (1999), Dorsey (2015), Spain (2024), Tejada | Contemporary news coverage; Arlington Historical Society maintains a curated entry covering all four | Well documented |
| Gender, all years | All | Naming conventions, with obituaries consulted for some earlier years | Adequate with a methods note; cheap to spot-check |

## The one that matters

The 1889–1986 stretch is a negative claim — that no Black member served for
nearly a century — and a negative claim needs evidence that someone looked.
Right now it rests on a phrase, not a review.

Open: whether that record was ever systematically examined, and by whom. Sally
is contacting the Arlington Historical Society (info@arlingtonhistorical.com),
which authored the curated roster and uses the phrasing, to find out.

If the answer is that nobody has checked, the report should say so plainly
rather than repeat the framing.

## Census population, 1870-1890

The county-only population figures for 1870, 1880 and 1890 were established
from original census records, and the scanned volumes in
`raw/2026-09-22-handoff/Historical Census Records/` are those records.

This corrects an earlier reading. The totals first used for those three decades
counted the City of Alexandria alongside the county, which the Board did not
govern. Arlington County was named Alexandria County before 1920, and the
combined figure is what several sources report. The discrepancy surfaced while
building the residents-per-seat figure: the drop from 18,597 in 1890 to 6,430
in 1900 was too large to be real.

The county-only 1890 figure is **4,596**, from the census volumes. A working
estimate of 4,258 was derived by subtracting a secondary-source city figure
from a secondary-source combined total; it is superseded and should not be
cited.

Race breakdowns for those years are in the corrected spreadsheet. They are
incomplete: in 1870 the White and Black counts total 3,085 of 3,185 residents,
and in 1890 4,318 of 4,596. The remainder appears as "Other/multiracial/
unreported". Whether those census tables list further categories is worth
checking against the scans.

## For a research assistant

Roughly in order of value:

1. Establish what supports the 1889–1986 coding. Start with the Historical
   Society's reply.
2. Verify the five Reconstruction-era members against the 1870 and 1880
   manuscript census, following Hjerpe's method.
3. Collect citations for the 1987–present members into the `source` column.
4. Spot-check gender coding against obituaries for the pre-1950 years.

Record each source in the roster's `source` column as you go, rather than in a
separate document — the point is that every coded cell can be traced.
