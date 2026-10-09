"""How close each contest was, at the general election and at the nomination -> data/clean/elections_margins.csv

One row per contest. `stage` is "general" or "nomination". The margin is the
fewest votes that won a seat minus the most votes that lost one: with two
seats, the second-place candidate against the third. As a share it is of
the votes cast in the contest, write-ins included, so a two-seat contest
counts every ballot twice; a source that prints only percentages gives
the difference in points. A contest whose margin cannot be computed is kept,
with `status` saying why.

    1931 on       the county's candidate history to 2021, the state's
                  database from 2022; the nominating contests are
                  elections_nominations.csv
    before 1931   single-seat district contests: O'Leary names the winner,
                  the Alexandria Gazette's returns name losers and, in
                  some years, give counts (candidates_gazette.csv)

Seats are the county's, except where the page prints a contest's seats
wrongly (SEATS). docs/elections.md, "How close the contests were".
"""
import re

import numpy as np
import pandas as pd

import elections
import elections_results
import paths
from elections import COUNTY_HISTORY_THROUGH, LABELS, label_of, surname
from elections_nominations import iso
from paths import write

# The county prints "Vote for 1" on contests that filled more seats; the
# roster (docs/elections.md, "Votes are not voters") counts them.
SEATS = {"1931 November 3 County Board": 5,
         "1935 November 5 County Board": 5,
         "1939 November 7 County Board": 5,
         "1943 November 2 County Board": 2,
         "1952 November 4 County Board Special Election": 3}

# Contests whose printed list cannot be the whole field.
INCOMPLETE = {"1935 November 5 County Board":
              "the county lists five names for five seats and the Sun's report of the new Board names others"}

# A label's band, as elections_results counts it.
OTHER_BANDS = {"Republican", "independent", "other"}
MAJOR = {"Democratic", "ABC"}

COLUMNS = ["year", "stage", "tier", "contest", "party", "date", "method", "counting", "seats",
           "winners", "last_winner_votes", "top_loser", "top_loser_votes", "margin_votes",
           "votes_cast", "margin_share", "share_of", "candidates", "other_labels", "contested_other", "status",
           "source", "note"]


def tidy(name) -> str:
    """A candidate's name without the marks the county's page hangs on it:
    a leading asterisk, a label, a trailing remark."""
    s = re.sub(r"\(.*?\)", "", str(name)).lstrip("*").strip()
    return re.split(r", (?:re-elected|incumbent|new|conservative|unopposed)|\s+-\s+", s)[0].strip(" ,;")


def _row(**kw):
    return {c: kw.get(c, np.nan) for c in COLUMNS}


def margin(won: pd.DataFrame, lost: pd.DataFrame, cast):
    """(last winner's votes, top loser's name, top loser's votes, margin,
    share) for named winners and losers with counts."""
    last = won.votes.min()
    top = lost.loc[lost.votes.idxmax()]
    m = last - top.votes
    return last, top["name"], top.votes, m, (m / cast if cast else np.nan)


# ---------------------------------------------------------------- general, 1931 on

def labels_of(g: pd.DataFrame, year: int, parties: dict, dem_nominees: set) -> dict:
    """surname -> band ("Democratic", "Republican", "ABC", "independent",
    "other" or "" for none printed) for a contest's named candidates."""
    out = {}
    for _, r in g.iterrows():
        if r.record == "county":
            label = label_of(r.candidate, where=f"{year}: ")
            out[r.surname] = LABELS[label] if label else ""
        elif r.party == "Democratic" or (year, r.surname) in dem_nominees:
            out[r.surname] = "Democratic"
        elif r.party == "Republican":
            out[r.surname] = "Republican"
        elif isinstance(r.party, str):
            out[r.surname] = "independent"
        elif (year, r.surname) in parties:
            out[r.surname] = {"rep": "Republican", "dem": "Democratic"}.get(parties[(year, r.surname)][0], "independent")
        else:
            out[r.surname] = ""
    return out


