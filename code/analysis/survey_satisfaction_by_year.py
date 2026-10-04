"""Question 3's items across the County's three survey waves, 2018 to 2026.

One row per item, a dot per wave, ordered by where the item stands in 2026.
The two items the chart prints with the same figure in 2018 as in 2026 are
drawn as read; docs/survey_satisfaction.md says why they are doubted.
"""
import charts
import paths
import style


def main():
    style.apply()
    d = paths.read("survey_satisfaction_by_year")
    order = (d[d.year == 2026].sort_values("satisfied", ascending=False).item.tolist())
    wide = d.pivot(index="item", columns="year", values="satisfied").reindex(order)
    entries = {label: (wide[year].tolist(), colour)
               for year, (label, colour) in style.WAVES.items()}
    fig, ax = charts.figure()
    charts.hdots(ax, [i.replace("Arlington County", "the County") for i in order], entries)
    charts.share_axis(ax, "very satisfied or satisfied, don't knows excluded")
    charts.legend(fig, entries)
    paths.save(fig)


if __name__ == "__main__":
    main()
