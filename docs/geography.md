# What "Arlington County" means here

The Board governed a territory whose name, boundaries and census treatment all
changed over the period this report covers. Every population figure depends on
getting this right, and the one error found so far came from getting it wrong.

## The definition this project uses

**Arlington County is the territory of the present-day county: the Arlington,
Jefferson and Washington magisterial districts. It excludes the City of
Alexandria in every year.**

The city is excluded because the Board did not govern it. That is the whole
justification, and it is why a published "Alexandria County" figure cannot be
used as-is for the early decades.

## How the territory appears in each census

| Period | Name | What the published county figure contains |
|---|---|---|
| to 1846 | Alexandria County, D.C. | part of the District of Columbia |
| 1847–1919 | Alexandria County, Virginia | the three districts **and** Alexandria city |
| 1920– | Arlington County, Virginia | the three districts only |

Two dates do the work:

**1900.** Alexandria city became independent of the county. From this census
onward the published county figure already excludes the city and needs nothing
done to it.

**1920.** Alexandria County was renamed Arlington County. Only a name change —
the territory did not move.

Source: *Population of States and Counties of the United States: 1790-1990*,
census.gov, Virginia notes, pdf p185.

## What this means in practice

**1870, 1880, 1890** — the published county figure includes Alexandria city.
A county-only figure must be derived, either by subtracting the city or by
summing the three magisterial districts. Both routes agree where they have been
checked.

**1900 onward** — use the published county figure directly.

## The three districts, and what sits inside them

In 1890 the county outside the city divides into exactly three magisterial
districts:

| District | 1890 | 1880 |
|---|---|---|
| Arlington | 2,013 | 1,754 |
| Jefferson | 1,303 | 1,319 |
| Washington | 942 | 814 |
| **County outside the city** | **4,258** | **3,887** |

**Freedman village is not a fourth district.** It was a settlement of formerly
enslaved people on the confiscated Lee estate, inside Arlington district. The
census lists it as an indented sub-line — "Arlington district, *including*
Freedman village" — the same way it lists Alexandria city's four wards beneath
the city total. Its 338 residents in 1890 are already within Arlington
district's 2,013.

Counting it as a fourth district adds those 338 people twice and produces
4,596, which is the figure currently in `data/manual/`. See docs/questions.md
Q8.

The settlement is substantively important to this report regardless of the
arithmetic — see Q9.

## Checks worth running on any new early figure

- Does the county-outside-city figure equal the sum of the three districts?
- Does city plus the three districts equal the published county total?
- Is every line being added a place, rather than a detail of the line above it?

The third is the one that failed.