def generals(noms: pd.DataFrame) -> list:
    c = elections.contests()
    c = c[~c.primary & ((c.record == "county") | (c.year > COUNTY_HISTORY_THROUGH))]
    parties = elections_results.candidate_parties()
    dem_nominees = set(zip(noms[(noms.party == "Democratic") & (noms.outcome == "nominated")].year,
                           noms[(noms.party == "Democratic") & (noms.outcome == "nominated")].name.map(surname)))
    rows = []
    counted = c.groupby("contest").votes.apply(lambda v: v.notna().any())
    has_counts = c.assign(ok=c.contest.map(counted)).groupby("year").ok.any()
    for contest, g in c.groupby("contest", sort=False):
        first = g.iloc[0]
        year = int(first.year)
        # A contest with no count on any line is a list of the Board, not a
        # contest, unless the year has no counts anywhere (elections.contest_rows).
        if not counted[contest] and has_counts[year]:
            continue
        special = bool(first.special)
        # A candidate printed "unexpired term" stood in a second, same-day contest.
        unexp = g.candidate.str.contains("unexp", case=False)
        parts = [(special, g[~unexp])] + ([(True, g[unexp])] if unexp.any() else [])
        for sp, h in parts:
            date = noms_date(first, year)
            label = f"special {date}" if sp else "regular"
            base = dict(year=year, stage="general", tier="1931 on", contest=label, date=date,
                        source=first.source if first.record == "county" else
                        f"vaelections contest {contest}")
            if first.record == "county":
                h = elections.filled_from_press(h)
            named = h[h.person & ~h.writein & ~h.prose]
            if first.record == "county":
                _, complete, why = elections.contest_rows(h)
            else:
                complete, why = True, ""
            seats = SEATS.get(contest, int(first.seats)) if not unexp.any() or not sp else 1
            cast = h.votes.sum()
            lab = labels_of(named, year, parties, dem_nominees)
            ranked = named[named.votes.notna()].sort_values("votes", ascending=False)
            won, lost = ranked.iloc[:seats], ranked.iloc[seats:]
            bands = list(lab.values())
            if any(b in OTHER_BANDS for b in bands):
                contested = "yes"
            elif all(b in MAJOR for b in bands):
                contested = "no"
            else:
                contested = "unknown"
            names = list(won["name"]) if len(won) else (list(named["name"]) if len(named) <= seats else [])
            common = dict(base, seats=seats, winners="; ".join(map(tidy, names)),
                          candidates=len(named), votes_cast=cast if cast else np.nan,
                          other_labels=", ".join(f"{tidy(n)}: {lab[s] or 'none printed'}"
                                                 for n, s in zip(ranked["name"], ranked.surname)),
                          share_of="votes cast")
            row = _row(**common, contested_other=contested)
            if contest in INCOMPLETE:
                row.update(status="not computed", note=INCOMPLETE[contest])
            elif not complete:
                row.update(status="not computed", note=f"the county's returns are incomplete: {why}")
            elif len(named) <= seats:
                row.update(status="not computed", note="no named candidate stood against the winner")
            elif len(ranked) < len(named):
                row.update(status="not computed", note="a named candidate has no count")
            else:
                last, tl, tv, m, share = margin(won, lost, cast)
                row.update(last_winner_votes=last, top_loser=tl, top_loser_votes=tv,
                           margin_votes=m, margin_share=share, status="computed")
            rows.append(row)
    return rows


def noms_date(first, year: int) -> str:
    return iso(first.election_date, year)


# ---------------------------------------------------------------- nominations

def nominations(noms: pd.DataFrame) -> list:
    rows = []
    for (year, seat, party), g in noms[noms.party != "citizens'"].groupby(["year", "seat", "party"], sort=False):
        won = g[g.outcome.isin(["nominated", "unopposed"])]
        lost = g[g.outcome == "lost"]
        first = g.iloc[0]
        row = _row(year=int(year), stage="nomination", tier="1931 on" if year >= 1931 else "before 1931",
                   contest=seat, party=party, date=first.date, method=first.method,
                   counting=first.counting, seats=len(won), winners="; ".join(won["name"]),
                   candidates=len(g), share_of="votes cast", source=first.source)
        if lost.empty:
            row.update(status="not computed",
                       note="unopposed" if (g.outcome == "unopposed").any() else "no losing candidate is named")
        elif g.votes.notna().all():
            if (g.votes_kind == "first-choice").any():
                row.update(status="not computed",
                           note="ranked-choice count: the page prints first choices, which do not decide the winner")
            else:
                cast = max(g.votes.sum(), first.total_votes if pd.notna(first.total_votes) else 0)
                last, tl, tv, m, share = margin(won, lost, cast)
                row.update(last_winner_votes=last, top_loser=tl, top_loser_votes=tv, margin_votes=m,
                           votes_cast=cast, margin_share=share, status="computed")
        elif g.pct.notna().all():
            m = won.pct.min() - lost.pct.max()
            row.update(last_winner_votes=np.nan, top_loser=lost.loc[lost.pct.idxmax(), "name"],
                       margin_votes=np.nan, margin_share=m / 100, share_of="votes cast (percentages)",
                       votes_cast=first.total_votes, status="computed")
        else:
            row.update(status="not computed", note="the source prints no counts")
        rows.append(row)
    return rows


