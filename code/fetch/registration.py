"""Virginia registration statistics -> sources/government/state/va_dept_of_elections/registration_2010-2025.csv.gz

Run by hand after a November election, once the state has posted the
month's report; the build never touches the network (CLAUDE.md).

    .venv/bin/python code/fetch/registration.py

Arlington's registered voters at each November election from 2010, from
the Department of Elections' monthly registration statistics, which begin
in January 2010. The report filed under October is the count as the books
stood for the election, dated in the first days of November; the as-of
date is recorded where the file states it. One row per year is kept - the
state's own locality total, with the URL it was read from - because each
report is a whole-state file of half a megabyte. 2010-2012 are Excel
workbooks with one sheet per locality; from 2013 a CSV whose precinct rows
carry the locality total. "Active" is the state's turnout denominator;
"all" adds the inactive list.
"""
import io
import re
import urllib.request

import pandas as pd

import paths

ROOT = paths.ROOT
OUT = paths.VA_ELECTIONS / "registration_2010-2025.csv.gz"

SITE = "https://www.elections.virginia.gov"
PAGE = SITE + "/resultsreports/registration-statistics/{year}-registration-statistics/"
YEARS = range(2010, 2026)
# The site refuses requests that do not look like a browser's.
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 (KHTML, like Gecko)"}
LOCALITY = "ARLINGTON COUNTY"


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as r:
        return r.read()


def october_report(year):
    """The URL of the year's locality report filed under October."""
    page = fetch(PAGE.format(year=year)).decode(errors="replace")
    hits = re.findall(rf'href="(/media/registration-statistics/{year}/10/[^"]*'
                      rf'Registrant_Counts?_By_Locality[^"]*\.(?:csv|xls))"', page)
    if not hits:
        raise SystemExit(f"{year}: no October locality report on {PAGE.format(year=year)}")
    return SITE + hits[0]


def from_xls(body):
    """2010-2012: one sheet per locality; the last row of Arlington's sheet
    is its total, and the sheet's header states the as-of date."""
    sheets = pd.read_excel(io.BytesIO(body), header=None, sheet_name=None)
    for sheet in sheets.values():
        text = sheet.astype(str)
        if not text.apply(lambda r: r.str.contains(f"Locality: 013 {LOCALITY}").any(), axis=1).any():
            continue
        as_of = next(m.group(1) for cell in sheet[0] for m in [re.search(r"as of (\d+/\d+/\d+)", str(cell))] if m)
        total = sheet[text[5].str.startswith("# of Voters")].iloc[0]
        return {"as_of": pd.to_datetime(as_of).date().isoformat(),
                "precincts": int(total[4]),
                "active": int(total[6]), "inactive": int(total[7]), "all": int(total[8])}
    raise SystemExit(f"no sheet for {LOCALITY}")


def from_csv(body, url):
    """2013 on: every precinct row carries the locality's totals; the as-of
    date is in the filename from 2020. The columns named ...PrecinctLocality
    are the locality's and the ones named ...Locality the whole state's, so
    the total taken is checked against the sum of Arlington's precinct rows.
    """
    d = pd.read_csv(io.BytesIO(body), thousands=",", dtype={"PrecinctCode": str})
    a = d[d.Locality.str.contains(LOCALITY)]
    if a.empty:
        raise SystemExit(f"no rows for {LOCALITY} in {url}")
    totals = a[["TotalActiveVotersPrecinctLocality", "TotalInActiveVotersPrecinctLocality",
                "TotalAllVotersPrecinctLocality", "TotalPrecinctsInLocality"]].drop_duplicates()
    if len(totals) != 1:
        raise SystemExit(f"{url}: Arlington's rows disagree on the locality total")
    t = totals.iloc[0]
    if int(t.TotalAllVotersPrecinctLocality) != int(a.AllVoters.sum()):
        raise SystemExit(f"{url}: locality total {int(t.TotalAllVotersPrecinctLocality):,} is not "
                         f"the sum of Arlington's precincts, {int(a.AllVoters.sum()):,}")
    dated = re.search(r"_(\d{4})_(\d{2})_(\d{2})_\d+\.csv$", url)
    return {"as_of": "-".join(dated.groups()) if dated else "",
            "precincts": int(t.TotalPrecinctsInLocality),
            "active": int(t.TotalActiveVotersPrecinctLocality),
            "inactive": int(t.TotalInActiveVotersPrecinctLocality),
            "all": int(t.TotalAllVotersPrecinctLocality)}


def main():
    rows = []
    for year in YEARS:
        url = october_report(year)
        body = fetch(url)
        row = from_xls(body) if url.endswith(".xls") else from_csv(body, url)
        if row["active"] + row["inactive"] != row["all"]:
            raise SystemExit(f"{year}: active {row['active']:,} + inactive {row['inactive']:,} "
                             f"is not all {row['all']:,}")
        rows.append({"year": year, "report": f"{year}/10", **row, "file": url})
        print(f"  {year}  active {row['active']:>8,}  all {row['all']:>8,}  as of {row['as_of'] or '(not stated)'}")
    paths.write_text(OUT, pd.DataFrame(rows).to_csv(index=False))
    print(f"  {OUT.relative_to(ROOT)}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
