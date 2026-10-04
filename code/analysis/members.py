"""The years the member figures cover. A module, not a step: the member
figures read it so they agree on where their axes begin and end.

FIRST and LAST are the years the build covers, read from the seat table,
which ends in the year the roster was checked to. A figure's year axis
runs through LAST + 1, so every figure ends where the build does.

Seat-years, vacancies included, are counted once, in code/clean/members_by_year.py;
the figures on the three- and five-seat axis read that table.
"""

import paths

_by_year = paths.read("members_by_year")
FIRST, LAST = int(_by_year.year.min()), int(_by_year.year.max())
AGE_FIRST = 1910    # the age figures begin with the first census whose ages can be counted (docs/residents.md)
