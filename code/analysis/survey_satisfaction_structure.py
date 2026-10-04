"""How respondents answer whether Arlington's form of government and County
Board structure are right for this community, split by whether they call
themselves familiar with that structure.

The whole five-point scale, because the share who agree is not the picture:
respondents who do not claim familiarity answer neutral three times in four.
"""
import charts
import paths
import style

AGREE = ["Strongly Agree", "Agree"]
AWAY = ["Neutral", "Disagree", "Strongly Disagree"]


def spread(frame):
    held = frame.structure_right[frame.structure_right != ""]
    return 100 * held.value_counts(normalize=True).reindex(style.AGREEMENT, fill_value=0)


def main():
    style.apply()
    d = paths.read("survey_satisfaction", keep_default_na=False)
    cuts = {"says familiar": spread(d[d.familiar.isin(AGREE)]),
            "neutral or disagrees": spread(d[d.familiar.isin(AWAY)])}
    entries = {label: ([cuts[c].loc[k] for c in cuts], colour)
               for k, (label, colour) in style.AGREEMENT.items()}
    fig, ax = charts.figure()
    charts.hstacked_bars(ax, list(cuts), entries)
    charts.share_axis(ax, "share of respondents answering the statement")
    charts.legend(fig, entries, ncol=3)
    paths.save(fig)


if __name__ == "__main__":
    main()
