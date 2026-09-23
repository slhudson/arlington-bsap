"""Seats held per year, by race and by gender -> data/clean/board_seats.csv

One row per year, 1870-2026, in seat-years: a member who held a seat for the
whole year counts 1, for four months 4/12.

From 1870 to 1915 and from 1932 on, the rows are computed from
board_members.csv, whose terms run to the month. A term's months are its
start month through its end month, except that a month in which a successor
begins belongs to the successor - decided on Q13 in docs/questions.md,
because days are not recorded consistently and the month is the unit. The
three members whose end O'Leary never records are counted through 1915 only.

From 1916 to 1931 no terms are known, and the rows come from Alex Keena's
seat-count workbook as delivered. The `source` column says which.

The workbook's own years are also read for comparison and checked for
internal coherence - the race categories and the genders must each sum to
the seat count, three seats through 1930 and five from 1932 - but from 1932
its counts are not used: it splits a shared year half and half where the
roster has months.
"""
import pandas as pd

import citekeys
from paths import BOARD_SEATS_XLSX, CLEAN, numeric, write

COLUMNS = ["year", "white", "black", "hisp", "aapi", "men", "women"]
RACE = {"White": "white", "Black": "black", "Hispanic": "hisp", "Asian": "aapi"}
GENDER = {"man": "men", "woman": "women"}
WORKBOOK_YEARS = range(1916, 1932)
LAST_YEAR = 2026          # current terms run to 2029; the file stops at the present


def workbook() -> pd.DataFrame:
    """Alex's seat counts, one row per year, as delivered, with its checks."""
    b = pd.read_excel(BOARD_SEATS_XLSX)

    # The source header reads "aapi_m embers", with a space. by_human/ is
    # read-only, so the spacing is corrected here. Stripping spaces from every
    # header also lets columns be read by name rather than position, so a
    # reordered source column cannot silently swap two categories.
    b.columns = [c.replace(" ", "") for c in b.columns]
    b = b.rename(columns={"white_members": "white", "black_members": "black",
                          "hisp_latino_members": "hisp", "aapi_members": "aapi"})
    b = numeric(b[COLUMNS], COLUMNS)

    missing = b.loc[b["white"].isna(), "year"].tolist()
    assert missing == [1883, 1884, 1931], f"unexpected missing years: {missing}"

    # The Board is split two independent ways - by race and by gender - and
    # both must account for the same seats. Fractions are genuine, so compare
    # as floats.
    reported = b.dropna(subset=["white"]).copy()
    reported["seats"] = reported["year"].apply(lambda y: 3 if y < 1932 else 5)
    by_race = reported[["white", "black", "hisp", "aapi"]].sum(axis=1)
    by_gender = reported[["men", "women"]].sum(axis=1)
    for label, totals in (("race categories", by_race), ("men + women", by_gender)):
        off = reported.loc[(totals - reported["seats"]).abs() > 1e-9, "year"]
        assert off.empty, f"{label} do not sum to the seat count in {list(off.astype(int))}"
    off = reported.loc[(by_race - by_gender).abs() > 1e-9, "year"]
    assert off.empty, f"race and gender totals disagree in {list(off.astype(int))}"
    return b


def months_held(members: pd.DataFrame) -> pd.DataFrame:
    """One row per term per calendar year: how many months of it were held."""
    m = members.copy()
    m["end_year"] = m.end_year.fillna(m.start_year)      # end unrecorded: this year only
    m["end_month"] = m.end_month.fillna(12)
    m["start"] = m.start_year * 12 + m.start_month - 1   # months since year 0, inclusive
    m["stop"] = m.end_year * 12 + m.end_month             # exclusive

    # The handover month belongs to the incoming member: where a successor in
    # the same district begins in a term's last month, that month is dropped
    # from the outgoing term. A term ending in December has no successor
    # beginning in December, so it keeps all twelve months.
    starts = m.groupby("district").start.apply(set)
    m["stop"] = [stop - 1 if (stop - 1) in starts[d] else stop
                 for d, stop in zip(m.district, m.stop)]

    rows = []
    for _, t in m.iterrows():
        for year in range(int(t.start_year), int(t.end_year) + 1):
            lo, hi = max(t.start, year * 12), min(t.stop, year * 12 + 12)
            if hi > lo:
                rows.append({"year": year, "months": hi - lo,
                             "race": RACE[t.race], "gender": GENDER[t.gender]})
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    members = pd.read_csv(CLEAN / "board_members.csv")
    held = months_held(members)
    by_race = held.pivot_table(index="year", columns="race", values="months", aggfunc="sum", fill_value=0) / 12
    by_gender = held.pivot_table(index="year", columns="gender", values="months", aggfunc="sum", fill_value=0) / 12
    built = by_race.join(by_gender).reindex(columns=COLUMNS[1:], fill_value=0.0).reset_index()
    built = built[built.year <= LAST_YEAR]
    built["source"] = citekeys.DERIVED

    delivered = workbook()
    fill = delivered[delivered.year.isin(WORKBOOK_YEARS)].copy()
    fill["source"] = citekeys.KEENA

    d = pd.concat([built[~built.year.isin(WORKBOOK_YEARS)], fill]).sort_values("year").reset_index(drop=True)
    years = list(d.year)
    assert years == list(range(1870, LAST_YEAR + 1)), f"years are not 1870-2026 without gaps: {years[:3]}..{years[-3:]}"

    # The seats held never exceed the seats that exist, and fall short only
    # where the roster records a vacancy or the year the Board began.
    seats = d.year.apply(lambda y: 3 if y < 1932 else 5)
    total = d[["white", "black", "hisp", "aapi"]].sum(axis=1)
    over = d.loc[total - seats > 1e-9, "year"]
    assert over.empty, f"more seat-years than seats in {list(over)}"
    short = d.loc[(seats - total > 1e-9) & (d.source == citekeys.DERIVED), "year"]
    # 1870: the Board began in May. 1873: Washington district vacant from the
    # May election to December. 1990: Milliken resigned in February and the
    # special election was in May.
    assert list(short) == [1870, 1873, 1990], f"seats fall short in {list(short)}; expected only 1870, 1873, 1990"
    return d


if __name__ == "__main__":
    write(build(), "board_seats")
