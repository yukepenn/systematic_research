"""G3_AUCTCYCLE_20260906 -- STEP 1: parse the raw TreasuryDirect pulls into out/auction_calendar.csv.

RAW SOURCE (persisted, $0 public data): out/td_raw/td_{Note,Bond}_{2009..2026}.json, pulled
year-by-year from the documented securities-search endpoint
    https://www.treasurydirect.gov/TA_WS/securities/search?format=json&type={Note,Bond}
        &startDate=YYYY-01-01&endDate=YYYY-12-31&dateFieldName=auctionDate
(2026 endDate=2026-07-31). Full URL list: out/td_raw/urls.txt; pull timestamp:
out/td_raw/pull_timestamp_utc.txt.

INCLUSION RULE, declared BEFORE any outcome exists (data-shape rule, not outcome-dependent):
  10y events = securityType == 'Note' and originalSecurityTerm of 10-year class
               ('10-Year', or a '9-Year X-Month' odd-original form)      -> market ZN
  30y events = securityType == 'Bond' and originalSecurityTerm of 30-year class
               ('30-Year', or a '29-Year X-Month' odd-original form)     -> market ZB
  (20-Year bonds, TIPS, FRNs excluded by construction: TIPS/FRN are different `type`s,
   20-Year originals fail the term rule.)
One event = one (auctionDate, tenor). reopening flag kept ('Yes'/'No').
Calendar window: auctionDate in 2009-01-01 .. 2026-07-31 (spec).
The full distribution of originalSecurityTerm values found is PRINTED so the rule's coverage
is auditable.
"""
from __future__ import annotations

import json
import os
import re

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
OUT = os.path.join(RUN, "out")
RAW = os.path.join(OUT, "td_raw")

CAL_START, CAL_END = pd.Timestamp("2009-01-01"), pd.Timestamp("2026-07-31")

TEN_Y = re.compile(r"^(10-Year|9-Year( \d+-(Month|Day))?.*)$")
THIRTY_Y = re.compile(r"^(30-Year|29-Year( \d+-(Month|Day))?.*)$")


def main():
    ts = open(os.path.join(RAW, "pull_timestamp_utc.txt"), encoding="utf-8").read().strip()
    urls = [u.strip() for u in open(os.path.join(RAW, "urls.txt"), encoding="utf-8")]
    url_by_key = {}
    for u in urls:
        m = re.search(r"type=(Note|Bond).*startDate=(\d{4})", u)
        url_by_key[(m.group(1), int(m.group(2)))] = u

    rows, term_dist = [], {}
    for f in sorted(os.listdir(RAW)):
        m = re.match(r"^td_(Note|Bond)_(\d{4})\.json$", f)
        if not m:
            continue
        typ, year = m.group(1), int(m.group(2))
        recs = json.load(open(os.path.join(RAW, f), encoding="utf-8"))
        for r in recs:
            ost = r.get("originalSecurityTerm", "")
            key = (r.get("securityType", ""), ost)
            term_dist[key] = term_dist.get(key, 0) + 1
            if typ == "Note" and TEN_Y.match(ost):
                tenor, mkt = "10Y", "ZN"
            elif typ == "Bond" and THIRTY_Y.match(ost):
                tenor, mkt = "30Y", "ZB"
            else:
                continue
            ad = pd.Timestamp(r["auctionDate"][:10])
            if not (CAL_START <= ad <= CAL_END):
                continue
            rows.append(dict(
                auction_date=ad.date(), tenor=tenor, market=mkt,
                reopening=r.get("reopening", ""), cusip=r.get("cusip", ""),
                security_term=r.get("securityTerm", ""), original_security_term=ost,
                issue_date=str(r.get("issueDate", ""))[:10],
                security_type=r.get("securityType", ""),
                source_url=url_by_key.get((typ, year), ""), pull_ts_utc=ts))

    cal = pd.DataFrame(rows).sort_values(["auction_date", "tenor"]).reset_index(drop=True)
    dup = cal.duplicated(subset=["auction_date", "tenor"]).sum()
    cal = cal.drop_duplicates(subset=["auction_date", "tenor"], keep="first").reset_index(drop=True)
    cal.to_csv(os.path.join(OUT, "auction_calendar.csv"), index=False)

    print("=" * 100)
    print("=== STEP 1: TreasuryDirect auction calendar")
    print("=" * 100)
    print("originalSecurityTerm distribution (type, term -> count)  [rule-coverage audit]:")
    for k in sorted(term_dist):
        picked = (k[0] == "Note" and bool(TEN_Y.match(k[1]))) or \
                 (k[0] == "Bond" and bool(THIRTY_Y.match(k[1])))
        print(f"    {k[0]:<5} {k[1]:<22} {term_dist[k]:>5}   {'<-- SELECTED' if picked else ''}")
    print(f"\nevents: {len(cal)} (dupes dropped: {dup})")
    for t in ("10Y", "30Y"):
        s = cal[cal.tenor == t]
        print(f"    {t}: {len(s):>4}  ({(s.reopening == 'Yes').sum()} reopenings, "
              f"{(s.reopening == 'No').sum()} originals)  "
              f"{s.auction_date.min()} -> {s.auction_date.max()}")
    print(f"pull timestamp: {ts}")
    print(f"WROTE {os.path.join(OUT, 'auction_calendar.csv')}")


if __name__ == "__main__":
    main()
