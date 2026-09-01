# -*- coding: utf-8 -*-
"""quote_sampler -- append-only NQ/MNQ front-vs-back quote samples across the roll window.

WHY, AND WHY NOW
----------------
`runs/ROLL01_SUCCESSOR_DESIGN_20260901/DESIGN.md` §4: the ~$437/wk roll blackout can only be
priced if we know what the BACK MONTH costs to trade in the 8-10 days before the volume
crossover. That measurement does not exist and CANNOT be recovered from local data -- the
NT8 tick store keeps only the front month at any time (MNQ 03-26 ends 2026-03-13, MNQ 06-26
starts 03-15), so the pre-crossover back month is exactly the period not retained, and every
file is `.Last.ncd` with no quotes at all.

It is also the ONLY unmeasured input in the live book's own cost estimate: `COST_MODEL.md`
§5 shows the MNQ-vs-NQ spread differential swings the live friction from -$6/wk to +$76/wk,
and the repo currently labels that ASSUMED.

Both questions are answered by the same cheap thing: sample the quote on all four
instruments through the 2026-09 roll. $0, read-only, touches nothing live. **The crossover
happens once a quarter -- if this window is missed the packet waits three months.**

STRICTLY READ-ONLY
------------------
Calls the CrossTrade MCP `GetQuote` only. Places no order, changes no strategy or account.
`GetQuote` is on the explicitly-allowed read-only list in CLAUDE.md §1.

USAGE
    This module has no MCP client of its own -- the agent calls GetQuote and feeds the
    payloads in. That keeps the tool surface where the safety rules can see it.

        from research_sdk.quote_sampler import record
        record(payloads)          # list of GetQuote `data` dicts

    Output: research/operational/roll_quotes/quotes.csv  (append-only, one row per sample)
        python -m research_sdk.quote_sampler --summary
"""
from __future__ import annotations

import csv
import io
import os
import sys
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(REPO, "research", "operational", "roll_quotes")
PATH = os.path.join(OUTDIR, "quotes.csv")

FIELDS = ["sampled_at_et", "instrument", "contract", "root", "bid", "ask",
          "spread_pts", "spread_ticks", "tick_size", "point_value",
          "spread_usd_per_contract", "spread_usd_per_nq_equiv",
          "last", "volume", "quote_time", "market_open", "note"]

# The four instruments that price the roll: front and back, NQ and MNQ.
WANT = ["NQ 09-26", "NQ 12-26", "MNQ 09-26", "MNQ 12-26"]

NQ_POINT_VALUE = 20.0          # the common denominator: $ per index point at NQ size


def record(payloads, note="", path=PATH):
    """Append one sample. `payloads` are GetQuote `data` dicts, verbatim."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fresh = not os.path.exists(path)
    rows = []
    for d in payloads:
        if not d:
            continue
        bid, ask = d.get("bid"), d.get("ask")
        tick = float(d.get("tickSize") or 0.25)
        pv = float(d.get("pointValue") or 0.0)
        sp = (float(ask) - float(bid)) if (bid and ask) else None
        inst = d.get("instrument") or ""
        root = "MNQ" if inst.startswith("MNQ") else ("NQ" if inst.startswith("NQ") else inst[:3])
        rows.append({
            "sampled_at_et": now,
            "instrument": inst,
            "contract": d.get("expiration") or "",
            "root": root,
            "bid": bid, "ask": ask,
            "spread_pts": None if sp is None else round(sp, 4),
            "spread_ticks": None if sp is None else round(sp / tick, 2),
            "tick_size": tick, "point_value": pv,
            # per CONTRACT: what one round turn of spread costs on that contract
            "spread_usd_per_contract": None if sp is None else round(sp * pv, 2),
            # per NQ-EQUIVALENT: the ONLY fair comparison between NQ and MNQ
            "spread_usd_per_nq_equiv": None if sp is None else round(sp * NQ_POINT_VALUE, 2),
            "last": d.get("last"), "volume": d.get("volume"),
            "quote_time": d.get("quoteTime") or "",
            "market_open": d.get("isMarketOpen"),
            "note": note,
        })
    with io.open(path, "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if fresh:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    return rows


def summary(path=PATH):
    if not os.path.exists(path):
        return "no samples yet -- %s does not exist" % path
    import pandas as pd
    df = pd.read_csv(path)
    out = ["samples: %d rows, %d timestamps, %s -> %s"
           % (len(df), df["sampled_at_et"].nunique(),
              df["sampled_at_et"].min(), df["sampled_at_et"].max()), ""]
    g = df.dropna(subset=["spread_ticks"]).groupby("instrument")
    out.append("%-10s %5s %10s %10s %10s %14s" %
               ("INSTR", "n", "med_ticks", "p90_ticks", "med_$/ctr", "med_$/NQ-equiv"))
    for k, v in g:
        out.append("%-10s %5d %10.2f %10.2f %10.2f %14.2f"
                   % (k, len(v), v["spread_ticks"].median(), v["spread_ticks"].quantile(.9),
                      v["spread_usd_per_contract"].median(),
                      v["spread_usd_per_nq_equiv"].median()))
    # the two questions this file exists to answer
    med = df.dropna(subset=["spread_usd_per_nq_equiv"]).groupby("instrument")[
        "spread_usd_per_nq_equiv"].median().to_dict()
    out.append("")
    nqf, mnqf = med.get("NQU6"), med.get("MNQU6")
    if nqf and mnqf:
        out.append("Q1  MNQ vs NQ spread, per NQ-equivalent, FRONT month: "
                   "$%.2f vs $%.2f  ->  MNQ is %+.0f%%   (COST_MODEL.md §5 assumes 0%%)"
                   % (mnqf, nqf, 100 * (mnqf / nqf - 1)))
    nqb, mnqb = med.get("NQZ6"), med.get("MNQZ6")
    if mnqf and mnqb:
        out.append("Q2  MNQ back vs front month: $%.2f vs $%.2f  ->  back month is %+.0f%%"
                   "   (ROLL01 §4: the cost of rolling early)"
                   % (mnqb, mnqf, 100 * (mnqb / mnqf - 1)))
    else:
        out.append("Q2  back month not yet sampled or not quoting -- the ROLL01 question is OPEN")
    return "\n".join(out)


if __name__ == "__main__":
    if "--summary" in sys.argv:
        print(summary())
    else:
        print(__doc__.split("USAGE")[0])
        print("instruments to sample: %s" % ", ".join(WANT))
        print("output: %s" % PATH)