# ---------------------------------------------------------------- before 1931

def district_rows() -> list:
    g = paths.typed(paths.built("candidates_gazette"))
    rows = []
    covered = set()
    for (year, district), h in g.groupby(["year", "district"], sort=False):
        covered.add((int(year), district))
        won, lost = h[h.outcome == "won"], h[h.outcome == "lost"]
        row = _row(year=int(year), stage="general", tier="before 1931", contest=f"{district} District",
                   date=h.election_date.iloc[0], seats=1, winners="; ".join(won["name"]),
                   candidates=len(h), source=h.source.iloc[0], share_of="votes cast")
        read = ", ".join(sorted(set(h.read_from)))
        if lost.empty and h.votes.notna().all():
            # One candidate, so there is no margin; the printed count is the contest's votes.
            row.update(status="not computed", votes_cast=h.votes.sum(), last_winner_votes=won.votes.max(),
                       note=f"no opponent is printed, so no margin; the count is read from the {read}")
        elif lost.empty:
            row.update(status="not computed", note="no loser is named")
        elif h.votes.isna().any():
            row.update(status="not computed", note="a candidate's count is not printed or not legible")
        elif won.votes.max() <= lost.votes.max():
            row.update(status="not computed", note="the winner's count does not exceed a loser's: a figure is misread")
        else:
            cast = h.votes.sum()
            last, tl, tv, m, share = margin(won, lost, cast)
            row.update(last_winner_votes=last, top_loser=tl, top_loser_votes=tv, margin_votes=m,
                       votes_cast=cast, margin_share=share, status="computed",
                       note=f"read from the {read}")
        said = h[h.note.fillna("").str.contains("tie", case=False)]
        if row["status"] == "not computed" and len(said):
            row["note"] = f"{row['note']}; " + "; ".join(said.quote.unique())
        rows.append(row)
    o = elections.oleary(elections.SUPERVISORS)
    for _, r in o.iterrows():
        if (int(r.year), r.district) in covered:
            continue
        rows.append(_row(year=int(r.year), stage="general", tier="before 1931",
                         contest=f"{r.district} District", date=r.election_date,
                         seats=1, winners=r.entry.split(" (")[0], status="not computed",
                         source="oleary2010 p." + str(r["page"]),
                         note="O'Leary names the winner and no one else"))
    return rows


# The county spells one winner two ways across its pages.
SPELLED = {"blevens": "blevins"}


def seated(d: pd.DataFrame):
    """Every general-election winner the votes name must be a member the
    roster seated from that election. A wrong seat count, which this table
    cannot see by itself, puts a loser among the winners or drops a winner
    and moves the margin without a sign."""
    m = paths.read("members")
    sat = {(int(y), surname(n)) for y, n in zip(m.election_year.dropna(), m.name[m.election_year.notna()])}
    sat |= {(int(y), surname(n)) for y, n in zip(m.start_year, m.name)}
    g = d[(d.stage == "general") & (d.tier == "1931 on") & (d.status == "computed")]
    missing = []
    for _, r in g.iterrows():
        for w in str(r.winners).split("; "):
            s = SPELLED.get(surname(w), surname(w))
            if (int(r.year), s) not in sat and (int(r.year), surname(w)) not in sat:
                missing.append((int(r.year), w))
    if missing:
        raise ValueError(f"general-election winners the roster did not seat in that year: {missing}. "
                         f"A contest's seat count is probably wrong (SEATS).")


def build() -> pd.DataFrame:
    noms = paths.read("elections_nominations")
    rows = generals(noms) + nominations(noms) + district_rows()
    d = pd.DataFrame(rows)
    d = d.reindex(columns=COLUMNS)
    d["stage"] = pd.Categorical(d.stage, ["general", "nomination"])
    d = d.sort_values(["year", "stage", "date", "contest"]).reset_index(drop=True)
    d["stage"] = d.stage.astype(str)
    c = d[d.status == "computed"]
    seated(d)
    assert (c.margin_votes.dropna() >= 0).all(), "a computed margin is negative"
    assert (c.margin_share.dropna().between(0, 1)).all(), "a margin share is outside 0-1"
    return d


if __name__ == "__main__":
    write(build(), "elections_margins")
