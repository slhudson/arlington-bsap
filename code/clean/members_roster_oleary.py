"""Who held each magisterial district, 1870-1915, from O'Leary's election
listings. A module, not a step: members_roster.py assembles it with the rest.

From 1903 an entry lists every candidate with a vote count and the highest
wins; earlier it names the holder, with replacements in prose. A November
win is a four-year term, or shorter where the next listed election seats a
successor first. Each handover in the prose ends the sitting member's term
and begins the successor's: "Replaced by H. Dwight Smith in Dec.; replaced
by Lott W. Crocker in March 1873, replaced by Francis D. Schutt in April"
is a term for each man in the Arlington seat of 1872-73. A month without a
year takes the previous handover's year, rolling forward when the month
goes backwards. Schutt's April appointment and his May 1873 election are
two terms, not a duplicate. From 1907 O'Leary gives surnames only, so
"Corbett" and "Duncan" from 1907 are rows of their own until NAMES in
members_roster_arlhist.py and apply_duncan_join in members_roster.py join
them to the full names.
"""
import re

import citekeys
import elections
from members_terms import APPOINTMENT, ELECTION, MONTH, TERM_YEARS, UNRECORDED, month_of
from elections import MONTHS

NAME = r"([A-Z][A-Za-z.'’\- ]+?)"
# "Corbett 213 Hagen 189" - a name followed by its vote count, repeated
CANDIDATE_VOTES = re.compile(r"([A-Z][A-Za-z.'’\- ]*?)\s+([\d,]+)(?=\s|$)")
# "Replaced by H. Dwight Smith in Dec." / "Samuel Titus appointed in Dec."
SUCCESSION = re.compile(
    rf"(?:replaced by|appointed|successfully contested by)\s+(?:by\s+)?{NAME}\s+in\s+{MONTH}"
    r"(?:\s+((?:18|19)\d\d))?", re.I)
APPOINTED_AFTER_VACANCY = re.compile(
    rf"{NAME}\s+appointed\s+in\s+{MONTH}(?:\s+((?:18|19)\d\d))?", re.I)

# The Washington district seat's 1903 and 1907 entries name its holder two
# ways; the Alexandria Gazette's independent read of the 1907 vote count
# agrees with the county list on all three tallies but gives the winner's
# middle initial as N, not M, so both are read as one man (docs/members.md,
# "W. N. Febrey is one household").
NAME_CORRECTIONS = {
    (1903, "W. N. Febrey County"): "W. N. Febrey",
    (1907, "W.M. Febrey"): "W. N. Febrey",
}
NAME_CORRECTION_NOTES = {
    (1907, "W. N. Febrey"): "The county's list names this term's winner "
        "W.M. Febrey; the Alexandria Gazette's independent read of the same "
        "three vote tallies gives W. N. Febrey (alexandriagazette1907election), "
        "read as one man with the 1904-08 term (docs/members.md).",
}


# What a row says where O'Leary's listings do not record the end of a term.
# A later source that gives the end drops these (members_roster_arlhist.py).
UNRECORDED_END = "End of service not recorded; O'Leary's listings stop at 1915."
STATUTORY_END = ("Term ends by statute (Va. Const. 1902 sec. 112); no source "
                 "records the departure.")


# The month a term begins where the election is not the November one: the
# Board's year ran 1 July to 30 June through 1901, and every election
# O'Leary lists before the Constitution of 1902 is a May one.
TERM_BEGINS = 7


def seated(year, election_date):
    """When an election's winners take office: (year, month). A November
    election seats on 1 January following (Va. Const. 1902; schedule-1902 in
    docs/questions.csv); a May election seats on 1 July, the start of the
    Board's year (vaacts1870 ch. 76 sec. 4, township officers' terms
    commence 1 July; sec. 14 makes a supervisor one).

    Being elected is not taking office, and that held both halves of the
    period, not only the later one. The Board's own minute books date every
    term block of 1870-1901 from 1 July to 30 June (arlhist1967officials
    pp.39-42), and the article's footnote at 1901 corroborates it: the 1902
    Constitution moved the Board to four-year calendar terms, and "the extra
    six months of this Board covered the transition period" - thirty months
    on a July-June year, thirty-two on a May one. docs/members.md."""
    month = month_of(election_date)
    return (year + 1, 1) if month == 11 else (year, TERM_BEGINS)


