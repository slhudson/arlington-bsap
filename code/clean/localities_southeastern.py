"""Arlington's Board beside nineteen southeastern cities of its size
-> data/clean/localities_southeastern.csv

One row per city: its voting seats and its residents. A city's seats are
the appendix's council members, a Mayor who sits and votes included as the
appendix counts one (docs/localities.md). Its residents are the appendix's
thousands, so a peer's figure is good to the nearest thousand; Arlington's
row is the Board's five and its 2020 census total, from
data/clean/localities.csv.
"""
import pandas as pd

import paths
from paths import write


def build() -> pd.DataFrame:
    b = paths.built("localities_southeastern")
    out = pd.DataFrame({
        "locality": b["city"].str.rsplit(", ", n=1).str[0],
        "state": b["city"].str.rsplit(", ", n=1).str[1],
        "members": b["council_members"].astype(int),
        "members_source": b["source"],
        "residents": b["residents_thousands"].astype(int) * 1000,
    })
    own = paths.read("localities")
    arl = own[own["locality"] == "Arlington"].iloc[0]
    return pd.concat([out, pd.DataFrame([{
        "locality": "Arlington", "state": "VA", "members": int(arl["members"]),
        "members_source": arl["members_source"], "residents": int(arl["residents"])}])],
        ignore_index=True)


if __name__ == "__main__":
    write(build(), "localities_southeastern")
