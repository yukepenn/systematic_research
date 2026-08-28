"""MS-BBO-V1 step 1 - FILL / DECISION CONTRACT CERTIFICATION.  No model until this passes.

Directive s12/s14. THIS SCRIPT LOOKS AT TIMESTAMPS ONLY. It never reads a price and never computes
a P&L, so the max-fill-wait rule it produces cannot have been chosen using performance.

THE DISTINCTION THAT MATTERS (s14):
    FEATURES stop at   timestamp STRICTLY < t
    EXECUTION happens  at the first DISTINCT timestamp > t

Those are different clocks and conflating them is how a microstructure study leaks. MS01A already
established that same-millisecond ordering is unrecoverable, so:
    - a feature may never read an event stamped exactly t
    - a fill may never be taken from a quote stamped exactly t either, because "the quote at t"
      is ambiguous inside that millisecond - the first STRICTLY LATER distinct timestamp is used

DECISION SCHEDULE, frozen here before any P&L exists:
    RTH, fixed non-overlapping 60-second grid, decisions 10:00:00 -> 15:30:00 ET inclusive.
    Start 10:00 so the opening auction and its microstructure initialisation are excluded;
    end 15:30 so the last holding period closes at 15:31, well before closing-auction effects.
    NO time-of-day search: this window is declared, not selected.
"""
from __future__ import annotations

import glob
import os
import re

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
V2 = os.path.join(ROOT, "research/data_microstructure_v2/raw/NQ")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

NS = 1_000_000_000
GRID_S = 60
HORIZON_S = 60
RTH_START, RTH_END = "10:00:00", "15:30:00"
SEAL = "2026-08-01"
_fh = open(os.path.join(OUT, "fill_contract.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def first_after(ev_t, grid):
    """Index of the first event at a DISTINCT timestamp STRICTLY GREATER than each grid point.
    side='right' gives the count of events with t <= g, which is exactly that index."""
    idx = np.searchsorted(ev_t, grid, side="right")
    ok = idx < len(ev_t)
    return idx, ok


def main():
    files = sorted(glob.glob(os.path.join(V2, "s*.parquet")))
    P("=" * 100)
    P("=== MS-BBO-V1 - FILL CONTRACT CERTIFICATION.  TIMESTAMPS ONLY: no price, no P&L.")
    P("=" * 100)
    P(f"    candidate sessions {len(files)}   (v2 substrate: no truncation, quote-complete)")
    P(f"    decision grid  {RTH_START} -> {RTH_END} ET, every {GRID_S}s, horizon {HORIZON_S}s")
    P("    features < t   |   entry at first DISTINCT quote > t   |   exit > t+h")

    rows = []
    for f in files:
        s = re.match(r"^s(\d{8})", os.path.basename(f)).group(0)
        d = pq.read_table(f, columns=["bip", "time"]).to_pandas()
        tt = d["time"].values.astype("datetime64[ns]")
        if pd.Timestamp(tt.max()) >= pd.Timestamp(SEAL):
            continue
        day = pd.Timestamp(tt.max()).normalize()
        g0 = (day + pd.Timedelta(RTH_START)).value
        g1 = (day + pd.Timedelta(RTH_END)).value
        grid = np.arange(g0, g1 + 1, GRID_S * NS)
        if len(grid) < 10:
            continue
        ti = tt.astype("int64")
        bid_t = np.unique(ti[d["bip"].values == 1])
        ask_t = np.unique(ti[d["bip"].values == 2])
        if len(bid_t) == 0 or len(ask_t) == 0:
            continue
        gh = grid + HORIZON_S * NS
        rec = dict(session=s, n_grid=len(grid))
        for lab, base, ev in (("entry_bid", grid, bid_t), ("entry_ask", grid, ask_t),
                              ("exit_bid", gh, bid_t), ("exit_ask", gh, ask_t)):
            idx, ok = first_after(ev, base)
            dly = np.full(len(base), np.nan)
            dly[ok] = (ev[idx[ok]] - base[ok]) / 1e6          # ms
            rec[f"{lab}_miss"] = float(np.mean(~ok))
            rec[f"{lab}_med"] = float(np.nanmedian(dly))
            rec[f"{lab}_p99"] = float(np.nanpercentile(dly, 99))
            rec[f"{lab}_max"] = float(np.nanmax(dly))
        rows.append(rec)
        if len(rows) % 15 == 0:
            P(f"    ... {len(rows)} sessions")
    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(OUT, "fill_contract.csv"), index=False)

    P("")
    P("=" * 100)
    P("=== FILL AVAILABILITY  (delay from the instant to the first DISTINCT quote strictly after)")
    P("=" * 100)
    P(f"    sessions certified {len(r)}   decisions/session {int(r['n_grid'].median())}   "
      f"total decisions {int(r['n_grid'].sum()):,}")
    P("")
    P(f"    {'leg':<12}{'missing':>10}{'median ms':>12}{'p99 ms':>11}{'worst ms':>12}")
    P("    " + "-" * 57)
    for lab in ("entry_bid", "entry_ask", "exit_bid", "exit_ask"):
        P(f"    {lab:<12}{100*r[f'{lab}_miss'].mean():>9.3f}%{r[f'{lab}_med'].median():>12.1f}"
          f"{r[f'{lab}_p99'].median():>11.1f}{r[f'{lab}_max'].max():>12.1f}")

    worst_p99 = max(r[f"{l}_p99"].median() for l in
                    ("entry_bid", "entry_ask", "exit_bid", "exit_ask"))
    # FROZEN FROM THE TIMESTAMP DISTRIBUTION ALONE, never from performance.
    cap = float(np.ceil(worst_p99 / 100.0) * 100.0)
    cap = max(cap, 1000.0)
    P("")
    P("=" * 100)
    P("=== FROZEN MAX-FILL-WAIT RULE")
    P("=" * 100)
    P(f"    worst median-p99 across the four legs   {worst_p99:,.1f} ms")
    P(f"    >>> MAX FILL WAIT = {cap:,.0f} ms, rounded up from that p99 and floored at 1,000 ms.")
    P("    >>> A decision whose entry OR exit quote does not arrive inside the cap is DROPPED,")
    P("    >>> not filled at a stale price. Chosen from the TIMESTAMP distribution only - this")
    P("    >>> script never read a price, so the cap cannot have been tuned on P&L.")
    frac_ok = 1.0 - max(r[f"{l}_miss"].mean() for l in
                        ("entry_bid", "entry_ask", "exit_bid", "exit_ask"))
    P("")
    P(f"    usable decisions after the rule (upper bound) {100*frac_ok:.3f} %")
    P(f"    >>> {'FILL AVAILABILITY IS ADEQUATE' if frac_ok > 0.98 else '*** FILL AVAILABILITY IS POOR - REPORT BEFORE FITTING ***'}")
    pd.DataFrame([dict(max_fill_wait_ms=cap, worst_p99_ms=worst_p99,
                       sessions=len(r), decisions=int(r["n_grid"].sum()),
                       rth_start=RTH_START, rth_end=RTH_END,
                       grid_s=GRID_S, horizon_s=HORIZON_S)]).to_csv(
        os.path.join(OUT, "FROZEN_FILL_RULE.csv"), index=False)
    _fh.close()


if __name__ == "__main__":
    main()