def succession(entry, start_year, start_month):
    """Every handover in an entry's prose, in order: (name, year, month, seated_by).

    A month without a year carries the previous handover's year, rolling
    forward when the month goes backwards. "Appointed" is an appointment,
    "successfully contested" is the election, "replaced by" is unrecorded.
    """
    matches = list(SUCCESSION.finditer(entry)) or list(APPOINTED_AFTER_VACANCY.finditer(entry))
    year, month = start_year, start_month or 1
    for m in matches:
        name = m.group(1).strip()
        new_month = MONTHS[m.group(2).title()]
        new_year = int(m.group(3)) if m.group(3) else (year + 1 if new_month < month else year)
        verb = m.group(0).lower()
        how = (APPOINTMENT if "appointed" in verb
               else ELECTION if "contested" in verb else UNRECORDED)
        yield name, new_year, new_month, how
        year, month = new_year, new_month


def terms():
    """One row per person per term, from the listings."""
    d = elections.oleary(elections.SUPERVISORS)
    listed = sorted(d.year.unique())
    for year, nxt in zip(listed, listed[1:] + [None]):
        nxt_seated = (seated(int(nxt), d[d.year == nxt].election_date.iloc[0])
                      if nxt is not None else None)
        for _, r in d[d.year == year].iterrows():
            entry = str(r.entry)
            prose = "(" in entry or re.search(r"replac|vacant|appointed|contested", entry, re.I)
            paired = [] if prose else CANDIDATE_VOTES.findall(entry)
            if paired:
                name = max(paired, key=lambda p: int(p[1].replace(",", "")))[0].strip()
            else:
                name = re.split(r"\s*[(–]|\s+elected\b", entry, maxsplit=1)[0].strip(" -,")
            name = NAME_CORRECTIONS.get((int(year), name), name)

            start_year, start_month = seated(int(year), r.election_date)
            statutory = ((start_year + TERM_YEARS, start_month)
                         if month_of(r.election_date) == 11 else None)
            ends = [e for e in (statutory, nxt_seated) if e]
            term_end = min(ends) if ends else ("", "")
            statutory_end = statutory is not None and (nxt_seated is None or statutory < nxt_seated)
            end_unrecorded = not ends

            vacant = name.lower().startswith("vacant") or not name
            holders = ([] if vacant else [(name, start_year, start_month, ELECTION)]) \
                + list(succession(entry, start_year, start_month))
            for i, (who, y0, m0, how) in enumerate(holders):
                y1, m1 = holders[i + 1][1:3] if i + 1 < len(holders) else term_end
                last = i == len(holders) - 1
                parts = []
                if i > 0:
                    parts.append("Appointed after the seat fell vacant." if vacant
                                 else "Took the seat after successfully contesting the election."
                                 if "contested" in entry else "Took the seat mid-term.")
                elif "contested" in entry:
                    parts.append("Election successfully contested; the seat passed to "
                                 f"{holders[1][0]}.")
                if i == 0 and (int(year), who) in NAME_CORRECTION_NOTES:
                    parts.append(NAME_CORRECTION_NOTES[int(year), who])
                if last and end_unrecorded:
                    parts.append(UNRECORDED_END)
                elif last and statutory_end:
                    parts.append(STATUTORY_END)
                yield {"name": who, "district": r.district,
                       "start_year": y0, "start_month": m0,
                       "end_year": y1, "end_month": m1, "seated_by": how,
                       "source": f"{citekeys.OLEARY} p.{r.page}", "note": " ".join(parts)}
