"""The Resident Satisfaction Survey's respondents set against the county they
are drawn from, by race and ethnicity.

Census categories, so the two can be read side by side: Hispanic or Latino of
any race, and among the rest White, Black, Asian and Pacific Islander, and
everyone else together. Respondents who declined or left it blank are not in
the base; the caption says how many.
"""
import charts
import paths
import style

ORDER = ["white", "black", "hispanic", "aapi", "other_or_multiracial"]
NAMES = {"white": "White", "black": "Black", "hispanic": "Hispanic or Latino",
         "aapi": "Asian & Pacific Islander", "other_or_multiracial": "Other or Multiracial"}
CENSUS = {"white": "white", "black": "black", "hispanic": "hisp", "aapi": "aapi"}
CENSUS_YEAR = 2020


def main():
    style.apply()
    survey = paths.read("survey_satisfaction", keep_default_na=False)
    named = survey[~survey.race.isin(["", "declined"])]
    share = 100 * named.race.value_counts(normalize=True).reindex(ORDER, fill_value=0)

    county = paths.read("residents")
    row = county[county.year == CENSUS_YEAR].iloc[0]
    counted = {k: row[c] for k, c in CENSUS.items()}
    counted["other_or_multiracial"] = row.total - sum(counted.values())
    county_share = [100 * counted[k] / row.total for k in ORDER]

    entries = {style.SAMPLE["survey"][0]: (share.tolist(), style.SAMPLE["survey"][1]),
               style.SAMPLE["county"][0]: (county_share, style.SAMPLE["county"][1])}
    fig, ax = charts.figure()
    charts.hgrouped_bars(ax, [NAMES[k] for k in ORDER], entries)
    charts.share_axis(ax, "share of those naming a race", top=80, step=20)
    charts.legend(fig, entries)
    paths.save(fig)


if __name__ == "__main__":
    main()
