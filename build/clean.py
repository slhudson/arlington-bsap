"""Turn the frozen spreadsheets in raw/ into analysis-ready files in data/.

This is the only place that reads raw/, and the only place where a subjective
decision about what a number *is* may be made. The rule that divides the two
stages:

    If two reasonable people could disagree about what the value is, the
    decision belongs here. If they would only disagree about how to show it,
    it belongs in analysis/.

Decisions made here are deliberately few, because the contested ones are not
settled yet. What this script does:

  * reads columns by name, not position, after fixing the header spacing in
    "aapi_m embers" (raw/ keeps the original spacing; the fix lives here)
  * turns "." into genuinely missing values, for 1883, 1884 and 1931 in the
    board counts and for not-yet-tabulated categories in the census data
  * writes values exactly as reported otherwise

What this script deliberately does NOT do, pending docs/questions.md:

  * reconcile the 1970 and 1990 race categories, which sum above the reported
    total (Q1)
  * decide whether not-reported should read as zero (Q2)

Those two treatments live in build/conventions.py, applied explicitly by each
figure, so that the current disagreement between figures is visible in code
rather than buried. When Q1 and Q2 are settled they move in here and the
per-figure calls go away.
"""
import pandas as pd

from paths import BOARD_XLSX, DATA, DEMOGRAPHICS_XLSX, ROSTER_XLSX


def _numeric(df, cols):
    """Coerce to numbers, turning "." and blanks into NaN."""
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def demographics() -> pd.DataFrame:
    """Census data, one row per census year.

    The sheet carries two source URLs in rows below the data; those rows have
    no year and are dropped by the notna() filter rather than by row count, so
    adding a third URL later will not silently truncate the data.
    """
    d = pd.read_excel(DEMOGRAPHICS_XLSX)
    d = d.rename(columns={
        "census": "year",
        "population_total": "total",
        "white_population": "white",
        "black_population": "black",
        "hisp-latino_population": "hisp",
        "aapi_population": "aapi",
    })
    cols = ["year", "total", "white", "black", "hisp", "aapi", "board_seats",
            "at_large", "residents_per_seat", "cube_root_p", "cube_root_resident_ratio"]
    d = _numeric(d[cols], cols)
    d = d[d["year"].notna()].reset_index(drop=True)

    # Structural checks: these are derived columns, so they must agree with
    # the figures they are derived from. A silent disagreement here would
    # propagate into the cube-root figure.
    assert (d["residents_per_seat"] - d["total"] / d["board_seats"]).abs().max() < 1e-6, \
        "residents_per_seat does not equal population / seats"
    assert (d["cube_root_resident_ratio"] - d["total"] ** (2 / 3)).abs().max() < 1e-6, \
        "cube_root_resident_ratio does not equal population^(2/3)"
    return d


def board_counts() -> pd.DataFrame:
    """Board composition, one row per year, 1871-2026.

    The source header reads "aapi_m embers", with a space. raw/ is read-only,
    so the spacing is corrected here rather than in the file.
    """
    b = pd.read_excel(BOARD_XLSX)
    b.columns = [c.replace(" ", "") for c in b.columns]
    b = b.rename(columns={
        "white_members": "white",
        "black_members": "black",
        "hisp_latino_members": "hisp",
        "aapi_members": "aapi",
    })
    cols = ["year", "white", "black", "hisp", "aapi", "men", "women"]
    b = _numeric(b[cols], cols)

    missing = b.loc[b["white"].isna(), "year"].tolist()
    assert missing == [1883, 1884, 1931], f"unexpected missing years: {missing}"
    return b


def roster() -> pd.DataFrame:
    """Person-level roster, one row per member per year, 1932-2026.

    Not yet used by any figure. Cleaned and written so that the descriptive
    coding has a home, and so a source column can be added per docs/sources.md.
    """
    r = pd.read_excel(ROSTER_XLSX)
    r.columns = [c.strip().lower().replace("/", "_") for c in r.columns]
    return r


def main() -> None:
    DATA.mkdir(exist_ok=True)
    for name, frame in [("demographics", demographics()),
                        ("board_counts", board_counts()),
                        ("roster", roster())]:
        path = DATA / f"{name}.csv"
        frame.to_csv(path, index=False)
        print(f"  {path.name:<20} {len(frame):>4} rows")


if __name__ == "__main__":
    main()
